# V18 publication-damage frontier refinement — frozen plan

Scope: **synthetic-only**.

The coarse frontier is already established and must not be changed by this experiment:

```text
re-quantization: 1.00x passes 4/4; 1.25x fails 1/4
additive noise:  0.10 delta passes 4/4; 0.15 delta fails 2/4
```

This experiment only measures those transition intervals more finely. It does **not** change q, delta, ECC, table budgets, host model, locator, publication logic, or decoding.

## Fresh seeds

Use eight payload/host seeds not used in the coarse frontier:

```text
401,402,403,404,405,406,407,408
```

Fresh seeds are required so the refinement does not merely fit the previous four realizations.

Common configuration:

```text
payload = 512 bytes / seed
channels = 2
candidate corpus = 2,000
Top-K = 100
smooth-reference V18 host mode
```

## Re-quantization refinement

Test exactly:

```text
1.00x  baseline control
1.05x
1.10x
1.15x
1.20x
1.25x  coarse-failure control
```

The existing publication step recorded in B remains the reference. B is not updated with the unknown factor.

## Additive-noise refinement

Test exactly:

```text
0.10 delta  coarse-pass control
0.11 delta
0.12 delta
0.13 delta
0.14 delta
0.15 delta  coarse-failure control
```

Noise is zero-mean Gaussian in each table's current transform domain. The realization is unknown to the decoder and is not recorded in B.

## No combined-damage sweep

Combined re-quantization + noise was already clearly outside the coarse all-seed envelope. This refinement does **not** add more combined points. The purpose is to resolve the two one-dimensional transitions first.

## Lifecycle position

As in the coarse frontier:

```text
V18 embed
-> A-keyed public assignment
-> unknown numeric damage
-> seal c over damaged b
-> A locate
-> strict open
-> B decode
-> final hash
```

This remains a pre-seal V18 publication-damage measurement. Post-seal corruption belongs to V20 outer reliability.

## Metrics and PASS rule

For every condition record:

```text
direct B + damaged-b exact recovery
full-protocol exact recovery
target rank / Recall@100
```

A condition is an **all-seed PASS** only when all eight fresh seeds have:

```text
direct exact recovery = 8/8
full-protocol exact recovery = 8/8
Recall@100 = 1.0
```

Also record the exact pass count even for failed conditions; do not collapse 7/8 and 0/8 into the same narrative.

## Interpretation

The result may narrow the all-seed demonstrated frontier, but it must not be treated as a universal deterministic threshold. Eight seeds still sample a stochastic payload/host/noise process.

Report:

```text
largest tested re-quantization factor with 8/8 exact
first tested re-quantization factor below 8/8
largest tested noise sigma/delta with 8/8 exact
first tested noise sigma/delta below 8/8
pass count at every grid point
failure layer at every grid point
```

If the fresh-seed baseline `1.00x` does not pass 8/8, the harness/reference assumption is invalid and the refinement is rejected.

If the fresh-seed `0.10 delta` control does not reproduce 8/8, explicitly downgrade the earlier `0.10 delta` boundary rather than tuning the carrier.

No parameter rescue is allowed in this result.
