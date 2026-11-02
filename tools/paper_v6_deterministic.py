#!/usr/bin/env python3
"""Drop-in deterministic numeric-fit candidate for tools/paper_v6.py.

Synthetic/mock benchmark only.

This wrapper preserves paper-v6 morphology thresholds, fit grids, story logic,
claims, experiments, and prose while replacing only the small descriptive
least-squares and R2 numerical kernels with fixed-order scalar arithmetic.
"""
from __future__ import annotations

import math
import runpy
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASE = runpy.run_path(str(HERE / "paper_v6.py"))

for _name, _value in BASE.items():
    if not _name.startswith("__"):
        globals()[_name] = _value

LS_TOL = 1e-14


def _dot(a, b) -> float:
    return math.fsum(float(x) * float(y) for x, y in zip(a, b))


def _norm(v) -> float:
    return math.sqrt(max(0.0, _dot(v, v)))


def _axpy_sub(v: list[float], q: list[float], coeff: float) -> None:
    for i in range(len(v)):
        v[i] = float(v[i]) - float(coeff) * float(q[i])


def stable_lstsq(A, y) -> np.ndarray:
    """Small fixed-order two-pass MGS least-squares solver.

    paper-v6 uses only tiny descriptive systems (normally 2 or 3 columns;
    fallback polynomial at most 4 columns). This deliberately avoids BLAS/LAPACK
    reduction order for package-visible fit summaries.
    """
    A = np.asarray(A, dtype=float)
    y = np.asarray(y, dtype=float).reshape(-1)
    if A.ndim != 2 or A.shape[0] != len(y):
        raise ValueError("least-squares shape mismatch")
    n, m = A.shape
    if n < m or m == 0:
        raise ValueError("unsupported least-squares geometry")

    cols = [[float(A[i, j]) for i in range(n)] for j in range(m)]
    qcols: list[list[float]] = []
    R = [[0.0 for _ in range(m)] for _ in range(m)]

    for j in range(m):
        v = cols[j][:]
        # First MGS pass.
        for k in range(j):
            c = _dot(qcols[k], v)
            R[k][j] += c
            _axpy_sub(v, qcols[k], c)
        # Second pass fixes residual projection deterministically.
        for k in range(j):
            c = _dot(qcols[k], v)
            R[k][j] += c
            _axpy_sub(v, qcols[k], c)
        diag = _norm(v)
        if not math.isfinite(diag) or diag <= LS_TOL:
            raise RuntimeError("deterministic descriptive fit is rank deficient")
        R[j][j] = diag
        qcols.append([float(x) / diag for x in v])

    qty = [_dot(q, y) for q in qcols]
    coeff = [0.0 for _ in range(m)]
    for i in range(m - 1, -1, -1):
        tail = math.fsum(R[i][j] * coeff[j] for j in range(i + 1, m))
        coeff[i] = (qty[i] - tail) / R[i][i]
    return np.asarray(coeff, dtype=float)


def stable_predict(A, coeff) -> np.ndarray:
    A = np.asarray(A, dtype=float)
    c = np.asarray(coeff, dtype=float).reshape(-1)
    if A.ndim != 2 or A.shape[1] != len(c):
        raise ValueError("prediction shape mismatch")
    return np.asarray([
        math.fsum(float(A[i, j]) * float(c[j]) for j in range(A.shape[1]))
        for i in range(A.shape[0])
    ], dtype=float)


def r2(y, p):
    y = np.asarray(y, dtype=float).reshape(-1)
    p = np.asarray(p, dtype=float).reshape(-1)
    if len(y) != len(p):
        raise ValueError("R2 shape mismatch")
    if not len(y):
        return 0.0
    mean_y = math.fsum(float(v) for v in y) / float(len(y))
    ss_res = math.fsum((float(a) - float(b)) ** 2 for a, b in zip(y, p))
    ss_tot = math.fsum((float(v) - mean_y) ** 2 for v in y)
    return 1.0 - ss_res / (ss_tot + 1e-12)


