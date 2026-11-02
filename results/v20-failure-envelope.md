# V20 fixed-geometry failure envelope

Scope: **synthetic/mock benchmark only**.

This experiment held the already-current V20 geometry fixed and deliberately pushed post-seal numeric `b` damage until repair failed.

Source CI:

```text
workflow run: 41375218480
artifact:     13110887337
artifact sha: 07ec4b1536fd3b9adbbab19bb26b5a86f98661283d9161b1e45f7ae126b5df9c
```

## Fixed geometry

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
RS byte-error bound       <=4 bytes per shard
parity total              32 bytes
payload parity overhead   6.25%
```

No code, shard, parity, carrier, locator, or integrity parameter changed.

## Paired additive-noise boundary

| sigma/delta | V18 exact | V20 exact | packages with >4 byte errors in a shard | max byte errors in one shard |
|---:|---:|---:|---:|---:|
| 0.16 | 9/24 | 24/24 | 0 | 2 |
| 0.18 | 2/24 | 24/24 | 0 | 4 |
| 0.20 | 0/24 | 17/24 | 7 | 7 |
| 0.22 | 0/24 | 5/24 | 19 | 12 |
| 0.25 | 0/24 | 0/24 | 24 | 19 |
| 0.30 | 0/24 | 0/24 | 24 | 38 |
| 0.35 | 0/24 | 0/24 | 24 | 65 |

First tested V20 failure point: **0.20 delta**.

At `0.20 delta`, exactly seven packages exceeded the per-shard RS bound and exactly seven packages failed V20. The remaining 17 packages repaired successfully.

## Re-quantization boundary

| factor | V18 exact | V20 exact | packages with >4 byte errors in a shard | max byte errors in one shard |
|---:|---:|---:|---:|---:|
| 1.30x | 15/24 | 24/24 | 0 | 2 |
| 1.50x | 9/24 | 24/24 | 0 | 3 |
| 1.75x | 0/24 | 20/24 | 4 | 6 |
| 2.00x | 0/24 | 0/24 | 24 | 33 |
| 2.50x | 0/24 | 0/24 | 24 | 27 |
| 3.00x | 0/24 | 0/24 | 24 | 55 |

First tested V20 failure point: **1.75x**.

At `1.75x`, exactly four packages exceeded the per-shard RS bound and exactly four packages failed V20.

## Capacity alignment

Across **every individual run in the frozen stronger grid**:

```text
V20 failure  <=>  at least one 128-byte shard has >4 candidate byte errors
```

Observed mismatch count: **0**.

This is stronger evidence than simply observing declining package success. It shows that, within this synthetic damage matrix, the fixed V20 implementation continues to work until the declared Reed-Solomon correction capacity is actually exceeded. There is no observed earlier failure caused by locator loss, envelope logic, or final-hash handling.

All tested locator structural scores remained `1.0`.

Both negative integrity controls remained valid:

```text
masked repair-field bitflip + unchanged tag -> rejected
manifest B bitflip + unchanged tag          -> rejected
```

## Interpretation

The current V20 geometry now has a measured bounded failure envelope:

- paired noise: 24/24 through `0.18 delta`; first tested partial failure at `0.20 delta`;
- re-quantization: 24/24 through `1.50x`; first tested partial failure at `1.75x`.

These are **tested grid boundaries**, not universal continuous thresholds.

The mechanism of failure is also bounded and interpretable: once any fixed 128-byte shard crosses the four-byte RS error capacity, repair can fail; packages remaining within the bound repaired successfully in every tested run.

This does not prove the geometry is optimal. The correct next question is no longer “does V20 work at all?” but whether a different shard/code geometry is worth its overhead for a desired damage envelope. That is a separate design/optimization question and should not overwrite this fixed-geometry result.
