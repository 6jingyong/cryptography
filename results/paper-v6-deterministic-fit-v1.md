# Paper-v6 deterministic fit v1

Status: **REGRESSION GATES PASS / INDEPENDENT-RUN DETERMINISM STILL TO BE TESTED**

Scope: synthetic/mock benchmark only.

This repair follows the failed `structural-parity-determinism-v1` gate. That failure was localized to paper-v6 descriptive fitting at ~1e-16 scale while all carrier/package/CSV/E5 semantics were exact.

## Repair candidate

`tools/paper_v6_deterministic.py` is a drop-in candidate. It does not replace current `tools/paper_v6.py` yet.

Only the descriptive numeric fitting kernel changes:

```text
R² reductions       -> fixed-order math.fsum
small least squares -> fixed-order two-pass MGS + deterministic back-substitution
prediction           -> fixed-order scalar reduction
linear/polyfit path  -> same deterministic small-LS kernel
```

Frozen unchanged:

```text
morphology thresholds
saturation tau grid
periodic cycle grid
bell-peak mu/sigma grids
archetype weights
story logic
E1-E6 definitions/thresholds
claims C1/C2/C4/C5
paper wording and limitations
A / V18 / q / delta / structural code / V20 geometry
```

No output rounding was introduced as a substitute for deterministic computation.

## Gate 1 result

One workflow exercised the same candidate paper tool against **both** the old promoted technical path and the structural candidate path.

### Old promoted A-v3 path

```text
8/8 exact recovery
Recall@20 = 1
Recall@100 = 1
median/max rank = 1/1
paper-v7 PASS
4 figures
12 raw CSV tables
C1/C2/C4/C5 traced
story = multi_regime_characterization
archetype = materials characterization / physical chemistry
selected examples = bell 7 / linear 11 / periodic 9 / saturating 1
final bundle = 23 files
nested manifest mismatch = 0
```

### A-v4 + 11+1 structural candidate

```text
8/8 exact recovery
Recall@20 = 1
Recall@100 = 1
median/max rank = 1/1
paper-v7 PASS
4 figures
12 raw CSV tables
C1/C2/C4/C5 traced
story = multi_regime_characterization
archetype = materials characterization / physical chemistry
selected examples = bell 3 / linear 10 / periodic 7 / saturating 0
final bundle = 23 files
nested manifest mismatch = 0
```

The workflow's explicit final presentation-contract assertion passed:

```text
paper-v6 deterministic fit regression gates PASS
```

## Interpretation

The deterministic numerical repair is not a structural-candidate-specific exception. The same candidate paper tool preserves the already-audited old current path and the new structural path.

This is sufficient to proceed to a **new independent-run determinism-v2 gate**. It is not sufficient by itself to replace current paper-v6 or promote A-v4 + 11+1.

The failed determinism-v1 result remains valid historical evidence and is not rewritten as pass.

## Evidence

```text
frozen plan  results/paper-v6-deterministic-fit-v1-plan.md
candidate    tools/paper_v6_deterministic.py
workflow     41499860764
job          125464242600
artifact     13167798227
artifact zip sha256:3a0fef1de7bbbc153884fcd6c89fa6fec5c7e3579c6eb12a2eafabf79db1af96
```

## Boundary

This proves regression compatibility in the declared CI run. It does not yet prove two-independent-run semantic equality, all-platform identity, real-publication behavior, or security.
