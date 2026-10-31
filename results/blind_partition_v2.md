# Blind partition validation v2

## Question

Can an optimizer that sees only observable `x/y` values, and never the latent generating function, select a fixed-size subset from a dirty data pool whose binned geometric means form a smooth, plausible curve with stable first-difference slopes?

This is a curve-construction test only. It does not implement a complete encoding protocol.

## Setup

- synthetic dirty pool: 1,224 rows (1,200 generated + 24 duplicate-like rows)
- x range: 0–20
- 20 fixed-width x bins
- optimizer chooses 12 observations per bin
- target: a modestly smoothed spline of the **observable full-bin geometric means**
- optimizer sees only x/y values
- candidate selection penalizes both center mismatch and unrealistically narrow within-bin spread
- comparison: 500 matched random selections for the main seed

## Main-seed result

| Metric | Optimized subset | Random median | Full pool |
|---|---:|---:|---:|
| Spline roughness | 36.04 | 285.04 | 65.19 |
| Derivative total variation | 19.97 | 55.10 | 27.02 |
| Slope SD | 2.07 | 2.58 | 2.19 |
| RMSE to observable smooth target | 0.030 | 1.049 | — |
| Slope correlation to full-pool curve | 0.955 | 0.857 | 1.000 |

The optimized subset beat all 500 random selections on:

- spline roughness;
- derivative total variation;
- RMSE to the observable smooth target.

Only about 0.4% of the random selections matched or exceeded the optimized subset's slope correlation with the full-pool curve.

## Multi-seed check

The same algorithm and hyperparameters were then tested on 12 independently generated dirty pools.

Results:

- median optimized/random roughness ratio: **0.134**
- range of roughness ratio: **0.101–0.180**
- median optimized/random RMSE ratio: **0.042**
- median slope correlation to full-pool curve: **0.956**
- slope-correlation range: **0.943–0.977**
- optimized roughness beat every matched random baseline in **12/12** seeds
- optimized RMSE beat every matched random baseline in **12/12** seeds
- optimized slope correlation exceeded the random 95th percentile in **12/12** seeds

## Interpretation

This is a positive result for the narrow construction hypothesis:

> Given a sufficiently rich dirty pool, a simple blind subset-selection process can recover a much smoother center line than random grouping while preserving the broad first-difference structure of the full observed pool.

The important point is that the optimizer never uses the latent generating function. Its target is derived only from the observable full data.

## What this does not yet prove

The experiment is deliberately easier than the full proposed system.

1. The target curve is derived from the same full pool, so the optimizer is asked to reproduce an observable smooth trend rather than an arbitrary target slope sequence.
2. The remaining observations have not yet been separated into distinct distribution / codebook / interference roles.
3. Detectability has not yet been measured with an independent classifier.
4. No constraint has yet been imposed on a second statistical channel such as a histogram or digit-frequency distribution.
5. The experiment demonstrates combinatorial freedom, not cryptographic security.

## Next test

The next useful experiment is a two-objective partition:

- center-line subset must satisfy curve / slope constraints;
- a second subset must satisfy an independently specified coarse distribution state;
- remaining rows act as interference;
- the full visible pool and every role-specific subset are evaluated for statistical plausibility.

The key question becomes whether the center-line and distribution constraints can be satisfied simultaneously without making either layer obviously artificial.
