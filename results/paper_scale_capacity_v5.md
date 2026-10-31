# Paper-scale capacity stress test v5

## Main conclusion

Raw row count is not the correct capacity variable for the current construction.

The current codebook channel creates state at the level of an **independent statistical cell** (for example, one x-bin / condition block with its own local distribution). Adding more replicate rows to an existing cell improves statistical stability but does not create a proportional number of new discrete states.

Therefore the relevant hierarchy is:

`raw rows -> independent statistical cells -> robust states per cell -> effective payload`

## Histogram-state count

For the current 15-point / 3-tertile codebook, enumerate all integer histograms `(a,b,c)` with `a+b+c=15` and retain only states close to the balanced distribution `(5,5,5)`.

| Naturalness bound | Candidate states | Theoretical bits/cell |
|---|---:|---:|
| JS <= 0.005 | 7 | 2.807 |
| JS <= 0.010 | 10 | 3.322 |
| JS <= 0.020 | 19 | 4.248 |
| JS <= 0.050 | 46 | 5.524 |

These are combinatorial candidate counts, not yet robust payload rates. States that are numerically close may be hard to distinguish after missing observations or resampling.

## Robustness of the current 3-state codebook

The existing patterns are `[6,5,4]`, `[5,5,5]`, and `[4,5,6]`. A simple nearest-proportion decoder was tested after independently dropping codebook observations.

| Random codebook-row loss | State recovery |
|---|---:|
| 0% | 100% |
| 1% | ~97% |
| 5% | ~86% |
| 10% | ~77% |
| 20% | ~65% |

So the nominal `log2(3)=1.585 bits/cell` is not equal to robust effective capacity. Error correction or wider state separation would reduce usable payload further.

## Illustrative paper-scale scenarios

The following scenarios are deliberately synthetic capacity stress tests, not empirical claims about all scientific papers.

| Scenario | Raw rows | Independent statistical cells |
|---|---:|---:|
| ordinary | 10,000 | 300 |
| data-rich | 100,000 | 1,000 |
| heavy processed-data | 1,000,000 | 3,000 |

Using only the codebook-distribution channel:

| Scenario | 7 states/cell | 19 states/cell | 46 states/cell |
|---|---:|---:|---:|
| ordinary | ~105 B/paper | ~159 B/paper | ~207 B/paper |
| data-rich | ~351 B/paper | ~531 B/paper | ~690 B/paper |
| heavy processed-data | ~1.05 KB/paper | ~1.59 KB/paper | ~2.07 KB/paper |

The corresponding nominal bits/row actually **decrease** in the larger scenarios if row count grows faster than the number of independent cells.

For the `JS <= 0.05` case:

- ordinary: ~0.166 bits/row
- data-rich: ~0.055 bits/row
- heavy processed-data: ~0.0166 bits/row

This is the opposite of a naive `more rows = proportionally more payload` model.

## Pure combinatorial ceiling

With roughly 49 non-center observations left in a bin and 15 selected for a codebook role, the raw subset-choice count is approximately:

`log2(C(49,15)) ~= 40.5 bits/cell`.

That is a mathematical ceiling before naturalness, decodability, robustness, and detector constraints.

Even if every independent cell somehow achieved this impossible-to-realize ceiling, the illustrative scenarios would carry only roughly:

- 300 cells: ~1.5 KB
- 1,000 cells: ~5.1 KB
- 3,000 cells: ~15.2 KB

Therefore a single paper-like collection of ordinary chart/source-data structures cannot approach LoRA-sized payloads using this one distribution channel.

## Consequence for the research direction

The key metric should be changed from `bits/row` alone to two separate quantities:

1. **robust bits per independent statistical cell**;
2. **number of plausibly independent cells per carrier collection**.

A large raw dataset helps only if it introduces new independently controllable structure. Replicates that merely sharpen the same mean/distribution do not create linear capacity.

The next useful experiment is therefore to add an independently controlled slope channel and measure whether its robust information is approximately additive with the distribution channel, rather than simply increasing raw rows.
