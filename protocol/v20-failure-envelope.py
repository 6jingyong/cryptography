#!/usr/bin/env python3
"""Map the failure envelope of the already-fixed bounded V20 geometry.

Synthetic-only. No code/shard/parity/carrier/locator parameters are changed.
"""
from __future__ import annotations

import argparse
import base64
import json
import runpy
from collections import Counter
from pathlib import Path

import numpy as np

NOISE_ALPHAS = [0.16, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35]
REQUANT_FACTORS = [1.30, 1.50, 1.75, 2.00, 2.50, 3.00]


def load(path: Path):
    return runpy.run_path(str(path))


def byte_error_geometry(candidate: bytes, expected: bytes, shard_bytes: int):
    if len(candidate) != len(expected):
        raise RuntimeError("candidate payload length mismatch")
    flags = np.frombuffer(candidate, dtype=np.uint8) != np.frombuffer(expected, dtype=np.uint8)
    by_shard = []
    for start in range(0, len(expected), shard_bytes):
        by_shard.append(int(np.sum(flags[start:start+shard_bytes])))
    return {
        "total_byte_errors": int(np.sum(flags)),
        "byte_errors_by_shard": by_shard,
        "max_byte_errors_in_shard": int(max(by_shard) if by_shard else 0),
        "shards_over_rs_bound": int(sum(x > 4 for x in by_shard)),
        "shards_with_byte_errors": int(sum(x > 0 for x in by_shard)),
    }


def mutate_b(v20: dict, stats: dict, built: dict, seed: int, family: str, value: float):
    A = built["A"]
    if family == "noise":
        damaged = stats["noisy_package"](built["b"], built["B"], seed, value)
    elif family == "requant":
        damaged = stats["requantize_package"](built["b"], built["B"], value)
    else:
        raise ValueError(family)
    c = dict(built["c"])
    c[A.field_payload] = base64.b64encode(damaged).decode()
    return c, damaged


def one_run(v20: dict, stats: dict, engine: dict, built: dict, seed: int, family: str, value: float):
    A, B = built["A"], built["B"]
    c, damaged = mutate_b(v20, stats, built, seed, family, value)
    B_bytes = v20["serialize_B"](B)

    try:
        candidate, candidate_sha, direct_ok = v20["V18"]["decode_package"](engine, B_bytes, damaged)
        geometry = byte_error_geometry(candidate, built["payload"], v20["DATA_SHARD_BYTES"])
    except Exception as exc:
        candidate_sha = None
        direct_ok = False
        geometry = {
            "total_byte_errors": None,
            "byte_errors_by_shard": None,
            "max_byte_errors_in_shard": None,
            "shards_over_rs_bound": None,
            "shards_with_byte_errors": None,
            "candidate_decode_exception": type(exc).__name__,
        }

    opened = v20["try_open_v20"](A, engine, c)
    row = {
        "seed": int(seed),
        "family": family,
        "value": float(value),
        "v18_direct_exact": bool(direct_ok),
        "candidate_sha256": candidate_sha,
        **geometry,
        "accepted": bool(opened["accepted"]),
        "v20_exact": bool(opened["accepted"] and opened.get("payload_sha256") == B["payload_sha256"]),
        "reason": opened["reason"],
        "repair_attempted": bool(opened.get("repair_attempted", False)),
        "repair_success": bool(opened.get("repair_success", False)),
        "corrected_shards": int(opened.get("corrected_shards", 0) or 0),
        "locator_score": float(v20["locator_score"](A, c)),
    }
    return row


def pct(values, q):
    vals = [x for x in values if x is not None]
    return None if not vals else float(np.percentile(np.asarray(vals, dtype=float), q))


def summarize(rows: list[dict], key: str, value: float):
    maxerr = [r["max_byte_errors_in_shard"] for r in rows]
    totalerr = [r["total_byte_errors"] for r in rows]
    over = [r["shards_over_rs_bound"] for r in rows]
    failed = [r for r in rows if not r["v20_exact"]]
    reasons = dict(Counter(r["reason"] for r in failed))
    candidate_available = [r for r in rows if r["total_byte_errors"] is not None]
    return {
        key: float(value),
        "seed_count": len(rows),
        "v18_direct_exact_count": int(sum(r["v18_direct_exact"] for r in rows)),
        "v20_exact_count": int(sum(r["v20_exact"] for r in rows)),
        "repair_attempted_count": int(sum(r["repair_attempted"] for r in rows)),
        "repair_success_count": int(sum(r["repair_success"] for r in rows)),
        "v20_failed_count": len(failed),
        "failure_reasons": reasons,
        "candidate_payload_available_count": len(candidate_available),
        "total_byte_errors_median": pct(totalerr, 50),
        "total_byte_errors_p90": pct(totalerr, 90),
        "total_byte_errors_max": None if not candidate_available else int(max(r["total_byte_errors"] for r in candidate_available)),
        "max_byte_errors_in_shard_median": pct(maxerr, 50),
        "max_byte_errors_in_shard_p90": pct(maxerr, 90),
        "max_byte_errors_in_shard_max": None if not candidate_available else int(max(r["max_byte_errors_in_shard"] for r in candidate_available)),
        "packages_with_shard_over_rs_bound": int(sum((x or 0) > 0 for x in over if x is not None)),
        "all_locator_scores_one": bool(all(r["locator_score"] == 1.0 for r in rows)),
        "locator_score_min": float(min(r["locator_score"] for r in rows)),
        "locator_score_max": float(max(r["locator_score"] for r in rows)),
        "all_final_hash_exact_when_accepted": bool(all((not r["accepted"]) or r["v20_exact"] for r in rows)),
    }


