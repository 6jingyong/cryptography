# V18 post-embedding / pre-seal publication-damage frontier — frozen plan

Scope: **synthetic-only**.

This experiment isolates the next unresolved V18 variable after the known-host residual matrix.

## Lifecycle position

Damage is applied in exactly this order:

```text
V18 encode payload into noisy-host b
-> apply A-keyed public table assignment
-> apply unknown numeric publication damage to b
-> seal c / compute outer integrity over the damaged b
-> A locate
-> strict open
-> B decode damaged b
-> final payload hash verify
```

This ordering is deliberate.

If bytes are changed **after c has already been sealed**, the current strict outer HMAC should reject them before inner decoding. That is an outer reliability / V20 question, not a V18 carrier-robustness question.

Therefore this matrix tests **post-embedding, pre-seal publication damage** while keeping the outer integrity layer valid.

B is not updated with the unknown damage condition.

## Fixed reference mode

Use the current smooth-reference V18 host mode to isolate channel damage from host-distribution shape.

```text
payload seeds = 301,302,303,304
payload = 512 bytes / seed
channels = 2
candidate corpus = 2,000
Top-K = 100
q policy = unchanged current V18 policy
```

No q/delta/budget/guard retuning is permitted after seeing results.

## Damage domain

Damage is applied in each table's current transform domain:

```text
identity tables -> y domain
gaussian/log tables -> log(y) domain
```

This avoids making log-domain tables fail merely because an additive perturbation creates non-positive y.

## Matrix A — coarser re-quantization

Re-quantize encoded values at:

```text
1.00x
1.25x
1.50x
1.75x
2.00x
2.50x
3.00x
```

times the table's existing publication step.

`1.00x` is the baseline control.

## Matrix B — unknown additive numeric noise

Add zero-mean Gaussian noise after embedding with transform-domain standard deviation:

```text
0.00 delta
0.05 delta
0.10 delta
0.15 delta
0.20 delta
0.25 delta
```

where `delta` is the table's current q-ary coefficient spacing recorded in B.

The noise realization is not recorded in B and is not known to the decoder.

## Matrix C — combined damage

For each pair:

```text
re-quantization = 1.50x or 2.00x
noise sigma/delta = 0.05, 0.10, 0.15
```

apply:

```text
additive noise -> coarser re-quantization
```

in transform space.

## Metrics

For every condition and seed report both:

### Inner decode

Decode `B + damaged b` directly, bypassing locator, and record exact final hash recovery.

### Full current protocol

Seal c over the damaged b, then run:

```text
A locate -> strict open -> B decode -> final hash
```

Record:

```text
target rank
accepted rank
exact recovery
Recall@20
Recall@100
```

This separates inner carrier failure from locator/fingerprint failure.

## Condition PASS

A condition passes only if all four seeds have:

```text
direct exact recovery = 4/4
full-protocol exact recovery = 4/4
Recall@100 = 1.0
```

No majority-pass rule is used.

## Frontier reporting

Report, without rescue tuning:

```text
largest re-quantization factor with condition PASS
largest noise sigma/delta with condition PASS
all combined pairs that PASS / FAIL
first failure conditions
whether failure starts in inner decode or locator/full protocol
```

If baseline `1.00x / 0 noise` fails, classify the harness as invalid rather than interpreting the frontier.

## Interpretation

Passing this matrix would support only the tested **pre-seal publication-damage envelope**.

It must not be upgraded to:

```text
post-seal tamper tolerance
outer package repair
universal channel coding
real-publication robustness
cryptographic security
```

If the current q=4 carrier fails early, retain the failure boundary. Do not widen delta or add V20 redundancy inside this result. Such changes belong to a later design decision after the frontier is known.
