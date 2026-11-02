---
name: synthetic-paper-benchmark
description: Run and render clearly labeled synthetic/mock structured-numeric carrier benchmarks using the corrected A -> c -> B/b/r -> a protocol. Keep reproducible machine results authoritative and paper presentation downstream.
---

# Synthetic Paper Benchmark

## Scope

Use this skill only for synthetic/mock research artifacts.

Every scientific-looking artifact must remain visibly labeled, for example:

```text
SYNTHETIC BENCHMARK
SIMULATED DATA
MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS
```

Do not use this workflow to hide real confidential material in real publications, fabricate real evidence, impersonate real institutions/authors, or claim synthetic results came from real experiments.

# Project objective

Treat the repository as one system, not a collection of carrier micro-benchmarks.

```text
synthetic payload a
-> numeric carrier b
-> per-package reconstruction/reliability manifest B
-> optional authenticated repair data r
-> candidate c mixed among synthetic background d
-> pre-shared A locates / bootstraps c
-> authenticated open
-> B decodes b; optional V20 repair
-> exact a
-> same current machine package/results feed the mock-paper bundle
```

```text
A = long-lived root locator / canonicalization / bootstrap protocol
B = per-package reconstruction + reliability manifest
```

Package-specific q, delta, transform, geometry, ECC, payload length, **basis version**, shard size, parity count, etc. belong in B, not A.

# Priority

```text
1. A can find/bootstrap c
2. c can be opened/authenticated
3. B completely explains b/r
4. exact a is recovered
5. machine evidence is reproducible under its declared environment
6. the paper layer consumes that same evidence without hand substitution
7. figures/data/claims remain traceable
8. only then optimize capacity/rate/overhead
```

Do not trade locator recall, reconstruction metadata, strict verification, reproducibility, or traceability for a prettier bit/value number.

# Current V18 engine

Current engine:

```text
src/noisy_host_package_v18_deterministic.py
basis_version = deterministic-dct-mgs-v1
```

Legacy baseline:

```text
src/noisy_host_package_v18.py
```

The current deterministic basis uses fixed-order DCT-II candidates plus two-pass modified Gram-Schmidt and fixed scalar reductions. Basis version is B state. A decoder must reject a mismatched declared basis version.

Frozen promotion evidence:

```text
Gate A: current E2E/paper viability PASS
Gate B: two independent CI runners, exact semantic equality, mismatch_count=0
Gate C: bounded V18/V20 evidence PASS without q/delta/RS retuning
```

Evidence:

```text
results/deterministic-basis-v1-plan.md
results/deterministic-basis-v1.json
results/deterministic-basis-v1.md
```

This establishes exact semantic reproducibility for the frozen configuration across the declared independent GitHub Actions environment. Do not generalize it into universal every-platform bit identity.

# V18 bounded interpretation

V18 remains a bounded host-aware modulo-QIM carrier for explicit sender-observed synthetic residual hosts.

Broad publication robustness is explicitly rejected. Re-quantization remains alignment-dependent/non-monotonic, and q=2 fallback remains unexercised.

# V20 logical outer reliability

Current fixed geometry:

```text
512-byte payload
4 x 128-byte data shards
8 parity bytes / shard
<=4 byte errors correctable / shard
32 parity bytes total = 6.25% payload parity overhead
```

Final acceptance requires exact authenticated payload SHA-256. In the tested stronger grid, V20 failure aligns with at least one shard exceeding the declared four-byte correction capacity.

# V19 selector

V19 remains sender-side mode-selection policy. It is not the immediate priority while one integrated current carrier mode is primary.

# Current end-to-end test

Use:

```text
tools/current_end_to_end.py
```

Preferred engine argument:

```text
--engine src/noisy_host_package_v18_deterministic.py
```

Frozen seeds `901..908` pass:

```text
8 / 8 unique payload hashes
8 / 8 exact recovery
Recall@20 = 1.0
Recall@100 = 1.0
paper E5 completed from the same current result
```

# Paper bundle v7

Current implementation:

```text
tools/paper_v6.py
tools/paper_bundle_v7.py
tools/finalize_paper_bundle_v7.py
```

Paper-v7 generates from one fresh current V20 bundle:

```text
4 SVG figures
12 raw-data CSV tables
figure_plan.json
figure_manifest.json
data_manifest.json
traceability.json
paper_v7.md
paper_v7_manifest.json
validation_result.json
paper_v7_bundle_manifest.json
```

Frozen figures:

```text
F1 -> all visible current curves
F2 -> highest-confidence example per available non-other morphology
F3 -> morphology-matched descriptive fit vs same-curve linear baseline
F4 -> same current-V20 E5 used by paper E5
```

Selected examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

Claim traceability:

```text
C1 -> F1/F2 + raw data
C2 -> F3 + current fit analysis + current curves
C4 -> F4 + current-V20 E5
C5 -> mandatory non-provenance/non-mechanism limitation
```

The earlier paper-v7 reproducibility caveat is resolved in the declared CI environment. The last paper-only drift came from `np.polyfit` at ~1e-16 scale and is now replaced with fixed-order analytic linear regression and `math.fsum` R².

# Paper interpretation discipline

Morphology-based archetypes are presentation choices, not provenance inference. A good generic fit is descriptive, not mechanistic proof.

Only completed machine evidence may be rendered as evidence. Keep experiment states explicit:

```text
READY_LOCAL
REQUESTED_BENCHMARK_ENGINE
COMPLETED
FAILED
```

# Next system-level milestone

Do not keep optimizing determinism now that the declared-CI gate passes. Do not add another dense numeric-noise grid, more figures, or rate tuning by default.

The next high-value technical gap is actual package structural damage, because Structural-v4 is descriptor-level only:

```text
whole table deletion
row truncation / changed table shape
shape-preserving localized value burst
```

Any such experiment should identify which layer fails first:

```text
A/locator
NPZ/b parsing
inner decode
candidate payload
V20 repair
authenticated B/r
```

If the dominant failure is structural A/parser behavior, fix that layer rather than adding RS parity. If structural handling is not currently blocking the complete system, prioritize integrated package usability instead.

# Claim discipline

Never write:

```text
undetectable
proven secure
real experimental evidence
universally compatible
mechanism proven by fit
```

unless a machine benchmark genuinely establishes that exact statement—which the current project does not.

Prefer bounded language such as:

```text
exact in this synthetic run
all tested seeds passed
empirical operating point
descriptive fit
morphology-based presentation archetype
not a universal guarantee
```
