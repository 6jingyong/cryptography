# Protocol Reset v1 — A → c → B → b → a

**SYNTHETIC BENCHMARK / RESEARCH PROTOCOL ONLY**

This document resets the architecture around the original two-codebook idea.

The central chain is:

```text
pre-shared root codebook A
        ↓
find / recognize candidate package c
        ↓
open c
        ↓
extract per-package codebook B + processed payload b
        ↓
B explains how b should be interpreted
        ↓
recover payload a
```

The two codebooks are **not peers**.

\[
\boxed{A \text{ is the root / locator / bootstrap protocol}}
\]

\[
\boxed{B \text{ is the per-package reconstruction manifest}}
\]

The package-level dependency is therefore better written as:

\[
\boxed{A \rightarrow c \rightarrow B \rightarrow b \rightarrow a}
\]

rather than `A + B -> c`.

---

# 1. The six objects

## a — payload

`a` is the synthetic benchmark payload that the system ultimately wants to
recover exactly.

In the research repository this must remain synthetic/mock data.

Properties:

```text
opaque byte string
known final length
independent integrity identity
```

Typical benchmark verification:

```text
SHA-256(a_recovered) == SHA-256(a_original)
```

---

## b — processed payload representation

`b` is the representation of `a` after carrier-side processing.

It may include:

```text
fragmentation
symbol mapping
inner ECC
host-aware embedding state
outer ECC payload shards
padding
ordering
```

`b` is not expected to be self-describing.

Without the correct per-package reconstruction information, `b` may be
ambiguous.

---

## B — per-package reconstruction codebook

`B` is generated for one concrete package.

Its job is:

> once the correct package has already been found and opened, explain how to
> interpret `b` and reconstruct `a`.

Typical fields belong here:

```text
carrier family
transform
q / inner carrier mode
delta / publication guard
block geometry
symbol ordering
fragment ordering
ECC parameters
outer-code parameters
length / padding
basis / protocol version
publication precision
canonicalization details needed after opening
```

Important:

- `B` is **not** the global locator.
- `B` is **not** pre-shared for every message.
- `B` does **not** need to be optimized to the smallest possible byte count if
  removing fields makes reconstruction ambiguous.
- The semantics of `B` may themselves be defined by `A`.

A useful abstraction is:

\[
(b,B)=\operatorname{EncodePackagePayload}_A(a;r)
\]

where `r` denotes synthetic randomness / package configuration.

---

## c — candidate package

`c` is the unit that can be mixed among unrelated public/background records.

It combines at least:

```text
fingerprint-bearing public structure
processed payload representation b
per-package reconstruction codebook B
package integrity / version / framing
```

Conceptually:

\[
c=\operatorname{Pack}_A(
    \text{fingerprint},
    B,
    b,
    \text{integrity}
)
\]

The fingerprint is **part of the observable structure of c**, but its useful
meaning is interpreted through `A`.

So:

```text
fingerprint is present in c
A says how to recognize / normalize / score it
```

---

## d — unrelated public/background data

`d` represents records that are not target packages.

The public collection can therefore be modeled as:

\[
S = \operatorname{Mix}(c,d_1,d_2,\ldots,d_n)
\]

The receiver does not begin by knowing which element is `c`.

This is exactly why `A` exists.

---

## A — pre-shared root codebook

`A` exists before any individual package is produced.

Both sides already know it.

Its job is broader than a single decoding recipe.

`A` defines the root protocol:

```text
what public structure to observe
how to canonicalize candidate records
how to derive / compare the fingerprint
how to tolerate reorder / missing structure / extraction noise
how to rank candidate c records
how to recognize outer package framing
how B is represented inside c
how to bootstrap interpretation of B
how strict package verification is invoked
```

Therefore:

\[
\boxed{
A =
\text{locator protocol}
+
\text{bootstrap protocol}
+
\text{root interpretation rules}
}
\]

This is the shared long-lived object.

---

# 2. Sender state machine

The sender-side synthetic protocol should be modeled as:

```text
INPUT:
  payload a
  pre-shared root codebook A

STATE S1 — choose package configuration
  A defines allowed package families / versions / framing rules

STATE S2 — encode payload
  a
   ↓
  inner processing
   ↓
  b

STATE S3 — generate per-package reconstruction codebook
  package-specific choices
   ↓
  B

STATE S4 — construct fingerprint-bearing package
  fingerprint(A, public structure)
  + B
  + b
  + integrity
   ↓
  c

STATE S5 — place c among unrelated records
  c + d1 + d2 + ...
   ↓
  public collection S
```

The sender does **not** need to modify `A` for every package.

That is an important invariant.

---

# 3. Receiver state machine

The receiver begins with:

```text
public collection S
pre-shared root codebook A
```

Then:

```text
STATE R1 — canonicalize
  normalize public records using rules in A

STATE R2 — locate
  compute / compare A-defined structural fingerprint
  rank candidates

STATE R3 — candidate bootstrap
  try opening top candidate c using A-defined framing

STATE R4 — package verification
  reject malformed / wrong candidate
  false-positive locator hits are allowed

STATE R5 — extract
  c
   ↓
  B + b

STATE R6 — interpret B
  A defines how B itself should be parsed

STATE R7 — reconstruct
  B explains b
   ↓
  decode / reorder / ECC / trim
   ↓
  candidate a

STATE R8 — strict final verification
  accept only if package / payload integrity passes
```

