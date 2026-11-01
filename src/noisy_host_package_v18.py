#!/usr/bin/env python3
"""Noisy-host carrier V18 rebuild — synthetic-only.

This is a protocol-reintegration experiment, not a restoration of historical
V18 numbers.  It exposes the same minimal engine surface used by Protocol-v3:

    run_package, decode_table, bits_to_bytes, synthetic_payload

The carrier differs from clean-host V12 in one important way.  A non-zero
smooth residual host is generated in the free subspace first.  Payload symbols
are then embedded with modulo-QIM by moving each host coefficient to the
nearest lattice point in the required q-ary coset.  Thus the payload does not
assume a zero residual host.

Concrete q/QIM/geometry/publication parameters are emitted in per-package B.
Nothing in this module is locator state for long-lived A.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


Q_MODES = {
    2: {"m": 1, "poly": 0b11, "delta_multiple": 2.0},
    4: {"m": 2, "poly": 0b111, "delta_multiple": 2.5},
}
HOST_SIGMA_MULTIPLE = 6.0
HOST_ACTIVE_DIMS = 12
BENCHMARK_SEED = 0


def set_benchmark_seed(seed: int):
    global BENCHMARK_SEED
    BENCHMARK_SEED = int(seed)


def synthetic_payload(nbytes: int) -> bytes:
    return hashlib.shake_256(b"noisy-host-v18-synthetic").digest(nbytes)


# ---------------------------------------------------------------------------
# GF(2^m), q-ary Hamming [q+1,q-1,3], bit packing
# ---------------------------------------------------------------------------

def gf_mul_scalar(a: int, b: int, m: int, poly: int) -> int:
    out = 0
    top = 1 << m
    mask = top - 1
    a, b = int(a), int(b)
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & top:
            a ^= poly
    return out & mask


def gf_table(q: int) -> np.ndarray:
    cfg = Q_MODES[q]
    return np.asarray(
        [[gf_mul_scalar(a, b, cfg["m"], cfg["poly"]) for b in range(q)] for a in range(q)],
        dtype=np.uint16,
    )


GF_TABLES = {q: gf_table(q) for q in Q_MODES}


def hamming_encode(info: np.ndarray, q: int) -> np.ndarray:
    T = GF_TABLES[q]
    info = np.asarray(info, dtype=np.uint16)
    if info.shape[-1] != q - 1:
        raise ValueError("bad info width")
    cw = np.zeros(info.shape[:-1] + (q + 1,), dtype=np.uint16)
    cw[..., : q - 1] = info
    p1 = np.bitwise_xor.reduce(info, axis=-1)
    cw[..., q - 1] = p1
    p2 = np.zeros(info.shape[:-1], dtype=np.uint16)
    for i in range(q - 1):
        p2 ^= T[i, info[..., i]]
    p2 ^= T[q - 1, p1]
    cw[..., q] = p2
    return cw


def correction_lookup(q: int):
    T = GF_TABLES[q]
    pos = np.full((q, q), -1, dtype=np.int16)
    err = np.zeros((q, q), dtype=np.uint16)
    for i in range(q):
        for e in range(1, q):
            pos[e, T[e, i]] = i
            err[e, T[e, i]] = e
    for e in range(1, q):
        pos[0, e] = q
        err[0, e] = e
    return pos, err


CORR = {q: correction_lookup(q) for q in Q_MODES}


def hamming_correct(received: np.ndarray, q: int) -> np.ndarray:
    T = GF_TABLES[q]
    pos_lut, err_lut = CORR[q]
    out = np.asarray(received, dtype=np.uint16).copy()
    s0 = np.bitwise_xor.reduce(out[..., :q], axis=-1)
    s1 = out[..., q].copy()
    for i in range(q):
        s1 ^= T[i, out[..., i]]
    pos = pos_lut[s0, s1]
    err = err_lut[s0, s1]
    flat = out.reshape(-1, q + 1)
    posf = np.asarray(pos).reshape(-1)
    errf = np.asarray(err).reshape(-1)
    rows = np.nonzero(posf >= 0)[0]
    if len(rows):
        flat[rows, posf[rows]] ^= errf[rows]
    return flat.reshape(out.shape)


def bytes_to_bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="big")


def bits_to_bytes(bits: np.ndarray) -> bytes:
    bits = np.asarray(bits, dtype=np.uint8).reshape(-1)
    pad = (-len(bits)) % 8
    if pad:
        bits = np.pad(bits, (0, pad))
    return np.packbits(bits, bitorder="big").tobytes()


def bits_to_symbols(bits: np.ndarray, m: int):
    bits = np.asarray(bits, dtype=np.uint8).reshape(-1)
    original = len(bits)
    pad = (-len(bits)) % m
    if pad:
        bits = np.pad(bits, (0, pad))
    g = bits.reshape(-1, m)
    weights = (1 << np.arange(m - 1, -1, -1)).astype(np.uint16)
    return (g @ weights).astype(np.uint16), original


def symbols_to_bits(symbols: np.ndarray, m: int, bit_length: int):
    s = np.asarray(symbols, dtype=np.uint16).reshape(-1)
    shifts = np.arange(m - 1, -1, -1, dtype=np.uint16)
    bits = ((s[:, None] >> shifts[None, :]) & 1).astype(np.uint8).reshape(-1)
    return bits[:bit_length]


# ---------------------------------------------------------------------------
# Macro family and smooth free subspace
# ---------------------------------------------------------------------------
@dataclass
class FamilySpec:
    family: str
    transform: str
    params: dict
    protected_dims: int


def family_spec(family: str) -> FamilySpec:
    if family == "affine":
        return FamilySpec("affine", "identity", {}, 2)
    if family == "periodic":
        return FamilySpec("periodic", "identity", {"cycles": 1.5}, 5)
    if family == "saturation":
        return FamilySpec("saturation", "identity", {"tau": 0.75}, 2)
    if family == "gaussian":
        return FamilySpec("gaussian", "log", {}, 3)
    raise ValueError(family)


def local_x(n: int):
    return np.linspace(-1.0, 1.0, n, endpoint=True)


def basis_for(spec: FamilySpec, x: np.ndarray):
    if spec.family == "affine":
        return np.column_stack([np.ones_like(x), x])
    if spec.family == "periodic":
        w = 2.0 * np.pi * float(spec.params["cycles"]) / (x[-1] - x[0])
        return np.column_stack([
            np.ones_like(x), np.sin(w*x), np.cos(w*x),
            np.sin(2*w*x), np.cos(2*w*x),
        ])
    if spec.family == "saturation":
        t = 2.0 * (x + 1.0)
        return np.column_stack([np.ones_like(x), np.exp(-t / float(spec.params["tau"]))])
    if spec.family == "gaussian":
        return np.column_stack([np.ones_like(x), x, x*x])
    raise ValueError(spec.family)


def channel_beta(spec: FamilySpec, channel: int, channels: int):
    phase = 2.0 * np.pi * channel / max(channels, 1)
    if spec.family == "affine":
        return np.asarray([50.0 + 0.25*channel, 8.0 + 0.7*np.sin(phase)])
    if spec.family == "periodic":
        return np.asarray([
            55.0 + 0.20*channel,
            7.0 + 0.6*np.sin(phase),
            1.6*np.cos(0.3*phase),
            1.4 + 0.3*np.cos(phase),
            0.5*np.sin(phase),
        ])
    if spec.family == "saturation":
        return np.asarray([58.0 + 0.2*channel, -(24.0 + 1.2*np.sin(phase))])
    if spec.family == "gaussian":
        mu = 0.10*np.sin(phase)
        sigma = 0.55 + 0.03*np.cos(phase)
        amp = 45.0 + 1.5*np.sin(phase)
        c = -1.0/(2*sigma*sigma)
        b = mu/(sigma*sigma)
        a = math.log(amp) - mu*mu/(2*sigma*sigma)
        return np.asarray([a, b, c])
    raise ValueError(spec.family)


def inverse_y(z: np.ndarray, transform: str):
    return np.exp(z) if transform == "log" else np.asarray(z, dtype=float)


def transform_y(y: np.ndarray, transform: str):
    return np.log(np.asarray(y, dtype=float)) if transform == "log" else np.asarray(y, dtype=float)


def second_difference_matrix(n: int):
    D = np.zeros((n-2, n), dtype=float)
    for i in range(n-2):
        D[i, i:i+3] = (1.0, -2.0, 1.0)
    return D


def smooth_free_basis(B: np.ndarray):
    Q, _ = np.linalg.qr(B, mode="complete")
    rank = int(np.linalg.matrix_rank(B))
    U0 = Q[:, rank:]
    D2 = second_difference_matrix(B.shape[0])
    G = (D2 @ U0).T @ (D2 @ U0)
    vals, V = np.linalg.eigh(G)
    U = U0 @ V[:, np.argsort(vals)]
    for j in range(U.shape[1]):
        k = int(np.argmax(np.abs(U[:, j])))
        if U[k, j] < 0:
            U[:, j] *= -1
    return U


def baseline(spec: FamilySpec, n: int, channel: int, channels: int):
    x = local_x(n)
    B = basis_for(spec, x)
    beta = channel_beta(spec, channel, channels)
    z = B @ beta
    return x, B, z, inverse_y(z, spec.transform)


def table_n(table_id: int) -> int:
    # Public x-grid lengths are unique and independent of q.
    return 24 + 2 * int(table_id)


# ---------------------------------------------------------------------------
# Host-aware modulo-QIM
# ---------------------------------------------------------------------------
def publication_params(spec: FamilySpec, n: int, channels: int, q: int):
    Y0 = np.asarray([baseline(spec, n, c, channels)[3] for c in range(channels)])
    if spec.transform == "log":
        model = "log_step"
        step = math.log1p(1e-3)
    else:
        model = "absolute_step"
        step = float(np.max(Y0) - np.min(Y0)) * 1e-3
    return model, step, step * float(Q_MODES[q]["delta_multiple"])


def host_coefficients(rng: np.random.Generator, slots: int, free_dims: int, sigma: float):
    active = min(HOST_ACTIVE_DIMS, free_dims)
    coeff = np.zeros((slots, free_dims), dtype=float)
    decay = 1.0 / (1.0 + 0.18*np.arange(active, dtype=float))
    coeff[:, :active] = rng.normal(0.0, sigma, size=(slots, active)) * decay[None, :]
    return coeff


def coset_quantize(host: np.ndarray, symbols: np.ndarray, q: int, delta: float):
    """Nearest lattice coefficient whose rounded integer index is symbol mod q."""
    host = np.asarray(host, dtype=float)
    symbols = np.asarray(symbols, dtype=np.int64)
    cycles = np.rint((host / delta - symbols) / q)
    return (symbols + q*cycles) * delta


def raw_symbols_from_coeff(coeff: np.ndarray, q: int, delta: float):
    idx = np.rint(np.asarray(coeff, dtype=float) / delta).astype(np.int64)
    return np.mod(idx, q).astype(np.uint16)


def payload_symbols_per_codeword(q: int) -> int:
    return 1 if q == 2 else q - 2


def embed_payload_symbols(payload: np.ndarray, host_first: np.ndarray, q: int, delta: float):
    """Return Hamming codewords and nearest-coset encoded coefficients."""
    payload = np.asarray(payload, dtype=np.uint16)
    host_first = np.asarray(host_first, dtype=float)
    blocks = len(payload)
    if q == 2:
        info = payload.reshape(blocks, 1)
        cw = hamming_encode(info, q)
        return cw, coset_quantize(host_first, cw, q, delta)

    best_cost = np.full(blocks, np.inf)
    best_cw = np.empty((blocks, q+1), dtype=np.uint16)
    best_coeff = np.empty((blocks, q+1), dtype=float)
    for shape in range(q):
        info = np.empty((blocks, q-1), dtype=np.uint16)
        info[:, :q-2] = payload
        info[:, q-2] = shape
        cw = hamming_encode(info, q)
        coeff = coset_quantize(host_first, cw, q, delta)
        cost = np.sum((coeff-host_first)**2, axis=1)
        take = cost < best_cost
        best_cost[take] = cost[take]
        best_cw[take] = cw[take]
        best_coeff[take] = coeff[take]
    return best_cw, best_coeff


def publish(z: np.ndarray, y: np.ndarray, model: str, step: float, transform: str):
    if model == "log_step":
        zp = np.round(z / step) * step
        return zp, inverse_y(zp, transform)
    yp = np.round(y / step) * step
    return transform_y(yp, transform), yp


def nrmse(reference: np.ndarray, test: np.ndarray):
    ref = np.asarray(reference, dtype=float)
    denom = float(np.ptp(ref))
    if denom <= 1e-15:
        denom = float(np.std(ref)) or 1.0
    return float(np.sqrt(np.mean((np.asarray(test)-ref)**2)) / denom)


def calibration(table_id: int, family: str, budget: float, q: int, channels: int, blocks: int = 1024):
    spec = family_spec(family)
    n = table_n(table_id)
    x, B, z0, y0 = baseline(spec, n, 0, channels)
    U = smooth_free_basis(B)
    if U.shape[1] < q+1:
        raise RuntimeError("insufficient free dimensions")
    model, step, delta = publication_params(spec, n, channels, q)
    sigma = HOST_SIGMA_MULTIPLE * step
    rng = np.random.default_rng(18_000_000 + table_id*1009 + q*37)
    host_c = host_coefficients(rng, blocks, U.shape[1], sigma)
    ppcw = payload_symbols_per_codeword(q)
    payload = rng.integers(0, q, size=(blocks, ppcw), dtype=np.uint16)
    cw, encoded_first = embed_payload_symbols(payload, host_c[:, :q+1], q, delta)
    encoded_c = host_c.copy()
    encoded_c[:, :q+1] = encoded_first
    zh = z0[None, :] + host_c @ U.T
    ze = z0[None, :] + encoded_c @ U.T
    yh = inverse_y(zh, spec.transform)
    ye = inverse_y(ze, spec.transform)
    zp, yp = publish(ze, ye, model, step, spec.transform)

    pinv = np.linalg.pinv(B)
    beta = zp @ pinv.T
    fit = beta @ B.T
    coeff = (zp-fit) @ U[:, :q+1]
    raw = raw_symbols_from_coeff(coeff, q, delta)
    corrected = hamming_correct(raw, q)
    got = corrected[:, :ppcw]
    exact = float(np.mean(np.all(got == payload, axis=1)))
    raw_ser = float(np.mean(raw != cw))
    adjust_nrmse = float(np.mean([nrmse(a, b) for a, b in zip(yh, yp)]))
    host_rms = float(np.sqrt(np.mean((yh-y0[None, :])**2)))
    adjustment_rms = float(np.sqrt(np.mean((yp-yh)**2)))
    ratio = float(adjustment_rms / max(host_rms, 1e-15))
    return {
        "table_id": table_id,
        "family": family,
        "q": q,
        "m": Q_MODES[q]["m"],
        "budget_nrmse": budget,
        "points_per_block": n,
        "publication_model": model,
        "publication_step": step,
        "delta": delta,
        "host_sigma": sigma,
        "host_active_dims": min(HOST_ACTIVE_DIMS, U.shape[1]),
        "exact_block_recovery": exact,
        "raw_symbol_error_rate": raw_ser,
        "host_adjustment_nrmse": adjust_nrmse,
        "host_residual_rms": host_rms,
        "embedding_adjustment_rms": adjustment_rms,
        "adjustment_to_host_rms_ratio": ratio,
        "feasible": bool(exact == 1.0 and adjust_nrmse <= budget),
    }


def choose_mode(table_id: int, family: str, budget: float, channels: int):
    trials = []
    q4 = calibration(table_id, family, budget, 4, channels)
    trials.append(q4)
    if q4["feasible"]:
        return q4, trials
    q2 = calibration(table_id, family, budget, 2, channels)
    trials.append(q2)
    if q2["feasible"]:
        return q2, trials
    return None, trials


TABLE_BLUEPRINT = [
    ("affine", 0.0045), ("affine", 0.0150), ("affine", 0.0350),
    ("periodic", 0.0045), ("periodic", 0.0150), ("periodic", 0.0350),
    ("saturation", 0.0045), ("saturation", 0.0150), ("saturation", 0.0350),
    ("gaussian", 0.0045), ("gaussian", 0.0150), ("gaussian", 0.0350),
]


def split_bits(total_bits: np.ndarray, tables: int):
    n = len(total_bits)
    starts = [round(i*n/tables) for i in range(tables+1)]
    return [total_bits[starts[i]:starts[i+1]] for i in range(tables)]


def table_rng(table_id: int):
    # Payload and host seeds are domain-separated by the protocol harness.
    return np.random.default_rng(18_500_000 + BENCHMARK_SEED*10007 + table_id*1009)


def encode_table(bit_chunk: np.ndarray, table_id: int, family: str, chosen: dict, channels: int):
    q = int(chosen["q"])
    m = int(chosen["m"])
    spec = family_spec(family)
    n = int(chosen["points_per_block"])
    x = local_x(n)
    B = basis_for(spec, x)
    U = smooth_free_basis(B)
    ppcw = payload_symbols_per_codeword(q)

    syms, bit_length = bits_to_symbols(bit_chunk, m)
    blocks = math.ceil(len(syms) / ppcw)
    padded = np.pad(syms, (0, blocks*ppcw-len(syms))).reshape(blocks, ppcw)
    segments = math.ceil(blocks/channels)
    slots = segments*channels
    padded_payload = np.zeros((slots, ppcw), dtype=np.uint16)
    padded_payload[:blocks] = padded

    rng = table_rng(table_id)
    host_c = host_coefficients(rng, slots, U.shape[1], float(chosen["host_sigma"]))
    cw, encoded_first = embed_payload_symbols(padded_payload, host_c[:, :q+1], q, float(chosen["delta"]))
    encoded_c = host_c.copy()
    encoded_c[:, :q+1] = encoded_first

    z0 = np.asarray([baseline(spec, n, c, channels)[2] for c in range(channels)])
    channel_ids = np.arange(slots) % channels
    zh = z0[channel_ids] + host_c @ U.T
    ze = z0[channel_ids] + encoded_c @ U.T
    yh = inverse_y(zh, spec.transform)
    ye = inverse_y(ze, spec.transform)
    zp, yp = publish(ze, ye, chosen["publication_model"], float(chosen["publication_step"]), spec.transform)

    pub = np.empty((segments*n, channels), dtype=float)
    for s in range(segments):
        pub[s*n:(s+1)*n, :] = yp[s*channels:(s+1)*channels].T

    host_rms = float(np.sqrt(np.mean((yh - inverse_y(z0[channel_ids], spec.transform))**2)))
    adjustment_rms = float(np.sqrt(np.mean((yp-yh)**2)))
    manifest = {
        "table_id": table_id,
        "family": family,
        "transform": spec.transform,
        "carrier_mode": "host-aware-modulo-qim-v18",
        "q": q,
        "m": m,
        "poly": Q_MODES[q]["poly"],
        "channels": channels,
        "points_per_block": n,
        "segments": segments,
        "valid_codewords": blocks,
        "payload_symbols_per_codeword": ppcw,
        "payload_bit_length": bit_length,
        "publication_step": chosen["publication_step"],
        "publication_model": chosen["publication_model"],
        "delta": chosen["delta"],
        "residual_budget_nrmse": chosen["budget_nrmse"],
        "calibration_host_adjustment_nrmse": chosen["host_adjustment_nrmse"],
        "calibration_exact_block_recovery": chosen["exact_block_recovery"],
        "host_model": {
            "kind": "smooth-free-subspace-gaussian",
            "benchmark_seed": BENCHMARK_SEED,
            "sigma": chosen["host_sigma"],
            "active_dims": chosen["host_active_dims"],
        },
        "observed_host_residual_rms": host_rms,
        "observed_embedding_adjustment_rms": adjustment_rms,
        "observed_adjustment_to_host_rms_ratio": float(adjustment_rms/max(host_rms, 1e-15)),
    }
    return x, pub, manifest


def decode_table(pub: np.ndarray, manifest: dict):
    family = manifest["family"]
    q = int(manifest["q"])
    m = int(manifest["m"])
    channels = int(manifest["channels"])
    n = int(manifest["points_per_block"])
    segments = int(manifest["segments"])
    valid = int(manifest["valid_codewords"])
    ppcw = int(manifest["payload_symbols_per_codeword"])
    delta = float(manifest["delta"])
    spec = family_spec(family)
    x = local_x(n)
    B = basis_for(spec, x)
    U = smooth_free_basis(B)
    recovered = np.empty((segments*channels, ppcw), dtype=np.uint16)
    k = 0
    pinv = np.linalg.pinv(B)
    for s in range(segments):
        Y = pub[s*n:(s+1)*n, :].T
        Z = transform_y(Y, spec.transform)
        beta = Z @ pinv.T
        fit = beta @ B.T
        coeff = (Z-fit) @ U[:, :q+1]
        raw = raw_symbols_from_coeff(coeff, q, delta)
        corr = hamming_correct(raw, q)
        recovered[k:k+channels] = corr[:, :ppcw]
        k += channels
    recovered = recovered[:valid].reshape(-1)
    return symbols_to_bits(recovered, m, int(manifest["payload_bit_length"]))


def run_package(payload_bytes: int = 4096, channels: int = 4, out_dir: Path = Path("v18_out")):
    out_dir.mkdir(parents=True, exist_ok=True)
    selected, calibrations, failed = [], [], []
    for i, (family, budget) in enumerate(TABLE_BLUEPRINT):
        chosen, trials = choose_mode(i, family, budget, channels)
        calibrations.append({"table_id": i, "family": family, "budget": budget, "trials": trials})
        if chosen is None:
            failed.append(i)
        else:
            selected.append((family, chosen))

    if failed:
        failure = {
            "version": "noisy-host-v18-rebuild",
            "scope": "synthetic-only",
            "status": "FAIL_CALIBRATION",
            "failed_table_ids": failed,
            "calibrations": calibrations,
        }
        (out_dir/"noisy_host_v18_failure.json").write_text(json.dumps(failure, indent=2), encoding="utf-8")
        print(json.dumps(failure, indent=2))
        raise RuntimeError(f"V18 calibration failed for tables {failed}")

    payload = synthetic_payload(payload_bytes)
    bits = bytes_to_bits(payload)
    chunks = split_bits(bits, len(selected))
    arrays, table_manifests = {}, []
    bit_cursor = 0
    for i, ((family, chosen), chunk) in enumerate(zip(selected, chunks)):
        x, pub, tm = encode_table(chunk, i, family, chosen, channels)
        tm["payload_bit_offset"] = bit_cursor
        bit_cursor += len(chunk)
        arrays[f"table_{i}_x"] = x
        arrays[f"table_{i}_y"] = pub
        table_manifests.append(tm)

    package_filename = "published_noisy_host_v18.npz"
    manifest_filename = "manifest_noisy_host_v18.json"
    package_path = out_dir/package_filename
    np.savez_compressed(package_path, **arrays)
    manifest = {
        "version": "noisy-host-v18-rebuild",
        "scope": "synthetic-only",
        "payload_bytes": payload_bytes,
        "payload_bit_length": len(bits),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "q_candidates": [4, 2],
        "host_sigma_multiple": HOST_SIGMA_MULTIPLE,
        "tables": table_manifests,
    }
    manifest_path = out_dir/manifest_filename
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    loaded = np.load(package_path)
    recovered_bits = np.zeros(len(bits), dtype=np.uint8)
    for tm in table_manifests:
        tid = int(tm["table_id"])
        rb = decode_table(loaded[f"table_{tid}_y"], tm)
        off = int(tm["payload_bit_offset"])
        recovered_bits[off:off+len(rb)] = rb
    recovered = bits_to_bytes(recovered_bits)[:payload_bytes]

    total_rows = sum(arrays[f"table_{i}_y"].shape[0] for i in range(len(selected)))
    total_values = total_rows*channels
    q_counts = {str(q): sum(1 for _, c in selected if c["q"] == q) for q in (2,4)}
    ratios = [float(t["observed_adjustment_to_host_rms_ratio"]) for t in table_manifests]
    result = {
        "version": "noisy-host-v18-rebuild",
        "scope": "synthetic-only",
        "status": "PASS" if recovered == payload else "FAIL_RECOVERY",
        "benchmark_seed": BENCHMARK_SEED,
        "payload_bytes": payload_bytes,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "decoded_sha256": hashlib.sha256(recovered).hexdigest(),
        "exact_recovery": recovered == payload,
        "channels_per_table": channels,
        "table_count": len(selected),
        "q_distribution": q_counts,
        "published_rows_total": total_rows,
        "published_numeric_values_total": total_values,
        "gross_bits_per_numeric_value": payload_bytes*8/total_values,
        "median_adjustment_to_host_rms_ratio": float(np.median(ratios)),
        "max_adjustment_to_host_rms_ratio": float(np.max(ratios)),
        "manifest_filename": manifest_filename,
        "package_filename": package_filename,
        "selected_tables": [
            {
                "table_id": i,
                "family": family,
                "budget_nrmse": chosen["budget_nrmse"],
                "q": chosen["q"],
                "calibration_exact_block_recovery": chosen["exact_block_recovery"],
                "calibration_host_adjustment_nrmse": chosen["host_adjustment_nrmse"],
                "calibration_adjustment_to_host_rms_ratio": chosen["adjustment_to_host_rms_ratio"],
            }
            for i, (family, chosen) in enumerate(selected)
        ],
        "calibrations": calibrations,
    }
    (out_dir/"noisy_host_v18_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload-bytes", type=int, default=4096)
    ap.add_argument("--channels", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out-dir", type=Path, default=Path("v18_out"))
    args = ap.parse_args()
    set_benchmark_seed(args.seed)
    result = run_package(args.payload_bytes, args.channels, args.out_dir)
    slim = {k:v for k,v in result.items() if k != "calibrations"}
    print(json.dumps(slim, indent=2))


if __name__ == "__main__":
    main()
