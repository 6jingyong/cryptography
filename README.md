# cryptography

Synthetic-only research on structured numeric carriers, locator protocols, package reliability, reproducibility, and clearly labeled paper-shaped benchmark reporting.

> **This repository is a synthetic/mock benchmark. It does not claim real experimental evidence and is not intended for hiding real confidential material in real scientific publications.**

## What this project is actually trying to prove

The project-level question is not “how many bits can one curve carry?” or “how much noise can one QIM setting survive?”. The target is one coherent system:

```text
synthetic payload a
    ↓
encode into numeric representation b
    ↓
create per-package reconstruction/reliability manifest B
    ↓
construct candidate package c
    ↓
mix c among unrelated synthetic public/background records d
    ↓
pre-shared root codebook A locates / bootstraps c
    ↓
authenticated open
    ↓
B explains b; optional reliability data r repairs bounded sparse damage
    ↓
recover exact a
    ↓
feed the same current machine package/results into a clearly labeled, traceable mock-paper bundle
```

Core separation:

```text
A = long-lived locator / canonicalization / bootstrap root
B = per-package reconstruction + reliability manifest
b = processed numeric payload representation
r = optional authenticated/masked repair data
c = discoverable public candidate package
d = unrelated public/background record
a = final synthetic payload
```

Package-specific q, transform, geometry, ECC, host model, payload length, publication parameters, basis version, shard size, and parity geometry belong in `B`, not long-lived `A`.

Priority:

```text
find c
> open / authenticate c
> interpret B
> recover exact a
> reproducible machine evidence
> traceable presentation
> only then optimize capacity / rate / overhead
```

See [`protocol/README.md`](protocol/README.md).

## Current engine and reproducibility milestone

The current V18 carrier engine is:

```text
src/noisy_host_package_v18_deterministic.py
```

The previous engine remains as a legacy baseline:

```text
src/noisy_host_package_v18.py
```

Current basis contract:

```text
deterministic-dct-mgs-v1
```

It is explicit B state. The current decoder rejects a package declaring another basis version.

The deterministic engine passed the frozen promotion gates in [`results/deterministic-basis-v1.md`](results/deterministic-basis-v1.md):

```text
Gate A: 8/8 exact current E2E, Recall@20=1, Recall@100=1, paper-v7 PASS
Gate B: two independent CI runners, exact semantic equality, mismatch_count=0
Gate C: existing V18/V20 bounded evidence passes with no q/delta/RS retuning
```

Gate B compares canonical B, all x/y float64 table arrays, all exported CSVs, current-V20 E5, paper-v7 numeric figure plan, morphology selection, and presentation archetype/story. The final semantic authority SHA-256 was identical across both runners.

This resolves the earlier fixed-seed visible-carrier reproducibility blocker **within the declared independent GitHub Actions environment**. It is not a universal claim of bit-identical behavior across every CPU/libm/NumPy/Python implementation.

## Current project-level integration

Current runner:

```text
tools/current_end_to_end.py
```

Frozen seeds `901..908` use the deterministic current V18 carrier + bounded V20 reliability layer, a 2,000-candidate synthetic corpus, and the current paper analysis pipeline.

Machine result:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

The representative current V20 package is passed directly to the paper layer. Paper E5 is completed from the **same current-V20 8-seed result**, not a historical fixture.

See:

- [`results/current-e2e-integration-plan.md`](results/current-e2e-integration-plan.md)
- [`results/current-e2e-integration.json`](results/current-e2e-integration.json)
- [`results/current-e2e-integration.md`](results/current-e2e-integration.md)

## Current technical spine

| Layer | Current meaning |
|---|---|
| V12 | clean-host adaptive-q carrier for processed payload `b` |
| V16 | historical A-layer labeled locator / erasure research |
| V17 | historical publication/canonicalization observations, responsibilities remapped |
| Protocol v3 | A-layer fingerprint bound to actual public NPZ structure; locator does not parse B before ranking |
| Structural v4 | explicit synthetic locator stress model with visible heavy-damage boundary |
| V18 deterministic | current bounded host-aware modulo-QIM carrier; deterministic DCT-II + fixed-order MGS basis |
| V20 | current bounded logical outer-reliability layer with fixed RS geometry |
| Paper v6/v7 | machine-results-first analysis, claim gate, multi-figure/raw-data paper bundle |
| Current E2E | one current V20 technical package feeds recovery and the paper pipeline |

## V18 — bounded carrier, not universal publication robustness

Current evidence includes:

```text
smooth residual host: current-protocol exact recovery
five frozen sender-observed residual families: pass
paired additive-noise transition: measured over 24 seeds
re-quantization: alignment-dependent / non-monotonic
transition-region residual errors: sparse after inner Hamming correction
```

