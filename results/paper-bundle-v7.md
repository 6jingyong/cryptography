# Paper bundle v7 — PASS with an explicit cross-run determinism boundary

Scope: **synthetic/mock benchmark only**.

Frozen plan: `results/paper-bundle-v7-plan.md`.

Final source evidence:

```text
workflow run: 41377319772
artifact: 13111387910
artifact sha256: 9be547a7fb26344172ffb1ed0654123bca9b3506479d38d9a4fac9f790836c8f
```

## What passed

The paper side now consumes a fresh current end-to-end V18/V20 bundle and produces a genuine multi-figure, raw-data-exporting, claim-traceable synthetic paper package.

Final paper-v7 output contains:

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

Automatically selected morphology examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

Independent audit confirmed this exactly matches the frozen highest-confidence-per-morphology rule.

Nine non-linear tables enter Figure 3. Every recorded morphology-matched R² equals the current paper-v6 machine analysis, and every linear baseline independently recomputed from the same current visible curve matches the figure plan.

Current technical control remains:

```text
8 seeds
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
all payload hashes unique
median target rank = 1
max target rank = 1
```

The paper retains:

```text
MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS
SYNTHETIC BENCHMARK / SIMULATED DATA ONLY
```

and the mandatory limitation that morphology/framing/generic fits are descriptive presentation choices rather than evidence of real provenance or physical mechanism.

## Traceability

Claims explicitly traced:

```text
C1 -> response-regime / morphology breadth -> F1 + F2 + all raw-data tables
C2 -> descriptive fit quantification       -> F3 + fit_results + current curves
C4 -> current technical recoverability     -> F4 + current-V20 E5
C5 -> mandatory provenance/mechanism limit -> manuscript + manifests
```

The final complete paper-v7 manifest covers **23 files excluding itself**, including both `validation_result.json` and the nested `paper_v7_manifest.json`.

Independent recomputation found:

```text
nested manifest mismatch count = 0
final complete manifest mismatch count = 0
```

## Visual audit

The generated SVGs were rendered and inspected after download.

- F1 shows all twelve synthetic curves clearly.
- F2 shows four distinct morphology examples and rule-selected metadata.
- F3 visibly separates morphology-matched fits from linear baselines on the non-linear curves.
- F4 is visually simple because every tested seed has target rank 1 and exact recovery 1; that simplicity reflects the machine result rather than a plotting failure.

## Important negative result: same seed is not yet numerically identical across fresh runs

A second project-level audit compared two independent successful paper-v7 CI artifacts generated with the same frozen seeds and configuration:

```text
first success run: 41377065172 / artifact 13111592914
final run:         41377319772 / artifact 13111387910
```

Stable across both runs:

```text
representative payload SHA-256: identical
current-V20 E5 file/hash: identical
8-seed exact/locator result: identical
selected morphology examples: identical
presentation archetype: identical
story type: identical
```

Not identical:

```text
representative current NPZ byte hash
representative current B manifest byte hash
visible response data in 8 / 12 tables
```

Differing visible table IDs:

```text
0, 2, 3, 5, 6, 7, 10, 11
```

The largest visible absolute difference among those tables was about `0.1321` synthetic response units.

Therefore the correct bounded conclusion is:

> Paper-v7 is fully traceable within each generated artifact and preserves the same payload, current E5 result, morphology selection, archetype, and story across the two audited runs; however, fixed-seed visible carrier data are not yet numerically identical across independent fresh runs.

This does **not** invalidate the paper-v7 traceability result. It does invalidate any stronger claim that the current generator is already numerically deterministic across CI runs.

The likely technical locus is the already-known deterministic-basis problem around numerical QR/eigendecomposition, not a paper selection or evidence-substitution problem. That should be treated as the next system-level reproducibility issue, not hidden by freezing one artifact.

## Supported conclusion

The current system can now turn one current V20 machine package into a multi-figure synthetic paper-shaped bundle with raw-data export, explicit claim tracing, and complete per-file hashes without manually substituting data or evidence.

## Not supported

This milestone does not establish:

```text
cross-run numerical identity of the visible carrier for a fixed seed
real experimental evidence or provenance
physical mechanism proof
real-publication covert deployment
undetectability or cryptographic security
optimal carrier rate or parity overhead
```

## Next priority

Do not respond to this result by adding more figures or more V20 damage points.

The next high-value system task is **deterministic visible-carrier generation**: make the current basis/generation path produce numerically identical current paper data for the same seed across independent runs, while keeping the existing A/B responsibilities and current bounded carrier/reliability meaning unchanged.
