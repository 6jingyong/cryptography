# V15/V16 — reorder, erasure and locator scaling

## Conclusion

The second codebook should be modeled as a **labeled structural fingerprint**,
not as a fragile ordered sequence and not as an unlabeled bag of symbols.

Each fingerprint position has a stable public/canonicalizable label
(e.g. table role, figure role, axis family or other coarse structural identity),
and the pre-shared codebook supplies the expected coarse value at that label.

Therefore:

- reordering can be normalized away;
- missing tables/figures become erasures;
- unreadable structure becomes substitutions;
- strict verification remains separate from retrieval.

All experiments here use synthetic descriptors only.

## V15 — reorder is a protocol problem, not a capacity problem

Stress case:

- corpus: 10,000
- fingerprint length: 16
- value alphabet: 12
- erasure: 25%
- substitution: 10%
- random reorder: enabled
- hard near-decoys: 1%, sharing 50% of target structure

### Naive ordered matching

- median rank: **4066**
- P90 rank: **8368**
- P(target in Top-100): **6.0%**

### Canonical labeled matching

- median rank: **1**
- P90 rank: **1**
- P(target in Top-100): **100.0%**

So figure/table reorder should not consume locator redundancy if labels can be
reconstructed from public structure.

## V16 — scaling to 1M candidates

Common stress model:

- 10% substitution on retained target positions;
- 1% hard near-decoys;
- each near-decoy shares 50% of target labeled values;
- canonical labeled matching;
- 30 independent seeds for the 1M-candidate tests.

### Joint-structure-like alphabet: A=12

#### 16 labeled positions, 25% erasure

- Top-20: **96.7%**
- Top-100: **100.0%**
- median rank: **1.0**
- P90 rank: **4.0**
- mean retained positions: **12.2**

Nominal value entropy before erasure:

`16 * log2(12) = 57.4 bit`

#### 24 labeled positions, 50% erasure

- Top-20: **90.0%**
- Top-100: **100.0%**
- median rank: **2.0**
- P90 rank: **10.3**

#### 32 labeled positions, 50% erasure

- Top-20: **100.0%**
- Top-100: **100.0%**
- median rank: **1.0**
- P90 rank: **3.3**

### q-only-like alphabet: A=3

Even at length 32:

#### 25% erasure

- Top-20: **86.7%**
- Top-100: **96.7%**
- P90 rank: **23.4**

#### 50% erasure

- Top-20: **46.7%**
- Top-100: **66.7%**
- P90 rank: **502.3**

This confirms that q should be only one component of the locator value.

## Practical reading of the current benchmark

For the current synthetic model:

- ~16 labeled joint-structure positions are already strong for 1M candidates
  when erasure is around 25%;
- ~24 positions preserve Top-100 retrieval under 50% erasure in this 30-seed run;
- ~32 positions are much more comfortable if 50% erasure must still keep the
  target inside a small Top-K.

These are empirical stress-test results, not cryptographic guarantees.

The stable labels used for canonicalization are part of the public package
structure; only the expected coarse structural values belong to the locator
codebook.

## Next step

The locator architecture is now sufficiently specified to move attention back
to Codebook A:

1. deterministic publication transforms;
2. row/column reorder;
3. unit scaling `y -> a*y+b`;
4. decimal/significant-digit changes;
5. table split/merge;
6. self-contained decode after those transforms.
