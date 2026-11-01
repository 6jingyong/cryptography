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

Structural v4 descriptor model:

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

Smooth-host first-pass evidence:

```text
12 / 12 tables selected q=4
q=2 fallback not exercised
all calibration exact block recovery = 1.0
host-adjustment NRMSE ~= 0.000720 .. 0.001093
strictest declared budget = 0.0045
8 / 8 full-protocol seeds exact
Recall@100 = 1.0
median target rank = 1
max target rank = 2
```

Embedding adjustment is material: median adjustment RMS is about `0.446 ×` host-residual RMS; maximum observed about `0.485`.

The old V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` summary remains retired and was not restored.

## 4. V18 known-host residual-model matrix

Frozen equal-energy challenge families:

```text
iid Gaussian                 PASS
heteroscedastic Gaussian     PASS
AR(1), rho=0.85              PASS
low-frequency drift          PASS
Gaussian + sparse outliers   PASS
```

For every model:

```text
12 / 12 calibration tables passed
12 / 12 selected q=4
0 / 12 selected q=2
4 / 4 exact full-protocol recovery
Recall@100 = 1.0
median/max target rank = 1
```

Predeclared classification: **GENERAL_V18_SUPPORTED within the declared sender-observed synthetic host matrix**.

This does not mean universal noisy-host robustness. Because the encoder sees the host and snaps its free-subspace coefficients to payload cosets, pre-embedding host-distribution shape is not the dominant remaining failure variable.

Evidence:

```text
results/v18-residual-matrix-plan.md
results/v18-residual-matrix.json
results/v18-residual-matrix.md
```

## 5. V18 post-embedding / pre-seal publication-damage frontier

This experiment applies unknown numeric damage in transform space after embedding **and after A-keyed public assignment**, but before c is sealed. The outer integrity tag therefore covers the damaged b and does not trivially mask the inner-carrier boundary.

Frozen result, seeds 301–304:

```text
baseline 1.00x re-quantization      PASS 4/4
1.25x re-quantization              FAIL 3/4
1.50x re-quantization              FAIL 2/4
>=1.75x re-quantization            FAIL 0/4

