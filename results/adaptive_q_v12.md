# V12 adaptive-q package benchmark

## Main result

A heterogeneous synthetic package can select q independently per table from:

`q ∈ {8, 16, 32}`

using two gates:

1. exact q-ary Hamming recovery in a 4096-block calibration;
2. table-specific NRMSE residual budget.

Publication precision is transform-aware:

- identity-domain families: absolute quantization step;
- log-domain Gaussian family: fixed log-step, corresponding to relative precision.

The decoder uses only the published NPZ package plus manifest.

## Full adaptive package

Payload: **131,072 bytes**

Round-trip:

- exact recovery: **True**
- input SHA-256: `d9bec3e8091833a05f1ed95afc4d0e609593400d33a983898dec62402d9893b9`
- output SHA-256: `d9bec3e8091833a05f1ed95afc4d0e609593400d33a983898dec62402d9893b9`

Adaptive selection distribution:

- q=8: **4 tables**
- q=16: **4 tables**
- q=32: **4 tables**

Package capacity:

- published rows: **27,760**
- published numeric values: **444,160**
- gross: **37.773 bit/row**
- net after manifest: **35.705 bit/row**
- gross: **2.361 bit/value**
- manifest: **7,176 B (5.47% of this small 128 KiB payload)**

## Comparison with fixed q=8

Same payload, families and channel count:

| mode | exact | rows | gross bit/value | net bit/row |
|---|:---:|---:|---:|---:|
| fixed q=8 | True | 43,776 | 1.497 | 22.646 |
| adaptive q | True | 27,760 | 2.361 | 35.705 |

Adaptive-q therefore:

- raises net bits/row by **57.7%**;
- raises gross bits/value by **57.7%**;
- reduces required published rows by **36.6%**.

## Empirical q frontier under conservative spacing

With the larger calibration and stricter symbol spacing used for package-scale
exact recovery, q=32 enters later than the earlier small benchmark suggested.

Approximate entry points:

| family | q=16 region | q=32 first feasible around |
|---|---|---:|
| affine | ~1.25% NRMSE | **3.16%** |
| periodic | ~1.10% | **2.89%** |
| saturation | ~1.17% | **2.98%** |
| Gaussian/log | ~0.90% | **2.34%** |

So a useful first-order rule is now:

- residual budget below ~0.5% -> q=8;
- around 1–1.5% -> q=16;
- around 2.5–3.5% -> q=32.

This is an empirical benchmark rule, not a universal constant.

## Important correction

For affine baselines, the usual `roughness_ratio = roughness(encoded) /
roughness(baseline)` is numerically meaningless because the second derivative of
the ideal affine baseline is zero. The huge affine roughness ratios in raw
diagnostics should therefore be ignored; affine tables should use absolute
second-difference energy or residual RMS instead.

## Current interpretation

Adaptive q is useful only when the data model explicitly declares how much
raw-data scatter is acceptable. q is not a global protocol constant anymore;
it is a per-table operating point selected from the residual budget and
publication precision model.

All payloads in this benchmark are synthetic high-entropy data.
