# V18 residual-model matrix

**SYNTHETIC BENCHMARK ONLY.**

## Result

All five challenge residual families passed the frozen matrix:

```text
iid Gaussian                 PASS
heteroscedastic Gaussian     PASS
AR(1), rho=0.85              PASS
low-frequency drift          PASS
Gaussian + sparse outliers   PASS
```

Under the predeclared interpretation rule, the matrix result is:

```text
GENERAL_V18_SUPPORTED
```

but this phrase means only:

> The unchanged q4-first host-aware modulo-QIM carrier passed these five equal-energy synthetic host-residual families and the declared current-protocol gate.

It does **not** mean universal noisy-host robustness.

## Calibration

Every model passed all 12 tables. No table needed q=2:

```text
q=4 selected: 12 / 12 for every model
q=2 selected:  0 / 12 for every model
```

Maximum selected-table host-adjustment NRMSE stayed close across models:

| model | max NRMSE |
|---|---:|
| iid Gaussian | 0.0011032 |
| heteroscedastic Gaussian | 0.0010971 |
| AR(1) | 0.0010922 |
| low-frequency drift | 0.0010817 |
| Gaussian + sparse outliers | 0.0011046 |

The strictest pre-existing table budget remained `0.0045`, so no model required a budget change or rescue sweep.

Calibration median adjustment-RMS / host-residual-RMS ratios remained around `0.439–0.446`; the largest calibration ratio was `0.483` in the low-frequency-drift model.

## Current-protocol gate

Each model ran seeds `201–204` through:

```text
host generation
-> encode
-> public package
-> A locate
-> strict open
-> B decode
-> final hash verify
```

For **every** model:

```text
4 / 4 payload hashes distinct
4 / 4 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
maximum target rank = 1
V18 package-specific state present in B = yes
```

The largest full-run adjustment-RMS / host-residual-RMS ratio was approximately `0.491` for low-frequency drift.

## Why 5/5 PASS is not the end of V18 robustness work

This result is informative, but its mechanism also explains why the five residual **shapes** are not the hardest remaining variable.

The sender sees the host before embedding. The carrier projects the observed host into the free subspace and moves those coefficients directly to the desired modulo-QIM cosets. Therefore the original host distribution is largely converted into an **embedding-distortion** question rather than an unknown-interference question.

With free-subspace RMS energy normalized across models, all five distributions produced very similar adjustment costs. The all-pass result is therefore consistent with the architecture rather than evidence that arbitrary future corruption is harmless.

The matrix does **not** test:

```text
unknown noise added after embedding
stronger publication re-quantization after embedding
unknown coefficient drift after the sender loses control
q=2 fallback behavior
basis mismatch / cross-platform numerical mismatch
real data or real publication pipelines
```

## Consequence

V18 can now be treated as **distribution-broad within the declared known-host synthetic matrix**, rather than smooth-host-only.

However, the next high-value falsification target should move from **host distribution before embedding** to **channel damage after embedding**. That is the variable the host-aware modulo-QIM construction does not cancel by design.

A useful next matrix should freeze post-embedding conditions such as:

```text
coarser re-quantization factors
small additive free-subspace noise relative to delta
combined re-quantization + noise
```

and record the exact failure frontier instead of optimizing rate.

Machine summary: `results/v18-residual-matrix.json`.
Frozen plan: `results/v18-residual-matrix-plan.md`.
CI source: workflow run `41340671651`, artifact `13096538512`.
