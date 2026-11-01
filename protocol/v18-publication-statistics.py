#!/usr/bin/env python3
"""Statistical characterization of V18 pre-seal publication damage.

Synthetic-only.  Carrier behavior is unchanged.  The experiment maps:
- direct package-exact recovery across a dense deterministic re-quantization grid;
- direct package-exact recovery under paired/scaled Gaussian noise fields.

The public structural locator score is checked as a sentinel for every damaged
package.  Scientific failure is data; runtime/harness failure is an error.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import runpy
from pathlib import Path

import numpy as np

REQUANT_FACTORS = [round(1.00 + 0.02*i, 2) for i in range(16)]
NOISE_ALPHAS = [round(0.08 + 0.01*i, 2) for i in range(11)]


def load(path: Path):
    return runpy.run_path(str(path))


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n <= 0:
        return [None, None]
    phat = k / n
    z2 = z*z
    denom = 1.0 + z2/n
    center = (phat + z2/(2*n)) / denom
    half = z * math.sqrt(phat*(1-phat)/n + z2/(4*n*n)) / denom
    return [float(max(0.0, center-half)), float(min(1.0, center+half))]


def table_map(B: dict):
    return {int(t["table_id"]): t for t in B["tables"]}


def npz_bytes(arrays: dict):
    out = io.BytesIO()
    np.savez_compressed(out, **arrays)
    return out.getvalue()


def transform_table(Y: np.ndarray, transform: str):
    return np.log(Y) if transform == "log" else np.asarray(Y, dtype=float).copy()


def inverse_table(Z: np.ndarray, transform: str):
    return np.exp(Z) if transform == "log" else Z


def requantize_package(b_bytes: bytes, B: dict, factor: float):
    z = np.load(io.BytesIO(b_bytes))
    tm = table_map(B)
    arrays = {}
    for name in z.files:
        arr = np.asarray(z[name])
        if not (name.startswith("table_") and name.endswith("_y")):
            arrays[name] = arr
            continue
        tid = int(name.split("_")[1])
        t = tm[tid]
        Z = transform_table(np.asarray(arr, dtype=float), t["transform"])
        step = float(factor) * float(t["publication_step"])
        Z = np.round(Z / step) * step
        arrays[name] = inverse_table(Z, t["transform"])
    return npz_bytes(arrays)


def paired_noise_field(seed: int, tid: int, shape):
    raw = hashlib.sha256(f"v18-paired-noise|{seed}|{tid}".encode()).digest()[:8]
    rng = np.random.default_rng(int.from_bytes(raw, "big"))
    return rng.normal(0.0, 1.0, size=shape)


def noisy_package(b_bytes: bytes, B: dict, seed: int, alpha: float):
    z = np.load(io.BytesIO(b_bytes))
    tm = table_map(B)
    arrays = {}
    for name in z.files:
        arr = np.asarray(z[name])
        if not (name.startswith("table_") and name.endswith("_y")):
            arrays[name] = arr
            continue
        tid = int(name.split("_")[1])
        t = tm[tid]
        Z = transform_table(np.asarray(arr, dtype=float), t["transform"])
        g = paired_noise_field(seed, tid, Z.shape)
        Z = Z + float(alpha) * float(t["delta"]) * g
        arrays[name] = inverse_table(Z, t["transform"])
    return npz_bytes(arrays)


def direct_exact(protocol: dict, engine: dict, B: dict, b_bytes: bytes):
    try:
        _, _, ok = protocol["decode_package"](
            engine,
            json.dumps(B, separators=(",", ":")).encode(),
            b_bytes,
        )
        return bool(ok)
    except Exception:
        return False


def summarize(value_key: str, values, successes_by_value, locator_by_value):
    rows = []
    n = len(next(iter(successes_by_value.values())))
    for value in values:
        flags = successes_by_value[value]
        k = int(sum(flags))
        scores = locator_by_value[value]
        rows.append({
            value_key: float(value),
            "exact_count": k,
            "seed_count": n,
            "exact_rate": float(k/n),
            "wilson95": wilson(k, n),
            "all_seed_exact": bool(k == n),
            "locator_score_min": float(min(scores)),
            "locator_score_max": float(max(scores)),
        })
    return rows


def count_monotone_nonincreasing(rows):
    counts = [r["exact_count"] for r in rows]
    return all(b <= a for a, b in zip(counts, counts[1:]))


def run(args):
    protocol = load(args.protocol)
    V3 = protocol["V3"]
    engine = protocol["load_engine"](args.engine)
    A = V3["default_A"]()
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]

    rq_success = {x: [] for x in REQUANT_FACTORS}
    rq_locator = {x: [] for x in REQUANT_FACTORS}
    noise_success = {x: [] for x in NOISE_ALPHAS}
    noise_locator = {x: [] for x in NOISE_ALPHAS}

    for seed in seeds:
        protocol["set_seed"](engine, seed)
        B0, b0, _ = protocol["generate_B_b"](engine, args.payload_bytes, args.channels, seed)
        B, b = V3["permute_package_to_A"](A, B0, b0)

        for factor in REQUANT_FACTORS:
            damaged = requantize_package(b, B, factor)
            rq_success[factor].append(direct_exact(protocol, engine, B, damaged))
            rq_locator[factor].append(float(V3["structural_score"](A, damaged)))

        for alpha in NOISE_ALPHAS:
            damaged = noisy_package(b, B, seed, alpha)
            noise_success[alpha].append(direct_exact(protocol, engine, B, damaged))
            noise_locator[alpha].append(float(V3["structural_score"](A, damaged)))

    rq_rows = summarize("factor", REQUANT_FACTORS, rq_success, rq_locator)
    noise_rows = summarize("sigma_over_delta", NOISE_ALPHAS, noise_success, noise_locator)

    # Per-seed monotonicity for paired/scaled noise.  A monotonic seed has no
    # later success after its first failure as alpha increases.
    paired_noise_seed_monotone = []
    for i, seed in enumerate(seeds):
        flags = [noise_success[a][i] for a in NOISE_ALPHAS]
        seen_fail = False
        mono = True
        for f in flags:
            if not f:
                seen_fail = True
            elif seen_fail:
                mono = False
                break
        paired_noise_seed_monotone.append({"seed": seed, "monotone_pass_fail": mono, "pattern": flags})

    out = {
        "version": "v18-publication-statistics-v1",
        "scope": "synthetic-only",
        "frozen_plan": "results/v18-publication-statistics-plan.md",
        "configuration": {
            "seeds": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "requant_factors": REQUANT_FACTORS,
            "paired_noise_sigma_over_delta": NOISE_ALPHAS,
            "damage_position": "post-embedding/post-A-assignment/pre-c-seal",
            "carrier_changes": "none",
        },
        "requantization": {
            "rows": rq_rows,
            "exact_count_monotonic_nonincreasing": count_monotone_nonincreasing(rq_rows),
            "all_locator_scores_one": bool(all(r["locator_score_min"] == 1.0 and r["locator_score_max"] == 1.0 for r in rq_rows)),
        },
        "paired_additive_noise": {
            "rows": noise_rows,
            "exact_count_monotonic_nonincreasing": count_monotone_nonincreasing(noise_rows),
            "seed_monotonicity": paired_noise_seed_monotone,
            "all_seed_patterns_monotone": bool(all(x["monotone_pass_fail"] for x in paired_noise_seed_monotone)),
            "all_locator_scores_one": bool(all(r["locator_score_min"] == 1.0 and r["locator_score_max"] == 1.0 for r in noise_rows)),
        },
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "version": out["version"],
        "requantization": rq_rows,
        "requant_count_monotone": out["requantization"]["exact_count_monotonic_nonincreasing"],
        "paired_noise": noise_rows,
        "noise_count_monotone": out["paired_additive_noise"]["exact_count_monotonic_nonincreasing"],
        "all_paired_seed_patterns_monotone": out["paired_additive_noise"]["all_seed_patterns_monotone"],
    }, indent=2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--protocol", type=Path, default=Path("protocol/real-package-v18.py"))
    ap.add_argument("--seeds", default=",".join(str(i) for i in range(501,525)))
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--out", type=Path, default=Path("v18-publication-statistics.json"))
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
