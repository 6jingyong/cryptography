# HANDOFF — audited project state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current checked-in machine evidence and reproducible CI are authoritative. Historical prose and retired V18–V21 claims are not.

## 1. Project orientation

Do not treat this project as a carrier-parameter contest.

```text
synthetic payload a
-> numeric b
-> per-package B (+ optional repair r)
-> candidate c mixed among unrelated synthetic d
-> long-lived A locates / bootstraps c without parsing B during ranking
-> authenticated open
-> B explains b; reliability layers may repair
-> exact a
-> same machine package/results feed a clearly labeled mock-paper bundle
```

```text
A = long-lived locator / canonicalization / bootstrap root
B = per-package reconstruction + reliability manifest
```

Package-specific q, transform, geometry, ECC, host model, publication parameters, basis version, structural data/parity roles, shard size, parity geometry, etc. belong in B, not A.

Priority:

```text
find c > authenticate/open c > interpret B > exact a > reproducible evidence > traceable presentation > rate/overhead optimization
```

## 2. Current promoted path

The current promoted path is still:

```text
A-v3
+ src/noisy_host_package_v18_deterministic.py
+ bounded V20
```

Current engine:

```text
basis_version = deterministic-dct-mgs-v1
```

Legacy engine remains:

```text
src/noisy_host_package_v18.py
```

The structural-parity-v3 candidate has passed its own frozen gate but is **not yet promoted**. It must first pass current-E2E + paper-v7 integration.

## 3. Deterministic V18 promotion

Frozen promotion gates:

```text
Gate A — current protocol viability
8/8 unique payload hashes
8/8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median/max target rank = 1/1
paper-v7 = PASS

Gate B — independent-run semantic determinism
2 independent GitHub Actions runners
semantic_equal = true
mismatch_count = 0
raw NPZ container hash equal = true
semantic authority SHA-256 = 243b05fd32624e931379ea471c2d209700fb3491c33a911f9071084e8f57bc04

Gate C — bounded evidence regression
V18 core/residual/publication/error-profile = PASS
V20 bounded/failure-envelope = PASS
q/delta/RS geometry not retuned
```

Boundary: exact semantic reproducibility is established only across the declared independent GitHub Actions environment, not every CPU/libm/NumPy/Python platform.

## 4. V18 state

Status: **CURRENT_BOUNDED_REINTEGRATION + DECLARED-CI DETERMINISM PASS**.

Current bounded evidence includes:

```text
smooth reference 8/8 exact
five frozen sender-observed residual families pass
q=4 selected for tested tables
q=2 fallback unexercised
```

Broad V18 publication robustness remains **REJECTED**.

24-seed paired additive noise:

```text
0.08..0.12 delta : 24/24
0.13             : 23/24
0.14             : 20/24
0.15             : 16/24
0.16             :  9/24
0.17             :  4/24
0.18             :  1/24
```

Re-quantization remains alignment-dependent and non-monotonic; no universal scalar threshold claim.

## 5. V20 state

Status: **CURRENT_BOUNDED_REINTEGRATION**.

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
RS byte-error bound       <=4 bytes/shard
parity total              32 bytes
payload parity overhead   6.25%
```

Integrity:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw b is not in the envelope tag. Final acceptance requires exact SHA-256 equality to the authenticated target in B.

Across the tested stronger candidate-producing numeric-damage grid:

```text
V20 failure <=> at least one 128-byte shard has >4 candidate byte errors
```

Mismatch count: **0**.

## 6. Structural evidence progression

### 6.1 Physical structural damage v1

Status: **BOUNDED_LAYER_MAPPING_PASS**.

Fresh seeds `1001..1024`, actual NPZ mutation, deterministic V18 and V20 unchanged.

```text
whole x+y table deletion
  -> current A-v3 locator first failure
  -> R@100 = 0
  -> median rank = 1749
  -> no candidate

one tail y-segment truncation
  -> locator rank 1
  -> decoder fails before candidate
  -> V20 cannot participate

4-segment localized numeric burst
  -> 4 candidate byte errors
  -> 24/24 V20 repair

6-segment localized numeric burst
  -> 6 candidate byte errors
  -> 0/24 V20 repair
```

Conclusion: whole-table deletion and tail truncation were upstream structural failures; adding V20 parity first would have been a wrong-layer fix.

### 6.2 Structural erasure v2

Status: **EXECUTION GATE FAIL / EVIDENCE VALID / PROMOTION DEFERRED**.

Candidates:

```text
A-v4
  stable label = public x-grid length
  missing table = one erasure
  B not parsed during ranking

decoder-v2
  decode all complete prefix segments
  expose missing payload bits as erasures
