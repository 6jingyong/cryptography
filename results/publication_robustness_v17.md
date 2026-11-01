# V17 — publication pipeline robustness

## Conclusion

V17 separates post-publication operations into three classes:

1. **natural invariant** — no normalization metadata is needed;
2. **canonicalizable** — public schema/metadata restores canonical form;
3. **destructive at the current operating point** — information is lost unless the carrier is encoded with more publication margin.

The main result is:

> row/column/table reordering is mostly a schema problem; numeric precision is the real robustness bottleneck.

All payloads and packages in this benchmark are synthetic.

## Reorder / split / merge

Using the current adaptive-q package:

| transform | exact recovery |
|---|:---:|
| baseline | yes |
| column reorder, labels discarded | no |
| column reorder, channel labels retained | **yes** |
| row reorder, row identity discarded | no |
| row reorder, `(segment_id,x_index)` retained | **yes** |
| row + column reorder, labels retained | **yes** |
| table split / merge, labels retained | **yes** |

Therefore Codebook A should not depend on file order.

Required public identities are ordinary schema, not secret locator information:

- table identity / role;
- segment or group identity;
- x / local-position identity;
- channel / series identity.

If these survive publication, arbitrary order can be canonicalized before decoding.

## Unit transforms

For Gaussian/log tables:

\[
y'=ay
\]

implies:

\[
\log y'=\log y+\log a
\]

and the extra constant remains inside the protected macro subspace.

Synthetic test:

- multiply Gaussian/log tables by 1000;
- do **not** tell decoder the scale;
- exact recovery: **yes**.

So positive multiplicative unit conversion is a natural invariant for the current Gaussian/log mode.

For general identity-domain affine transforms:

\[
y'=ay+b
\]

unknown transforms break the current coefficient scale, but public unit metadata restores exact recovery.

## Precision is the hard boundary

Current spacing profile:

```text
q8  : delta = 2.0 x publication step
q16 : delta = 2.5 x
q32 : delta = 3.0 x
```

On the 64 KiB synthetic package:

| post-publication precision | exact |
|---|:---:|
| original publication step | yes |
| 1.5x re-quantization | no |
| 2 decimal places | **yes** |
| 1 decimal place | no |
| 4 significant digits | **yes** |
| 3 significant digits | no |

A per-table scan shows the first failures are not simply “high q fails first”.
q32 often survives longer because its symbol spacing is already more conservative.

Therefore the useful variable is:

\[
\boxed{\Delta/\delta_{final}}
\]

rather than q alone.

## Guarded publication modes

| profile | q8/q16/q32 spacing | q distribution | bit/value | rows | tested exact re-quantization frontier |
|---|---|---|---:|---:|---:|
| current | 2 / 2.5 / 3 | 4 / 4 / 4 | 2.312 | 7,088 | 1.0x |
| guarded | 3 / 3.5 / 4.5 | 7 / 5 / 0 | 1.844 | 8,884 | 1.5x |
| strong guard | 4 / 5 / 6 | 8 / 4 / 0 | 1.762 | 9,296 | 1.75x |
| very strong guard | 5 / 6.5 / 8 | 8 / 4 / 0 | 1.762 | 9,296 | **3.0x** |

For the tested 32 KiB package, `very_strong_guard` remains exact through 3.0x re-quantization and fails at 3.25x.

Relative to current:

- guarded bit/value loss: **20.2%**;
- guarded row increase: **25.3%**;
- very-strong bit/value loss: **23.8%**;
- very-strong row increase: **31.2%**.

The density drop is mostly caused by adaptive-q moving q32 tables back to q16/q8.

## Combined publication pipeline

With `very_strong_guard`, this full synthetic chain was tested:

```text
known unit conversion
-> inverse normalization using public unit metadata
-> arbitrary row reorder
-> arbitrary column reorder
-> table split / merge
-> canonicalization by public labels
-> re-quantization
-> decode
```

Exact recovery remained true through **3.0x** the original publication step and failed at 3.25x.

This supports an explicit Codebook-A operating mode:

\[
\text{capacity}\leftrightarrow\text{publication margin}
\]

instead of trying to make one spacing profile optimal for every publishing pipeline.

## Protocol implication

Codebook A should be split conceptually into:

### Structural interpretation

- family;
- transform;
- q;
- ECC/shaping;
- block geometry.

### Public canonicalization schema

- stable table identity;
- stable group/segment identity;
- x/local-position identity;
- channel identity;
- unit conversion metadata when needed.

### Publication robustness mode

For example:

```text
high_density
guarded_1p5x
guarded_1p75x
guarded_3x
```

The mode controls coefficient spacing and therefore the adaptive-q frontier.

## Limitation

A stable row identity is not free if the published table has no natural group/sample identifier.

The reorder result should be read as:

> reorder is free **conditional on public recoverable identity**.

Likewise, “3.0x exact” is an empirical result for the tested synthetic package and spacing profile, not a universal guarantee.

## Next step

The next high-value experiment is explicit synthetic residual modeling:

\[
y=f(x)+\epsilon
\]

with examples such as iid Gaussian, heteroscedastic Gaussian, AR(1), batch drift, and Gaussian + sparse outliers.

The question becomes:

> under a declared residual model, what q and publication guard can be used while the carrier residual remains compatible with that model?
