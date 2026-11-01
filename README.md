# cryptography

Synthetic-only research on structured numeric carriers, locator protocols, and paper-shaped benchmark reporting.

> **This repository is a synthetic/mock benchmark. It does not claim real experimental evidence and is not intended for hiding real confidential material in real scientific publications.**

## Current protocol

The corrected lifecycle is:

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
A = long-lived root locator / canonicalization / bootstrap codebook
B = per-package reconstruction codebook
```

A does **not** need each package's concrete q, transform, ECC, table geometry, payload length, or padding. Those package-specific values belong in B.

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
  locator-structural-v4.py

src/
  adaptive_q_*_v12.py
  locator_erasure_scaling_v16.py
  publication_robustness_v17.py

tools/
  paper_v6.py
  audit_current.py
  paper_claim_gate_v7.py

results/
  README.md
  e5-multiseed-final.json
  locator-structural-v4.json
  locator-structural-v4.md
  paper-v6-experiments.json
  paper-claim-audit-v7.json
  paper-claim-audit-v7.md
  current-summary.json
```

## Audited technical spine

The current machine-verifiable spine is:

| Version | Audited role |
|---|---|
| V12 | adaptive-q numeric carrier for processed payload `b` |
| V16 | historical labeled locator / erasure research for A-layer discovery |
| V17 | historical publication/canonicalization research, remapped across A/c/B |
| Protocol v2 | V12 `B+b` tested end-to-end under `A→c→B→b→a` |
| Protocol v3 | A-layer fingerprint bound to actual NPZ public table structure; clean-host E5 closed |
| Structural v4 | explicit synthetic descriptor retrieval stress model with visible heavy-damage failures |
| Paper claim gate v7 | machine gate for bounded C1–C6 claims; C5 remains mandatory |

The project deliberately does **not** optimize rate before locator/bootstrap/reconstruction constraints.

## Protocol-v3 / E5 evidence

Protocol-v3 derives its locator feature from the public NPZ structure itself:

```text
morphology class + local x-grid length
```

Candidate ranking reads public candidate structure and A-defined rules only. B is parsed after a candidate is opened.

The recorded clean-host E5 benchmark contains:

```text
8 seeded full re-encodes
8 unique payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
```

The audit workflow also reruns fresh Protocol-v3 seeds on Python 3.12.

See [`results/protocol-real-package-v3.md`](results/protocol-real-package-v3.md) and [`results/e5-multiseed-final.json`](results/e5-multiseed-final.json).

## Structural v4 boundary

The audited v4 model uses:

```text
12 stable labels
1,000,000 candidates
10,000 rank trials
1% strong near-decoys
near-decoys have exactly 6 / 12 correct label→ID pairs
ties count ahead
```

Under that explicit model, 25% deletion remains inside Top-100 in the tested run, while 50% deletion fails even Top-1000 because the target falls to the six-match near-decoy boundary. This intentionally contradicts earlier unauditable handoff numbers rather than preserving them.

`physical_reorder` and `labeled_split_merge` in v4 are descriptor-level canonicalization controls. They do **not** mean the current Protocol-v3 NPZ parser accepts a changed physical table count.

See [`results/locator-structural-v4.md`](results/locator-structural-v4.md).

## Paper line

The paper toolchain is downstream of machine results:

```text
machine results
    ↓
morphology analysis
    ↓
domain narrative archetype
    ↓
generic descriptive fits
    ↓
claim-evidence gate
    ↓
mock paper
```

The paper layer may change presentation, terminology, section order, and figure selection. It may not invent benchmark numbers, convert requested work into completed evidence, claim real provenance, or turn descriptive fits into mechanism proof.

Paper v6's six recorded experiments pass under their synthetic criteria. Paper claim gate v7 checks bounded C1–C6 roles against those results plus the explicit v4 boundary.

See [`results/paper-v6-experiments.json`](results/paper-v6-experiments.json) and [`results/paper-claim-audit-v7.md`](results/paper-claim-audit-v7.md).

## V18–V21 status

V18–V20 still map conceptually into the corrected lifecycle, but their precise historical metrics do not currently have an auditable executable/raw-result chain in the inspected repository history. They are therefore **not current machine evidence**.

```text
V18 -> noisy-host b carrier; parameters in B -> NEEDS-REINTEGRATION
V19 -> sender policy for choosing (b,B) -> NEEDS-REINTEGRATION
V20 -> outer reliability in b/c; parameters in B -> NEEDS-REINTEGRATION
V21 -> retain "protocol constraints before rate" only; old quantitative results STALE
```

See [`protocol/version-remap-v12-v21.md`](protocol/version-remap-v12-v21.md).

## Run the audit

```bash
python -m pip install -r requirements.txt
python tools/audit_current.py
python protocol/locator-structural-v4.py --json-out /tmp/v4.json --md-out /tmp/v4.md
python tools/paper_claim_gate_v7.py --v4-result /tmp/v4.json --json-out /tmp/claims.json --md-out /tmp/claims.md
```

The GitHub Actions audit runs these checks on pull requests.

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
