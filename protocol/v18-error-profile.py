#!/usr/bin/env python3
"""Profile residual V18 decode errors after synthetic publication damage.

Synthetic-only. The carrier is unchanged. This harness measures whether failed
post-embedding / pre-seal packages contain sparse or diffuse residual payload
errors after the existing per-codeword Hamming correction.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import runpy
from pathlib import Path

import numpy as np

NOISE_ALPHAS = [0.12, 0.13, 0.14, 0.15, 0.16]
REQUANT_FACTORS = [1.00, 1.06, 1.10, 1.20, 1.22, 1.30]


def load(path: Path):
    return runpy.run_path(str(path))


def expected_payload_bytes(engine: dict, payload_bytes: int) -> bytes:
    fn = engine.get("synthetic_payload")
    if fn is None:
        raise RuntimeError("engine has no synthetic_payload")
    return fn(payload_bytes)


def expected_bits(payload: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(payload, dtype=np.uint8), bitorder="big")


def syndrome_nonzero(engine: dict, raw: np.ndarray, q: int) -> np.ndarray:
    T = engine["GF_TABLES"][q]
    s0 = np.bitwise_xor.reduce(raw[..., :q], axis=-1)
    s1 = raw[..., q].copy()
    for i in range(q):
        s1 ^= T[i, raw[..., i]]
    return (s0 != 0) | (s1 != 0)


def diagnose_table(engine: dict, pub: np.ndarray, manifest: dict, exp_bits: np.ndarray) -> dict:
    q = int(manifest["q"])
    m = int(manifest["m"])
    channels = int(manifest["channels"])
    n = int(manifest["points_per_block"])
    segments = int(manifest["segments"])
    valid = int(manifest["valid_codewords"])
    ppcw = int(manifest["payload_symbols_per_codeword"])
    bit_length = int(manifest["payload_bit_length"])
    delta = float(manifest["delta"])
    family = manifest["family"]

    if len(exp_bits) != bit_length:
        raise RuntimeError(f"expected bit length mismatch for table {manifest['table_id']}")

    spec = engine["family_spec"](family)
    x = engine["local_x"](n)
    B = engine["basis_for"](spec, x)
    U = engine["smooth_free_basis"](B)
    pinv = np.linalg.pinv(B)

    raw_payload_parts = []
    corrected_payload_parts = []
    correction_changed = 0
    syndrome_count = 0

    for s in range(segments):
        Y = np.asarray(pub[s*n:(s+1)*n, :], dtype=float).T
        Z = engine["transform_y"](Y, spec.transform)
        beta = Z @ pinv.T
        fit = beta @ B.T
        coeff = (Z - fit) @ U[:, :q+1]
        raw = engine["raw_symbols_from_coeff"](coeff, q, delta)
        corr = engine["hamming_correct"](raw, q)
        raw_payload_parts.append(raw[:, :ppcw])
        corrected_payload_parts.append(corr[:, :ppcw])
        correction_changed += int(np.sum(np.any(raw != corr, axis=1)))
        syndrome_count += int(np.sum(syndrome_nonzero(engine, raw, q)))

    raw_payload = np.concatenate(raw_payload_parts, axis=0)[:valid]
    corr_payload = np.concatenate(corrected_payload_parts, axis=0)[:valid]

    exp_syms, _ = engine["bits_to_symbols"](exp_bits, m)
    need = valid * ppcw
    if len(exp_syms) > need:
        raise RuntimeError(f"symbol capacity mismatch for table {manifest['table_id']}")
    exp_syms = np.pad(exp_syms, (0, need-len(exp_syms))).reshape(valid, ppcw)

    raw_err = raw_payload != exp_syms
    corr_err = corr_payload != exp_syms
    recovered = engine["symbols_to_bits"](corr_payload.reshape(-1), m, bit_length)
    bit_err = recovered != exp_bits

    return {
        "table_id": int(manifest["table_id"]),
        "family": family,
        "q": q,
        "payload_bits": bit_length,
        "valid_codewords": valid,
        "bit_errors": int(np.sum(bit_err)),
        "bit_error_rate": float(np.mean(bit_err)) if bit_length else 0.0,
        "raw_payload_symbol_errors": int(np.sum(raw_err)),
        "corrected_payload_symbol_errors": int(np.sum(corr_err)),
        "codewords_with_raw_payload_error": int(np.sum(np.any(raw_err, axis=1))),
        "codewords_with_corrected_payload_error": int(np.sum(np.any(corr_err, axis=1))),
        "correction_changed_codewords": correction_changed,
        "nonzero_syndrome_codewords": syndrome_count,
        "table_exact": bool(not np.any(bit_err)),
    }


def diagnose_package(protocol: dict, engine: dict, A, B: dict, damaged: bytes, exp_payload: bytes) -> dict:
    V3 = protocol["V3"]
    z = np.load(io.BytesIO(damaged))
    bits = expected_bits(exp_payload)
    tables = []
    for manifest in sorted(B["tables"], key=lambda t: int(t["payload_bit_offset"])):
        tid = int(manifest["table_id"])
        off = int(manifest["payload_bit_offset"])
        bit_length = int(manifest["payload_bit_length"])
        tables.append(diagnose_table(
            engine,
            z[f"table_{tid}_y"],
            manifest,
            bits[off:off+bit_length],
        ))

    total_bit_errors = int(sum(t["bit_errors"] for t in tables))
    bad_tables = [t for t in tables if t["bit_errors"] > 0]
    corrected_codeword_errors = int(sum(t["codewords_with_corrected_payload_error"] for t in tables))
    corrected_symbol_errors = int(sum(t["corrected_payload_symbol_errors"] for t in tables))
    raw_symbol_errors = int(sum(t["raw_payload_symbol_errors"] for t in tables))
    max_share = 0.0
    if total_bit_errors:
        max_share = max(t["bit_errors"] for t in tables) / total_bit_errors

    return {
        "package_exact": bool(total_bit_errors == 0),
        "payload_bits": int(len(bits)),
        "payload_bit_errors": total_bit_errors,
        "payload_ber": float(total_bit_errors / max(len(bits), 1)),
        "tables_with_bit_errors": int(len(bad_tables)),
        "max_table_bit_error_share": float(max_share),
        "raw_payload_symbol_errors": raw_symbol_errors,
        "corrected_payload_symbol_errors": corrected_symbol_errors,
        "codewords_with_corrected_payload_error": corrected_codeword_errors,
        "tables_with_corrected_codeword_error": int(sum(t["codewords_with_corrected_payload_error"] > 0 for t in tables)),
        "locator_score": float(V3["structural_score"](A, damaged)),
        "tables": tables,
    }


def percentile(values, q):
    return None if not values else float(np.percentile(np.asarray(values, dtype=float), q))


def aggregate(rows: list[dict], value_key: str, value: float) -> dict:
    failed = [r for r in rows if not r["package_exact"]]
    out = {
        value_key: float(value),
        "seed_count": len(rows),
        "exact_count": int(sum(r["package_exact"] for r in rows)),
        "exact_rate": float(np.mean([r["package_exact"] for r in rows])),
        "failed_count": len(failed),
        "locator_score_min": float(min(r["locator_score"] for r in rows)),
        "locator_score_max": float(max(r["locator_score"] for r in rows)),
    }
    if not failed:
        out["failed_profile"] = None
        return out

    bit_errors = [r["payload_bit_errors"] for r in failed]
    bers = [r["payload_ber"] for r in failed]
    bad_tables = [r["tables_with_bit_errors"] for r in failed]
    bad_codewords = [r["codewords_with_corrected_payload_error"] for r in failed]
    max_shares = [r["max_table_bit_error_share"] for r in failed]
    raw_syms = [r["raw_payload_symbol_errors"] for r in failed]
    corr_syms = [r["corrected_payload_symbol_errors"] for r in failed]
    out["failed_profile"] = {
        "bit_errors_median": percentile(bit_errors, 50),
        "bit_errors_p90": percentile(bit_errors, 90),
        "bit_errors_max": int(max(bit_errors)),
        "ber_median": percentile(bers, 50),
        "ber_p90": percentile(bers, 90),
        "tables_with_bit_errors_median": percentile(bad_tables, 50),
        "tables_with_bit_errors_p90": percentile(bad_tables, 90),
        "tables_with_bit_errors_max": int(max(bad_tables)),
        "bad_codewords_median": percentile(bad_codewords, 50),
        "bad_codewords_p90": percentile(bad_codewords, 90),
        "bad_codewords_max": int(max(bad_codewords)),
        "max_table_bit_error_share_median": percentile(max_shares, 50),
        "raw_payload_symbol_errors_median": percentile(raw_syms, 50),
        "corrected_payload_symbol_errors_median": percentile(corr_syms, 50),
        "failed_with_one_bad_table_fraction": float(np.mean([x == 1 for x in bad_tables])),
        "failed_with_le4_bad_codewords_fraction": float(np.mean([x <= 4 for x in bad_codewords])),
    }
    return out


def run(args):
    protocol = load(args.protocol)
    stats = load(args.statistics)
    engine = protocol["load_engine"](args.engine)
    V3 = protocol["V3"]
    A = V3["default_A"]()
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]

    noise_rows = {a: [] for a in NOISE_ALPHAS}
    requant_rows = {f: [] for f in REQUANT_FACTORS}

    for seed in seeds:
        B0, b0, _ = protocol["generate_B_b"](engine, args.payload_bytes, args.channels, seed)
        exp = expected_payload_bytes(engine, args.payload_bytes)
        B, b = V3["permute_package_to_A"](A, B0, b0)
        if hashlib.sha256(exp).hexdigest() != B["payload_sha256"]:
            raise RuntimeError(f"expected payload hash mismatch at seed {seed}")

        for alpha in NOISE_ALPHAS:
            damaged = stats["noisy_package"](b, B, seed, alpha)
            row = diagnose_package(protocol, engine, A, B, damaged, exp)
            row["seed"] = seed
            row["sigma_over_delta"] = alpha
            noise_rows[alpha].append(row)

        for factor in REQUANT_FACTORS:
            damaged = stats["requantize_package"](b, B, factor)
            row = diagnose_package(protocol, engine, A, B, damaged, exp)
            row["seed"] = seed
            row["factor"] = factor
            requant_rows[factor].append(row)

    out = {
        "version": "v18-publication-error-profile-v1",
        "scope": "synthetic-only",
        "frozen_plan": "results/v18-error-profile-plan.md",
        "configuration": {
            "seeds": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "noise_sigma_over_delta": NOISE_ALPHAS,
            "requant_factors": REQUANT_FACTORS,
            "damage_position": "post-embedding/post-A-assignment/pre-c-seal",
            "carrier_changes": "none",
        },
        "paired_additive_noise": {
            "summary": [aggregate(noise_rows[a], "sigma_over_delta", a) for a in NOISE_ALPHAS],
            "runs": [r for a in NOISE_ALPHAS for r in noise_rows[a]],
        },
        "requantization": {
            "summary": [aggregate(requant_rows[f], "factor", f) for f in REQUANT_FACTORS],
            "runs": [r for f in REQUANT_FACTORS for r in requant_rows[f]],
        },
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "version": out["version"],
        "paired_additive_noise": out["paired_additive_noise"]["summary"],
        "requantization": out["requantization"]["summary"],
    }, indent=2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--protocol", type=Path, default=Path("protocol/real-package-v18.py"))
    ap.add_argument("--statistics", type=Path, default=Path("protocol/v18-publication-statistics.py"))
    ap.add_argument("--seeds", default=",".join(str(i) for i in range(601, 625)))
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--out", type=Path, default=Path("v18-error-profile.json"))
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
