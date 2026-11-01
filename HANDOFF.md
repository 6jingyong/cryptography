# HANDOFF — audit before extension

Repository: `6jingyong/cryptography`  
Branch: `main`  
Scope: **synthetic/mock benchmark only**

> **Do not continue development first.** In the next conversation, fetch the current `main` head/tree and audit this handoff against the actual code and machine-result files. Mark every item `PASS`, `FAIL`, `UNVERIFIED`, or `STALE`. If this document conflicts with current code/results, trust the current code/results.

## 1. Authoritative protocol

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

Background records are `d`.

```text
A = long-lived pre-shared locator / canonicalization / bootstrap protocol
B = per-package reconstruction codebook / manifest
b = processed payload representation
c = candidate package containing public fingerprint structure + B + b + integrity
a = final synthetic payload
d = unrelated public/background record
```

Hard invariant: A should **not** need package-specific q, transform, table geometry, ECC, payload length, padding, or decoder parameters. Those belong in B. The old pre-reset naming that reversed these roles is retired.

## 2. Current protocol implementation

Primary implementation: `protocol/real-package-v3.py`.

Protocol v3 derives the A-layer fingerprint from **public structure of the published V12 NPZ itself**, rather than an extra attached synthetic fingerprint. The current public table identity uses:

```text
numeric morphology class + local x-grid length
```

A applies a pre-shared keyed ordering / assignment over those public table identities.

**Mandatory audit:** prove from code that locator ranking uses only `A + public candidate structure`; B must not be parsed to obtain locator features before candidate ranking. Parsing B is allowed only after a candidate is selected/opened.

## 3. E5 nominal full re-encode

Authoritative file: `results/e5-multiseed-final.json`.

Recorded result:

```text
8 independently seeded synthetic payloads
8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
```

This closes the tested clean-host V12 E5 path. It is **nominal**, not structural-damage robustness, V18 noisy-host robustness, universal reliability, or cryptographic-security evidence.

## 4. A-layer structural robustness v4

Files:

```text
protocol/locator-structural-v4.py
results/locator-structural-v4.json
results/locator-structural-v4.md
```

Stress model:

```text
1,000,000 candidates
10,000 rank trials
1% strong near-decoys
near-decoys preserve 6 / 12 exact label→ID pairs
ties count ahead
```

Recorded boundary — re-read exact values from JSON during audit:

```text
baseline: Recall@20 ~0.924, Recall@100 1.000, median rank ~15
physical reorder: Recall@100 1.000
labeled split/merge: Recall@100 1.000
25% deletion: Recall@100 1.000
50% deletion: Recall@100 0, Recall@1000 1.000, median rank ~780
20% substitution: Recall@100 0, Recall@1000 1.000, median rank ~223
50% deletion + 20% substitution: Recall@1000 0, median rank ~2663
```

Interpretation:

```text
locator success != unique rank 1
false positives are expected
strict candidate verification is mandatory
```

“Labeled split/merge” does **not** mean arbitrary destructive/unlabeled split/merge is reversible. Heavy-damage failures are real; do not hide them by changing the metric or optimizing capacity first.

## 5. Paper line

Current executable: `tools/paper_v6.py`  
Current claim audit: `results/paper-claim-audit-v7.md`

Current claim roles:

```text
C1 primary conclusion — multiple synthetic response regimes, bounded by tested perturbation/LOO conditions
C2 supporting quantification — morphology-matched descriptive fits beat the tested linear baseline on tested nonlinear tables
C3 presentation support — morphology-based domain archetype is stable under tested LOO
C4 technical control — exact recovery / locator / decoy rejection / E5
C5 mandatory limitation — field framing/fits are descriptive, not real provenance or mechanism evidence
C6 locator robustness — only within explicit v4 envelope and failure boundary
```

Never upgrade:

```text
domain archetype -> real provenance
high R² -> proven physical mechanism
synthetic locator benchmark -> universal undetectability/security
requested experiment -> completed evidence
```

`C5` must remain visible.

## 6. Historical V12–V21 remap

```text
V12 -> b carrier / package-specific settings in B
V16 -> A-layer labeled locator research
V17 -> A/c/B publication + canonicalization boundary
V18 -> noisy-host b carrier / settings in B
V19 -> sender-side strategy for choosing (b,B)
V20 -> outer package reliability / B parameters
V21 -> retain “protocol constraints before rate”
```

Pre-reset V18–V21 scripts/results are historical research, not automatically authoritative implementations of the current lifecycle. They must be re-integrated and re-tested under `A -> c -> B -> b -> a`.

