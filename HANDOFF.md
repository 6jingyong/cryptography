# HANDOFF — audited protocol state

Repository: `6jingyong/cryptography`  
Scope: **synthetic/mock benchmark only**

Current code, checked-in machine results, and reproducible CI are authoritative; historical prose is not.

## 1. Authoritative lifecycle

```text
pre-shared root codebook A
        ↓
find / rank candidate package c
        ↓
open / verify c
        ↓
extract B + b
        ↓
B explains b
        ↓
recover synthetic payload a
```

```text
A = long-lived locator / canonicalization / bootstrap protocol
B = per-package reconstruction codebook / manifest
b = processed payload representation
c = candidate package containing public fingerprint structure + B + b + integrity
a = final synthetic payload
d = unrelated public/background record
```

Hard invariant: package-specific q, transform, geometry, ECC, host model, payload length, padding, publication parameters, and decoder parameters belong in `B`, not long-lived `A`.

## 2. Protocol-v3 locator independence

Primary locator implementation: `protocol/real-package-v3.py`.

The locator derives its score from:

```text
A + public NPZ structure
```

using public morphology class + local x-grid length and A-keyed table ordering. Candidate ranking does **not** parse B. B is parsed only after a candidate is opened/verified.

Status: **PASS**.

## 3. Clean-host V12 E5

Authoritative result: `results/e5-multiseed-final.json`.

```text
8 seeded full re-encodes
8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
```

The audit CI additionally reruns fresh repository seeds 101 and 102 under Python 3.12. Both recover exactly at rank 1 and produce different payload hashes.

Status: **PASS for tested clean-host V12 nominal path only**.

## 4. A-layer structural robustness v4 — audited rebuild

Files:

```text
protocol/locator-structural-v4.py
results/locator-structural-v4.json
results/locator-structural-v4.md
```

Explicit model:

```text
12 stable labels
1,000,000 candidates
10,000 rank trials
1% strong near-decoys = 10,000 candidates
near-decoys have exactly 6 / 12 correct label→ID pairs
random decoys are uniform random permutations of 12 IDs
score = correct A-defined pairs / fixed 12-label contract
ties count fully ahead
```

Audited results:

```text
baseline: R@20=1.0000, R@100=1.0000, median rank=1
physical reorder after label canonicalization: R@100=1.0000
labeled split/merge after logical canonicalization: R@100=1.0000
25% deletion: R@100=1.0000, median rank=2
50% deletion: R@1000=0, median rank=10589
20% substitution: R@20=0.9283, R@100=0.9793, R@1000=0.9812, median rank=1
50% deletion + 20% substitution: R@1000=0, median rank=13640
```

The old handoff values for 50% deletion were wrong and are retired.

Important boundary: v4 is a **synthetic descriptor-level A-layer retrieval model**. It does not prove that the current NPZ parser survives actual table deletion or changed physical table count.

## 5. V18 noisy-host reintegration — bounded current result

Implementation:

```text
src/noisy_host_package_v18.py
protocol/real-package-v18.py
results/v18-reintegration-plan.md
results/noisy-host-v18-reintegration.json
results/noisy-host-v18-reintegration.md
.github/workflows/v18-reintegration.yml
```

The first-pass hypothesis and refusal rule were frozen before results. The carrier generates a non-zero smooth residual host in the free subspace **before** embedding, then uses host-aware modulo-QIM to move coefficients to the nearest payload coset. `q=4` is attempted first and `q=2` is allowed only as a fallback if q=4 fails the declared table distortion budget.

Current fixed-model result:

```text
12 / 12 tables selected q=4
0 / 12 tables selected q=2
all selected-table calibration exact block recovery = 1.0
calibration host-adjustment NRMSE range ~= 0.000720 .. 0.001093
strictest declared table budget = 0.0045
```

