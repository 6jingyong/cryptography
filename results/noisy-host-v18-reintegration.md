# V18 noisy-host reintegration — current protocol result

**SYNTHETIC BENCHMARK ONLY.**

## Conclusion

The first-pass V18 hypothesis is **accepted, but only in a narrow sense**.

Under the fixed smooth synthetic residual-host model declared before the run, the host-aware modulo-QIM carrier can be attached to the current lifecycle:

```text
A -> c -> B -> noisy-host b -> a
```

without moving package-specific decoder state into long-lived `A`.

The fixed 8-seed protocol gate passed:

```text
unique payload hashes = 8 / 8
exact recovery        = 8 / 8
Recall@20             = 1.0
Recall@100            = 1.0
median target rank    = 1
maximum target rank   = 2
B contains V18 state  = 8 / 8
```

This is enough to reject the stronger pessimistic hypothesis that a non-zero residual host necessarily breaks the current carrier/protocol architecture.

It is **not** enough to restore the historical V18 quantitative summary or claim a generally robust noisy-host carrier.

## Fixed calibration result

All 12 tables selected `q=4`; the `q=2` fallback was never exercised.

Every selected table had exact block recovery `1.0` after the declared publication quantization. The strictest predeclared distortion budget was NRMSE `0.0045`; observed calibration adjustment NRMSE over all tables ranged from approximately:

```text
0.0007202 .. 0.0010927
```

so every table passed its declared budget without a rescue sweep.

One Gaussian calibration had a small raw symbol error rate (`0.0001953125`), but q-ary Hamming correction restored exact block recovery.

## How much the host was changed

The embedding is not negligible relative to the existing synthetic residual.

Across the 8 full protocol seeds:

```text
median embedding-adjustment RMS / host-residual RMS ~= 0.446
maximum observed ratio                              ~= 0.485
```

The single-seed package showed a similar range table by table, about `0.429 .. 0.466`.

Interpretation:

- embedding adjustment is materially smaller than the pre-existing host residual;
- it is not so small that the carrier can be described as leaving the residual almost untouched;
- therefore the current evidence supports **feasibility**, not invisibility.

## Rate observation

The fixed 512-byte single-seed run produced a gross rate of about:

```text
0.1134 payload bit / published numeric value
```

This is intentionally recorded rather than optimized away. The experiment was designed to test protocol compatibility and noisy-host feasibility, not rate.

It therefore does **not** reproduce the old V18/V20 throughput claims.

## Locator behavior

Seven seeds ranked the real package first. Seed 101 ranked it second; the rank-1 decoy failed strict opening and the real package was accepted at rank 2.

That is acceptable under the protocol design:

```text
retrieval narrows candidates
strict verification decides validity
```

It also reinforces why locator success must not be defined as unique rank 1.

## What is now current

Current bounded result:

> A host-aware modulo-QIM carrier is viable for the tested smooth synthetic residual model under the current `A -> c -> B -> b -> a` lifecycle.

All host model, q/QIM, publication, geometry and decoder settings remain in per-package `B`. Candidate ranking continues to use `A + public package structure`, not B.

## What remains rejected / unverified

The following are **not** restored by this result:

1. the old V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` quantitative summary;
2. q=2 fallback effectiveness — it was not exercised;
3. robustness to iid, heteroscedastic, AR(1), drift or sparse-outlier residual families;
4. rate optimality;
5. universal undetectability or cryptographic security;
6. real-publication deployment.

## Next falsification target

Before building V19 around this carrier, the highest-value test is a frozen residual-model matrix. The same carrier should be tested without post-result retuning against materially different synthetic residual structures, including at least:

```text
iid Gaussian
heteroscedastic Gaussian
AR(1)-like correlated residual
batch / low-frequency drift
Gaussian + sparse outliers
```

If the current carrier fails materially outside its smooth-free-subspace host distribution, V18 should remain a model-specific mode rather than become the general noisy-host default.

Machine summary: `results/noisy-host-v18-reintegration.json`.
CI source: workflow run `41339991758`, artifact `13096549169`.
