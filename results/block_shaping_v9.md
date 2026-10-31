# q=5 block shaping v9

## Question

Can the current q=5 statistical-state channel benefit from two mature coding ideas without changing the statistical carrier itself?

- **wet-paper-style feasibility**: a cell/symbol pair may be unavailable rather than forcibly realized;
- **STC-like shaping**: a Hamming information dimension may be left free so the encoder can choose the lowest-cost legal codeword for a 6-cell block.

The benchmark remains synthetic-only. It is not a complete communication protocol and it still uses parent-bin statistics as shared reference during decoding.

## Fixed structure

The statistical carrier remains:

- center state;
- log-variance state;
- skew state.

These form 27 joint ternary states. A global, fixed q=5 coloring is used:

`color = (4*center + 4*logvar + 3*skew + 1) mod 5`.

No per-cell alphabet is stored.

The outer error-correcting code is the q=5 Hamming code `[6,4,3]_5`.

Three constructions are compared:

1. **4P0S** — four q=5 payload symbols, no shaping freedom;
2. **3P1S_fixed** — three payload symbols, fourth Hamming information symbol fixed to zero;
3. **3P1S_shaped** — three payload symbols, fourth information symbol is free and the encoder tries all five legal codewords, choosing the minimum-cost one.

The third construction preserves the same Hamming single-symbol correction ability as the second; it uses the spare information dimension only for shaping.

## Local + curve cost

For each cell and q=5 symbol, candidate subsets are assigned a local statistical distortion cost. A 6-cell dynamic program then adds a pairwise center-line penalty:

`total cost = local statistical cost + pairwise curve cost`.

Thus shaping is not a per-cell greedy choice: the whole block is optimized jointly.

## Main result

Six disjoint synthetic test seeds were used.

| construction | payload rate | mean block cost | roughness ratio | 5% loss block recovery |
|---|---:|---:|---:|---:|
| 4P0S | **1.548 bit/cell** | 0.341 | 1.040x | 70.7% |
| 3P1S_fixed | 1.161 bit/cell | 0.428 | 1.058x | 64.0% |
| 3P1S_shaped | 1.161 bit/cell | **0.237** | **1.022x** | 70.4% |

The clean comparison is `3P1S_fixed` vs `3P1S_shaped`: same payload rate and same outer Hamming code, but allowing one shaping degree of freedom reduces mean block cost by about **45%** and improves curve roughness.

The shaped version does **not** materially outperform `4P0S` on 5% row-loss recovery. That is expected: shaping solves feasibility/distortion; Hamming solves post-construction symbol errors.

## Wet-paper-style hard feasibility

A second test marks every candidate whose local cost exceeds a threshold as unavailable.

| local cost cap | 4P0S feasible | 3P1S shaped feasible |
|---:|---:|---:|
| 0.05 | 4.9% | **14.4%** |
| 0.08 | 14.5% | **26.7%** |
| 0.12 | 26.5% | **43.7%** |
| 0.20 | 66.9% | **78.1%** |
| 0.30 | 81.5% | **87.6%** |

This is the strongest v9 result.

When difficult/high-cost cell-symbol choices are treated as genuinely unavailable, one shaping dimension gives the encoder alternate legal Hamming codewords and rescues many blocks that the unique-codeword construction cannot realize.

## Interpretation

The useful abstraction is now:

`payload constraint + ECC constraint + shaping freedom + cell/symbol cost`.

For cell `j` and q=5 symbol `a`, let the best realizable statistical candidate have cost `rho[j,a]`; unavailable choices have infinite cost.

For a block, the encoder solves:

`min sum_j rho[j,z_j] + curve_cost(z_1,...,z_6)`

subject to `z` belonging to the legal Hamming/coset family for the payload.

This borrows the core ideas of wet-paper coding and distortion-minimizing syndrome coding without importing an image-specific implementation.

## Important limitations

1. **Rate trade-off**: one shaping dimension changes the fixed payload rate from 1.548 to 1.161 bit/cell.
2. **Shaping is not ECC**: it reduces construction cost and increases feasibility but does not by itself improve symbol stability after row deletion.
3. **Shared-reference assumption remains**: center/logvar/skew states are still defined relative to parent-bin statistics. A self-contained decoder remains unresolved.
4. **Adaptive-rate mode is not yet protocol-complete**: switching individual blocks between 4P0S and 3P1S would require a reproducible mode schedule or explicit mode metadata.
5. Results are synthetic and should be read as mechanism tests, not real-world invisibility/security claims.

## Next step

The next useful experiment is not another statistical feature. It is to test whether a **fixed-rate 3P1S trellis** remains advantageous when:

- boundary-depth robustness is included directly in `rho[j,a]`;
- 5% and 10% row loss are evaluated after construction;
- block interleaving is added;
- self-contained state definitions are tested against the current shared-reference version.

Only after that should adaptive-rate shaping be considered.
