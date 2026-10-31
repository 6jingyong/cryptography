# Two-channel validation v3

## Question

Can the same dirty x/y pool support two simultaneous role-specific structures?

1. a center-line subset whose binned geometric means form a smooth curve with stable first-difference slopes;
2. a second, disjoint codebook subset whose within-bin y distribution matches a prescribed coarse state;
3. all remaining observations act as interference.

The optimizer sees only observable x/y values. No latent generating function is used for selection.

## Codebook v0

This first codebook is intentionally weak and interpretable. In every x-bin, the full-pool y values define three tertile regions. A 15-point codebook subset is asked to match one of three count patterns:

- state 0: `[6, 5, 4]` — mildly lower-heavy;
- state 1: `[5, 5, 5]` — balanced;
- state 2: `[4, 5, 6]` — mildly upper-heavy.

Among subsets satisfying the requested state, the selector prefers a geometric mean and log-space spread close to the full bin. This makes the distribution state deliberately subtle rather than maximizing separation.

## Main seed

Pool: 1,224 observations, 20 x-bins.

Per bin:

- 12 observations assigned to the center-line role;
- 15 observations assigned to the codebook role;
- the remainder assigned to interference.

### Center channel

| Metric | Optimized | Random baseline median |
|---|---:|---:|
| Spline roughness | 27.04 | 266.25 |
| Slope correlation to full pool | 0.960 | 0.852 |

The addition of the codebook role does not alter the already-selected center-line subset.

### Codebook channel

| Metric | Optimized codebook | Random subset median |
|---|---:|---:|
| Target-state hit rate | 100% | — |
| Feasible bins | 100% | — |
| Mean JS divergence from full-bin tertile histogram | 0.00231 | 0.01343 |
| Mean absolute geometric-mean shift | 0.169% | 1.103% |
| Mean log-spread ratio to full bin | 1.004 | 0.938 |

So in the main seed, all 20 requested distribution states were realized while the selected codebook subsets were, by these coarse diagnostics, *closer* to the parent-bin distribution than ordinary random 15-point subsets.

This is possible because the state patterns are mild: the selector is not asked to create an obviously skewed histogram, only a small relative bias that remains decodable under the agreed three-state rule.

## Multi-seed check

The same construction was tested on 12 independently generated dirty pools.

- 11/12 seeds achieved 100% codebook feasibility and state recovery in all 20 bins.
- One seed achieved 95% because one bin did not contain enough remaining observations in the requested tertile after center-line selection.
- Median codebook JS divergence to the full-bin distribution was about `0.00234`, versus about `0.01365` for random codebook subsets.
- Median absolute codebook geometric-mean shift was about `0.247%`, versus roughly `1.19%` for random subsets.
- Mean log-space spread remained close to the full-bin spread (median ratio about `0.997`).
- The center-line roughness remained roughly 9%–20% of matched random-subset roughness across the 12 seeds.

Raw per-seed values are in `results/two_channel_multiseed_v3.csv`.

## Interpretation

This is a positive result for the first two-channel construction:

> A sufficiently rich dirty pool can be partitioned into a smooth center-line subset and a second, disjoint coarse-distribution subset while leaving a large interference remainder.

The two objectives did not strongly compete in this benchmark because they consume different combinatorial freedom: the center channel controls the geometric center of a small subset, while the codebook channel controls a mild distributional pattern in a different subset.

## Important limitation

This codebook is deliberately easy. Three tertile-count states carry only a small amount of information, and the requested patterns differ by only two observations between the low and high tails.

The next meaningful stress test is therefore not to add more machinery, but to increase codebook difficulty along one axis at a time:

1. increase the number of states;
2. reduce codebook sample count;
3. require stronger robustness to missing observations;
4. use a less direct statistic than the same tertile histogram used by the selector;
5. jointly constrain the center slope sequence rather than merely preserving the observable smooth trend.

The current result establishes feasibility, not capacity or security.
