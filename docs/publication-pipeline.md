# Publication pipeline specification

## Purpose

Codebook A must survive ordinary synthetic data-publication transforms without
depending on file order.

The publication layer is therefore split into:

```text
numeric carrier
+ public canonicalization schema
+ publication robustness mode
```

The canonicalization schema is public and is not part of Codebook B.

## Public identity requirements

A reorder-safe package needs enough public information to recover:

- table identity or table role;
- group / segment identity;
- x value or local x position;
- channel / series identity.

If these identities survive, row, column, file and table-fragment order are not
semantically meaningful.

If identity is discarded together with order, the current block decoder cannot
infer the original grouping.

## Unit normalization

For identity-domain modes, general affine unit changes should either:

1. be inverted using public unit metadata; or
2. use a future scale-normalized carrier.

For log-domain Gaussian mode, positive multiplicative scaling is naturally
absorbed by the protected constant term:

\[
\log(ay)=\log y+\log a
\]

and does not require scale metadata in the current benchmark.

## Precision modes

The final effective publication step matters more than q alone.

Define:

\[
G=\Delta/\delta_{pub}
\]

where:

- \(\Delta\) is coefficient-state spacing;
- \(\delta_{pub}\) is the effective final publication quantization.

V17 synthetic operating points:

```text
current:
    q8/q16/q32 spacing = 2 / 2.5 / 3
    highest density
    little extra re-quantization margin

guarded:
    3 / 3.5 / 4.5
    exact through 1.5x publication step in tested package

strong_guard:
    4 / 5 / 6
    exact through 1.75x

very_strong_guard:
    5 / 6.5 / 8
    exact through 3.0x
```

These are empirical package results, not guarantees.

## Decoder order

Recommended synthetic decoder pipeline:

```text
1. identify table / group / channel labels
2. canonicalize row/column/table-fragment order
3. normalize units when the transform is not naturally invariant
4. read Codebook-A mode / manifest
5. reconstruct protected basis
6. decode q-ary coefficients
7. ECC correction
8. reassemble package payload
9. strict integrity verification
```

## Boundary

This specification is for synthetic/mock package benchmarking only.
