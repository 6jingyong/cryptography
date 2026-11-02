# Current end-to-end integration plan

Scope: **synthetic/mock benchmark only**.

This milestone is intentionally broader than another carrier stress test. Its purpose is to prove that the current repository is one coherent system rather than a collection of individually passing modules.

## Project-level objective

The target chain is:

```text
synthetic payload a
  -> current V18/V20 encode
  -> candidate package c with A-visible structure and per-package B
  -> mix c among synthetic background d records
  -> A ranks / bootstraps c without parsing B during ranking
  -> authenticated open
  -> B decodes b, optional V20 repair, exact a
  -> the same machine package/results feed the synthetic mock-paper renderer
  -> claim/label checks keep paper presentation downstream of machine evidence
```

The project is **not** optimized here for bit/value, parity overhead, or a larger damage envelope.

## Frozen configuration

Fresh technical seeds:

```text
901..908
```

Representative bundle seed:

```text
901
```

Per seed:

```text
payload_bytes = 512
channels = 2
corpus_size = 2000
near_decoy_fraction = 0.01
top_k = 100
carrier/reliability = current V18 + current fixed V20 geometry
```

No V18/V20 carrier, q, delta, locator, parity, shard, or integrity parameter may change in this milestone.

## Required machine outputs

The integration runner must emit one bundle containing at least:

```text
published_v20.npz
manifest_v20.json
candidate_c.json
collection_recipe.json
technical_summary.json
e5_current_v20.json
paper_v6_output/
bundle_manifest.json
```

`collection_recipe.json` is sufficient for the synthetic background collection: it must record deterministic corpus RNG, target index, corpus size, near-decoy fraction, and A-visible ranking result so the d population can be regenerated instead of storing thousands of redundant descriptors.

## Pass gate

The milestone passes only if:

1. all 8 seeds produce distinct payload hashes;
2. all 8 seeds recover the exact synthetic payload through current V20 open/recovery;
3. all 8 targets are inside Top-100;
4. representative target is found without parsing B during ranking;
5. representative decoy / tampered envelope is rejected;
6. `paper_v6.py` consumes the representative **current V20** numeric package and B manifest, not a historical V12 fixture;
7. paper E5 is completed from this milestone's 8-seed current-V20 result;
8. generated paper and manifest retain visible synthetic/mock labels and mandatory non-provenance limitation;
9. `bundle_manifest.json` hashes the machine and paper artifacts so the bundle is inspectable as one unit.

If the paper tool cannot consume the current V20 package/manifest without hand-editing package data, the milestone fails as an integration failure. Do not change the carrier or paper evidence to force a pass; fix only the interface/metadata contract if warranted.

## Explicit non-goals

This milestone does not claim or test:

```text
real confidential payload hiding
real-publication deployment
undetectability
cryptographic security of the numeric carrier
optimal bit/value
optimal parity overhead
universal locator robustness
```

A successful result means only that the current synthetic technical and paper pipelines form one reproducible end-to-end benchmark.