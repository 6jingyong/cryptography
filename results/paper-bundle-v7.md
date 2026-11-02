# Paper bundle v7 — passed; original reproducibility boundary resolved by follow-up

Scope: **synthetic/mock benchmark only**.

Frozen plan: `results/paper-bundle-v7-plan.md`.

The original paper-v7 milestone passed its per-artifact traceability gate but correctly exposed a fixed-seed cross-run reproducibility boundary. That negative result is preserved rather than rewritten. A later frozen follow-up, `deterministic-basis-v1`, resolved the current boundary in the declared independent GitHub Actions environment.

## Original paper-v7 milestone

Source evidence:

```text
workflow run: 41377319772
artifact: 13111387910
artifact sha256: 9be547a7fb26344172ffb1ed0654123bca9b3506479d38d9a4fac9f790836c8f
```

Paper-v7 produced:

```text
4 SVG figures
12 per-table raw-data CSV files
figure_plan.json
figure_manifest.json
data_manifest.json
traceability.json
paper_v7.md
paper_v7_manifest.json
validation_result.json
paper_v7_bundle_manifest.json
```

Figure roles:

```text
F1 -> all visible current response curves
F2 -> one rule-selected high-confidence example per non-other morphology
F3 -> morphology-matched descriptive fit R² vs same-curve linear baseline
F4 -> same current-V20 E5 locator/exact-recovery result used by paper E5
```

Selected morphology examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

Current technical control:

```text
8 seeds
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
all payload hashes unique
median/max target rank = 1 / 1
```

The paper retains explicit synthetic/mock labels and the mandatory limitation that morphology, framing, and generic fits are descriptive presentation choices rather than evidence of real provenance or physical mechanism.

The final complete manifest covered 23 files excluding itself, with zero nested/final manifest mismatches.

## Original negative result

Two independent successful fresh CI artifacts with the same frozen seeds preserved payload, E5, morphology selection, archetype, and story, but differed in visible numeric carrier values in 8/12 tables and in NPZ/B hashes.

Differing table IDs were:

```text
0, 2, 3, 5, 6, 7, 10, 11
```

This was a valid result at the time and motivated the deterministic-basis work. It was not hidden by freezing one preferred artifact.

## Follow-up resolution

See:

```text
results/deterministic-basis-v1-plan.md
results/deterministic-basis-v1.json
results/deterministic-basis-v1.md
```

Current engine:

```text
src/noisy_host_package_v18_deterministic.py
basis_version = deterministic-dct-mgs-v1
```

Frozen follow-up gates:

```text
Gate A: current E2E + paper viability PASS
Gate B: two independent runners, semantic_equal=true, mismatch_count=0
Gate C: bounded V18/V20 evidence PASS without q/delta/RS retuning
```

Gate B now includes canonical B, all x/y float64 arrays, all CSV bytes, current E5, paper-v7 numeric figure plan, morphology selection, and archetype/story.

Final semantic authority SHA-256 across both independent runners:

```text
243b05fd32624e931379ea471c2d209700fb3491c33a911f9071084e8f57bc04
```

The final paper-only ~1e-16 mismatch was traced to `np.polyfit` in the Figure 3 linear baseline. Paper-v7 now uses fixed-order analytic one-variable regression plus `math.fsum` R². No carrier parameter changed for this repair.

Therefore the **current** bounded conclusion is:

> Paper-v7 is traceable and semantically reproducible for the frozen current configuration across the declared independent GitHub Actions environment.

This does not establish universal bit-identical behavior across every CPU/libm/NumPy/Python implementation.

## Still not supported

```text
real experimental evidence or provenance
physical mechanism proof
real-publication covert deployment
undetectability or cryptographic security
optimal carrier rate or parity overhead
universal every-platform bit identity
```

## Next priority

Do not continue floating-point micro-optimization or add more figures merely because determinism is now solved in the declared CI environment.

The next high-value question returns to the whole system: actual package structural loss (table deletion, truncation, changed shape, localized burst) is still not covered by descriptor-level Structural-v4 and should be tested only insofar as it informs A/locator, parser, inner decode, or V20 layer design.
