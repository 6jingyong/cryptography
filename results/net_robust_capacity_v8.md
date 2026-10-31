# Net robust capacity v8

## Question

v7 achieved about 4.4 bits/cell of **construction capacity** with an adaptive feasible-state alphabet over three coarse features:

- slope residual relative to the observable full-pool trend;
- log-variance relative to the parent cell;
- skew shift relative to the parent cell.

v8 freezes the global thresholds on disjoint synthetic training pools and asks what remains after robustness, codebook overhead, and a simple detectability test.

## Setup

- 10 synthetic training seeds for frozen thresholds;
- 12 disjoint held-out test seeds;
- 2,400 generated observations + 24 duplicate-like records per pool;
- 20 x-bins;
- 24 selected observations per cell;
- 1,000 candidate subsets per cell;
- beam width 30;
- global feature rule is fixed across every test seed.

The held-out test does **not** retune thresholds per seed.

## Construction capacity

Across 12/12 successful held-out constructions:

- median raw adaptive capacity: **4.40 bits/cell**;
- range: **4.27–4.44 bits/cell**;
- median absolute geometric-mean shift: **0.54%**;
- median spline roughness ratio to the full-pool center line: **1.20×**.

So the v7 construction result survives a disjoint frozen-rule test.

## Robustness

The same selected subsets were then perturbed and decoded with the same frozen thresholds.

| Perturbation | Joint 3-channel state recovery | Slope | Log-variance | Skew |
|---|---:|---:|---:|---:|
| 1% random row loss | 87.5% | 88.7% | 98.5% | 98.2% |
| 5% random row loss | 62.9% | 68.9% | 92.7% | 92.0% |
| 10% random row loss | 49.9% | 61.0% | 86.3% | 86.3% |
| Bootstrap resampling | 21.0% | 43.3% | 66.1% | 61.5% |

The slope channel is the main robustness bottleneck. Its state depends on two adjacent selected cells, so small center shifts can flip a coarse slope state even when the two within-cell distribution states remain stable.

## Optimistic ECC-adjusted capacity proxy

Treating the empirical joint-state error as a q-ary symmetric channel gives an optimistic capacity approximation:

| Perturbation | Approx. net bits/cell |
|---|---:|
| 1% row loss | **3.32** |
| 5% row loss | **1.84** |
| 10% row loss | **1.23** |
| Bootstrap resampling | **0.24** |

These are not achieved ECC rates. They are upper-style channel-capacity proxies that show how quickly raw construction capacity can shrink once symbol errors are included.

For the current rule, **5% row loss reduces the useful-capacity proxy from about 4.4 to about 1.84 bits/cell**.

## Detectability

A detector was trained on observable cell-summary features only. Each structured cell was paired with a matched random 24-point subset from the same parent bin. Cross-validation was grouped by synthetic seed.

| Detector | Mean ROC-AUC | Fold SD |
|---|---:|---:|
| Logistic regression | 0.556 | 0.076 |
| Random forest | 0.648 | 0.066 |
| Histogram gradient boosting | 0.638 | 0.059 |

This is a meaningful negative result.

The linear detector is only slightly above chance, but the nonlinear detectors reach roughly **0.64–0.65 AUC**. Therefore the current selection rule leaves a weak-to-moderate learnable footprint in these synthetic summary statistics.

An AUC near 0.5 would not prove indistinguishability; conversely, AUC above 0.5 is direct evidence that the present construction is not yet statistically neutral.

## Internal-codebook overhead

The adaptive idea still benefits from a small global rule, but overhead must be amortized over many cells.

As an intentionally narrow parameter-only floor, suppose the rule stores:

- six float32 threshold values;
- one 64-bit seed;
- four uint16 integer parameters.

That is **320 bits** before implementation/protocol description.

Amortized cost:

| Cells sharing the same rule | Parameter-only overhead |
|---:|---:|
| 20 | 16.00 bits/cell |
| 300 | 1.07 bits/cell |
| 1,000 | 0.32 bits/cell |
| 3,000 | 0.11 bits/cell |

So a tiny 20-cell carrier cannot justify a bespoke internal codebook. The low-overhead premise only becomes credible when one compact rule governs hundreds or thousands of cells, or when protocol constants are shared independently of the payload.

## Main conclusion

v8 changes the interpretation of the project:

> **4.4 bits/cell is a real construction result, but not yet a realistic payload rate.**

Under a modest 5% missing-row stress test, the current three-feature system falls to roughly **1.8 bits/cell** before codebook overhead. It also has a detectable nonlinear selection footprint around **0.65 AUC**.

The bottleneck is now clear:

1. make state regions wider / add margin so row loss does not flip states;
2. especially redesign the slope channel, which currently dominates symbol errors;
3. add naturalness penalties that directly suppress detector features;
4. keep the codebook global enough that its fixed cost is amortized across many cells.

The next optimization target should therefore be:

`net robust bits/cell subject to detector AUC <= target`

rather than raw state count alone.
