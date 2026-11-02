# Structural parity current integration

Status: **WHOLE-SYSTEM VIABILITY PASS / DETERMINISM RECHECK PENDING**

Scope: synthetic/mock benchmark only.

This gate tested whether the passing structural-parity-v3 candidate could rejoin the already-audited technical + paper pipeline **without changing the carrier, V20 geometry, paper-v6, or paper-v7**.

## Frozen stack

```text
A-v4-erasure-xlen
+ 11 data tables + 1 XOR structural-parity table
+ deterministic-dct-mgs-v1 V18
+ unchanged V20: 4 x 128 B + 8 parity B/shard
-> current-style E2E
-> unchanged paper-v6
-> unchanged paper-v7
```

Fresh seeds: `1301..1308`, representative seed `1301`.

## Technical result

```text
8 / 8 distinct payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
```

Representative package:

```text
payload SHA-256 = dd901bfd73c39260d98ce3198a9d2d583fc162fa5d3168ca797e50d416afa6c3
target rank = 1
locator score = 1.0
decoy rejected = true
repair-field tamper rejected = true
11 structural data tables
12 physical public tables
373 structural parity bits
V20 shard geometry remains 128 B + 8 parity B/shard
```

Representative machine hashes:

```text
published NPZ = 76589f23ef5ee43eaf214ac90b93af2a079c1323ceff6daa99b322b437bade88
manifest      = a1f7e799fcaef8409841ccc908305863667061fa68adf897473b407f21124607
E5 result      = 76dc8c25b965ac736f6480c12e6582514931f59a6bf8aff08da3b7f0a36c341e
```

## Paper-v6 result

The unchanged paper-v6 renderer consumed the same representative package and same fresh 8-seed machine result.

```text
story     = multi_regime_characterization
archetype = materials characterization / physical chemistry
E5        = COMPLETED / PASS
synthetic labels present = true
mandatory non-provenance limitation present = true
```

## Paper-v7 result

The unchanged paper-v7 renderer and finalizer also passed directly:

```text
figure count = 4
raw CSV tables = 12
paper-v6 E5 == candidate E5 = true
required claims traced = C1, C2, C4, C5
synthetic labels present = true
mandatory limitation present = true
```

Rule-selected morphology examples for this representative package are:

```text
bell_peak  -> table 3
linear     -> table 10
periodic   -> table 7
saturating -> table 0
```

These differ from the earlier A-v3 representative package because the visible synthetic package itself changed. The selection rule and paper code did not change.

Final paper-v7 bundle:

```text
file count = 23
covers validation result = true
covers paper-v7 manifest = true
nested manifest mismatch count = 0
```

## Interpretation

The structural reliability change does **not** force a presentation fork or a special paper fixture. The same 12-table package produced by the candidate technical path can flow through the existing paper-v6/v7 stack unchanged.

This closes the major whole-system viability concern left after structural-parity-v3:

```text
A-v4 + 11+1 structural parity
-> exact current-style technical E2E
-> unchanged paper-v6
-> unchanged paper-v7
```

However, this is not yet enough to replace the current promoted path. The previous deterministic-basis promotion required independent-run semantic equality, and this candidate must meet the same standard.

Therefore classification is:

```text
WHOLE_SYSTEM_VIABILITY_PASS
DETERMINISM_RECHECK_PENDING
NOT YET CURRENT-PROMOTED
```

## Evidence

```text
frozen plan  results/structural-parity-current-integration-plan.md
runner       tools/structural_parity_current_end_to_end.py
workflow     41497969290
job          125457790006
artifact     13167542189
artifact zip sha256:be02968d1c26207742999f567c024a84eab6b69d3fbfc4e2c9727f2a6904770d
```

## Boundary

This is a synthetic/mock viability result in one declared CI run. It does not establish independent-run determinism, general A-v4 profile stability across arbitrary configurations, multi-table recovery, real-publication robustness, optimal redundancy, confidential-payload hiding, or undetectability/security.