def _linear_fit(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    A = np.column_stack([x, np.ones_like(x)])
    c = stable_lstsq(A, y)
    return c, stable_predict(A, c)


def features(x, y):
    """Original paper-v6 features with deterministic linear sub-fit."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    d = np.diff(y)
    _c, lin_pred = _linear_fit(x, y)
    lin = r2(y, lin_pred)
    mono = float(max(np.mean(d >= 0), np.mean(d <= 0))) if len(d) else 0
    k = max(2, len(d) // 3) if len(d) else 1
    sat = 0 if len(d) < 6 else mono * max(
        0,
        min(1, 1 - (np.mean(np.abs(d[-k:])) / (np.mean(np.abs(d[:k])) + 1e-12))),
    )
    yy = y - np.mean(y)
    power = np.abs(np.fft.rfft(yy)) ** 2
    per = 0 if len(power) <= 2 else float(np.max(power[1:]) / (np.sum(power[1:]) + 1e-12))
    imax = int(np.argmax(y))
    peak = 0
    if len(y) >= 7 and 1 < imax < len(y) - 2:
        yr = float(np.ptp(y)) + 1e-12
        left = y[:imax + 1]
        right = y[imax:][::-1]
        m = min(len(left), len(right))
        sym = 0 if m < 3 else 1 - min(1, float(np.sqrt(np.mean((left[-m:] - right[-m:]) ** 2)) / yr))
        peak = max(0, min(1, float((y[imax] - .5 * (y[0] + y[-1])) / yr))) * max(0, sym)
    ys = np.convolve(y, np.ones(3) / 3, mode="same")
    dd = np.diff(ys)
    th = .015 * (float(np.ptp(ys)) + 1e-12)
    signs = np.sign(np.where(np.abs(dd) >= th, dd, 0))
    for i in range(1, len(signs)):
        if signs[i] == 0:
            signs[i] = signs[i - 1]
    nz = signs[signs != 0]
    turns = 0 if len(nz) < 2 else int(np.sum(nz[1:] != nz[:-1]))
    return {
        "linear_r2": float(lin),
        "monotonicity": mono,
        "saturation": float(sat),
        "periodicity": per,
        "bell_peak": float(peak),
        "significant_extrema": turns,
    }


def fit_curve(m, x, y):
    """Original paper-v6 fit families/grids with deterministic LS reductions."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)

    if m == "linear":
        c, pred = _linear_fit(x, y)
        return "linear", r2(y, pred), {"slope": float(c[0]), "intercept": float(c[1])}

    if m == "saturating":
        t = x - x.min()
        xr = max(float(np.ptp(t)), 1e-9)
        best = (-1, None, None)
        for tau in np.logspace(math.log10(max(xr / 50, 1e-4)), math.log10(max(5 * xr, 1e-3)), 100):
            g = np.exp(-t / tau)
            A = np.column_stack([np.ones_like(g), g])
            c = stable_lstsq(A, y)
            pred = stable_predict(A, c)
            s = r2(y, pred)
            if s > best[0]:
                best = (s, pred, {"asymptote": float(c[0]), "amplitude": float(c[1]), "tau": float(tau)})
        return "single_exponential_saturation", best[0], best[2]

    if m == "periodic":
        xr = max(float(np.ptp(x)), 1e-9)
        best = (-1, None, None)
        for cyc in np.linspace(.5, 4, 120):
            w = 2 * np.pi * cyc / xr
            A = np.column_stack([
                np.ones_like(x),
                np.sin(w * (x - x.min())),
                np.cos(w * (x - x.min())),
            ])
            c = stable_lstsq(A, y)
            pred = stable_predict(A, c)
            s = r2(y, pred)
            if s > best[0]:
                best = (s, pred, {"cycles": float(cyc), "amplitude": float(math.hypot(c[1], c[2]))})
        return "single_harmonic", best[0], best[2]

    if m == "bell_peak":
        xr = max(float(np.ptp(x)), 1e-9)
        best = (-1, None, None)
        for mu in np.linspace(x.min() + .05 * xr, x.max() - .05 * xr, 50):
            for sig in np.linspace(.04 * xr, .5 * xr, 50):
                g = np.exp(-(x - mu) ** 2 / (2 * sig * sig))
                A = np.column_stack([np.ones_like(g), g])
                c = stable_lstsq(A, y)
                pred = stable_predict(A, c)
                s = r2(y, pred)
                if s > best[0]:
                    best = (s, pred, {"center": float(mu), "sigma": float(sig), "fwhm": float(2.35482 * sig)})
        return "gaussian_peak", best[0], best[2]

    degree = min(3, len(x) - 1)
    cols = [np.power(x, p) for p in range(degree, -1, -1)]
    A = np.column_stack(cols)
    c = stable_lstsq(A, y)
    pred = stable_predict(A, c)
    return "descriptive_polynomial", r2(y, pred), {"coefficients": [float(v) for v in c]}


def _patch_base_globals():
    g = BASE["main"].__globals__
    g["r2"] = r2
    g["features"] = features
    g["fit_curve"] = fit_curve


_patch_base_globals()


if __name__ == "__main__":
    BASE["main"]()
