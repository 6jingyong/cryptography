#!/usr/bin/env python3
"""Paper-scale capacity stress test for the synthetic dirty-channel benchmark.

This script does not implement a communication protocol. It estimates how much
coarse statistical state can exist per independent statistical cell, and shows
why raw row count is not the same thing as payload capacity.
"""
from __future__ import annotations

import itertools
import math
import random

import numpy as np


def js_divergence(p, q):
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)

    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log(a[mask] / b[mask])))

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def count_states(total=15, bins=3, js_threshold=0.02):
    # Enumerate integer histogram compositions and keep only states whose
    # divergence from the balanced histogram is below a chosen naturalness bound.
    balanced = np.full(bins, total / bins)
    out = []
    for a in range(total + 1):
        for b in range(total - a + 1):
            c = total - a - b
            v = (a, b, c)
            d = js_divergence(v, balanced)
            if d <= js_threshold:
                out.append((v, d))
    return sorted(out, key=lambda z: z[1])


def decode_three_state(counts):
    patterns = [
        np.asarray([6, 5, 4], dtype=float),
        np.asarray([5, 5, 5], dtype=float),
        np.asarray([4, 5, 6], dtype=float),
    ]
    p = counts / counts.sum()
    scores = [float(np.sum((p - q / q.sum()) ** 2)) for q in patterns]
    return int(np.argmin(scores))


def deletion_recovery(drop_prob, reps=30000, seed=20261031):
    rng = np.random.default_rng(seed)
    patterns = [np.array([6, 5, 4]), np.array([5, 5, 5]), np.array([4, 5, 6])]
    hits = total = 0
    each = max(1, reps // len(patterns))
    for state, counts in enumerate(patterns):
        cats = np.repeat(np.arange(3), counts)
        for _ in range(each):
            keep = rng.random(len(cats)) >= drop_prob
            if not keep.any():
                continue
            observed = np.bincount(cats[keep], minlength=3)
            hits += int(decode_three_state(observed) == state)
            total += 1
    return hits / total


def main():
    thresholds = [0.005, 0.01, 0.02, 0.05]
    print("Natural histogram-state counts (15 points, 3 tertiles):")
    for t in thresholds:
        n = len(count_states(js_threshold=t))
        print(f"  JS <= {t:.3f}: {n:3d} states, {math.log2(n):.3f} bits/cell")

    print("\nCurrent 3-state deletion stress test:")
    for p in [0.00, 0.01, 0.05, 0.10, 0.20]:
        print(f"  drop={p:>4.0%}: recovery={deletion_recovery(p):.3%}")

    # These are intentionally illustrative paper-scale scenarios, not empirical
    # claims about all papers. The independent-cell count matters more than rows.
    scenarios = [
        ("ordinary", 10_000, 300),
        ("data_rich", 100_000, 1_000),
        ("heavy_processed", 1_000_000, 3_000),
    ]
    schemes = [
        ("3-state", math.log2(3)),
        ("JS<=0.005", math.log2(len(count_states(js_threshold=0.005)))),
        ("JS<=0.020", math.log2(len(count_states(js_threshold=0.020)))),
        ("JS<=0.050", math.log2(len(count_states(js_threshold=0.050)))),
    ]

    print("\nIllustrative paper-scale payload from codebook channel only:")
    for name, rows, cells in scenarios:
        print(f"\n{name}: rows={rows:,}, independent_cells={cells:,}")
        for label, bpc in schemes:
            bits = cells * bpc
            print(
                f"  {label:10s}: {bpc:5.2f} bits/cell, "
                f"{bits/8:9.1f} bytes/paper, {bits/rows:.4f} bits/row"
            )


if __name__ == "__main__":
    main()
