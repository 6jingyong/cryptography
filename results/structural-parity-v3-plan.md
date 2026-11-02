# Structural parity v3 — frozen candidate plan

Scope: **synthetic/mock benchmark only**.

This experiment follows `structural-erasure-v2`. It does not alter the promoted current A-v3/V18/V20 path before results.

## Decision before results

The current 512-byte payload contains 4096 bits. Under the existing 12-data-table split the tables carry 341/342 payload bits each. A whole-table deletion therefore removes more arbitrary information than the current V20 repair field can guarantee to reconstruct: V20 carries 32 parity bytes = 256 bits, while the tested first logical table carried 341 bits.

Two table-level architectures were considered:

### Option A — 11 data + 1 XOR parity inside the existing 12 public tables

- split the 4096 payload bits across 11 data chunks;
- chunk lengths are 372/373 bits;
- XOR the zero-right-padded chunks into one 373-bit parity chunk;
- encode the 11 data chunks plus one parity chunk with the existing 12 deterministic V18 carriers;
- keep the public table count at 12;
- keep q/delta/calibration rules unchanged;
- keep current V20 `4 x 128 B + 8 parity B/shard` unchanged.

Structural redundancy is 373 bits = 46.625 bytes = 9.1064453125% of the 4096-bit payload.

### Option B — retain 12 data tables and add a 13th parity table

A parity chunk would need only 342 bits = 42.75 bytes = 8.349609375% of payload, but this changes the public table count, requires a 13th x-grid/family/budget definition, changes A's table profile, and touches downstream 12-table presentation assumptions.

**Frozen choice: Option A (11+1).** The ~0.76 percentage-point structural-overhead advantage of 12+1 is not worth expanding the public protocol surface before the simpler 11+1 architecture is tested.

## A/B responsibility

The experiment reuses the **A-v4 candidate** from structural-erasure-v2:

- A sees only stable public x-grid identities for ranking;
- a missing table is an A-visible erasure, not a reason to renormalize all surviving labels;
- A does not learn which table is data or parity.

The following remain in **B**:

- which public tables carry data vs XOR parity;
- data-chunk indices and bit lengths;
- zero-right-padding rule;
- parity-table public ID;
- all V18 q/delta/geometry/basis state;
- unchanged V20 geometry.

## Decoder candidate

For each table, decode every complete prefix segment and mark any missing tail bits as erasures. Then apply bitwise XOR structural recovery:

- if exactly one data bit at a parity position is erased and the parity bit is available, recover it from XOR of parity and all known data bits;
- missing parity alone does not matter when all data are present;
- unresolved bits remain explicit and may then be passed to unchanged V20.

No structural parity is added to A and no V20 parameter is retuned.

## Frozen seeds and damage matrix

Fresh seeds: `1201..1224`.

Configuration:

```text
payload          512 bytes
channels         2
public tables    12
structural code  11 data + 1 XOR parity
corpus           2,000 candidates
near decoys      1%
locator gate     Top-20
V20              unchanged 4x128 B + 8 parity B/shard
```

For **every seed and every public table**:

1. clean control;
2. delete that table's complete x+y pair;
3. truncate one complete tail y-segment from that table.

This yields 24 clean runs + 288 whole-table deletion runs + 288 tail-truncation runs = 600 observations.

## Promotion gate frozen before results

Strict rank-1 is **not** the gate in this experiment. Structural-erasure-v2 established an exact A-visible descriptor collision in the frozen corpus; records with identical A-visible evidence cannot be ordered correctly by an A-only locator. The protocol-level contract is therefore Top-K retrieval followed by authenticated open.

Promotion gate:

- every clean run is within Top-20, forms a candidate, is directly exact, and is finally accepted;
- every one-table deletion is within Top-20, forms a candidate, has zero unresolved structural payload bits after XOR recovery, is directly exact, and is finally accepted;
- every one-tail-segment truncation satisfies the same conditions;
- no q/delta or V20 geometry changes are allowed after seeing results.

A failed gate remains a failed gate. Counterexamples are evidence and will not be removed by seed selection.

## Boundaries

Even a pass would establish only bounded synthetic single-table/single-tail-segment erasure handling for this frozen 12-table configuration. It would not establish multi-table loss, arbitrary insertion/reordering, real-publication robustness, optimal redundancy, cryptographic security, or universal locator uniqueness.
