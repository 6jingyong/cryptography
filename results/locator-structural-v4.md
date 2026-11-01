# A-layer structural robustness v4 — audit rebuild

**SYNTHETIC DESCRIPTOR BENCHMARK ONLY.**

This rebuild replaces the unauditable v4 numbers previously named in `HANDOFF.md`.
It uses an explicit model: 12 stable labels, 1,000,000 candidates, 10,000 rank trials,
1% near-decoys with **exactly 6/12** correct label→ID pairs, and conservative ties-ahead ranking.

`physical_reorder` and `labeled_split_merge` assume public labels restore the same 12 logical
identities before scoring. They do not claim that the current Protocol-v3 NPZ parser accepts
missing or extra physical tables.

| scenario | R@20 | R@100 | R@1000 | median rank | p90 rank |
|---|---:|---:|---:|---:|---:|
| baseline | 1.0000 | 1.0000 | 1.0000 | 1.0 | 1.0 |
| physical_reorder | 1.0000 | 1.0000 | 1.0000 | 1.0 | 1.0 |
| labeled_split_merge | 1.0000 | 1.0000 | 1.0000 | 1.0 | 1.0 |
| deletion_25pct | 1.0000 | 1.0000 | 1.0000 | 2.0 | 3.0 |
| deletion_50pct | 0.0000 | 0.0000 | 0.0000 | 10589.0 | 10621.0 |
| substitution_20pct | 0.9283 | 0.9793 | 0.9812 | 1.0 | 14.0 |
| deletion_50pct_plus_substitution_20pct | 0.0000 | 0.0000 | 0.0000 | 13640.0 | 29139.5 |

## Failure boundary

With exactly 10,000 strong near-decoys tied at six correct pairs, any target reduced to
six or fewer correct pairs necessarily ranks worse than 10,000 under the ties-ahead policy.
Therefore a claim such as `50% deletion -> Recall@1000 = 1` is mathematically incompatible
with this stated near-decoy model and tie policy.

The 20% substitution condition is stochastic per label. Its median trial remains rank 1,
but a small tail crosses the six-match near-decoy boundary; that is why Recall@1000 is
0.9812 rather than 1.0.

This is an A-layer retrieval stress result, not cryptographic-security or undetectability evidence.
