# HANDOFF — audited project state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative. Historical prose and legacy V18–V21 numbers are not.

## 1. Project orientation

Do not treat this project as a sequence of carrier-parameter competitions.

```text
synthetic payload a
-> numeric b
-> per-package B (+ optional repair r)
-> candidate c mixed among unrelated synthetic d
-> long-lived A locates / bootstraps c without parsing B during ranking
-> authenticated open
-> B explains b; optional V20 repair
-> exact a
-> same current machine package/results feed a clearly labeled mock-paper bundle
```

```text
A = long-lived locator / canonicalization / bootstrap root
B = per-package reconstruction + reliability manifest
```

Package-specific q, transform, geometry, ECC, host model, publication parameters, **basis version**, shard size, parity geometry, etc. belong in B, not A.

Priority:

```text
find c > open/authenticate c > interpret B > exact a > reproducible evidence > traceable presentation > rate/overhead optimization
```

## 2. Current engine — deterministic V18 promoted

Current engine:

```text
src/noisy_host_package_v18_deterministic.py
basis_version = deterministic-dct-mgs-v1
```

Legacy baseline retained:

```text
src/noisy_host_package_v18.py
```

The deterministic engine replaces the old QR/eigh free-basis path with fixed-order DCT-II candidates + two-pass modified Gram-Schmidt and fixed-order scalar reductions. The basis version is explicit B state; the decoder rejects a mismatched declared basis version.

Frozen promotion gates all pass:

```text
Gate A — protocol viability
8 / 8 unique payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median/max target rank = 1 / 1
paper-v7 = PASS

Gate B — independent-run semantic determinism
two independent GitHub Actions runners
semantic_equal = true
mismatch_count = 0
raw NPZ container hash equal = true

Gate C — bounded evidence regression
V18 core / residual matrix / publication statistics / error profile = PASS
V20 bounded matrix / fixed-geometry failure envelope = PASS
q / delta / RS geometry were not retuned
```

Gate B compares canonical B, all x/y float64 arrays, all CSVs, current E5, paper-v7 numeric figure plan, morphology selection, and archetype/story.

Evidence:

```text
results/deterministic-basis-v1-plan.md
results/deterministic-basis-v1.json
results/deterministic-basis-v1.md
```

Boundary: exact semantic reproducibility is established across the declared independent GitHub Actions environment for the frozen configuration. This is not a universal every-CPU/libm/NumPy/Python bit-identity claim.

## 3. Current integrated technical path

Current runner:

```text
tools/current_end_to_end.py
```

Current workflows use the deterministic V18 engine + bounded V20 layer.

Frozen seeds `901..908`, representative seed `901`, payload 512 B, channels 2, 2,000-candidate corpus, Top-100:

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

## 4. V18 state

Status: **CURRENT_BOUNDED_REINTEGRATION + DECLARED-CI DETERMINISM PASS**.

Current evidence supports:

```text
smooth reference: 8/8 exact
five frozen sender-observed residual families: pass
q=4 selected for all tested tables; q=2 fallback unexercised
```

Broad V18 publication robustness remains **REJECTED**.

24-seed paired additive-noise result from the audited bounded evidence:

```text
0.08..0.12 delta : 24/24
0.13             : 23/24
0.14             : 20/24
0.15             : 16/24
0.16             :  9/24
0.17             :  4/24
0.18             :  1/24
```

Re-quantization remains alignment-dependent and non-monotonic; no scalar threshold claim. Transition failures remain sparse after inner Hamming correction.

Gate C re-established the bounded V18 conclusions under the deterministic engine without retuning. Do not imply every historical floating-point statistic is byte-for-byte unchanged unless separately checked.

## 5. V20 state

Status: **CURRENT_BOUNDED_REINTEGRATION**.

```text
payload                  512 bytes
RS data shards            4 x 128 bytes
parity / shard            8 bytes
RS byte-error bound       <=4 bytes per shard
parity total              32 bytes
payload parity overhead   6.25%
```

