# cryptography

Synthetic-only research on structured numeric carriers, locator protocols, package reliability, and clearly labeled paper-shaped benchmark reporting.

> **This repository is a synthetic/mock benchmark. It does not claim real experimental evidence and is not intended for hiding real confidential material in real scientific publications.**

## What this project is actually trying to prove

The project-level question is not “how many bits can one curve carry?” and it is not “how much noise can one QIM setting survive?”.

The target is one coherent system:

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

Package-specific q, transform, geometry, ECC, host model, payload length, publication parameters, shard size, and parity geometry belong in `B`, not long-lived `A`.

Priority:

```text
find c
> open / authenticate c
> interpret B
> recover exact a
> traceable presentation
> only then optimize capacity / rate / overhead
```

See [`protocol/README.md`](protocol/README.md).

## Current project-level integration

Current runner:

```text
tools/current_end_to_end.py
```

Frozen seeds `901..908` use the current V18 carrier + current bounded V20 reliability layer, a 2,000-candidate synthetic corpus, and the current paper analysis pipeline.

Machine result:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

The representative current V20 package is passed directly to the paper layer. Paper E5 is completed from the **same current-V20 8-seed result**, not a historical V12 fixture.

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
| V18 | current bounded host-aware modulo-QIM carrier on sender-observed residual hosts |
| V20 | current bounded logical outer-reliability layer with fixed RS geometry |
| Paper v6/v7 | machine-results-first analysis, claim gate, multi-figure/raw-data paper bundle |
| Current E2E | one current V20 technical package feeds recovery and the paper pipeline |

## V18 — useful result and explicit rejection

V18 was rebuilt rather than restoring old unauditable summaries.

Current evidence includes:

```text
smooth residual host: current-protocol exact recovery
five frozen sender-observed residual families: pass
paired additive-noise transition: measured over 24 seeds
re-quantization: alignment-dependent / non-monotonic
transition-region residual errors: sparse after inner Hamming correction
```

A broad “publication robust” claim is **rejected**. The useful result is an explicit measured operating envelope and a known sparse failure structure.

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

Independent audit confirmed:

```text
Figure 2 rule selection: exact
Figure 3 matched-fit values: exact vs machine analysis
Figure 3 linear baselines: exact when recomputed from same current curves
Figure 4: same current-V20 E5 used by paper E5
nested manifest mismatch count: 0
final complete manifest mismatch count: 0
```

Status:

```text
PASS_WITH_REPRODUCIBILITY_BOUNDARY
```

See:

- [`results/paper-bundle-v7-plan.md`](results/paper-bundle-v7-plan.md)
- [`results/paper-bundle-v7.json`](results/paper-bundle-v7.json)
- [`results/paper-bundle-v7.md`](results/paper-bundle-v7.md)

The paper bundle remains visibly labeled as synthetic/mock, and generic fits / morphology framing remain presentation choices rather than provenance or mechanism evidence.

## Important current system boundary: fixed-seed visible data are not yet numerically deterministic

Two independent successful fresh CI runs with the same frozen seeds preserved:

```text
representative payload SHA-256
current-V20 E5 hash/result
morphology representative selection
presentation archetype
story type
```

but differed in:

```text
current NPZ hash
current B manifest hash
visible response values in 8 / 12 tables
```

Thus the current system is fully traceable **within each generated artifact**, but it does not yet guarantee numerically identical visible carrier data for the same seed across independent runs.

This makes the previously known numerical basis-determinism issue (`QR/eigh/sign`) the next project-level reproducibility priority rather than a low-level footnote.

## Current status

```text
V12 -> CURRENT clean-host carrier
V18 -> CURRENT_BOUNDED_REINTEGRATION
V19 -> NEEDS-REINTEGRATION, but not immediate priority
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped capacity-aligned failure envelope
V21 -> retain "protocol constraints before rate" principle only; old quantitative results stale
Current E2E -> PASS, with cross-run visible-data determinism caveat
Paper bundle v7 -> PASS_WITH_REPRODUCIBILITY_BOUNDARY
```

## Next priority

Do **not** add more figures, another dense damage grid, tune parity, or optimize bit/value next.

The next high-value system task is:

```text
same seed + same current protocol
-> same semantic B
-> same numeric table arrays
-> same exported CSV values
-> stable figure inputs
while locator / exact recovery / V20 gates remain intact
```

The first technical hypothesis is deterministic basis construction, not paper selection or payload RNG.

## Run the current integration

```bash
python -m pip install -r requirements.txt
python tools/current_end_to_end.py \
  --v20 protocol/real-package-v20.py \
  --engine src/noisy_host_package_v18.py \
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
