# Structural parity determinism v1 — frozen promotion gate

Scope: **synthetic/mock benchmark only**.

This gate follows two already-passing candidate milestones:

1. `structural-parity-v3`: bounded single-table/tail erasure gate PASS;
2. `structural-parity-current-integration`: whole-system technical + unchanged paper-v7 viability PASS.

The candidate is still **not current-promoted**. This gate applies the same independent-run semantic determinism standard previously required for the deterministic V18 promotion.

## Frozen stack

```text
A-v4-erasure-xlen
+ 11 data tables + 1 XOR structural-parity table
+ src/noisy_host_package_v18_deterministic.py
+ unchanged protocol/real-package-v20.py
+ tools/structural_parity_current_end_to_end.py
+ unchanged paper-v6
+ unchanged paper-v7/finalizer
```

Fresh/current candidate E2E configuration is unchanged from the viability gate:

```text
seeds = 1301..1308
representative seed = 1301
payload = 512 B
channels = 2
corpus = 2,000
near decoys = 1%
Top-K open = 100
```

No q/delta/RS/structural/paper parameter may be changed after seeing results.

## Independent replicas

Two GitHub Actions matrix jobs, `a` and `b`, must each independently:

1. build the full candidate E2E bundle;
2. render unchanged paper-v7;
3. finalize the paper-v7 bundle;
4. run the existing `tools/current_bundle_semantic_fingerprint.py`.

A third independent comparison job downloads both fingerprints and runs the existing strict `tools/compare_semantic_fingerprints.py`.

## Semantic authority

Exact equality is required for:

- payload SHA;
- declared basis version;
- canonical B JSON semantics;
- canonical technical summary;
- canonical 8-seed E5 result;
- canonical integration result;
- every NPZ table x/y float64 array by shape/dtype/SHA-256;
- every exported paper-v7 CSV by rows/channels/SHA-256;
- paper-v7 numeric figure plan;
- morphology representative selection;
- presentation archetype;
- story type;
- aggregate semantic-authority SHA-256.

Raw NPZ/manifest container hashes remain diagnostic only. They may be reported but are not the semantic authority.

## Frozen pass rule

```text
semantic_equal = true
mismatch_count = 0
```

Both replica builds must independently pass upstream technical + paper-v7 gates before fingerprinting.

A failure is retained. Do not round, canonicalize, retune, or weaken comparison fields after results merely to obtain equality.

## Promotion interpretation

If this gate passes, then within the frozen current 12-table configuration the candidate will have:

- bounded single-table structural erasure evidence;
- whole-system E2E + paper-v7 viability;
- two-independent-run semantic determinism under the same authority used for the current deterministic engine.

That is sufficient to make it a **current-path promotion candidate for the frozen supported configuration**, subject to a final static diff/reference migration audit. It is not evidence of arbitrary configuration stability, every-platform bit identity, multi-table erasure recovery, real-publication robustness, or security.