```

Fresh seeds `1101..1124`.

Clean:

```text
24/24 exact
R@100 = 1
median rank = 1
max rank = 2
```

The frozen strict rank-1 gate failed because seed `1116` contained an exact 12/12 A-visible near-decoy descriptor duplicate before the target. This gate remains failed; it was never relaxed post hoc. The collision also established that an A-only locator cannot uniquely order records with identical A-visible evidence, so protocol disambiguation must ultimately rely on Top-K retrieval + authenticated open.

Whole-table deletion under A-v4/decoder-v2:

```text
locator score = 11/12
R@100 = 1
candidate 24/24
341 payload bits erased
43 payload bytes touched
current V20 final recovery 0/24
```

Tail truncation:

```text
5 payload bits erased
candidate 24/24
3/24 direct exact
21/21 V20 repairs
24/24 final acceptance
```

Information bound:

```text
whole-table unknown information = 341 bits
current total V20 parity        = 256 bits
shortfall                       = 85 bits
```

Therefore current V20 cannot guarantee recovery of one arbitrary whole-table erasure even with perfect erasure location.

### 6.3 Structural parity v3

Status: **PROMOTION GATE PASS / WHOLE-SYSTEM PROMOTION PENDING**.

Frozen choice before results:

```text
11 data tables
+ 1 XOR structural-parity table
= 12 public tables total
```

Why 11+1 rather than 12+1:

- 11+1 preserves the existing 12-table public profile;
- 12+1 would save only ~0.76 percentage points of structural overhead but require a 13th x-grid/family/budget and change downstream 12-table assumptions.

For 4096 payload bits, 11 data chunks are:

```text
372, 373, 372, 372, 373, 372, 373, 372, 372, 373, 372 bits
```

Structural parity:

```text
373 bits
46.625 bytes equivalent
9.1064453125% of payload
```

The table's data/parity role is B state. A-v4 sees only stable public x-grid identities. q/delta and current V20 are unchanged.

Frozen fresh seeds `1201..1224`. Every public table was independently damaged for every seed:

```text
24 clean controls
288 complete one-table deletions
288 one-tail-segment truncations
600 total observations
```

Frozen gate required:

```text
Top-20 locator retrieval
candidate formation
zero unresolved structural payload bits
exact payload recovery
final authenticated acceptance
```

Result:

```text
clean
  24/24 directly exact
  R@20 = 1
  max rank = 1

any one public table deleted
  288/288 candidates
  288/288 directly exact
  288/288 accepted
  R@20 = 1
  median locator score = 11/12
  unresolved structural bits max = 0
  V20 repair attempts = 0

any one public table tail-truncated
  288/288 candidates
  288/288 directly exact
  288/288 accepted
  R@20 = 1
  unresolved structural bits max = 0
  V20 repair attempts = 0
```

Breakdown:

```text
data-table deletion          264/264 exact
parity-table deletion         24/24 exact
data-table tail truncation   264/264 exact
parity-table tail truncation  24/24 exact
```

This is the first current candidate to make bounded single-table structural erasure a **pre-V20 solved problem**. V20 remains a separate layer for residual numeric corruption rather than structural table loss.

Evidence:

```text
results/structural-parity-v3-plan.md
results/structural-parity-v3.json
results/structural-parity-v3.md
protocol/structural-parity-v3.py
workflow run 41495970007
job          125450880152
artifact     13166113925
artifact zip sha256:f4b8d67f75552991a18674a6405642eca507f5db9e275a59e5418af4e84f5be9
```

Boundary: this proves only the declared synthetic single-table/single-tail-segment matrix. It does not prove two-table recovery, insertion/reordering robustness, optimal redundancy, real-publication behavior, or security.

## 7. Current E2E and paper-v7

Current promoted E2E seeds `901..908` remain:

```text
8/8 distinct payload hashes
8/8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median/max target rank = 1/1
```

Paper-v7 remains PASS and produces:

```text
4 SVG figures
12 raw-data CSV files
figure/data manifests
claim traceability
explicit synthetic/mock manuscript
complete bundle manifest
```

The last paper-only ~1e-16 `np.polyfit` drift was replaced with fixed-order analytic linear regression + `math.fsum` R²; no carrier parameter changed.

## 8. Current classification

```text
V12 -> CURRENT clean-host carrier baseline
V16 -> HISTORICAL-BUT-VALID A-layer benchmark
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 deterministic -> CURRENT_BOUNDED_REINTEGRATION + declared-CI determinism PASS
V19 -> NEEDS-REINTEGRATION, deferred
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped RS-capacity boundary
V21 -> retain "protocol constraints before rate" principle only
Current E2E -> PASS
Paper bundle v7 -> PASS
Deterministic basis v1 -> PROMOTION_GATES_PASS
Physical structural damage v1 -> BOUNDED_LAYER_MAPPING_PASS
Structural erasure v2 -> EVIDENCE_VALID / GATE_FAIL / PROMOTION_DEFERRED
Structural parity v3 -> PROMOTION_GATE_PASS / CURRENT-E2E INTEGRATION PENDING
```

## 9. Highest-value unresolved work

1. Integrate A-v4 + 11+1 structural parity + deterministic V18 + unchanged V20 into one current-E2E/paper-v7 gate before promotion.
2. Verify A-v4 public x-length profile remains stable across the package configurations that the current system actually supports.
3. Preserve the protocol rule that exact A-visible duplicates are resolved by Top-K + authenticated open; do not invent an impossible rank-1 guarantee.
4. Only after single-table integration succeeds, consider broader structural families such as two-table loss, insertion/reordering, partial x loss, split/merge, or authenticated B/r damage.
5. V18 q=2 fallback remains unexercised.
6. Re-quantization alignment mechanism remains unmodeled.
7. V20 6.25% geometry is not shown minimal/optimal for numeric damage.
8. Exact semantic identity outside the declared CI environment is not proven.
9. No universal undetectability/security or real-publication claim is supported.

## 10. Next action

Do **not** run another parity grid now.

The next gate should be one integrated path:

```text
A-v4
+ 11+1 XOR structural parity
+ deterministic V18
+ unchanged V20
-> current E2E
-> paper-v7
```

Freeze that integration before results. If it passes without q/delta/RS retuning and without deterministic/presentation regression, then structural-parity-v3 becomes a legitimate whole-system promotion candidate.