## 7. Known unresolved issues

1. Public label stability has been checked across payload seeds, not all package configurations.
2. 50% structural deletion exceeds current Top-100 locator envelope.
3. 20% structural substitution exceeds current Top-100 locator envelope.
4. 50% deletion + 20% substitution exceeds Top-1000 in current v4 stress.
5. Fingerprint assumes enough public table identity survives canonicalization.
6. Strong near-decoys can create exact/tied locator matches; strict verification remains essential.
7. Cross-platform deterministic basis generation remains unresolved; NumPy QR/eigh/sign canonicalization is not proven cross-platform deterministic.
8. E5 closes clean-host V12, not V18 noisy-host.
9. V18–V21 need protocol-level reintegration.
10. `tools/paper_v6.py` is the cleaned current executable and may be simpler than the historical chain; audit functionality, not version prestige.
11. No universal undetectability/security claim is supported.
12. No real-publication deployment is in scope.

## 8. Mandatory next-conversation audit

Before coding anything new:

### A. Repository state
- Fetch current `main`; record exact head SHA.
- Fetch recursive tree.
- Confirm this `HANDOFF.md` corresponds to that tree.
- Identify files/commits newer than the handoff.

### B. Terminology / architecture
Inspect `README.md`, `protocol/README.md`, `protocol/schema-v1.json`, and `protocol/version-remap-v12-v21.md`. Verify A/B roles are consistent everywhere. Mark stale wording explicitly.

### C. Locator independence
Inspect `protocol/real-package-v3.py`. Prove candidate ranking does not parse B for locator features. If it does, mark `FAIL`.

### D. Code health
Compile all current Python files and run a small Protocol-v3 end-to-end synthetic test. Record exact commands/results.

### E. E5
Inspect `results/e5-multiseed-final.json`: verify 8 runs, 8 distinct hashes, 8/8 exact recovery, Recall@20=1.0, Recall@100=1.0. Rerun at least 2 fresh synthetic seeds if supported.

### F. Structural v4
Cross-check `protocol/locator-structural-v4.py`, `results/locator-structural-v4.json`, and `.md`. Verify table/JSON agreement, near-decoy model, conservative tie handling, labeled-only split/merge claim, and visible heavy-damage failures.

### G. Paper claim gate
Inspect `tools/paper_v6.py` and `results/paper-claim-audit-v7.md`. Cross-check every upgraded claim against machine results; verify `C5` remains mandatory.

### H. V18–V21 classification
Mark each current reference as `CURRENT`, `HISTORICAL-BUT-VALID`, `NEEDS-REINTEGRATION`, or `STALE`.

## 9. Required audit output

| item | status | evidence | correction/action |
|---|---|---|---|
| main/head/tree | PASS/FAIL/... | SHA + files | ... |
| A/B terminology | ... | ... | ... |
| locator independence | ... | ... | ... |
| Protocol-v3 run | ... | ... | ... |
| E5 | ... | ... | ... |
| v4 robustness | ... | ... | ... |
| Paper-v7 claims | ... | ... | ... |
| V18–V21 classification | ... | ... | ... |

End with exactly one of:

```text
AUDIT GATE: PASS — safe to continue development
```

or

```text
AUDIT GATE: FAIL — repair these items before extension
```

If the audit gate fails, do not continue substantial development in the same answer.

## 10. Only after audit passes

Do **not** return to bit/value optimization first. Preferred A-layer directions:

```text
richer / multi-view public fingerprint
stable public labels
error-correcting fingerprint representation
hierarchical retrieval
adaptive verification budget
```

Goal: improve Recall@K under deletion/substitution **without moving package-specific decoder state from B into A**.

Then re-integrate V18 noisy-host carrier into `A -> c -> B -> b -> a` and run an E5-style multi-seed benchmark.

## 11. Suggested first message for the next conversation

> 先不要继续开发。连接 GitHub 仓库 `6jingyong/cryptography`，从当前 `main` 开始，对 `HANDOFF.md` 做严格、怀疑式审核。逐项核对代码、结果文件和实验数字，给出 PASS / FAIL / UNVERIFIED / STALE；发现冲突以当前代码和结果文件为准。尤其检查 A/B 职责、locator 是否未解析 B、E5 多 seed、结构鲁棒性 v4 的边界、paper v7 claim gate、以及历史 V18–V21 是否还能挂回当前协议。审核通过后再提出下一步，不要先追 bit/value。

## 12. Handoff principle

The next conversation is expected to **challenge this handoff**, not merely repeat it.

The handoff is a map. The repository and reproducible machine results are the evidence.
