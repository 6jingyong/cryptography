#!/usr/bin/env python3
"""Deterministic current-V18 candidate engine.

This file intentionally does not replace noisy_host_package_v18.py yet.
It reuses the current carrier/QIM/ECC/publication logic while replacing:

1. QR/eigh free-basis construction with fixed-order DCT-II + two-pass MGS;
2. package-visible coefficient-to-signal products with fixed-order math.fsum;
3. package-visible trigonometric/exponential model evaluation with scalar
   ``math`` calls and canonical snapping for exact 0/+1/-1 trig values;
4. reconstruction-irrelevant diagnostic floats in B/results with a declared
   fixed decimal serialization precision.

No q/delta/host/V20/locator performance parameter is changed.

Synthetic/mock benchmark only.
"""
from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASE = runpy.run_path(str(HERE / "noisy_host_package_v18.py"))

# Re-export the base engine surface so existing diagnostic harnesses that use
# helpers beyond run_package/decode_table continue to work with this candidate.
for _name, _value in BASE.items():
    if not _name.startswith("__"):
        globals()[_name] = _value

BASIS_VERSION = "deterministic-dct-mgs-v1"
ORTHO_TOL = 1e-11
TRIG_SNAP_TOL = 1e-15
DIAGNOSTIC_ROUND_DECIMALS = 14
_CANDIDATE_BENCHMARK_SEED = 0

_BASE_RUN_PACKAGE = BASE["run_package"]
_BASE_DECODE_TABLE = BASE["decode_table"]
_BASE_SET_BENCHMARK_SEED = BASE.get("set_benchmark_seed")
_BASE_CALIBRATION = BASE["calibration"]


def _snap_trig(value: float) -> float:
    value = float(value)
    if abs(value) <= TRIG_SNAP_TOL:
        return 0.0
    if abs(value - 1.0) <= TRIG_SNAP_TOL:
        return 1.0
    if abs(value + 1.0) <= TRIG_SNAP_TOL:
        return -1.0
    return value


def deterministic_local_x(n: int) -> np.ndarray:
    if n < 2:
        raise ValueError("n must be >= 2")
    den = float(n - 1)
    return np.asarray([-1.0 + 2.0 * float(i) / den for i in range(n)], dtype=float)


def deterministic_basis_for(spec, x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float).reshape(-1)
    if spec.family == "affine":
        return np.column_stack([np.ones_like(x), x])
    if spec.family == "periodic":
        w = 2.0 * math.pi * float(spec.params["cycles"]) / (float(x[-1]) - float(x[0]))
        c1s = [_snap_trig(math.sin(w * float(v))) for v in x]
        c1c = [_snap_trig(math.cos(w * float(v))) for v in x]
        c2s = [_snap_trig(math.sin(2.0 * w * float(v))) for v in x]
        c2c = [_snap_trig(math.cos(2.0 * w * float(v))) for v in x]
        return np.column_stack([
            np.ones_like(x),
            np.asarray(c1s, dtype=float),
            np.asarray(c1c, dtype=float),
            np.asarray(c2s, dtype=float),
            np.asarray(c2c, dtype=float),
        ])
    if spec.family == "saturation":
        tau = float(spec.params["tau"])
        decay = [math.exp(-(2.0 * (float(v) + 1.0)) / tau) for v in x]
        return np.column_stack([np.ones_like(x), np.asarray(decay, dtype=float)])
    if spec.family == "gaussian":
        return np.column_stack([np.ones_like(x), x, x * x])
    raise ValueError(spec.family)


def deterministic_channel_beta(spec, channel: int, channels: int) -> np.ndarray:
    phase = 2.0 * math.pi * int(channel) / max(int(channels), 1)
    sp = _snap_trig(math.sin(phase))
    cp = _snap_trig(math.cos(phase))
    c03 = _snap_trig(math.cos(0.3 * phase))
    if spec.family == "affine":
        return np.asarray([50.0 + 0.25 * channel, 8.0 + 0.7 * sp], dtype=float)
    if spec.family == "periodic":
        return np.asarray([
            55.0 + 0.20 * channel,
            7.0 + 0.6 * sp,
            1.6 * c03,
            1.4 + 0.3 * cp,
            0.5 * sp,
        ], dtype=float)
    if spec.family == "saturation":
        return np.asarray([58.0 + 0.2 * channel, -(24.0 + 1.2 * sp)], dtype=float)
    if spec.family == "gaussian":
        mu = 0.10 * sp
        sigma = 0.55 + 0.03 * cp
        amp = 45.0 + 1.5 * sp
        c = -1.0 / (2.0 * sigma * sigma)
        b = mu / (sigma * sigma)
        a = math.log(amp) - mu * mu / (2.0 * sigma * sigma)
        return np.asarray([a, b, c], dtype=float)
    raise ValueError(spec.family)


