# Results index

Only milestones still useful under the corrected protocol remain in the current working tree.

| File | Current meaning |
|---|---|
| `adaptive_q_v12.md` | clean-host carrier baseline for processed payload `b` |
| `locator_v16.md` | historical A-layer labeled locator / erasure benchmark |
| `publication_robustness_v17.md` | historical publication/canonicalization observations; responsibilities remapped |
| `protocol-real-package-v3.md` | current A-v3 fingerprint bound to actual NPZ public structure |
| `locator-structural-v4.json/.md` | descriptor-level A-layer stress model |
| `noisy-host-v18-reintegration.json/.md` | bounded V18 noisy-host evidence |
| `v18-residual-matrix.json/.md` | five sender-observed residual families |
| `v18-publication-damage.json/.md` | broad V18 publication robustness rejected |
| `v18-publication-statistics.json/.md` | paired-noise transition + alignment-dependent re-quantization |
| `v18-error-profile.json/.md` | sparse post-Hamming residual errors in failed packages |
| `v20-bounded-reintegration.json/.md` | fixed 6.25% RS geometry initial bounded gate |
| `v20-failure-envelope.json/.md` | tested V20 failures align with declared shard capacity |
| `physical-structural-damage-v1-plan.md` | frozen actual-NPZ structural damage contract |
| `physical-structural-damage-v1.json/.md` | actual NPZ layer mapping: locator vs parser/decoder vs V20 |
| `structural-erasure-v2-plan.md` | frozen A-v4/decoder-v2 candidate contract |
| `structural-erasure-v2.json/.md` | evidence-valid candidate result; rank-1 gate fails, promotion deferred |
| `structural-parity-v3-plan.md` | frozen 11-data + 1-XOR-parity architecture and gate |
| `structural-parity-v3.json/.md` | 600-observation single-table structural-parity gate; PASS |
| `current-e2e-integration.json/.md` | current A-v3/V18/V20 technical package feeds recovery and paper analysis |
| `paper-bundle-v7.json/.md` | multi-figure/raw-data/traceability synthetic paper bundle |
| `deterministic-basis-v1.json/.md` | A/B/C promotion evidence for the current deterministic V18 engine |
| `paper-claim-audit-v7.json/.md` | bounded claim gate and mandatory limitations |
| `current-summary.json` | compact audited current state |

## Current promoted whole-system state

```text
synthetic a
-> deterministic current V18 carrier
-> bounded V20 package
-> c mixed among d
-> current A-v3 locator/bootstrap
-> authenticated open
-> B decode / optional V20 repair
-> exact a
-> same current package + machine evidence
-> traceable synthetic paper bundle
```

Current promoted engine:

```text
src/noisy_host_package_v18_deterministic.py
basis_version = deterministic-dct-mgs-v1
```

The promoted protocol still remains **A-v3 + deterministic V18 + bounded V20** until structural-parity-v3 passes a current-E2E/paper integration gate.

## Deterministic-basis promotion

```text
Gate A  current E2E / paper viability                  PASS
Gate B  two independent runners, exact semantic match PASS
Gate C  bounded V18/V20 evidence without retuning     PASS
```

Final Gate B semantic authority SHA-256:

```text
243b05fd32624e931379ea471c2d209700fb3491c33a911f9071084e8f57bc04
```

## Structural evidence progression

### Physical structural damage v1

Actual NPZ mutation established the original layer split:

```text
whole-table deletion -> A-v3 locator failure
one tail segment      -> decoder fails before candidate
shape-preserving burst -> reaches V20 and follows its <=4 byte/shard capacity
```

### Structural erasure v2

A-v4 stable x-grid labels + decoder-v2 moved failures downstream:

```text
whole-table deletion -> candidate exists, but 341 unknown bits > current 256 V20 parity bits
one tail segment      -> 24/24 final acceptance with unchanged V20
```

The frozen strict rank-1 gate failed because seed 1116 contained a genuine exact A-visible descriptor duplicate. This remains a failed historical gate; it was not retroactively relaxed.

### Structural parity v3

Frozen architecture:

```text
11 data tables + 1 XOR parity table
12 public tables total
4096 payload bits
373 structural parity bits = 46.625 B = 9.1064% payload overhead
q/delta unchanged
V20 unchanged
```

Fresh seeds `1201..1224`; every public table tested separately:

```text
24 clean controls
288 complete one-table deletions
288 one-tail-segment truncations
600 total observations
```

Result:

```text
clean                       24/24 exact
any one public table lost  288/288 exact
any one tail segment lost  288/288 exact
Recall@20                  1.0 for all three conditions
max target rank            1 in this frozen corpus
unresolved structural bits 0 in all 600 observations
V20 repair attempts         0
```

Breakdown:

```text
data-table deletion          264/264 exact
parity-table deletion         24/24 exact
data-table tail truncation   264/264 exact
parity-table tail truncation  24/24 exact
```

This is the first candidate that makes bounded single-table structural erasure a **pre-V20 solved problem** rather than an outer-RS failure.

It is not yet the current path because structural reliability still needs one integration gate with current E2E and paper-v7.

## Current E2E and paper

Current promoted seeds `901..908` remain:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median/max target rank = 1 / 1
```

Paper-v7 remains PASS with 4 SVG figures, 12 raw-data CSV files, traceability, explicit synthetic/mock labeling, and deterministic numeric planning in the declared CI environment.

## What matters next

Do not return to floating-point micro-optimization, dense numeric-noise grids, or blind V20 parity tuning.

The highest-value next gate is:

```text
A-v4
+ 11+1 XOR structural parity
+ deterministic V18
+ unchanged V20
-> current E2E
-> paper-v7
```

If that integrated gate passes without q/delta/RS retuning or determinism regression, structural-parity-v3 becomes a serious promotion candidate. Only after that should broader structural families such as two-table loss, insertion/reordering, or split/merge be considered.

Still unsupported: real-publication deployment, real confidential payload hiding, universal undetectability/security, real provenance/mechanism, or universal every-platform bit identity.