Full current-protocol run, seeds 101–108:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
maximum target rank = 2
all V18 package-specific state present in B = yes
```

Host-change magnitude:

```text
median embedding-adjustment RMS / host-residual RMS ~= 0.446
maximum observed ratio                              ~= 0.485
```

The fixed 512-byte single-seed run had gross rate about `0.1134 payload bit / published numeric value`. This was recorded, not optimized.

Status: **CURRENT_BOUNDED_REINTEGRATION**.

Accepted claim:

> Under the frozen synthetic smooth-residual host model, host-aware modulo-QIM is viable in the current `A -> c -> B -> b -> a` lifecycle for the tested seeds.

Not restored / not proved:

```text
old V18 59/60 or 57-q4/2-q2/1-unresolved numbers
q=2 fallback effectiveness
other residual distributions
rate optimality
undetectability / cryptographic security
real-publication deployment
```

Seed 101 ranked the real package second; the rank-1 decoy failed strict verification and the real package opened at rank 2. This is expected protocol behavior and is another reason not to equate locator success with unique rank 1.

## 6. Paper line / claim gate v7

Executable presentation pipeline: `tools/paper_v6.py`  
Claim gate: `tools/paper_claim_gate_v7.py`  
Recorded audit: `results/paper-claim-audit-v7.json` and `.md`

All bounded claim roles C1–C6 pass. C5 remains mandatory: descriptive field framing/fits are not provenance or mechanism evidence. C6 remains limited to the explicit descriptor-v4 model.

Never upgrade:

```text
domain archetype -> real provenance
high R² -> proven physical mechanism
synthetic locator benchmark -> universal undetectability/security
requested experiment -> completed evidence
descriptor-level v4 canonicalization -> current NPZ deletion/split-merge support
bounded V18 smooth-host result -> general noisy-host robustness
```

## 7. Historical V12–V21 classification

```text
V12 -> CURRENT / clean-host b carrier; package-specific settings in B
V16 -> HISTORICAL-BUT-VALID A-layer benchmark; old "second codebook" wording is stale
V17 -> HISTORICAL-BUT-VALID observations; A/c/B responsibilities remapped
V18 -> CURRENT_BOUNDED_REINTEGRATION for the new smooth-host implementation; old quantitative summary retired
V19 -> NEEDS-REINTEGRATION; sender policy for choosing (b,B)
V20 -> NEEDS-REINTEGRATION; outer reliability in b/c, concrete parameters in B
V21 -> HISTORICAL-BUT-VALID principle only: protocol constraints before rate; old quantitative results STALE
```

Old precise V18–V20 summaries remain non-authoritative. The new V18 result does not retroactively validate the old V18 numbers.

## 8. Known unresolved issues

1. Public label stability is not proven across all package configurations.
2. Current NPZ locator is not proven robust to actual physical table deletion or changed table count.
3. The 12-label descriptor model has a sharp failure boundary when the target falls to six or fewer correct pairs against 10,000 exact-six near-decoys.
4. 20% locator substitution has a catastrophic tail even though median rank remains 1.
5. Cross-platform deterministic basis generation remains unresolved; NumPy QR/eigh/sign behavior is not proven bit-identical across platforms.
6. V18 is tested only on the frozen smooth synthetic residual-host model.
7. V18 q=2 fallback was not exercised because all 12 tables passed q=4.
8. V18 embedding adjustment is material (~44–49% of host-residual RMS), so feasibility must not be restated as invisibility.
9. V19 and V20 still need protocol-level reintegration and fresh machine results.
10. No universal undetectability/security claim is supported.
11. No real-publication deployment is in scope.

## 9. Reproducible gates

Core audit:

```bash
python tools/audit_current.py
python protocol/locator-structural-v4.py --json-out /tmp/v4.json --md-out /tmp/v4.md
python tools/paper_claim_gate_v7.py --v4-result /tmp/v4.json --json-out /tmp/claims.json --md-out /tmp/claims.md
```

V18:

```bash
python src/noisy_host_package_v18.py --seed 101 --payload-bytes 512 --channels 2 --out-dir /tmp/v18-single
python protocol/real-package-v18.py \
  --engine src/noisy_host_package_v18.py \
  --seeds 101,102,103,104,105,106,107,108 \
  --payload-bytes 512 --channels 2 --corpus-size 2000 --top-k 100 \
  --out /tmp/v18-protocol-result.json
```

GitHub Actions workflows run both sets of checks on pull requests.

## 10. Current gate status

```text
A/B terminology                         PASS
locator independence                    PASS
clean-host V12 E5                       PASS
structural v4 model/results             PASS
Paper-v7 bounded claim gate             PASS
V18 fixed-model calibration             PASS
V18 current-protocol 8-seed recovery    PASS
V18 old quantitative-summary recovery   REJECTED / NOT ATTEMPTED
V19                                     NEEDS-REINTEGRATION
V20                                     NEEDS-REINTEGRATION
```

## 11. Next work

Do **not** return to bit/value optimization first and do not build V19 around a single convenient residual distribution yet.

The highest-value next step is a frozen **V18 residual-model matrix** with no post-result rescue sweep:

```text
iid Gaussian
heteroscedastic Gaussian
AR(1)-like correlated residual
batch / low-frequency drift
Gaussian + sparse outliers
```

The question is whether the same host-aware carrier remains viable across materially different synthetic residual structures. If not, V18 remains a model-specific mode and V19 must learn/select among explicitly supported host regimes rather than treating V18 as a general noisy-host default.

AUDIT GATE: PASS — safe to continue bounded development
