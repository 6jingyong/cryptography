# Paper-v6 deterministic fit v1 — frozen repair scope

Scope: **synthetic/mock benchmark only**.

Trigger: `structural-parity-determinism-v1` failed with exactly two semantic mismatches, both caused by a `1.1102230246251565e-16` difference in Figure 3 table 11 `matched_fit_r2` / `delta_r2`. Carrier/package semantics, NPZ arrays, CSVs, E5, morphology selection, archetype, story, and raw container hashes were exact.

Post-run inspection also found tiny coefficient/feature drift in `paper_v6_output/fit_results.json` for several tables. The current `tools/paper_v6.py` uses `np.polyfit`, `np.linalg.lstsq`, and vector reductions in small descriptive fits.

## Frozen repair boundary

Create a **drop-in candidate** `tools/paper_v6_deterministic.py`. Do not modify current `tools/paper_v6.py` before gates pass.

Allowed changes inside the candidate only:

1. replace R² sums with fixed-order `math.fsum` scalar reductions;
2. replace small 2–4 column least-squares solves with fixed-order two-pass modified Gram-Schmidt + deterministic back-substitution;
3. replace current linear/polyfit descriptive fit paths with the same deterministic least-squares kernel;
4. use fixed-order matrix-vector prediction for those fits.

Frozen unchanged behavior:

- morphology labels and thresholds;
- all feature definitions other than the numerical implementation of the linear R² sub-fit;
- saturation tau grid;
- periodic cycle grid;
- bell-peak center/sigma grids;
- archetype weights;
- story-selection logic;
- E1–E6 experiment definitions and thresholds;
- claims C1/C2/C4/C5;
- paper wording and synthetic/mock limitations;
- structural parity, A-v4, deterministic V18, q/delta, and V20 geometry.

No rounding/canonicalization of final fit values is allowed as a substitute for deterministic computation.

## Gate 1 — presentation regression

The candidate paper tool must pass both:

A. the old promoted A-v3/deterministic-V18/V20 current-style E2E + paper-v7 flow;
B. the A-v4 + 11+1 structural-parity candidate E2E + paper-v7 flow.

Both must retain completed passing E5, 4 figures, 12 raw CSVs, C1/C2/C4/C5 traceability, synthetic labels, and mandatory non-provenance limitation.

The exact old floating-point fit coefficients are **not** a required regression target; the model family/grid/story/claim outcomes are.

## Gate 2 — independent-run structural candidate determinism v2

Only if Gate 1 passes, run two independent structural-candidate whole-system replicas with the same frozen `1301..1308` configuration and the same existing semantic fingerprint/comparator.

Pass condition:

```text
semantic_equal = true
mismatch_count = 0
```

The failed determinism-v1 evidence remains authoritative historical evidence and must not be overwritten.
