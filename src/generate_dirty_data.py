#!/usr/bin/env python3
"""
Generate a reproducible synthetic "dirty" 2D dataset.

The dataset intentionally includes several common data-quality issues:
- smooth latent trend
- heteroskedastic noise
- slow instrument drift
- occasional outliers
- mixed rounding precision
- missing metadata
- duplicate-like rows

The latent function is used only to generate the benchmark and should not be
used by downstream grouping/validation algorithms.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path


def generate(seed: int = 20261031, n: int = 240) -> list[dict[str, object]]:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []

    for i in range(n):
        x = i / 12.0

        # Smooth positive latent process.
        base = (
            35.0
            + 2.4 * x
            + 8.0 * math.sin(x / 2.8)
            + 3.5 * math.cos(x / 1.7)
        )

        # Heteroskedastic measurement noise.
        sigma = 1.4 + 0.12 * x
        y = base + rng.gauss(0.0, sigma)

        source = "A" if i % 3 else "B"
        quality = "ok"

        # Slow drift in the latter part of the measurement range.
        if x > 12:
            y += 0.22 * (x - 12)

        # Sparse outlier-like observations.
        if rng.random() < 0.04:
            y += rng.choice((-1, 1)) * rng.uniform(8, 18)
            quality = "outlier_like"

        # Mixed instrument/reporting precision.
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

        # Missing metadata, not missing measurement values, in v0.
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
            }
        )

    # Add a few duplicate-like records to mimic export / merge artifacts.
    duplicate_indices = rng.sample(range(n), 6)
    for new_id, source_idx in enumerate(duplicate_indices, start=n):
        duplicate = dict(rows[source_idx])
        duplicate["row_id"] = new_id
        duplicate["note"] = "duplicate_like"
        rows.append(duplicate)

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
        default=Path("data/synthetic_dirty_v0.csv"),
    )
    parser.add_argument("--seed", type=int, default=20261031)
    parser.add_argument("--n", type=int, default=240)
    args = parser.parse_args()

    rows = generate(seed=args.seed, n=args.n)
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
