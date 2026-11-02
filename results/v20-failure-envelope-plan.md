# V20 fixed-geometry failure-envelope map — frozen plan

Scope: **synthetic/mock benchmark only**.

The preceding V20 first-pass gate succeeded. This experiment does **not** change the code, shard size, parity size, carrier, locator, payload size, or integrity semantics. Its only purpose is to locate where the already-fixed V20 geometry stops working.

## Fixed geometry

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
byte-error correction     <=4 bytes per shard (RS bound)
parity total              32 bytes
payload parity overhead   6.25%
```

## Fresh packages

```text
seeds 801..824  (24 packages)
channels = 2
```

## Frozen post-seal numeric damage grid

Paired additive noise (same per-seed/table base field scaled by alpha):

```text
sigma/delta = 0.16, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35
```

Re-quantization:

```text
factor = 1.30, 1.50, 1.75, 2.00, 2.50, 3.00
```

No extra grid points will be added after seeing results in this PR.

## Measurements

For every seed × condition:

- V18 direct exact / non-exact;
- candidate payload total byte errors before V20 repair;
- byte errors in each 128-byte shard;
- maximum byte errors in one shard;
- number of shards above the fixed RS bound (>4 byte errors);
- V20 repair attempted / successful;
- V20 final exact hash acceptance;
- rejection reason on failure;
- A-layer structural locator score sentinel.

For each condition report exact counts and distributions of the candidate byte-error geometry.

## Integrity controls

Keep explicit negative controls:

- masked repair `r` bitflip with unchanged tag -> must reject;
- serialized B bitflip with unchanged tag -> must reject.

## Interpretation rules

This is a boundary map, not a pass gate that must be rescued.

- If a condition is 24/24 V20 exact, it is inside the measured envelope.
- The first tested condition below 24/24 is a measured failure point, not permission to add parity.
- If V20 failures coincide with >4 candidate byte errors in at least one 128-byte shard while locator remains intact, that supports the expected RS-capacity explanation.
- If V20 fails while all shards remain within <=4 byte errors, inspect the implementation/integrity model before making any code-capacity claim.
- If locator structural score drops first, record an A-layer/public-structure boundary rather than calling it a V20 repair failure.
- If all frozen points remain 24/24, report that the failure envelope was not reached; do not extend the grid in the same result set.

Do not change redundancy or optimize rate in this experiment.
