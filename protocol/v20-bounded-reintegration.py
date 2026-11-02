#!/usr/bin/env python3
"""Frozen first-pass V20 reliability experiment over the current V18 carrier.

Synthetic-only. The fixed 4 x 128-byte, 8-parity-byte-per-shard RS geometry is
not retuned in response to results. Scientific gate failure is valid data.
"""
from __future__ import annotations

import argparse
import base64
import json
import runpy
from pathlib import Path

import numpy as np

NOISE_ALPHAS = [0.14, 0.15, 0.16]
REQUANT_FACTORS = [1.06, 1.20, 1.30]


def load(path: Path):
    return runpy.run_path(str(path))


def damaged_record(v20: dict, stats: dict, built: dict, seed: int, family: str, value: float):
    A = built["A"]
    B = built["B"]
    b = built["b"]
    if family == "noise":
        damaged = stats["noisy_package"](b, B, seed, value)
    elif family == "requant":
        damaged = stats["requantize_package"](b, B, value)
    else:
        raise ValueError(family)
    c = dict(built["c"])
    c[A.field_payload] = base64.b64encode(damaged).decode()
    return c, damaged


def summarize(rows: list[dict], key: str, value: float):
    repaired = [r for r in rows if r["repair_attempted"]]
    successful_repairs = [r for r in repaired if r["repair_success"]]
    corrected = [r["corrected_shards"] for r in successful_repairs]
    return {
        key: float(value),
        "seed_count": len(rows),
        "v18_direct_exact_count": int(sum(r["v18_direct_exact"] for r in rows)),
        "v18_direct_exact_rate": float(np.mean([r["v18_direct_exact"] for r in rows])),
        "v20_exact_count": int(sum(r["v20_exact"] for r in rows)),
        "v20_exact_rate": float(np.mean([r["v20_exact"] for r in rows])),
        "repairs_attempted": len(repaired),
        "repairs_successful": len(successful_repairs),
        "corrected_shards_median": None if not corrected else float(np.median(corrected)),
        "corrected_shards_max": None if not corrected else int(max(corrected)),
        "all_locator_scores_one": bool(all(r["locator_score"] == 1.0 for r in rows)),
        "all_final_hash_exact_when_accepted": bool(all((not r["accepted"]) or r["v20_exact"] for r in rows)),
    }


