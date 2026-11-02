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
| `v18-residual-matrix.json/.md` | five sender-observed residual families pass the declared matrix |
| `v18-publication-damage.json/.md` | broad V18 publication robustness rejected; failures begin in inner decode |
| `v18-publication-frontier-refine.json/.md` | re-quantization non-monotonicity discovered; independent-noise ambiguity exposed |
| `v18-publication-statistics.json/.md` | 24-seed alignment-dependent re-quantization + monotonic paired-noise curve |
| `v18-error-profile.json/.md` | failed V18 packages have sparse post-Hamming residual errors |
| `v20-bounded-reintegration-plan.md` | frozen first V20 RS geometry and refusal gate |
| `v20-bounded-reintegration.json/.md` | fixed 6.25% RS geometry passes the declared 24-seed six-condition post-seal matrix |
| `paper-v6-experiments.json` | completed machine validation experiments for the paper line |
| `paper-claim-audit-v7.json/.md` | bounded claim gate C1–C6 and mandatory limitations |
| `current-summary.json` | compact audited current state |

## Current technical interpretation

V18 is **CURRENT_BOUNDED_REINTEGRATION**, not broadly publication-robust. Known-host feasibility is good in the frozen synthetic matrix, additive-noise degradation is measurable under paired scaling, re-quantization is alignment-dependent rather than monotonic, and failed transition-region packages leave only sparse residual errors after the inner Hamming layer.

That sparse profile justified one fixed V20 experiment rather than carrier retuning.

V20 first geometry:

```text
512-byte payload
4 x 128-byte RS data shards
8 parity bytes per shard
32 parity bytes total = 6.25% payload parity overhead
```

Frozen fresh seeds 701–724 produced:

```text
paired noise         V18 direct -> V20 final
0.14 delta            20/24     -> 24/24
0.15 delta            15/24     -> 24/24
0.16 delta             7/24     -> 24/24

re-quantization      V18 direct -> V20 final
1.06x                 17/24     -> 24/24
1.20x                 19/24     -> 24/24
1.30x                 17/24     -> 24/24
```

There were 49 repair attempts and all 49 succeeded. Successful repairs touched at most two 128-byte shards. Every accepted final payload hash was exact, every locator structural score remained 1.0, and an authenticated repair-field bitflip was rejected.

V20 therefore advances to **CURRENT_BOUNDED_REINTEGRATION** for this declared synthetic matrix.

Important protocol distinction: V20 does not authenticate raw `b` bytes with the old `HMAC(B+b)` rule. It authenticates `B + masked r`, then requires an exact authenticated final payload hash after decoding or repair. Do not conflate this logical reliability envelope with raw NPZ byte integrity.

Still unsupported: universal post-seal robustness, optimality of 6.25% overhead, real-publication robustness, cryptographic security/undetectability, or restoration of historical V18/V20 numerical summaries.

Next measurement should hold this V20 geometry fixed and map where it fails under stronger or structurally different post-seal damage before considering any different redundancy geometry.
