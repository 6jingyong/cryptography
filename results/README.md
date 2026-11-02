# Results index

Only milestones still useful under the corrected protocol remain in the current working tree.

| File | Current meaning |
|---|---|
| `adaptive_q_v12.md` | clean-host carrier baseline for processed payload `b` |
| `locator_v16.md` | historical A-layer labeled locator / erasure benchmark |
| `publication_robustness_v17.md` | historical publication/canonicalization observations; responsibilities remapped |
| `protocol-real-package-v3.md` | A fingerprint bound to actual NPZ public structure |
| `locator-structural-v4.json/.md` | descriptor-level A-layer stress model; not physical NPZ deletion proof |
| `noisy-host-v18-reintegration.json/.md` | bounded V18 noisy-host evidence |
| `v18-residual-matrix.json/.md` | five sender-observed residual families |
| `v18-publication-damage.json/.md` | broad V18 publication robustness rejected |
| `v18-publication-statistics.json/.md` | paired-noise transition + alignment-dependent re-quantization |
| `v18-error-profile.json/.md` | sparse post-Hamming residual errors in failed packages |
| `v20-bounded-reintegration.json/.md` | fixed 6.25% RS geometry initial bounded gate |
| `v20-failure-envelope.json/.md` | tested V20 failures align with declared shard capacity |
| `physical-structural-damage-v1-plan.md` | pre-result frozen contract for actual NPZ structural damage |
| `physical-structural-damage-v1.json/.md` | actual NPZ layer mapping: locator vs parser/decoder vs V20 |
| `structural-erasure-v2-plan.md` | frozen A-v4/decoder-v2 candidate contract |
| `structural-erasure-v2.json/.md` | evidence-valid candidate result; rank-1 gate fails, promotion deferred |
| `current-e2e-integration.json/.md` | one current technical package feeds recovery and paper analysis |
| `paper-bundle-v7.json/.md` | multi-figure/raw-data/traceability synthetic paper bundle |
| `deterministic-basis-v1.json/.md` | A/B/C promotion evidence for the current deterministic V18 engine |
| `paper-claim-audit-v7.json/.md` | bounded claim gate and mandatory limitations |
| `current-summary.json` | compact audited current state |

## Current whole-system state

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
-> multi-figure traceable synthetic paper bundle
```

Current engine:

```text
src/noisy_host_package_v18_deterministic.py
basis_version = deterministic-dct-mgs-v1
```

The promoted protocol remains A-v3 + deterministic V18 + bounded V20. A-v4/decoder-v2 are **candidates only**.

## Deterministic-basis promotion

Frozen promotion gates:

```text
Gate A  current E2E / paper viability                  PASS
Gate B  two independent runners, exact semantic match PASS
Gate C  bounded V18/V20 evidence without retuning     PASS
```

Final Gate B:

```text
semantic_equal = true
mismatch_count = 0
raw container hash equal = true
semantic authority SHA-256 = 243b05fd32624e931379ea471c2d209700fb3491c33a911f9071084e8f57bc04
```

## Current E2E

Seeds `901..908`:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

## Physical structural damage v1

Fresh seeds `1001..1024`, actual public NPZ mutation, unchanged deterministic V18 and unchanged V20 geometry:

```text
whole x+y table deletion
  -> locator first failure
  -> R@100 = 0
  -> median rank = 1749
  -> no candidate payload

one tail y-segment truncation
  -> locator stays rank 1
  -> decoder cannot form candidate payload
  -> V20 not applicable

4-segment localized burst, sigma=4 delta
  -> locator stays rank 1
  -> 4 candidate byte errors
  -> 24/24 V20 repair success

6-segment localized burst, sigma=4 delta
  -> locator stays rank 1
  -> 6 candidate byte errors
  -> 0/24 V20 repair success
```

Across every candidate-producing run in that matrix:

```text
V20 failure <=> any 128-byte shard has >4 candidate byte errors
```

Mismatch count: **0**.

## Structural erasure v2 candidate

Fresh seeds `1101..1124`; current deterministic V18 and current V20 remain unchanged. Only the candidate A canonicalization/locator and candidate structural decoder differ.

A-v4 uses independently stable public x-grid lengths rather than renormalizing surviving table classes after deletion. Decoder-v2 decodes all complete segments and zero-fills explicit missing payload intervals.

Observed:

```text
clean
  -> 24/24 exact
  -> R@100 = 1
  -> median rank = 1
  -> max rank = 2

one whole table deleted
  -> locator score = 11/12
  -> R@100 = 1
  -> median rank = 1
  -> candidate payload 24/24
  -> 341 payload bits erased
  -> current V20 final recovery 0/24

one tail segment truncated
  -> candidate payload 24/24
  -> 5 payload bits erased, 1 byte touched
  -> 3/24 direct exact
  -> 21/21 V20 repair success
  -> final acceptance 24/24
```

The frozen promotion gate required every clean target to rank 1. It **fails** at seed `1116`, where the existing near-decoy generator creates an exact 12/12 A-visible descriptor duplicate before the target. The gate was not relaxed post hoc. Classification: **evidence valid, promotion deferred**.

The important architectural result is nevertheless clear: A-v4/decoder-v2 move the tested structural failures to the correct layer. Tail truncation needs no additional parity once a candidate exists. Whole-table loss does.

A whole logical-first table contains 341 arbitrary payload bits, while current V20 has only 256 parity bits total. Therefore:

```text
256 < 341
```

So interleaving alone cannot guarantee one arbitrary whole-table recovery with current V20 redundancy. The minimum information shortfall is 85 bits before code-geometry overhead is considered.

## Paper bundle v7

Paper-v7 generates 4 SVG figures, 12 per-table raw-data CSV files, figure/data manifests, C1/C2/C4/C5 traceability, explicit synthetic/mock labeling, and a complete final bundle manifest.

Rule-selected examples remain:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

## What matters next

Do not continue floating-point micro-optimization, dense numeric-noise grids, or blindly increase V20 parity.

The next high-value question is now narrower and more structural:

```text
A-v4 / decoder-v2
  -> keep as candidate, not promoted

single tail-segment loss
  -> already recoverable once parser emits a candidate

single whole-table loss
  -> requires >=341 bits of independent recovery information for arbitrary payloads
  -> current V20 provides only 256 bits
```

Therefore the next useful design is a **structural redundancy layout** that can cover one table erasure while preserving A/B responsibilities and reasonable overhead. Rank-1 locator semantics under exact A-visible descriptor collisions must also be specified explicitly rather than hidden by seed choice.

V19 remains deferred until multiple genuinely current carrier modes make selector policy useful.

Still unsupported: real-publication deployment, real confidential payload hiding, universal undetectability/security, real provenance/mechanism, or universal every-platform bit identity.