def run(args):
    v20 = load(args.v20)
    stats = load(args.statistics)
    engine = v20["load_engine"](args.engine)
    V18 = v20["V18"]
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]

    built_by_seed = {}
    clean_rows = []
    for seed in seeds:
        built = v20["build_v20_package"](engine, seed, args.payload_bytes, args.channels)
        built_by_seed[seed] = built
        opened = v20["try_open_v20"](built["A"], engine, built["c"])
        clean_rows.append({
            "seed": seed,
            "accepted": bool(opened["accepted"]),
            "exact": bool(opened["accepted"] and opened.get("payload_sha256") == built["B"]["payload_sha256"]),
            "repair_attempted": bool(opened.get("repair_attempted", False)),
            "locator_score": float(v20["locator_score"](built["A"], built["c"])),
        })

    noise_rows = {a: [] for a in NOISE_ALPHAS}
    requant_rows = {f: [] for f in REQUANT_FACTORS}

    for seed in seeds:
        built = built_by_seed[seed]
        A = built["A"]
        B = built["B"]
        B_bytes = v20["serialize_B"](B)

        for alpha in NOISE_ALPHAS:
            c, damaged = damaged_record(v20, stats, built, seed, "noise", alpha)
            try:
                _, _, direct_ok = V18["decode_package"](engine, B_bytes, damaged)
            except Exception:
                direct_ok = False
            opened = v20["try_open_v20"](A, engine, c)
            row = {
                "seed": seed,
                "sigma_over_delta": alpha,
                "v18_direct_exact": bool(direct_ok),
                "accepted": bool(opened["accepted"]),
                "v20_exact": bool(opened["accepted"] and opened.get("payload_sha256") == B["payload_sha256"]),
                "reason": opened["reason"],
                "repair_attempted": bool(opened.get("repair_attempted", False)),
                "repair_success": bool(opened.get("repair_success", False)),
                "corrected_shards": int(opened.get("corrected_shards", 0) or 0),
                "locator_score": float(v20["locator_score"](A, c)),
            }
            noise_rows[alpha].append(row)

        for factor in REQUANT_FACTORS:
            c, damaged = damaged_record(v20, stats, built, seed, "requant", factor)
            try:
                _, _, direct_ok = V18["decode_package"](engine, B_bytes, damaged)
            except Exception:
                direct_ok = False
            opened = v20["try_open_v20"](A, engine, c)
            row = {
                "seed": seed,
                "factor": factor,
                "v18_direct_exact": bool(direct_ok),
                "accepted": bool(opened["accepted"]),
                "v20_exact": bool(opened["accepted"] and opened.get("payload_sha256") == B["payload_sha256"]),
                "reason": opened["reason"],
                "repair_attempted": bool(opened.get("repair_attempted", False)),
                "repair_success": bool(opened.get("repair_success", False)),
                "corrected_shards": int(opened.get("corrected_shards", 0) or 0),
                "locator_score": float(v20["locator_score"](A, c)),
            }
            requant_rows[factor].append(row)

    # One explicit envelope-authentication control: mutate masked repair bytes,
    # leave tag unchanged, and require rejection before repair.
    first = built_by_seed[seeds[0]]
    tampered = dict(first["c"])
    masked = bytearray(base64.b64decode(tampered[v20["FIELD_REPAIR"]]))
    masked[0] ^= 1
    tampered[v20["FIELD_REPAIR"]] = base64.b64encode(bytes(masked)).decode()
    tamper_opened = v20["try_open_v20"](first["A"], engine, tampered)
    tamper_control = {
        "repair_field_bitflip_rejected": bool(not tamper_opened["accepted"]),
        "reason": tamper_opened["reason"],
    }

    noise_summary = [summarize(noise_rows[a], "sigma_over_delta", a) for a in NOISE_ALPHAS]
    requant_summary = [summarize(requant_rows[f], "factor", f) for f in REQUANT_FACTORS]
    clean_exact = int(sum(r["exact"] for r in clean_rows))

    gate = bool(
        clean_exact == len(seeds)
        and all(x["v20_exact_count"] == len(seeds) for x in noise_summary)
        and all(x["v20_exact_count"] == len(seeds) for x in requant_summary)
        and all(x["all_final_hash_exact_when_accepted"] for x in noise_summary + requant_summary)
        and all(x["all_locator_scores_one"] for x in noise_summary + requant_summary)
        and tamper_control["repair_field_bitflip_rejected"]
    )

    out = {
        "version": "v20-bounded-reintegration-v1",
        "scope": "synthetic-only",
        "frozen_plan": "results/v20-bounded-reintegration-plan.md",
        "configuration": {
            "seeds": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "data_shard_bytes": v20["DATA_SHARD_BYTES"],
            "parity_bytes_per_shard": v20["PARITY_BYTES_PER_SHARD"],
            "shard_count": args.payload_bytes // v20["DATA_SHARD_BYTES"],
            "total_parity_bytes": (args.payload_bytes // v20["DATA_SHARD_BYTES"]) * v20["PARITY_BYTES_PER_SHARD"],
            "payload_parity_overhead": ((args.payload_bytes // v20["DATA_SHARD_BYTES"]) * v20["PARITY_BYTES_PER_SHARD"]) / args.payload_bytes,
            "noise_sigma_over_delta": NOISE_ALPHAS,
            "requant_factors": REQUANT_FACTORS,
            "damage_position": "after c construction/seal; numeric b replaced; B/r/tag unchanged",
            "raw_b_in_v20_tag": False,
        },
        "clean_control": {
            "exact_count": clean_exact,
            "seed_count": len(seeds),
            "all_locator_scores_one": bool(all(r["locator_score"] == 1.0 for r in clean_rows)),
            "any_repair_attempted": bool(any(r["repair_attempted"] for r in clean_rows)),
        },
        "tamper_control": tamper_control,
        "paired_additive_noise": {"summary": noise_summary, "runs": [r for a in NOISE_ALPHAS for r in noise_rows[a]]},
        "requantization": {"summary": requant_summary, "runs": [r for f in REQUANT_FACTORS for r in requant_rows[f]]},
        "gate_pass": gate,
        "gate_rule": "24/24 clean and 24/24 after V20 for every frozen damage condition; final authenticated hash exact; locator sentinel 1.0; repair-field tamper rejected",
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "version": out["version"],
        "clean_control": out["clean_control"],
        "tamper_control": tamper_control,
        "paired_additive_noise": noise_summary,
        "requantization": requant_summary,
        "gate_pass": gate,
    }, indent=2))
    # Scientific gate failure is data; runtime/harness errors still fail CI.
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--v20", type=Path, default=Path("protocol/real-package-v20.py"))
    ap.add_argument("--statistics", type=Path, default=Path("protocol/v18-publication-statistics.py"))
    ap.add_argument("--seeds", default=",".join(str(i) for i in range(701, 725)))
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--out", type=Path, default=Path("v20-bounded-result.json"))
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
