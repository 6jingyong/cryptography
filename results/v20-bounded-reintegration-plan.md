# V20 bounded outer-reliability reintegration — frozen plan

Scope: **synthetic/mock benchmark only**.

This experiment is motivated by the current V18 error profile, which found only a few residual payload bits / corrected codewords wrong after the existing inner Hamming layer. It does not restore historical V20 numbers and does not optimize bit/value.

## 1. Protocol role

V20 is an **outer logical reliability layer** around recovered payload `a`.

Authoritative chain remains:

```text
A -> locate/rank c -> open authenticated envelope -> decode damaged b -> optional outer repair -> exact a
```

Responsibilities:

- `A`: long-lived locator/bootstrap root; may define field vocabulary and authenticate/mask the repair envelope, but contains no package-specific shard/parity geometry.
- `B`: per-package manifest; contains the concrete V20 code family and shard/parity geometry.
- `b`: V18 numeric carrier, still subject to publication damage.
- `r`: V20 repair bytes, masked under an A-derived HMAC stream and authenticated with B.
- `a`: final synthetic payload.

## 2. Integrity semantics

Current v3/v18 outer HMAC binds raw `B+b`, so any post-seal numeric rewrite of b fails before inner decode. V20 deliberately changes this part of the envelope:

```text
v20_tag = HMAC_A(B_bytes || masked_r)
```

Raw `b` is **not** included in the V20 envelope tag. Instead:

1. B and masked repair bytes must authenticate before decode;
2. B contains the expected final payload SHA-256;
3. damaged b is decoded to a candidate payload;
4. if the candidate hash already matches B, accept without repair;
5. otherwise use authenticated repair bytes to correct the candidate;
6. accept only if the repaired payload hash exactly matches the authenticated B value.

Thus V20 authenticates the logical payload target and repair envelope rather than requiring raw NPZ byte identity across publication transforms.

This is a protocol change and must not be described as current v3 raw-byte integrity.

## 3. Fixed outer code

First-pass code is frozen before results:

```text
scheme: Reed-Solomon over GF(256)
payload bytes: 512
shards: 4
bytes per data shard: 128
parity bytes per shard: 8
byte errors correctable per shard: 4
total parity bytes: 32
payload-level parity overhead: 6.25%
```

No alternate parity size will be tried in this PR.

Repair bytes are parity only; they are XOR-masked with a deterministic HMAC-SHA256 stream derived from `A.root_key` and the authenticated payload SHA-256 context before being stored in `r`.

## 4. Damage lifecycle

Construct and seal V20 c first. Then mutate only the numeric b field using the existing publication-damage functions. B, masked r, and tag remain unchanged.

This is intentionally a **post-seal numeric-b damage** experiment.

## 5. Frozen test matrix

Fresh seeds:

```text
701..724   (24 packages)
```

No-damage control:

```text
24/24 exact required
```

Paired additive noise:

```text
sigma/delta = 0.14, 0.15, 0.16
```

Representative alignment-sensitive re-quantization:

```text
factor = 1.06, 1.20, 1.30
```

For every condition report:

- V18 direct exact count before V20 repair;
- V20 exact count after optional repair;
- repairs attempted / successful;
- corrected shard count;
- final authenticated payload-hash match;
- A-layer structural locator score sentinel.

## 6. Refusal rule

This first geometry is accepted only if:

```text
clean control = 24/24 exact
AND every one of the six damaged conditions = 24/24 exact after V20 repair
AND every accepted package passes the authenticated final payload hash
```

If any damaged condition is below 24/24, **reject this 128-byte / 8-parity-byte shard geometry**. Do not increase parity, change shard size, or add retries inside the same result set.

A failed geometry does not invalidate the sparse V18 error profile; it means this particular V20 mapping is not sufficient.

## 7. Claims not allowed

Even if the gate passes, do not claim:

- universal post-seal robustness;
- real-publication robustness;
- cryptographic security of the carrier;
- that raw b bytes are authenticated unchanged;
- that 6.25% is optimal redundancy;
- that historical V20 metrics are restored.
