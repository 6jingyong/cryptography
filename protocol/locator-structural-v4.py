#!/usr/bin/env python3
"""A-layer structural locator stress model v4 (synthetic descriptors only).

This is an audit reconstruction, not a capacity optimization and not evidence
that protocol/real-package-v3.py already implements deletion/split/merge
canonicalization.

Model:
- 12 stable public labels, each with one expected A-layer ID.
- corpus size = 1,000,000 candidates.
- 1% strong near-decoys.
- every near-decoy has EXACTLY 6/12 correct label->ID pairs.
- all other candidates are uniform random permutations of the 12 IDs.
- score = number of correct A-layer pairs out of the fixed 12-label contract;
  deleted or substituted target pairs score as non-matches.
- ties count fully ahead of the target (conservative retrieval rank).
- random-corpus ranks are sampled exactly from the permutation fixed-point tail
  probability; the million descriptors do not need to be materialized.

"physical reorder" and "labeled split/merge" are descriptor-level
canonicalization controls: labels are assumed to restore the same 12 logical
identities before scoring. They are NOT claims that the current v3 NPZ parser
can accept a changed physical table count.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

LENGTH = 12
CORPUS_SIZE = 1_000_000
TRIALS = 10_000
NEAR_FRACTION = 0.01
NEAR_EXACT_MATCHES = 6
SEED = 4_004_004


def derangements(n: int) -> int:
    # exact integer recurrence avoids floating rounding in the probability table
    if n == 0:
        return 1
    if n == 1:
        return 0
    a, b = 1, 0
    for k in range(2, n + 1):
        a, b = b, (k - 1) * (a + b)
    return b


def permutation_fixed_point_tail(n: int = LENGTH) -> dict[int, float]:
    denom = math.factorial(n)
    exact = {
        k: math.comb(n, k) * derangements(n - k) / denom
        for k in range(n + 1)
    }
    return {m: float(sum(exact[k] for k in range(m, n + 1))) for m in range(n + 1)}


def intact_matches(mode: str, rng: np.random.Generator) -> int:
    if mode in {"baseline", "physical_reorder", "labeled_split_merge"}:
        return 12
    if mode == "deletion_25pct":
        return 9  # exactly 3 of 12 labels deleted
    if mode == "deletion_50pct":
        return 6  # exactly 6 of 12 labels deleted
    if mode == "substitution_20pct":
        # Independent structural extraction errors. A substituted pair is wrong.
        return int(np.sum(rng.random(12) >= 0.20))
    if mode == "deletion_50pct_plus_substitution_20pct":
        # Six labels survive deletion, then each surviving pair can be wrong.
        return int(np.sum(rng.random(6) >= 0.20))
    raise ValueError(mode)


def run_scenario(mode: str, rng: np.random.Generator, tails: dict[int, float]) -> dict:
    non_targets = CORPUS_SIZE - 1
    near_n = int(round(non_targets * NEAR_FRACTION))
    random_n = non_targets - near_n
    ranks = np.empty(TRIALS, dtype=np.int64)
    intact = np.empty(TRIALS, dtype=np.int16)

    for i in range(TRIALS):
        m = intact_matches(mode, rng)
        intact[i] = m

        # Strong near-decoys have exactly six correct A-pairs. Under conservative
        # tie handling, every one of them counts ahead whenever target m <= 6.
        near_ahead = near_n if m <= NEAR_EXACT_MATCHES else 0

        # A uniform random permutation has >=m fixed points with exact probability
        # tails[m]. Draw how many such random candidates occur in this corpus.
        random_ahead = int(rng.binomial(random_n, tails[m]))
        ranks[i] = 1 + near_ahead + random_ahead

    return {
        "scenario": mode,
        "median_intact_matches": float(np.median(intact)),
        "recall_at_20": float(np.mean(ranks <= 20)),
        "recall_at_100": float(np.mean(ranks <= 100)),
        "recall_at_1000": float(np.mean(ranks <= 1000)),
        "median_rank": float(np.median(ranks)),
        "p90_rank": float(np.percentile(ranks, 90)),
        "max_rank": int(np.max(ranks)),
    }


def build_result() -> dict:
    rng = np.random.default_rng(SEED)
    tails = permutation_fixed_point_tail()
    scenarios = [
        "baseline",
        "physical_reorder",
        "labeled_split_merge",
        "deletion_25pct",
        "deletion_50pct",
        "substitution_20pct",
        "deletion_50pct_plus_substitution_20pct",
    ]
    rows = [run_scenario(mode, rng, tails) for mode in scenarios]
    return {
        "version": "locator-structural-v4-audit-rebuild",
        "scope": "synthetic-descriptor-only",
        "seed": SEED,
        "model": {
            "labels": LENGTH,
            "candidate_corpus": CORPUS_SIZE,
            "rank_trials": TRIALS,
            "near_decoy_fraction": NEAR_FRACTION,
            "near_decoy_count": int(round((CORPUS_SIZE - 1) * NEAR_FRACTION)),
            "near_decoy_exact_pairs": NEAR_EXACT_MATCHES,
            "random_decoys": "uniform random permutations of 12 IDs",
            "score": "correct A-defined label->ID pairs / fixed 12-label contract",
            "tie_policy": "all ties count ahead",
            "random_rank_sampling": "exact permutation fixed-point tail + binomial corpus draw",
        },
        "important_boundary": {
            "descriptor_canonicalization_only": True,
            "current_v3_npz_deletion_support_claimed": False,
            "current_v3_split_merge_support_claimed": False,
        },
        "results": rows,
    }


def to_markdown(result: dict) -> str:
    lines = [
        "# A-layer structural robustness v4 — audit rebuild",
        "",
        "**SYNTHETIC DESCRIPTOR BENCHMARK ONLY.**",
        "",
        "This rebuild replaces the unauditable v4 numbers previously named in `HANDOFF.md`.",
        "It uses an explicit model: 12 stable labels, 1,000,000 candidates, 10,000 rank trials,",
        "1% near-decoys with **exactly 6/12** correct label→ID pairs, and conservative ties-ahead ranking.",
        "",
        "`physical_reorder` and `labeled_split_merge` assume public labels restore the same 12 logical",
        "identities before scoring. They do not claim that the current Protocol-v3 NPZ parser accepts",
        "missing or extra physical tables.",
        "",
        "| scenario | R@20 | R@100 | R@1000 | median rank | p90 rank |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in result["results"]:
        lines.append(
            f"| {r['scenario']} | {r['recall_at_20']:.4f} | {r['recall_at_100']:.4f} | "
            f"{r['recall_at_1000']:.4f} | {r['median_rank']:.1f} | {r['p90_rank']:.1f} |"
        )
    lines += [
        "",
        "## Failure boundary",
        "",
        "With exactly 10,000 strong near-decoys tied at six correct pairs, any target reduced to",
        "six or fewer correct pairs necessarily ranks worse than 10,000 under the ties-ahead policy.",
        "Therefore a claim such as `50% deletion -> Recall@1000 = 1` is mathematically incompatible",
        "with this stated near-decoy model and tie policy.",
        "",
        "This is an A-layer retrieval stress result, not cryptographic-security or undetectability evidence.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path, default=Path("locator-structural-v4.json"))
    ap.add_argument("--md-out", type=Path, default=Path("locator-structural-v4.md"))
    args = ap.parse_args()
    result = build_result()
    args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    args.md_out.write_text(to_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
