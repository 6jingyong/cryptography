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
B explains b; optional reliability data r repairs sparse damage
    ↓
recover exact a
    ↓
feed the same machine package/results into a clearly labeled mock-paper renderer
```

The core separation is:

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

The optimization priority is therefore:

```text
find c
> open / authenticate c
> interpret B
> recover exact a
> only then optimize capacity / rate / overhead
```

See [`protocol/README.md`](protocol/README.md).

## Current project-level integration milestone

The repository now has a current end-to-end integration runner:

```text
tools/current_end_to_end.py
```

Frozen fresh seeds `901..908` use the current V18 carrier + current bounded V20 reliability layer, a 2,000-candidate synthetic corpus, and the current `paper_v6.py` renderer.

Machine result:

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

The representative current V20 package is then passed directly to `tools/paper_v6.py`. Paper E5 is completed from the **same current-V20 8-seed result**, not a historical V12 fixture.

The generated bundle contains:

```text
published_v20.npz
manifest_v20.json
candidate_c.json
collection_recipe.json
technical_summary.json
e5_current_v20.json
integration_result.json
paper_v6_output/*
bundle_manifest.json
```

The bundle keeps visible mock/synthetic labels and the mandatory limitation that narrative framing and descriptive fits are not evidence of real provenance or physical mechanism. Its per-file SHA-256 manifest was independently recomputed with zero mismatches.

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
| Paper v6/v7 | machine-results-first mock-paper renderer + bounded claim gate |
| Current E2E | one current V20 technical package feeds both recovery and mock-paper generation |

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

A broad “publication robust” claim is **rejected**. The point of the V18 work is not that the carrier survives everything; it is that the current channel has an explicit, measured operating envelope and a known sparse failure structure.

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

A stronger fresh-seed envelope then held the geometry fixed. Every tested V20 failure coincided exactly with at least one shard exceeding the declared four-byte RS correction capacity; mismatch count was zero. Locator score remained 1.0 throughout.

This supports a bounded reliability claim, not universal post-seal robustness and not optimality of 6.25% overhead.

See:

- [`results/v20-bounded-reintegration.json`](results/v20-bounded-reintegration.json)
- [`results/v20-failure-envelope.json`](results/v20-failure-envelope.json)

## Paper line

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
clearly labeled mock paper
```

It may choose presentation style, terminology, section order, and descriptive fits. It may not invent benchmark numbers, turn requested work into completed evidence, claim real provenance, or turn high R² into mechanism proof.

The current integration milestone confirms that the paper renderer can consume a **current V20 package and current V20 multi-seed result directly**.

The next high-value paper milestone is therefore not another carrier tweak; it is a more complete **multi-figure paper-shaped bundle** generated from the same current carrier data while retaining explicit synthetic/mock labeling and machine-backed claims.

## Current status

```text
V12 -> CURRENT clean-host carrier
V18 -> CURRENT_BOUNDED_REINTEGRATION
V19 -> NEEDS-REINTEGRATION, but not immediate priority while one integrated current mode is primary
V20 -> CURRENT_BOUNDED_REINTEGRATION with mapped capacity-aligned failure envelope
V21 -> retain "protocol constraints before rate" principle only; old quantitative results stale
Current E2E -> PASS
```

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

For the broader audit suite, see [`HANDOFF.md`](HANDOFF.md) and [`results/current-summary.json`](results/current-summary.json).

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
