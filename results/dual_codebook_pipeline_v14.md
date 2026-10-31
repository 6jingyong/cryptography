# V14 — dual-codebook retrieval + verification integration

## Conclusion

The current synthetic architecture is better described as **two codebooks plus a
strict verifier**, not as a single low-detectability carrier.

1. **Interpretation codebook**: defines how a published numeric package is
   interpreted — macro family, transform, protected subspace, q, q-ary Hamming,
   shaping and publication precision.
2. **Locator codebook**: a compact pre-shared structural fingerprint used only
   to rank likely packages.
3. **Strict verification**: the authoritative accept/reject step. False
   positives from retrieval are allowed.

The locator does not need unique identification.

## Actual target package

One real synthetic adaptive-q package was generated and decoded from only its
published NPZ + manifest:

- payload: **131,072 bytes**
- tables: **12**
- q schedule: `[8, 16, 32, 8, 16, 32, 8, 16, 32, 8, 16, 32]`
- family schedule:
  `['affine', 'affine', 'affine', 'periodic', 'periodic', 'periodic', 'saturation', 'saturation', 'saturation', 'gaussian', 'gaussian', 'gaussian']`
- decoder SHA-256 match: **True**

## 10,000-candidate retrieval benchmark

Conditions:

- one actual target pattern;
- 10,000 candidate packages;
- 200 independently generated corpora;
- 20% fingerprint extraction corruption on the target;
- 1% hard near-decoys;
- each near-decoy copies 50% of target fingerprint positions.

### q-only locator

- Top-1 probability: **11.5%**
- Top-5 probability: **32.5%**
- Top-10 probability: **46.0%**
- Top-20 probability: **58.0%**
- Top-50 probability: **71.5%**
- Top-100 probability: **83.5%**
- median rank: **13.0**
- P90 rank: **221.1**
- P99 rank: **1675.8**
- mean verification attempts: **99.765**

### joint `(family, q)` locator

- Top-1 probability: **70.0%**
- Top-5 probability: **85.0%**
- Top-10 probability: **91.0%**
- Top-20 probability: **93.5%**
- Top-50 probability: **98.5%**
- Top-100 probability: **98.5%**
- median rank: **1.0**
- P90 rank: **10.0**
- P99 rank: **101.2**
- mean verification attempts: **5.585**

The joint structural fingerprint is therefore much more useful than q alone.

## Representative strict verification

In the representative corpus:

- target rank: **1**
- verification attempts: **1**
- accepted candidate is true target: **True**
- actual published-package decoder SHA match: **True**

## Revised interpretation of detectability

A repeatable structural pattern is not automatically a protocol failure.

Under the current model, recognizability can serve the locator codebook:

`structural fingerprint -> Top-K candidates -> decode/verify -> accept or reject`

The useful retrieval objective is therefore high target recall with low expected
verification cost, not necessarily a detector AUC near 0.5.

Detectability remains measurable, but it is no longer the single optimization
target.

## Scope

All packages, payloads and corpus entries in this benchmark are synthetic/mock.
The repository does not implement real secret/model-weight transfer or
fabricated real scientific evidence.
