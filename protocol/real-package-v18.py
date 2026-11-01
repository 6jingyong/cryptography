#!/usr/bin/env python3
"""Protocol-v3 lifecycle exercised with the noisy-host V18 engine.

Synthetic-only.  Long-lived A is imported unchanged from real-package-v3.py.
V18-specific host/QIM/geometry parameters remain inside per-package B.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import io
import json
import runpy
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
V3 = runpy.run_path(str(HERE / "real-package-v3.py"))


def load_engine(path: Path):
    return V3["load_engine"](path)


def set_seed(engine: dict, seed: int):
    V3["set_payload_seed"](engine, seed)
    setter = engine.get("set_benchmark_seed")
    if setter is not None:
        setter(int(seed))


def generate_B_b(engine, payload_bytes: int, channels: int, seed: int):
    set_seed(engine, seed)
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        result = engine["run_package"](payload_bytes=payload_bytes, channels=channels, out_dir=out)
        mf = result.get("manifest_filename", "manifest_adaptive_q_v12.json")
        pf = result.get("package_filename", "published_adaptive_q_v12.npz")
        B = json.loads((out / mf).read_text(encoding="utf-8"))
        b = (out / pf).read_bytes()
    return B, b, result


def decode_package(engine, B_bytes: bytes, b_bytes: bytes):
    B = json.loads(B_bytes.decode())
    z = np.load(io.BytesIO(b_bytes))
    bits = np.zeros(int(B["payload_bit_length"]), dtype=np.uint8)
    for table in B["tables"]:
        tid = int(table["table_id"])
        decoded = engine["decode_table"](z[f"table_{tid}_y"], table)
        off = int(table["payload_bit_offset"])
        bits[off:off+len(decoded)] = decoded
    payload = engine["bits_to_bytes"](bits)[:int(B["payload_bytes"])]
    sha = hashlib.sha256(payload).hexdigest()
    return payload, sha, sha == B["payload_sha256"]


def try_open(A, engine, record):
    if record.get("invalid_outer_tag"):
        return {"accepted": False, "reason": "c_outer_integrity_failed"}
    try:
        B_bytes = base64.b64decode(record[A.field_manifest], validate=True)
        b_bytes = base64.b64decode(record[A.field_payload], validate=True)
        tag = record[A.field_tag]
    except Exception:
        return {"accepted": False, "reason": "A_bootstrap_parse_failed"}
    if not hmac.compare_digest(str(tag), V3["package_tag"](A, B_bytes, b_bytes)):
        return {"accepted": False, "reason": "c_outer_integrity_failed"}
    try:
        payload, sha, ok = decode_package(engine, B_bytes, b_bytes)
    except Exception as exc:
        return {"accepted": False, "reason": "B_or_b_decode_failed", "detail": type(exc).__name__}
    if not ok:
        return {"accepted": False, "reason": "a_final_verification_failed"}
    return {"accepted": True, "reason": "strict_verify_pass", "payload": payload, "payload_sha256": sha}


def run_seed_with_engine(
    engine,
    payload_seed: int,
    payload_bytes: int = 512,
    channels: int = 2,
    corpus_size: int = 2000,
    near_decoy_fraction: float = 0.01,
    top_k: int = 100,
):
    A = V3["default_A"]()
    rng = np.random.default_rng(8_000_000 + int(payload_seed))
    B, b0, engine_result = generate_B_b(engine, payload_bytes, channels, payload_seed)
    B2, b = V3["permute_package_to_A"](A, B, b0)
    c = V3["make_c"](A, B2, b)
    target_index = int(rng.integers(0, corpus_size))
    near_count = int(round((corpus_size-1)*near_decoy_fraction))
    candidates = [i for i in range(corpus_size) if i != target_index]
    near_ids = set(int(x) for x in rng.choice(candidates, size=near_count, replace=False))
    corpus = [
        c if i == target_index else V3["make_d_descriptor"](A, rng, i in near_ids)
        for i in range(corpus_size)
    ]
    ranked = V3["rank_candidates"](A, corpus)
    target_rank = next(i+1 for i, r in enumerate(ranked) if r["index"] == target_index)
    attempts, accepted, accepted_rank = [], None, None
    for rank, item in enumerate(ranked[:top_k], start=1):
        opened = try_open(A, engine, corpus[item["index"]])
        attempts.append({"rank": rank, "score": item["score"], "accepted": opened["accepted"], "reason": opened["reason"]})
        if opened["accepted"]:
            accepted, accepted_rank = opened, rank
            break
    expected_sha = B2["payload_sha256"]
    exact = bool(accepted and accepted["payload_sha256"] == expected_sha)
    tables = B2["tables"]
    return {
        "payload_seed": int(payload_seed),
        "payload_sha256": expected_sha,
        "target_rank": int(target_rank),
        "accepted_rank": accepted_rank,
        "exact_recovery": exact,
        "target_locator_score": float(next(r["score"] for r in ranked if r["index"] == target_index)),
        "attempt_count": len(attempts),
        "q_distribution": engine_result.get("q_distribution"),
        "median_adjustment_to_host_rms_ratio": engine_result.get("median_adjustment_to_host_rms_ratio"),
        "max_adjustment_to_host_rms_ratio": engine_result.get("max_adjustment_to_host_rms_ratio"),
        "selected_tables": engine_result.get("selected_tables"),
        "B_contains_v18_settings": bool(all(
            t.get("carrier_mode") == "host-aware-modulo-qim-v18"
            and "host_model" in t and "delta" in t and "q" in t
            for t in tables
        )),
        "public_table_classes": V3["public_table_classes_from_npz_bytes"](b),
    }


def run_multiseed(engine_path: Path, seeds, payload_bytes=512, channels=2, corpus_size=2000, top_k=100):
    engine = load_engine(engine_path)
    runs = [
        run_seed_with_engine(
            engine,
            payload_seed=s,
            payload_bytes=payload_bytes,
            channels=channels,
            corpus_size=corpus_size,
            top_k=top_k,
        )
        for s in seeds
    ]
    hashes = [r["payload_sha256"] for r in runs]
    summary = {
        "version": "v18-current-protocol-multiseed",
        "scope": "synthetic-only",
        "seeds": len(runs),
        "all_payload_hashes_unique": len(set(hashes)) == len(hashes),
        "exact_recovery_rate": float(np.mean([r["exact_recovery"] for r in runs])),
        "recall_at_20": float(np.mean([r["target_rank"] <= 20 for r in runs])),
        "recall_at_100": float(np.mean([r["target_rank"] <= 100 for r in runs])),
        "median_target_rank": float(np.median([r["target_rank"] for r in runs])),
        "max_target_rank": int(max(r["target_rank"] for r in runs)),
        "B_settings_present_all_runs": bool(all(r["B_contains_v18_settings"] for r in runs)),
        "median_adjustment_to_host_rms_ratio": float(np.median([r["median_adjustment_to_host_rms_ratio"] for r in runs])),
        "max_adjustment_to_host_rms_ratio": float(max(r["max_adjustment_to_host_rms_ratio"] for r in runs)),
    }
    gate = bool(
        summary["all_payload_hashes_unique"]
        and summary["exact_recovery_rate"] == 1.0
        and summary["recall_at_100"] == 1.0
        and summary["B_settings_present_all_runs"]
    )
    return {"gate_pass": gate, "summary": summary, "runs": runs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--seeds", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--corpus-size", type=int, default=2000)
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--out", type=Path, default=Path("v18-protocol-result.json"))
    args = ap.parse_args()
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    result = run_multiseed(args.engine, seeds, args.payload_bytes, args.channels, args.corpus_size, args.top_k)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["gate_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
