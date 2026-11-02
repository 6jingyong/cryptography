# Structural parity determinism v1

Status: **PROMOTION GATE FAIL / ROOT CAUSE LOCALIZED TO PRESENTATION NUMERICS**

Scope: synthetic/mock benchmark only.

Two independent GitHub Actions runners each completed the full structural candidate technical + paper-v7 pipeline successfully. The strict semantic comparison nevertheless failed, so the candidate is **not promoted** by this gate.

## Frozen result

```text
replica a upstream E2E/paper-v7 = PASS
replica b upstream E2E/paper-v7 = PASS
semantic_equal                  = false
mismatch_count                  = 2
raw NPZ/manifest container hash = equal
```

The two comparison mismatches were:

```text
paper_v7_numeric_figure_plan_canonical_sha256
semantic_authority_sha256
```

All other strict comparison fields matched exactly:

```text
payload SHA
basis version
canonical B
technical summary
8-seed E5
integration result
all 24 NPZ x/y float64 arrays
all 12 paper-v7 CSV files
morphology representative selection
presentation archetype
story type
```

## Exact numeric localization

A post-run field-by-field comparison of the two numeric figure plans found only two scalar differences, both in Figure 3 table 11:

```text
matched_fit_r2
  a = 0.9470977484367036
  b = 0.9470977484367035
  delta = 1.1102230246251565e-16

delta_r2
  a = 0.9311850894810650
  b = 0.9311850894810649
  delta = 1.1102230246251565e-16
```

The deterministic paper-v7 linear baseline itself was identical. The differing `matched_fit_r2` came from upstream paper-v6 descriptive fitting.

Further comparison of `paper_v6_output/fit_results.json` showed tiny cross-run coefficient/feature differences in several tables. The current paper-v6 implementation uses `np.polyfit`, `np.linalg.lstsq`, and vector reductions in its small descriptive regressions. This is therefore a presentation-side floating-point reduction issue, not a carrier/package mismatch.

## Interpretation

This result is deliberately **not** reclassified as pass merely because the discrepancy is only ~1e-16.

It does establish an important boundary:

```text
A-v4 / structural parity / deterministic V18 / V20 package semantics = exact
paper-v7 CSV-visible source data                               = exact
remaining nondeterminism                                      = paper-v6 fitted numeric summary
```

The correct repair scope is therefore presentation-only. Carrier, structural parity, A-v4, q/delta, V20 geometry, morphology thresholds, and story rules should not be changed in response.

## Next gate

A separate repair should replace paper-v6's small descriptive least-squares/R² reductions with fixed-order deterministic scalar arithmetic while preserving the same models, candidate grids, thresholds, and outputs semantically. After that repair, a **new** independent-run determinism gate must be frozen and executed.

This v1 failure remains historical evidence even if the follow-up passes.

## Evidence

```text
workflow run        41498877024
replica a job       125460893683
replica b job       125460893961
compare job         125461476614
replica a artifact  13166414493
replica b artifact  13166439368
comparison artifact 13167547469
comparison zip sha256:fa52c53e39aa178757650ce39a6dc477e6816af2c5b7ddc0ce264ed18f528fa0
```

## Boundary

This diagnosis applies to the frozen declared CI replicas. It does not imply universal floating-point identity, real-publication behavior, or security properties.
