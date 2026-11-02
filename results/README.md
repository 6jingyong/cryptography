# Results index

Only milestones still useful under the corrected protocol remain in the current working tree.

| File | Current meaning |
|---|---|
| `adaptive_q_v12.md` | adaptive-q clean-host carrier for processed payload `b` |
| `locator_v16.md` | historical A-layer labeled locator / erasure benchmark |
| `publication_robustness_v17.md` | historical publication/canonicalization observations; responsibilities remapped |
| `protocol-real-package-v3.md` | A fingerprint bound to actual NPZ public structure |
| `e5-multiseed-final.json` | recorded clean-host full re-encode → locator → exact-recovery result |
| `locator-structural-v4.json/.md` | audited A-layer descriptor stress model and failure boundary |
| `noisy-host-v18-reintegration.json/.md` | bounded V18 noisy-host calibration + current-protocol result |
| `v18-residual-matrix.json/.md` | five sender-observed residual families pass the declared matrix |
| `v18-publication-damage.json/.md` | broad V18 publication robustness rejected |
| `v18-publication-statistics.json/.md` | paired-noise transition + alignment-dependent re-quantization |
| `v18-error-profile.json/.md` | failed V18 packages leave sparse post-Hamming residual errors |
| `v20-bounded-reintegration.json/.md` | fixed 6.25% RS geometry passes initial post-seal matrix |
| `v20-failure-envelope.json/.md` | tested V20 failures align exactly with per-shard RS capacity exceedance |
| `current-e2e-integration.json/.md` | current technical path and paper-v6 consume the same current V20 package/evidence |
| `paper-bundle-v7-plan.md` | frozen multi-figure/raw-data/traceability paper-package plan |
| `paper-bundle-v7.json/.md` | paper-v7 passes per-artifact traceability; cross-run visible-carrier numerical identity remains unresolved |
| `paper-claim-audit-v7.json/.md` | bounded claim gate and mandatory limitations |
| `current-summary.json` | compact audited current state |

## Current whole-system state

The repository now has one integrated synthetic path:

```text
synthetic a
-> current V18/V20 package
-> c mixed among d
-> A locator/bootstrap
-> authenticated open
-> B decode / optional V20 repair
-> exact a
-> same current package + current machine evidence
-> multi-figure paper-shaped synthetic bundle
```

Current E2E machine control, seeds `901..908`:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

## Paper bundle v7

Paper-v7 now generates from one fresh current V20 bundle:

```text
4 SVG figures
12 per-table raw-data CSV files
figure/data manifests
C1/C2/C4/C5 traceability
clearly labeled synthetic manuscript
complete final bundle hash manifest
```

Frozen rule-selected morphology examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

Independent audit confirmed:

```text
Figure 2 selection rule: exact
Figure 3 matched-fit values: exact vs current paper-v6 analysis
Figure 3 linear baselines: exact when recomputed from same current curves
Figure 4 E5 source: same current-V20 machine result used by paper E5
nested manifest mismatches: 0
final complete manifest mismatches: 0
```

Status:

```text
PASS_WITH_REPRODUCIBILITY_BOUNDARY
```

## Newly exposed system-level boundary

Two independent successful fresh CI runs with the same frozen seeds preserve:

```text
representative payload hash
current-V20 E5 hash/result
morphology representative selection
presentation archetype
story type
```

but do **not** produce numerically identical visible carrier data:

```text
NPZ hash differs
B manifest hash differs
8 / 12 visible tables differ numerically
```

Differing visible table IDs:

```text
0, 2, 3, 5, 6, 7, 10, 11
```

Thus current paper artifacts are completely traceable **within a run**, but fixed-seed cross-run numerical identity is not yet established.

This elevates the previously known QR/eigh/sign deterministic-basis issue from a technical footnote to the next whole-system reproducibility priority.

## What not to optimize next

Do not respond by adding more figures, more noise-grid points, tuning parity, or optimizing bit/value.

The next high-value milestone is:

```text
same seed + same protocol
-> same semantic B
-> same numeric visible table arrays
-> same exported raw-data values
-> stable paper inputs
while preserving existing locator / exact recovery / V20 gates
```

Still unsupported: real-publication deployment, real confidential payload hiding, universal undetectability/security, real provenance/mechanism, or restoration of historical V18/V20 numerical summaries.
