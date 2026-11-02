# Structural parity current integration — frozen gate

Scope: **synthetic/mock benchmark only**.

This gate is downstream of the passing `structural-parity-v3` single-table matrix. It does not re-tune the structural code or carrier. Its only purpose is to determine whether the candidate can rejoin the already-passing current technical + paper pipeline.

## Frozen stack

```text
A candidate       A-v4-erasure-xlen
structural layer  11 data tables + 1 XOR parity table
physical tables   12
carrier            src/noisy_host_package_v18_deterministic.py
basis              deterministic-dct-mgs-v1
V20                unchanged protocol/real-package-v20.py
paper-v6           unchanged tools/paper_v6.py
paper-v7           unchanged tools/paper_bundle_v7.py + finalize_paper_bundle_v7.py
```

No q/delta/RS/paper rule may be changed in response to the result.

## Fresh seeds

```text
1301..1308
representative seed = 1301
payload = 512 bytes
channels = 2
corpus = 2,000
near decoys = 1%
Top-K open window = 100
```

The same representative candidate package must feed:

```text
technical E2E
-> paper-v6
-> paper-v7
```

The same 8-seed machine result must feed paper E5.

## Frozen gate

Technical:

- 8/8 payload hashes unique;
- exact recovery 8/8;
- Recall@20 = 1;
- Recall@100 = 1;
- explicit decoy rejected;
- repair-field tamper rejected at authenticated envelope;
- representative B declares 11 data + 1 XOR parity and unchanged V20 geometry.

Paper-v6:

- consumes the same representative NPZ/B and same 8-seed E5 machine result;
- E5 is completed and passing;
- explicit synthetic/mock labels remain present;
- mandatory non-provenance limitation remains present.

Paper-v7:

- renders from that same base bundle;
- retains 12 raw-data CSV tables;
- produces 4 figures and traceability outputs;
- final validation/finalization completes without changing presentation code.

## Decision rule

A failure is retained as evidence. Do not alter 11+1 geometry, q/delta, V20 parity, morphology rules, or paper claim gates after seeing the result.

A pass establishes whole-system **viability** of the structural candidate in the declared CI environment. It does not by itself re-establish two-run semantic determinism; that remains a separate promotion requirement before replacing current A-v3/V18/V20.
