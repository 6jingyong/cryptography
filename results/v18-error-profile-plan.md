# V18 publication-damage error profile — frozen plan

Scope: **synthetic/mock benchmark only**.

This experiment does **not** change V18 carrier parameters, q, delta, ECC, host model, publication budget, payload size, or locator behavior. It only inspects the residual errors inside damaged `b` after the already-measured post-embedding / pre-seal publication channel.

## Question

When package-exact recovery fails, is the residual damage:

- sparse and concentrated in a few payload bits / codewords / tables; or
- diffuse across many tables and many codewords?

This determines whether a future V20-style reliability layer is structurally plausible. It does not by itself authorize adding redundancy.

## Frozen configuration

- fresh seeds: `601..624` (24 packages)
- payload: 512 bytes
- channels: 2
- carrier: unchanged V18 host-aware modulo-QIM
- damage position: post-embedding, post-A-assignment, pre-c-seal
- locator: structural score sentinel only; no corpus retuning

Paired additive-noise conditions:

```text
sigma/delta = 0.12, 0.13, 0.14, 0.15, 0.16
```

Deterministic re-quantization conditions:

```text
factor = 1.00, 1.06, 1.10, 1.20, 1.22, 1.30
```

The re-quantization factors deliberately include previously observed valleys and rebounds; they are not treated as a monotonic damage axis.

## Metrics

For every seed × condition:

- package exact / non-exact;
- total payload bit errors and BER;
- number of tables with payload bit errors;
- maximum share of payload bit errors contributed by one table;
- raw payload-symbol errors before Hamming correction;
- corrected payload-symbol errors after Hamming correction;
- number of codewords with corrected payload-symbol errors;
- number of tables with corrected codeword errors;
- A-layer structural locator score sentinel.

For each condition, failed-package distributions are summarized with median / p90 / max values rather than forcing an arbitrary binary “repairable” label.

## Interpretation rule

A future V20 reliability prototype is justified only if the observed failed-package errors are meaningfully sparse or concentrated. If transition-region failures are broadly distributed across many tables/codewords or have large payload BER, the correct conclusion is to reject a simple outer-redundancy rescue of current V18 and revisit the inner carrier/channel model instead.

Scientific failure is valid data. CI should fail only for harness/runtime errors, not because the results are unfavorable.
