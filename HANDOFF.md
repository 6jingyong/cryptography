# HANDOFF — audited project state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative. Historical prose and legacy V18–V21 numbers are not.

## 1. Project orientation

Do not treat this project as a sequence of carrier-parameter competitions.

The intended system is:

```text
synthetic payload a
-> numeric b
-> per-package B (+ optional repair r)
-> candidate package c mixed among unrelated synthetic d
-> long-lived A locates / bootstraps c without parsing B during ranking
-> authenticated open
-> B explains b; optional V20 repair
-> exact a
-> the same current machine package/results feed a clearly labeled mock-paper bundle
```

```text
A = long-lived locator / canonicalization / bootstrap root
B = per-package reconstruction + reliability manifest
```

Package-specific q, transform, geometry, ECC, host model, publication parameters, shard size, parity geometry, etc. belong in B, not A.

Priority:

```text
find c > open/authenticate c > interpret B > exact a > traceable presentation > rate/overhead optimization
```

A locally better q, parity count, damage threshold, or prettier figure is not automatically project progress if it does not improve the complete system.

## 2. Current integrated technical path

Current runner:

```text
tools/current_end_to_end.py
```

Frozen seeds `901..908`, representative seed `901`, payload 512 B, channels 2, 2,000-candidate corpus, Top-100.

Technical result:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

Representative controls:

```text
target rank = 1
locator score = 1.0
explicit decoy rejected
repair-field bitflip rejected
```

The same current V20 NPZ/B and same current-V20 8-seed result feed the paper line; paper E5 is `COMPLETED` and passes.

Evidence:

```text
results/current-e2e-integration-plan.md
results/current-e2e-integration.json
results/current-e2e-integration.md
```

Important refinement after paper-v7 audit: this is an integrated and per-artifact traceable path, but fixed-seed visible carrier values are not yet numerically identical across independent fresh CI runs. Do not overstate byte/numeric reproducibility until the basis issue is fixed.

## 3. V18 state

Status: **CURRENT_BOUNDED_REINTEGRATION**.

Current evidence:

```text
smooth reference: 8/8 exact
five frozen sender-observed residual families: pass
q=4 selected for all tested tables; q=2 fallback unexercised
```

Broad V18 publication robustness is **REJECTED**.

24-seed paired additive-noise result:

```text
0.08..0.12 delta : 24/24
0.13             : 23/24
0.14             : 20/24
0.15             : 16/24
0.16             :  9/24
0.17             :  4/24
0.18             :  1/24
```

Re-quantization is alignment-dependent and non-monotonic; no scalar threshold claim.

Transition failures are sparse after inner Hamming correction, motivating V20 rather than more V18 retuning.

## 4. V20 state

Status: **CURRENT_BOUNDED_REINTEGRATION**.

Fixed geometry:

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
RS byte-error bound       <=4 bytes per shard
parity total              32 bytes
payload parity overhead   6.25%
```

Integrity semantics:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw numeric b is not in the V20 envelope tag. Final acceptance always requires exact SHA-256 equality to the authenticated target in B.

Initial frozen gate:

```text
clean + six damaged conditions: 24/24 each after V20
49 / 49 attempted repairs successful
```

Stronger fixed-geometry envelope found:

```text
V20 failure <=> at least one 128-byte shard has >4 candidate byte errors
```

Mismatch count: **0** across the tested stronger grid. Locator remained score 1.0.

This is a bounded, mechanically interpretable synthetic reliability result, not universal robustness or proof that 6.25% is optimal.

## 5. Paper bundle v7 — current paper milestone

Implementation:

```text
tools/paper_v6.py
tools/paper_bundle_v7.py
tools/finalize_paper_bundle_v7.py
```

Paper-v7 consumes one fresh current V20 package plus current paper-v6 machine analysis and produces:

```text
4 SVG figures
12 raw-data CSV files
figure/data manifests
claim traceability
paper_v7.md
validation result
nested paper manifest
complete final bundle manifest
```

Frozen figure roles:

```text
F1 -> all visible current response curves
F2 -> highest-confidence example per non-other morphology
F3 -> morphology-matched descriptive fit vs same-curve linear baseline
F4 -> same current-V20 E5 result used by paper E5
```

Automatically selected morphology examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

Claims traced:

```text
C1 -> F1/F2 + raw data
C2 -> F3 + fit machine output + current curves
C4 -> F4 + current-V20 E5
C5 -> mandatory non-provenance/non-mechanism limitation
```

Final complete manifest covers 23 files excluding itself. Nested-manifest and independent final-manifest mismatch counts are both 0.

Visual audit confirms all four figures contain meaningful output; F4 is intentionally flat/simple because all eight seeds are rank 1 and exact 1.

Evidence:

```text
results/paper-bundle-v7-plan.md
results/paper-bundle-v7.json
results/paper-bundle-v7.md
```

### Paper-v7 cross-run reproducibility boundary

Two independent successful fresh CI runs used the same frozen seeds/configuration.

Stable:

```text
representative payload SHA-256
current-V20 E5 hash/result
morphology representative selection
presentation archetype
story type
```

Not stable:

```text
current NPZ byte hash
current B manifest byte hash
visible response values in 8 / 12 tables
```

Differing visible table IDs:

```text
0, 2, 3, 5, 6, 7, 10, 11
```

Therefore paper-v7 status is:

```text
PASS_WITH_REPRODUCIBILITY_BOUNDARY
```

It proves complete traceability **within each generated artifact**, not fixed-seed numerical identity across independent runs.

## 6. Current classification

```text
V12 -> CURRENT clean-host carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION
V19 -> NEEDS-REINTEGRATION, not immediate priority
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped RS-capacity boundary
V21 -> retain "protocol constraints before rate" only
Current E2E -> PASS, with visible-data determinism caveat
Paper bundle v7 -> PASS_WITH_REPRODUCIBILITY_BOUNDARY
```

Historical V18/V20 precise summaries remain retired unless recreated by current executable evidence.

## 7. Known unresolved issues, ordered by project value

1. **Fixed-seed visible carrier numerical determinism across independent runs is not achieved.** This is now directly relevant because paper figures/raw tables consume those values.
2. Cross-platform QR/eigh/sign basis determinism is the leading suspected technical locus and was already a known unresolved issue before paper-v7 exposed its artifact-level consequence.
3. Public locator-label stability is not proven across all package configurations.
4. Current NPZ locator is not proven robust to actual physical table deletion / changed table count.
5. V18 q=2 fallback remains unexercised.
6. Re-quantization alignment structure is not mechanistically modeled.
7. V20 has one RS geometry; 6.25% overhead is not shown minimal/optimal.
8. V19 is not current.
9. No universal undetectability/security or real-publication claim is supported.

## 8. Next work — system-level reproducibility, not another feature

Do **not** add more paper figures, another damage grid, a V19 selector, or a rate optimization pass yet.

The next high-value task is to make the current **visible carrier deterministic for the same seed across independent runs**, without changing A/B responsibilities or tuning q/delta/RS for performance.

Target:

```text
same seed + same current protocol
-> same semantic B
-> same numeric table arrays
-> same exported CSV values
-> stable figure inputs
-> exact recovery / locator / V20 gates remain intact
```

The first hypothesis to test is the numerical basis construction (`QR/eigh/sign`) rather than the paper renderer or payload RNG. Any fix must be validated by rerunning the existing V18/V20/current-E2E/paper-v7 gates; do not accept determinism at the cost of silently changing the audited protocol behavior.

AUDIT GATE: PASS — the whole technical-to-paper artifact exists and is traceable; cross-run visible-carrier determinism is now the highest-value system gap