Integrity:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw numeric b is not in the V20 envelope tag. Final acceptance requires exact SHA-256 equality to the authenticated target in B.

Initial frozen gate: clean + six damaged conditions pass 24/24 each after V20, with 49/49 attempted repairs successful.

Stronger fixed-geometry envelope:

```text
V20 failure <=> at least one 128-byte shard has >4 candidate byte errors
```

Mismatch count: **0** in the tested stronger grid. Locator remained score 1.0. Gate C revalidated this bounded conclusion with the deterministic engine.

## 6. Paper bundle v7

Implementation:

```text
tools/paper_v6.py
tools/paper_bundle_v7.py
tools/finalize_paper_bundle_v7.py
```

Paper-v7 produces:

```text
4 SVG figures
12 raw-data CSV files
figure/data manifests
claim traceability
paper_v7.md
validation result
complete final bundle manifest
```

Frozen figure roles:

```text
F1 -> all visible current response curves
F2 -> highest-confidence example per non-other morphology
F3 -> morphology-matched descriptive fit vs same-curve linear baseline
F4 -> same current-V20 E5 result used by paper E5
```

Selected examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

The earlier paper-v7 reproducibility caveat is resolved in the declared CI environment. The last remaining ~1e-16 paper-plan mismatch came from `np.polyfit`; Figure 3 now uses fixed-order analytic one-variable regression plus `math.fsum` R². No carrier parameter changed for that repair.

Paper-v7 remains visibly synthetic/mock, and descriptive fits/morphology framing are not provenance or mechanism evidence.

## 7. Current classification

```text
V12 -> CURRENT clean-host carrier
V16 -> HISTORICAL-BUT-VALID A-layer benchmark
V17 -> HISTORICAL-BUT-VALID observations; responsibilities remapped
V18 deterministic -> CURRENT_BOUNDED_REINTEGRATION + declared-CI determinism PASS
V19 -> NEEDS-REINTEGRATION, not immediate priority
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped RS-capacity boundary
V21 -> retain "protocol constraints before rate" only
Current E2E -> PASS
Paper bundle v7 -> PASS
Deterministic basis v1 -> PROMOTION_GATES_PASS
```

## 8. Known unresolved issues, ordered by project value

1. Public locator-label stability is not proven across all package configurations.
2. Structural-v4 is descriptor-level only; the current NPZ path is not proven robust to **actual physical table deletion / changed table count / truncation**.
3. V18 q=2 fallback remains unexercised.
4. Re-quantization alignment structure is measured but not mechanistically modeled.
5. V20 has one RS geometry; 6.25% overhead is not shown minimal or optimal.
6. Physical structural-damage behavior is not comprehensively characterized.
7. V19 is not current; a selector remains low value while there is only one primary current carrier path.
8. Exact semantic identity outside the declared CI environment is not proven.
9. No universal undetectability/security or real-publication claim is supported.

## 9. Next work — return to the whole system

Do **not** keep optimizing deterministic floating-point details now that the declared-CI reproducibility gate is solved. Do not immediately tune q/delta/RS or add dense noise-grid points either.

The next technical question with the highest whole-system value is whether **real package structure damage** breaks A/locator, NPZ parsing, inner decoding, or V20 repair first. A small frozen experiment using actual table deletion/truncation/shape-preserving local burst would close a gap that descriptor-level Structural-v4 cannot answer.

That work should remain layer-aware:

```text
A/locator failure
vs b/NPZ parse failure
vs candidate payload error
vs V20 repair capacity
vs authenticated B/r rejection
```

If structural testing shows the dominant failure is A or parser structure, fix that layer rather than adding more RS parity. If the complete system does not need this immediately, prioritize integrated package usability instead. V19 should wait until multiple genuinely current carrier modes exist.

AUDIT GATE: PASS — the current technical-to-paper path is integrated and semantically deterministic across the declared independent CI environment; next priority returns to whole-system structural/package gaps, not floating-point micro-optimization.
