# V18 publication-damage refinement — fresh-seed result

**SYNTHETIC BENCHMARK ONLY.**

## Conclusion

The refinement validates the earlier qualitative weakness but **rejects the idea that one scalar monotonic re-quantization threshold has been measured**.

Fresh seeds `401–408` reproduce both controls:

```text
1.00x re-quantization = 8 / 8 exact
0.10 delta noise      = 8 / 8 exact
```

However, the refined grids show different structures for the two damage families.

## Re-quantization is non-monotonic

| factor | exact |
|---:|---:|
| 1.00x | 8 / 8 |
| 1.05x | 7 / 8 |
| 1.10x | 8 / 8 |
| 1.15x | 7 / 8 |
| 1.20x | 7 / 8 |
| 1.25x | 6 / 8 |

The key observation is not merely that 1.25x performs worse than baseline. It is:

```text
1.05x FAILS the 8/8 gate
1.10x PASSES the 8/8 gate
```

Therefore success is not monotonic in the tested re-quantization factor.

The most plausible mechanism is discrete alignment between:

```text
post-embedding quantization grid
QIM coset / coefficient lattice
basis reconstruction + rounding
```

A coarser grid is not guaranteed to be strictly worse than every finer grid if one factor happens to align more favorably with encoded coefficient locations.

Consequently, these statements are **not** justified:

```text
"the threshold is between 1.10x and 1.15x"
"1.10x is universally safe"
"all factors below the largest passing factor are safe"
```

What is justified is only the measured grid map above.

## Additive noise: 0.11 delta passes 8/8, but this is not a deterministic threshold

| sigma / delta | exact |
|---:|---:|
| 0.10 | 8 / 8 |
| 0.11 | 8 / 8 |
| 0.12 | 7 / 8 |
| 0.13 | 3 / 8 |
| 0.14 | 6 / 8 |
| 0.15 | 6 / 8 |

The all-seed PASS/FAIL gate is monotonic on this particular grid:

```text
PASS, PASS, FAIL, FAIL, FAIL, FAIL
```

but the exact pass counts are not monotonic.

This is expected to some degree because each alpha condition uses a different deterministic random-noise realization. `0.14 delta` is therefore not simply the `0.13 delta` perturbation scaled upward; it is another noise sample with a different direction.

Thus the result supports:

> `0.10 delta` reproduces on eight fresh seeds, and `0.11 delta` also passes 8/8 in this experiment.

It does **not** support:

> The universal deterministic failure threshold lies between `0.11` and `0.12 delta`.

## Locator remains irrelevant to these failures

Every refined condition retained:

```text
Recall@100 = 1.0
```

Whenever exact recovery failed, direct inner decode failed as well. This continues to support the separation established by the coarse experiment:

```text
A-layer public structural retrieval remains intact
inner payload reconstruction is the limiting layer
```

## Methodological correction

The next experiment should not add still finer points to a supposed scalar threshold.

For additive noise, estimate **success probability** under controlled sampling. A stronger design should use:

```text
many fresh payload/host seeds
paired base noise fields scaled across alpha values
or multiple independent noise replicates per alpha
confidence intervals for package-exact recovery probability
```

For re-quantization, use a dense factor map and treat factor as a **grid-alignment parameter**, not a monotonic damage axis. The target is to identify safe/unsafe bands or periodic structure, not one threshold.

This is a methodological consequence of the machine result, not a change made to rescue V18.

## Current V18 interpretation

The combined evidence now says:

```text
known sender-observed host distributions: broad within tested matrix
unknown additive post-embedding noise: modest tolerance, stochastic
post-embedding re-quantization: fragile and non-monotonic in grid factor
locator under these numeric-damage tests: stable
```

Broad publication robustness remains rejected.

Machine summary: `results/v18-publication-frontier-refine.json`.
Frozen plan: `results/v18-publication-frontier-refine-plan.md`.
CI source: workflow run `41341873027`, artifact `13097383059`.
