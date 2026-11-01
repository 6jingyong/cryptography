#!/usr/bin/env python3
"""
V15/V16 synthetic-only locator benchmark.

Models the second codebook as a set of *labeled* structural positions.
Labels are public/canonicalizable (table role, figure role, axis family, etc.),
while each position carries a coarse structural value from an alphabet.
Therefore figure/table reordering is normalized away; erasure means a labeled
position is missing/unreadable.

The benchmark studies:
- naive ordered matching vs canonical labeled matching under reorder;
- erasure/substitution robustness;
- corpus scaling from 10k to 1M descriptors;
- alphabet sizes 3 (q-only-like) and 12 (joint-structure-like).

All candidates are synthetic descriptors. No real papers or real payloads are
searched or processed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def random_different(vals, alphabet, rng):
    vals = np.asarray(vals, dtype=np.int16)
    r = rng.integers(0, alphabet - 1, size=vals.shape, dtype=np.int16)
    return r + (r >= vals).astype(np.int16)


def binom_gt_eq_probs(m, threshold, p):
    probs = np.array([
        math.comb(m, k) * (p ** k) * ((1 - p) ** (m - k))
        for k in range(m + 1)
    ], dtype=float)
    return float(probs[threshold + 1:].sum()), float(probs[threshold])


def deterministic_target(length, alphabet):
    raw = hashlib.shake_256(
        f"canonical-locator-v16-{length}-{alphabet}".encode()
    ).digest(length)
    return np.frombuffer(raw, dtype=np.uint8).astype(np.int16) % alphabet


def near_decoy_matches(target, observed, kept_idx, near_n, near_share, alphabet, rng):
    if near_n == 0:
        return np.empty(0, dtype=np.int16)

    length = len(target)
    shared = int(round(near_share * length))
    vals = rng.integers(0, alphabet, size=(near_n, length), dtype=np.int16)

    if shared:
        keys = rng.random((near_n, length), dtype=np.float32)
        idx = np.argpartition(keys, kth=shared - 1, axis=1)[:, :shared]
        rows = np.arange(near_n)[:, None]
        vals[rows, idx] = target[idx]

    return np.sum(vals[:, kept_idx] == observed[None, :], axis=1).astype(np.int16)


def canonical_labeled_trial(
    corpus_size,
    length,
    alphabet,
    erasure_rate,
    substitution_rate,
    near_fraction,
    near_share,
    seed,
):
    rng = np.random.default_rng(seed)
    target = deterministic_target(length, alphabet)

    keep = rng.random(length) >= erasure_rate
    kept_idx = np.where(keep)[0]
    retained = len(kept_idx)
    if retained == 0:
        return {"rank": corpus_size / 2, "retained": 0, "true_matches": 0}

    observed = target[kept_idx].copy()
    sub = rng.random(retained) < substitution_rate
    if np.any(sub):
        observed[sub] = random_different(observed[sub], alphabet, rng)

    true_matches = int(np.sum(observed == target[kept_idx]))

    non_targets = corpus_size - 1
    near_n = int(round(non_targets * near_fraction))
    random_n = non_targets - near_n

    # Random decoys: matches at retained labeled positions are Binomial(M, 1/A).
    p_gt, p_eq = binom_gt_eq_probs(retained, true_matches, 1.0 / alphabet)
    gt, eq, _ = rng.multinomial(
        random_n, [p_gt, p_eq, max(0.0, 1.0 - p_gt - p_eq)]
    )

    # Hard near-decoys share a fixed fraction of labeled target values.
    nmatches = near_decoy_matches(
        target, observed, kept_idx, near_n, near_share, alphabet, rng
    )
    better = int(gt) + int(np.sum(nmatches > true_matches))
    equal = int(eq) + int(np.sum(nmatches == true_matches))

    # Expected rank under random ordering among ties.
    return {
        "rank": float(1 + better + 0.5 * equal),
        "retained": int(retained),
        "true_matches": true_matches,
        "target_similarity": true_matches / retained,
    }


def summarize(cfg, seeds):
    rows = [
        canonical_labeled_trial(seed=500000 + i, **cfg)
        for i in range(seeds)
    ]
    ranks = np.asarray([r["rank"] for r in rows], dtype=float)
    retained = np.asarray([r["retained"] for r in rows], dtype=float)
    return {
        **cfg,
        "seeds": seeds,
        "mean_retained_positions": float(retained.mean()),
        "p_top5": float(np.mean(ranks <= 5)),
        "p_top20": float(np.mean(ranks <= 20)),
        "p_top50": float(np.mean(ranks <= 50)),
        "p_top100": float(np.mean(ranks <= 100)),
        "median_rank": float(np.median(ranks)),
        "p90_rank": float(np.percentile(ranks, 90)),
        "p99_rank": float(np.percentile(ranks, 99)),
        "mean_rank": float(np.mean(ranks)),
    }


def reorder_control(seed, corpus_size=10000, length=16, alphabet=12,
                    erasure=0.25, substitution=0.10,
                    near_fraction=0.01, near_share=0.50):
    rng = np.random.default_rng(seed)
    target = deterministic_target(length, alphabet)

    keep = rng.random(length) >= erasure
    pos = np.where(keep)[0]
    observed = target[pos].copy()
    sub = rng.random(len(observed)) < substitution
    if np.any(sub):
        observed[sub] = random_different(observed[sub], alphabet, rng)

    perm = rng.permutation(len(observed))
    reordered_obs = observed[perm]
    reordered_labels = pos[perm]

    candidates = rng.integers(
        0, alphabet, size=(corpus_size - 1, length), dtype=np.int16
    )
    near_n = int(round((corpus_size - 1) * near_fraction))
    if near_n:
        shared = int(round(near_share * length))
        keys = rng.random((near_n, length), dtype=np.float32)
        idx = np.argpartition(keys, kth=shared - 1, axis=1)[:, :shared]
        rr = np.arange(near_n)[:, None]
        candidates[:near_n][rr, idx] = target[idx]

    # Naive ordered scorer ignores labels and assumes current order is protocol order.
    naive_target = float(np.mean(target[pos] == reordered_obs))
    naive_scores = np.mean(candidates[:, pos] == reordered_obs[None, :], axis=1)

    # Canonical labeled scorer sorts by stable public labels before comparison.
    order = np.argsort(reordered_labels)
    aligned_labels = reordered_labels[order]
    aligned_obs = reordered_obs[order]
    canonical_target = float(np.mean(target[aligned_labels] == aligned_obs))
    canonical_scores = np.mean(
        candidates[:, aligned_labels] == aligned_obs[None, :], axis=1
    )

    def rank(target_score, scores):
        return float(1 + np.sum(scores > target_score) + 0.5 * np.sum(scores == target_score))

    return rank(naive_target, naive_scores), rank(canonical_target, canonical_scores)


def run(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    # V15 reorder control.
    rows = [reorder_control(7000 + i) for i in range(50)]
    naive = np.asarray([r[0] for r in rows])
    canonical = np.asarray([r[1] for r in rows])
    reorder_result = {
        "corpus_size": 10000,
        "length": 16,
        "alphabet": 12,
        "erasure": 0.25,
        "substitution": 0.10,
        "random_reorder": True,
        "naive_ordered": {
            "median_rank": float(np.median(naive)),
            "p90_rank": float(np.percentile(naive, 90)),
            "p_top100": float(np.mean(naive <= 100)),
        },
        "canonical_labeled": {
            "median_rank": float(np.median(canonical)),
            "p90_rank": float(np.percentile(canonical, 90)),
            "p_top100": float(np.mean(canonical <= 100)),
        },
    }

    scaling = []
    for corpus_size, seeds in [(10000, 80), (100000, 60), (1000000, 30)]:
        for alphabet in [3, 12]:
            for length in [12, 16, 24, 32]:
                for erasure in [0.10, 0.25, 0.50]:
                    cfg = dict(
                        corpus_size=corpus_size,
                        length=length,
                        alphabet=alphabet,
                        erasure_rate=erasure,
                        substitution_rate=0.10,
                        near_fraction=0.01,
                        near_share=0.50,
                    )
                    scaling.append(summarize(cfg, seeds))

    (out_dir / "v15_reorder_control_results.json").write_text(
        json.dumps(reorder_result, indent=2), encoding="utf-8"
    )
    (out_dir / "v16_canonical_labeled_scaling_results.json").write_text(
        json.dumps(scaling, indent=2), encoding="utf-8"
    )

    print(json.dumps({
        "v15_reorder": reorder_result,
        "v16_rows": len(scaling),
    }, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=Path("locator_v16_out"))
    args = ap.parse_args()
    run(args.out_dir)