def tamper_controls(v20: dict, engine: dict, built: dict):
    A = built["A"]
    # r bitflip
    r_bad = dict(built["c"])
    masked = bytearray(base64.b64decode(r_bad[v20["FIELD_REPAIR"]]))
    masked[0] ^= 1
    r_bad[v20["FIELD_REPAIR"]] = base64.b64encode(bytes(masked)).decode()
    r_open = v20["try_open_v20"](A, engine, r_bad)

    # B bitflip at the serialized/base64-decoded byte level; unchanged tag.
    b_bad = dict(built["c"])
    B_bytes = bytearray(base64.b64decode(b_bad[A.field_manifest]))
    pos = min(8, len(B_bytes)-1)
    B_bytes[pos] ^= 1
    b_bad[A.field_manifest] = base64.b64encode(bytes(B_bytes)).decode()
    b_open = v20["try_open_v20"](A, engine, b_bad)
    return {
        "repair_field_bitflip_rejected": bool(not r_open["accepted"]),
        "repair_reason": r_open["reason"],
        "manifest_bitflip_rejected": bool(not b_open["accepted"]),
        "manifest_reason": b_open["reason"],
    }


def run(args):
    v20 = load(args.v20)
    stats = load(args.statistics)
    engine = v20["load_engine"](args.engine)
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]

    built_by_seed = {
        seed: v20["build_v20_package"](engine, seed, args.payload_bytes, args.channels)
        for seed in seeds
    }

    clean = []
    for seed, built in built_by_seed.items():
        opened = v20["try_open_v20"](built["A"], engine, built["c"])
        clean.append({
            "seed": seed,
            "exact": bool(opened["accepted"] and opened.get("payload_sha256") == built["B"]["payload_sha256"]),
            "locator_score": float(v20["locator_score"](built["A"], built["c"])),
        })

    noise = {a: [] for a in NOISE_ALPHAS}
    requant = {f: [] for f in REQUANT_FACTORS}
    for seed, built in built_by_seed.items():
        for alpha in NOISE_ALPHAS:
            noise[alpha].append(one_run(v20, stats, engine, built, seed, "noise", alpha))
        for factor in REQUANT_FACTORS:
            requant[factor].append(one_run(v20, stats, engine, built, seed, "requant", factor))

    noise_summary = [summarize(noise[a], "sigma_over_delta", a) for a in NOISE_ALPHAS]
    requant_summary = [summarize(requant[f], "factor", f) for f in REQUANT_FACTORS]
    controls = tamper_controls(v20, engine, built_by_seed[seeds[0]])

    def first_fail(rows, key):
        for r in rows:
            if r["v20_exact_count"] < r["seed_count"]:
                return r[key]
        return None

    out = {
        "version": "v20-fixed-geometry-failure-envelope-v1",
        "scope": "synthetic-only",
        "frozen_plan": "results/v20-failure-envelope-plan.md",
        "configuration": {
            "seeds": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "data_shard_bytes": v20["DATA_SHARD_BYTES"],
            "parity_bytes_per_shard": v20["PARITY_BYTES_PER_SHARD"],
            "noise_sigma_over_delta": NOISE_ALPHAS,
            "requant_factors": REQUANT_FACTORS,
            "geometry_changes": "none",
        },
        "clean_control": {
            "exact_count": int(sum(x["exact"] for x in clean)),
            "seed_count": len(clean),
            "all_locator_scores_one": bool(all(x["locator_score"] == 1.0 for x in clean)),
        },
        "tamper_controls": controls,
        "paired_additive_noise": {
            "summary": noise_summary,
            "runs": [r for a in NOISE_ALPHAS for r in noise[a]],
            "first_tested_v20_failure_sigma_over_delta": first_fail(noise_summary, "sigma_over_delta"),
        },
        "requantization": {
            "summary": requant_summary,
            "runs": [r for f in REQUANT_FACTORS for r in requant[f]],
            "first_tested_v20_failure_factor": first_fail(requant_summary, "factor"),
        },
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "version": out["version"],
        "clean_control": out["clean_control"],
        "tamper_controls": controls,
        "paired_additive_noise": noise_summary,
        "first_noise_failure": out["paired_additive_noise"]["first_tested_v20_failure_sigma_over_delta"],
        "requantization": requant_summary,
        "first_requant_failure": out["requantization"]["first_tested_v20_failure_factor"],
    }, indent=2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--v20", type=Path, default=Path("protocol/real-package-v20.py"))
    ap.add_argument("--statistics", type=Path, default=Path("protocol/v18-publication-statistics.py"))
    ap.add_argument("--seeds", default=",".join(str(i) for i in range(801, 825)))
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--out", type=Path, default=Path("v20-failure-envelope.json"))
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
