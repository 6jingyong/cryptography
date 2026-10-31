# Feature independence benchmark v6

## Question

After moving from a fixed two-channel design to an adaptive multi-channel design, the first question is not “how many features can be invented?” but:

> Which observable statistical features provide approximately independent coarse states, and which of them remain stable under ordinary data loss?

This benchmark uses synthetic dirty data only. The feature extractor does not use the latent generating function.

## Setup

- 60 independently generated dirty-data seeds
- 20 x-bins per seed
- 1,200 statistical cells total
- 7 candidate features:
  - slope
  - curvature
  - log-variance
  - IQR in log-space
  - skewness
  - residual lag-1 autocorrelation
  - residual low/high spectral-energy ratio
- every feature is quantized into 3 global tertile states
- pairwise dependence is measured using mutual information and Spearman correlation
- robustness is measured by recomputing states after random row loss

## Pairwise dependence

Each ternary feature has a marginal ceiling of:

`log2(3) = 1.585 bits`

Selected pairwise mutual information values:

| Pair | Mutual information |
|---|---:|
| slope – logvar | 0.009 bit |
| slope – skew | 0.010 bit |
| slope – autocorr | <0.001 bit |
| logvar – skew | 0.069 bit |
| curvature – slope | 0.098 bit |
| slope – IQR | 0.102 bit |
| autocorr – spectrum | 0.414 bit |

The strongest redundancy is between residual autocorrelation and the spectral ratio. Their Spearman correlation is about `0.777`, so they should not be treated as two nearly independent channels.

By contrast, slope, log-variance and skewness have low discrete mutual information with one another.

## Robustness to row loss

State recovery rate after recomputing the same feature:

| Feature | 1% loss | 5% loss | 10% loss |
|---|---:|---:|---:|
| slope | 98.7% | 95.2% | 93.1% |
| curvature | 96.8% | 91.4% | 87.2% |
| logvar | 98.4% | 93.2% | 88.6% |
| IQR | 96.5% | 88.6% | 82.9% |
| skew | 98.6% | 94.8% | 90.0% |
| autocorr | 95.5% | 83.5% | 73.5% |
| spectrum | 91.4% | 73.4% | 64.2% |

The first five are substantially more robust than the two residual-order/frequency features under this benchmark.

## Joint feature sets

### slope + logvar + skew

- joint entropy: **4.650 bits/cell**
- independent ternary ceiling: **4.755 bits/cell**
- redundancy loss: only **0.105 bit/cell**
- complete joint-state recovery after 5% row loss: **86.0%**
- after 10% row loss: **77.5%**

This is the best simple fixed set found so far when balancing low redundancy and robustness.

### slope + logvar + skew + autocorr

- joint entropy: **6.197 bits/cell**
- independent ceiling: **6.340 bits/cell**
- redundancy loss: **0.143 bit/cell**
- complete joint-state recovery after 5% row loss: **73.2%**
- after 10% row loss: **59.4%**

The fourth channel adds substantial nominal entropy, but the joint state becomes much less robust.

### slope + skew + autocorr

This combination is nearly information-theoretically additive in the observed sample:

- joint entropy: **4.737 bits/cell**
- ceiling: **4.755 bits/cell**
- redundancy: only **0.018 bit/cell**

However, its row-loss robustness is weaker than `slope + logvar + skew`, so low mutual information alone is not sufficient.

## Internal feature-map overhead

A critical negative result appears if every cell is allowed to choose one arbitrary feature from seven.

A naïve per-cell feature identifier costs:

`log2(7) = 2.807 bits/cell`

but one ternary feature carries only:

`log2(3) = 1.585 bits/cell`

Therefore:

> fully arbitrary per-cell feature selection is net-negative before ECC and other metadata.

This supports a more constrained internal-codebook design:

- use a small fixed feature set globally; or
- choose one feature set per block/figure/region rather than per cell; or
- derive the schedule from a compact seed/rule;
- allow exceptions only when their added capacity exceeds their description cost.

In MDL terms, the project should maximize:

`useful joint state entropy - feature-map description length - ECC overhead`

rather than maximizing the number of available feature types.

## Interpretation

This benchmark gives the first evidence for a useful “statistical basis”:

> slope, log-variance and skewness are relatively low-coupling and individually robust in the current synthetic dirty-data model.

The result is encouraging for multi-channel capacity, but it also rejects the simplest version of fully adaptive per-cell channel selection.

The internal password/codebook remains plausible only if it describes a compact rule family rather than a per-cell lookup table.

## Next experiment

The next useful step is to move beyond passive measurement.

For a fixed low-overhead feature set such as:

`{slope, logvar, skew}`

construct target ternary state triples and ask whether an optimizer can deliberately realize them simultaneously while preserving:

- curve smoothness;
- parent distribution similarity;
- robustness after 5% row loss;
- detector difficulty.

That will test **controllability**, not merely naturally occurring independence.
