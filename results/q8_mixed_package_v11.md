# V11 — mixed-package auto-encoder and detectability benchmark

## Scope

Synthetic-only benchmark. The payload is deterministic high-entropy synthetic
bytes generated inside the benchmark. No real model weights, secrets, or real
scientific evidence are encoded.

## Goal

V10 showed that a homogeneous periodic package can scale to large synthetic
payloads. V11 asks a harder question:

> Can one q=8 encoder operate on a package containing heterogeneous macro
> structures, choose the transform automatically, emit a compact manifest, and
> decode exactly from only the published numeric package + manifest?

## Fixed codec

- q = 8 / GF(8)
- Hamming `[9,7,3]_8`
- `6 payload + 1 shaping + 2 parity`
- 18 payload bits per q=8 codeword
- 24 published points per local block

The carrier is always constructed in the free subspace orthogonal to the
selected protected macro model.

## Six macro families

The benchmark package contains:

1. affine
2. single-frequency periodic
3. periodic + second harmonic
4. saturation
5. Gaussian peak in log-domain
6. strict mirror-symmetric even curve

The encoder evaluates candidate modes and selects the highest-capacity mode that
passes the macro-fit threshold.

### Automatic selections

| synthetic family | selected mode | codewords / 24-point block | nominal payload density |
|---|---|---:|---:|
| affine | affine | 2 | 1.50 bit/value |
| periodic | periodic1 | 2 | 1.50 |
| harmonic | periodic2 | 2 | 1.50 |
| saturation | saturation | 2 | 1.50 |
| Gaussian | gaussian_log | 2 | 1.50 |
| symmetric | symmetric_even | 1 | 0.75 |

The symmetric family has lower capacity because strict mirror symmetry removes
roughly half of the raw degrees of freedom.

## Self-contained round-trip experiment

Configuration:

- payload: 262,144 bytes
- y-series per table: 16
- six heterogeneous tables
- publication precision: 3 decimal places
- decoder input: only `published_package_v11.npz + manifest_v11.json`

Result:

- exact SHA-256 recovery: **yes**
- manifest: **2,781 bytes**
- manifest overhead: **1.061% of payload size**
- total published rows: **101,976**
- gross rate: **20.565 bit/row**
- net rate after manifest: **20.347 bit/row**
- gross rate: **1.2853 bit/numeric value**
- net rate after manifest: **1.2717 bit/numeric value**
- mean raw q=8 symbol error before ECC: **0%** in this three-decimal benchmark

### Structural distortion

| family | mean NRMSE | roughness ratio | macro-parameter drift |
|---|---:|---:|---:|
| affine | 0.111% | n/a (baseline second difference ~0) | 1.89e-6 |
| periodic | 0.117% | 1.00007x | 2.18e-6 |
| harmonic | 0.120% | 1.00005x | 3.05e-6 |
| saturation | 0.0718% | 1.0056x | 3.06e-6 |
| Gaussian-log | 0.541% | 1.213x | 4.55e-6 |
| symmetric | 0.139% | 1.0157x | 2.30e-5 |

Gaussian-log is currently the most distortion-expensive mode. It remains exact
to decode but is the first candidate for future shape-aware tuning.

## Detectability benchmark

Controls are matched continuous residuals with the same estimated coefficient
mean/covariance as encoded blocks. The benchmark uses 8,400 samples across all
six macro families.

### Generic detector

The generic detector sees only ten residual-shape features and does not know the
q=8 lattice or Hamming structure.

| detector | ROC AUC |
|---|---:|
| logistic regression | 0.522 |
| random forest | 0.703 |
| histogram gradient boosting | 0.680 |

Leave-one-family-out logistic AUC averages **0.534**.

Interpretation: low-order residual statistics alone are weak, but nonlinear
models still find a moderate footprint. This is not evidence of invisibility.

### Oracle / codebook-aware detector

The oracle detector additionally receives q=8 lattice-distance and Hamming
codeword-consistency features.

- logistic AUC: **1.000**
- random forest AUC: **1.000**
- HistGB AUC: **1.000**
- leave-one-family-out logistic mean: **1.000**

This is the most important negative V11 result:

> If the transform / q=8 lattice / Hamming structure is known, the current
> carrier is trivially identifiable.

Therefore future work must not interpret generic-detector failure as security.

## Protocol correction found during V11

The first mixed-package attempt allowed saturation channels to use different
`tau` values while writing only one table-level `tau` into the manifest. That
broke the self-contained protocol. V11 now requires macro parameters declared
at table level to actually be shared by all series in that table (or else they
must be explicitly represented per series).

Likewise, log-domain coefficient spacing must be chosen according to the
published numeric precision rather than copied blindly from identity-domain
modes.

## Current conclusion

V11 turns the V10 special case into a more general algorithmic object:

`macro-family detection -> protected transform -> free subspace -> q=8 shaping -> publication -> manifest-only decode`

The next bottleneck is no longer capacity or basic self-contained decoding. It
is **detectability under a knowledgeable adversary** and, secondarily, reducing
the Gaussian-log distortion footprint.

## Boundaries

- synthetic benchmark only
- no real secret/model-weight exfiltration workflow
- no fabricated real scientific evidence
- detector AUC near 0.5 is never treated as proof of information-theoretic invisibility
