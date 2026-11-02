# HANDOFF — audited project state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative. Historical prose and legacy V18–V21 numbers are not.

## 1. Project orientation

Do not treat this project as a sequence of carrier-parameter competitions.

```text
synthetic payload a
-> numeric b
-> per-package B (+ optional repair r)
-> candidate c mixed among unrelated synthetic d
-> long-lived A locates / bootstraps c without parsing B during ranking
-> authenticated open
-> B explains b; optional V20 repair
-> exact a
-> same current machine package/results feed a clearly labeled mock-paper bundle
```

```text
A = long-lived locator / canonicalization / bootstrap root
B = per-package reconstruction + reliability manifest
```

Package-specific q, transform, geometry, ECC, host model, publication parameters, **basis version**, shard size, parity geometry, etc. belong in B, not A.

Priority:

```text
find c > open/authenticate c > interpret B > exact a > reproducible evidence > traceable presentation > rate/overhead optimization
```

## 2. Current promoted path

Current promoted path remains:

```text
A-v3
+ src/noisy_host_package_v18_deterministic.py
+ bounded V20
```

Current engine:

```text
src/noisy_host_package_v18_deterministic.py
basis_version = deterministic-dct-mgs-v1
```

Legacy baseline retained:

```text
src/noisy_host_package_v18.py
```

The deterministic engine replaces the old QR/eigh free-basis path with fixed-order DCT-II candidates + two-pass modified Gram-Schmidt and fixed-order scalar reductions. The basis version is explicit B state; the decoder rejects a mismatched declared basis version.

Frozen deterministic promotion gates all pass:

```text
Gate A — protocol viability
8 / 8 unique payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median/max target rank = 1 / 1
paper-v7 = PASS

Gate B — independent-run semantic determinism
two independent GitHub Actions runners
semantic_equal = true
mismatch_count = 0
raw NPZ container hash equal = true

Gate C — bounded evidence regression
V18 core / residual matrix / publication statistics / error profile = PASS
V20 bounded matrix / fixed-geometry failure envelope = PASS
q / delta / RS geometry were not retuned
```

Boundary: exact semantic reproducibility is established across the declared independent GitHub Actions environment for the frozen configuration. This is not a universal every-CPU/libm/NumPy/Python bit-identity claim.

## 3. Current integrated technical path

Current runner:

```text
tools/current_end_to_end.py
```

Frozen seeds `901..908`, payload 512 B, channels 2, 2,000-candidate corpus, Top-100:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

The same current V20 NPZ/B and current-V20 8-seed result feed the paper line; paper E5 is `COMPLETED` and passes.

Evidence:

```text
results/current-e2e-integration-plan.md
results/current-e2e-integration.json
results/current-e2e-integration.md
```

## 4. V18 state

Status: **CURRENT_BOUNDED_REINTEGRATION + DECLARED-CI DETERMINISM PASS**.

Current evidence supports:

```text
smooth reference: 8/8 exact
five frozen sender-observed residual families: pass
q=4 selected for all tested tables; q=2 fallback unexercised
```

Broad V18 publication robustness remains **REJECTED**.

24-seed paired additive-noise result:

```text
0.08..0.12 delta : 24/24
0.13             : 23/24
0.14             : 20/24
0.15             : 16/24
0.16             :  9/24
0.17             :  4/24
0.18             :  1/24
```

Re-quantization remains alignment-dependent and non-monotonic; no scalar threshold claim.

## 5. V20 state

Status: **CURRENT_BOUNDED_REINTEGRATION**.

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
RS byte-error bound       <=4 bytes per shard
parity total              32 bytes
payload parity overhead   6.25%
```

Integrity:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw numeric b is not in the V20 envelope tag. Final acceptance requires exact SHA-256 equality to the authenticated target in B.

Across the tested stronger numeric-damage grid:

```text
V20 failure <=> at least one 128-byte shard has >4 candidate byte errors
```

Mismatch count: **0**.

## 6. Physical structural damage v1

Status: **BOUNDED_LAYER_MAPPING_PASS**.

Frozen seeds `1001..1024`; actual public NPZ mutation; deterministic V18 and V20 geometry unchanged.

```text
whole x+y table deletion
  -> A locator first failure
  -> R@100 = 0
  -> median rank = 1749
  -> no candidate payload

one tail y-segment truncation
  -> locator remains rank 1
  -> decoder cannot form candidate
  -> V20 cannot participate

4-segment numeric burst, sigma=4 delta
  -> candidate byte errors = 4
  -> 24/24 V20 repair

6-segment numeric burst, sigma=4 delta
  -> candidate byte errors = 6
  -> 0/24 V20 repair
```

This proved that structural deletion/truncation were upstream failures and that adding more V20 parity was not the correct first response.

Evidence:

```text
results/physical-structural-damage-v1-plan.md
results/physical-structural-damage-v1.json
results/physical-structural-damage-v1.md
```

## 7. Structural erasure v2 candidate

Status: **EXECUTION GATE FAIL / EVIDENCE VALID / PROMOTION DEFERRED**.

This experiment tests two candidates without replacing the promoted A-v3/V18/V20 path:

```text
A-v4 candidate
  stable public label = x-grid length
  missing table = erasure, not renormalization of all survivors
  B is still not parsed during ranking

