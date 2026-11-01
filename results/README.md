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
| `v18-publication-frontier-refine.json/.md` | refinement: re-quantization is non-monotonic; additive-noise threshold not deterministic |
| `paper-v6-experiments.json` | completed machine validation experiments for the paper line |
| `paper-claim-audit-v7.json/.md` | bounded claim gate C1–C6 and mandatory limitations |
| `current-summary.json` | compact audited current state |

## V18 evidence hierarchy

V18 evidence must be read as four distinct layers:

1. **Smooth-host feasibility** — rebuilt host-aware modulo-QIM recovers exactly under the current lifecycle.
2. **Known-host distribution breadth** — five equal-energy sender-observed synthetic residual families all pass without carrier retuning.
3. **Coarse post-embedding publication damage** — narrow margin; `1.25x` re-quantization already fails one of four seeds and `0.15 delta` noise recovers only two of four; locator remains intact.
4. **Fresh-seed refinement** — the simple scalar-threshold picture is itself partly wrong.

Fresh seeds 401–408 produce:

```text
re-quantization:
1.00x 8/8, 1.05x 7/8, 1.10x 8/8, 1.15x 7/8, 1.20x 7/8, 1.25x 6/8

additive noise:
0.10 delta 8/8, 0.11 8/8, 0.12 7/8, 0.13 3/8, 0.14 6/8, 0.15 6/8
```

The re-quantization result is non-monotonic: a coarser `1.10x` condition passes all eight seeds after `1.05x` failed one. Treat re-quantization factor as a grid/coset-alignment parameter, not a monotonic damage axis.

For additive noise, `0.10 delta` independently reproduces and `0.11 delta` also passes 8/8, but exact counts are not monotonic because each alpha uses a different noise realization. The experiment therefore does not establish a deterministic threshold between `0.11` and `0.12 delta`.

Every refined condition retains Recall@100=1; failures remain inner `B + damaged b` reconstruction rather than A-layer retrieval.

Therefore **broad V18 publication robustness remains rejected**, and the next measurement should estimate success probability/alignment structure rather than add still finer points to one supposed threshold.

The historical V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` summary remains retired and was not restored. V19–V20 historical precise metrics remain non-current; V21 retains only the principle **protocol constraints before rate**.

The authoritative chain is current code + checked-in machine results + reproducible CI. Historical prose does not override them.
