# V18 publication statistics — paired-noise and dense re-quantization map

Scope: **synthetic-only**.

Frozen plan: `results/v18-publication-statistics-plan.md`

Source CI:

- workflow run `41342407361`
- artifact `13097591662`
- artifact SHA256 `eeb5fd905526e8e4cb3cdfb3fdc7d52179552959779f6bbfea3c1930d9168531`

No carrier parameters were changed. Fresh seeds `501..524` were used.

## Re-quantization

Exact package recovery over 24 seeds:

| factor | exact |
|---:|---:|
| 1.00 | 24/24 |
| 1.02 | 24/24 |
| 1.04 | 22/24 |
| 1.06 | 19/24 |
| 1.08 | 21/24 |
| 1.10 | 22/24 |
| 1.12 | 21/24 |
| 1.14 | 19/24 |
| 1.16 | 20/24 |
| 1.18 | 22/24 |
| 1.20 | 17/24 |
| 1.22 | 22/24 |
| 1.24 | 21/24 |
| 1.26 | 19/24 |
| 1.28 | 17/24 |
| 1.30 | 16/24 |

The response is **not monotonic**. A larger factor can recover better than a smaller one. Therefore the tested factor cannot be interpreted as a one-dimensional monotonic damage threshold. The result is consistent with grid/coset/basis alignment effects, but no specific periodic model is claimed.

All locator structural scores remained `1.0`; failures are inner-decoder failures.

## Paired additive noise

For each seed/table, one standard-normal base field was drawn and the same field was scaled across all alpha values. Thus alpha is a genuine nested noise-strength axis for each seed.

Exact package recovery:

| sigma / delta | exact | rate | Wilson 95% |
|---:|---:|---:|---:|
| 0.08 | 24/24 | 1.000 | 0.862–1.000 |
| 0.09 | 24/24 | 1.000 | 0.862–1.000 |
| 0.10 | 24/24 | 1.000 | 0.862–1.000 |
| 0.11 | 24/24 | 1.000 | 0.862–1.000 |
| 0.12 | 24/24 | 1.000 | 0.862–1.000 |
| 0.13 | 23/24 | 0.958 | 0.798–0.993 |
| 0.14 | 20/24 | 0.833 | 0.641–0.933 |
| 0.15 | 16/24 | 0.667 | 0.467–0.820 |
| 0.16 | 9/24 | 0.375 | 0.212–0.573 |
| 0.17 | 4/24 | 0.167 | 0.067–0.359 |
| 0.18 | 1/24 | 0.042 | 0.007–0.202 |

All 24 per-seed PASS→FAIL sequences are monotonic under paired scaling.

This repairs the earlier methodological ambiguity: additive-noise strength is a valid monotonic axis when the same underlying perturbation direction is scaled. The previous non-monotonic exact counts came from comparing different random noise realizations across alpha.

## Accepted conclusions

- V18 known-host feasibility remains supported.
- Broad post-embedding publication robustness remains **rejected**.
- Re-quantization factor is **not** a scalar monotonic robustness frontier on the tested grid.
- Paired additive noise produces a clear stochastic transition: 24/24 exact through `0.12 delta`, then falling success probability from `0.13 delta` onward.
- Locator retrieval remains intact; observed failures begin in the inner `B + damaged b` decoder.

## Not supported

- a universal deterministic additive-noise threshold;
- a monotonic re-quantization threshold;
- any periodic re-quantization law from this dataset alone;
- real-publication robustness;
- post-seal corruption repair;
- q=2 fallback effectiveness.

## Consequence

The next useful question is no longer “where is one V18 threshold?”. For additive noise, the right object is a success-probability curve with more independent replicates around the transition. For re-quantization, the right object is an alignment-response map; treating factor magnitude alone as damage severity is rejected.
