# V18 reintegration — falsifiable migration gate

Scope: **synthetic-only**.

This is not an attempt to restore the old V18 numbers. The old precise V18 summary is non-authoritative. The migration succeeds only if a newly executable noisy-host carrier satisfies the current protocol and the predeclared gates below.

## Architecture invariant

```text
A -> rank public c -> strict open -> extract B + noisy-host b -> recover a
```

- `A` remains the long-lived public-structure locator/bootstrap protocol.
- Host model, q/QIM mode, publication step, lattice spacing, table geometry, payload offsets and decoder parameters are package-specific and belong in `B`.
- Candidate ranking must not parse `B`.

## Rebuild hypothesis

A host-aware modulo-QIM carrier should be able to quantize an existing synthetic residual coefficient to a payload coset instead of adding a clean-host coefficient on top of the residual. The expected benefit is bounded embedding displacement on a non-zero residual host while preserving exact recovery after the declared publication quantization.

This hypothesis may be rejected.

## Fixed first-pass design

The first pass is intentionally small and fixed before seeing results:

- synthetic macro families: affine / periodic / saturation / gaussian;
- 12 tables, with unique public x-grid lengths independent of q;
- non-zero smooth residual host in the free subspace;
- candidate q modes: `q=4`, then `q=2` only if q=4 fails the table distortion budget;
- q-ary Hamming protection;
- host-aware modulo-QIM: choose the nearest lattice point in the payload symbol coset;
- publication quantization remains explicit and transform-aware;
- no rate optimization and no post-result parameter sweep to rescue a failed conclusion.

## Acceptance gates

### G1 — protocol separation

PASS only if the existing A-layer ranking remains independent of B and all V18-specific settings are serialized in B.

### G2 — codec calibration

For every selected table mode:

- calibration exact block recovery = `1.0` after publication quantization;
- no selected mode may be marked feasible if its host-adjustment NRMSE exceeds that table's predeclared distortion budget;
- if neither q=4 nor q=2 is feasible for a table, the first-pass V18 hypothesis fails rather than silently falling back.

### G3 — end-to-end multi-seed

Run at least 8 independent payload seeds through full:

```text
host generation -> encode -> public package -> A locate -> strict open -> B decode -> final hash verify
```

Required:

- 8 / 8 distinct payload hashes;
- 8 / 8 exact recovery;
- Recall@100 = 1.0 under the nominal candidate corpus used for the run.

### G4 — noisy-host claim boundary

The machine result must report, not hide:

- host residual RMS;
- embedding adjustment RMS;
- adjustment / host-residual RMS ratio;
- per-table selected q and distortion budget;
- any failed calibration mode.

No undetectability/security claim follows from passing these gates.

## Refusal rule

If G2 or G3 fails under this fixed first-pass definition, the legacy statement that V18 is already a viable noisy-host carrier is **rejected for the current protocol**. A later alternative may be researched, but the failed run is retained as evidence and is not tuned away in the same result.
