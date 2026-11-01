#!/usr/bin/env python3
"""V18 post-embedding / pre-seal publication-damage frontier.

Synthetic-only.  Damage is applied after the A-keyed public table assignment and
after V18 embedding, but before c is sealed.  Therefore the outer integrity tag
covers the damaged numeric package and does not trivially mask inner-carrier or
locator failures.

Hypothesis failure is a valid experimental result; the script exits normally
unless the harness itself crashes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import runpy
from pathlib import Path

import numpy as np


REQUANT_FACTORS = [1.00, 1.25, 1.50, 1.75, 2.00, 2.50, 3.00]
NOISE_ALPHAS = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25]
COMBINED_FACTORS = [1.50, 2.00]
COMBINED_ALPHAS = [0.05, 0.10, 0.15]


def load(path: Path):
    return runpy.run_path(str(path))


def condition_id(prefix: str, factor=None, alpha=None):
    parts = [prefix]
    if factor is not None:
        parts.append(f"rq{factor:.2f}")
    if alpha is not None:
        parts.append(f"n{alpha:.2f}")
    return "_".join(parts).replace(".", "p")


def conditions():
    out = []
    # Requant 1.00x is the baseline control.
    for factor in REQUANT_FACTORS:
        out.append({
            "id": condition_id("requant", factor=factor),
            "family": "requant",
            "requant_factor": factor,
            "noise_sigma_over_delta": 0.0,
            "order": "requant_only",
        })
    # 0.00 noise is represented by the 1.00x baseline above; avoid duplicate.
    for alpha in NOISE_ALPHAS[1:]:
        out.append({
            "id": condition_id("noise", alpha=alpha),
            "family": "noise",
            "requant_factor": None,
            "noise_sigma_over_delta": alpha,
            "order": "noise_only",
        })
    for factor in COMBINED_FACTORS:
        for alpha in COMBINED_ALPHAS:
            out.append({
                "id": condition_id("combined", factor=factor, alpha=alpha),
                "family": "combined",
                "requant_factor": factor,
                "noise_sigma_over_delta": alpha,
                "order": "noise_then_requant",
            })
    return out


def table_by_id(B: dict):
    return {int(t["table_id"]): t for t in B["tables"]}


def damage_rng(seed: int, cid: str, tid: int):
    raw = hashlib.sha256(f"v18-damage|{seed}|{cid}|{tid}".encode()).digest()[:8]
    return np.random.default_rng(int.from_bytes(raw, "big"))


def damage_package(b_bytes: bytes, B: dict, condition: dict, seed: int):
    z = np.load(io.BytesIO(b_bytes))
    tables = table_by_id(B)
    arrays = {}
    for name in z.files:
        arr = np.asarray(z[name])
        if not (name.startswith("table_") and name.endswith("_y")):
            arrays[name] = arr
            continue
        tid = int(name.split("_")[1])
        t = tables[tid]
        Y = np.asarray(arr, dtype=float)
        transform = t["transform"]
        Z = np.log(Y) if transform == "log" else Y.copy()

        alpha = float(condition["noise_sigma_over_delta"])
        if alpha > 0:
            rng = damage_rng(seed, condition["id"], tid)
            Z = Z + rng.normal(0.0, alpha*float(t["delta"]), size=Z.shape)

        factor = condition["requant_factor"]
        if factor is not None:
            step = float(factor) * float(t["publication_step"])
            Z = np.round(Z/step) * step

        arrays[name] = np.exp(Z) if transform == "log" else Z

    out = io.BytesIO()
    np.savez_compressed(out, **arrays)
    return out.getvalue()


def direct_decode(protocol: dict, engine: dict, B: dict, damaged_b: bytes):
    try:
        _, sha, ok = protocol["decode_package"](
            engine,
            json.dumps(B, separators=(",", ":")).encode(),
            damaged_b,
        )
        return {"exact_recovery": bool(ok), "decoded_sha256": sha, "error": None}
    except Exception as exc:
        return {"exact_recovery": False, "decoded_sha256": None, "error": type(exc).__name__}


def build_background(V3: dict, A, seed: int, corpus_size: int, near_fraction: float):
    rng = np.random.default_rng(96_000_000 + int(seed))
    target_index = int(rng.integers(0, corpus_size))
    near_count = int(round((corpus_size-1)*near_fraction))
    candidates = [i for i in range(corpus_size) if i != target_index]
    near_ids = set(int(x) for x in rng.choice(candidates, size=near_count, replace=False))
    background = []
    for i in range(corpus_size):
        if i == target_index:
            background.append(None)
        else:
            background.append(V3["make_d_descriptor"](A, rng, i in near_ids))
    return target_index, background


def full_protocol(protocol: dict, V3: dict, A, engine: dict, B: dict, damaged_b: bytes, target_index: int, background, top_k: int):
    c = V3["make_c"](A, B, damaged_b)
    corpus = list(background)
    corpus[target_index] = c
    ranked = V3["rank_candidates"](A, corpus)
    target_rank = next(i+1 for i, r in enumerate(ranked) if r["index"] == target_index)
    target_score = float(next(r["score"] for r in ranked if r["index"] == target_index))
    accepted = None
    accepted_rank = None
    attempts = 0
    for rank, item in enumerate(ranked[:top_k], start=1):
        opened = protocol["try_open"](A, engine, corpus[item["index"]])
        attempts += 1
        if opened["accepted"]:
            accepted = opened
            accepted_rank = rank
            break
    exact = bool(accepted and accepted["payload_sha256"] == B["payload_sha256"])
    return {
        "target_rank": int(target_rank),
        "target_locator_score": target_score,
        "accepted_rank": accepted_rank,
        "attempt_count": attempts,
        "exact_recovery": exact,
    }


def summarize_condition(rows):
    direct = [r["direct"]["exact_recovery"] for r in rows]
    exact = [r["protocol"]["exact_recovery"] for r in rows]
    ranks = [r["protocol"]["target_rank"] for r in rows]
    out = {
        "seeds": len(rows),
        "direct_exact_recovery_rate": float(np.mean(direct)),
        "protocol_exact_recovery_rate": float(np.mean(exact)),
        "recall_at_20": float(np.mean([x <= 20 for x in ranks])),
        "recall_at_100": float(np.mean([x <= 100 for x in ranks])),
        "median_target_rank": float(np.median(ranks)),
        "max_target_rank": int(max(ranks)),
    }
    out["pass"] = bool(
        out["direct_exact_recovery_rate"] == 1.0
        and out["protocol_exact_recovery_rate"] == 1.0
        and out["recall_at_100"] == 1.0
    )
    if out["direct_exact_recovery_rate"] < 1.0:
        out["first_failure_layer"] = "inner_decode"
    elif out["protocol_exact_recovery_rate"] < 1.0 or out["recall_at_100"] < 1.0:
        out["first_failure_layer"] = "locator_or_full_protocol"
    else:
        out["first_failure_layer"] = None
    return out


def run(args):
    protocol = load(args.protocol)
    V3 = protocol["V3"]
    engine = protocol["load_engine"](args.engine)
    A = V3["default_A"]()
    conds = conditions()
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    per_condition = {c["id"]: {"condition": c, "runs": []} for c in conds}

    for seed in seeds:
        protocol["set_seed"](engine, seed)
        B0, b0, _ = protocol["generate_B_b"](engine, args.payload_bytes, args.channels, seed)
        # Encode the A-layer fingerprint first; publication damage happens after
        # the public assignment but before c is sealed.
        B, b_assigned = V3["permute_package_to_A"](A, B0, b0)
        target_index, background = build_background(V3, A, seed, args.corpus_size, args.near_decoy_fraction)

        for c in conds:
            damaged_b = damage_package(b_assigned, B, c, seed)
            direct = direct_decode(protocol, engine, B, damaged_b)
            full = full_protocol(protocol, V3, A, engine, B, damaged_b, target_index, background, args.top_k)
            per_condition[c["id"]]["runs"].append({
                "seed": seed,
                "direct": direct,
                "protocol": full,
            })

    results = []
    for c in conds:
        item = per_condition[c["id"]]
        item["summary"] = summarize_condition(item["runs"])
        results.append(item)

    baseline = next(r for r in results if r["condition"]["family"] == "requant" and r["condition"]["requant_factor"] == 1.0)
    harness_valid = bool(baseline["summary"]["pass"])

    rq_pass = [r["condition"]["requant_factor"] for r in results if r["condition"]["family"] == "requant" and r["summary"]["pass"]]
    noise_pass = [r["condition"]["noise_sigma_over_delta"] for r in results if r["condition"]["family"] == "noise" and r["summary"]["pass"]]
    combined = [
        {
            "requant_factor": r["condition"]["requant_factor"],
            "noise_sigma_over_delta": r["condition"]["noise_sigma_over_delta"],
            "pass": r["summary"]["pass"],
            "direct_exact_recovery_rate": r["summary"]["direct_exact_recovery_rate"],
            "protocol_exact_recovery_rate": r["summary"]["protocol_exact_recovery_rate"],
            "recall_at_100": r["summary"]["recall_at_100"],
            "first_failure_layer": r["summary"]["first_failure_layer"],
        }
        for r in results if r["condition"]["family"] == "combined"
    ]

    out = {
        "version": "v18-publication-damage-frontier-v1",
        "scope": "synthetic-only",
        "frozen_plan": "results/v18-publication-damage-plan.md",
        "lifecycle_position": "after A-keyed public assignment and embedding; before c sealing / outer integrity",
        "configuration": {
            "seeds": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "candidate_corpus": args.corpus_size,
            "near_decoy_fraction": args.near_decoy_fraction,
            "top_k": args.top_k,
            "requant_factors": REQUANT_FACTORS,
            "noise_sigma_over_delta": NOISE_ALPHAS,
            "combined_requant_factors": COMBINED_FACTORS,
            "combined_noise_sigma_over_delta": COMBINED_ALPHAS,
        },
        "harness_valid": harness_valid,
        "frontier": {
            "largest_requant_factor_all_seed_pass": None if not rq_pass else float(max(rq_pass)),
            "largest_noise_sigma_over_delta_all_seed_pass": 0.0 if not noise_pass else float(max(noise_pass)),
            "combined": combined,
        },
        "results": results,
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(json.dumps({
        "version": out["version"],
        "harness_valid": harness_valid,
        "frontier": out["frontier"],
        "conditions": [
            {
                "id": r["condition"]["id"],
                "pass": r["summary"]["pass"],
                "direct_exact": r["summary"]["direct_exact_recovery_rate"],
                "protocol_exact": r["summary"]["protocol_exact_recovery_rate"],
                "r100": r["summary"]["recall_at_100"],
                "max_rank": r["summary"]["max_target_rank"],
                "failure_layer": r["summary"]["first_failure_layer"],
            }
            for r in results
        ],
    }, indent=2))
    # Scientific failure is data.  Only harness/runtime errors should fail CI.
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--protocol", type=Path, default=Path("protocol/real-package-v18.py"))
    ap.add_argument("--seeds", default="301,302,303,304")
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--corpus-size", type=int, default=2000)
    ap.add_argument("--near-decoy-fraction", type=float, default=0.01)
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--out", type=Path, default=Path("v18-publication-damage.json"))
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
