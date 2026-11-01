# V18 publication-damage statistics — frozen plan

Scope: **synthetic-only**.

The fresh-seed refinement rejected two overly simple interpretations:

1. re-quantization success is not monotonic in the tested factor;
2. independent noise realizations at each alpha do not define a deterministic nested threshold.

This experiment changes the **measurement model only**. The V18 carrier, q/delta/ECC policy, host model, publication logic, A-layer locator, B schema and decoder are unchanged.

## Fresh sample

Use 24 new payload/host seeds:

```text
501..524
```

Common package configuration:

```text
payload = 512 bytes
channels = 2
smooth-reference V18 host
A-keyed public assignment before damage
post-embedding / pre-c-seal damage position
```

The experiment measures direct `B + damaged b` package-exact recovery because the two previous damage experiments showed Recall@100=1.0 and target locator score/rank intact across all tested conditions. The target structural locator score is still checked for every damaged package as a sentinel.

## A. Dense re-quantization response map

Test factors:

```text
1.00, 1.02, 1.04, ..., 1.30
```

For each factor report:

```text
exact package count / 24
exact package rate
95% Wilson interval
target structural locator score min/max
```

Do **not** summarize this as one monotonic threshold unless the response itself is monotonic. The intended output is a factor-response map capable of revealing safe/unsafe bands or grid-alignment structure.

## B. Paired additive-noise probability map

Test:

```text
sigma/delta = 0.08,0.09,...,0.18
```

For each seed and table, generate **one** standard-normal base field `g`. Every alpha for that seed/table uses:

```text
noise(alpha) = alpha * delta * g
```

Thus alpha conditions are paired/scaled versions of the same noise direction rather than unrelated random draws.

For each alpha report:

```text
exact package count / 24
exact package rate
95% Wilson interval
target structural locator score min/max
```

This is still a finite-sample probability estimate, not a universal deterministic threshold.

## No rescue / no optimization

Forbidden in this result:

```text
changing delta
changing q policy
adding redundancy
changing table budgets
changing host energy
choosing different seeds after seeing failures
optimizing bit/value
```

Hypothesis failure is valid data and must not fail CI merely for being unfavorable.

## Interpretation target

The useful questions are now:

```text
Does re-quantization show reproducible alignment bands?
How quickly does package-exact probability fall under paired additive noise?
Does the public structural locator score remain intact while inner decode degrades?
```

Only after these are answered should a later design compare explicit publication guard modes, inner-code changes, or V20-style outer reliability.
