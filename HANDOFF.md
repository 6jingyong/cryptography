# HANDOFF — audited protocol state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative. Historical prose and legacy V18–V21 numbers are not.

## 1. Authoritative lifecycle

```text
A -> locate/rank c -> authenticated open -> decode b -> optional outer repair -> exact a
```

```text
A = long-lived locator / canonicalization / bootstrap root
B = per-package reconstruction + reliability manifest
b = processed numeric payload representation
r = optional V20 repair bytes, masked and authenticated with B
c = public candidate package
a = final synthetic payload
d = unrelated public/background record
```

Package-specific q, transform, geometry, ECC, host model, payload length, padding, publication parameters, outer-code family, shard size and parity geometry belong in `B`, not long-lived `A`.

## 2. Audited base state

- Protocol-v3 locator uses `A + public NPZ structure` and does not parse B before ranking: **PASS**.
- Clean-host V12 E5: 8/8 unique payload hashes, 8/8 exact recovery, Recall@20=1, Recall@100=1, median target rank=1.
- Structural-v4 remains descriptor-level A-layer evidence only; it does not prove arbitrary physical NPZ deletion/split/merge survival.
- Paper claim gate v7 remains PASS only for bounded C1–C6 claims; C5 remains mandatory.

## 3. V18 current state

Current V18 implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

The sender observes a non-zero residual host before embedding. Host-aware modulo-QIM moves free-subspace coefficients to payload cosets. Concrete q/host/geometry/decoder state remains in B.

Supported bounded evidence:

```text
smooth reference: 8/8 current-protocol exact
known-host matrix: 5/5 frozen residual families pass
q=4 selected for all tested tables; q=2 fallback remains unexercised
```

Broad V18 publication robustness is **REJECTED**.

24-seed paired additive noise established a monotonic strength axis under paired scaling:

```text
sigma/delta : exact/24
0.08..0.12 : 24/24
0.13       : 23/24
0.14       : 20/24
0.15       : 16/24
0.16       :  9/24
0.17       :  4/24
0.18       :  1/24
```

Dense re-quantization is non-monotonic and alignment-dependent; a scalar threshold is rejected.

## 4. V18 residual-error profile

Fresh seeds 601–624 showed that transition-region failures are sparse after the existing inner Hamming code.

Across 37 failed paired-noise packages:

```text
payload bit errors        median 2, p90 4, max 4
bad tables                median 1, p90 2, max 3
bad corrected codewords   median 1, p90 2, max 3
raw payload-symbol errors median 18
post-Hamming symbol errs  median 2
```

Across 23 failed representative re-quantized packages:

```text
payload bit errors        median 2, p90 3, max 5
bad tables                median 1, p90 1, max 2
bad corrected codewords   median 1, p90 1, max 2
raw payload-symbol errors median 15
post-Hamming symbol errs  median 1
```

This justified testing a small V20 outer code rather than enlarging V18 delta or retuning the carrier.

Evidence:

```text
results/v18-error-profile-plan.md
results/v18-error-profile.json
results/v18-error-profile.md
```

## 5. V20 bounded reintegration — CURRENT within declared matrix

Implementation:

```text
protocol/real-package-v20.py
protocol/v20-bounded-reintegration.py
```

Frozen first geometry:

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
parity total              32 bytes
payload parity overhead   6.25%
```

No alternate geometry was tried in the result set.

### V20 integrity semantics

V20 deliberately does **not** reuse v3/v18 raw `HMAC(B+b)` semantics, because raw-b authentication would reject any post-seal numeric publication transform before repair.

Instead:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw `b` is excluded from this envelope tag. B contains the authenticated expected final payload SHA-256 and concrete outer-code geometry.

Receiver flow:

1. locator ranks from public b without parsing B;
2. authenticate B + masked r;
3. decode damaged b to candidate payload;
4. accept directly if candidate hash equals authenticated target;
5. otherwise repair candidate using authenticated RS parity;
6. accept only if repaired payload SHA-256 exactly equals the authenticated target in B.

Repair bytes are HMAC-stream masked under A before storage in `r`. A repair-field bitflip with unchanged tag is rejected.

### Frozen 24-seed post-seal result

Clean:

```text
24/24 exact; no repairs attempted
```

Paired additive noise:

```text
condition    V18 direct   V20 final
0.14 delta   20/24        24/24
0.15 delta   15/24        24/24
0.16 delta    7/24        24/24
```

Representative re-quantization:

```text
condition    V18 direct   V20 final
1.06x        17/24        24/24
1.20x        19/24        24/24
1.30x        17/24        24/24
```

Across all six damaged conditions:

```text
49 repair attempts
49 successful repairs
corrected shards: median ~1, maximum 2
all accepted final payload hashes exact
all locator structural scores = 1.0
repair-field tamper control rejected
```

Frozen gate: **PASS**.

Evidence:

```text
results/v20-bounded-reintegration-plan.md
results/v20-bounded-reintegration.json
results/v20-bounded-reintegration.md
```

Supported claim:

> A bounded V20 logical outer-reliability layer with 6.25% RS parity overhead passes the declared synthetic 24-seed / six-condition post-seal numeric-damage matrix.

Do not upgrade this to universal post-seal robustness, real-publication robustness, optimal redundancy, raw-b byte integrity, cryptographic security, or restoration of historical V20 metrics.

## 6. Current classification

```text
V12 -> CURRENT clean-host b carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old terminology stale
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION
       - known-host feasibility supported
       - broad publication robustness REJECTED
       - re-quantization scalar threshold REJECTED
       - sparse residual-error profile measured
V19 -> NEEDS-REINTEGRATION
V20 -> CURRENT_BOUNDED_REINTEGRATION
       - fixed 6.25% RS geometry passes frozen six-condition matrix
       - logical B+r authentication + final payload hash, not raw-b integrity
V21 -> retain "protocol constraints before rate" only; old quantitative results STALE
```

Historical V18/V20 precise summaries remain retired unless recreated by current executable evidence.

## 7. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion / changed table count.
3. Cross-platform QR/eigh/sign basis determinism remains unresolved.
4. V18 q=2 fallback remains unexercised.
5. Re-quantization alignment structure is measured but not mechanistically modeled.
6. V20 has only one frozen RS geometry and one 24-seed / six-condition damage matrix.
7. V20 behavior under stronger, differently structured, burst/table-level, repair-field loss, or manifest damage is not characterized.
8. 6.25% parity overhead is not shown optimal or minimal.
9. V19 is not current.
10. No universal undetectability/security or real-publication claim is supported.

## 8. Next work

Do **not** optimize bit/value and do not tune V20 redundancy downward/upward yet.

The next useful step is to characterize the **failure envelope of the now-fixed V20 geometry**, not to search for a better code immediately. Use fresh seeds and hold 4x128B + 8 parity bytes/shard fixed while testing stronger or structurally different post-seal damage, including conditions designed to exceed four byte errors within one shard and conditions that spread damage across shards.

Also separate recoverable numeric-b damage from unrecoverable/authentication-sensitive B/r damage. The goal is to identify where this exact V20 geometry stops working. If it fails, record the boundary before considering another geometry.

AUDIT GATE: PASS — V18 remains bounded; V20 first fixed geometry passes its frozen post-seal matrix
