# Active multichannel construction v7

## Question

Can the same synthetic dirty-data pool actively satisfy several coarse statistical targets at once, rather than merely exhibiting those features naturally?

This benchmark uses three candidate channels:

- slope residual relative to the observable full-pool trend;
- log-variance relative to the parent bin;
- skew shift relative to the parent bin.

All three are quantized into three coarse states. The benchmark remains synthetic-only and does not implement a complete encoding/decoding protocol.

## Important negative result: fixed 27-state control fails

A naive design would require every cell to support every combination in

`3 slope states × 3 logvar states × 3 skew states = 27 states`.

That assumption is false.

When random candidate subsets are sampled from each bin, the locally feasible `logvar × skew` combinations vary by cell. In the main seed, cells exposed between 5 and 9 of the 9 possible local combinations, with a mean of about 8.4.

Therefore an arbitrary globally fixed ternary tuple sequence can fail even when the pool is large enough for many other combinations.

This is not primarily an optimizer failure; some target combinations are simply absent or extremely rare in a given local pool.

## Adaptive feasible-state benchmark

The v7 benchmark therefore uses an adaptive state-set test:

1. candidate subsets are generated from each observable bin;
2. local feature states are defined relative to the parent-bin statistics;
3. at each step, only joint states that have at least one realizable low-cost transition are counted as feasible;
4. one feasible joint state is chosen and the beam is advanced;
5. capacity is reported as the sum of `log2(number of feasible joint states)` across cells.

This is a *capacity proxy*. It assumes that the feasible-state rule can be reproduced from the observable carrier and a compact global rule. The benchmark does not yet measure the exact description length of such a rule.

## Main-seed result

With 2,400 generated rows plus duplicate-like observations, 20 bins, and 24 selected observations per bin:

- all 20 selected joint targets were satisfied;
- effective state-set capacity proxy: about **85.6 bits / 20 cells**;
- capacity proxy: about **4.28 bits/cell**;
- mean feasible joint-state count per step: about **20.8**;
- minimum feasible state count at any step: **7**;
- mean absolute geometric-mean shift: about **0.88%**;
- slope-residual RMSE versus the observable full-pool trend: about **0.49**;
- spline roughness ratio versus the full-pool center line: about **1.32×**.

A matched random 24-point-per-bin subset had a roughness ratio around **2.71×** in the same main-seed comparison.

## Multi-seed check

The lighter cross-seed stress test used 6 independently generated pools with identical settings.

| Metric | Result |
|---|---:|
| Successful constructions | 6 / 6 |
| Median capacity proxy | **4.42 bits/cell** |
| Capacity range | **4.36–4.53 bits/cell** |
| Median feasible joint-state count | **22.4 states/step** |
| Minimum feasible-state count observed | **6–8 states** |
| Median absolute geometric-mean shift | **0.49%** |
| Random-subset geometric-mean shift median | **0.97%** |
| Median slope-residual RMSE | **0.423** |
| Random-subset slope RMSE median | **0.988** |
| Median roughness ratio | **1.26×** |
| Random-subset roughness ratio median | **2.61×** |

## Interpretation

The result supports a narrower version of the adaptive-codebook idea:

> A cell should not be assumed to expose a universal fixed state alphabet. Instead, a compact global rule can define how to measure and rank the subset of states that are actually feasible in that cell.

This preserves much of the multi-feature capacity while avoiding impossible local targets.

The main gain over v6 is conceptual: the relevant object is no longer `3^k` nominal states, but the **locally feasible joint-state set under naturalness constraints**.

## Remaining limitation

The current capacity number is still optimistic because it does not yet subtract:

- the exact description length of the adaptive state-set rule;
- error-correction redundancy;
- loss under missing rows / resampling;
- detectability by an independent classifier;
- any additional cost needed to reproduce state ordering deterministically.

Therefore **4.4 bits/cell is a construction-capacity proxy, not a robust payload rate**.

## Next experiment

The next useful test is to freeze the state-set rule globally and then measure three things jointly:

1. state-set description length / codebook overhead;
2. recovery after row loss and resampling;
3. detector AUC between adaptive constructions and matched random subsets.

That will convert the current construction capacity into a more realistic `net robust bits/cell` estimate.
