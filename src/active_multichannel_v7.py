#!/usr/bin/env python3
"""Synthetic active-multichannel construction benchmark v7.

This benchmark does NOT implement a complete communication protocol. It tests a
narrow research question: can a dirty-data pool actively realize several coarse
statistical states at once while preserving a plausible center line?

Channels:
- slope residual relative to the observable full-pool trend;
- log-variance relative to the parent bin;
- skew shift relative to the parent bin.

The key v7 change is adaptive feasibility: a cell is not assumed to support all
27 ternary combinations. Only states observed to be locally realizable are
counted in the capacity proxy.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

import feature_independence_v6 as fi


def geom_mean(points):
    return float(np.exp(np.mean(np.log([r[2] for r in points]))))


def local_features(points):
    ly = np.log(np.asarray([r[2] for r in points], dtype=float))
    return geom_mean(points), float(np.var(ly)), fi.skewness(ly)


def state(value, thresholds):
    return 0 if value <= thresholds[0] else (1 if value <= thresholds[1] else 2)


def train_relative_thresholds(seeds=8, n=2400, subset_count=24, samples=200):
    logvar_rel, skew_delta, slope_resid = [], [], []
    for i in range(seeds):
        seed = 20261031 + i * 137
        buckets = fi.bucketize(fi.generate_pool(seed, n))
        keys = sorted(buckets)
        full = [local_features(buckets[k]) for k in keys]
        x = np.asarray([np.mean([r[1] for r in buckets[k]]) for k in keys])
        g = np.asarray([v[0] for v in full])
        base_slope = np.diff(g) / np.diff(x)
        rng = random.Random(seed + 555)
        candidate_g = []
        for j, k in enumerate(keys):
            fg, flv, fsk = full[j]
            gs = []
            for _ in range(samples):
                subset = rng.sample(buckets[k], subset_count)
                gm, lv, sk = local_features(subset)
                logvar_rel.append(math.log((lv + 1e-12) / (flv + 1e-12)))
                skew_delta.append(sk - fsk)
                gs.append(gm)
            candidate_g.append(gs)
        for j in range(1, len(keys)):
            dx = x[j] - x[j - 1]
            for t in range(samples):
                slope_resid.append(
                    (candidate_g[j][t] - candidate_g[j - 1][t]) / dx
                    - base_slope[j - 1]
                )
    return {
        "logvar_rel": tuple(np.quantile(logvar_rel, [1 / 3, 2 / 3])),
        "skew_delta": tuple(np.quantile(skew_delta, [1 / 3, 2 / 3])),
        "slope_resid": tuple(np.quantile(slope_resid, [1 / 3, 2 / 3])),
    }


def build_candidates(seed, thresholds, n=2400, subset_count=24, trials=1800):
    rows = fi.generate_pool(seed, n)
    buckets = fi.bucketize(rows)
    keys = sorted(buckets)
    full = [local_features(buckets[k]) for k in keys]
    x = np.asarray([np.mean([r[1] for r in buckets[k]]) for k in keys])
    base_g = np.asarray([v[0] for v in full])
    base_slope = np.diff(base_g) / np.diff(x)
    rng = random.Random(seed + 444)
    candidates = {}

    for j, k in enumerate(keys):
        fg, flv, fsk = full[j]
        raw = []
        for _ in range(trials):
            ids = rng.sample(range(len(buckets[k])), subset_count)
            subset = [buckets[k][i] for i in ids]
            gm, lv, sk = local_features(subset)
            rv = math.log((lv + 1e-12) / (flv + 1e-12))
            ds = sk - fsk
            raw.append((ids, gm, rv, ds))

        gscale = max(np.std([r[1] for r in raw]), 1e-6)
        candidates[k] = [
            {
                "ids": ids,
                "gm": gm,
                "lv_state": state(rv, thresholds["logvar_rel"]),
                "sk_state": state(ds, thresholds["skew_delta"]),
                "cost": 0.15 * ((gm - fg) / gscale) ** 2,
            }
            for ids, gm, rv, ds in raw
        ]

    return buckets, keys, x, base_g, base_slope, candidates


def construct(seed, thresholds, trials=1800, beam_width=40, min_candidates=2):
    buckets, keys, x, base_g, base_slope, candidates = build_candidates(
        seed, thresholds, trials=trials
    )
    rng = random.Random(seed + 909)

    first = {}
    for lv in range(3):
        for sk in range(3):
            arr = [c for c in candidates[keys[0]] if c["lv_state"] == lv and c["sk_state"] == sk]
            if len(arr) >= min_candidates:
                first[(lv, sk)] = sorted(arr, key=lambda c: c["cost"])[:500]
    if not first:
        return None

    pair = rng.choice(sorted(first))
    beam = sorted([(c["cost"], [c]) for c in first[pair]], key=lambda z: z[0])[:beam_width]
    feasible_counts = [len(first)]

    for j in range(1, len(keys)):
        transitions = {}
        dx = x[j] - x[j - 1]
        for lv in range(3):
            for sk in range(3):
                curr = [c for c in candidates[keys[j]] if c["lv_state"] == lv and c["sk_state"] == sk]
                if len(curr) < min_candidates:
                    continue
                curr = sorted(curr, key=lambda c: c["cost"])[:500]
                tmp = {0: [], 1: [], 2: []}
                for cost, path in beam:
                    prev = path[-1]
                    for c in curr:
                        residual = (c["gm"] - prev["gm"]) / dx - base_slope[j - 1]
                        ss = state(residual, thresholds["slope_resid"])
                        scale = max(abs(thresholds["slope_resid"][0]), abs(thresholds["slope_resid"][1]), 0.4)
                        nc = cost + c["cost"] + 0.02 * (residual / scale) ** 2
                        tmp[ss].append((nc, path + [c]))
                for ss, arr in tmp.items():
                    if arr:
                        transitions[(ss, lv, sk)] = sorted(arr, key=lambda z: z[0])[:beam_width]
        if not transitions:
            return None
        chosen = rng.choice(sorted(transitions))
        beam = transitions[chosen]
        feasible_counts.append(len(transitions))

    path = beam[0][1]
    g = np.asarray([c["gm"] for c in path])
    slope = np.diff(g) / np.diff(x)
    slope_resid = slope - base_slope
    sp = CubicSpline(x, g, bc_type="natural")
    sp0 = CubicSpline(x, base_g, bc_type="natural")
    grid = np.linspace(x.min(), x.max(), 800)
    rough = float(np.trapezoid(sp(grid, 2) ** 2, grid))
    rough0 = float(np.trapezoid(sp0(grid, 2) ** 2, grid))

    return {
        "seed": seed,
        "capacity_bits": float(sum(math.log2(c) for c in feasible_counts)),
        "bits_per_cell": float(sum(math.log2(c) for c in feasible_counts) / len(keys)),
        "mean_feasible_states": float(np.mean(feasible_counts)),
        "minimum_feasible_states": int(min(feasible_counts)),
        "mean_abs_gmean_shift": float(np.mean(np.abs(g / base_g - 1.0))),
        "slope_residual_rmse": float(np.sqrt(np.mean(slope_resid ** 2))),
        "roughness_ratio": float(rough / rough0),
    }


def main():
    thresholds = train_relative_thresholds()
    runs = []
    for i in range(6):
        result = construct(20261031 + i * 137, thresholds)
        runs.append(result)

    good = [r for r in runs if r is not None]
    summary = {
        "successful_runs": len(good),
        "bits_per_cell_median": float(np.median([r["bits_per_cell"] for r in good])),
        "bits_per_cell_range": [
            float(min(r["bits_per_cell"] for r in good)),
            float(max(r["bits_per_cell"] for r in good)),
        ],
        "mean_feasible_states_median": float(np.median([r["mean_feasible_states"] for r in good])),
        "gmean_shift_median": float(np.median([r["mean_abs_gmean_shift"] for r in good])),
        "slope_residual_rmse_median": float(np.median([r["slope_residual_rmse"] for r in good])),
        "roughness_ratio_median": float(np.median([r["roughness_ratio"] for r in good])),
    }

    output = {
        "thresholds": {k: [float(v[0]), float(v[1])] for k, v in thresholds.items()},
        "summary": summary,
        "runs": runs,
        "note": "Construction-capacity benchmark only; no complete protocol or robust payload rate is claimed.",
    }
    path = Path("results/active_multichannel_repro_v7.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