def deterministic_inverse_y(z: np.ndarray, transform: str) -> np.ndarray:
    arr = np.asarray(z, dtype=float)
    if transform != "log":
        return arr
    flat = [math.exp(float(v)) for v in arr.reshape(-1)]
    return np.asarray(flat, dtype=float).reshape(arr.shape)


def _stable_dot(a, b) -> float:
    return math.fsum(float(x) * float(y) for x, y in zip(a, b))


def _stable_norm(v) -> float:
    return math.sqrt(max(0.0, _stable_dot(v, v)))


def _stable_rms(values: np.ndarray) -> float:
    flat = np.asarray(values, dtype=float).reshape(-1)
    if len(flat) == 0:
        return 0.0
    return math.sqrt(math.fsum(float(v) * float(v) for v in flat) / float(len(flat)))


def _subtract_projection_in_place(w: np.ndarray, q: np.ndarray, coeff: float):
    for i in range(len(w)):
        w[i] = float(w[i]) - float(coeff) * float(q[i])


def _orthogonalize(v, basis, passes: int = 2) -> np.ndarray:
    w = np.asarray(v, dtype=float).reshape(-1).copy()
    for _ in range(passes):
        for q in basis:
            c = _stable_dot(q, w)
            _subtract_projection_in_place(w, q, c)
    return w


def _normalize_and_canonicalize(w: np.ndarray) -> np.ndarray | None:
    nrm = _stable_norm(w)
    if not math.isfinite(nrm) or nrm <= ORTHO_TOL:
        return None
    out = np.asarray([float(x) / nrm for x in w], dtype=float)
    nrm2 = _stable_norm(out)
    out = np.asarray([float(x) / nrm2 for x in out], dtype=float)
    k = max(range(len(out)), key=lambda i: (abs(float(out[i])), -i))
    if float(out[k]) < 0.0:
        out = -out
    return out


def deterministic_smooth_free_basis(B: np.ndarray) -> np.ndarray:
    """Fixed-order smooth-ish basis for the orthogonal complement of B."""
    B = np.asarray(B, dtype=float)
    if B.ndim != 2:
        raise ValueError("B must be a 2-D matrix")
    n, p = B.shape
    if n <= p:
        raise RuntimeError("no free subspace")

    protected = []
    for j in range(p):
        w = _orthogonalize(B[:, j], protected)
        q = _normalize_and_canonicalize(w)
        if q is None:
            raise RuntimeError("protected model columns are numerically dependent")
        protected.append(q)

    target = n - len(protected)
    free = []
    for k in range(n):
        cand = np.asarray([
            math.cos(math.pi * (i + 0.5) * k / n)
            for i in range(n)
        ], dtype=float)
        w = _orthogonalize(cand, protected + free)
        q = _normalize_and_canonicalize(w)
        if q is not None:
            w2 = _orthogonalize(q, protected + free)
            q2 = _normalize_and_canonicalize(w2)
            if q2 is not None:
                free.append(q2)
        if len(free) == target:
            break

    if len(free) < target:
        for j in range(n):
            cand = np.zeros(n, dtype=float)
            cand[j] = 1.0
            w = _orthogonalize(cand, protected + free)
            q = _normalize_and_canonicalize(w)
            if q is not None:
                free.append(q)
            if len(free) == target:
                break

    if len(free) != target:
        raise RuntimeError(f"deterministic basis incomplete: {len(free)} != {target}")

    U = np.column_stack(free)
    worst_protected = 0.0
    for q in protected:
        for j in range(U.shape[1]):
            worst_protected = max(worst_protected, abs(_stable_dot(q, U[:, j])))
    worst_free = 0.0
    for i in range(U.shape[1]):
        for j in range(U.shape[1]):
            expected = 1.0 if i == j else 0.0
            worst_free = max(worst_free, abs(_stable_dot(U[:, i], U[:, j]) - expected))
    if worst_protected > 5e-10 or worst_free > 5e-10:
        raise RuntimeError(
            f"deterministic basis orthogonality failed: protected={worst_protected}, free={worst_free}"
        )
    return U


