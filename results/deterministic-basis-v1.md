# Deterministic basis v1

Status: **PROMOTION GATES PASS**.

Frozen plan: `results/deterministic-basis-v1-plan.md`.

Current engine after promotion:

```text
src/noisy_host_package_v18_deterministic.py
```

Legacy baseline retained:

```text
src/noisy_host_package_v18.py
```

The promoted basis contract is:

```text
deterministic-dct-mgs-v1
```

It remains B state and is declared in the package manifest. A decoder using this engine rejects a different declared basis version.

## Gate A — protocol viability

Fresh current integration seeds `901..908`:

```text
8 / 8 unique payload hashes
8 / 8 exact recovery
Recall@20  = 1.0
Recall@100 = 1.0
median target rank = 1
max target rank = 1
paper-v7 gate = PASS
```

No q, delta, V20 RS geometry, locator rule, payload size, or paper claim gate was relaxed.

## Gate B — independent semantic determinism

Two independent GitHub Actions runners generated the same frozen current bundle semantics.

Compared authority included:

```text
canonical B JSON
all per-table x float64 arrays
all per-table y float64 arrays
all exported CSV bytes
current-V20 E5
paper-v7 numeric figure plan
morphology representative selection
presentation archetype / story
```

Final comparison:

```text
semantic_equal = true
mismatch_count = 0
raw NPZ container hash equal = true
semantic authority SHA-256 = 243b05fd32624e931379ea471c2d209700fb3491c33a911f9071084e8f57bc04
```

Workflow run: `41393344543`  
Comparison artifact: `13118720466`  
Artifact digest: `sha256:5ef4da7eefbea48227553bdc89069e1db6e400fe40a65268cb7c9f1a8142185b`

The last paper-side mismatch was traced to `np.polyfit` producing ~1e-16 R² differences on identical inputs. Paper-v7 now uses fixed-order analytic one-variable regression and `math.fsum` for the baseline R² calculation. No carrier parameter changed for that repair.

## Gate C — bounded evidence regression

The deterministic engine passed the existing frozen bounded harnesses without retuning q/delta/RS:

```text
V18 core / 8-seed current protocol         PASS
V18 frozen residual matrix                 PASS
V18 24-seed publication statistics         PASS
V18 transition error profile               PASS
V20 bounded reintegration                  PASS
V20 fixed-geometry failure envelope        PASS
```

Workflow run: `41393344478`.

Artifacts:

```text
13118044396  deterministic-basis-gate-c-v18-core
13118637081  deterministic-basis-gate-c-v18-damage
13117789652  deterministic-basis-gate-c-v20
```

## Promotion decision

**Promote.** The current workflows now use `src/noisy_host_package_v18_deterministic.py`. The old V18 engine remains in the repository as a legacy baseline rather than being rewritten in place.

This resolves the paper-v7 fixed-seed visible-carrier reproducibility blocker under the declared CI environment.

Boundary: this is an exact semantic reproducibility result across the frozen independent GitHub Actions environment. It is not a claim of bit-identical behavior across every CPU, libm, NumPy, or Python implementation.
