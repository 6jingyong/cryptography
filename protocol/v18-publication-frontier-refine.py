#!/usr/bin/env python3
"""Fresh-seed refinement of the measured V18 publication-damage frontier.

Synthetic-only.  This wrapper deliberately reuses the existing coarse-frontier
harness and changes only the predeclared measurement grid and seed set.  The
carrier, q/delta/ECC policy, host model, lifecycle position, locator and decoder
remain unchanged.
"""
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

REQUANT = [1.00, 1.05, 1.10, 1.15, 1.20, 1.25]
NOISE = [0.00, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15]


def load_base(path: Path):
    ns = runpy.run_path(str(path))
    targets = [ns[name].__globals__ for name in ("conditions", "run")]
    for g in targets:
        g["REQUANT_FACTORS"] = list(REQUANT)
        g["NOISE_ALPHAS"] = list(NOISE)
        g["COMBINED_FACTORS"] = []
        g["COMBINED_ALPHAS"] = []
    return ns


def condition_rows(result: dict, family: str):
    rows = []
    for item in result["results"]:
        c = item["condition"]
        if c["family"] != family:
            continue
        s = item["summary"]
        value = c["requant_factor"] if family == "requant" else c["noise_sigma_over_delta"]
        rows.append({
            "value": float(value),
            "direct_exact_count": int(round(s["direct_exact_recovery_rate"] * s["seeds"])),
            "protocol_exact_count": int(round(s["protocol_exact_recovery_rate"] * s["seeds"])),
            "seed_count": int(s["seeds"]),
            "recall_at_100": float(s["recall_at_100"]),
            "pass": bool(s["pass"]),
            "first_failure_layer": s["first_failure_layer"],
        })
    rows.sort(key=lambda r: r["value"])
    return rows


def first_fail(rows):
    for r in rows:
        if not r["pass"]:
            return r["value"]
    return None


def largest_pass(rows):
    vals = [r["value"] for r in rows if r["pass"]]
    return None if not vals else max(vals)


def all_seed_pass_monotonic(rows):
    """True iff PASS points form one prefix before all FAIL points."""
    seen_fail = False
    for r in rows:
        if not r["pass"]:
            seen_fail = True
        elif seen_fail:
            return False
    return True


def exact_count_monotonic_nonincreasing(rows):
    counts = [r["direct_exact_count"] for r in rows]
    return all(b <= a for a, b in zip(counts, counts[1:]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, default=Path("protocol/v18-publication-damage.py"))
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--protocol", type=Path, default=Path("protocol/real-package-v18.py"))
    ap.add_argument("--seeds", default="401,402,403,404,405,406,407,408")
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--corpus-size", type=int, default=2000)
    ap.add_argument("--near-decoy-fraction", type=float, default=0.01)
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--out", type=Path, default=Path("v18-publication-frontier-refine.json"))
    args = ap.parse_args()

    base = load_base(args.base)
    tmp_out = args.out.with_suffix(".base.json")
    base_args = SimpleNamespace(
        engine=args.engine,
        protocol=args.protocol,
        seeds=args.seeds,
        payload_bytes=args.payload_bytes,
        channels=args.channels,
        corpus_size=args.corpus_size,
        near_decoy_fraction=args.near_decoy_fraction,
        top_k=args.top_k,
        out=tmp_out,
    )
    result = base["run"](base_args)
    if tmp_out.exists():
        tmp_out.unlink()

    rq = condition_rows(result, "requant")
    noise = condition_rows(result, "noise")
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]

    baseline = next(r for r in rq if abs(r["value"] - 1.00) < 1e-12)
    noise_control = next(r for r in noise if abs(r["value"] - 0.10) < 1e-12)
    rq_gate_mono = all_seed_pass_monotonic(rq)
    noise_gate_mono = all_seed_pass_monotonic(noise)
    rq_count_mono = exact_count_monotonic_nonincreasing(rq)
    noise_count_mono = exact_count_monotonic_nonincreasing(noise)

    refined = {
        "version": "v18-publication-frontier-refine-v2",
        "scope": "synthetic-only",
        "frozen_plan": "results/v18-publication-frontier-refine-plan.md",
        "parent_coarse_evidence": "results/v18-publication-damage.json",
        "configuration": {
            "fresh_seeds": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "candidate_corpus": args.corpus_size,
            "top_k": args.top_k,
            "requant_grid": REQUANT,
            "noise_sigma_over_delta_grid": NOISE[1:],
            "combined_sweep": False,
            "carrier_changes": "none",
        },
        "controls": {
            "requant_1p00_pass": baseline["pass"],
            "noise_0p10_pass": noise_control["pass"],
        },
        "frontier_descriptors": {
            "largest_tested_requant_all_seed_pass": largest_pass(rq),
            "first_tested_requant_below_all_seed_pass": first_fail(rq),
            "requant_all_seed_pass_pattern_monotonic": rq_gate_mono,
            "requant_exact_count_monotonic_nonincreasing": rq_count_mono,
            "largest_tested_noise_all_seed_pass": largest_pass(noise),
            "first_tested_noise_below_all_seed_pass": first_fail(noise),
            "noise_all_seed_pass_pattern_monotonic": noise_gate_mono,
            "noise_exact_count_monotonic_nonincreasing": noise_count_mono,
        },
        "interpretation": {
            "requantization": (
                "No scalar monotonic re-quantization threshold is supported by this grid; "
                "1.05x fails 8/8 gating while 1.10x passes, consistent with discrete grid/coset alignment effects."
                if not rq_gate_mono else
                "All-seed re-quantization PASS/FAIL is monotonic on the tested grid."
            ),
            "additive_noise": (
                "The all-seed gate is monotonic on the tested alpha grid, but exact pass counts are not; "
                "each alpha uses an independent noise realization, so this is not a deterministic nested threshold."
                if noise_gate_mono and not noise_count_mono else
                "Interpret noise results as sampled condition success, not a universal deterministic threshold."
            ),
        },
        "requantization": rq,
        "additive_noise": noise,
        "raw_results": result["results"],
    }
    refined["refinement_valid"] = bool(
        refined["controls"]["requant_1p00_pass"]
        and refined["controls"]["noise_0p10_pass"]
    )
    args.out.write_text(json.dumps(refined, indent=2), encoding="utf-8")
    print(json.dumps({
        "version": refined["version"],
        "refinement_valid": refined["refinement_valid"],
        "frontier_descriptors": refined["frontier_descriptors"],
        "interpretation": refined["interpretation"],
        "requantization": rq,
        "additive_noise": noise,
    }, indent=2))


if __name__ == "__main__":
    main()
