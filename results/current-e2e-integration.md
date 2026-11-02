# Current end-to-end integration — PASS

Scope: **synthetic/mock benchmark only**.

Frozen plan: `results/current-e2e-integration-plan.md`.

Source machine evidence:

```text
workflow run 41376173270
artifact 13111715465
artifact sha256 b1fe1167cf43704d394a62b33688e7c2f22b77a391a6c3e0a1915aa3de9a65f1
```

## Why this milestone exists

This is a project-level integration check, not another carrier stress test.

The current repository now exercises one coherent chain:

```text
synthetic a
-> current V18/V20 encode
-> candidate c mixed among synthetic d
-> A locator/bootstrap
-> authenticated open
-> B decode / optional V20 repair
-> exact a
-> same current numeric package + same machine result
-> paper_v6 synthetic mock-paper bundle
```

No q, delta, locator, parity, shard, or integrity parameter was changed for this milestone.

## Technical result

Fresh seeds `901..908`:

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
payload sha256:
  c9507550ad695236dae78c8a07cdff00ba4c140c331af0104314a81db93dd768

published NPZ sha256:
  6e7c1c1012119674d7030e84fc561bd7b1dbf972c337b8c89a598596d6360fdf

target index: 1734 / 2000
target rank: 1
target locator score: 1.0
near decoys: 20
explicit decoy: rejected
repair-field bitflip: rejected by V20 envelope integrity
```

The background collection is represented by a deterministic regeneration recipe rather than checking in thousands of redundant synthetic descriptors.

## Paper integration result

`tools/paper_v6.py` consumed the representative **current V20** numeric NPZ and current B manifest directly.

It did not use a historical V12 fixture.

The same current-V20 8-seed result completed paper E5:

```text
E5 status = COMPLETED
E5 pass   = true
exact recovery rate = 1.0
Recall@100 = 1.0
all payload hashes unique = true
```

Generated paper state:

```text
selected archetype:
  materials characterization / physical chemistry
story type:
  multi_regime_characterization
```

The paper retains both visible labels:

```text
MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS
SYNTHETIC BENCHMARK / SIMULATED DATA ONLY
```

and the mandatory limitation that field framing / generic fits are descriptive presentation choices rather than evidence of real provenance or physical mechanism.

## Bundle integrity

The uploaded integration bundle contains both technical and paper artifacts:

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

`bundle_manifest.json` covers 14 files excluding itself. Every recorded file size and SHA-256 was independently recomputed after downloading the CI artifact; mismatch count was **0**.

## Supported conclusion

The current technical and paper pipelines now form one reproducible synthetic benchmark path. The paper layer can consume a current V20 package and current multi-seed machine evidence without hand-editing carrier data or substituting a historical fixture.

This is the important project-level result: the repository is no longer only a collection of separately passing carrier, locator, reliability, and paper components.

## Not supported

This milestone does not support claims of:

```text
real confidential payload hiding
real-publication deployment
undetectability
cryptographic security of the numeric carrier
optimal bit/value or parity overhead
universal locator/publication robustness
real provenance or scientific mechanism
```

## Next priority

Do not immediately add another V-number or another damage grid.

The next work should improve the **whole artifact** and close remaining system-level gaps. In particular, the paper side is now the thinner half of the integrated system: it produces a correctly gated Markdown mock paper and analysis JSON, but not yet a polished multi-figure paper-shaped package derived from the same current carrier data.

That is a higher-value next milestone than further tuning V18/V20 numeric robustness.
