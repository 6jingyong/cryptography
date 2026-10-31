#!/usr/bin/env python3
"""
q8_package_v10.py

Synthetic-only package-level q=8 protected-subspace benchmark.

A package contains multiple synthetic "tables". Each table has:
  - one shared x axis
  - multiple deterministic periodic y-series
  - local 14-point blocks
  - 5 protected macro dimensions
  - 9 free carrier dimensions
  - GF(8) [9,7,3] Hamming
  - 6 payload + 1 shaping + 2 parity symbols

The benchmark payload is deterministic synthetic high-entropy bytes generated
inside the program. It does NOT read arbitrary payload files and does NOT
generate deceptive scientific claims.

Dependencies: numpy only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

GF_MOD = 0b1011
LEVELS = np.asarray([-0.5, 0.5, -1.5, 1.5, -2.5, 2.5, -3.5, 3.5], dtype=np.float64)
H_COLS = [(1, a) for a in range(8)] + [(0, 1)]

BLOCK_POINTS = 14
PROTECTED_DIMS = 5
CODE_N = 9
INFO_K = 7
PAYLOAD_SYMBOLS = 6
BITS_PER_SYMBOL = 3
PAYLOAD_BITS_PER_BLOCK = PAYLOAD_SYMBOLS * BITS_PER_SYMBOL  # 18


def gf_mul_scalar(a: int, b: int) -> int:
    out = 0
    a = int(a)
    b = int(b)
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 0b1000:
            a ^= GF_MOD
    return out & 7


MUL = np.asarray(
    [[gf_mul_scalar(a, b) for b in range(8)] for a in range(8)],
    dtype=np.uint8,
)

# syndrome -> one-symbol correction lookup
CORR_POS = np.full((8, 8), -1, dtype=np.int8)
CORR_ERR = np.zeros((8, 8), dtype=np.uint8)
for pos, (h0, h1) in enumerate(H_COLS):
    for err in range(1, 8):
        s0 = gf_mul_scalar(err, h0)
        s1 = gf_mul_scalar(err, h1)
        CORR_POS[s0, s1] = pos
        CORR_ERR[s0, s1] = err


def bytes_to_symbols(data: bytes) -> tuple[np.ndarray, int]:
    """Vectorized 3 bytes -> 8 GF(8) symbols, with a small tail fallback."""
    raw = np.frombuffer(data, dtype=np.uint8)
    bit_length = len(data) * 8
    full = (len(raw) // 3) * 3
    groups = raw[:full].reshape(-1, 3)
    if len(groups):
        b0 = groups[:, 0]
        b1 = groups[:, 1]
        b2 = groups[:, 2]
        out = np.empty((len(groups), 8), dtype=np.uint8)
        out[:, 0] = b0 >> 5
        out[:, 1] = (b0 >> 2) & 7
        out[:, 2] = ((b0 & 3) << 1) | (b1 >> 7)
        out[:, 3] = (b1 >> 4) & 7
        out[:, 4] = (b1 >> 1) & 7
        out[:, 5] = ((b1 & 1) << 2) | (b2 >> 6)
        out[:, 6] = (b2 >> 3) & 7
        out[:, 7] = b2 & 7
        syms = out.reshape(-1)
    else:
        syms = np.empty(0, dtype=np.uint8)

    if full < len(raw):
        tail_bits = np.unpackbits(raw[full:], bitorder="big")
        pad = (-len(tail_bits)) % 3
        if pad:
            tail_bits = np.pad(tail_bits, (0, pad))
        tri = tail_bits.reshape(-1, 3)
        tail = (4 * tri[:, 0] + 2 * tri[:, 1] + tri[:, 2]).astype(np.uint8)
        syms = np.concatenate([syms, tail])
    return syms, bit_length


def symbols_to_bytes(symbols: np.ndarray, bit_length: int) -> bytes:
    """Vectorized 8 GF(8) symbols -> 3 bytes, with a small tail fallback."""
    s = np.asarray(symbols, dtype=np.uint8).reshape(-1)
    full = (len(s) // 8) * 8
    groups = s[:full].reshape(-1, 8)
    if len(groups):
        out = np.empty((len(groups), 3), dtype=np.uint8)
        out[:, 0] = (groups[:, 0] << 5) | (groups[:, 1] << 2) | (groups[:, 2] >> 1)
        out[:, 1] = ((groups[:, 2] & 1) << 7) | (groups[:, 3] << 4) | (groups[:, 4] << 1) | (groups[:, 5] >> 2)
        out[:, 2] = ((groups[:, 5] & 3) << 6) | (groups[:, 6] << 3) | groups[:, 7]
        raw = out.reshape(-1)
    else:
        raw = np.empty(0, dtype=np.uint8)

    if full < len(s):
        tail = s[full:]
        bits = np.empty((len(tail), 3), dtype=np.uint8)
        bits[:, 0] = (tail >> 2) & 1
        bits[:, 1] = (tail >> 1) & 1
        bits[:, 2] = tail & 1
        flat = bits.reshape(-1)
        need_tail_bits = bit_length - len(raw) * 8
        flat = flat[:need_tail_bits]
        pad = (-len(flat)) % 8
        if pad:
            flat = np.pad(flat, (0, pad))
        tail_raw = np.packbits(flat, bitorder="big")
        raw = np.concatenate([raw, tail_raw])

    return raw.tobytes()[: math.ceil(bit_length / 8)]


def deterministic_payload(nbytes: int, seed: str = "q8-package-v10") -> bytes:
    return hashlib.shake_256(seed.encode("utf-8")).digest(nbytes)


def macro_basis(x: np.ndarray, period: float) -> np.ndarray:
    w = 2.0 * np.pi / period
    return np.column_stack(
        [
            np.ones_like(x),
            np.sin(w * x),
            np.cos(w * x),
            np.sin(2.0 * w * x),
            np.cos(2.0 * w * x),
        ]
    )


def macro_curve(x: np.ndarray, period: float, table_id: int, channel_id: int, channels: int) -> np.ndarray:
    w = 2.0 * np.pi / period
    phase = 2.0 * np.pi * channel_id / channels + 0.11 * table_id
    amp = 7.0 + 1.2 * np.sin(phase + 0.07 * table_id)
    harmonic = 1.0 + 0.5 * np.cos(2.0 * phase - 0.03 * table_id)
    offset = 55.0 + 0.14 * channel_id + 0.45 * table_id
    return (
        offset
        + amp * np.sin(w * x + phase)
        + 1.5 * np.cos(w * x - 0.28 * phase)
        + harmonic * np.sin(2.0 * w * x + 0.18 + 0.45 * phase)
    )


def second_difference_matrix(n: int) -> np.ndarray:
    D = np.zeros((n - 2, n), dtype=np.float64)
    for i in range(n - 2):
        D[i, i] = 1.0
        D[i, i + 1] = -2.0
        D[i, i + 2] = 1.0
    return D


def smooth_free_basis(B: np.ndarray) -> np.ndarray:
    Q, _ = np.linalg.qr(B, mode="complete")
    rank = int(np.linalg.matrix_rank(B))
    U0 = Q[:, rank:]
    D2 = second_difference_matrix(B.shape[0])
    G = (D2 @ U0).T @ (D2 @ U0)
    eigvals, V = np.linalg.eigh(G)
    U = U0 @ V[:, np.argsort(eigvals)]
    for j in range(U.shape[1]):
        k = int(np.argmax(np.abs(U[:, j])))
        if U[k, j] < 0:
            U[:, j] *= -1.0
    return U


def fit_macro(B: np.ndarray, Y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Y: (..., n)
    pinv = np.linalg.pinv(B)
    beta = Y @ pinv.T
    fit = beta @ B.T
    return beta, fit


def hamming_encode_batch(info6: np.ndarray, shaping: np.ndarray) -> np.ndarray:
    """
    info6: (N, 6), shaping: (N,)
    Returns codewords (N, 9).
    """
    N = info6.shape[0]
    info7 = np.empty((N, 7), dtype=np.uint8)
    info7[:, :6] = info6
    info7[:, 6] = shaping

    cw = np.zeros((N, 9), dtype=np.uint8)
    cw[:, :7] = info7

    p7 = np.bitwise_xor.reduce(info7, axis=1)
    cw[:, 7] = p7

    p8 = np.zeros(N, dtype=np.uint8)
    for i in range(7):
        p8 ^= MUL[i, info7[:, i]]
    p8 ^= MUL[7, p7]
    cw[:, 8] = p8
    return cw


def hamming_correct_batch(r: np.ndarray) -> np.ndarray:
    out = np.asarray(r, dtype=np.uint8).copy()

    s0 = np.bitwise_xor.reduce(out[:, :8], axis=1)
    s1 = out[:, 8].copy()
    for i in range(8):
        s1 ^= MUL[i, out[:, i]]

    pos = CORR_POS[s0, s1]
    err = CORR_ERR[s0, s1]
    bad = pos >= 0
    rows = np.nonzero(bad)[0]
    if len(rows):
        out[rows, pos[rows]] ^= err[rows]
    return out


def shaping_metric_matrix(U: np.ndarray) -> np.ndarray:
    D2 = second_difference_matrix(U.shape[0])
    # cost = ||U c||^2 + 0.25 ||D2 U c||^2 = c^T M c
    return U.T @ U + 0.25 * (D2 @ U).T @ (D2 @ U)


def choose_shaped_codewords(info6: np.ndarray, M: np.ndarray, batch_size: int = 50000) -> np.ndarray:
    """
    Vectorized 8-way shaping search. delta^2 cancels in the argmin.
    """
    N = info6.shape[0]
    out = np.empty((N, 9), dtype=np.uint8)

    for start in range(0, N, batch_size):
        end = min(start + batch_size, N)
        block = info6[start:end]
        n = len(block)

        best_cost = np.full(n, np.inf, dtype=np.float64)
        best_cw = np.zeros((n, 9), dtype=np.uint8)

        for shape in range(8):
            shaping = np.full(n, shape, dtype=np.uint8)
            cw = hamming_encode_batch(block, shaping)
            coeff = LEVELS[cw]  # (n, 9)
            cost = np.einsum("bi,ij,bj->b", coeff, M, coeff, optimize=True)
            take = cost < best_cost
            if np.any(take):
                best_cost[take] = cost[take]
                best_cw[take] = cw[take]
        out[start:end] = best_cw
    return out


def coeffs_to_symbols(coeff: np.ndarray, delta: float) -> np.ndarray:
    scaled = coeff / float(delta)
    return np.argmin(
        np.abs(scaled[..., None] - LEVELS[None, None, :]),
        axis=-1,
    ).astype(np.uint8)


def roughness_rows(Y: np.ndarray) -> np.ndarray:
    d2 = np.diff(Y, n=2, axis=-1)
    return np.sum(d2 * d2, axis=-1)


@dataclass
class TableMetrics:
    table_id: int
    channels: int
    blocks: int
    rows: int
    publication_step: float
    delta: float
    raw_symbol_error_rate: float
    nrmse_percent: float
    mean_roughness_ratio: float
    max_roughness_ratio: float
    cross_channel_corr_mae: float
    macro_beta_relative_error_mean: float


def split_block_ranges(total_blocks: int, tables: int) -> list[tuple[int, int]]:
    base = total_blocks // tables
    rem = total_blocks % tables
    out = []
    start = 0
    for t in range(tables):
        count = base + (1 if t < rem else 0)
        out.append((start, start + count))
        start += count
    return out



def payload6_to_index(info6: np.ndarray) -> np.ndarray:
    a = np.asarray(info6, dtype=np.uint32)
    weights = np.asarray([8**5, 8**4, 8**3, 8**2, 8, 1], dtype=np.uint32)
    return a @ weights


def build_shaping_lookup(M: np.ndarray) -> np.ndarray:
    """Best codeword for every one of 8^6 possible payload tuples."""
    ids = np.arange(8**6, dtype=np.uint32)
    info = np.empty((len(ids), 6), dtype=np.uint8)
    z = ids.copy()
    for col in range(5, -1, -1):
        info[:, col] = z & 7
        z >>= 3
    return choose_shaped_codewords(info, M, batch_size=32768)


def run_package(
    payload_bytes: int = 1_048_576,
    tables: int = 16,
    channels: int = 64,
    publication_fraction: float = 1e-3,
    delta_multiple: float = 2.0,
) -> dict:
    payload = deterministic_payload(payload_bytes)
    payload_sha = hashlib.sha256(payload).hexdigest()

    syms, bit_length = bytes_to_symbols(payload)
    total_blocks = math.ceil(len(syms) / PAYLOAD_SYMBOLS)
    padded = np.pad(
        syms,
        (0, total_blocks * PAYLOAD_SYMBOLS - len(syms)),
    ).reshape(total_blocks, PAYLOAD_SYMBOLS)

    ranges = split_block_ranges(total_blocks, tables)
    recovered_global = np.empty((total_blocks, PAYLOAD_SYMBOLS), dtype=np.uint8)

    table_metrics = []
    total_raw_err = 0
    total_raw_symbols = 0
    start_time = time.perf_counter()

    # All local blocks use the same normalized phase grid, so the protected
    # basis and shaping metric are identical across tables.
    template_period = 6.0
    template_x = np.arange(BLOCK_POINTS, dtype=np.float64) * template_period / BLOCK_POINTS
    template_B = macro_basis(template_x, template_period)
    template_U = smooth_free_basis(template_B)
    template_M = shaping_metric_matrix(template_U)
    shaping_lookup = build_shaping_lookup(template_M)

    for table_id, (lo, hi) in enumerate(ranges):
        table_info = padded[lo:hi]
        table_blocks = hi - lo

        period = 5.5 + 0.17 * (table_id % 7)
        x = np.arange(BLOCK_POINTS, dtype=np.float64) * period / BLOCK_POINTS
        B = macro_basis(x, period)
        U = template_U
        assert U.shape == (BLOCK_POINTS, CODE_N)
        codewords = shaping_lookup[payload6_to_index(table_info)]

        # Round-robin blocks across channels.
        per_channel = math.ceil(table_blocks / channels)
        slot_count = per_channel * channels

        # Padding blocks are ignored in recovery and metrics that rely on validity.
        cw_slots = np.zeros((slot_count, CODE_N), dtype=np.uint8)
        cw_slots[:table_blocks] = codewords

        # channel-major layout: block i -> channel i % channels, local i // channels
        # Build index map from global-in-table block order to (channel, local).
        ch_ids = np.arange(slot_count) % channels
        local_ids = np.arange(slot_count) // channels

        baselines = np.asarray(
            [macro_curve(x, period, table_id, c, channels) for c in range(channels)]
        )
        global_range = float(np.max(baselines) - np.min(baselines))
        publication_step = global_range * publication_fraction
        delta = publication_step * delta_multiple

        coeff = LEVELS[cw_slots] * delta
        perturb = coeff @ U.T  # (slots, 14)

        Y = baselines[ch_ids] + perturb
        Y_pub = np.round(Y / publication_step) * publication_step

        # Because B.T @ U ~= 0 and each macro baseline lies in span(B),
        # the carrier coefficients are recovered directly from y @ U.
        coeff_hat = Y_pub @ U
        raw = coeffs_to_symbols(coeff_hat, delta)

        valid = np.arange(slot_count) < table_blocks
        raw_valid = raw[valid]
        tx_valid = cw_slots[valid]
        raw_err = int(np.sum(raw_valid != tx_valid))
        total_raw_err += raw_err
        total_raw_symbols += table_blocks * CODE_N

        corrected = hamming_correct_batch(raw_valid)
        recovered_global[lo:hi] = corrected[:, :PAYLOAD_SYMBOLS]

        base_valid = baselines[ch_ids[valid]]
        pub_valid = Y_pub[valid]

        nrmse = (
            100.0
            * float(np.sqrt(np.mean((pub_valid - base_valid) ** 2)))
            / global_range
        )

        rough0 = roughness_rows(base_valid)
        rough1 = roughness_rows(pub_valid)
        rough_ratio = rough1 / np.maximum(rough0, 1e-15)

        # Cross-channel correlation and macro drift use the mean published block
        # for each series; decoding itself does not need these fitted parameters.
        mean_pub_by_channel = np.empty_like(baselines)
        for c in range(channels):
            mask = valid & (ch_ids == c)
            if np.any(mask):
                mean_pub_by_channel[c] = np.mean(Y_pub[mask], axis=0)
            else:
                mean_pub_by_channel[c] = baselines[c]

        beta0, _ = fit_macro(B, baselines)
        beta_mean, _ = fit_macro(B, mean_pub_by_channel)
        beta_rel = np.linalg.norm(beta_mean - beta0, axis=1) / np.maximum(
            np.linalg.norm(beta0, axis=1), 1e-15
        )

        corr0 = np.corrcoef(baselines)
        corr1 = np.corrcoef(mean_pub_by_channel)
        tri = np.triu_indices(channels, k=1)
        corr_mae = float(np.mean(np.abs(corr1[tri] - corr0[tri])))

        table_metrics.append(
            asdict(
                TableMetrics(
                    table_id=table_id,
                    channels=channels,
                    blocks=table_blocks,
                    rows=per_channel * BLOCK_POINTS,
                    publication_step=publication_step,
                    delta=delta,
                    raw_symbol_error_rate=raw_err / max(table_blocks * CODE_N, 1),
                    nrmse_percent=nrmse,
                    mean_roughness_ratio=float(np.mean(rough_ratio)),
                    max_roughness_ratio=float(np.max(rough_ratio)),
                    cross_channel_corr_mae=corr_mae,
                    macro_beta_relative_error_mean=float(np.mean(beta_rel)),
                )
            )
        )

    recovered_bytes = symbols_to_bytes(recovered_global.reshape(-1), bit_length)
    decoded_sha = hashlib.sha256(recovered_bytes).hexdigest()

    total_rows = sum(t["rows"] for t in table_metrics)
    total_numeric_values = total_rows * channels

    elapsed = time.perf_counter() - start_time

    return {
        "scope": "synthetic-only package benchmark",
        "version": "v10",
        "q": 8,
        "field": "GF(8)",
        "code": "[9,7,3]_8",
        "block_layout": "6 payload + 1 shaping + 2 parity",
        "payload_bytes": payload_bytes,
        "payload_sha256": payload_sha,
        "decoded_sha256": decoded_sha,
        "exact_recovery": recovered_bytes == payload,
        "tables": tables,
        "channels_per_table": channels,
        "total_hamming_blocks": total_blocks,
        "published_rows_total": total_rows,
        "published_numeric_values_total": total_numeric_values,
        "effective_payload_bits_per_row": payload_bytes * 8 / total_rows,
        "effective_payload_bits_per_numeric_value": payload_bytes * 8 / total_numeric_values,
        "raw_symbol_error_rate": total_raw_err / max(total_raw_symbols, 1),
        "mean_table_nrmse_percent": float(np.mean([t["nrmse_percent"] for t in table_metrics])),
        "mean_table_roughness_ratio": float(np.mean([t["mean_roughness_ratio"] for t in table_metrics])),
        "mean_cross_channel_corr_mae": float(np.mean([t["cross_channel_corr_mae"] for t in table_metrics])),
        "mean_macro_beta_relative_error": float(np.mean([t["macro_beta_relative_error_mean"] for t in table_metrics])),
        "elapsed_seconds": elapsed,
        "tables_detail": table_metrics,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload-bytes", type=int, default=1_048_576)
    ap.add_argument("--tables", type=int, default=16)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument(
        "--json-out",
        type=Path,
        default=Path("q8_package_v10_results.json"),
    )
    args = ap.parse_args()

    result = run_package(
        payload_bytes=args.payload_bytes,
        tables=args.tables,
        channels=args.channels,
    )
    args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "tables_detail"}, indent=2))


if __name__ == "__main__":
    main()
