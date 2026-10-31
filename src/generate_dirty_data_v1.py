#!/usr/bin/env python3
"""
Generate a reproducible synthetic "dirty" 2D dataset with benchmark interference points.

The base dataset includes:
- smooth latent trend
- heteroskedastic noise
- slow instrument drift
- occasional outliers
- mixed rounding precision
- missing metadata
- duplicate-like rows

V1 adds a small set of synthetic interference observations. These are generated
in symmetric log-space pairs around the local latent level so they can look like
ordinary replicate scatter while having only a small effect on the local
geometric mean.

The `benchmark_role` column is ground truth for validation only. It should be
removed when testing an observer/detector that is not allowed to know which rows
are interference.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path


def latent(x: float) -> float:
    return (
        35.0
        + 2.4 * x
        + 8.0 * math.sin(x / 2.8)
        + 3.5 * math.cos(x / 1.7)
    )


def generate(
    seed: int = 20261031,
    n: int = 240,
    interference_pairs: int = 12,
) -> list[dict[str, object]]:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []

    for i in range(n):
        x = i / 12.0
        base = latent(x)

        sigma = 1.4 + 0.12 * x
        y = base + rng.gauss(0.0, sigma)

        source = "A" if i % 3 else "B"
        quality = "ok"

        if x > 12:
            y += 0.22 * (x - 12)

        if rng.random() < 0.04:
            y += rng.choice((-1, 1)) * rng.uniform(8, 18)
            quality = "outlier_like"

        r = rng.random()
        if r < 0.09:
            y = round(y, 1)
            rounding = "1dp"
        elif r < 0.18:
            y = round(y, 2)
            rounding = "2dp"
        else:
            y = round(y, 3)
            rounding = "3dp"

        batch = "" if rng.random() < 0.05 else f"B{1 + (i // 40)}"
        note = "manual_review" if rng.random() < 0.025 else ""

        rows.append(
            {
                "row_id": i,
                "x": round(x, 4),
                "y": y,
                "source": source,
                "batch": batch,
                "quality_hint": quality,
                "rounding": rounding,
                "note": note,
                "benchmark_role": "observed",
            }
        )

    duplicate_indices = rng.sample(range(n), 6)
    for new_id, source_idx in enumerate(duplicate_indices, start=len(rows)):
        duplicate = dict(rows[source_idx])
        duplicate["row_id"] = new_id
        duplicate["note"] = "duplicate_like"
        rows.append(duplicate)

    # Add paired interference observations. The pair is symmetric in log-space:
    #
    #   y_- = g * exp(-d)
    #   y_+ = g * exp(+d)
    #
    # therefore sqrt(y_- * y_+) = g.
    #
    # This makes geometric mean a useful first benchmark statistic: the
    # interference can alter within-bin scatter/distribution more than it moves
    # the local center line.
    max_x = (n - 1) / 12.0
    lo, hi = 1.5, max(1.6, max_x - 1.5)
    if interference_pairs > 0:
        if interference_pairs == 1:
            centers = [(lo + hi) / 2]
        else:
            step = (hi - lo) / (interference_pairs - 1)
            centers = [lo + j * step for j in range(interference_pairs)]

        next_id = len(rows)
        for pair_idx, center in enumerate(centers):
            base = latent(center)
            if center > 12:
                base += 0.22 * (center - 12)

            delta = rng.uniform(0.025, 0.065)
            jitter = rng.uniform(0.01, 0.04)

            for sign in (-1, 1):
                x = center + sign * jitter
                y = base * math.exp(sign * delta)

                rows.append(
                    {
                        "row_id": next_id,
                        "x": round(x, 4),
                        "y": round(y, 3),
                        "source": "I",
                        "batch": f"I{pair_idx + 1:02d}",
                        "quality_hint": "ok",
                        "rounding": "3dp",
                        "note": "",
                        "benchmark_role": "interference",
                    }
                )
                next_id += 1

    return rows


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "row_id",
        "x",
        "y",
        "source",
        "batch",
        "quality_hint",
        "rounding",
        "note",
        "benchmark_role",
    ]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/synthetic_dirty_v1.csv"),
    )
    parser.add_argument("--seed", type=int, default=20261031)
    parser.add_argument("--n", type=int, default=240)
    parser.add_argument("--interference-pairs", type=int, default=12)
    args = parser.parse_args()

    rows = generate(
        seed=args.seed,
        n=args.n,
        interference_pairs=args.interference_pairs,
    )
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
