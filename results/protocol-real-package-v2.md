# Protocol Harness v2 — real V12 package under A → c → B → b → a

## Conclusion

The protocol reset has now been tested with the repository's real synthetic V12
numeric package rather than a toy payload transform.

The executed chain is:

```text
pre-shared root codebook A
        ↓
locate candidate package c
        ↓
strict outer package verification
        ↓
extract B + b
        ↓
B = real V12 JSON manifest
b = real published V12 NPZ package
        ↓
real V12 decoder
        ↓
recover synthetic payload a
        ↓
SHA-256 exact verification
```

This is the first end-to-end test in the corrected architecture where `B` and
`b` are the actual package artifacts used by the carrier benchmark.

---

## Real-package run

Configuration:

```text
payload a                = 2,048 synthetic bytes
B                        = V12 per-package manifest
b                        = V12 published NPZ numeric package
tables                   = 12
channels                 = 4
public candidate corpus  = 3,000 records
near-decoys              = 30
fingerprint erasure      = 25%
fingerprint substitution = 10%
Top-K verification       = 100
```

Observed:

```text
target rank     = 1
accepted rank   = 1
attempt count   = 1
exact recovery  = TRUE
```

Package details from this run:

```text
B manifest bytes   = 7,167
b NPZ bytes        = 44,081
q schedule         = [8,16,32] repeated across four macro families
published rows     = 1,904
gross bit/value    = 2.151
```

---

## Acceptance tests with the real V12 decoder

All tests passed.

### T1 — normal open

```text
A -> c -> B+b -> V12 decoder -> a
```

Result:

```text
strict_verify_pass
```

### T2 — B corruption

A single byte in the real V12 manifest was modified without updating the outer
package integrity tag.

Result:

```text
c_outer_integrity_failed
```

The V12 decoder was not trusted to interpret a corrupted manifest.

### T3 — b corruption

A byte in the published NPZ package was modified without updating the package
integrity tag.

Result:

```text
c_outer_integrity_failed
```

### T4 — locator false positive

A synthetic decoy was given the same visible fingerprint structure as the real
target.

Observed:

```text
rank 1 decoy
    -> c_outer_integrity_failed

rank 2 real c
    -> strict_verify_pass
    -> exact a recovery
```

This directly validates the intended principle:

\[
\boxed{\text{locator false positive} \neq \text{protocol failure}}
\]

A only needs to pull the true `c` into the verified candidate set.

### T5 — wrong A

The correct package was opened using a different root codebook A.

Result:

```text
c_outer_integrity_failed
```

The root codebook therefore remains part of the bootstrap/opening path.

---

## What now belongs in B

The real V12 manifest naturally demonstrates the intended role of the
per-package codebook B.

It carries package-specific information such as:

```text
q
transform
table geometry
payload offsets
publication parameters
decoder parameters
payload length / hash
```

These values do not need to live in long-lived A.

This is exactly the distinction the protocol reset was intended to restore.

---

## What A still does in this harness

A currently defines:

```text
locator fingerprint semantics
fingerprint normalization / scoring
outer field mapping
manifest format identifier
payload-package format identifier
outer package integrity rule
```

It does **not** know the concrete q schedule or table-by-table decoding
parameters.

That separation should remain an invariant.

---

## What is still synthetic / simplified

The current A-defined fingerprint is still a synthetic structural fingerprint
attached at the outer package layer.

The next technical step is not another capacity optimizer.

It is to connect the fingerprint more closely to public structural properties of
the actual generated package while preserving the rule:

```text
A defines how to recognize the fingerprint
B defines how to reconstruct the specific payload package
```

The benchmark must remain synthetic-only.

**SYNTHETIC BENCHMARK — NOT REAL EXPERIMENTAL RESULTS**
