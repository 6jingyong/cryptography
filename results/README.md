# Results index

Only milestones still useful under the corrected protocol remain in the current working tree.

| File | Current meaning |
|---|---|
| `adaptive_q_v12.md` | adaptive-q clean-host carrier for processed payload `b` |
| `locator_v16.md` | historical A-layer labeled locator / erasure benchmark; pre-reset wording may be stale |
| `publication_robustness_v17.md` | historical publication/canonicalization robustness; responsibilities remapped by `protocol/version-remap-v12-v21.md` |
| `protocol-real-package-v2.md` | end-to-end V12 `B+b` under `A→c→B→b→a` |
| `protocol-real-package-v3.md` | A fingerprint bound to actual NPZ public structure |
| `e5-multiseed-final.json` | recorded 8-seed clean-host full re-encode → locator → exact-recovery result |
| `locator-structural-v4.json` | audited 1M-candidate / 10k-trial A-layer descriptor stress result |
| `locator-structural-v4.md` | human-readable v4 model, numbers, and failure boundary |
| `v18-reintegration-plan.md` | first V18 hypothesis / gates / refusal rule frozen before results |
| `noisy-host-v18-reintegration.json` | bounded V18 smooth-host calibration + 8-seed protocol machine summary |
| `noisy-host-v18-reintegration.md` | smooth-host V18 interpretation and rejected upgrades |
| `v18-residual-matrix-plan.md` | five-model residual-distribution matrix frozen before results |
| `v18-residual-matrix.json` | five-model residual matrix machine summary |
| `v18-residual-matrix.md` | matrix interpretation for sender-observed host distributions |
| `v18-publication-damage-plan.md` | frozen post-embedding / pre-seal damage matrix |
| `v18-publication-damage.json` | machine summary of re-quantization/noise failure frontier |
| `v18-publication-damage.md` | bounded interpretation: known-host breadth but narrow publication margin |
| `paper-v6-experiments.json` | completed machine validation experiments for the paper line |
| `paper-claim-audit-v7.json` | machine claim-gate summary C1–C6 |
| `paper-claim-audit-v7.md` | bounded claim interpretation and mandatory limitations |
| `current-summary.json` | compact audited current state |

## Evidence status

V18 now has three distinct evidence layers which must not be conflated:

1. **Smooth-host feasibility:** exact current-protocol recovery under the rebuilt host-aware modulo-QIM carrier.
2. **Known-host distribution breadth:** iid Gaussian, heteroscedastic Gaussian, AR(1), low-frequency drift, and Gaussian+sparse-outlier hosts all pass when the sender observes the host before embedding and free-subspace RMS is normalized.
3. **Unknown post-embedding publication damage:** narrow. The frozen four-seed matrix passes additive noise through `0.10 delta`, but `0.15 delta` recovers only 2/4; `1.25x` re-quantization already recovers only 3/4, so no extra all-seed re-quantization margin beyond the existing `1.00x` grid is demonstrated.

In the publication-damage matrix every target remained locator rank 1 with score 1.0 and Recall@100=1.0. Failures begin in inner `B + damaged b` reconstruction, not A-layer retrieval.

Therefore **broad publication robustness is rejected** for the current V18 q=4 configuration. The old V18 precise summary (`59/60`, `57 q4 / 2 q2 / 1 unresolved`, etc.) also remains retired and was not restored by the new work.

Damage after c has already been sealed is a different problem: strict outer integrity is expected to reject it, so repair/survival belongs to V20 outer reliability rather than the V18 carrier frontier.

V19–V20 historical precise metrics still do not have an auditable executable/raw-result chain in the inspected history. V21 retains only the principle **protocol constraints before rate**; its old quantitative locator/geometry results are stale.

The authoritative chain is current code + checked-in machine results + reproducible CI. Historical prose does not override them.
