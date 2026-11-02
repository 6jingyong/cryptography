# Deterministic basis v1 — frozen candidate plan

Scope: **synthetic/mock benchmark only**.

This milestone responds to the paper-v7 cross-run audit, which found that the same payload seed preserved payload/E5/high-level paper selection but produced different visible carrier values in 8/12 tables across two independent fresh CI runs.

This is a system-level reproducibility repair experiment. It is **not** a q/delta/RS/rate optimization.

## Problem statement

Current V18 free-subspace construction uses numerical QR + eigendecomposition + sign normalization:

```text
B
-> complete QR
-> free subspace U0
-> second-difference roughness matrix
-> eigh
-> ordered smooth free basis
```

That construction is mathematically sensible but does not currently guarantee a numerically identical basis across independent runners when eigenspaces are nearly/actually degenerate.

Paper-v7 made the consequence visible: fixed-seed paper inputs can differ numerically even while exact recovery and high-level morphology/story remain stable.

## Candidate algorithm

Do not modify current `src/noisy_host_package_v18.py` in place during the candidate stage.

Create a separate candidate engine:

```text
src/noisy_host_package_v18_deterministic.py
```

Candidate basis version:

```text
deterministic-dct-mgs-v1
```

Construction:

1. deterministically orthonormalize the protected model columns of B using two-pass modified Gram-Schmidt;
2. use a fixed ordered DCT-II cosine family as smooth candidate vectors, lowest frequency first;
3. project each candidate against the protected subspace and previously accepted free vectors;
4. use two-pass modified Gram-Schmidt with scalar products/norms accumulated by `math.fsum` rather than QR/eigh;
5. skip numerically dependent candidates using one fixed tolerance;
6. canonicalize each accepted vector sign by making its largest-absolute component positive;
7. if the DCT candidate family does not span the required complement, fall back to canonical coordinate vectors in index order under the same projection/orthogonalization rule.

The resulting basis still spans the orthogonal complement of the protected model space, but it deliberately does **not** claim to be the exact old minimum-second-difference eigenbasis.

## Manifest rule

The candidate must write:

```text
basis_version = deterministic-dct-mgs-v1
```

into current per-package B (top-level and/or every table as needed for unambiguous reconstruction).

The candidate decoder must refuse a manifest declaring a different basis version.

This is B state, not A state.

## Frozen technical configuration

No changes to:

```text
V18 q candidates
QIM delta multiples
host sigma multiple
host active dimension count
V20 shard size
V20 parity bytes
A locator rules
payload sizes
publication steps
paper morphology/claim rules
```

Primary current integration seeds remain:

```text
901..908
```

## Candidate pass gates

### Gate A — single-run protocol viability

Using the candidate engine:

```text
8 / 8 distinct payload hashes
8 / 8 exact current-V20 recovery
Recall@20 = 1.0
Recall@100 = 1.0
paper-v7 gate passes
```

If calibration or recovery fails, reject this candidate basis rather than tuning q/delta/RS in the same experiment.

### Gate B — independent-run semantic determinism

Run the same candidate configuration on **two independent GitHub Actions runners**.

Compare canonical semantic outputs, not ZIP container metadata:

```text
payload SHA-256
current-V20 E5 JSON hash
canonical B JSON hash
per-table x float64 bytes
per-table y float64 bytes
per-table exported CSV bytes
paper-v7 figure-plan numeric JSON
morphology representative selection
presentation archetype/story
```

Required:

```text
zero semantic mismatches
zero current visible-table numeric mismatches
```

SVG byte hashes are not required to match because renderer metadata may contain non-semantic timestamps. Figure source data and numeric plans must match.

### Gate C — bounded current evidence does not silently regress

Only after Gates A/B pass, rerun the existing current bounded evidence with the candidate engine where the harness supports an engine argument:

```text
V18 current-protocol reintegration
V18 residual matrix
V18 publication statistics / error profile as applicable
V20 bounded reintegration
V20 failure envelope
current E2E
paper-v7
```

The purpose is not to preserve every historical floating-point metric exactly. It is to ensure that the current bounded conclusions remain supported under the deterministic basis.

If a major current conclusion fails, do not hide it. Either reject the candidate basis or rebuild the affected claim from fresh evidence before any promotion.

## Promotion rule

The candidate does **not** replace `src/noisy_host_package_v18.py` merely because two runs match.

Promotion requires:

```text
A pass
B pass
C pass or an explicitly accepted/rebuilt bounded evidence set
```

Only after promotion may README/HANDOFF stop listing fixed-seed visible-carrier determinism as unresolved.

## Non-goals

This experiment does not prove:

```text
universal bit-identical behavior across every CPU/libm/NumPy/Python implementation
better carrier capacity
better distortion
better robustness
real-publication deployment
security / undetectability
```

The first target is narrower and project-relevant: independent fresh CI runners under the declared environment should generate the same semantic current carrier and paper inputs for the same seed.
