# V20 bounded outer-reliability reintegration

Scope: **synthetic/mock benchmark only**.

The first V20 geometry was frozen before results and passed its declared gate without retuning.

Source CI:

```text
workflow run: 41374655647
artifact:     13109779354
artifact sha: 4c080cee1bf1fc2ca9bee35efcb1023e7f2c31ee74870b1fec53ead20739682c
```

## Fixed geometry

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
maximum byte errors / shard (RS bound) 4
parity total              32 bytes
payload parity overhead   6.25%
```

No alternate parity or shard size was tried in this result set.

## Integrity model

This is intentionally different from v3/v18 raw-byte outer integrity.

V20 authenticates:

```text
B + masked repair bytes r
```

and **does not** include raw numeric `b` in the V20 envelope tag. This lets a post-seal numeric publication transform modify `b` without making repair impossible by construction.

Acceptance remains strict:

1. authenticate B + masked r;
2. decode damaged b to candidate payload;
3. if candidate hash matches authenticated B, accept directly;
4. otherwise use authenticated RS parity to repair the candidate;
5. accept only if repaired payload SHA-256 exactly matches the authenticated target in B.

A repair-field bitflip with unchanged tag was rejected as `v20_envelope_integrity_failed`.

## Frozen 24-seed result

Clean control:

```text
24/24 exact
0 repairs attempted
locator structural score = 1.0 for all
```

Paired additive noise:

| sigma/delta | V18 direct exact | V20 exact | repairs | corrected shards median / max |
|---:|---:|---:|---:|---:|
| 0.14 | 20/24 | 24/24 | 4/4 successful | 1.5 / 2 |
| 0.15 | 15/24 | 24/24 | 9/9 successful | 1 / 2 |
| 0.16 | 7/24 | 24/24 | 17/17 successful | 1 / 2 |

Representative re-quantization:

| factor | V18 direct exact | V20 exact | repairs | corrected shards median / max |
|---:|---:|---:|---:|---:|
| 1.06x | 17/24 | 24/24 | 7/7 successful | 1 / 1 |
| 1.20x | 19/24 | 24/24 | 5/5 successful | 1 / 2 |
| 1.30x | 17/24 | 24/24 | 7/7 successful | 1 / 2 |

Across the six damaged conditions there were **49 repair attempts and 49 successful repairs**. Every accepted package matched the authenticated final payload hash, and every tested locator structural score remained 1.0.

Therefore the frozen first-pass gate is **PASS**.

## Interpretation

This result is consistent with the preceding V18 error profile: failures near the tested transition are sparse enough that a small outer code can absorb them. Successful repairs affected at most two 128-byte shards, rather than requiring package-wide reconstruction.

Current supported claim:

> A bounded V20 logical outer-reliability layer with 6.25% RS parity overhead passes the declared synthetic 24-seed / six-condition post-seal numeric-damage matrix.

This does **not** mean V20 is generally robust to arbitrary post-seal damage. In particular, the experiment does not establish the optimality of 6.25% overhead, a universal damage envelope, real-publication robustness, raw-b byte integrity, or the historical V20 numerical claims.

The old raw `HMAC(B+b)` semantics and this V20 logical integrity mode must not be conflated. V20 authenticates the recovery target and repair envelope, then verifies the exact final payload hash after decode/repair.
