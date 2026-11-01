#!/usr/bin/env python3
"""
publication_robustness_v17.py

Synthetic-only publication-pipeline robustness benchmark.

Tests:
- row/column reorder;
- table split/merge;
- unit transforms;
- decimal/significant-digit changes;
- post-publication re-quantization;
- spacing-guard profiles.

No real papers, secrets, model weights, or confidential payloads are used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import runpy
import shutil
from pathlib import Path

import numpy as np


PROFILES = {
    "current": {8: 2.0, 16: 2.5, 32: 3.0},
    "guarded": {8: 3.0, 16: 3.5, 32: 4.5},
    "strong_guard": {8: 4.0, 16: 5.0, 32: 6.0},
    "very_strong_guard": {8: 5.0, 16: 6.5, 32: 8.0},
    "extreme_guard": {8: 6.0, 16: 8.0, 32: 10.0},
}


def load_namespace(source: Path):
    return runpy.run_path(str(source))


def decode_package(ns, arrays, manifest):
    decode_table = ns["decode_table"]
    bits_to_bytes = ns["bits_to_bytes"]

    recovered_bits = np.zeros(
        int(manifest["payload_bit_length"]), dtype=np.uint8
    )
    for table in manifest["tables"]:
        table_id = int(table["table_id"])
        bits = decode_table(arrays[f"table_{table_id}_y"], table)
        offset = int(table["payload_bit_offset"])
        recovered_bits[offset:offset + len(bits)] = bits

    decoded = bits_to_bytes(recovered_bits)[:int(manifest["payload_bytes"])]
    sha = hashlib.sha256(decoded).hexdigest()
    return sha == manifest["payload_sha256"], sha


def build_labeled_table(pub, table):
    segments = int(table["segments"])
    n = int(table["points_per_block"])
    channels = int(table["channels"])

    return {
        "y": pub.copy(),
        "segment_id": np.repeat(np.arange(segments, dtype=np.int32), n),
        "x_index": np.tile(np.arange(n, dtype=np.int16), segments),
        "channel_id": np.arange(channels, dtype=np.int16),
    }


def canonicalize_labeled_table(table):
    row_order = np.lexsort((table["x_index"], table["segment_id"]))
    col_order = np.argsort(table["channel_id"], kind="stable")
    return table["y"][row_order][:, col_order]


def shuffle_rows_cols_labeled(arrays, manifest, rng, rows=True, cols=True):
    raw = {}
    labeled = {}

    for table in manifest["tables"]:
        table_id = int(table["table_id"])
        t = build_labeled_table(arrays[f"table_{table_id}_y"], table)

        if rows:
            p = rng.permutation(len(t["y"]))
            t["y"] = t["y"][p]
            t["segment_id"] = t["segment_id"][p]
            t["x_index"] = t["x_index"][p]

        if cols:
            p = rng.permutation(t["y"].shape[1])
            t["y"] = t["y"][:, p]
            t["channel_id"] = t["channel_id"][p]

        labeled[table_id] = t
        raw[f"table_{table_id}_y"] = t["y"]
        raw[f"table_{table_id}_x"] = arrays[f"table_{table_id}_x"]

    return raw, labeled


def arrays_from_labeled(labeled, arrays, manifest):
    out = {}
    for table in manifest["tables"]:
        table_id = int(table["table_id"])
        out[f"table_{table_id}_y"] = canonicalize_labeled_table(
            labeled[table_id]
        )
        out[f"table_{table_id}_x"] = arrays[f"table_{table_id}_x"]
    return out


def split_merge_labeled(arrays, manifest, rng, pieces=4):
    labeled = {}
    for table in manifest["tables"]:
        table_id = int(table["table_id"])
        t = build_labeled_table(arrays[f"table_{table_id}_y"], table)
        chunks = np.array_split(np.arange(len(t["y"])), pieces)
        rng.shuffle(chunks)

        shuffled = []
        for chunk in chunks:
            chunk = chunk.copy()
            rng.shuffle(chunk)
            shuffled.append(chunk)

        order = np.concatenate(shuffled)
        t["y"] = t["y"][order]
        t["segment_id"] = t["segment_id"][order]
        t["x_index"] = t["x_index"][order]
        labeled[table_id] = t

    return arrays_from_labeled(labeled, arrays, manifest)


def apply_unit_transform(arrays, manifest, a=1000.0, b=0.0, only_families=None):
    out = {k: v.copy() for k, v in arrays.items()}
    for table in manifest["tables"]:
        if only_families is not None and table["family"] not in only_families:
            continue
        table_id = int(table["table_id"])
        key = f"table_{table_id}_y"
        out[key] = a * out[key] + b
    return out


def invert_unit_transform(arrays, manifest, a=1000.0, b=0.0, only_families=None):
    out = {k: v.copy() for k, v in arrays.items()}
    for table in manifest["tables"]:
        if only_families is not None and table["family"] not in only_families:
            continue
        table_id = int(table["table_id"])
        key = f"table_{table_id}_y"
        out[key] = (out[key] - b) / a
    return out


def requantize(arrays, manifest, factor):
    out = {k: v.copy() for k, v in arrays.items()}

    for table in manifest["tables"]:
        table_id = int(table["table_id"])
        key = f"table_{table_id}_y"
        y = out[key]
        step = float(table["publication_step"]) * factor

        if table.get("publication_model") == "log_step":
            z = np.log(y)
            out[key] = np.exp(np.round(z / step) * step)
        else:
            out[key] = np.round(y / step) * step

    return out


def decimal_round(arrays, decimals):
    out = {k: v.copy() for k, v in arrays.items()}
    for key in out:
        if key.endswith("_y"):
            out[key] = np.round(out[key], decimals)
    return out


def significant_round(arrays, digits):
    out = {k: v.copy() for k, v in arrays.items()}
    for key in out:
        if not key.endswith("_y"):
            continue
        y = out[key]
        magnitude = np.floor(np.log10(np.abs(y)))
        scale = np.power(10.0, digits - 1 - magnitude)
        out[key] = np.round(y * scale) / scale
    return out


def patch_delta_multiples(source_text, multiples):
    old = (
        'Q_MODES = {\n'
        '    8:  {"m": 3, "poly": 0b1011,   "delta_multiple": 2.0},\n'
        '    16: {"m": 4, "poly": 0b10011,  "delta_multiple": 2.5},\n'
        '    32: {"m": 5, "poly": 0b100101, "delta_multiple": 3.0},\n'
        '}'
    )
    new = (
        'Q_MODES = {\n'
        f'    8:  {{"m": 3, "poly": 0b1011,   "delta_multiple": {multiples[8]}}},\n'
        f'    16: {{"m": 4, "poly": 0b10011,  "delta_multiple": {multiples[16]}}},\n'
        f'    32: {{"m": 5, "poly": 0b100101, "delta_multiple": {multiples[32]}}},\n'
        '}'
    )
    if old not in source_text:
        raise RuntimeError("expected Q_MODES block not found")
    return source_text.replace(old, new, 1)


def base_transform_tests(ns, arrays, manifest, rng):
    tests = []

    def record(name, category, candidate, note):
        try:
            ok, sha = decode_package(ns, candidate, manifest)
            error = None
        except Exception as exc:
            ok = False
            sha = None
            error = f"{type(exc).__name__}: {exc}"
        tests.append({
            "name": name,
            "category": category,
            "exact_recovery": bool(ok),
            "decoded_sha256": sha,
            "note": note,
            "error": error,
        })

    record("baseline", "reference", arrays, "No post-publication transform.")

    raw, labeled = shuffle_rows_cols_labeled(
        arrays, manifest, rng, rows=False, cols=True
    )
    record(
        "column_reorder_unlabeled",
        "destructive_without_labels",
        raw,
        "Channel identity discarded.",
    )
    record(
        "column_reorder_labeled",
        "canonicalizable",
        arrays_from_labeled(labeled, arrays, manifest),
        "Public channel labels restore canonical order.",
    )

    raw, labeled = shuffle_rows_cols_labeled(
        arrays, manifest, rng, rows=True, cols=False
    )
    record(
        "row_reorder_unlabeled",
        "destructive_without_labels",
        raw,
        "Segment/x identity discarded.",
    )
    record(
        "row_reorder_labeled",
        "canonicalizable",
        arrays_from_labeled(labeled, arrays, manifest),
        "Public segment/x labels restore order.",
    )

    raw, labeled = shuffle_rows_cols_labeled(
        arrays, manifest, rng, rows=True, cols=True
    )
    record(
        "row_column_reorder_labeled",
        "canonicalizable",
        arrays_from_labeled(labeled, arrays, manifest),
        "Both axes reordered and canonicalized.",
    )

    record(
        "table_split_merge_labeled",
        "canonicalizable",
        split_merge_labeled(arrays, manifest, rng, pieces=5),
        "Table fragments shuffled then regrouped by labels.",
    )

    gaussian_scaled = apply_unit_transform(
        arrays, manifest, a=1000.0, b=0.0, only_families={"gaussian"}
    )
    record(
        "gaussian_log_multiplicative_scale_unknown",
        "natural_invariant",
        gaussian_scaled,
        "Log-domain Gaussian tables multiplied by 1000 with no scale metadata.",
    )

    all_scaled = apply_unit_transform(
        arrays, manifest, a=1000.0, b=273.15
    )
    record(
        "all_tables_affine_unit_transform_unknown",
        "destructive_without_metadata",
        all_scaled,
        "Unknown y'=1000*y+273.15.",
    )
    record(
        "all_tables_affine_unit_transform_with_metadata",
        "canonicalizable",
        invert_unit_transform(all_scaled, manifest, a=1000.0, b=273.15),
        "Public unit metadata restores canonical numeric domain.",
    )

    for factor in (1.0, 1.5, 2.0, 3.0):
        record(
            f"requantize_{factor:g}x_step",
            "precision_stress",
            requantize(arrays, manifest, factor),
            f"Re-quantized at {factor:g}x original publication step.",
        )

    for decimals in (3, 2, 1):
        record(
            f"decimal_round_{decimals}",
            "precision_stress",
            decimal_round(arrays, decimals),
            f"Rounded to {decimals} digits after decimal point.",
        )

    for digits in (5, 4, 3):
        record(
            f"significant_digits_{digits}",
            "precision_stress",
            significant_round(arrays, digits),
            f"Rounded to {digits} significant digits.",
        )

    return tests


def spacing_profile_sweep(adaptive_source, out_dir, payload_bytes=32768, channels=16):
    source_text = adaptive_source.read_text(encoding="utf-8")
    rows = []

    for name, multiples in PROFILES.items():
        profile_source = out_dir / f"adaptive_{name}.py"
        profile_source.write_text(
            patch_delta_multiples(source_text, multiples),
            encoding="utf-8",
        )
        ns = load_namespace(profile_source)

        profile_dir = out_dir / f"profile_{name}"
        profile_dir.mkdir(parents=True, exist_ok=True)

        result = ns["run_package"](
            payload_bytes=payload_bytes,
            channels=channels,
            out_dir=profile_dir,
        )

        manifest = json.loads(
            (profile_dir / "manifest_adaptive_q_v12.json").read_text(
                encoding="utf-8"
            )
        )
        npz = np.load(profile_dir / "published_adaptive_q_v12.npz")
        arrays = {k: npz[k].copy() for k in npz.files}

        exact = {}
        for factor in (
            1.0, 1.25, 1.5, 1.75, 2.0,
            2.5, 2.75, 3.0, 3.25, 3.5, 4.0,
        ):
            exact[str(factor)] = bool(
                decode_package(
                    ns,
                    requantize(arrays, manifest, factor),
                    manifest,
                )[0]
            )

        selected = result["selected_tables"]
        rows.append({
            "profile": name,
            "delta_multiples": multiples,
            "q_distribution": result["q_distribution"],
            "published_rows": result["published_rows_total"],
            "gross_bits_per_value": result["gross_bits_per_numeric_value"],
            "net_bits_per_row_after_manifest":
                result["net_bits_per_row_after_manifest"],
            "mean_calibration_nrmse": float(
                np.mean([t["calibration_nrmse"] for t in selected])
            ),
            "max_calibration_nrmse": float(
                np.max([t["calibration_nrmse"] for t in selected])
            ),
            "requantization_exact": exact,
        })

    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--adaptive-source",
        type=Path,
        default=Path("adaptive_q_package_v12.py"),
    )
    ap.add_argument("--out-dir", type=Path, default=Path("v17_out"))
    ap.add_argument("--payload-bytes", type=int, default=65536)
    ap.add_argument("--channels", type=int, default=16)
    args = ap.parse_args()

    if args.out_dir.exists():
        shutil.rmtree(args.out_dir)
    args.out_dir.mkdir(parents=True)

    ns = load_namespace(args.adaptive_source)
    base_dir = args.out_dir / "base"
    result = ns["run_package"](
        payload_bytes=args.payload_bytes,
        channels=args.channels,
        out_dir=base_dir,
    )

    manifest = json.loads(
        (base_dir / "manifest_adaptive_q_v12.json").read_text(encoding="utf-8")
    )
    npz = np.load(base_dir / "published_adaptive_q_v12.npz")
    arrays = {k: npz[k].copy() for k in npz.files}

    output = {
        "scope": "synthetic-only publication robustness",
        "base_payload_bytes": args.payload_bytes,
        "base_exact": result["exact_recovery"],
        "base_tests": base_transform_tests(
            ns, arrays, manifest, np.random.default_rng(17001)
        ),
        "spacing_profiles": spacing_profile_sweep(
            args.adaptive_source,
            args.out_dir,
            payload_bytes=32768,
            channels=args.channels,
        ),
    }

    result_path = args.out_dir / "publication_robustness_v17.json"
    result_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
