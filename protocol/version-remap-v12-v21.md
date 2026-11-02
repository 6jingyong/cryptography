# Version Remap — where V12–V21 belong after the protocol reset

The corrected lifecycle is:

```text
A -> locate/rank c -> authenticated open -> B decodes b -> optional outer repair -> a
```

This note preserves useful historical work without preserving pre-reset naming or treating unaudited summaries as current evidence.

## V12 — adaptive q

**Correct layer:** primarily `b`; concrete package choices belong in `B`.

Status: **CURRENT / RETAIN**.

## V14 — historical dual-codebook experiment

```text
old locator portion -> current A
old decoder-manifest portion -> current B
```

Status: **HISTORICAL-BUT-VALID EXPERIMENTS; TERMINOLOGY STALE**.

## V16 — labeled locator

**Correct layer:** `A`.

Status: **HISTORICAL-BUT-VALID A-LAYER BENCHMARK**.

## V17 — publication robustness

**Correct layer:** split across `A`, `c`, and `B`.

- public labels / canonical ordering before locating -> `A`;
- package framing and publication survival -> `c`;
- actual transform, q, precision, geometry, decoder settings -> `B`.

Status: **HISTORICAL-BUT-VALID RESULTS; RESPONSIBILITIES REMAPPED**.

## V18 — host-aware residual carrier

**Correct layer:** `b`, with concrete host model / q / QIM / geometry / publication parameters in `B`.

Historical precise V18 summaries remain retired.

Current evidence covers the rebuilt non-zero-host carrier, five frozen sender-observed residual families, paired additive-noise statistics, alignment-dependent re-quantization, and residual error profiling after the inner Hamming layer.

Key boundary:

- broad V18 publication robustness is **REJECTED**;
- re-quantization is not a scalar monotonic severity axis;
- paired additive-noise strength is monotonic per seed under the paired construction;
- transition-region residual failures are sparse after Hamming correction.

Status: **CURRENT_BOUNDED_REINTEGRATION**.

Still unresolved: q=2 fallback effectiveness, cross-platform deterministic basis generation, mechanistic re-quantization alignment model, and universal/real-publication robustness.

## V19 — regime selector

**Correct layer:** sender-side policy for choosing `(b,B)`. `A` may define allowed vocabulary but must not absorb package-specific mode choice.

A future V19 must select only among modes with explicit audited evidence envelopes.

Status: **NEEDS-REINTEGRATION**.

## V20 — outer logical reliability

**Correct layer:** package reliability around decoded `a`; concrete code/shard/parity geometry belongs in `B`; repair bytes may be carried separately in `c`; A supplies long-lived bootstrap/authentication vocabulary but no package-specific parity geometry.

Historical V20 numerical summaries remain retired.

Current implementation:

```text
protocol/real-package-v20.py
protocol/v20-bounded-reintegration.py
protocol/v20-failure-envelope.py
```

Fixed current geometry:

```text
512-byte payload
4 x 128-byte RS data shards
8 parity bytes / shard
<=4 byte errors corrected per shard
32 parity bytes total = 6.25% payload parity overhead
```

Logical integrity:

```text
V20 tag authenticates B + masked repair bytes r
raw numeric b is not in the V20 tag
final acceptance requires exact SHA-256 match to authenticated payload target in B
```

Initial fresh-seed matrix (`701..724`) passed all six frozen damaged conditions, with 49/49 attempted repairs successful.

A second fresh-seed failure-envelope map (`801..824`) held the geometry fixed:

```text
paired noise:
  0.18 delta -> 24/24
  0.20 delta -> 17/24, exactly 7 packages above the >4-byte/shard RS bound
  0.22 delta -> 5/24, exactly 19 packages above the bound
  >=0.25     -> 0/24, all packages above the bound

re-quantization:
  1.50x -> 24/24
  1.75x -> 20/24, exactly 4 packages above the >4-byte/shard RS bound
  >=2.00x -> 0/24, all packages above the bound
```

Across every individual run in the frozen stronger grid:

```text
V20 failure <=> at least one 128-byte shard exceeded four candidate byte errors
```

Mismatch count: **0**. Locator score remained 1.0 throughout. Manifest and repair-field bitflip controls were rejected.

Status: **CURRENT_BOUNDED_REINTEGRATION with measured capacity-aligned failure envelope**.

Still unresolved: structurally different damage such as table deletion/truncation/burst loss, optimal/minimal parity overhead, and real-publication robustness.

## V21 — constrained optimizer

Retained principle:

> protocol constraints before rate.

Old quantitative locator schema and package-geometry results remain stale.

Status: **HISTORICAL-BUT-VALID PRINCIPLE ONLY; QUANTITATIVE RESULTS STALE**.

## Current audited spine

```text
A/B reset
-> V12 clean-host carrier
-> Protocol-v3 public-structure locator
-> exact clean-host recovery / E5
-> V18 bounded noisy-host carrier
-> V18 publication-damage statistics + sparse residual profile
-> V20 fixed 6.25% RS logical repair envelope
-> V20 initial post-seal gate PASS
-> V20 stronger failure envelope mapped to its declared RS shard capacity
```

Structural-v4 remains a separate A-layer descriptor benchmark; it is not proof that the physical NPZ parser tolerates arbitrary table deletion or split/merge.

Further points on the same numeric damage axes have diminishing value. Next work should either test structurally different damage with the fixed V20 geometry or reintegrate V19 over already-audited modes.
