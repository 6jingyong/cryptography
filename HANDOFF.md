# HANDOFF — audited project state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative. Historical prose and legacy V18–V21 numbers are not.

## 1. Project-level orientation

Do not treat this project as a sequence of carrier-parameter competitions.

The intended system is:

```text
synthetic payload a
-> encode to numeric b
-> create per-package manifest B (+ optional repair r)
-> construct candidate package c
-> mix c among unrelated synthetic d records
-> long-lived A locates / bootstraps c without parsing B during ranking
-> authenticated open
-> B explains b; optional V20 repair handles bounded sparse damage
-> exact a
-> same current machine package/results feed a clearly labeled mock-paper renderer
```

The central two-codebook distinction remains:

```text
A = long-lived locator / canonicalization / bootstrap root
B = per-package reconstruction + reliability manifest
```

Package-specific q, transform, geometry, ECC, host model, payload length, publication parameters, outer-code family, shard size, and parity geometry belong in B, not A.

Priority order:

```text
find c > open/authenticate c > interpret B > recover a > presentation > rate/overhead optimization
```

A locally better q, parity count, or damage threshold is not automatically project progress if it does not improve the complete system.

## 2. Current project-level integration — PASS

Current runner:

```text
tools/current_end_to_end.py
```

Frozen fresh seeds `901..908`, representative seed `901`, payload 512 B, channels 2, 2,000-candidate corpus, Top-100.

The runner uses the **current V18 carrier + current bounded V20 logical reliability layer**, then feeds the representative current V20 NPZ + B manifest and the same 8-seed machine result into `tools/paper_v6.py`.

Technical result:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

Representative seed 901:

```text
target index = 1734 / 2000
target rank = 1
locator score = 1.0
20 near decoys
explicit decoy rejected
repair-field bitflip rejected by V20 envelope integrity
```

Paper integration:

```text
paper input = representative current V20 package/manifest
paper E5 input = same current-V20 8-seed result
E5 status = COMPLETED
E5 pass = true
visible synthetic/mock labels = present
mandatory non-provenance limitation = present
```

The uploaded bundle contains both technical and paper artifacts and a per-file SHA-256 manifest. All 14 recorded file entries were independently recomputed with zero mismatches.

Evidence:

```text
results/current-e2e-integration-plan.md
results/current-e2e-integration.json
results/current-e2e-integration.md
```

This is the current highest-level milestone: the repository now has one reproducible path connecting locator, carrier, reliability, exact recovery, and mock-paper generation.

## 3. Base / locator state

- Protocol-v3 locator uses `A + public NPZ structure` and does not parse B before ranking: **PASS**.
- Clean-host V12 E5: 8/8 unique payload hashes, 8/8 exact recovery, Recall@20=1, Recall@100=1, median target rank=1.
- Structural-v4 remains descriptor-level A-layer evidence only; it does not prove arbitrary physical NPZ deletion/split/merge survival.
- Paper claim gate v7 remains PASS only for bounded C1–C6 claims; C5 remains mandatory.

## 4. V18 state

Current implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
```

Status: **CURRENT_BOUNDED_REINTEGRATION**.

Current evidence:

```text
smooth reference: 8/8 exact under current protocol
known-host matrix: 5/5 frozen sender-observed residual families pass
q=4 selected for all tested tables; q=2 fallback remains unexercised
```

Broad V18 publication robustness is **REJECTED**.

24-seed paired additive-noise statistics:

```text
sigma/delta : exact/24
0.08..0.12 : 24/24
0.13       : 23/24
0.14       : 20/24
0.15       : 16/24
0.16       :  9/24
0.17       :  4/24
0.18       :  1/24
```

Dense re-quantization is non-monotonic and alignment-dependent; a scalar threshold is rejected.

Transition-region residual failures are sparse after the existing Hamming layer:

```text
paired-noise failures: median 2 payload bits, 1 bad table, 1 bad corrected codeword
representative requant failures: median 2 payload bits, 1 bad table, 1 bad corrected codeword
```

That sparse profile motivated V20 rather than continued V18 retuning.

## 5. V20 state

Implementation:

```text
protocol/real-package-v20.py
protocol/v20-bounded-reintegration.py
protocol/v20-failure-envelope.py
```

Fixed geometry:

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
RS byte-error bound       <=4 bytes per shard
parity total              32 bytes
payload parity overhead   6.25%
```

