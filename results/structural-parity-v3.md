# Structural parity v3 candidate

Status: **PROMOTION GATE PASS / CURRENT-PATH PROMOTION NOT YET COMPLETED**

Scope: synthetic/mock benchmark only.

This candidate addresses the whole-table information shortfall identified by `structural-erasure-v2` without adding a 13th public table and without changing deterministic V18 q/delta or the current V20 geometry.

## Frozen architecture

The 512-byte payload contains 4096 bits. Instead of spreading those bits over all 12 current tables, the candidate uses:

```text
11 data tables
1 XOR structural-parity table
12 physical public tables total
```

The 11 data chunks are:

```text
372, 373, 372, 372, 373, 372, 373, 372, 372, 373, 372 bits
```

The parity table carries the XOR of the 11 right-zero-padded chunks:

```text
373 bits = 46.625 bytes
structural overhead = 9.1064453125% of the 4096-bit payload
```

The structural role of each public table belongs in B. A-v4 sees only stable public x-grid identities and does not know which table is parity.

Current V20 remains unchanged:

```text
4 x 128-byte data shards
8 parity bytes / shard
32 V20 parity bytes total
```

## Frozen matrix

Fresh seeds `1201..1224`.

For every seed, every one of the 12 public tables was tested independently under:

1. complete x+y table deletion;
2. deletion of one complete tail y-segment.

Together with clean controls:

```text
24 clean
288 one-table deletions
288 one-tail-segment truncations
600 total observations
```

The promotion gate was frozen before results. It required Top-20 locator retrieval, candidate formation, zero unresolved structural payload bits, exact payload recovery, and final authenticated acceptance for every tested damage case.

## Result

### Clean

```text
24 / 24 candidate produced
24 / 24 directly exact
24 / 24 finally accepted
Recall@20 = 1.0
median/max rank = 1 / 1
unresolved structural bits max = 0
V20 repairs attempted = 0
```

### Delete any one public table

```text
288 / 288 candidate produced
288 / 288 directly exact
288 / 288 finally accepted
Recall@20 = 1.0
median/max rank = 1 / 1
median locator score = 11/12 = 0.9167
unresolved structural bits max = 0
V20 repairs attempted = 0
```

Breakdown:

```text
data-table deletion   264 / 264 exact
parity-table deletion  24 / 24 exact
```

Deleting a data table is recovered from the XOR parity table. Deleting the parity table needs no recovery because all 11 data chunks remain present.

### Truncate one tail segment from any table

```text
288 / 288 candidate produced
288 / 288 directly exact
288 / 288 finally accepted
Recall@20 = 1.0
median/max rank = 1 / 1
unresolved structural bits max = 0
V20 repairs attempted = 0
```

Breakdown:

```text
data-table tail truncation   264 / 264 exact
parity-table tail truncation  24 / 24 exact
```

## Architectural consequence

The previous failure chain was:

```text
whole-table loss
-> current A-v3 loses useful rank
-> decoder cannot form complete payload
-> current V20 is too small to guarantee 341-bit table recovery
```

The candidate changes it to:

```text
whole-table loss
-> A-v4 treats the absent stable x-grid identity as one erasure
-> B identifies data/parity roles
-> XOR table layer reconstructs the missing payload chunk
-> exact payload exists before V20
-> authenticated acceptance
```

The important result is that **V20 no longer needs to absorb structural table loss**. It can remain a separate logical reliability layer for residual numeric corruption.

This also validates the decision not to add a 13th table yet. The 11+1 layout preserves the existing 12-table public profile while providing the missing single-table erasure capacity at 9.11% structural overhead.

## Promotion status

The candidate itself passes the frozen structural promotion gate, but it is **not yet the current promoted whole-system path**.

Current promoted path remains:

```text
A-v3
+ deterministic V18
+ current bounded V20
```

Before replacing that path, the next step is a current-E2E integration gate using A-v4 + 11+1 structural parity + deterministic V18 + unchanged V20, including the paper-v7 consumer. The goal is to verify that fixing structural reliability does not break the already-passing deterministic/presentation pipeline.

## Evidence

```text
frozen plan    results/structural-parity-v3-plan.md
candidate      protocol/structural-parity-v3.py
workflow run   41495970007
job            125450880152
artifact       13166113925
artifact zip   sha256:f4b8d67f75552991a18674a6405642eca507f5db9e275a59e5418af4e84f5be9
```

The uploaded artifact contains the complete 600-observation JSON and generated summary Markdown.

## Boundary

This supports only the declared synthetic single-table and single-tail-segment erasure matrix. It does not establish recovery from two simultaneous table losses, arbitrary insertion/reordering, optimal structural redundancy, real-publication robustness, confidential-payload hiding, or undetectability/security.
