# Input → Output: one complete mock-paper run

This page is the shortest concrete description of the tool.

> **MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS**

## Input

The user gives a small JSON config:

```json
{
  "label": "MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS",
  "payload_bytes": 8192,
  "channels_per_table": 8,
  "locator": {
    "candidate_count": 1000,
    "near_decoys": 20,
    "shared_structure_fraction": 0.5,
    "target_substitutions": 1
  }
}
```

That is enough for the example generator.

There is no real paper, author, institution, material, patient, experiment, or
arbitrary secret file in the input.

## Run

```bash
python examples/generate_mock_paper.py \
  --config examples/mock-paper-config.json \
  --out-dir mock_paper_output
```

## What happens internally?

```text
1. CREATE
   deterministic synthetic payload

2. WRITE
   payload -> q-ary symbols -> ECC -> adaptive-q numeric tables

3. PUBLISH
   write numeric package + manifest

4. FIND
   derive structural fingerprint
   rank target among synthetic candidates

5. VERIFY
   reject best structural decoy
   decode true target
   compare SHA-256

6. PRESENT
   generate mock paper + SVG + CSV + readable JSON
```

## Output

```text
mock_paper_output/
├── README.md
├── paper.md
├── manifest_readable.json
├── verification.json
├── figures/
│   ├── figure_1_periodic_before_after.svg
│   ├── figure_2_adaptive_q_schedule.svg
│   └── figure_3_locator_verifier.svg
├── data/
│   ├── periodic_table_sample.csv
│   └── gaussian_table_sample.csv
└── carrier/
    ├── published_adaptive_q_v12.npz
    ├── manifest_adaptive_q_v12.json
    └── adaptive_q_v12_results.json
```

## Which output should a human read?

```text
paper.md
figures/
manifest_readable.json
verification.json
```

## Which output is authoritative?

Not the prose.

The authoritative chain is:

```text
carrier/published_adaptive_q_v12.npz
+ carrier/manifest_adaptive_q_v12.json
        ↓
decoder
        ↓
recovered synthetic payload
        ↓
verification.json
```

## The one sentence explanation

The example tool:

> generates a synthetic multi-table numeric package, uses a second structural
> codebook to find it among mock candidates, and accepts it only when the
> numeric decoder and strict integrity verification both succeed.

That is the project in one sentence.
