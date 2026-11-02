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
-> A locator/bootstrap
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

Legacy baseline:

```text
src/noisy_host_package_v18.py
```

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

Compared semantics include canonical B, all x/y float64 table arrays, all CSVs, current E5, paper-v7 numeric figure plan, morphology selection, and archetype/story.

Gate C also passed V18 core/residual/publication/error-profile and V20 bounded/failure-envelope harnesses with no q/delta/RS retuning.

This resolves the fixed-seed visible-data blocker in the declared independent GitHub Actions environment. It is not a universal cross-platform bit-identity guarantee.

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

## Paper bundle v7

Paper-v7 generates:

```text
4 SVG figures
12 per-table raw-data CSV files
figure/data manifests
C1/C2/C4/C5 traceability
clearly labeled synthetic manuscript
complete final bundle manifest
```

Rule-selected examples remain:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

The last paper-only cross-run drift was a ~1e-16 difference in two `np.polyfit` linear baseline R² values on identical inputs. It was replaced with fixed-order analytic linear regression + `math.fsum` R². The final paper numeric plan now participates in the exact Gate B equality.

## What matters next

Do not continue floating-point micro-optimization, dense numeric-noise grids, parity tuning, or bit/value optimization merely because they are available.

The highest-value unresolved technical gap is now **real package structural damage**: Structural-v4 is only a descriptor model and does not establish what happens when the actual NPZ loses a table, changes row count, or suffers a localized shape-preserving burst.

A future frozen structural experiment should distinguish:

```text
A/locator failure
b/NPZ parse failure
candidate payload corruption
V20 repair success/failure
authenticated B/r rejection
```

V19 should remain deferred until multiple genuinely current carrier modes make selector policy useful.

Still unsupported: real-publication deployment, real confidential payload hiding, universal undetectability/security, real provenance/mechanism, or universal every-platform bit identity.
