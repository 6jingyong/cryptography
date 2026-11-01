---
name: synthetic-paper-benchmark
description: Generate a clearly labeled synthetic/mock paper-style benchmark package that demonstrates the repository's numeric carrier, locator, decoder, publication pipeline, and strict verification. Never represent synthetic results as real experiments.
---

# Synthetic Paper Benchmark Skill

## What this skill is for

Use this skill when you want a **paper-shaped demonstration package** for the
repository's synthetic carrier benchmark.

The skill is not "write a fake scientific claim."

It is:

```text
WRITE
  synthetic payload -> numeric carrier

FIND
  structural fingerprint -> candidate ranking

VERIFY
  candidate decode -> strict integrity check
```

and then package those benchmark steps into something that looks like a
scientific supplementary package so a human can inspect it easily.

Every generated artifact must remain visibly labeled as synthetic/mock.

---

# Non-negotiable boundary

The skill may generate:

- deterministic synthetic numeric data;
- synthetic high-entropy benchmark payloads;
- mock scientific tables;
- mock-paper prose;
- SVG figures;
- CSV excerpts;
- reproducibility manifests;
- locator benchmarks over synthetic candidate corpora;
- exact-recovery / SHA-256 verification reports.

It must not:

- fabricate evidence for a real scientific claim;
- impersonate an existing paper, journal, lab, author, institution, company, or dataset;
- invent human/animal experiments and present them as observations;
- remove the synthetic/mock label;
- hide a real secret, credential, confidential file, model weight, or private dataset;
- build a real-paper covert retrieval network;
- optimize a real carrier to evade reviewers, security tools, or forensic detection.

If a requested package would cross those boundaries, keep the same benchmark
structure but replace the payload/data/claim with synthetic surrogates.

---

# The three-layer mental model

## 1. WRITE — Codebook A

Codebook A answers:

> How should this numeric table be interpreted?

Current fields may include:

```text
family
transform
q
ECC mode
block geometry
publication precision
publication guard mode
```

The numeric carrier is modeled as:

\[
z=B(x)\beta+U(x)c
\]

where:

- \(B(x)\beta\) is the protected macro structure;
- \(U(x)c\) is the controllable carrier component.

Current q candidates are:

\[
q\in\{8,16,32\}
\]

with q-ary Hamming coding and one shaping degree of freedom.

The skill should use the repository's actual encoder/decoder when available,
rather than inventing reported metrics.

---

## 2. FIND — Codebook B

Codebook B is only a locator.

It answers:

> Which synthetic candidate packages are worth trying first?

A locator position is better represented as a labeled structural value:

\[
F=\{(\ell_i,v_i)\}
\]

For example:

```text
label = table role
value = (family, q)
```

False positives are allowed.

The skill should report:

- candidate corpus size;
- target rank;
- Recall@K when running repeated trials;
- structural similarity;
- near-decoy configuration.

Do not describe locator success as final authentication.

---

## 3. VERIFY — strict verifier

The final decision belongs to the verifier.

A benchmark package may check:

```text
format
length
version
keyed integrity tag
SHA-256 equality
```

The paper-style report should explicitly distinguish:

\[
\text{recognizability}
\neq
\text{interpretability}
\neq
\text{verified recovery}
\]

A candidate that ranks highly but fails strict verification is a normal
retrieval false positive, not a protocol failure.

---

# Inputs

## Required

### `benchmark_goal`

One or more of:

```text
capacity
exact_recovery
publication_robustness
locator_retrieval
distortion
multichannel_scaling
transform_comparison
residual_model_compatibility
```

### `macro_families`

Choose synthetic families such as:

```text
affine
periodic
harmonic
saturation
gaussian_peak
symmetric
hysteresis_like
```

### `package_geometry`

For example:

```text
tables = 12
channels_per_table = 8
payload_bytes = 8192
```

### `publication_model`

Examples:

```text
absolute_step
log_step
decimal_rounding
significant_digits
guarded_1p5x
guarded_3x
```

---

## Optional

### `q_candidates`

Default:

```text
[8, 16, 32]
```

### `locator_config`

For example:

```text
candidate_count = 1000
near_decoys = 20
shared_structure_fraction = 0.5
target_substitution_rate = 0.1
```

### `paper_length`

```text
short
standard
extended
```

### `output_formats`

Any subset of:

```text
markdown
svg
csv
json
npz
zip
```

---

# Required workflow

## Step 0 — establish synthetic scope

Before generating anything, make the benchmark subject generic.

Good:

```text
synthetic periodic response
simulated saturation index
mock Gaussian peak response
```

Bad:

```text
named hospital patient trial
named laboratory alloy experiment
real drug efficacy result
real company's proprietary benchmark
```

The title and first screen of every paper-style artifact must visibly say one
of:

```text
SYNTHETIC BENCHMARK
SIMULATED DATA
MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS
```

---

## Step 1 — generate deterministic macro structure

For each table/series define:

\[
y_{macro}=f(x,\theta)
\]

with reproducible parameters.

Examples:

Periodic:

```text
[1, sin(wx), cos(wx), sin(2wx), cos(2wx)]
```

Affine:

```text
[1, x]
```

Gaussian in log domain:

```text
[1, x, x^2]
```

Saturation:

```text
[1, exp(-t/tau)]
```

Do not claim these functions came from real measurements.

---

## Step 2 — run Codebook-A carrier

For each table:

1. construct protected basis \(B\);
2. construct free basis \(U\);
3. choose q using the benchmark's current adaptive-q policy;
4. encode deterministic synthetic high-entropy bytes;
5. apply q-ary ECC;
6. use shaping to reduce declared structural cost;
7. apply the explicit publication transform.

The decoder must operate from the published package + manifest, not from the
original unencoded values.

---

## Step 3 — apply publication pipeline

When relevant, test:

```text
row reorder
column reorder
table split/merge
known unit conversion
decimal rounding
significant-digit rounding
re-quantization
```

Classify each operation as:

```text
natural invariant
canonicalizable
destructive at current operating point
```

Public canonicalization labels are schema, not Codebook B.

---

## Step 4 — run Codebook-B locator benchmark

Build the synthetic structural fingerprint from declared coarse features such
as:

```text
(family, q)
(family, q, transform)
(table role, family, q)
```

Place the target among a synthetic candidate corpus.

Include random decoys and, when requested, hard near-decoys.

Report target rank or Recall@K.

---

## Step 5 — strict verification

Run strict verification independently of locator score.

At minimum report:

```text
best high-ranking decoy -> ACCEPT / REJECT
true target -> ACCEPT / REJECT
payload SHA-256
decoded SHA-256
exact equality
```

A paper-style result must never imply that locator rank alone proves identity.

---

## Step 6 — generate paper-style artifacts

Minimum recommended package:

```text
paper.md
README.md
manifest_readable.json
verification.json
figures/
  figure_1_*.svg
  figure_2_*.svg
data/
  *_sample.csv
```

Optional machine-readable benchmark artifacts:

```text
carrier/
  published_*.npz
  manifest_*.json
  results_*.json
```

---

# Required paper structure

## Title block

Must visibly include:

```text
MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS
```

## Abstract

State:

- that all data are synthetic;
- benchmark goal;
- package geometry;
- exact recovery outcome;
- locator outcome if present.

Do not write a real-world scientific conclusion.

## 1. Benchmark objective

Explain WRITE / FIND / VERIFY in plain language.

## 2. Synthetic-data construction

Explain macro families and protected structure.

## 3. Carrier algorithm

Explain adaptive q, ECC, shaping, and publication mode at the level needed for
reproducibility.

## 4. Published numeric example

Include at least one figure comparing:

```text
baseline macro
vs
published carrier
```

## 5. Locator and verifier

Show that a plausible decoy can rank highly yet be rejected.

## 6. Recovery result

Include:

- payload bytes;
- published rows;
- gross bit/value;
- q distribution;
- exact recovery;
- input/output SHA-256.

## 7. Limitations

Explicitly say the benchmark does not establish compatibility with real
experimental processes.

## 8. Reproducibility

Point to manifest, verification output, generator, and machine-readable data.

---

# Example A — minimal teaching package

Input concept:

```text
goal = explain the system
families = [affine, periodic, gaussian_peak]
payload_bytes = 1024
channels = 4
candidates = 500
paper_length = short
```

Expected story:

```text
1. generate synthetic payload
2. encode a few numeric tables
3. show one baseline-vs-published curve
4. rank target among 500 mock candidates
5. reject one high-ranking decoy
6. decode target
7. SHA-256 PASS
```

Use this for README/Quick Start examples.

---

# Example B — standard 12-table mock paper

Input concept:

```text
goal = [exact_recovery, locator_retrieval, publication_robustness]

families:
  affine:      low / medium / high residual budget
  periodic:    low / medium / high residual budget
  saturation:  low / medium / high residual budget
  gaussian:    low / medium / high residual budget

payload_bytes = 8192
channels = 8
q_candidates = [8, 16, 32]

locator:
  candidate_count = 1000
  near_decoys = 20
  shared_structure_fraction = 0.5
```

Expected paper structure:

```text
Table 1-3   affine      q8/q16/q32-like operating points
Table 4-6   periodic    q8/q16/q32-like operating points
Table 7-9   saturation  q8/q16/q32-like operating points
Table 10-12 gaussian    q8/q16/q32-like operating points
```

Expected figures:

```text
Figure 1  baseline vs published periodic series
Figure 2  adaptive-q schedule across tables
Figure 3  locator -> strict verifier flow
```

The checked-in complete example should be referenced rather than duplicating
large outputs in this file.

---

# Quality checks before finalizing an artifact

The skill must verify:

### Labeling

- title contains synthetic/mock label;
- figures contain synthetic/mock label;
- CSV samples contain a synthetic marker;
- README states the package is not real experimental evidence.

### Reproducibility

- generator or exact construction parameters are included;
- manifest is machine-readable;
- payload and decoded SHA-256 are recorded.

### Architecture clarity

A new reader should be able to identify:

```text
WRITE
FIND
VERIFY
```

without first understanding all math.

### Metric honesty

Do not report:

```text
100% robust
undetectable
cryptographically secure
realistic experimental evidence
```

unless the benchmark actually establishes that exact claim. In general it does
not.

Prefer:

```text
exact in this synthetic run
all tested seeds passed
empirical Top-K result
not a universal guarantee
```

---

# Repository example

The repository's complete example should live under a path such as:

```text
examples/mock-paper/
```

and contain a visibly labeled mock paper plus data/figures/manifests.

A lightweight generator should live under:

```text
examples/generate_mock_paper.py
```

The example is a teaching artifact, not evidence for a real scientific result.