V20 uses logical integrity:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw numeric b is excluded from the envelope tag. B contains the authenticated expected final payload SHA-256 and reliability geometry. Final acceptance always requires exact SHA-256 equality to that authenticated target.

First frozen 24-seed gate:

```text
clean                     24/24
noise 0.14 delta          24/24 V20
noise 0.15 delta          24/24 V20
noise 0.16 delta          24/24 V20
requant 1.06x             24/24 V20
requant 1.20x             24/24 V20
requant 1.30x             24/24 V20
49 / 49 attempted repairs successful
```

Stronger fixed-geometry failure envelope:

```text
noise 0.18 delta   24/24
noise 0.20 delta   17/24; exactly 7 packages exceed RS shard bound
noise 0.22 delta    5/24; exactly 19 exceed bound
noise >=0.25        0/24; all exceed bound

requant 1.50x      24/24
requant 1.75x      20/24; exactly 4 packages exceed RS shard bound
requant >=2.00x     0/24; all exceed bound
```

Across every tested stronger-damage run:

```text
V20 failure <=> at least one 128-byte shard has >4 candidate byte errors
```

Mismatch count: **0**. Locator structural score stayed 1.0.

Interpretation: current V20 is bounded but mechanically interpretable inside the tested synthetic channel. It does not exhibit an earlier unexplained protocol failure before its declared RS capacity is exceeded.

## 6. Paper line

Current renderer:

```text
tools/paper_v6.py
```

The paper layer is downstream of machine evidence:

```text
machine result
-> morphology analysis
-> narrative archetype
-> generic descriptive fits
-> claim/experiment gate
-> clearly labeled mock paper
```

Current end-to-end integration confirms that `paper_v6.py` can consume a **current V20 package and current V20 multiseed result directly**.

The renderer must retain the distinction:

```text
morphology / framing / descriptive fits = presentation
not provenance
not physical-mechanism proof
```

## 7. Current classification

```text
V12 -> CURRENT clean-host carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old terminology stale
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION
V19 -> NEEDS-REINTEGRATION, but not immediate priority
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped RS-capacity failure envelope
V21 -> retain "protocol constraints before rate" only; old quantitative results stale
Current end-to-end technical + paper integration -> PASS
```

Historical V18/V20 precise summaries remain retired unless recreated by current executable evidence.

## 8. Known unresolved issues

1. Public locator-label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion / changed table count.
3. Cross-platform QR/eigh/sign basis determinism remains unresolved.
4. V18 q=2 fallback remains unexercised.
5. Re-quantization alignment structure is measured but not mechanistically modeled.
6. V20 has only one RS geometry; 6.25% overhead is not shown minimal or optimal.
7. V20 structural-damage behavior is not comprehensively characterized.
8. V19 is not current.
9. The current paper output is a correctly gated Markdown/JSON package, not yet a polished multi-figure paper-shaped artifact.
10. No universal undetectability/security or real-publication claim is supported.

## 9. Next work — avoid local over-optimization

Do **not** immediately add another V-number, another dense damage grid, or a bit/value optimization pass.

The current technical path is sufficiently characterized for the project to move one level upward.

The next high-value milestone should improve the **integrated artifact**, especially the thinner paper side:

```text
current V20 numeric package
-> morphology-selected multi-figure layout
-> actual generated synthetic figures from the same package data
-> machine-backed captions / claim map
-> downloadable synthetic raw-data tables
-> clearly labeled mock-paper manuscript/package
-> bundle-level verification that figures/data/claims all trace back to current machine artifacts
```

This is closer to the project objective than continuing to optimize V18/V20 locally.

Structural-damage tests and V19 remain valid future work, but they should be pulled in when they unblock the complete system rather than because an unresolved bullet exists.

AUDIT GATE: PASS — current technical and mock-paper paths are now integrated; next priority is the whole paper-shaped artifact, not another carrier micro-benchmark
