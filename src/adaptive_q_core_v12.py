#!/usr/bin/env python3
"""
adaptive_q_package_v12.py

Synthetic-only adaptive-q package benchmark.

For each synthetic table:
  1. try q in {8,16,32};
  2. run a deterministic calibration through publication quantization;
  3. require exact q-ary Hamming recovery;
  4. require table-specific NRMSE <= residual budget;
  5. choose the highest feasible q.

The benchmark payload is generated internally and is never read from an
external file. The decoder uses only the published NPZ package + manifest.

Dependencies: numpy only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np


Q_MODES = {
    8:  {"m": 3, "poly": 0b1011,   "delta_multiple": 2.0},
    16: {"m": 4, "poly": 0b10011,  "delta_multiple": 2.5},
    32: {"m": 5, "poly": 0b100101, "delta_multiple": 3.0},
}

LEVEL_CACHE = {q: np.arange(q, dtype=np.float64) - (q - 1) / 2 for q in Q_MODES}


# ---------------------------------------------------------------------------
# GF(2^m) and q-ary Hamming [q+1,q-1,3]
# ---------------------------------------------------------------------------

def gf_mul_scalar(a: int, b: int, m: int, poly: int) -> int:
    out = 0
    top = 1 << m
    mask = top - 1
    a = int(a)
    b = int(b)
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
    """
    info shape (..., q-1), parity appended to positions q-1 and q.
    """
    T = GF_TABLES[q]
    info = np.asarray(info, dtype=np.uint16)
    if info.shape[-1] != q - 1:
        raise ValueError("bad info width")

    cw = np.zeros(info.shape[:-1] + (q + 1,), dtype=np.uint16)
    cw[..., :q-1] = info

    p1 = np.bitwise_xor.reduce(info, axis=-1)
    cw[..., q-1] = p1

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

    # columns: (1,a), a=0..q-1, and (0,1)
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


# ---------------------------------------------------------------------------
# Bit packing for q=2^m
# ---------------------------------------------------------------------------

def bits_to_symbols(bits: np.ndarray, m: int) -> tuple[np.ndarray, int]:
    bits = np.asarray(bits, dtype=np.uint8).reshape(-1)
    original = len(bits)
    pad = (-len(bits)) % m
    if pad:
        bits = np.pad(bits, (0, pad))
    g = bits.reshape(-1, m)
    weights = (1 << np.arange(m - 1, -1, -1)).astype(np.uint16)
    return (g @ weights).astype(np.uint16), original


def symbols_to_bits(symbols: np.ndarray, m: int, bit_length: int) -> np.ndarray:
    s = np.asarray(symbols, dtype=np.uint16).reshape(-1)
    shifts = np.arange(m - 1, -1, -1, dtype=np.uint16)
    bits = ((s[:, None] >> shifts[None, :]) & 1).astype(np.uint8).reshape(-1)
    return bits[:bit_length]


def bytes_to_bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="big")


def bits_to_bytes(bits: np.ndarray) -> bytes:
    bits = np.asarray(bits, dtype=np.uint8).reshape(-1)
    pad = (-len(bits)) % 8
    if pad:
        bits = np.pad(bits, (0, pad))
    return np.packbits(bits, bitorder="big").tobytes()


def synthetic_payload(nbytes: int) -> bytes:
    return hashlib.shake_256(b"adaptive-q-v12-synthetic").digest(nbytes)


# ---------------------------------------------------------------------------
# Macro families
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


def local_x(n: int) -> np.ndarray:
    return np.linspace(-1.0, 1.0, n, endpoint=True)


def basis_for(spec: FamilySpec, x: np.ndarray) -> np.ndarray:
    if spec.family == "affine":
        return np.column_stack([np.ones_like(x), x])

    if spec.family == "periodic":
        w = 2.0 * np.pi * float(spec.params["cycles"]) / (x[-1] - x[0])
        return np.column_stack(
            [np.ones_like(x), np.sin(w*x), np.cos(w*x), np.sin(2*w*x), np.cos(2*w*x)]
        )

    if spec.family == "saturation":
        t = 2.0 * (x + 1.0)
        tau = float(spec.params["tau"])
        return np.column_stack([np.ones_like(x), np.exp(-t / tau)])

    if spec.family == "gaussian":
        return np.column_stack([np.ones_like(x), x, x*x])

    raise ValueError(spec.family)
