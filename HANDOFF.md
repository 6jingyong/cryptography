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

Package-specific q, transform, geometry, ECC, host model, payload length, publication parameters, outer-code family, shard size and parity geometry belong in `B`, not long-lived `A`.

## 2. Base / locator state

- Protocol-v3 locator uses `A + public NPZ structure` and does not parse B before ranking: **PASS**.
- Clean-host V12 E5: 8/8 unique payload hashes, 8/8 exact recovery, Recall@20=1, Recall@100=1, median target rank=1.
- Structural-v4 remains descriptor-level A-layer evidence only; it does not prove arbitrary physical NPZ deletion/split/merge survival.
- Paper claim gate v7 remains PASS only for bounded C1–C6 claims; C5 remains mandatory.

## 3. V18 state

Current V18 implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

V18 is **CURRENT_BOUNDED_REINTEGRATION**.

Supported bounded evidence:

```text
smooth reference: 8/8 current-protocol exact
known-host matrix: 5/5 frozen sender-observed residual families pass
q=4 selected for all tested tables; q=2 fallback remains unexercised
```

Broad V18 publication robustness is **REJECTED**.

24-seed paired additive-noise statistics:

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

V18 transition-region residual errors after the existing Hamming layer are sparse:

```text
paired-noise failures: median 2 payload bits, 1 bad table, 1 bad corrected codeword
representative requant failures: median 2 payload bits, 1 bad table, 1 bad corrected codeword
```

This sparse profile motivated V20 rather than V18 carrier retuning.

## 4. V20 implementation and integrity semantics

Implementation:

```text
protocol/real-package-v20.py
protocol/v20-bounded-reintegration.py
protocol/v20-failure-envelope.py
```

Fixed geometry:

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
RS byte-error bound       <=4 bytes per shard
parity total              32 bytes
payload parity overhead   6.25%
```

V20 deliberately does **not** reuse old raw `HMAC(B+b)` semantics. Instead:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw numeric `b` is excluded from the V20 envelope tag. B contains the authenticated expected final payload SHA-256 and concrete reliability geometry.

Receiver flow:

1. locator ranks from public b without parsing B;
2. authenticate B + masked r;
3. decode damaged b;
4. accept directly if candidate payload hash equals authenticated target;
5. otherwise use authenticated RS parity to repair;
6. accept only if repaired payload SHA-256 exactly equals the authenticated target in B.

Repair bytes are HMAC-stream masked under A before storage in `r`.

## 5. V20 first bounded gate — PASS

Fresh seeds 701–724, frozen before results.

```text
condition                 V18 direct   V20 final
clean                     24/24        24/24
noise 0.14 delta          20/24        24/24
noise 0.15 delta          15/24        24/24
noise 0.16 delta           7/24        24/24
requant 1.06x             17/24        24/24
requant 1.20x             19/24        24/24
requant 1.30x             17/24        24/24
```

Across six damaged conditions: 49 repair attempts, 49 successes; successful repairs touched at most two 128-byte shards. Final authenticated payload hashes were exact, locator score remained 1.0, and repair-field tamper was rejected.

Evidence:

```text
results/v20-bounded-reintegration-plan.md
results/v20-bounded-reintegration.json
results/v20-bounded-reintegration.md
```

## 6. V20 fixed-geometry failure envelope

Fresh seeds 801–824. Geometry and protocol remained unchanged.

### Paired additive noise

```text
sigma/delta   V20 exact   packages with any shard >4 byte errors
0.16          24/24       0
0.18          24/24       0
0.20          17/24       7
0.22           5/24       19
0.25           0/24       24
0.30           0/24       24
0.35           0/24       24
```

First tested V20 failure point: **0.20 delta**.

At 0.20 delta, exactly seven packages crossed the RS per-shard capacity and exactly seven V20 packages failed.

### Re-quantization

```text
factor        V20 exact   packages with any shard >4 byte errors
1.30x         24/24       0
1.50x         24/24       0
1.75x         20/24       4
2.00x          0/24       24
2.50x          0/24       24
3.00x          0/24       24
```

First tested V20 failure point: **1.75x**.

At 1.75x, exactly four packages crossed the RS per-shard capacity and exactly four V20 packages failed.

### Capacity alignment

Across every individual run in the frozen stronger grid:

```text
V20 failure  <=>  at least one 128-byte shard has >4 candidate byte errors
```

Observed mismatch count: **0**.

All locator structural scores remained 1.0. Manifest-B and masked-repair-r bitflip controls were both rejected by envelope integrity.

Interpretation: within the tested synthetic channel, V20 does not exhibit an earlier unexplained protocol failure. It remains successful until the fixed Reed-Solomon per-shard correction capacity is actually exceeded.

Evidence:

```text
results/v20-failure-envelope-plan.md
results/v20-failure-envelope.json
results/v20-failure-envelope.md
```

The listed 0.20-delta and 1.75x values are **first tested failure grid points**, not universal continuous thresholds.

## 7. Current classification

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
       - fixed 6.25% RS logical repair envelope
       - first frozen matrix PASS
       - stronger failure envelope mapped
       - observed failures align exactly with >4 byte errors in a shard
V21 -> retain "protocol constraints before rate" only; old quantitative results STALE
```

Historical V18/V20 precise summaries remain retired unless recreated by current executable evidence.

## 8. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion / changed table count.
3. Cross-platform QR/eigh/sign basis determinism remains unresolved.
4. V18 q=2 fallback remains unexercised.
5. Re-quantization alignment structure is measured but not mechanistically modeled.
6. V20 has only one RS geometry; 6.25% overhead is not shown minimal or optimal.
7. V20 has not been tested against physical table deletion, missing repair bytes, partial manifest loss, or other non-numeric structural damage beyond authenticated bitflip rejection.
8. The current failure boundary is tied to the declared synthetic damage families and grid.
9. V19 is not current.
10. No universal undetectability/security or real-publication claim is supported.

## 9. Next work

Do **not** immediately optimize parity overhead or bit/value.

The most useful next step is now a protocol-level choice:

- either test **structurally different damage** with the same V20 geometry (table deletion/truncation/burst loss) to see whether the RS shard model is still appropriate;
- or rebuild V19 as a selector that chooses only among already-audited carrier/reliability modes.

Because the numeric-damage V20 failure mechanism is now cleanly explained by its declared RS capacity, more points on the same additive-noise/re-quantization axes have diminishing value.

AUDIT GATE: PASS — V18 remains bounded; V20 fixed geometry passes its initial matrix and has an explicit measured capacity-aligned failure envelope
