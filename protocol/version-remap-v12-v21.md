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

**Correct layer:** `b`, with concrete mode parameters in `B`.

The architecture maps cleanly, but no auditable V18 executable/raw result is present in the current repository history inspected during the 2026-11-02 audit. Precise V18 numbers preserved in old summaries are therefore not current machine evidence.

Status: **NEEDS-REINTEGRATION**.

## V19 — regime selector

**Correct layer:** sender-side policy for choosing `(b,B)`. `A` may define the allowed vocabulary, but must not absorb package-specific mode choice.

The architecture is reusable; the historical quantitative summary lacks an auditable current executable/result chain.

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
-> V12 carrier
-> Protocol-v3 public-structure locator
-> strict open/verify
-> B+b decode
-> exact a recovery
-> E5 multi-seed nominal benchmark
```

A separate structural-v4 synthetic descriptor benchmark now records the explicit retrieval boundary for a 12-label A-layer model. It is research on the retrieval layer, not evidence that the current v3 NPZ parser already tolerates physical table deletion or split/merge.

The next integration target after the audit gate is V18, not another rate/bit-value sweep.
