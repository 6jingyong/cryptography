# HANDOFF — audited protocol state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative; historical prose is not.

## 1. Authoritative lifecycle

```text
A -> locate/rank c -> strict open -> extract B+b -> B decodes b -> recover a
```

```text
A = long-lived locator / canonicalization / bootstrap protocol
B = per-package reconstruction codebook / manifest
b = processed payload representation
c = candidate package containing public fingerprint structure + B + b + integrity
a = final synthetic payload
d = unrelated public/background record
```

Package-specific q, transform, geometry, ECC, host model, payload length, padding, publication parameters, and decoder parameters belong in `B`, not long-lived `A`.

## 2. Locator / clean-host / structural state

Protocol-v3 candidate ranking uses `A + public NPZ structure` and does not parse B before ranking: **PASS**.

Clean-host V12 E5:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20 = 1.0
Recall@100 = 1.0
median target rank = 1
```

Structural v4 remains the explicit descriptor-level retrieval model:

```text
25% deletion: R@100=1.0, median rank=2
50% deletion: R@1000=0, median rank=10589
20% substitution: R@20=.9283, R@100=.9793, R@1000=.9812
50% deletion + 20% substitution: R@1000=0, median rank=13640
```

Descriptor-level reorder/split-merge controls do not prove the current NPZ parser survives physical table deletion or changed table count.

## 3. V18 current carrier

Implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

The sender observes a non-zero residual host before embedding. Host-aware modulo-QIM moves free-subspace coefficients to the nearest payload cosets. Concrete host/QIM/q/geometry state stays in B.

The original smooth-host first-pass gate remains valid:

```text
12 / 12 tables selected q=4
q=2 fallback not exercised
all selected-table calibration exact block recovery = 1.0
host-adjustment NRMSE ~= 0.000720 .. 0.001093
strictest declared budget = 0.0045
8 / 8 full-protocol seeds exact
Recall@100 = 1.0
median target rank = 1
max target rank = 2
```

Embedding adjustment is material: median adjustment RMS is about `0.446 ×` host-residual RMS; maximum observed in that run about `0.485`.

The old V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` summary remains **retired** and was not restored.

## 4. V18 residual-model matrix

Frozen plan:

```text
results/v18-residual-matrix-plan.md
```

Machine result:

```text
results/v18-residual-matrix.json
results/v18-residual-matrix.md
```

Five challenge residual families were tested at comparable free-subspace RMS energy without changing carrier policy after seeing results:

```text
iid Gaussian                 PASS
heteroscedastic Gaussian     PASS
AR(1), rho=0.85              PASS
low-frequency drift          PASS
Gaussian + sparse outliers   PASS
```

For **every** model:

```text
12 / 12 calibration tables passed
12 / 12 selected q=4
0 / 12 selected q=2
4 / 4 payload hashes distinct
4 / 4 exact full-protocol recovery
Recall@20 = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

Largest selected-table calibration NRMSE over the matrix: approximately `0.0011046`, still below the strictest existing budget `0.0045`.

Largest full-run embedding-adjustment RMS / host-residual RMS ratio: approximately `0.4914`.

Predeclared matrix classification: **GENERAL_V18_SUPPORTED within the declared synthetic known-host matrix**.

This wording is deliberately narrow. It does not mean universal noisy-host robustness.

### Why the 5/5 result is not surprising

The encoder sees the host and directly quantizes the observed free-subspace coefficients to payload cosets. Therefore host **distribution shape before embedding** mainly changes embedding distortion, not an unknown channel-interference term. Equal-energy challenge distributions consequently produced similar costs.

The matrix therefore shifts the main unresolved variable from host distribution to **damage after embedding**.

## 5. Paper line

Paper claim gate v7 remains PASS for bounded C1–C6 claims. C5 remains mandatory: descriptive framing/fits are not provenance or mechanism evidence. C6 remains limited to descriptor-v4.

Do not upgrade any current V18 result to:

```text
universal noisy-host robustness
unknown post-embedding noise robustness
coarser re-quantization robustness
q=2 fallback effectiveness
undetectability / cryptographic security
real-publication deployment
```

## 6. V12–V21 classification

```text
V12 -> CURRENT clean-host b carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old terminology stale
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION; distribution-broad within declared known-host synthetic matrix
V19 -> NEEDS-REINTEGRATION
V20 -> NEEDS-REINTEGRATION
V21 -> retain “protocol constraints before rate” only; old quantitative results STALE
```

Historical V18–V20 precise summaries remain non-authoritative unless recreated by current executable evidence.

## 7. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion or changed table count.
3. Structural-v4 has a sharp near-decoy boundary at six or fewer correct pairs.
4. 20% locator substitution has a catastrophic tail despite median rank 1.
5. Cross-platform QR/eigh/sign basis determinism is unresolved.
6. V18 q=2 fallback remains unexercised.
7. V18 host-distribution matrix uses sender-observed host residuals normalized to comparable free-subspace RMS.
8. Unknown **post-embedding** noise/drift has not been tested.
9. Stronger/coarser post-embedding publication re-quantization has not been tested for V18.
10. V19/V20 are not current implementations.
11. No universal undetectability/security or real-publication claim is supported.

## 8. Reproducible gates

Core audit:

```bash
python tools/audit_current.py
python protocol/locator-structural-v4.py --json-out /tmp/v4.json --md-out /tmp/v4.md
python tools/paper_claim_gate_v7.py --v4-result /tmp/v4.json --json-out /tmp/claims.json --md-out /tmp/claims.md
```

V18 smooth reference:

```bash
python src/noisy_host_package_v18.py --seed 101 --payload-bytes 512 --channels 2 --out-dir /tmp/v18-single
python protocol/real-package-v18.py --engine src/noisy_host_package_v18.py \
  --seeds 101,102,103,104,105,106,107,108 \
  --payload-bytes 512 --channels 2 --corpus-size 2000 --top-k 100 \
  --out /tmp/v18-protocol-result.json
```

V18 residual matrix:

```bash
python protocol/v18-residual-matrix.py \
  --engine src/noisy_host_package_v18.py \
  --protocol protocol/real-package-v18.py \
  --seeds 201,202,203,204 \
  --payload-bytes 512 --channels 2 --corpus-size 2000 --top-k 100 \
  --out /tmp/v18-residual-matrix.json
```

## 9. Current gate status

```text
A/B separation                              PASS
locator independence                        PASS
clean-host V12 E5                           PASS
structural v4                               PASS
Paper-v7 bounded claim gate                 PASS
V18 smooth-host first pass                  PASS
V18 five-model known-host residual matrix   PASS
old V18 quantitative-summary restoration    REJECTED / NOT CLAIMED
post-embedding V18 damage robustness         UNVERIFIED
V19                                           NEEDS-REINTEGRATION
V20                                           NEEDS-REINTEGRATION
```

## 10. Next work

Do **not** move to V19 or bit/value optimization yet.

The next falsification target should be a frozen **post-embedding channel-damage matrix**, because host distribution before embedding is no longer the main uncertainty.

At minimum it should vary:

```text
coarser re-quantization after embedding
small additive free-subspace / numeric noise relative to delta
combined re-quantization + noise
```

The purpose is to find the exact V18 recovery frontier, not to tune it away. If the current q=4 carrier fails early, record that boundary and only then decide whether V20-style outer reliability or a different guard mode is justified.

AUDIT GATE: PASS — safe to continue bounded falsification
