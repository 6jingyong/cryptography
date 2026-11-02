# Results index

Only milestones still useful under the corrected protocol remain in the current working tree.

| File | Current meaning |
|---|---|
| `adaptive_q_v12.md` | adaptive-q clean-host carrier for processed payload `b` |
| `locator_v16.md` | historical A-layer labeled locator / erasure benchmark; pre-reset wording may be stale |
| `publication_robustness_v17.md` | historical publication/canonicalization robustness; responsibilities remapped |
| `protocol-real-package-v3.md` | A fingerprint bound to actual NPZ public structure |
| `e5-multiseed-final.json` | recorded 8-seed clean-host full re-encode → locator → exact-recovery result |
| `locator-structural-v4.json/.md` | audited A-layer descriptor stress model and failure boundary |
| `v18-reintegration-plan.md` | first V18 hypothesis / gates / refusal rule frozen before results |
| `noisy-host-v18-reintegration.json/.md` | bounded V18 smooth-host calibration + 8-seed current-protocol result |
| `v18-residual-matrix-plan.md` | five-model known-host residual matrix frozen before results |
| `v18-residual-matrix.json/.md` | all five sender-observed residual families pass the declared matrix |
| `v18-publication-damage-plan.md` | frozen post-embedding / pre-seal damage matrix |
| `v18-publication-damage.json/.md` | coarse result: broad publication robustness rejected; failures begin in inner decode |
| `v18-publication-frontier-refine-plan.md` | fresh 8-seed measurement-only refinement plan |
| `v18-publication-frontier-refine.json/.md` | re-quantization non-monotonicity discovered; independent-noise ambiguity exposed |
| `v18-publication-statistics-plan.md` | 24-seed dense re-quantization + paired-noise statistical plan |
| `v18-publication-statistics.json/.md` | alignment-dependent re-quantization and monotonic paired-noise success curve |
| `v18-error-profile-plan.md` | frozen residual-error decomposition plan before V20 |
| `v18-error-profile.json/.md` | failed V18 packages have sparse post-Hamming residual errors; bounded V20 prototype justified |
| `paper-v6-experiments.json` | completed machine validation experiments for the paper line |
| `paper-claim-audit-v7.json/.md` | bounded claim gate C1–C6 and mandatory limitations |
| `current-summary.json` | compact audited current state |

## V18 evidence hierarchy

V18 evidence now has six distinct layers:

1. **Smooth-host feasibility** — rebuilt host-aware modulo-QIM recovers exactly under the current lifecycle.
2. **Known-host distribution breadth** — five equal-energy sender-observed residual families pass without carrier retuning.
3. **Coarse post-embedding publication damage** — broad publication robustness is rejected; failures begin in inner decode while locator retrieval remains intact.
4. **Fresh-seed refinement** — re-quantization is demonstrably non-monotonic and the original independent-noise sweep cannot define a deterministic threshold.
5. **24-seed statistics** — paired noise establishes a monotonic strength axis, while dense re-quantization confirms alignment dependence.
6. **Residual error profile** — failed transition-region packages are sparse after the existing Hamming layer.

Current error-profile evidence, fresh seeds 601–624:

```text
paired noise failures (37 packages):
  residual payload bits   median 2, p90 4, max 4
  bad tables              median 1, p90 2, max 3
  bad corrected codewords median 1, p90 2, max 3
  raw payload-symbol errs median 18
  post-Hamming symbol err median 2

representative re-quantization failures (23 packages):
  residual payload bits   median 2, p90 3, max 5
  bad tables              median 1, p90 1, max 2
  bad corrected codewords median 1, p90 1, max 2
  raw payload-symbol errs median 15
  post-Hamming symbol err median 1
```

About 95.7% of failed re-quantized packages concentrated final payload errors in one table. Every failed package in the measured profile had at most four bad corrected codewords.

This changes the V20 decision: a **small, bounded outer-reliability prototype is now justified**. It should target the measured sparse residual regime rather than use large redundancy to force success.

Broad V18 publication robustness remains rejected. The sparse error profile does not validate any V20 code family, shard geometry, post-seal repair path, or real-publication robustness.

The historical V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` summary remains retired. Historical V20 numerical summaries also remain non-current; V21 retains only **protocol constraints before rate**.

The authoritative chain is current code + checked-in machine results + reproducible CI. Historical prose does not override them.
