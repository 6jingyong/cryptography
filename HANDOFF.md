# HANDOFF — audited protocol state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative. Historical prose and legacy V18–V21 numbers are not.

## 1. Authoritative lifecycle

```text
A -> locate/rank c -> strict open -> extract B+b -> B decodes b -> recover a
```

```text
A = long-lived locator / canonicalization / bootstrap protocol
B = per-package reconstruction codebook / manifest
b = processed payload representation
c = public candidate package containing fingerprint structure + B + b + integrity
a = final synthetic payload
d = unrelated background record
```

Package-specific q, transform, geometry, ECC, host model, payload length, padding, publication parameters, and decoder parameters belong in `B`, not long-lived `A`.

## 2. Audited base state

- Protocol-v3 locator uses `A + public NPZ structure` and does not parse B before ranking: **PASS**.
- Clean-host V12 E5: 8/8 unique payload hashes, 8/8 exact recovery, Recall@20=1, Recall@100=1, median target rank=1.
- Structural-v4 remains a descriptor-level A-layer stress model. Important failures remain visible: 50% deletion has Recall@1000=0 and median rank 10589; 20% substitution has R@20=.9283/R@100=.9793/R@1000=.9812.
- Paper claim gate v7 remains PASS only for bounded C1–C6 claims; C5 remains mandatory.

## 3. V18 rebuilt carrier

Implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

The sender observes a non-zero residual host before embedding. Host-aware modulo-QIM moves free-subspace coefficients to the nearest payload cosets. All concrete host/QIM/q/geometry state remains in B.

Smooth-reference first pass:

```text
12/12 tables selected q=4
q=2 fallback not exercised
all calibration exact block recovery = 1.0
host-adjustment NRMSE ~= 0.000720 .. 0.001093
strictest table budget = 0.0045
8/8 full-protocol seeds exact
Recall@100 = 1.0
median target rank = 1
max target rank = 2
```

Embedding adjustment is material: median adjustment RMS is about `0.446 ×` host-residual RMS; maximum observed about `0.485`.

The historical V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` summary remains **retired** and was not restored.

## 4. Known-host residual breadth

Frozen equal-energy matrix:

```text
iid Gaussian                 PASS
heteroscedastic Gaussian     PASS
AR(1), rho=.85               PASS
low-frequency drift          PASS
Gaussian + sparse outliers   PASS
```

Every model passed all 12 calibration tables, selected q=4 for all 12, and recovered 4/4 fresh protocol seeds with Recall@100=1.

Interpretation: **distribution-broad within the declared sender-observed synthetic host matrix**, not universal noisy-host robustness.

Evidence:

```text
results/v18-residual-matrix-plan.md
results/v18-residual-matrix.json
results/v18-residual-matrix.md
```

## 5. Post-embedding / pre-seal publication damage — coarse result

Damage is applied after V18 embedding and A-keyed public assignment but before c is sealed, so outer integrity does not trivially mask V18 reconstruction failure.

Seeds 301–304:

```text
1.00x re-quantization   4/4 exact
1.25x                   3/4
1.50x                   2/4
>=1.75x                 0/4

noise 0.05 delta        4/4
noise 0.10 delta        4/4
noise 0.15 delta        2/4
noise >=0.20 delta      0/4
```

All tested combined 1.50x/2.00x + 0.05–0.15 delta conditions failed the all-seed gate.

Every target remained locator rank 1 / score 1.0 / Recall@100=1. Failure begins in direct `B + damaged b` decoding.

Therefore **broad V18 publication robustness is REJECTED**.

Evidence:

```text
results/v18-publication-damage-plan.md
results/v18-publication-damage.json
results/v18-publication-damage.md
```

## 6. Fresh-seed refinement — important methodological correction

The transition intervals were retested with fresh seeds 401–408 and no carrier changes.

### Re-quantization

```text
1.00x  8/8
1.05x  7/8
1.10x  8/8
1.15x  7/8
1.20x  7/8
1.25x  6/8
```

The key result is **non-monotonicity**: `1.05x` fails the 8/8 gate while `1.10x` passes. Therefore a scalar monotonic “re-quantization threshold” is not supported by this grid. Grid/coset/basis alignment matters.

Do not state:

```text
threshold lies between 1.10x and 1.15x
all factors below 1.10x are safe
largest passing factor = universal frontier
```

### Additive noise

```text
0.10 delta  8/8
0.11 delta  8/8
0.12 delta  7/8
0.13 delta  3/8
0.14 delta  6/8
0.15 delta  6/8
```

The all-seed PASS/FAIL pattern is PASS, PASS, FAIL, FAIL, FAIL, FAIL, but exact pass counts are not monotonic because each alpha uses a different deterministic random-noise realization.

Therefore `0.10 delta` is independently reproduced and `0.11 delta` also passes this fresh 8-seed set, but a deterministic threshold between `0.11` and `0.12 delta` is **not** established.

Every refined condition still has Recall@100=1; failure remains inner decode.

Evidence:

```text
results/v18-publication-frontier-refine-plan.md
results/v18-publication-frontier-refine.json
results/v18-publication-frontier-refine.md
```

## 7. V18 / V20 boundary

Pre-seal publication damage is a V18 inner-carrier question.

Numeric corruption **after c is sealed** should fail strict outer integrity before inner decoding. Repair/survival of post-seal corruption belongs to **V20 outer reliability**, not V18.

## 8. Current classification

```text
V12 -> CURRENT clean-host b carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old terminology stale
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION
       - broad across tested known-host distributions
       - broad publication robustness REJECTED
       - re-quantization response non-monotonic on tested grid
       - additive-noise result is stochastic, not a deterministic threshold
V19 -> NEEDS-REINTEGRATION
V20 -> NEEDS-REINTEGRATION; post-seal repair belongs here
V21 -> retain "protocol constraints before rate" only; old quantitative results STALE
```

## 9. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion / changed table count.
3. Structural-v4 has a sharp near-decoy boundary at six or fewer correct pairs.
4. Cross-platform QR/eigh/sign basis determinism remains unresolved.
5. V18 q=2 fallback remains unexercised.
6. V18 re-quantization needs a dense success map, not another scalar-threshold search.
7. V18 additive-noise behavior needs a success-probability experiment with paired/scaled noise or multiple replicates per alpha.
8. V19 and V20 are not current implementations.
9. No universal undetectability/security or real-publication claim is supported.

## 10. Next work

Do **not** widen delta, add redundancy, move to V19, or optimize bit/value yet.

The next experiment should change the **measurement model**, not the carrier:

```text
re-quantization:
  dense factor map -> identify safe/unsafe alignment bands or periodic structure

additive noise:
  many fresh payload/host seeds
  paired base-noise fields scaled across alpha, and/or multiple independent replicates per alpha
  estimate package-exact success probability with uncertainty
```

This follows directly from the non-monotonic refinement result. If a later guard mode or V20 redundancy is justified, it should be designed only after this probability/alignment map exists.

AUDIT GATE: PASS — evidence chain remains auditable; broad V18 publication robustness and a scalar re-quantization threshold are rejected
