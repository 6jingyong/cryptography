# Version Remap — where V12–V21 belong after the protocol reset

The corrected lifecycle is:

```text
A -> c -> B -> b -> a
```

This note preserves useful historical work without preserving pre-reset naming or treating unaudited summaries as current evidence.

## V12 — adaptive q

**Correct layer:** primarily `b`; concrete package choices belong in `B`.

Retain: adaptive q, q-ary ECC, shaping, protected subspace, publication quantization, exact reconstruction.

Status: **CURRENT / RETAIN**.

## V14 — historical dual-codebook experiment

Useful components remain, but the old names are retired:

```text
old locator portion -> current A
old decoder-manifest portion -> current B
```

Status: **HISTORICAL-BUT-VALID EXPERIMENTS; TERMINOLOGY STALE**.

## V16 — labeled locator

**Correct layer:** `A`.

The labeled fingerprint is historical A-layer retrieval research. References in the old report to the "second codebook" are pre-reset wording and now mean the A-layer locator, not current `B`.

Status: **HISTORICAL-BUT-VALID A-LAYER BENCHMARK**.

## V17 — publication robustness

**Correct layer:** split across `A`, `c`, and `B`.

- public labels / canonical ordering before locating -> `A`;
- package framing and publication survival -> `c`;
- actual transform, q, precision, geometry, decoder settings -> `B`.

The old V17 report contains pre-reset statements placing q/transform/ECC/geometry in "Codebook A". Those statements are stale; the experimental observations may still be retained under the remap above.

Status: **HISTORICAL-BUT-VALID RESULTS; RESPONSIBILITIES REMAPPED**.

## V18 — host-aware residual carrier

**Correct layer:** `b`, with concrete host model / q / QIM / geometry / publication parameters in `B`.

The old precise V18 summary had no auditable executable/raw-result chain and remains retired. It was **not** restored.

A new implementation now exists:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

It first generates a non-zero smooth synthetic residual host, then embeds payload symbols by moving free-subspace coefficients to the nearest modulo-QIM payload coset. The hypothesis/gates were frozen before the machine run.

Current bounded evidence:

```text
12 / 12 tables selected q=4
q=2 fallback not exercised
all selected-table calibration exact recovery = 1.0
calibration adjustment NRMSE ~= 0.000720 .. 0.001093
strictest declared budget = 0.0045
8 / 8 payload seeds distinct
8 / 8 exact full-protocol recovery
Recall@100 = 1.0
median target rank = 1
max target rank = 2
```

Embedding adjustment RMS is material but smaller than the pre-existing host residual: median ratio about `0.446`, maximum observed about `0.485` in the 8-seed run.

Status: **CURRENT_BOUNDED_REINTEGRATION** for the frozen smooth synthetic residual model only.

Still unverified:

```text
q=2 fallback effectiveness
other residual distributions
rate optimality
historical V18 quantitative summary
```

## V19 — regime selector

**Correct layer:** sender-side policy for choosing `(b,B)`. `A` may define the allowed vocabulary, but must not absorb package-specific mode choice.

The architecture is reusable; the historical quantitative summary lacks an auditable current executable/result chain.

Do not build V19 on the assumption that the current V18 mode is a universal noisy-host default. First test V18 across a frozen residual-model matrix. If the carrier is model-specific, V19 should select among explicitly supported host regimes.

Status: **NEEDS-REINTEGRATION**.

## V20 — outer ECC / verified package reliability

**Correct layer:** mainly `b` and `c`; concrete shard/parity geometry belongs in `B`; bootstrap/verification rules belong to A/c framing.

The architecture is reusable; historical quantitative values are not current machine evidence until rerun under the corrected lifecycle.

Status: **NEEDS-REINTEGRATION**.

## V21 — constrained optimizer

The retained principle is:

> protocol constraints before rate.

The old quantitative locator schema and package-geometry results were produced under the pre-reset abstraction and must not be attached directly to current Protocol-v3.

Status: **HISTORICAL-BUT-VALID PRINCIPLE ONLY; QUANTITATIVE RESULTS STALE**.

## Current audited state

The current verified spine is:

```text
A/B reset
-> V12 clean-host carrier
-> Protocol-v3 public-structure locator
-> strict open/verify
-> B+b decode
-> exact a recovery
-> E5 multi-seed nominal benchmark
-> V18 bounded smooth-residual noisy-host carrier
-> V18 current-protocol 8-seed exact-recovery benchmark
```

A separate structural-v4 synthetic descriptor benchmark records the explicit retrieval boundary for a 12-label A-layer model. It is research on the retrieval layer, not evidence that the current NPZ parser already tolerates physical table deletion or split/merge.

The next high-value test is the V18 residual-model matrix, not another rate/bit-value sweep and not yet V19 policy optimization.
