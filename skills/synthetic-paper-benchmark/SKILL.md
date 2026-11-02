---
name: synthetic-paper-benchmark
description: Run and render clearly labeled synthetic/mock structured-numeric carrier benchmarks using the corrected A -> c -> B/b/r -> a protocol. Keep machine results authoritative and paper presentation downstream.
---

# Synthetic Paper Benchmark

## Scope

Use this skill only for synthetic/mock research artifacts.

Every generated scientific-looking artifact must remain visibly labeled with language such as:

```text
SYNTHETIC BENCHMARK
SIMULATED DATA
MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS
```

Do not use the workflow to hide real confidential material in real publications, fabricate real evidence, impersonate real institutions/authors, or claim a synthetic result came from a real experiment.

# Project objective

Treat the repository as one system, not a collection of carrier micro-benchmarks.

```text
synthetic payload a
-> numeric carrier b
-> per-package reconstruction/reliability manifest B
-> optional authenticated repair data r
-> candidate package c mixed among synthetic background d
-> pre-shared A locates / bootstraps c
-> authenticated open
-> B decodes b; optional V20 repair
-> exact a
-> same current machine package/results feed the mock-paper bundle
```

```text
A = long-lived root locator / canonicalization / bootstrap protocol
B = per-package reconstruction + reliability manifest
```

Package-specific q, delta, transform, geometry, ECC, payload length, shard size, parity count, etc. belong in B, not A.

# Priority

Use this ordering:

```text
1. A can find/bootstrap c
2. c can be opened/authenticated
3. B completely explains b/r
4. exact a is recovered
5. machine evidence feeds the paper layer without hand substitution
6. paper figures/data/claims remain traceable to the same current artifact
7. fixed-seed paper inputs should be numerically reproducible
8. only then optimize capacity/rate/overhead
```

Do not trade locator recall, reconstruction metadata, strict verification, evidence traceability, or determinism for a prettier bit/value number.

# Current technical modes

## V18 noisy-host carrier

Current bounded host-aware modulo-QIM carrier for explicit sender-observed synthetic residual hosts.

Evidence covers frozen residual families and publication-damage statistics. Broad publication robustness is explicitly rejected.

## V20 logical outer reliability

Current bounded V20 uses fixed RS shard geometry around the decoded payload and logical integrity over `B + masked r`, with exact final payload SHA-256 required for acceptance.

```text
512-byte payload
4 x 128-byte data shards
8 parity bytes / shard
<=4 byte errors correctable / shard
32 parity bytes total = 6.25% payload parity overhead
```

Its tested stronger failure envelope aligns with the declared per-shard RS correction capacity.

## V19 selector

V19 remains sender-side policy for choosing among package modes. It is not the immediate priority while one integrated current mode is primary.

# Current end-to-end test

Use:

```text
tools/current_end_to_end.py
```

Current integrated path:

```text
current V18/V20 encode
-> c mixed among synthetic d
-> A rank candidate c without parsing B
-> authenticated V20 open
-> exact a
-> explicit decoy/tamper rejection
-> same current V20 NPZ + B -> paper analysis
-> same current multiseed result -> paper E5
```

Frozen seeds `901..908` currently pass:

```text
8 / 8 unique payload hashes
8 / 8 exact recovery
Recall@20 = 1.0
Recall@100 = 1.0
paper E5 completed from the same current result
```

# Paper bundle v7

Current implementation:

```text
tools/paper_v6.py
tools/paper_bundle_v7.py
tools/finalize_paper_bundle_v7.py
```

Paper-v7 is now the preferred paper-shaped artifact. From one fresh current V20 bundle it generates:

```text
4 SVG figures
12 raw-data CSV tables
figure_plan.json
figure_manifest.json
data_manifest.json
traceability.json
paper_v7.md
paper_v7_manifest.json
validation_result.json
paper_v7_bundle_manifest.json
```

Frozen figures:

```text
F1 -> all visible current curves
F2 -> highest-confidence example per available non-other morphology
F3 -> morphology-matched descriptive fit vs same-curve linear baseline
F4 -> same current-V20 E5 used by paper E5
```

Current selected examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

Current claim traceability:

```text
C1 -> F1/F2 + raw data
C2 -> F3 + current fit analysis + current curves
C4 -> F4 + current-V20 E5
C5 -> mandatory non-provenance/non-mechanism limitation
```

The final complete manifest covers all pre-existing paper-v7 outputs and independently verifies with zero mismatches.

Evidence:

```text
results/paper-bundle-v7-plan.md
results/paper-bundle-v7.json
results/paper-bundle-v7.md
```

# Current reproducibility boundary

Paper-v7 passes traceability **within each artifact**, but a fixed seed does not yet guarantee numerically identical visible carrier data across independent fresh runs.

Two audited runs keep stable:

```text
payload SHA-256
current-V20 E5 hash/result
morphology representative selection
presentation archetype
story type
```

but differ in:

```text
current NPZ hash
current B manifest hash
visible values in 8 / 12 tables
```

Do not call the visible current carrier numerically deterministic until this is fixed.

The leading suspected locus is numerical basis construction (`QR/eigh/sign`), which was already a known unresolved technical issue before paper-v7 exposed its artifact-level consequence.

# Paper interpretation discipline

The paper layer is downstream of authoritative machine evidence.

```text
current machine package/results
-> morphology analysis
-> narrative archetype
-> descriptive fits
-> figure planning
-> claim map
-> traceable synthetic paper bundle
```

Morphology-based archetypes are presentation choices, not provenance inference.

A peak-shaped synthetic curve may justify “peak-profile analysis”; it does not justify inventing a real Raman experiment, material, instrument, patient cohort, institution, or mechanism.

A good generic fit is descriptive, not mechanistic proof.

# Claim-driven experiment states

```text
READY_LOCAL
REQUESTED_BENCHMARK_ENGINE
COMPLETED
FAILED
```

Only `COMPLETED` machine results may be rendered as evidence.

# Next system-level milestone

Do not add another carrier version, more paper figures, or another dense damage grid next.

The next high-value milestone is deterministic visible-carrier generation:

```text
same seed + same current protocol
-> same semantic B
-> same numeric table arrays
-> same exported CSV values
-> stable paper inputs
-> existing locator / exact recovery / V20 gates remain intact
```

The first hypothesis to test is basis construction rather than paper selection or payload RNG.

Any deterministic-basis change must rerun the current V18/V20/E2E/paper-v7 gates. Do not accept numerical determinism if it silently changes A/B responsibilities or invalidates the existing bounded reliability semantics.

# Claim discipline

Never write:

```text
undetectable
proven secure
real experimental evidence
universally compatible
mechanism proven by fit
```

unless a machine benchmark genuinely establishes that exact statement—which the current project does not.

Prefer:

```text
exact in this synthetic run
all tested seeds passed
empirical operating point
descriptive fit
morphology-based presentation archetype
unresolved / pending under the current gate
not a universal guarantee
```
