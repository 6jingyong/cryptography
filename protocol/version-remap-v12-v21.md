# Version Remap — where V12–V21 belong after the protocol reset

This note remaps previous work onto the corrected architecture:

```text
A -> c -> B -> b -> a
```

The purpose is to preserve useful experiments without preserving incorrect
naming.

---

# V12 — adaptive q

**Correct layer:** primarily `b`, with package choices recorded in `B`.

Useful retained work:

```text
adaptive q
q-ary Hamming ECC
shaping
protected subspace
publication quantization
exact reconstruction
```

Interpretation:

- V12 is a carrier/codec experiment for how `b` is represented numerically.
- Actual q, transform, block geometry, etc. belong in per-package `B`.

Status: **retain**.

---

# V14 — "dual codebook"

**Correct layer:** mixed two different concepts and therefore should be renamed
historically rather than treated as the final architecture.

Useful retained work:

```text
candidate structural fingerprint
strict candidate verification
actual package decoder
```

Correct remap:

- locator portion -> `A`
- decode manifest portion -> `B`

Status: **retain experiments, retire terminology**.

---

# V16 — labeled locator

**Correct layer:** `A`.

The labeled fingerprint:

\[
F=\{(\ell_i,v_i)\}
\]

is an A-defined way to observe candidate package `c`.

Reordering and erasure are locator/canonicalization concerns.

Status: **retain as A-layer benchmark**.

---

# V17 — publication robustness

**Correct layer:** split between `A`, `c`, and `B`.

- public labels / canonical ordering needed before locating -> `A`
- package surviving reorder/split/merge/quantization -> `c`
- actual transform / precision / local decode settings -> `B`

Status: **retain, split responsibilities**.

---

# V18 — host-aware residual carrier

**Correct layer:** `b`, with mode parameters in `B`.

Host-aware syndrome/QIM determines how payload representation is carried in the
numeric free subspace.

Status: **retain**.

---

# V19 — regime selector

**Correct layer:** sender-side generation policy for `(b,B)`.

The selector chooses which inner carrier family should be used for one package.

It is not part of long-lived `A` unless `A` merely defines the allowed mode
vocabulary.

Status: **retain, reclassify**.

---

# V20 — outer ECC / verified package rate

**Correct layer:** mainly `b` and `c`, with parameters in `B`.

- outer data/parity structure -> payload/package reliability
- actual shard geometry / parity counts -> `B`
- integrity framing / opening rules -> `c` and A-defined bootstrap

Status: **retain**.

---

# V21 — constrained optimizer

**Correct lesson retained:**

> capacity must be optimized only after protocol constraints pass.

**Incorrect abstraction to retire:**

- treating "Codebook A" as the package reconstruction manifest;
- treating "Codebook B" as the locator.

After reset:

```text
A = pre-shared root locator/bootstrap codebook
B = per-package reconstruction codebook
```

The previous V21 locator experiments should be interpreted as experiments on
the **A-layer fingerprint schema**.

The previous fixed-manifest accounting should be interpreted as **B + package
metadata cost**, not as the cost of A.

Status: **retain results selectively, rewrite architecture**.

---

# Current status and next integration step

The protocol-level lifecycle now exists and has been tested with the real synthetic V12 manifest and published NPZ package:

```text
A
-> locate c
-> strict outer verify
-> extract real B + b
-> real V12 decode
-> recover a
-> strict final verify
```

The next technical integration step is **not** another throughput sweep. It is to bind the A-layer fingerprint to public structural properties of the actual generated package, while preserving the separation:

```text
A defines how to find / bootstrap c
B defines how this concrete b reconstructs a
```

V18–V21 should be reintroduced only after each mode is cleanly attached to this corrected lifecycle.