noise sigma=0.05 delta             PASS 4/4
noise sigma=0.10 delta             PASS 4/4
noise sigma=0.15 delta             FAIL 2/4
noise sigma>=0.20 delta            FAIL 0/4
```

All six tested combined conditions at `1.50x`/`2.00x` re-quantization plus `0.05–0.15 delta` noise failed the all-seed gate. The lightest combined case (`1.50x + 0.05 delta`) recovered only 1/4 exactly.

Crucially, **every condition retained target locator rank 1, locator score 1.0, and Recall@100=1.0**. Failure starts in direct `B + damaged b` decoding, not A-layer retrieval.

Therefore the following upgrade is explicitly **REJECTED**:

> rebuilt V18 already has broad publication robustness after embedding.

Current supported interpretation:

> V18 is broad across the tested sender-observed host distributions, but its unknown post-embedding/pre-seal numeric damage margin is narrow. All-seed additive-noise recovery was demonstrated through `0.10 delta`; no extra all-seed re-quantization margin beyond the existing `1.00x` grid was demonstrated.

Evidence:

```text
results/v18-publication-damage-plan.md
results/v18-publication-damage.json
results/v18-publication-damage.md
```

The exact transition still lies inside:

```text
re-quantization: 1.00x .. 1.25x
additive noise:  0.10 delta .. 0.15 delta
```

## 6. V18 versus V20 boundary

The publication-damage frontier above is a V18 question because damage occurs before c is sealed.

If numeric bytes change **after** c has been sealed, strict outer integrity is expected to reject the candidate before inner decoding. Repair/survival of that post-seal corruption belongs to **V20 outer package reliability**, not V18.

Do not use V18 results to claim post-seal tamper tolerance.

## 7. Paper line

Paper claim gate v7 remains PASS for bounded C1–C6 claims. C5 remains mandatory: descriptive framing/fits are not provenance or mechanism evidence. C6 remains limited to descriptor-v4.

Do not upgrade V18 evidence to:

```text
broad publication robustness
post-seal tamper tolerance
q=2 fallback effectiveness
undetectability / cryptographic security
real-publication deployment
```

## 8. V12–V21 classification

```text
V12 -> CURRENT clean-host b carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old terminology stale
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION; broad known-host matrix, narrow measured publication margin
V19 -> NEEDS-REINTEGRATION
V20 -> NEEDS-REINTEGRATION; post-seal reliability belongs here
V21 -> retain “protocol constraints before rate” only; old quantitative results STALE
```

Historical V18–V20 precise summaries remain non-authoritative unless recreated by current executable evidence.

## 9. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion or changed table count.
3. Structural-v4 has a sharp near-decoy boundary at six or fewer correct pairs.
4. 20% locator substitution has a catastrophic tail despite median rank 1.
5. Cross-platform QR/eigh/sign basis determinism is unresolved.
6. V18 q=2 fallback remains unexercised.
7. Exact V18 publication transition inside `1.00–1.25x` requant and `0.10–0.15 delta` noise is not yet refined.
8. V20 post-seal repair/reliability is not current.
9. V19 is not current.
10. No universal undetectability/security or real-publication claim is supported.

## 10. Reproducible gates

Core audit:

```bash
python tools/audit_current.py
python protocol/locator-structural-v4.py --json-out /tmp/v4.json --md-out /tmp/v4.md
python tools/paper_claim_gate_v7.py --v4-result /tmp/v4.json --json-out /tmp/claims.json --md-out /tmp/claims.md
```

V18 smooth reference and known-host matrix:

```bash
python src/noisy_host_package_v18.py --seed 101 --payload-bytes 512 --channels 2 --out-dir /tmp/v18-single
python protocol/real-package-v18.py --engine src/noisy_host_package_v18.py \
  --seeds 101,102,103,104,105,106,107,108 \
  --payload-bytes 512 --channels 2 --corpus-size 2000 --top-k 100 \
  --out /tmp/v18-protocol-result.json
python protocol/v18-residual-matrix.py --engine src/noisy_host_package_v18.py \
  --protocol protocol/real-package-v18.py --seeds 201,202,203,204 \
  --payload-bytes 512 --channels 2 --corpus-size 2000 --top-k 100 \
  --out /tmp/v18-residual-matrix.json
```

Publication-damage frontier:

```bash
python protocol/v18-publication-damage.py --engine src/noisy_host_package_v18.py \
  --protocol protocol/real-package-v18.py --seeds 301,302,303,304 \
  --payload-bytes 512 --channels 2 --corpus-size 2000 --top-k 100 \
  --out /tmp/v18-publication-damage.json
```

## 11. Current gate status

```text
A/B separation                               PASS
locator independence                         PASS
clean-host V12 E5                            PASS
structural v4                                PASS
Paper-v7 bounded claim gate                  PASS
V18 smooth-host first pass                   PASS
V18 five-model known-host matrix             PASS
V18 broad publication-robustness upgrade     REJECTED
V18 additive noise <=0.10 delta              PASS in tested 4 seeds
V18 extra requantization >=1.25x             FAIL in tested matrix
V19                                            NEEDS-REINTEGRATION
V20                                            NEEDS-REINTEGRATION
```

## 12. Next work

Do **not** widen delta, add redundancy, move to V19, or optimize bit/value yet.

First refine the already-measured transition intervals **without changing the carrier**:

```text
re-quantization between 1.00x and 1.25x
additive noise between 0.10 delta and 0.15 delta
```

This is boundary measurement, not rescue tuning. Only after that frontier is measured should we decide whether the appropriate response is an explicit publication guard mode, an inner-code change, or V20-style outer reliability.

AUDIT GATE: PASS — evidence chain remains auditable; broad V18 publication robustness is rejected
