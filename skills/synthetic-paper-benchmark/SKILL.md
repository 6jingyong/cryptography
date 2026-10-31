---
name: synthetic-paper-benchmark
description: Generate clearly labeled synthetic/mock scientific data packages and paper-style figures for benchmarking statistical carrier algorithms. Never represent synthetic results as real experiments.
---

# Synthetic Paper Benchmark Skill

## Purpose

Use this skill to create a **clearly labeled synthetic/mock research package**
for testing statistical-carrier algorithms.

The package may imitate the *structure* of a scientific paper:

- abstract-like benchmark summary
- methods
- synthetic datasets
- multi-panel figures
- tables
- supplementary-data style files
- reproducibility metadata

But every artifact must state that it is **synthetic / simulated / benchmark-only**.

Do not fabricate real-world scientific evidence, impersonate an actual paper,
invent human/animal experiments, or present synthetic results as observations.

## Inputs

1. `benchmark_goal`
   - capacity
   - robustness
   - distortion
   - multichannel scaling
   - transform comparison

2. `macro_families`
   - monotonic
   - periodic
   - harmonic
   - symmetric
   - gaussian_peak
   - saturation
   - hysteresis_like

3. `channels`
   - number of y-series sharing an x-axis

4. `rows`
   - numeric rows per data table

5. `carrier_mode`
   - q=8 protected-subspace carrier
   - GF(8) [9,7,3]
   - 6 payload + 1 shaping + 2 parity

6. `publication_precision`
   - explicit numeric rounding / quantization model

## Required workflow

### 1. Generate deterministic synthetic macros

For every series define a deterministic macro function:

`y_macro = f(x, fixed_parameters)`

No hidden random seed should be necessary to reproduce the macro structure.

### 2. Define protected macro subspace

Construct `B(x)` from the terms whose fitted interpretation must remain stable.

Examples:

Periodic:
`[1, sin(wx), cos(wx), sin(2wx), cos(2wx)]`

Affine:
`[1, x]`

Quadratic / peak in transformed space:
`[1, x, x^2]`

### 3. Build carrier complement

Compute a deterministic orthogonal complement `U` satisfying:

`B.T @ U ~= 0`

Prefer the smoothest free coordinates by ranking them with a second-difference
roughness operator.

### 4. Encode benchmark payload

Use deterministic synthetic high-entropy bytes only.

Map:

`bytes -> 3-bit GF(8) symbols -> [9,7,3]_8 blocks`

For each block use:

- 6 payload symbols
- 1 shaping symbol
- 2 parity symbols

Choose the shaping symbol that minimizes the declared distortion cost.

### 5. Publish transform

Apply an explicit deterministic publication transform, such as:

- numeric rounding
- decimal quantization
- table serialization

Record the transform exactly.

### 6. Decode self-contained

The decoder may use:

- published x
- published y values
- the compact benchmark codebook / mode metadata

It must not use the original unencoded y values.

### 7. Verify

Always report:

- SHA-256 exact payload recovery
- raw GF(8) symbol error rate
- payload bits / published numeric value
- payload bits / published row
- macro-fit parameter drift
- NRMSE
- roughness ratio
- for multichannel tables: correlation-matrix drift

## Paper-style output rules

Every mock paper or figure must visibly contain one of:

- `SYNTHETIC BENCHMARK`
- `SIMULATED DATA`
- `MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS`

Recommended sections:

1. Benchmark objective
2. Synthetic-data construction
3. Carrier algorithm
4. Publication transform
5. Recovery results
6. Structural distortion
7. Capacity scaling
8. Limitations
9. Reproducibility manifest

## Prohibited use

Do not use this skill to:

- fabricate evidence for a real scientific claim
- create a counterfeit real paper
- falsely attribute results to researchers/institutions
- disguise real secret/model-weight exfiltration as scientific data
- remove synthetic/mock labeling
