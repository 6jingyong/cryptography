# Physical structural damage v1 — frozen plan

Status before results: **FROZEN / NOT YET INTERPRETED**

Scope: synthetic/mock benchmark only.

## Question

The current descriptor-level structural-v4 benchmark does not establish how the
actual public NPZ package, parser, deterministic V18 decoder, and bounded V20
outer-reliability layer behave under physical structural damage.

This experiment asks only: **where does each frozen physical NPZ damage first
break the current end-to-end lifecycle?**

The layer order is:

1. A/public locator,
2. NPZ / b parser and deterministic V18 decode,
3. candidate payload production,
4. bounded V20 repair,
5. authenticated final payload hash.

## Frozen implementation

- current engine: `src/noisy_host_package_v18_deterministic.py`
- V20 wrapper: `protocol/real-package-v20.py`
- payload: 512 bytes
- channels: 2
- seeds: 1001..1024 inclusive
- locator corpus: 2,000 records, 1% descriptor near-decoys
- A unchanged
- q/delta/calibration unchanged
- V20 geometry unchanged:
  - 4 × 128-byte data shards
  - 8 parity bytes per shard
  - <=4 byte errors/shard nominal RS correction capacity

The target table is chosen by a rule fixed before results:
minimum `payload_bit_offset`, then minimum public `table_id`.

## Frozen damage conditions

1. `clean`
   - no damage; execution control only.

2. `drop_logical_first_table`
   - remove both `table_<id>_x` and `table_<id>_y` from the actual NPZ.

3. `truncate_tail_segment_logical_first_table`
   - keep x and the public first block unchanged;
   - remove exactly one final `points_per_block` segment from that table's y
     array;
   - table count and x-grid remain unchanged.

4. `localized_burst_4_segments_sigma4delta`
   - preserve NPZ keys and shapes;
   - leave public segment 0 untouched;
   - apply deterministic Gaussian disturbance in the table's transform domain
     over four contiguous interior segments;
   - sigma = 4 × the table's declared delta.

5. `localized_burst_6_segments_sigma4delta`
   - identical to condition 4, but six contiguous interior segments.

The 4/6-segment pair is not a tuned performance sweep. It is a small,
predeclared check of whether a damage that still yields a candidate payload
continues to follow the already-observed V20 shard-capacity mechanism.

## Decision rules

For each run record:

- locator score and corpus rank;
- whether locator parsing itself raises;
- whether deterministic V18 produces a candidate payload;
- candidate payload byte errors and per-shard byte-error counts when available;
- V20 direct success, repair attempt/success, and final reason;
- first observed failure layer.

Interpretation:

- locator exception or degraded locator is an A/public-structure result;
- locator survives but no candidate payload is produced is a b/parser/decoder
  structural result; V20 is not blamed for a payload it never receives;
- only when a candidate payload exists is RS-capacity comparison applicable;
- B/r authentication failures are integrity results, not repair opportunities.

## Anti-tuning rule

Damaged outcomes are **not** CI pass/fail criteria.

The workflow passes only if all clean controls execute with:
- locator score 1.0,
- target rank 1,
- exact direct decode,
- V20 acceptance without repair.

If any damaged condition contradicts the hypotheses above, preserve the result.
Do not change A, q, delta, target-table selection, burst amplitude/width, or V20
RS geometry inside this experiment to make the result look better.
