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
- Structural-v4 remains descriptor-level A-layer evidence only; it does not prove the physical NPZ parser survives arbitrary deletion/split/merge.
- Paper claim gate v7 remains PASS only for bounded C1–C6 claims; C5 remains mandatory.

## 3. V18 rebuilt carrier

Current implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

The sender observes a non-zero residual host before embedding. Host-aware modulo-QIM moves free-subspace coefficients to payload cosets. Concrete q/host/geometry/decoder state remains in B.

Smooth-reference first pass:

```text
12/12 tables selected q=4
q=2 fallback not exercised
host-adjustment NRMSE ~= 0.000720 .. 0.001093
strictest table budget = 0.0045
8/8 full-protocol seeds exact
Recall@100 = 1.0
```

Embedding adjustment is material: median adjustment RMS is about `0.446 ×` host-residual RMS; maximum observed about `0.485`.

The historical V18 `59/60`, `57 q4 / 2 q2 / 1 unresolved` summary remains **retired** and was not restored.

## 4. Known-host residual breadth

The frozen equal-energy matrix passed all five declared sender-observed host families:

```text
iid Gaussian
heteroscedastic Gaussian
AR(1), rho=.85
low-frequency drift
Gaussian + sparse outliers
```

Each model passed all 12 calibration tables and 4/4 current-protocol seeds with Recall@100=1.

Interpretation: **distribution-broad within the declared sender-observed synthetic host matrix**, not universal noisy-host robustness.

Evidence:

```text
results/v18-residual-matrix-plan.md
results/v18-residual-matrix.json
results/v18-residual-matrix.md
```

## 5. Post-embedding / pre-seal damage

Damage is applied after V18 embedding and A-keyed public assignment but before c is sealed. This isolates the inner carrier rather than letting outer integrity reject the sample first.

The coarse and 8-seed refinement experiments established two facts:

1. broad publication robustness is **REJECTED**;
2. failures begin in `B + damaged b` inner decode while locator retrieval stays intact.

The 8-seed refinement also showed that re-quantization factor is not a simple monotonic damage axis.

## 6. 24-seed publication statistics — current best evidence

Fresh seeds `501..524`; no carrier changes.

### Re-quantization

Exact package recovery:

```text
factor : exact/24
1.00   : 24
1.02   : 24
1.04   : 22
1.06   : 19
1.08   : 21
1.10   : 22
1.12   : 21
1.14   : 19
1.16   : 20
1.18   : 22
1.20   : 17
1.22   : 22
1.24   : 21
1.26   : 19
1.28   : 17
1.30   : 16
```

This response is **non-monotonic**. For example, `1.06x -> 19/24`, `1.10x -> 22/24`; `1.20x -> 17/24`, `1.22x -> 22/24`.

Therefore the following claim is rejected:

```text
larger re-quantization factor = monotonically worse V18 robustness
```

The data are consistent with grid/coset/basis alignment effects. No periodic law is claimed yet.

### Paired additive noise

For each seed/table, one base Gaussian field is drawn and the same field is scaled across alpha. Thus alpha is a genuine nested strength axis.

```text
sigma/delta : exact/24
0.08        : 24
0.09        : 24
0.10        : 24
0.11        : 24
0.12        : 24
0.13        : 23
0.14        : 20
0.15        : 16
0.16        :  9
0.17        :  4
0.18        :  1
```

All 24 per-seed PASS→FAIL sequences are monotonic under paired scaling.

This corrects the earlier independent-noise ambiguity. Additive-noise strength is a valid monotonic axis under the paired construction, but the result is still stochastic rather than a universal deterministic threshold.

Supported statement:

```text
24/24 exact package recovery was observed through 0.12 delta;
success probability declines sharply from 0.13 delta onward.
```

All locator structural scores remain `1.0`; failures remain inner decode.

Evidence:

```text
results/v18-publication-statistics-plan.md
results/v18-publication-statistics.json
results/v18-publication-statistics.md
```

## 7. V18 / V20 boundary

Pre-seal numeric damage is a V18 inner-carrier question.

Numeric corruption **after c is sealed** should fail strict outer integrity before inner decoding. Repair/survival of post-seal corruption belongs to **V20 outer reliability**.

The current statistics are not enough to size V20 redundancy. Before V20 is rebuilt, measure the multiplicity and location of inner decode errors under the paired-noise transition and representative re-quantization factors.

## 8. Current classification

```text
V12 -> CURRENT clean-host b carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old terminology stale
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION
       - known-host feasibility supported
       - tested host-distribution breadth supported
       - broad publication robustness REJECTED
       - scalar monotonic re-quantization threshold REJECTED
       - paired additive-noise transition measured statistically
V19 -> NEEDS-REINTEGRATION
V20 -> NEEDS-REINTEGRATION; do not size redundancy before error-profile measurement
V21 -> retain "protocol constraints before rate" only; old quantitative results STALE
```

## 9. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion / changed table count.
3. Cross-platform QR/eigh/sign basis determinism remains unresolved.
4. V18 q=2 fallback remains unexercised.
5. Re-quantization alignment structure is measured but not mechanistically modeled.
6. Additive-noise package success probability has only 24 payload/host seeds; confidence intervals remain wide near the transition.
7. Inner error multiplicity/location is not yet characterized.
8. V19 and V20 are not current implementations.
9. No universal undetectability/security or real-publication claim is supported.

## 10. Next work

Do **not** widen delta, add redundancy, move to V19, or optimize bit/value yet.

Next experiment should be measurement-only:

```text
paired additive noise:
  inspect failed packages at 0.13..0.18 delta
  count symbol/byte/block/table errors
  determine whether failures are sparse or catastrophic

representative re-quantization:
  inspect error multiplicity at safe/unsafe alignment points
  compare error structure, not only package-exact rate
```

Only after that should V20 outer reliability be designed. If failures are dense/catastrophic, V20-style redundancy may be a poor response and the current V18 carrier should remain explicitly bounded rather than “rescued”.

AUDIT GATE: PASS — V18 feasibility is current, broad publication robustness is rejected, and the next decision depends on measured error structure
