# Version Remap — where V12–V21 belong after the protocol reset

The corrected lifecycle is:

```text
A -> locate/rank c -> authenticated open -> B decodes b -> optional outer repair -> a
```

This note preserves useful historical work without preserving pre-reset naming or treating unaudited summaries as current evidence.

## V12 — adaptive q

**Correct layer:** primarily `b`; concrete package choices belong in `B`.

Retain: adaptive q, q-ary ECC, shaping, protected subspace, publication quantization, exact reconstruction.

Status: **CURRENT / RETAIN**.

## V14 — historical dual-codebook experiment

Useful components remain, but old names are retired:

```text
old locator portion -> current A
old decoder-manifest portion -> current B
```

Status: **HISTORICAL-BUT-VALID EXPERIMENTS; TERMINOLOGY STALE**.

## V16 — labeled locator

**Correct layer:** `A`.

The labeled fingerprint is historical A-layer retrieval research. Old references to the "second codebook" now map to A-layer locator state, not current B.

Status: **HISTORICAL-BUT-VALID A-LAYER BENCHMARK**.

## V17 — publication robustness

**Correct layer:** split across `A`, `c`, and `B`.

- public labels / canonical ordering before locating -> `A`;
- package framing and publication survival -> `c`;
- actual transform, q, precision, geometry, decoder settings -> `B`.

Old statements placing q/transform/ECC/geometry in "Codebook A" are stale.

Status: **HISTORICAL-BUT-VALID RESULTS; RESPONSIBILITIES REMAPPED**.

## V18 — host-aware residual carrier

**Correct layer:** `b`, with concrete host model / q / QIM / geometry / publication parameters in `B`.

The historical precise V18 summary remains retired. It was not restored.

Current implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

Current evidence now covers:

- smooth non-zero synthetic residual host;
- five frozen equal-energy sender-observed residual families;
- current-protocol exact-recovery runs;
- paired additive-noise publication-damage statistics;
- alignment-dependent re-quantization behavior;
- residual error multiplicity/location after the existing inner Hamming layer.

Key boundary:

- broad V18 publication robustness is **REJECTED**;
- re-quantization factor is **not** a scalar monotonic severity axis;
- paired additive-noise strength is monotonic per seed under the paired construction;
- transition-region residual failures are sparse after Hamming correction.

Status: **CURRENT_BOUNDED_REINTEGRATION**.

Still unresolved:

```text
q=2 fallback effectiveness
cross-platform deterministic basis generation
mechanistic model of re-quantization alignment bands
universal / real-publication robustness
historical V18 quantitative summary
```

## V19 — regime selector

**Correct layer:** sender-side policy for choosing `(b,B)`. `A` may define allowed vocabulary, but must not absorb package-specific mode choice.

The architecture remains reusable; historical quantitative values are not current evidence.

Current V18 is bounded rather than universal, so a future V19 must select only among modes with explicit evidence envelopes.

Status: **NEEDS-REINTEGRATION**.

## V20 — outer logical reliability

**Correct layer:** package reliability around decoded `a`; concrete code/shard/parity geometry belongs in `B`; repair bytes may be carried separately in `c`; A supplies long-lived bootstrap/authentication vocabulary but no package-specific parity geometry.

Historical V20 numerical summaries remain retired.

Current implementation:

```text
protocol/real-package-v20.py
protocol/v20-bounded-reintegration.py
```

The current first-pass geometry was frozen before results:

```text
512-byte payload
4 x 128-byte RS data shards
8 parity bytes / shard
32 parity bytes total = 6.25% payload parity overhead
```

V20 uses **logical integrity**, not old raw-b byte integrity:

```text
v20 tag authenticates B + masked repair bytes r
raw numeric b is not in the V20 tag
final acceptance requires exact SHA-256 match to authenticated payload target in B
```

This permits post-seal numeric transforms of b to be decoded/repaired rather than rejected before inner decoding.

Frozen fresh-seed matrix (`701..724`) passed:

```text
clean: 24/24
noise 0.14 / 0.15 / 0.16 delta: V20 24/24 each
requant 1.06 / 1.20 / 1.30x: V20 24/24 each
49 / 49 attempted repairs successful
all final accepted hashes exact
all locator structural scores 1.0
repair-field tamper control rejected
```

Status: **CURRENT_BOUNDED_REINTEGRATION** for the declared synthetic post-seal matrix.

Still unresolved:

```text
stronger / structurally different damage envelope
burst or concentrated >4-byte-per-shard errors
B/r loss or corruption beyond authenticated rejection
optimal/minimal parity overhead
real-publication robustness
historical V20 quantitative summary
```

## V21 — constrained optimizer

Retained principle:

> protocol constraints before rate.

Old quantitative locator schema and package-geometry results were produced under the pre-reset abstraction and must not be attached directly to current protocol evidence.

Status: **HISTORICAL-BUT-VALID PRINCIPLE ONLY; QUANTITATIVE RESULTS STALE**.

## Current audited spine

```text
A/B reset
-> V12 clean-host carrier
-> Protocol-v3 public-structure locator
-> exact clean-host recovery / E5
-> V18 bounded noisy-host carrier
-> V18 residual-model + publication-damage characterization
-> V18 sparse residual-error profile
-> V20 fixed 6.25% RS logical repair envelope
-> V20 frozen 24-seed / six-condition post-seal gate PASS
```

Structural-v4 remains a separate A-layer descriptor benchmark; it is not proof that the physical NPZ parser tolerates arbitrary table deletion or split/merge.

Next work should hold the current V20 geometry fixed and map its failure envelope before changing redundancy or optimizing rate.
