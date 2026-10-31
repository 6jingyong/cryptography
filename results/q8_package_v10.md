# V10 — q=8 protected-subspace package benchmark

## Scope

This milestone is **synthetic-only**.

The payload is deterministic high-entropy synthetic bytes. The 23.4 MB target is
used as a LoRA-sized engineering reference; no real model weights are encoded.

## Architecture

Current fixed alphabet:

- `q = 8`
- field: `GF(8)`
- outer code: `[9,7,3]_8` Hamming
- block layout: `6 payload + 1 shaping + 2 parity`
- payload per block: `18 bit`

Each local curve block uses 14 published y-values:

- 5 protected macro dimensions:
  `1, sin(wx), cos(wx), sin(2wx), cos(2wx)`
- 9 orthogonal free dimensions
- exactly one q=8 Hamming codeword

Therefore the nominal carrier density is:

`18 / 14 = 1.285714 bit / published numeric value`

The encoder uses the free shaping symbol to select the lowest-distortion legal
codeword. The decoder recomputes the protected/free basis from x and directly
projects published y into the free basis; it does not need the original
unencoded y.

## Full package experiment

Configuration:

- payload: **23.4 MB**
- tables: **100**
- y-series per table: **64**
- total q=8 Hamming blocks: **10,400,000**
- total published rows across tables: **2,275,000**
- total published numeric y-values: **145,600,000**

Round-trip result:

- exact payload recovery: **True**
- input SHA-256: `4b409ea49d476a11df7acc5a203ef3f322fb97a068f9bb729831e24e28bf833a`
- output SHA-256: `4b409ea49d476a11df7acc5a203ef3f322fb97a068f9bb729831e24e28bf833a`

Capacity:

- effective payload: **82.286 bit / published row**
- effective payload: **1.285714 bit / numeric value**

Publication / structural metrics:

- raw q=8 symbol error rate before ECC: **0.018987%**
- mean table NRMSE: **0.3334%**
- mean table roughness ratio: **1.0419x**
- mean cross-channel correlation-matrix MAE: **0.00000718**
- mean protected macro coefficient relative error: **1.624e-06**
- benchmark runtime in the current Python/Numpy environment: **34.25 s**

## What changed from v9

v9 treated an independent statistical cell as the main capacity unit and used a
q=5 mapping over `center + logvar + skew`.

V10 changes the mathematical object:

`y = protected_macro(x) + free_subspace(x)`

The compact codebook defines how x determines the protected basis and therefore
the orthogonal free carrier coordinates.

This removes the earlier shared-parent statistical reference from the core
q=8 prototype and raises the experimentally demonstrated density from roughly
`0.073 bit/raw-row` in the old 16-row statistical-cell construction to roughly
`1.286 bit/published numeric value` in the current local protected-subspace
carrier.

For multivariate tables, capacity scales approximately with the number of
independent y-series sharing the x axis. The full 64-channel package benchmark
reaches about **82.3 bit/published row**.

## Important implementation result

For the local periodic block, normalized phase positions are the same across
period values. Therefore the q=8 shaping choice can be precomputed for all

`8^6 = 262,144`

possible six-symbol payload tuples.

The optimized encoder uses a deterministic lookup table for the best legal
codeword rather than enumerating eight shaping choices for every block.

The decoder also does not need a per-block macro least-squares fit because

`B.T @ U ~= 0`.

It can recover free coefficients directly with:

`c_hat = y_published @ U`

while fitted macro parameters are evaluated only as a distortion metric.

## Current conclusion

The q=8 codec is no longer the main bottleneck.

The experimentally relevant scaling variable is now:

`bits / published row`

for a package containing many tables and many y-series.

The full 23.4 MB synthetic package result demonstrates that package-level
multiplexing can cross the LoRA-sized capacity scale in the synthetic benchmark
without requiring a single implausibly large x-y curve.

## Boundaries

This repository continues to study synthetic statistical carriers only.

- no real secret/model-weight exfiltration workflow;
- no fabrication of real scientific evidence;
- no claim that low detector performance proves invisibility;
- any paper-style benchmark must be visibly labeled synthetic/simulated/mock.