decoder-v2 candidate
  missing table -> zero-fill declared payload bit interval + mark erasure
  tail truncation -> decode complete prefix + zero-fill missing tail

V20
  unchanged
```

Frozen seeds `1101..1124`.

### Clean

```text
24/24 exact
24/24 V20 accepted
R@100 = 1
median rank = 1
max rank = 2
```

The frozen promotion gate required every clean target to rank 1, so it **fails**.

Seed `1116` diagnosis:

```text
target index          = 1058
full-score near-decoy = 842
decoy score           = 1.0
```

The existing near-decoy generator preserves six positions and shuffles the other six. That shuffle can be the identity, which in this seed created a genuine **12/12 A-visible descriptor duplicate** before the target.

Therefore:

- the rank-1 gate stays failed; it is not relaxed post hoc;
- the result does not show x-grid length became seed-unstable;
- an exact A-visible duplicate is inherently indistinguishable to an A-only locator using that descriptor;
- protocol-level disambiguation remains Top-K retrieval followed by authenticated open.

### Whole-table deletion

A-v4/decoder-v2 move the failure to the correct layer:

```text
locator score = 11/12 = 0.9167
R@100 = 1
median rank = 1
max rank = 2
candidate payload = 24/24
```

But the missing logical-first table contains:

```text
341 payload bits
43 payload bytes touched
median/max candidate byte errors = 43 / 43
max errors in one 128-byte shard = 43
```

Unchanged V20 recovery:

```text
0/24
```

### One tail segment truncation

Decoder-v2 now forms a candidate in all runs:

```text
erased payload bits = 5
bytes touched        = 1
candidate byte errors median/max = 1 / 1
```

Outcome:

```text
3/24 direct exact
21/21 V20 repair success
24/24 final acceptance
```

So the previous tail-truncation failure was a candidate-formation problem, not a parity shortage.

### Information bound from whole-table loss

Current V20 carries:

```text
32 parity bytes = 256 parity bits
```

A single logical-first table exposes:

```text
341 arbitrary payload bits
```

Therefore:

```text
256 < 341
shortfall = 85 bits = 10.625 bytes
```

Even with perfect erasure location and ideal use of current parity, **interleaving alone cannot guarantee recovery of one arbitrary whole-table loss**. Additional structural redundancy or less data per independently losable table is required.

Evidence:

```text
results/structural-erasure-v2-plan.md
results/structural-erasure-v2.json
results/structural-erasure-v2.md
workflow run 41453152997
artifact     13144773631
artifact zip sha256:3dbd1a245c224f5cb466ec988a5c1f0ee11f1860663b950d08d65e50a581c47c
```

## 8. Paper bundle v7

Paper-v7 produces 4 SVG figures, 12 raw-data CSV files, figure/data manifests, claim traceability, explicit synthetic/mock labeling, validation, and a complete bundle manifest.

Selected examples remain:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

The last paper-only ~1e-16 `np.polyfit` drift was replaced with fixed-order analytic linear regression + `math.fsum` R². No carrier parameter changed.

## 9. Current classification

```text
V12 -> CURRENT clean-host carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 deterministic -> CURRENT_BOUNDED_REINTEGRATION + declared-CI determinism PASS
V19 -> NEEDS-REINTEGRATION, not immediate priority
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped RS-capacity boundary
V21 -> retain "protocol constraints before rate" only
Current E2E -> PASS
Paper bundle v7 -> PASS
Deterministic basis v1 -> PROMOTION_GATES_PASS
Physical structural damage v1 -> BOUNDED_LAYER_MAPPING_PASS
A-v4 / decoder-v2 -> CANDIDATE ONLY; EVIDENCE VALID; PROMOTION DEFERRED
```

## 10. Known unresolved issues, ordered by project value

1. A-v4 public x-length profile stability across package configurations is not proven; do not promote it yet.
2. Locator gate semantics under exact A-visible descriptor duplicates need an explicit protocol decision; the failed rank-1 gate must not be retroactively relaxed.
3. Guaranteed single-table recovery requires enough structural redundancy for at least 341 arbitrary erased payload bits; current V20 has only 256 parity bits.
4. Broader structural families remain unmapped: multi-table loss, insertion/reordering, partial x loss, split/merge, authenticated B/r structural damage.
5. V18 q=2 fallback remains unexercised.
6. Re-quantization alignment structure is measured but not mechanistically modeled.
7. V20 6.25% geometry is not shown minimal/optimal for numeric damage.
8. V19 remains non-current.
9. Exact semantic identity outside the declared CI environment is not proven.
10. No universal undetectability/security or real-publication claim is supported.

## 11. Highest-value next work

Do not continue parser work for the already-fixed single-tail-segment case, and do not blindly increase RS parity.

The next high-value design problem is:

```text
one independently losable table carries 341 payload bits
current total V20 parity carries only 256 bits
=> whole-table guaranteed recovery is impossible with current redundancy
```

Design a **structural redundancy layout** that can cover one table erasure while preserving A/B responsibilities and keeping overhead explicit. Candidate directions can include table-level systematic erasure coding or a payload layout that reduces data exposed per independently losable table, but the design should be derived from the 341-bit lower bound before any parameter grid is run.

Keep A-v4/decoder-v2 as candidates only until locator collision/gate semantics and profile stability are separately resolved.
