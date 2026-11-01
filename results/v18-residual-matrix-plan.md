# V18 residual-model matrix — frozen falsification plan

Scope: **synthetic-only**.

The smooth-residual V18 result is already current bounded evidence. This experiment asks a stronger question without changing the carrier after seeing results:

> Does the same host-aware modulo-QIM design remain viable across materially different residual structures at comparable residual energy?

No bit/value optimization and no post-result rescue sweep are allowed in this matrix.

## Fixed models

The carrier will be tested under exactly these five synthetic residual families:

```text
1. iid_gaussian
2. heteroscedastic_gaussian
3. ar1_rho_0p85
4. low_frequency_drift
5. gaussian_sparse_outliers
```

The existing `smooth_free_gaussian` result remains the reference but is not counted among the five challenge models.

## Energy normalization

Different residual shapes are normalized to a common per-row free-subspace RMS target derived from the existing smooth-host model at the same table size and publication step. This is intended to compare **structure**, not simply make one model harder by giving it more energy.

The macro/protected subspace is projected out before normalization. The decoder does not receive the generated residual realization.

## Model definitions

### iid_gaussian

Pointwise iid Gaussian residual in transform space, projected into the free subspace.

### heteroscedastic_gaussian

Pointwise Gaussian residual with deterministic standard-deviation envelope increasing from `0.5x` to `1.5x` across the local x grid, then projected into the free subspace.

### ar1_rho_0p85

Stationary AR(1)-like residual in transform space with `rho=0.85`, then projected into the free subspace.

### low_frequency_drift

Random linear combination of low-frequency sinusoidal/drift components that is then projected into the free subspace. The projection prevents protected macro components from being counted as host residual.

### gaussian_sparse_outliers

Pointwise Gaussian residual plus sparse signed outliers at `2%` of positions with magnitude `6 sigma`, projected into the free subspace.

## Carrier policy — frozen

For every model and table:

```text
q=4 first
q=2 only if q=4 fails the existing declared table distortion budget
same q-ary Hamming protection
same modulo-QIM embedding rule
same table blueprints and budgets
same publication quantization
same A-layer locator
```

No model-specific delta, budget, or q policy may be introduced after results.

## Stage A — calibration gate

For every model, all 12 tables are calibrated under that residual family.

A table passes only if a selected mode has:

```text
exact block recovery = 1.0
host-adjustment NRMSE <= the already-declared table budget
```

If q=4 and q=2 both fail a table, that model is marked **UNSUPPORTED**. The table is not silently dropped.

## Stage B — current-protocol gate

For each model that passes all 12 calibration tables, run seeds:

```text
201, 202, 203, 204
```

through the full lifecycle:

```text
host generation
-> encode
-> public package
-> A locate
-> strict open
-> B decode
-> final payload hash verify
```

Configuration:

```text
payload = 512 bytes / seed
channels = 2
candidate corpus = 2,000
Top-K = 100
```

Per-model protocol PASS requires:

```text
4 / 4 distinct payload hashes
4 / 4 exact recovery
Recall@100 = 1.0
all package-specific V18 state present in B
```

## Interpretation rule

### GENERAL-V18 SUPPORTED

Only if **all five** challenge models pass Stage A and Stage B.

This still means only the declared synthetic matrix, not real data or universal noisy-host robustness.

### MODEL-SPECIFIC V18

If one or more models fail, reject the claim that current V18 is a general noisy-host default. Retain the smooth model and any passing challenge models as explicitly supported regimes.

V19, if pursued later, must then select among supported regimes rather than assume one universal V18 mode.

### FIRST-PASS CARRIER FAILURE

If failures are widespread enough that only the original smooth reference survives, do not promote V18 beyond the already-recorded smooth-host bounded result.

## Reporting requirements

For every model report:

- calibration pass/fail per table;
- selected q distribution;
- min/max host-adjustment NRMSE;
- adjustment / host-residual RMS ratio;
- protocol exact-recovery rate and Recall@100 if Stage B runs;
- failed model/table identities without suppression.

No failed model is to be retuned in the same result.
