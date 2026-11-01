# Results index

Only milestones still useful under the corrected protocol remain in the current working tree.

| File | Current meaning |
|---|---|
| `adaptive_q_v12.md` | adaptive-q carrier for processed payload `b` |
| `locator_v16.md` | historical A-layer labeled locator / erasure benchmark; pre-reset wording may be stale |
| `publication_robustness_v17.md` | historical publication/canonicalization robustness; responsibilities remapped by `protocol/version-remap-v12-v21.md` |
| `protocol-real-package-v2.md` | end-to-end V12 `B+b` under `A→c→B→b→a` |
| `protocol-real-package-v3.md` | A fingerprint bound to actual NPZ public structure |
| `e5-multiseed-final.json` | recorded 8-seed full re-encode → locator → exact-recovery result |
| `locator-structural-v4.json` | audited 1M-candidate / 10k-trial A-layer descriptor stress result |
| `locator-structural-v4.md` | human-readable v4 model, numbers, and failure boundary |
| `paper-v6-experiments.json` | completed machine validation experiments for the paper line |
| `paper-claim-audit-v7.json` | machine claim-gate summary C1–C6 |
| `paper-claim-audit-v7.md` | bounded claim interpretation and mandatory limitations |
| `current-summary.json` | compact audited current state; V18–V21 legacy numbers explicitly demoted |

## Evidence status

V18–V20 map cleanly into the corrected architecture but their historical precise metrics do not have an auditable executable/raw-result chain in the currently inspected repository history. They are **not current machine evidence** and must be rerun when reintegrated.

V21 retains only the principle **protocol constraints before rate**. Its old quantitative locator/geometry results are stale under the current A/B protocol.

The authoritative chain is current code + checked-in machine results + reproducible CI. Historical prose does not override them.
