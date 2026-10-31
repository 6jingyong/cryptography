# Curve baseline v1

## Purpose

Test one narrow question before building any grouping optimizer:

> Can a modest amount of deliberately added within-bin scatter leave the geometric-mean center line and its discrete slopes nearly unchanged?

The baseline compares:

- `data/synthetic_dirty_v0.csv` — 246 rows
- v0 plus `data/interference_pairs_v1.csv` — 24 extra rows, about 9.76% of the base row count

The interference rows are paired approximately symmetrically in log-space around the local benchmark trend.

## Configuration

- fixed x-bin width: `1.0`
- center statistic: geometric mean of positive y values within each bin
- primary derived statistic: adjacent-bin `Δg/Δx`
- curve evaluator: natural cubic spline through the binned geometric means
- spline roughness metric: `∫(f''(x))² dx`

The spline is only an evaluator; it does not define the discrete slope representation.

## Results

| Metric | v0 | v1 with interference | Change |
|---|---:|---:|---:|
| Spline roughness | 596.529 | 484.063 | -18.9% |
| Derivative total variation | 70.254 | 61.342 | -12.7% |
| Max absolute spline slope | 7.874 | 7.565 | -3.9% |
| Discrete slope SD | 3.097 | 2.957 | -4.5% |
| Max absolute discrete slope | 7.483 | 7.052 | -5.8% |

Direct v0/v1 comparison:

- mean absolute geometric-mean shift: `0.1045`
- mean absolute geometric-mean shift: `0.186%`
- maximum absolute geometric-mean shift: `0.3740`
- maximum relative geometric-mean shift: `0.728%`
- discrete-slope RMSE: `0.3027`
- discrete-slope correlation: `0.9961`

## Interpretation

For this synthetic benchmark, adding roughly 10% extra scatter did **not** materially damage the binned geometric-mean trend. The slope sequence remained almost unchanged (`r ≈ 0.996`).

The spline roughness actually decreased. This should not be over-interpreted: the paired interference points were generated around the latent benchmark trend, so they can act like mild regularization when a noisy bin center is already displaced.

The useful conclusion is narrower:

> A distribution/scatter layer can be perturbed substantially more than the geometric center-line layer, at least in a controlled synthetic construction.

## What this does not prove

This baseline does **not** yet show that an arbitrary pool of dirty observations can be partitioned into useful roles while preserving a plausible curve. The current interference points were generated deliberately around the benchmark center.

The next experiment should therefore remove that advantage:

1. generate a larger unlabelled dirty pool;
2. forbid use of the latent function;
3. let an optimizer select which observations belong to the center-line group, distribution group, and interference group;
4. evaluate curve quality only from observable statistics;
5. compare against random selection with matched group sizes.

That is the first real test of the proposed construction problem.
