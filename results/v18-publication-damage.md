# V18 post-embedding / pre-seal publication-damage frontier

**SYNTHETIC BENCHMARK ONLY.**

## Conclusion

The current V18 carrier has a **narrow publication-damage margin**. The stronger interpretation that rebuilt V18 already has broad post-embedding publication robustness is rejected.

The frozen matrix applied unknown numeric damage after V18 embedding and A-keyed public table assignment, but **before** c was sealed. Outer integrity therefore remained valid and did not mask inner carrier failures.

The main boundary was:

```text
baseline existing publication grid       PASS 4/4
1.25x re-quantization                    FAIL: 3/4 exact
1.50x re-quantization                    FAIL: 2/4 exact
1.75x and coarser re-quantization        FAIL: 0/4 exact

additive noise sigma = 0.05 delta        PASS 4/4
additive noise sigma = 0.10 delta        PASS 4/4
additive noise sigma = 0.15 delta        FAIL: 2/4 exact
additive noise sigma >= 0.20 delta       FAIL: 0/4 exact
```

Every tested combined condition at `1.50x` or `2.00x` re-quantization failed the all-seed gate. Even the lightest combined case (`1.50x`, `0.05 delta`) recovered only 1/4 payloads exactly.

## The failure is not the locator

Across **every** condition and every seed in this matrix:

```text
target locator rank  = 1
target locator score = 1.0
Recall@100           = 1.0
```

When the condition failed, direct `B + damaged b` decoding failed first. The full protocol then correctly refused final acceptance because the reconstructed payload hash was wrong.

Therefore the measured boundary is an **inner carrier / reconstruction boundary**, not an A-layer locator failure.

This is useful because it cleanly separates two statements:

```text
public structural fingerprint remains recognizable
payload coefficients are no longer exactly recoverable
```

## Re-quantization result

The baseline `1.00x` re-quantization control was exact for all seeds, validating the harness.

At `1.25x`, seeds 301–303 remained exact but seed 304 failed. Under the predeclared rule, this condition is FAIL because the requirement was 4/4 exact, not majority success.

At `1.50x`, only seeds 301 and 303 remained exact. At `1.75x` and above, none of the four seeds recovered exactly.

Thus the coarse matrix establishes:

```text
all-seed demonstrated frontier = 1.00x
first tested failure            = 1.25x
```

It does **not** yet locate the precise threshold between those points.

## Unknown additive-noise result

Unknown zero-mean Gaussian transform-domain noise was tolerated through:

```text
sigma = 0.10 delta
```

for all four seeds.

At `0.15 delta`, only seeds 301 and 302 remained exact; seeds 303 and 304 failed. At `0.20 delta` and `0.25 delta`, all four failed.

Therefore the coarse matrix establishes:

```text
all-seed demonstrated frontier = 0.10 delta
first tested failure            = 0.15 delta
```

Again, the exact threshold inside that interval has not been measured yet.

## Combined damage

All six frozen combined conditions failed:

| re-quantization | noise sigma/delta | exact seeds |
|---:|---:|---:|
| 1.50x | 0.05 | 1 / 4 |
| 1.50x | 0.10 | 0 / 4 |
| 1.50x | 0.15 | 0 / 4 |
| 2.00x | 0.05 | 0 / 4 |
| 2.00x | 0.10 | 0 / 4 |
| 2.00x | 0.15 | 0 / 4 |

There is no basis to describe the present q=4 configuration as having a comfortable combined publication margin.

## What this changes about V18

The previous residual-model matrix showed that V18 is broad across several **sender-observed host distributions** at comparable energy. This new result identifies the complementary weakness:

> The encoder can adapt to the host it sees, but it cannot cancel unknown numeric damage introduced after embedding.

So the current supported interpretation is now:

```text
known-host distribution breadth: good within tested synthetic matrix
post-embedding publication margin: narrow
```

This is a stronger and more useful characterization than calling V18 generally "robust" or generally "fragile".

## What must be rejected

The following statement is not supported and should be rejected:

> Rebuilt V18 already provides broad publication robustness after embedding.

The current evidence instead supports only:

> Rebuilt V18 is viable for tested sender-observed residual hosts and survives modest unknown additive damage up to the tested `0.10 delta` all-seed condition, while even a `1.25x` re-quantization already causes an exact-recovery failure in one of four seeds.

## Protocol boundary: V18 versus V20

This matrix deliberately damages b **before c is sealed**.

If numeric bytes are changed after c has already been sealed, strict outer HMAC is supposed to reject the candidate. Repairing or surviving such post-seal corruption is an **outer package reliability / V20** problem.

Do not interpret this V18 result as post-seal tamper tolerance.

## Next measurement

The next defensible step is not to widen delta, add redundancy, or optimize rate. First refine the two measured transition intervals without changing the carrier:

```text
re-quantization: between 1.00x and 1.25x
additive noise:  between 0.10 delta and 0.15 delta
```

That is frontier measurement, not rescue tuning. After the frontier is measured, a separate decision can compare whether publication guard, inner-code changes, or V20-style outer reliability is the appropriate response.

Machine summary: `results/v18-publication-damage.json`.
Frozen plan: `results/v18-publication-damage-plan.md`.
CI source: workflow run `41341310689`, artifact `13097233406`.
