---
name: synthetic-paper-benchmark
description: Run and render clearly labeled synthetic/mock structured-numeric carrier benchmarks using the corrected A → c → B → b → a protocol. Keep machine results authoritative and paper presentation downstream.
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

# Current protocol

Use the corrected object model:

```text
A -> c -> B -> b -> a
```

with background records `d`.

Definitions:

```text
A = pre-shared root locator/bootstrap codebook
c = candidate package mixed among background records
B = per-package reconstruction codebook
b = processed payload representation
a = final synthetic payload
d = unrelated background record
```

The two codebooks are not peers.

## A responsibilities

A is long-lived and shared before any package exists.

A may define:

```text
fingerprint interpretation
candidate canonicalization
candidate ranking
outer package framing/bootstrap
how B is parsed
strict outer verification rule
```

A should not need each package's concrete q, table geometry, transform, ECC, padding, or payload length.

## B responsibilities

B is created for one concrete package.

B may contain:

```text
actual carrier mode
actual q
transform
block/table geometry
symbol/fragment ordering
ECC parameters
publication precision
padding and payload length
outer-code parameters
final payload binding
```

If deleting a B field makes reconstruction ambiguous, that field is not optional overhead.

## Locator rule

False positives are allowed.

```text
locator hit != valid package
```

The A-layer objective is high target Recall@K. Strict package verification is authoritative.

# Technical priority

Use this ordering:

```text
1. A can find/bootstrap c
2. c can be opened and verified
3. B completely explains b
4. b reconstructs a
5. only then optimize capacity/rate
```

Do not trade locator recall, reconstruction metadata, or strict verification for a prettier bit/value number.

# Retained technical modes

## V12 clean-host carrier

Use adaptive q `{8,16,32}`, q-ary Hamming ECC, shaping, and publication quantization for clean/nearly-clean synthetic free subspaces.

Concrete package choices belong in B.

## V18 noisy-host carrier

For an explicit synthetic residual model, use host-aware syndrome/QIM embedding.

Residual benchmark families include:

```text
iid Gaussian
heteroscedastic Gaussian
AR(1)
batch drift
sparse-outlier mixture
```

## V19 regime selector

V19 is sender-side policy for choosing the package's inner strategy.

It is not a replacement for A.

## V20/V21 package reliability

Outer integrity and erasure-code choices belong to package reliability / B.

Rate optimization is downstream of protocol constraints.

# Real-package protocol test

The preferred end-to-end technical test is:

```text
A
-> rank candidate c
-> strict outer verify
-> extract real V12 B + b
-> invoke real V12 decoder
-> recover a
-> verify payload hash
```

Important acceptance cases:

```text
normal package -> ACCEPT
corrupt B -> REJECT
corrupt b -> REJECT
wrong A -> REJECT
locator false positive -> reject decoy, continue
```

# Paper pipeline

The paper layer is downstream of authoritative machine evidence.

Recommended chain:

```text
machine result
-> morphology analysis
-> narrative archetype
-> generic descriptive fits
-> figure planning
-> story / claim hierarchy
-> experiment requests
-> completed experiment results
-> paper
```

## Morphology-driven domain archetype

The renderer may infer a narrative style from visible synthetic curve morphology.

Useful features:

```text
linearity
monotonicity
saturation
periodicity
single-peak prominence
peak symmetry
significant extrema
```

Candidate narrative archetypes may include:

```text
materials characterization / physical chemistry
spectroscopy / analytical chemistry
kinetics / transport / relaxation
oscillatory systems / controls
signal processing / measurement methods
```

This is a writing archetype, not provenance inference.

A peak-shaped synthetic curve may justify "peak-profile analysis"; it does not justify inventing a real Raman experiment, material, instrument, patient cohort, or mechanism.

# Generic fits

Descriptive fit examples:

```text
linear -> linear regression
saturating -> single-exponential saturation
periodic -> single-harmonic fit
bell peak -> Gaussian peak fit
```

A good fit is not mechanistic proof.

# Figure and story planning

Main figures should favor evidence breadth:

```text
morphology coverage
fit quality
morphology confidence
relevance to the primary claim
```

Do not automatically promote the prettiest/highest-R² curve to the primary conclusion.

Claim roles may include:

```text
primary_conclusion
supporting_quantification
presentation_support
technical_control
limitation_negative_result
supplementary_control
```

Material limitations may be forced into the Discussion.

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

A requested experiment must remain pending until a benchmark result exists.

Useful request classes:

```text
morphology perturbation stability
leave-one-table-out story stability
fit ablation
domain-archetype stability
multi-seed full re-encode / locator / exact recovery
limitation-retention audit
```

Preferred loop:

```text
claim
-> evidence gap
-> experiment request
-> benchmark result
-> paper update
```

# Current implementation

The cleaned repository exposes the current paper line through:

```text
tools/paper_v6.py
```

Historical v3/v4/v5/v6 helper chains are intentionally removed from the current working tree.

# Output package

A current paper package may contain:

```text
paper_v6.md
paper_manifest.json
experiment_results_v6.json
story_plan.json
claim_evidence_map.json
paper_plan.json
fit_results.json
domain_archetype.json
figures/
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
morphology-based narrative archetype
unresolved / pending under the current gate
not a universal guarantee
```
