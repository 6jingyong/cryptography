# Capacity / expansion estimate v4

## Bottom line

The current bottleneck is not standard encryption overhead. It is the very low
payload density of a deliberately subtle statistical carrier.

Using the v3 benchmark geometry (1,224 visible rows, 20 x-bins), the present
3-state codebook carries only:

- `log2(3) = 1.585 bits/bin`
- `31.7 bits` across 20 bins
- about `0.0259 bit/visible-row`

At this stage the center-line channel is **not** counted as payload capacity,
because it has only been asked to preserve an observable smooth trend rather
than reproduce an arbitrary externally specified slope sequence.

## Coarse codebook state count

For the current 15-point tertile codebook, the simple count-vector space has
136 mathematical states in total, but many are visually/statistically extreme.
Relative to an ideal balanced tertile distribution `[1/3,1/3,1/3]`, the number
of integer count patterns whose Jensen-Shannon divergence is below several
thresholds is:

| JS threshold | Count patterns | Bits/bin |
|---:|---:|---:|
| 0.005 | 7 | 2.807 |
| 0.010 | 7 | 2.807 |
| 0.020 | 13 | 3.700 |
| 0.050 | 37 | 5.209 |

These are only combinatorial candidates. They are **not** yet measured robust
states. Actual usable capacity must be lower after feasibility, missing-data,
noise and detectability constraints.

## Payload density and carrier expansion

The table below uses 32 bytes as an illustrative average serialized size per
visible row. The exact byte expansion scales linearly with this assumption.

| Codebook alphabet | Bits/bin | Bits/row | Approx. carrier bytes / payload byte |
|---|---:|---:|---:|
| 3 states (current) | 1.585 | 0.0259 | 9,885x |
| 7 mild states | 2.807 | 0.0459 | 5,581x |
| 13 moderate states | 3.700 | 0.0605 | 4,234x |
| 37 looser states | 5.209 | 0.0851 | 3,007x |

So, under the current low-density representation, even a 100 MB payload would
require roughly 0.3–1.0 TB of serialized carrier data depending on how many of
these coarse states prove usable.

A 35 GB model would correspond to roughly 105–346 TB of carrier data in these
same illustrative scenarios.

## Pure combinatorial ceiling

After selecting 12 center points from a roughly 61-row bin, about 49 rows remain.
Choosing an arbitrary 15-row codebook subset has a raw index capacity of:

`log2(C(49,15)) ≈ 40.52 bits/bin`.

Across the v3 row density, this is about `0.662 bit/row`. With 32 serialized
bytes per row, even this *unconstrained* subset-index ceiling corresponds to
about `387x` carrier expansion.

This is a useful upper-bound sanity check, not an achievable steganographic
capacity. Most of those subsets will violate naturalness, robustness or
pre-agreed decoding constraints.

## Implication for LoRA vs full model weights

The current architecture is therefore plausible only as a low-bandwidth
research channel. It is nowhere near efficient enough for large model weights.

A useful project split is:

1. **small payload benchmark** — keys, hashes, short messages;
2. **adapter benchmark** — tens to hundreds of MB, only after payload density
   improves by orders of magnitude;
3. **full-weight benchmark** — tens of GB, treated as a long-term theoretical
   stress test rather than a near-term target.

## What must improve

The next capacity gains cannot come from merely changing 3 states to 5 or 9.
That is only a logarithmic improvement. Large gains require additional nearly
independent degrees of freedom, for example measuring how much capacity is
available simultaneously in center-line slope, within-bin distribution and
other derived statistics.

For every proposed extra channel, capacity should be reported together with:

- feasibility rate;
- perturbation robustness;
- statistical distortion;
- detector performance;
- mutual information with existing channels.

The useful quantity is therefore not raw state count but **robust effective
bits per visible row under naturalness constraints**.
