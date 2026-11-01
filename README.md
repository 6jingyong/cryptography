# cryptography

Synthetic-only research on structured numeric carriers, locator protocols, and paper-shaped benchmark reporting.

> **This repository is a synthetic/mock benchmark. It does not claim real experimental evidence and is not intended for hiding real confidential material in real scientific publications.**

## Current protocol

The project now uses the corrected two-codebook model:

```text
pre-shared root codebook A
        ↓
locate / bootstrap candidate package c
        ↓
extract per-package codebook B + processed payload b
        ↓
B explains b
        ↓
recover synthetic payload a
```

With background records:

```text
public collection = c + d + d + d + ...
```

The key distinction is:

```text
A = long-lived root locator/bootstrap codebook
B = per-package reconstruction codebook
```

A does **not** need to know each package's concrete q, transform, ECC, or table geometry. Those package-specific values belong in B.

See [`protocol/README.md`](protocol/README.md).

## Repository map

```text
protocol/
  README.md
  schema-v1.json
  version-remap-v12-v21.md
  real-package-v2.py
  real-package-v2-tests.py
  real-package-v3.py

src/
  adaptive_q_*_v12.py
  locator_erasure_scaling_v16.py
  publication_robustness_v17.py

tools/
  paper_v6.py

results/
  README.md
  milestone reports
  compact authoritative summaries

skills/synthetic-paper-benchmark/
  SKILL.md
```

## Technical line

The current tree keeps the protocol-relevant executable core small. Later V18–V21 findings are summarized in `results/current-summary.json` and remapped in the protocol history note; their pre-reset scripts remain in Git history until they are reintegrated cleanly into the corrected protocol.

The retained technical milestones are:

| Version | Role after protocol reset |
|---|---|
| V12 | adaptive-q numeric carrier for processed payload `b` |
| V16 | labeled locator / erasure benchmark for A-layer discovery |
| V17 | publication/canonicalization robustness across A/c/B boundaries |
| V18 | host-aware residual carrier for noisy synthetic hosts |
| V19 | sender-side regime selector for choosing `(b,B)` strategy |
| V20 | outer reliability and verified package rate |
| V21 | constrained optimizer: protocol guarantees first, rate last |
| Protocol v2 | real V12 `B+b` package tested end-to-end under `A→c→B→b→a` |
| Protocol v3 | A-layer fingerprint bound to actual NPZ public table structure; multi-seed E5 closed |

The project deliberately does **not** optimize rate before locator/bootstrap/reconstruction constraints.

## Current real-package protocol test

A real synthetic V12 package was inserted into the corrected protocol:

```text
a = 2,048 synthetic bytes
B = real V12 manifest
b = real V12 published NPZ
candidate corpus = 3,000
near-decoys = 30
fingerprint erasure = 25%
fingerprint substitution = 10%
```

Observed:

```text
target rank = 1
accepted rank = 1
exact a recovery = TRUE
```

Protocol tests also confirm:

```text
corrupt B -> reject
corrupt b -> reject
wrong A -> reject
locator false positive -> reject decoy, continue, accept real c
```

See [`results/protocol-real-package-v2.md`](results/protocol-real-package-v2.md) and [`results/protocol-real-package-v3.md`](results/protocol-real-package-v3.md).

## Paper line

The paper toolchain is downstream of machine results.

```text
machine results
    ↓
morphology analysis
    ↓
domain narrative archetype
    ↓
generic descriptive fits
    ↓
figure / story planning
    ↓
claim-evidence map
    ↓
experiment requests
    ↓
completed machine experiments only
    ↓
mock paper
```

The paper layer may change presentation, terminology, section order, and figure selection. It may not invent benchmark numbers or convert requested work into completed evidence.

Paper v6 requested six validation experiments. All six now have machine results and pass under the recorded synthetic criteria; E5 completed an 8-seed full re-encode → locator → exact-recovery cycle with eight unique payload hashes.

See [`results/paper-v6-experiments.json`](results/paper-v6-experiments.json) and `tools/paper_v6.py`.

## Start here

For the protocol:

```bash
python protocol/real-package-v2.py \
  --engine src/adaptive_q_package_v12.py \
  --payload-bytes 2048 \
  --channels 4 \
  --corpus-size 3000
```

For protocol tests:

```bash
python protocol/real-package-v2-tests.py
```

The checked-in test script is synthetic-only and expects the repository layout above.

## Historical versions

The current working tree intentionally removes many V1–V11 exploratory scripts, old `dual-codebook` naming, duplicated docs, and obsolete mock-paper examples.

Nothing is erased from Git history.

See [`protocol/version-remap-v12-v21.md`](protocol/version-remap-v12-v21.md) for how retained findings map onto the corrected architecture.

## Scope

Allowed repository use:

```text
synthetic payloads
synthetic candidate corpora
numeric carrier benchmarks
locator robustness
publication-transform robustness
machine-verifiable recovery
clearly labeled mock-paper generation
```

Not represented by this repository:

```text
real experimental evidence
real confidential payload hiding
real-paper covert deployment
claims of universal undetectability
claims of cryptographic security for the carrier itself
```

MIT licensed.
