# HANDOFF — audited protocol state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

This handoff was rebuilt after a strict audit. Current code, checked-in machine results, and reproducible CI are authoritative; historical prose is not.

## 1. Authoritative lifecycle

```text
pre-shared root codebook A
        ↓
find / rank candidate package c
        ↓
open / verify c
        ↓
extract B + b
        ↓
B explains b
        ↓
recover synthetic payload a
```

```text
A = long-lived locator / canonicalization / bootstrap protocol
B = per-package reconstruction codebook / manifest
b = processed payload representation
c = candidate package containing public fingerprint structure + B + b + integrity
a = final synthetic payload
d = unrelated public/background record
```

Hard invariant: package-specific q, transform, geometry, ECC, payload length, padding, and decoder parameters belong in `B`, not long-lived `A`.

## 2. Protocol-v3 locator independence

Primary implementation: `protocol/real-package-v3.py`.

The locator derives its score from:

```text
A + public NPZ structure
```

using public morphology class + local x-grid length and A-keyed table ordering. Candidate ranking does **not** parse B. B is parsed only after a candidate is opened/verified.

Status: **PASS**.

## 3. E5 nominal full re-encode

Authoritative result: `results/e5-multiseed-final.json`.

```text
8 seeded full re-encodes
8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
```

The audit CI additionally reruns fresh repository seeds 101 and 102 under Python 3.12. Both recover exactly at rank 1 and produce different payload hashes.

Status: **PASS for tested clean-host V12 nominal path only**.

This is not V18 noisy-host evidence, structural-damage evidence, universal reliability, undetectability, or cryptographic-security evidence.

## 4. A-layer structural robustness v4 — audited rebuild

Files:

```text
protocol/locator-structural-v4.py
results/locator-structural-v4.json
results/locator-structural-v4.md
```

Explicit model:

```text
12 stable labels
1,000,000 candidates
10,000 rank trials
1% strong near-decoys = 10,000 candidates
near-decoys have exactly 6 / 12 correct label→ID pairs
random decoys are uniform random permutations of 12 IDs
score = correct A-defined pairs / fixed 12-label contract
ties count fully ahead
```

Audited results:

```text
baseline: R@20=1.0000, R@100=1.0000, median rank=1
physical reorder after label canonicalization: R@100=1.0000
labeled split/merge after logical canonicalization: R@100=1.0000
25% deletion: R@100=1.0000, median rank=2
50% deletion: R@1000=0, median rank=10589
20% substitution: R@20=0.9283, R@100=0.9793, R@1000=0.9812, median rank=1
50% deletion + 20% substitution: R@1000=0, median rank=13640
```

The previous handoff values such as `50% deletion -> Recall@1000=1, median rank~780` were **wrong** under the stated exact-6/ties-ahead model and are retired.

Important boundary: v4 is a **synthetic descriptor-level A-layer retrieval model**. `physical_reorder` / `labeled_split_merge` assume public labels reconstruct the same 12 logical identities. They do not prove that the current Protocol-v3 NPZ parser survives actual table deletion or a changed physical table count.

## 5. Paper line / claim gate v7

Executable presentation pipeline: `tools/paper_v6.py`  
Claim gate: `tools/paper_claim_gate_v7.py`  
Recorded audit: `results/paper-claim-audit-v7.json` and `.md`

All bounded claim roles pass:

```text
C1 PASS — multiple synthetic response regimes, bounded by tested perturbation/LOO
C2 PASS — morphology-matched descriptive fits beat tested linear baseline on tested nonlinear tables
C3 PASS — morphology-based presentation archetype stable under tested LOO
C4 PASS — clean-host E5 exact recovery / nominal locator evidence
C5 PASS — mandatory limitation: descriptive framing/fits are not provenance or mechanism evidence
C6 PASS — locator robustness only inside explicit descriptor-v4 model and visible failure boundary
```

Never upgrade:

```text
domain archetype -> real provenance
high R² -> proven physical mechanism
synthetic locator benchmark -> universal undetectability/security
requested experiment -> completed evidence
descriptor-level v4 canonicalization -> current v3 NPZ deletion/split-merge support
```

## 6. Historical V12–V21 classification

```text
V12 -> CURRENT / b carrier; package-specific settings in B
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old "second codebook" wording is stale
V17 -> HISTORICAL-BUT-VALID observations; A/c/B responsibilities remapped
V18 -> NEEDS-REINTEGRATION; noisy-host b carrier, settings in B
V19 -> NEEDS-REINTEGRATION; sender policy for choosing (b,B)
V20 -> NEEDS-REINTEGRATION; outer reliability in b/c, concrete parameters in B
V21 -> HISTORICAL-BUT-VALID principle only: protocol constraints before rate; old quantitative results STALE
```

Precise V18–V20 historical numbers preserved in old summaries are **UNVERIFIED_NOT_CURRENT_EVIDENCE** because no auditable executable/raw-result chain was found in the inspected repository history. Do not cite those numbers as current results until the modes are re-integrated and rerun.

## 7. Known unresolved issues

1. Public label stability is not proven across all package configurations.
2. Current Protocol-v3 NPZ locator is not proven robust to actual physical table deletion or changed table count.
3. The 12-label descriptor model has a sharp failure boundary when the target falls to six or fewer correct pairs against 10,000 exact-six near-decoys.
4. 20% substitution has a catastrophic tail even though median rank remains 1.
5. Cross-platform deterministic basis generation remains unresolved; NumPy QR/eigh/sign behavior is not proven bit-identical across platforms.
6. E5 closes clean-host V12 only, not V18 noisy-host.
7. V18–V20 need protocol-level reintegration and fresh machine results.
8. No universal undetectability/security claim is supported.
9. No real-publication deployment is in scope.

## 8. Reproducible audit gate

Run:

```bash
python tools/audit_current.py
python protocol/locator-structural-v4.py --json-out /tmp/v4.json --md-out /tmp/v4.md
python tools/paper_claim_gate_v7.py --v4-result /tmp/v4.json --json-out /tmp/claims.json --md-out /tmp/claims.md
```

The GitHub Actions workflow `.github/workflows/audit-current.yml` runs the same checks on pull requests.

## 9. Audit status

```text
A/B terminology                PASS
locator independence           PASS
Python compile                 PASS
Protocol-v3 fresh run          PASS
recorded E5 integrity          PASS
fresh E5-style seeds           PASS
structural v4 model/results    PASS
Paper-v7 bounded claim gate    PASS
V18–V21 classification         PASS
```

The status above means the **current evidence chain is internally auditable**, not that unresolved V18–V20 work has been completed.

## 10. Next work after this gate

Do **not** return to bit/value optimization first.

The highest-value next step is to re-integrate **V18 noisy-host carrier** into the current lifecycle:

```text
A -> c -> B -> noisy-host b -> a
```

with all concrete V18 mode parameters stored in B, followed by an E5-style multi-seed benchmark.

A-layer improvement remains relevant, especially stable public labels / richer or error-correcting fingerprint representation, but should be driven by the audited v4 failure boundary rather than by hiding it.

AUDIT GATE: PASS — safe to continue development
