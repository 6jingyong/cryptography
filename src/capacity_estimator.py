#!/usr/bin/env python3
"""Capacity/expansion estimator for the current dirty-channel toy model.

This script does not encode a real payload. It quantifies how much information
is represented by a coarse per-bin state alphabet and how that maps to carrier
expansion under a simple bytes-per-row assumption.
"""
from __future__ import annotations

import argparse
import math


def log2_comb(n: int, k: int) -> float:
    return (
        math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    ) / math.log(2)


def metrics(rows: int, bins: int, states: int, bytes_per_row: float) -> dict[str, float]:
    bits_per_bin = math.log2(states)
    bits_total = bins * bits_per_bin
    bits_per_row = bits_total / rows
    expansion = bytes_per_row * 8.0 / bits_per_row
    return {
        "bits_per_bin": bits_per_bin,
        "bits_total": bits_total,
        "bits_per_row": bits_per_row,
        "carrier_bytes_per_payload_byte": expansion,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=1224)
    ap.add_argument("--bins", type=int, default=20)
    ap.add_argument("--bytes-per-row", type=float, default=32.0)
    ap.add_argument("--states", type=int, nargs="*", default=[3, 7, 13, 37])
    ap.add_argument("--remaining-per-bin", type=int, default=49)
    ap.add_argument("--codebook-count", type=int, default=15)
    args = ap.parse_args()

    for s in args.states:
        m = metrics(args.rows, args.bins, s, args.bytes_per_row)
        print(
            f"states={s:>3} bits/bin={m['bits_per_bin']:.3f} "
            f"bits/row={m['bits_per_row']:.5f} "
            f"expansion={m['carrier_bytes_per_payload_byte']:.1f}x"
        )

    ceiling_bits = log2_comb(args.remaining_per_bin, args.codebook_count)
    ceiling_bpr = ceiling_bits / (args.rows / args.bins)
    ceiling_expansion = args.bytes_per_row * 8.0 / ceiling_bpr
    print(
        "subset-index ceiling: "
        f"log2(C({args.remaining_per_bin},{args.codebook_count}))="
        f"{ceiling_bits:.3f} bits/bin, {ceiling_bpr:.5f} bits/row, "
        f"{ceiling_expansion:.1f}x"
    )


if __name__ == "__main__":
    main()
