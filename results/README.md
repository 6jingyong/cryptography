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
| `noisy-host-v18-reintegration.json/.md` | bounded V18 smooth-host calibration + current-protocol result |
| `v18-residual-matrix.json/.md` | five sender-observed residual families pass the declared matrix |
| `v18-publication-damage.json/.md` | broad V18 publication robustness rejected |
| `v18-publication-statistics.json/.md` | 24-seed alignment-dependent re-quantization + paired-noise success curve |
| `v18-error-profile.json/.md` | failed V18 packages have sparse post-Hamming residual errors |
| `v20-bounded-reintegration-plan.md` | frozen first V20 RS geometry and refusal gate |
| `v20-bounded-reintegration.json/.md` | fixed 6.25% RS geometry passes initial 24-seed six-condition post-seal matrix |
| `v20-failure-envelope-plan.md` | frozen stronger damage grid with V20 geometry held fixed |
| `v20-failure-envelope.json/.md` | V20 first tested failures align exactly with per-shard RS capacity exceedance |
| `current-e2e-integration-plan.md` | frozen project-level integration gate |
| `current-e2e-integration.json/.md` | current V18/V20 technical path and paper_v6 renderer pass as one reproducible bundle |
| `paper-claim-audit-v7.json/.md` | bounded paper claim gate and mandatory limitations |
| `current-summary.json` | compact audited current state |

## Project-level result

The current repository now has one integrated synthetic path rather than only separately passing components:

```text
synthetic a
-> current V18/V20 package
-> c mixed among d
-> A locator/bootstrap
-> authenticated open
-> B decode / optional repair
-> exact a
-> same current package + same current multiseed evidence
-> paper_v6 mock-paper output
```

Fresh seeds `901..908`:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

The representative current V20 NPZ and B manifest are consumed directly by `tools/paper_v6.py`, and the same current-V20 8-seed result completes paper E5. Visible mock/synthetic labels and the mandatory non-provenance limitation are retained.

The CI bundle contains technical + paper outputs and a SHA-256 manifest covering 14 files; independent recomputation found zero mismatches.

This is now the preferred high-level evidence when asking whether the project works as a system.

## Technical boundary that still matters

V18 is **CURRENT_BOUNDED_REINTEGRATION**, not broadly publication-robust. Its transition-region failures are sparse after inner Hamming correction.

V20 uses fixed logical outer reliability:

```text
512-byte payload
4 x 128-byte RS data shards
8 parity bytes / shard
<=4 byte-error correction / shard
32 parity bytes total = 6.25% payload parity overhead
```

The first V20 frozen matrix passed 49/49 attempted repairs. A stronger fresh-seed envelope then showed:

```text
V20 failure <=> at least one shard exceeds the declared four-byte RS correction bound
```

Mismatch count: **0** in the tested stronger grid. Locator structural score remained 1.0 throughout.

This makes V20's current synthetic failure boundary interpretable, but does not prove universal robustness or optimality of the 6.25% overhead.

## What not to optimize next

Further dense points on the same numeric-noise grids, immediate parity tuning, or bit/value optimization have diminishing project value.

The thinner side of the now-integrated system is the **paper-shaped artifact**. The next high-value milestone should make the current paper output genuinely multi-figure and traceable to the same current V20 data:

```text
actual synthetic figures
multi-figure layout chosen from morphology
machine-backed captions / claim map
downloadable synthetic raw-data tables
clearly labeled mock-paper manuscript/package
bundle-level traceability to current machine artifacts
```

Structural-damage tests and V19 remain valid future work, but they should be pulled in when they unblock this whole-system objective rather than because an unresolved checkbox exists.

Still unsupported: real-publication deployment, real confidential payload hiding, universal undetectability/security, real provenance/mechanism, or restoration of historical V18/V20 numerical summaries.
