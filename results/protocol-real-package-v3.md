# Protocol v3 — fingerprint bound to actual published package structure

## Conclusion

Protocol v3 removes the extra synthetic fingerprint slots used by the v2 harness.
The A-layer locator now reads public structure from the actual published V12 NPZ package.

Current public table class:

```text
(numeric morphology class, local x-grid length)
```

For the 12-table V12 profile those classes are unique. A contains a long-lived root key that defines a permutation over the candidate package's canonical public table classes. The sender renumbers public table IDs so the actual NPZ structure follows that keyed permutation; B carries the corresponding concrete table IDs and decode metadata.

Therefore the roles remain separated:

```text
A -> says how public table structure should be ordered / recognized
B -> says how each concrete table should be decoded
```

No B field is read by the locator.

## Multi-seed full re-encode E5

The V12 benchmark engine was loaded once per run and its actual `run_package.__globals__["synthetic_payload"]` function was replaced with a seed-specific synthetic payload generator. This produces genuinely different `a`, then reruns the full V12 encode for each seed.

A first attempted implementation patched only the mapping returned by `runpy`; all SHA-256 values remained identical, so that run was rejected. The final implementation patches the callable's real global namespace and was accepted only after every seed produced a unique payload hash.

Final synthetic E5 configuration:

```text
seeds              = 8
payload             = 512 bytes / seed
channels            = 2
candidate corpus    = 2,000 / seed
near-decoy fraction = 1%
Top-K               = 100
fingerprint source  = actual NPZ public structure
```

Results:

| metric | result |
|---|---:|
| unique payload hashes | **8 / 8** |
| exact recovery | **8 / 8** |
| Recall@20 | **100%** |
| Recall@100 | **100%** |
| median target rank | **1** |
| maximum target rank | **1** |
| median locator score | **1.0** |

## What the fingerprint is now

The target fingerprint is no longer an extra `structure` dictionary attached to c.
It is encoded in the ordering / public IDs of real V12 tables whose classes are observable from the NPZ itself.

The receiver:

```text
published NPZ b
    ↓
extract public table morphology + x-grid length
    ↓
canonicalize class set
    ↓
convert observed public order to canonical ranks
    ↓
compare against A-keyed permutation
```

The strict outer integrity check still decides whether a candidate is a valid c.

## Important limitations

1. Background `d` records in this benchmark are structural descriptor surrogates, not 2,000 fully encoded NPZ packages. The target c is a real encoded NPZ; decoys model locator structure only.
2. The current keyed fingerprint uses public table renumbering/order as the controllable structural degree of freedom. Robustness to software that destroys table identity/order must be benchmarked separately.
3. The public morphology classifier is intentionally simple and synthetic. It is not a scientific provenance classifier.
4. The multi-seed run was executed against the standalone-equivalent V12 engine used in local development. The repository split launcher uses the same global-exec design, but a repository CI run should be added later rather than silently assumed.

These limitations are preferable to claiming the locator problem is solved.

**SYNTHETIC BENCHMARK — NOT REAL EXPERIMENTAL RESULTS**
