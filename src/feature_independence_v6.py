#!/usr/bin/env python3
"""Feature-independence benchmark v6.

Synthetic-only benchmark. It measures whether several observable statistical
features provide approximately independent coarse states, and how stable those
states remain under random row loss.

No latent function is used when computing feature states.
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = [
    "slope",
    "curvature",
    "logvar",
    "iqr",
    "skew",
    "autocorr",
    "spectrum",
]


def latent(x: float) -> float:
    return 40.0 + 1.9 * x + 7.5 * math.sin(x / 2.7) + 2.7 * math.cos(x / 1.25)


def generate_pool(seed: int = 20261031, n: int = 1200):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        x = rng.uniform(0.0, 20.0)
        base = latent(x)
        batch_shift = rng.choice([-0.7, 0.0, 0.45])
        drift = 0.16 * max(0.0, x - 11.0)
        sigma = 1.3 + 0.10 * x
        y = base + batch_shift + drift + rng.gauss(0, sigma)
        if rng.random() < 0.055:
            y += rng.choice([-1, 1]) * rng.uniform(7, 18)
        p = rng.random()
        if p < 0.12:
            y = round(y, 1)
        elif p < 0.28:
            y = round(y, 2)
        else:
            y = round(y, 3)
        if y <= 0:
            y = 0.1
        rows.append((i, x, y))

    for j, idx in enumerate(rng.sample(range(n), 24), start=n):
        _, x, y = rows[idx]
        rows.append((j, x, y))
    return rows


def bucketize(rows, width: float = 1.0):
    buckets = defaultdict(list)
    for row in rows:
        _, x, _ = row
        buckets[int(math.floor(x / width))].append(row)
    return {k: buckets[k] for k in sorted(buckets)}


def skewness(a):
    a = np.asarray(a, dtype=float)
    sd = float(a.std())
    if sd < 1e-12:
        return 0.0
    return float(np.mean(((a - a.mean()) / sd) ** 3))


def residual_features(points):
    points = sorted(points, key=lambda r: r[1])
    x = np.asarray([r[1] for r in points], dtype=float)
    ly = np.log(np.asarray([r[2] for r in points], dtype=float))

    X = np.vstack([np.ones_like(x), x]).T
    beta = np.linalg.lstsq(X, ly, rcond=None)[0]
    residual = ly - X @ beta

    if len(residual) < 5:
        return 0.0, 0.0

    if np.std(residual[:-1]) < 1e-12 or np.std(residual[1:]) < 1e-12:
        autocorr = 0.0
    else:
        autocorr = float(np.corrcoef(residual[:-1], residual[1:])[0, 1])

    z = residual - residual.mean()
    power = np.abs(np.fft.rfft(z)) ** 2
    power = power[1:]
    if len(power) <= 1:
        spectral_ratio = 0.0
    else:
        cut = max(1, len(power) // 3)
        low = float(power[:cut].sum())
        high = float(power[cut:].sum())
        spectral_ratio = math.log((low + 1e-12) / (high + 1e-12))

    return autocorr, spectral_ratio


def features_for_seed(seed: int, n: int = 1200, drop_frac: float = 0.0,
                      drop_seed: int | None = None):
    rows = generate_pool(seed, n)
    buckets = bucketize(rows)

    if drop_frac > 0:
        rng = random.Random(drop_seed if drop_seed is not None else seed + 999)
        reduced = {}
        for k, points in buckets.items():
            kept = [r for r in points if rng.random() >= drop_frac]
            reduced[k] = kept if len(kept) >= 8 else list(points)
        buckets = reduced

    keys = sorted(buckets)
    geomeans = []
    xcenters = []
    local = {}

    for k in keys:
        points = buckets[k]
        y = np.asarray([r[2] for r in points], dtype=float)
        ly = np.log(y)
        geomeans.append(float(np.exp(np.mean(ly))))
        xcenters.append(float(np.mean([r[1] for r in points])))
        autocorr, spectrum = residual_features(points)
        local[k] = {
            "logvar": float(np.var(ly)),
            "iqr": float(np.quantile(ly, 0.75) - np.quantile(ly, 0.25)),
            "skew": skewness(ly),
            "autocorr": autocorr,
            "spectrum": spectrum,
        }

    geomeans = np.asarray(geomeans)
    xcenters = np.asarray(xcenters)
    slopes = np.diff(geomeans) / np.diff(xcenters)

    records = []
    for idx, k in enumerate(keys):
        row = dict(local[k])
        row["seed"] = seed
        row["bin"] = k
        row["slope"] = float(slopes[idx] if idx < len(slopes) else slopes[-1])
        if idx == 0:
            curvature = slopes[1] - slopes[0]
        elif idx >= len(slopes):
            curvature = slopes[-1] - slopes[-2]
        else:
            curvature = slopes[idx] - slopes[idx - 1]
        row["curvature"] = float(curvature)
        records.append(row)
    return records


def state(value: float, thresholds):
    q1, q2 = thresholds
    return 0 if value <= q1 else (1 if value <= q2 else 2)


def mutual_information_bits(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    mi = 0.0
    for x in np.unique(a):
        px = np.mean(a == x)
        for y in np.unique(b):
            pxy = np.mean((a == x) & (b == y))
            if pxy > 0:
                py = np.mean(b == y)
                mi += pxy * math.log2(pxy / (px * py))
    return float(mi)


def tuple_entropy_bits(values):
    counts = Counter(map(tuple, values))
    n = len(values)
    return float(-sum((c / n) * math.log2(c / n) for c in counts.values()))


def main():
    train_seeds = [20261031 + i * 137 for i in range(60)]
    records = []
    for seed in train_seeds:
        records.extend(features_for_seed(seed))

    df = pd.DataFrame(records)
    thresholds = {
        f: tuple(float(x) for x in np.quantile(df[f], [1 / 3, 2 / 3]))
        for f in FEATURES
    }

    states = pd.DataFrame(index=df.index)
    for f in FEATURES:
        states[f] = [state(v, thresholds[f]) for v in df[f]]

    mi = {
        f: {g: mutual_information_bits(states[f], states[g]) for g in FEATURES}
        for f in FEATURES
    }
    spearman = df[FEATURES].corr(method="spearman").to_dict()

    test_seeds = train_seeds[:20]
    base = {}
    for seed in test_seeds:
        for row in features_for_seed(seed):
            base[(seed, row["bin"])] = {
                f: state(row[f], thresholds[f]) for f in FEATURES
            }

    robustness = {}
    for drop_frac in (0.01, 0.05, 0.10):
        hits = {f: 0 for f in FEATURES}
        total = {f: 0 for f in FEATURES}
        for seed in test_seeds:
            for rep in range(15):
                perturbed = features_for_seed(
                    seed,
                    drop_frac=drop_frac,
                    drop_seed=seed + 10000 + rep,
                )
                for row in perturbed:
                    old = base[(seed, row["bin"])]
                    for f in FEATURES:
                        hits[f] += int(state(row[f], thresholds[f]) == old[f])
                        total[f] += 1
        robustness[str(drop_frac)] = {
            f: hits[f] / total[f] for f in FEATURES
        }

    candidate_sets = [
        ("slope", "logvar", "skew"),
        ("slope", "logvar", "skew", "autocorr"),
        ("slope", "logvar", "iqr"),
        ("slope", "curvature", "logvar"),
        ("slope", "skew", "autocorr"),
    ]

    joint = {}
    for combo in candidate_sets:
        arr = states[list(combo)].to_numpy()
        H = tuple_entropy_bits(arr)
        joint["+".join(combo)] = {
            "joint_entropy_bits_per_cell": H,
            "independent_ternary_ceiling": len(combo) * math.log2(3),
            "redundancy_bits": len(combo) * math.log2(3) - H,
        }

    for drop_frac in (0.05, 0.10):
        joint_hits = {combo: 0 for combo in candidate_sets}
        joint_total = {combo: 0 for combo in candidate_sets}
        for seed in test_seeds:
            for rep in range(10):
                perturbed = features_for_seed(
                    seed,
                    drop_frac=drop_frac,
                    drop_seed=seed + 20000 + rep,
                )
                for row in perturbed:
                    old = base[(seed, row["bin"])]
                    for combo in candidate_sets:
                        before = tuple(old[f] for f in combo)
                        after = tuple(state(row[f], thresholds[f]) for f in combo)
                        joint_hits[combo] += int(before == after)
                        joint_total[combo] += 1
        for combo in candidate_sets:
            joint["+".join(combo)][f"joint_state_recovery_{int(drop_frac*100)}pct_loss"] = (
                joint_hits[combo] / joint_total[combo]
            )

    output = {
        "configuration": {
            "train_seeds": len(train_seeds),
            "cells": len(df),
            "features": FEATURES,
            "state_quantization": "global tertiles",
            "robustness_test_seeds": len(test_seeds),
            "robustness_repetitions": 15,
        },
        "thresholds": thresholds,
        "pairwise_mutual_information_bits": mi,
        "spearman": spearman,
        "state_recovery_after_row_loss": robustness,
        "candidate_joint_entropies": joint,
        "naive_per_cell_feature_id_cost_bits": math.log2(len(FEATURES)),
        "single_ternary_feature_payload_bits": math.log2(3),
    }

    path = Path("results/feature_independence_metrics_v6.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
