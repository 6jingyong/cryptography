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

Treat the repository as one system, not as a collection of carrier micro-benchmarks.

Preferred project chain:

```text
synthetic payload a
-> numeric carrier b
-> per-package reconstruction/reliability manifest B
-> optional authenticated repair data r
-> candidate package c
-> c mixed among synthetic background d
-> pre-shared A locates / bootstraps c
-> authenticated open
-> B decodes b; optional V20 repair
-> exact a
-> same current machine package/results feed the mock-paper renderer
```

The two codebooks are not peers:

```text
A = long-lived root locator / canonicalization / bootstrap protocol
B = per-package reconstruction + reliability manifest
```

## A responsibilities

A may define:

```text
fingerprint interpretation
candidate canonicalization
candidate ranking
outer package framing/bootstrap
how B is parsed
authentication vocabulary
```

A should not absorb package-specific q, table geometry, transform, ECC, payload length, shard size, or parity count.

## B responsibilities

B is created for one concrete package and may contain:

```text
actual carrier mode
actual q / delta
transform
block/table geometry
symbol/fragment ordering
inner ECC parameters
publication precision
padding and payload length
outer-code parameters
final authenticated payload binding
```

If deleting a B field makes reconstruction ambiguous, that field is not optional overhead.

## Locator rule

False positives are allowed.

```text
locator hit != valid package
```

Candidate ranking must not require parsing B. Strict authenticated open and final payload verification are authoritative.

# Priority

Use this ordering:

```text
1. A can find/bootstrap c
2. c can be opened/authenticated
3. B completely explains b/r
4. exact a is recovered
5. machine evidence can feed the paper layer without hand substitution
6. only then optimize capacity/rate/overhead
```

Do not trade locator recall, reconstruction metadata, strict verification, or paper evidence traceability for a prettier bit/value number.

# Current technical modes

## V12 clean-host carrier

Historical/current clean-host baseline using adaptive q, q-ary Hamming ECC, shaping, and publication quantization.

## V18 noisy-host carrier

Current bounded host-aware modulo-QIM carrier for explicit sender-observed synthetic residual hosts.

Evidence covers several frozen residual families and publication-damage statistics. Broad publication robustness is explicitly rejected.

## V20 logical outer reliability

Current bounded V20 uses fixed RS shard geometry around the decoded payload and logical integrity over `B + masked r`, with exact final payload SHA-256 required for acceptance.

Current fixed geometry:

```text
512-byte payload
4 x 128-byte data shards
8 parity bytes / shard
<=4 byte errors correctable / shard
32 parity bytes total = 6.25% payload parity overhead
```

Its stronger synthetic failure envelope aligns with the declared per-shard RS correction capacity in the tested grid.

## V19 selector

V19 remains sender-side policy for choosing among package modes. It is not a replacement for A and is not the immediate priority while one current integrated mode is primary.

# Preferred current end-to-end test

Use:

```text
tools/current_end_to_end.py
```

The preferred integrated test is now:

```text
current V18/V20 encode
-> c mixed among synthetic d
-> A rank candidate c without parsing B
-> authenticated V20 open
-> exact a
-> explicit decoy/tamper rejection
-> same current V20 NPZ + B manifest -> paper_v6
-> same current multiseed result -> paper E5
-> bundle hash manifest
```

The frozen current integration evidence uses seeds `901..908` and passes:

```text
8 / 8 unique payload hashes
8 / 8 exact recovery
Recall@20 = 1.0
Recall@100 = 1.0
paper E5 completed from the same current result
synthetic/mock labels retained
mandatory non-provenance limitation retained
```

# Paper pipeline

The paper layer is downstream of authoritative machine evidence.

Recommended chain:

```text
current machine package/results
-> morphology analysis
-> narrative archetype
-> generic descriptive fits
-> figure planning
-> claim hierarchy
-> machine-checkable experiment requests/results
-> clearly labeled mock paper
```

## Morphology-driven archetype

Useful visible features include:

```text
linearity
monotonicity
saturation
periodicity
single-peak prominence
peak symmetry
significant extrema
```

Candidate presentation archetypes may include:

```text
materials characterization / physical chemistry
spectroscopy / analytical chemistry
kinetics / transport / relaxation
oscillatory systems / controls
signal processing / measurement methods
```

This is a writing/presentation archetype, not provenance inference.

A peak-shaped synthetic curve may justify “peak-profile analysis”; it does not justify inventing a real Raman experiment, material, instrument, patient cohort, or mechanism.

# Generic fits

Descriptive fit examples:

```text
linear -> linear regression
saturating -> single-exponential saturation
periodic -> single-harmonic fit
bell peak -> Gaussian peak fit
```

A good fit is not mechanistic proof.

# Claim-driven experiment requests

When a claim lacks evidence, generate a machine-checkable request.

States:

```text
READY_LOCAL
REQUESTED_BENCHMARK_ENGINE
COMPLETED
FAILED
```

Only `COMPLETED` machine results may be rendered as evidence.

Preferred loop:

```text
claim
-> evidence gap
-> experiment request
-> benchmark result
-> paper update
```

# Current implementation

```text
tools/current_end_to_end.py
tools/paper_v6.py
tools/paper_claim_gate_v7.py
```

Current end-to-end evidence:

```text
results/current-e2e-integration-plan.md
results/current-e2e-integration.json
results/current-e2e-integration.md
```

# Next system-level paper milestone

Do not immediately create another carrier version just because an edge case remains.

The current paper side is thinner than the technical side. The next high-value integrated artifact should add:

```text
actual synthetic figures derived from the same current V20 NPZ
multi-figure layout selected from morphology
machine-backed captions / claim map
downloadable synthetic raw-data tables
clearly labeled mock-paper manuscript/package
bundle-level traceability from figure/data/claim back to current machine artifacts
```

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
