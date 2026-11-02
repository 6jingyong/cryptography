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
- Structural-v4 remains descriptor-level A-layer evidence only; it does not prove arbitrary physical NPZ deletion/split/merge survival.
- Paper claim gate v7 remains PASS only for bounded C1–C6 claims; C5 remains mandatory.

## 3. V18 rebuilt carrier

Implementation:

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

The frozen equal-energy matrix passed all five declared sender-observed host families: iid Gaussian, heteroscedastic Gaussian, AR(1) rho=.85, low-frequency drift, and Gaussian+sparse outliers. Each passed all 12 calibration tables and 4/4 current-protocol seeds.

Interpretation: **distribution-broad within the declared sender-observed synthetic host matrix**, not universal noisy-host robustness.

## 5. Publication-damage statistics

Damage is applied after V18 embedding and A-keyed public assignment but before c is sealed to isolate the inner carrier.

Broad publication robustness is **REJECTED**. Failures begin inside `B + damaged b`; locator retrieval remains intact.

24-seed paired additive noise (`501..524`) is monotonic per seed when one base noise field is scaled across alpha:

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

Dense re-quantization remains non-monotonic: e.g. `1.06x -> 19/24`, `1.10x -> 22/24`; `1.20x -> 17/24`, `1.22x -> 22/24`. Treat factor as an alignment variable, not scalar damage severity.

Evidence:

```text
results/v18-publication-statistics-plan.md
results/v18-publication-statistics.json
results/v18-publication-statistics.md
```

## 6. Residual error profile — current decision evidence

Fresh seeds `601..624`; no carrier changes. The experiment decomposes failed packages into payload bit errors, bad codewords, and bad tables after the existing per-codeword Hamming correction.

Across 37 failed paired-noise packages (`0.12..0.16 delta`):

```text
payload bit errors:        median 2, p90 4, max 4
bad tables:                median 1, p90 2, max 3
bad corrected codewords:   median 1, p90 2, max 3
raw payload-symbol errors: median 18, p90 26, max 29
post-Hamming symbol errors: median 2, p90 3, max 3
```

Across 23 failed representative re-quantization packages:

```text
payload bit errors:        median 2, p90 3, max 5
bad tables:                median 1, p90 1, max 2
bad corrected codewords:   median 1, p90 1, max 2
raw payload-symbol errors: median 15, p90 17.8, max 22
post-Hamming symbol errors: median 1, p90 2, max 3
```

Every failed package in this profile had at most four bad corrected codewords. About 95.7% of failed re-quantized packages concentrated all final bit errors in one table.

Interpretation: current V18 failures near the measured transition are **sparse residual failures after a strong inner-code reduction**, not package-wide collapse. This is sufficient evidence to justify a **bounded V20 outer-reliability prototype**.

Evidence:

```text
results/v18-error-profile-plan.md
results/v18-error-profile.json
results/v18-error-profile.md
protocol/v18-error-profile.py
```

This does not prove any V20 code/geometry yet, and it does not prove real post-seal corruption has exactly the same error distribution as the pre-seal diagnostic.

## 7. V18 / V20 boundary

Pre-seal numeric damage is a V18 inner-carrier question.

Numeric corruption **after c is sealed** should fail strict outer integrity before inner decoding. Repair/survival of post-seal corruption belongs to **V20 outer reliability**.

The error profile now gives a reason to test V20: residual errors are sparse enough that a small outer code may be efficient. V20 must still be evaluated under an explicit post-seal lifecycle with strict final integrity verification.

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
       - transition-region residual errors measured as sparse
V19 -> NEEDS-REINTEGRATION
V20 -> JUSTIFIED_FOR_BOUNDED_REINTEGRATION_EXPERIMENT
       - no current V20 implementation/effectiveness claim yet
V21 -> retain "protocol constraints before rate" only; old quantitative results STALE
```

## 9. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion / changed table count.
3. Cross-platform QR/eigh/sign basis determinism remains unresolved.
4. V18 q=2 fallback remains unexercised.
5. Re-quantization alignment structure is measured but not mechanistically modeled.
6. V20 code family, redundancy geometry, overhead, and post-seal lifecycle are not yet validated.
7. Pre-seal V18 error geometry may not equal real post-seal package corruption geometry.
8. V19 is not current.
9. No universal undetectability/security or real-publication claim is supported.

## 10. Next work

Do **not** optimize bit/value and do not restore historical V20 numbers.

Next step: rebuild a **minimal V20 outer-reliability prototype** against the current `A -> c -> B -> b -> a` lifecycle. Freeze redundancy before results, keep concrete parity/shard geometry in B/c rather than A, inject post-seal damage, attempt repair before final integrity acceptance, and require exact final payload hash.

The first V20 experiment should be deliberately small: enough redundancy to target the measured few-bit/few-codeword residual regime, not a large code designed to force success.

If that bounded prototype fails despite sparse errors, reject the proposed V20 geometry rather than increasing redundancy until it passes.

AUDIT GATE: PASS — V18 remains bounded; sparse residual-error evidence now justifies a minimal V20 reintegration experiment
