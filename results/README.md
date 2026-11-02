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
| `v18-publication-statistics.json/.md` | current best V18 damage evidence: alignment-dependent re-quantization and monotonic paired-noise success curve |
| `paper-v6-experiments.json` | completed machine validation experiments for the paper line |
| `paper-claim-audit-v7.json/.md` | bounded claim gate C1–C6 and mandatory limitations |
| `current-summary.json` | compact audited current state |

## V18 evidence hierarchy

V18 evidence now has five distinct layers:

1. **Smooth-host feasibility** — rebuilt host-aware modulo-QIM recovers exactly under the current lifecycle.
2. **Known-host distribution breadth** — five equal-energy sender-observed residual families pass without carrier retuning.
3. **Coarse post-embedding publication damage** — broad publication robustness is rejected; failures begin in inner decode while locator retrieval remains intact.
4. **Fresh-seed refinement** — re-quantization is demonstrably non-monotonic and the original independent-noise sweep cannot define a deterministic threshold.
5. **24-seed statistics** — paired noise resolves that ambiguity, while dense re-quantization confirms alignment dependence.

Current 24-seed paired-noise result:

```text
sigma/delta : exact/24
0.08        : 24
0.09        : 24
0.10        : 24
0.11        : 24
0.12        : 24
0.13        : 23
0.14        : 20
0.15        : 16
0.16        :  9
0.17        :  4
0.18        :  1
```

All 24 per-seed PASS→FAIL patterns are monotonic when the same base noise field is scaled across alpha. Thus additive-noise strength is a valid monotonic axis under this paired construction, although no universal deterministic threshold is claimed.

Dense re-quantization remains non-monotonic. For example `1.06x` recovers 19/24, `1.10x` 22/24; `1.20x` 17/24, `1.22x` 22/24. Treat factor as an alignment variable, not a scalar damage severity.

All tested locator structural scores remain 1.0; observed failure is inside `B + damaged b` reconstruction.

Therefore **broad V18 publication robustness remains rejected**. The next useful measurement is error multiplicity/location in failed packages; only then is it sensible to decide whether V20-style redundancy would help or merely mask a structurally poor inner channel.

The historical V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` summary remains retired. V19–V20 historical precise metrics remain non-current; V21 retains only **protocol constraints before rate**.

The authoritative chain is current code + checked-in machine results + reproducible CI. Historical prose does not override them.