So the recovery chain is:

\[
\boxed{
A
\rightarrow
\operatorname{Locate}(c)
\rightarrow
\operatorname{Open}(c)
\rightarrow
(B,b)
\rightarrow
a
}
\]

---

# 4. What the fingerprint actually is

The fingerprint should not be confused with `B`.

It is better represented as an A-defined view of public package structure.

Let:

\[
\phi_A(c)
\]

be the canonical structural observation of candidate package `c`.

Then the locator operates on:

\[
F_A(c)=\operatorname{Fingerprint}_A(\phi_A(c))
\]

The public may see the underlying structure.

But useful interpretation depends on `A`:

```text
which fields matter
how labels are normalized
which positions are comparable
what missing fields mean
how substitutions are scored
how candidate rank is computed
```

Thus:

\[
\text{observable structure}
\neq
\text{useful fingerprint semantics}
\]

---

# 5. Correct optimization priorities

The protocol should **not** be optimized as if every byte or fingerprint symbol
were equivalent payload overhead.

The priority order is:

```text
P0  A must reliably locate / bootstrap c

P1  c must remain openable and verifiable

P2  B must fully describe reconstruction of b

P3  b must recover a exactly / within the declared reliability target

P4  only then optimize capacity / publication cost / numeric efficiency
```

Equivalently:

\[
\boxed{
\text{find}
>
\text{open}
>
\text{interpret}
>
\text{recover}
>
\text{capacity}
}
\]

This means:

- do not shorten the A-defined fingerprint just to improve bit/value;
- do not delete necessary B fields to reduce manifest overhead;
- do not weaken strict verification for throughput;
- do not declare a high-capacity carrier successful if A can no longer find it.

---

# 6. What A may contain vs what B may contain

A useful separation table:

| Concern | A: pre-shared root codebook | B: per-package codebook |
|---|---|---|
| Fingerprint interpretation | yes | no |
| Candidate ranking | yes | no |
| Canonicalization before locating | yes | no |
| Package framing/version bootstrap | yes | optionally version instance |
| How to parse B | yes | self fields after bootstrap |
| q used by this package | allowed set only | actual q / mode |
| table/block geometry | allowed schema | actual geometry |
| transform used this package | allowed vocabulary | actual transform |
| ECC mode this package | allowed vocabulary | actual parameters |
| fragment ordering | rule family | actual order |
| payload length | no | yes |
| padding | no | yes |
| outer-code parity count | allowed range | actual count |
| final payload digest | verification rule | actual expected value / binding |
| locator Recall@K contract | yes | no |

This is the cleanest way to prevent the two codebooks from being confused again.

---

# 7. Protocol invariants

The following should become hard invariants.

## Invariant A1 — A is stable across packages

A new package may not require a new pre-shared codebook merely because its local
q, geometry, or ECC changed.

Those package-specific values belong in `B`.

## Invariant A2 — candidate false positives are acceptable

A locator hit is not final acceptance.

\[
\text{locator hit}
\neq
\text{valid c}
\]

Strict package verification remains authoritative.

## Invariant B1 — B is complete enough to reconstruct

If removing a B field makes two valid interpretations possible, that field is
not optional overhead.

## Invariant C1 — c is the unit of discovery

The locator should rank candidate packages `c`, not individual payload fragments
unless `A` explicitly defines a higher-level aggregation scheme.

## Invariant C2 — fingerprint and payload are separate logical functions

A fingerprint feature exists to help `A` identify `c`.

A payload-bearing degree of freedom exists to carry `b`.

The same public field may contribute to both in a synthetic benchmark, but the
two objectives should not be conflated.

## Invariant D1 — d does not need to decode

Background records `d` need only participate in the locator benchmark as
non-target candidates.

---

# 8. Revised architecture

```text
                PRE-SHARED
             ┌───────────────┐
             │   codebook A  │
             │ root / locator│
             └───────┬───────┘
                     │
       sender        │                 receiver
                     │
a ──► encode ──► b   │    public S ──► canonicalize
              │      │                   │
              ├─► B  │                   ▼
              │      │                 locate
              ▼      │                   │
             pack ◄──┘                   ▼
              │                        candidate c
              ▼                          │
              c                          ▼
              │                        verify/open
              ▼                          │
         mix with d                      ▼
              │                       B + b
              ▼                          │
          public S                       ▼
                                       decode
                                         │
                                         ▼
                                         a
```

---

# 9. Safety / benchmark scope

This repository should continue to restrict implementation and examples to
synthetic/mock payloads, synthetic public packages, and synthetic candidate
corpora.

The protocol model is useful for evaluating:

```text
locator robustness
self-description
reconstruction correctness
publication transforms
package integrity
synthetic capacity
```

It is not a deployment guide for hiding real confidential material in real
scientific publications.
