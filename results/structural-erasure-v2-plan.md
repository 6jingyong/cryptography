# Structural erasure v2 candidate — frozen plan

Scope: **synthetic/mock benchmark only**.

This experiment follows `physical-structural-damage-v1`. That run showed two upstream structural failures before V20 could help:

```text
whole-table deletion -> A-v3 locator collapses
one tail-segment truncation -> locator survives but current decoder forms no candidate payload
```

The v2 experiment tests a bounded architectural repair **without changing the promoted current protocol yet**.

## Candidate changes frozen before results

### A-v4 candidate

Replace the current package-wide canonical class `(morphology, x-grid length)` with an independently stable public label:

```text
label = x-grid length
```

For the frozen current V18 12-table profile, public lengths are:

```text
24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46
```

They are unique and independent of q in the current engine. A-v4 owns this public profile and its keyed public-ID permutation. B is not parsed during ranking.

Missing labels are treated as erasures. The score denominator remains the full 12-table profile, so one missing otherwise-correct table should score `11/12` rather than causing every surviving label to be renormalized.

### decoder-v2 candidate

After authenticated B is available:

- missing table: zero-fill that table's declared payload-bit interval and mark it erased;
- tail truncation: decode all complete prefix segments, then zero-fill the missing tail payload bits and mark them erased;
- complete tables use the unchanged deterministic V18 decoder.

The purpose is to form a full 512-byte candidate payload rather than fail before V20.

### V20 remains unchanged

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
byte-error capacity       <=4 per shard
```

No RS geometry, repair algorithm, q, delta, host model, or publication parameter may be changed in response to results.

## Frozen experiment

Fresh seeds:

```text
1101..1124
```

Configuration:

```text
payload         512 bytes
channels        2
corpus size     2000
near decoys     1%
engine          src/noisy_host_package_v18_deterministic.py
```

Conditions:

1. clean control;
2. delete the logical-first table's x+y arrays;
3. remove one complete tail y-segment from the logical-first table.

The target table is selected deterministically by minimum payload-bit offset, then minimum public table ID.

## Execution gate

Only implementation/architecture sanity gates execution:

- clean A-v4 public map exactly matches its declared 12-label profile;
- clean locator score = 1 and rank = 1 for every seed;
- clean decoder-v2 exact recovery = 1 for every seed;
- clean V20 open passes without repair;
- A-v4 does not parse B during ranking;
- current deterministic V18 and V20 geometry are unchanged.

**Damaged outcomes are observations, never pass/fail criteria.**

## Questions this experiment is allowed to answer

- Does independent x-length labeling prevent one-table deletion from destroying locator usefulness?
- Can missing-table and tail-truncation structure be converted into a concrete candidate payload?
- Once a candidate exists, does the unchanged V20 layer recover it or fail according to its existing capacity?

## Claims this experiment cannot establish

- universal locator robustness;
- arbitrary insertion/reordering/multi-table-loss handling;
- optimal structural code or parity geometry;
- real-publication behavior;
- confidential-payload hiding, undetectability, or security.
