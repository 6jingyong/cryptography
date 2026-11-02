# Structural parity determinism v2 — frozen promotion gate

Scope: **synthetic/mock benchmark only**.

This is a new gate, not a reinterpretation of the failed v1 result.

History:

1. `structural-parity-determinism-v1` — **FAIL**, because two independent whole-system replicas differed only in paper-v7 Figure 3 table 11 `matched_fit_r2` / `delta_r2` by `1.1102230246251565e-16`;
2. carrier/package/B/NPZ/CSV/E5/morphology/archetype/story were exact in v1;
3. `paper-v6-deterministic-fit-v1` replaced only the descriptive fit numerical kernel with fixed-order scalar least-squares/R² and passed regression gates on both the old current path and structural candidate path.

The v1 failure remains authoritative historical evidence.

## Frozen v2 stack

```text
A-v4-erasure-xlen
+ 11 data tables + 1 XOR structural-parity table
+ src/noisy_host_package_v18_deterministic.py
+ unchanged protocol/real-package-v20.py
+ tools/structural_parity_current_end_to_end.py
+ tools/paper_v6_deterministic.py
+ unchanged tools/paper_bundle_v7.py / finalize_paper_bundle_v7.py
```

Configuration remains exactly the candidate viability/v1 configuration:

```text
seeds = 1301..1308
representative seed = 1301
payload = 512 B
channels = 2
corpus = 2,000
near decoys = 1%
Top-K open = 100
```

No q/delta/RS/structural/morphology/grid/story/claim parameter may be changed after results.

## Replicas and comparator

Two independent GitHub Actions replicas `a` and `b` each:

1. build the full structural candidate E2E bundle;
2. render/finalize paper-v7;
3. fingerprint the bundle with the existing `tools/current_bundle_semantic_fingerprint.py`.

A third job uses the unchanged `tools/compare_semantic_fingerprints.py`.

Exact equality remains required for the same authority as v1:

- payload SHA;
- basis version;
- canonical B;
- technical summary;
- 8-seed E5;
- integration result;
- every NPZ x/y float64 array;
- all 12 paper-v7 CSVs;
- paper-v7 numeric figure plan;
- morphology representative selection;
- archetype/story;
- aggregate semantic authority SHA-256.

Raw NPZ/manifest container hash remains diagnostic only.

## Pass rule

```text
both upstream replicas PASS
semantic_equal = true
mismatch_count = 0
```

No rounding/canonicalization or comparison-field weakening is permitted after seeing results.

## Promotion meaning if PASS

A v2 pass, together with the already-passing structural-parity-v3 and whole-system viability gates, is sufficient machine evidence for a final static promotion/reference migration audit of the **frozen supported 12-table configuration**.

It does not prove arbitrary package-configuration stability, two-table erasure recovery, every-platform bit identity, real-publication robustness, or security.
