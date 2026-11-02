#!/usr/bin/env python3
"""Deterministic-basis candidate wrapper for the current synthetic V18 engine.

This file intentionally does not replace noisy_host_package_v18.py yet.
It reuses the current carrier/QIM/ECC/publication logic while replacing only
smooth_free_basis with a fixed-order DCT-II + two-pass modified Gram-Schmidt
construction whose scalar reductions use math.fsum.

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
_CANDIDATE_BENCHMARK_SEED = 0

_BASE_RUN_PACKAGE = BASE["run_package"]
_BASE_DECODE_TABLE = BASE["decode_table"]
_BASE_SET_BENCHMARK_SEED = BASE.get("set_benchmark_seed")


def _stable_dot(a, b) -> float:
    """Fixed-order double-precision dot product using Python/math.fsum."""
    return math.fsum(float(x) * float(y) for x, y in zip(a, b))


def _stable_norm(v) -> float:
    return math.sqrt(max(0.0, _stable_dot(v, v)))


def _subtract_projection_in_place(w: np.ndarray, q: np.ndarray, coeff: float):
    # Python scalar loop avoids delegating the reduction/update ordering to BLAS.
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
    # A final normalization with the same fixed-order norm keeps the contract
    # explicit after Python division rounding.
    nrm2 = _stable_norm(out)
    out = np.asarray([float(x) / nrm2 for x in out], dtype=float)
    k = max(range(len(out)), key=lambda i: (abs(float(out[i])), -i))
    if float(out[k]) < 0.0:
        out = -out
    return out


def deterministic_smooth_free_basis(B: np.ndarray) -> np.ndarray:
    """Deterministic smooth-ish basis for the orthogonal complement of B.

    Protected columns are orthonormalized first. DCT-II cosine candidates are
    then considered from lowest to highest frequency and projected against both
    the protected space and previously accepted free vectors. The DCT family is
    complete; coordinate vectors are a deterministic fallback only.
    """
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

    # Fixed-order DCT-II candidate family. k=0 is intentionally included; it
    # will be skipped automatically when constant content is protected.
    for k in range(n):
        cand = np.asarray([
            math.cos(math.pi * (i + 0.5) * k / n)
            for i in range(n)
        ], dtype=float)
        w = _orthogonalize(cand, protected + free)
        q = _normalize_and_canonicalize(w)
        if q is not None:
            # One extra two-pass projection after normalization reduces drift
            # from near-dependent low-frequency candidates.
            w2 = _orthogonalize(q, protected + free)
            q2 = _normalize_and_canonicalize(w2)
            if q2 is not None:
                free.append(q2)
        if len(free) == target:
            break

    # Deterministic fallback; normally unnecessary because the DCT family is
    # complete, but keeps the reconstruction contract total.
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

    # Fixed-order validation, avoiding a BLAS matrix multiply as the authority.
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


def _patch_base_globals():
    g = _BASE_RUN_PACKAGE.__globals__
    g["smooth_free_basis"] = deterministic_smooth_free_basis
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
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    result = dict(result)
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


# Patch helper functions immediately too, because some diagnostic harnesses call
# calibration/choose_mode helpers before run_package.
_patch_base_globals()


if __name__ == "__main__":
    # Keep direct CLI behavior intentionally minimal; protocol harnesses are the
    # authoritative candidate test surface.
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
