# Structural erasure v2 candidate

Status: **EXECUTION GATE FAIL / EVIDENCE VALID / PROMOTION DEFERRED**

Scope: synthetic/mock benchmark only.

This run tested two upstream candidate changes without replacing the current A-v3/V18/V20 path:

```text
A-v4 candidate       = independent public x-grid-length labels
Decoder-v2 candidate = decode complete prefix + explicit zero-filled erasure intervals
V20                  = unchanged 4 x 128 B shards, 8 parity B/shard
```

Frozen conditions are in `structural-erasure-v2-plan.md`. Damaged outcomes were never pass/fail criteria.

## Main result

| condition | locator median | R@100 | candidate | final V20 accept | key observation |
|---|---:|---:|---:|---:|---|
| clean | 1.0000 | 1.0 | 24/24 | 24/24 | exact decode 24/24, but one clean target ranks 2 |
| delete logical-first table | 0.9167 | 1.0 | 24/24 | 0/24 | locator/parser problem is removed; remaining loss is too large for current V20 |
| truncate one tail segment | 1.0000 | 1.0 | 24/24 | 24/24 | 3 direct exact + 21/21 repaired |

The frozen promotion gate required every clean target to rank 1. It therefore **fails** because seed `1116` has clean target rank 2. The gate is not relaxed after seeing the result.

## What A-v4 actually fixed

Under physical-structural-damage-v1, deleting one table caused the current A-v3 locator to collapse:

```text
median target rank = 1749
R@100 = 0
candidate payload = 0/24
```

With A-v4's independently stable x-grid labels, the same class of one-table deletion becomes:

```text
locator score = 11/12 = 0.9167
median rank = 1
max rank = 2
R@100 = 1
candidate payload = 24/24
```

This supports the architectural point: a missing label should be treated as an erasure; it should not renormalize every surviving table identity.

## Why the clean rank-1 gate failed

Post-run deterministic diagnosis of seed `1116`:

```text
target index            = 1058
full-score near-decoy   = 842
decoy locator score     = 1.0
```

The existing descriptor near-decoy generator preserves six positions and shuffles the other six. That shuffle is allowed to be the identity. In this seed it produced a **12/12 exact A-visible descriptor duplicate**, which appears before the target under stable sorting.

Therefore the observed rank-2 case is not evidence that x-grid length itself became seed-unstable. It is a genuine A-visible descriptor collision admitted by the current corpus generator. Any locator restricted to exactly the same A-visible descriptor is unable to distinguish those two records; the protocol-level disambiguation mechanism is Top-K retrieval followed by authenticated open.

This does **not** retroactively turn the frozen rank-1 gate into a pass. It means the proper classification is `PROMOTION_DEFERRED`, not `A-v4 disproved`.

## Decoder-v2 result

### One tail segment missing

The logical-first table carries 341 payload bits. Its final segment contains only the last 5 payload bits plus padding, so removing that complete segment produces:

```text
erased payload bits       = 5
bytes touched by erasure  = 1
candidate byte errors     = median 1, max 1
```

All 24 seeds produce a complete candidate payload.

- 3/24 candidates are already exact because all 5 missing payload bits happen to be zero.
- the remaining 21/24 invoke the unchanged V20 repair path;
- repair succeeds 21/21;
- final acceptance is 24/24.

So the previous truncation failure was primarily a parser/candidate-formation problem, not a need for more parity.

### One whole table missing

Deleting the logical-first table erases:

```text
341 payload bits
43 payload bytes touched
median/max candidate byte errors = 43 / 43
max errors in one 128-byte shard = 43
```

Decoder-v2 now forms a candidate in 24/24 runs, but current V20 repairs 0/24. This is the correct layer transition: the failure has moved from locator/parser into explicit outer-reliability capacity.

## Information bound

This result gives a stronger conclusion than another parity grid would.

A whole logical-first table contains 341 arbitrary payload bits. Current V20 carries only:

```text
32 parity bytes = 256 parity bits
```

Even with perfect erasure location and an ideal decoder, `256 < 341`. Therefore **interleaving alone cannot guarantee recovery of one arbitrary whole-table loss with the current 6.25% redundancy**.

The minimum redundancy shortfall is:

```text
341 - 256 = 85 bits = 10.625 bytes
```

That does not by itself specify the best new code geometry, but it rules out spending time trying to make the existing 32-byte parity magically solve this failure.

## Project-level consequence

The structural path now separates cleanly:

```text
single tail-segment loss
-> A survives
-> decoder-v2 forms candidate
-> current V20 is already sufficient

whole-table loss
-> A-v4 can still locate
-> decoder-v2 forms candidate
-> current V20 is information-theoretically under-provisioned for guaranteed recovery
```

So the next high-value design question is no longer parser robustness. It is **where to place at least one-table-worth of structural redundancy, and how to do so without contaminating A/B responsibilities or merely tuning RS numbers**.

## Evidence

- frozen experiment branch: `structural-erasure-v2-20261102`
- first run: `41452612409`
- evidence-preserving rerun: `41453152997`
- job: `125303077515`
- artifact: `13144773631`
- artifact ZIP SHA-256: `3dbd1a245c224f5cb466ec988a5c1f0ee11f1860663b950d08d65e50a581c47c`

## Boundary

Still unsupported: A-v4 promotion, universal structural robustness, arbitrary insertion/reordering/multi-table loss, optimal parity geometry, real-publication robustness, confidential-payload hiding, or undetectability/security.
