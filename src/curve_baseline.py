#!/usr/bin/env python3
"""
Baseline curve-quality comparison for cryptography dirty-channel experiments.

Compares:
1) data/synthetic_dirty_v0.csv
2) the same rows plus data/interference_pairs_v1.csv

For fixed-width x bins, the script computes:
- per-bin geometric mean
- adjacent-bin discrete slope Δg/Δx
- a natural cubic spline through the binned geometric means
- roughness ∫(f''(x))² dx
- total variation of the first derivative ∫|f''(x)| dx
- max absolute spline slope

The spline is an evaluator only. The discrete slope remains the primary
derived statistic.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def binned_geometric_means(
    rows: list[dict[str, str]],
    bin_width: float,
) -> list[dict[str, float | int]]:
    buckets: dict[int, list[tuple[float, float]]] = {}
    for row in rows:
        x = float(row["x"])
        y = float(row["y"])
        if y <= 0:
            continue
        b = math.floor(x / bin_width)
        buckets.setdefault(b, []).append((x, y))

    result: list[dict[str, float | int]] = []
    for b in sorted(buckets):
        pts = buckets[b]
        xs = np.array([p[0] for p in pts], dtype=float)
        ys = np.array([p[1] for p in pts], dtype=float)
        gmean = float(np.exp(np.mean(np.log(ys))))
        result.append(
            {
                "bin": b,
                "xbar": float(np.mean(xs)),
                "gmean": gmean,
                "n": len(pts),
            }
        )
    return result


def slopes(bins: list[dict[str, float | int]]) -> np.ndarray:
    x = np.array([float(r["xbar"]) for r in bins])
    y = np.array([float(r["gmean"]) for r in bins])
    return np.diff(y) / np.diff(x)


def curve_metrics(bins: list[dict[str, float | int]]) -> dict[str, float]:
    x = np.array([float(r["xbar"]) for r in bins])
    y = np.array([float(r["gmean"]) for r in bins])
    spline = CubicSpline(x, y, bc_type="natural")
    grid = np.linspace(x.min(), x.max(), 2000)
    d1 = spline(grid, 1)
    d2 = spline(grid, 2)
    discrete = slopes(bins)

    return {
        "roughness_int_d2_sq": float(np.trapezoid(d2 * d2, grid)),
        "derivative_total_variation": float(np.trapezoid(np.abs(d2), grid)),
        "max_abs_spline_slope": float(np.max(np.abs(d1))),
        "discrete_slope_sd": float(np.std(discrete)),
        "max_abs_discrete_slope": float(np.max(np.abs(discrete))),
    }


def compare(
    base_bins: list[dict[str, float | int]],
    v1_bins: list[dict[str, float | int]],
) -> dict[str, float]:
    if [r["bin"] for r in base_bins] != [r["bin"] for r in v1_bins]:
        raise ValueError("Base and v1 bin sets differ.")

    g0 = np.array([float(r["gmean"]) for r in base_bins])
    g1 = np.array([float(r["gmean"]) for r in v1_bins])
    s0 = slopes(base_bins)
    s1 = slopes(v1_bins)

    return {
        "mean_abs_geomean_shift": float(np.mean(np.abs(g1 - g0))),
        "max_abs_geomean_shift": float(np.max(np.abs(g1 - g0))),
        "mean_abs_geomean_shift_pct": float(np.mean(np.abs((g1 - g0) / g0)) * 100),
        "max_abs_geomean_shift_pct": float(np.max(np.abs((g1 - g0) / g0)) * 100),
        "slope_rmse": float(np.sqrt(np.mean((s1 - s0) ** 2))),
        "slope_correlation": float(np.corrcoef(s0, s1)[0, 1]),
    }


def write_bins(
    path: Path,
    base_bins: list[dict[str, float | int]],
    v1_bins: list[dict[str, float | int]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    s0 = np.r_[slopes(base_bins), np.nan]
    s1 = np.r_[slopes(v1_bins), np.nan]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "bin",
                "xbar_v0",
                "gmean_v0",
                "n_v0",
                "slope_to_next_v0",
                "xbar_v1",
                "gmean_v1",
                "n_v1",
                "slope_to_next_v1",
            ]
        )
        for i, (a, b) in enumerate(zip(base_bins, v1_bins)):
            writer.writerow(
                [
                    a["bin"],
                    f'{float(a["xbar"]):.6f}',
                    f'{float(a["gmean"]):.6f}',
                    a["n"],
                    "" if math.isnan(float(s0[i])) else f"{float(s0[i]):.6f}",
                    f'{float(b["xbar"]):.6f}',
                    f'{float(b["gmean"]):.6f}',
                    b["n"],
                    "" if math.isnan(float(s1[i])) else f"{float(s1[i]):.6f}",
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("data/synthetic_dirty_v0.csv"))
    parser.add_argument(
        "--interference",
        type=Path,
        default=Path("data/interference_pairs_v1.csv"),
    )
    parser.add_argument("--bin-width", type=float, default=1.0)
    parser.add_argument(
        "--bins-output",
        type=Path,
        default=Path("results/curve_baseline_bins_v1.csv"),
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        default=Path("results/curve_baseline_metrics_v1.json"),
    )
    args = parser.parse_args()

    base = read_rows(args.base)
    interference = read_rows(args.interference)
    v1 = base + interference

    base_bins = binned_geometric_means(base, args.bin_width)
    v1_bins = binned_geometric_means(v1, args.bin_width)

    metrics = {
        "configuration": {
            "bin_width": args.bin_width,
            "base_rows": len(base),
            "interference_rows": len(interference),
            "interference_fraction_vs_base_pct": 100.0 * len(interference) / len(base),
        },
        "v0": curve_metrics(base_bins),
        "v1": curve_metrics(v1_bins),
        "comparison": compare(base_bins, v1_bins),
    }

    write_bins(args.bins_output, base_bins, v1_bins)
    args.metrics_output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_output.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