def _stable_matrix_vector(M: np.ndarray, v: np.ndarray) -> np.ndarray:
    M = np.asarray(M, dtype=float)
    v = np.asarray(v, dtype=float).reshape(-1)
    if M.shape[1] != len(v):
        raise ValueError("matrix/vector dimension mismatch")
    return np.asarray([
        math.fsum(float(M[i, j]) * float(v[j]) for j in range(M.shape[1]))
        for i in range(M.shape[0])
    ], dtype=float)


def _stable_coefficients_to_signal(coeff: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Compute coeff @ U.T with fixed row/component reduction order."""
    coeff = np.asarray(coeff, dtype=float)
    U = np.asarray(U, dtype=float)
    if coeff.ndim != 2 or U.ndim != 2 or coeff.shape[1] != U.shape[1]:
        raise ValueError("coefficient/basis dimension mismatch")
    rows = np.empty((coeff.shape[0], U.shape[0]), dtype=float)
    for i in range(coeff.shape[0]):
        ci = coeff[i]
        for p in range(U.shape[0]):
            up = U[p]
            rows[i, p] = math.fsum(
                float(ci[j]) * float(up[j]) for j in range(coeff.shape[1])
            )
    return rows


def deterministic_baseline(spec, n: int, channel: int, channels: int):
    x = deterministic_local_x(n)
    B = deterministic_basis_for(spec, x)
    beta = deterministic_channel_beta(spec, channel, channels)
    z = _stable_matrix_vector(B, beta)
    return x, B, z, deterministic_inverse_y(z, spec.transform)


def deterministic_encode_table(bit_chunk: np.ndarray, table_id: int, family: str, chosen: dict, channels: int):
    """Current encode_table semantics with fixed-order package-visible synthesis."""
    q = int(chosen["q"])
    m = int(chosen["m"])
    spec = family_spec(family)
    n = int(chosen["points_per_block"])
    x = deterministic_local_x(n)
    B = deterministic_basis_for(spec, x)
    U = deterministic_smooth_free_basis(B)
    ppcw = payload_symbols_per_codeword(q)

    syms, bit_length = bits_to_symbols(bit_chunk, m)
    blocks = math.ceil(len(syms) / ppcw)
    padded = np.pad(syms, (0, blocks * ppcw - len(syms))).reshape(blocks, ppcw)
    segments = math.ceil(blocks / channels)
    slots = segments * channels
    padded_payload = np.zeros((slots, ppcw), dtype=np.uint16)
    padded_payload[:blocks] = padded

    rng = table_rng(table_id)
    host_c = host_coefficients(rng, slots, U.shape[1], float(chosen["host_sigma"]))
    _cw, encoded_first = embed_payload_symbols(
        padded_payload, host_c[:, :q+1], q, float(chosen["delta"])
    )
    encoded_c = host_c.copy()
    encoded_c[:, :q+1] = encoded_first

    z0 = np.asarray([
        deterministic_baseline(spec, n, c, channels)[2]
        for c in range(channels)
    ])
    channel_ids = np.arange(slots) % channels
    zh = z0[channel_ids] + _stable_coefficients_to_signal(host_c, U)
    ze = z0[channel_ids] + _stable_coefficients_to_signal(encoded_c, U)
    yh = deterministic_inverse_y(zh, spec.transform)
    ye = deterministic_inverse_y(ze, spec.transform)
    zp, yp = publish(
        ze, ye, chosen["publication_model"], float(chosen["publication_step"]), spec.transform
    )

    pub = np.empty((segments * n, channels), dtype=float)
    for s in range(segments):
        pub[s*n:(s+1)*n, :] = yp[s*channels:(s+1)*channels].T

    baseline_y = deterministic_inverse_y(z0[channel_ids], spec.transform)
    host_rms = _stable_rms(yh - baseline_y)
    adjustment_rms = _stable_rms(yp - yh)
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
            "benchmark_seed": _CANDIDATE_BENCHMARK_SEED,
            "sigma": chosen["host_sigma"],
            "active_dims": chosen["host_active_dims"],
        },
        "observed_host_residual_rms": host_rms,
        "observed_embedding_adjustment_rms": adjustment_rms,
        "observed_adjustment_to_host_rms_ratio": float(adjustment_rms / max(host_rms, 1e-15)),
    }
    return x, pub, manifest


def _round_diag(value):
    return round(float(value), DIAGNOSTIC_ROUND_DECIMALS)


def _canonicalize_diagnostic_floats(manifest: dict):
    fields = (
        "calibration_host_adjustment_nrmse",
        "observed_host_residual_rms",
        "observed_embedding_adjustment_rms",
        "observed_adjustment_to_host_rms_ratio",
    )
    for table in manifest.get("tables", []):
        for field in fields:
            if field in table:
                table[field] = _round_diag(table[field])
    manifest["diagnostic_round_decimals"] = DIAGNOSTIC_ROUND_DECIMALS


def _canonicalize_result_diagnostics(result: dict):
    out = dict(result)
    for field in (
        "median_adjustment_to_host_rms_ratio",
        "max_adjustment_to_host_rms_ratio",
    ):
        if field in out and out[field] is not None:
            out[field] = _round_diag(out[field])
    selected = []
    for row in out.get("selected_tables", []) or []:
        r = dict(row)
        for field in (
            "calibration_host_adjustment_nrmse",
            "calibration_adjustment_to_host_rms_ratio",
        ):
            if field in r and r[field] is not None:
                r[field] = _round_diag(r[field])
        selected.append(r)
    if "selected_tables" in out:
        out["selected_tables"] = selected
    out["diagnostic_round_decimals"] = DIAGNOSTIC_ROUND_DECIMALS
    return out


def _patch_base_globals():
    g = _BASE_RUN_PACKAGE.__globals__
    g["local_x"] = deterministic_local_x
    g["basis_for"] = deterministic_basis_for
    g["channel_beta"] = deterministic_channel_beta
    g["inverse_y"] = deterministic_inverse_y
    g["smooth_free_basis"] = deterministic_smooth_free_basis
    g["baseline"] = deterministic_baseline
    g["encode_table"] = deterministic_encode_table
    # real-package-v3 patches the candidate wrapper's synthetic_payload global;
    # forward that exact callable into the base engine before every encode.
    g["synthetic_payload"] = globals()["synthetic_payload"]
    if _BASE_SET_BENCHMARK_SEED is not None:
        _BASE_SET_BENCHMARK_SEED(int(_CANDIDATE_BENCHMARK_SEED))


def set_benchmark_seed(seed: int):
    global _CANDIDATE_BENCHMARK_SEED
    _CANDIDATE_BENCHMARK_SEED = int(seed)
    if _BASE_SET_BENCHMARK_SEED is not None:
        _BASE_SET_BENCHMARK_SEED(int(seed))


def run_package(payload_bytes: int = 4096, channels: int = 4, out_dir: Path = Path("v18_det_out")):
    _patch_base_globals()
    result = _BASE_RUN_PACKAGE(payload_bytes=payload_bytes, channels=channels, out_dir=out_dir)
    mf = result.get("manifest_filename", "manifest_noisy_host_v18.json")
    manifest_path = Path(out_dir) / mf
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["basis_version"] = BASIS_VERSION
    for table in manifest.get("tables", []):
        table["basis_version"] = BASIS_VERSION
    _canonicalize_diagnostic_floats(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    result = _canonicalize_result_diagnostics(result)
    result["basis_version"] = BASIS_VERSION
    return result


def decode_table(pub: np.ndarray, manifest: dict):
    declared = manifest.get("basis_version")
    if declared != BASIS_VERSION:
        raise RuntimeError(
            f"basis version mismatch: manifest={declared!r}, decoder={BASIS_VERSION!r}"
        )
    _patch_base_globals()
    return _BASE_DECODE_TABLE(pub, manifest)


_patch_base_globals()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out-dir", type=Path, default=Path("v18_det_out"))
    args = ap.parse_args()
    set_benchmark_seed(args.seed)
    out = run_package(args.payload_bytes, args.channels, args.out_dir)
    print(json.dumps(out, indent=2))
