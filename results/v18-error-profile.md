# V18 publication-damage error profile

Scope: **synthetic/mock benchmark only**.

This result profiles residual payload errors after the existing V18 per-codeword Hamming layer. No V18 carrier parameter changed.

Source CI:

```text
workflow run: 41373895320
artifact:     13110134062
artifact sha: 953680ef469764fb50ee5ea81cf2b97e0a182a2d5eb1f6e0a6b877f01d6b15a3
```

## Main result

The transition-region failures are **sparse**, not package-wide collapse.

Across all 37 failed paired-additive-noise packages (`0.12–0.16 delta`):

```text
payload bit errors:        median 2, p90 4, max 4
bad tables:                median 1, p90 2, max 3
bad corrected codewords:   median 1, p90 2, max 3
raw payload-symbol errors: median 18, p90 26, max 29
post-Hamming symbol errors: median 2, p90 3, max 3
```

Every failed noise package had at most four bad corrected codewords in this test.

Across all 23 failed re-quantized packages:

```text
payload bit errors:        median 2, p90 3, max 5
bad tables:                median 1, p90 1, max 2
bad corrected codewords:   median 1, p90 1, max 2
raw payload-symbol errors: median 15, p90 17.8, max 22
post-Hamming symbol errors: median 1, p90 2, max 3
```

About 95.7% of the failed re-quantized packages had all final payload bit errors concentrated in one table.

## Condition-level examples

Paired noise:

```text
0.12 delta: 23/24 exact; one failure with 3 bit errors across 2 tables / 2 codewords
0.14 delta: 17/24 exact; failed median 2 bit errors, 1 table, 1 bad codeword
0.15 delta: 11/24 exact; failed median 2 bit errors, 1 table, 1 bad codeword
0.16 delta: 10/24 exact; failed median 2 bit errors, 2 tables, 2 bad codewords; max 4 bits / 3 tables / 3 codewords
```

Re-quantization remains non-monotonic in package-exact rate, but its failure geometry is also sparse:

```text
1.06x: 20/24 exact; failed median 1.5 bits, always 1 table / 1 bad codeword
1.10x: 21/24 exact; failed median 1 bit, always 1 table / 1 bad codeword
1.20x: 17/24 exact; failed median 2 bits, always 1 table / 1 bad codeword
1.22x: 21/24 exact; failed median 2 bits, always 1 table / 1 bad codeword
1.30x: 18/24 exact; failed median 2 bits; max 5 bits / 2 tables / 2 codewords
```

The A-layer structural score remained `1.0` for every tested damaged package.

## Interpretation

The existing inner Hamming code is already removing most raw payload-symbol damage. The remaining failure is typically one or two corrected codewords that still carry one to a few wrong payload bits.

Therefore the evidence supports a **bounded V20 outer-reliability prototype**. The motivation is not to hide a broken V18 carrier: it is to test whether a small outer code can cheaply absorb the sparse residual errors that remain after V18's existing inner code.

This does **not** establish any particular V20 geometry. It also does not prove that real post-seal corruption has exactly the same error distribution as this pre-seal diagnostic. A V20 prototype must be evaluated under an explicit post-seal lifecycle with strict final integrity verification.

Broad V18 publication robustness remains rejected.