A broad “publication robust” claim remains **rejected**. The useful result is an explicit measured operating envelope and a known sparse failure structure.

See [`results/v18-publication-statistics.json`](results/v18-publication-statistics.json) and [`results/v18-error-profile.json`](results/v18-error-profile.json).

## V20 — bounded reliability, not magic robustness

Current fixed geometry:

```text
payload                 512 bytes
RS data shards           4 x 128 bytes
parity per shard         8 bytes
RS correction bound      <=4 byte errors / shard
parity total             32 bytes
payload parity overhead  6.25%
```

The first frozen 24-seed matrix passed all six damaged conditions with 49/49 repair attempts successful.

A stronger fresh-seed envelope held the geometry fixed. Every tested V20 failure coincided exactly with at least one shard exceeding the declared four-byte RS correction capacity; mismatch count was zero. Locator score remained 1.0 throughout.

This supports a bounded reliability claim, not universal post-seal robustness and not optimality of 6.25% overhead.

See:

- [`results/v20-bounded-reintegration.json`](results/v20-bounded-reintegration.json)
- [`results/v20-failure-envelope.json`](results/v20-failure-envelope.json)

## Paper bundle v7

The paper layer is downstream of machine evidence:

```text
current machine package/results
    ↓
morphology analysis
    ↓
narrative archetype
    ↓
generic descriptive fits
    ↓
claim / experiment gate
    ↓
actual SVG figures + raw CSV tables
    ↓
claim/data/figure traceability
    ↓
clearly labeled mock-paper bundle
```

Current implementation:

```text
tools/paper_v6.py
tools/paper_bundle_v7.py
tools/finalize_paper_bundle_v7.py
```

Paper-v7 produces from the same fresh current V20 bundle:

```text
4 SVG figures
12 per-table raw-data CSV files
figure/data manifests
C1/C2/C4/C5 traceability
paper_v7.md
validation result
complete final bundle manifest
```

Frozen rule-selected morphology examples:

```text
bell_peak  -> table 7
linear     -> table 11
periodic   -> table 9
saturating -> table 1
```

The earlier paper-v7 cross-run boundary is now resolved for the declared CI environment. The final 1e-16-level drift was traced to `np.polyfit` in the Figure 3 linear baseline and replaced with fixed-order analytic regression plus `math.fsum` R² calculation.

The paper bundle remains visibly labeled as synthetic/mock, and generic fits / morphology framing remain presentation choices rather than provenance or mechanism evidence.

## Current status

```text
V12 -> CURRENT clean-host carrier
V18 deterministic -> CURRENT_BOUNDED_REINTEGRATION + CI semantic determinism PASS
V19 -> NEEDS-REINTEGRATION, not immediate priority
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped capacity-aligned failure envelope
V21 -> retain "protocol constraints before rate" principle only; old quantitative results stale
Current E2E -> PASS
Paper bundle v7 -> PASS
Deterministic basis v1 -> PROMOTION_GATES_PASS
```

## Next priority

Do **not** return immediately to dense noise grids, parity tuning, or bit/value optimization.

The main technical/paper path is now coherent and reproducible in the declared CI environment. The next high-value work should be chosen by what improves the complete system, for example actual physical-structure loss behavior (table deletion/truncation) if it blocks realistic package handling, or broader paper/package usability if presentation is the limiting side. V19 should only be rebuilt when multiple genuinely current carrier modes exist and a selector has something meaningful to choose between.

## Run the current integration

```bash
python -m pip install -r requirements.txt
python tools/current_end_to_end.py \
  --v20 protocol/real-package-v20.py \
  --engine src/noisy_host_package_v18_deterministic.py \
  --paper-tool tools/paper_v6.py \
  --seeds 901,902,903,904,905,906,907,908 \
  --representative-seed 901 \
  --payload-bytes 512 \
  --channels 2 \
  --corpus-size 2000 \
  --near-decoy-fraction 0.01 \
  --top-k 100 \
  --out-dir /tmp/current-e2e-bundle
```

For broader audit state, see [`HANDOFF.md`](HANDOFF.md) and [`results/current-summary.json`](results/current-summary.json).

## Scope

Allowed repository use:

```text
synthetic payloads
synthetic candidate corpora
numeric carrier benchmarks
locator robustness
publication-transform robustness
machine-verifiable recovery
clearly labeled mock-paper generation
```

Not represented by this repository:

```text
real experimental evidence
real confidential payload hiding
real-paper covert deployment
claims of universal undetectability
claims of cryptographic security for the numeric carrier itself
```

MIT licensed.
