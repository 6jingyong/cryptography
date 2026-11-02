# Physical structural damage v1

Status: **FROZEN EXPERIMENT EXECUTED / CLEAN GATE PASS**

Scope: synthetic/mock benchmark only.

This experiment closes the earlier gap between the descriptor-only structural-v4 model and the actual public NPZ → locator → deterministic V18 → bounded V20 path.

Frozen conditions are recorded in `physical-structural-damage-v1-plan.md`. Damaged outcomes were never CI pass/fail criteria.

## Result

Fresh seeds `1001..1024`, payload 512 B, channels 2, 2,000-candidate corpus, current deterministic V18 engine, and unchanged V20 geometry:

| condition | locator 1.0 | R@100 | candidate payload | V20 accepted | primary result |
|---|---:|---:|---:|---:|---|
| clean | 24/24 | 1.0 | 24/24 | 24/24 | direct exact |
| whole x+y table deletion | 0/24 | 0.0 | 0/24 | 0/24 | A locator degraded first |
| one tail y-segment truncation | 24/24 | 1.0 | 0/24 | 0/24 | decoder cannot produce candidate |
| 4-segment localized burst, σ=4Δ | 24/24 | 1.0 | 24/24 | 24/24 | 4 byte errors; 24/24 V20 repairs |
| 6-segment localized burst, σ=4Δ | 24/24 | 1.0 | 24/24 | 0/24 | 6 byte errors; 24/24 exceed tested RS capacity |

Whole-table deletion pushed the target out of the useful locator set:
- Recall@20 = 0
- Recall@100 = 0
- median target rank = 1749
- max target rank = 1960

Tail truncation is a different failure:
- locator remains score 1.0 and rank 1 in all 24 runs;
- deterministic V18 fails before producing a candidate payload;
- therefore V20 has nothing to repair.

The localized burst pair reaches V20 cleanly:
- 4 segments: median/max candidate byte errors = 4/4; max shard byte errors = 4; 24/24 repair success.
- 6 segments: median/max candidate byte errors = 6/6; max shard byte errors = 6; 0/24 repair success.

Across every run in which a candidate payload existed, the tested rule remained exact:

```text
V20 final failure
<=>
at least one 128-byte shard has >4 candidate byte errors
```

Capacity-rule mismatch count: **0**.

## Project-level interpretation

This separates three responsibilities that were previously easy to conflate:

```text
whole-table deletion
-> A/public locator failure

tail structural truncation
-> locator survives
-> b/parser/decoder cannot form candidate payload

shape-preserving numeric burst
-> locator survives
-> candidate payload exists
-> V20 succeeds/fails according to its fixed per-shard RS capacity
```

The practical consequence is important: **more V20 parity is not the correct first repair for the observed structural deletion/truncation failures.** Those failures occur upstream and should be addressed in A/public structural canonicalization or b/parser erasure handling before outer payload ECC is reconsidered.

## Evidence

- frozen commit: `fbbb3e23f8eaf288931cd6a6feacf521100ae598`
- workflow run: `41423287034`
- job: `125203729548`
- artifact: `13130219293`
- artifact ZIP SHA-256: `925c0596f1fe61c4fb8227620601ac2f925c8d06b8ff4da24977aa677cd0621e`

The uploaded artifact contains the full 120-run JSON plus generated summary Markdown.

## Boundary

This is a bounded synthetic 24-seed experiment. It does not establish universal structural robustness, real-publication behavior, optimal parity geometry, or behavior under arbitrary insertion/reordering/multi-table loss/B-r corruption.
