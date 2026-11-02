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
| `paper-claim-audit-v7.json/.md` | bounded paper claim gate and mandatory limitations |
| `current-summary.json` | compact audited current state |

## Current technical interpretation

V18 is **CURRENT_BOUNDED_REINTEGRATION**, not broadly publication-robust. Its tested transition-region failures are sparse after the existing inner Hamming layer.

V20 uses one fixed logical outer-reliability geometry:

```text
512-byte payload
4 x 128-byte RS data shards
8 parity bytes per shard
<=4 byte-error correction per shard
32 parity bytes total = 6.25% payload parity overhead
```

The first frozen 24-seed matrix passed all six damaged conditions, with 49/49 repair attempts successful.

A second fresh-seed run then held the geometry fixed and deliberately crossed its failure boundary.

Paired additive noise:

```text
0.16 delta  24/24 V20, 0 packages over RS shard bound
0.18 delta  24/24 V20, 0 packages over RS shard bound
0.20 delta  17/24 V20, 7 packages over RS shard bound
0.22 delta   5/24 V20, 19 packages over RS shard bound
>=0.25       0/24 V20, 24 packages over RS shard bound
```

Re-quantization:

```text
1.30x  24/24 V20, 0 packages over RS shard bound
1.50x  24/24 V20, 0 packages over RS shard bound
1.75x  20/24 V20, 4 packages over RS shard bound
>=2.00x 0/24 V20, 24 packages over RS shard bound
```

Across every individual run in this stronger frozen grid, the equivalence was exact:

```text
V20 failure <=> at least one 128-byte shard exceeded 4 candidate byte errors
```

Mismatch count: **0**. Locator structural score remained 1.0 throughout, so the measured failures are not A-layer retrieval failures.

This makes the current V20 boundary mechanistically interpretable inside the declared synthetic channel: the implementation continues to work until the fixed Reed-Solomon shard capacity is exceeded.

Important protocol distinction: V20 authenticates `B + masked r`, not raw numeric `b`, and requires exact final payload SHA-256 after decode/repair. Both manifest and repair-field bitflip controls are rejected by the authenticated envelope.

Still unsupported: universal/continuous thresholds, optimality of 6.25% overhead, real-publication robustness, cryptographic security/undetectability, or restoration of historical V18/V20 numerical summaries.

Further points on the same numeric-noise grids have diminishing value. The next useful fork is either structurally different damage under the same V20 geometry, or V19 reintegration using only modes with audited evidence envelopes.
