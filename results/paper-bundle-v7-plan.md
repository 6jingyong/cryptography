# Paper bundle v7 plan

Scope: **synthetic/mock benchmark only**.

This milestone upgrades the paper side of the already-passing current end-to-end system. It does **not** change V18/V20 carrier, locator, reliability, or rate parameters.

## Input contract

All paper-v7 inputs must come from one fresh run of the current integration path:

```text
tools/current_end_to_end.py
```

Frozen integration inputs:

```text
technical seeds: 901..908
representative seed: 901
payload bytes: 512
current V18 + current bounded V20
corpus size: 2000
paper-v6 renderer: current tools/paper_v6.py
```

Paper-v7 must consume the representative current V20 NPZ, current B manifest, current technical summary, current-V20 E5 result, and current paper-v6 analysis outputs. It may not substitute a historical fixture.

## Required output package

```text
paper_v7_output/
  paper_v7.md
  paper_v7_manifest.json
  figure_plan.json
  figure_manifest.json
  data_manifest.json
  traceability.json
  figures/
    fig1_overview.svg
    fig2_morphology_examples.svg
    fig3_fit_ablation.svg
    fig4_e5_control.svg
  data/
    table_00.csv
    ... one CSV per current table ...
```

## Frozen figure roles

### Figure 1 — package response overview

Show all current visible synthetic response curves from the representative current V20 NPZ. This is the breadth/overview figure.

### Figure 2 — morphology examples

Select at most one representative table for each available non-`other` morphology class using **highest morphology confidence** from current paper-v6 analysis. No manual table selection after viewing the result.

### Figure 3 — fit ablation

For each non-linear/non-`other` table, compare the morphology-matched descriptive fit R² already recorded by paper-v6 with a linear baseline R² recomputed from the same visible curve. This is descriptive evidence only, not mechanism proof.

### Figure 4 — current technical control

Visualize the current-V20 E5 result from seeds 901..908: target rank per seed and exact-recovery state. This figure must use the same machine result that completed paper E5.

## Raw data export

Export one CSV per current table using the visible block used by the paper analysis:

```text
x
channel_0
channel_1
... all current channels
```

Do not invent values or export a different synthetic dataset for presentation.

## Traceability contract

Every generated figure must record:

```text
figure path
figure sha256
source current NPZ sha256
source table ids / machine result ids
claim ids supported
synthetic/mock caption
```

Every exported CSV must record its SHA-256 and source table id.

`traceability.json` must connect the paper's bounded claims to current machine evidence, figures, and/or raw-data tables.

Minimum claim roles:

```text
C1 -> response-regime breadth / morphology
C2 -> descriptive fit quantification
C4 -> current machine recoverability / locator control
C5 -> mandatory limitation: presentation framing is not provenance or mechanism evidence
```

## Paper requirements

`paper_v7.md` must:

- visibly display `MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS`;
- visibly display `SYNTHETIC BENCHMARK / SIMULATED DATA ONLY`;
- embed all four SVG figures;
- identify the selected domain as a **presentation archetype**, not provenance;
- link raw synthetic data tables / manifests;
- keep generic fits explicitly descriptive;
- include the mandatory non-provenance/non-mechanism limitation;
- state the current technical control from the same current-V20 E5 result;
- not invent a real material, instrument, institution, author, patient cohort, physical mechanism, or real experiment.

## Pass gate

PASS only if:

1. current end-to-end base bundle passes first;
2. all required figures are generated and non-empty;
3. one raw-data CSV exists for every current table;
4. all figure/data manifest hashes recompute exactly;
5. every figure records the representative current NPZ hash as its source where applicable;
6. Figure 2 selection follows highest-confidence-per-morphology rule;
7. Figure 3 matched-fit values equal paper-v6 recorded values and linear baselines are derived from the same current curves;
8. Figure 4 uses the same current-V20 E5 result that completed paper E5;
9. all required claim IDs have traceability entries;
10. paper labels and mandatory limitation are present;
11. no carrier/reliability parameters are changed to improve the paper.

If this fails, fix the paper/data/trace interface. Do not retune V18/V20 to make figures prettier.

## Non-goals

This milestone does not claim:

```text
real experimental evidence
real provenance
real mechanism
real-paper covert deployment
undetectability
cryptographic security of the numeric carrier
optimal carrier capacity or parity overhead
```
