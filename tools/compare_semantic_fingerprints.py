#!/usr/bin/env python3
"""Strictly compare two current-bundle semantic fingerprints.

Raw NPZ/manifest container hashes are diagnostic only. All semantic authority
fields must match exactly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def map_by(items, key):
    return {item[key]: item for item in items}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=Path, required=True)
    ap.add_argument("--b", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    a = load(args.a)
    b = load(args.b)
    mismatches = []

    scalar_fields = [
        "payload_sha256",
        "basis_version_top_level",
        "basis_versions_tables",
        "canonical_B_sha256",
        "technical_summary_canonical_sha256",
        "e5_current_v20_canonical_sha256",
        "integration_result_canonical_sha256",
        "paper_v7_numeric_figure_plan_canonical_sha256",
        "selected_morphology_examples",
        "presentation_archetype",
        "story_type",
        "semantic_authority_sha256",
    ]
    for field in scalar_fields:
        if a.get(field) != b.get(field):
            mismatches.append({"kind": "field", "field": field, "a": a.get(field), "b": b.get(field)})

    arrays_a = map_by(a.get("npz_semantic_arrays", []), "name")
    arrays_b = map_by(b.get("npz_semantic_arrays", []), "name")
    if set(arrays_a) != set(arrays_b):
        mismatches.append({
            "kind": "npz_array_set",
            "only_a": sorted(set(arrays_a) - set(arrays_b)),
            "only_b": sorted(set(arrays_b) - set(arrays_a)),
        })
    for name in sorted(set(arrays_a) & set(arrays_b)):
        for field in ("shape", "dtype", "sha256"):
            if arrays_a[name].get(field) != arrays_b[name].get(field):
                mismatches.append({
                    "kind": "npz_array",
                    "name": name,
                    "field": field,
                    "a": arrays_a[name].get(field),
                    "b": arrays_b[name].get(field),
                })

    csv_a = map_by(a.get("paper_v7_csvs", []), "table_id")
    csv_b = map_by(b.get("paper_v7_csvs", []), "table_id")
    if set(csv_a) != set(csv_b):
        mismatches.append({
            "kind": "csv_table_set",
            "only_a": sorted(set(csv_a) - set(csv_b)),
            "only_b": sorted(set(csv_b) - set(csv_a)),
        })
    for tid in sorted(set(csv_a) & set(csv_b)):
        for field in ("sha256", "rows", "channels"):
            if csv_a[tid].get(field) != csv_b[tid].get(field):
                mismatches.append({
                    "kind": "csv",
                    "table_id": tid,
                    "field": field,
                    "a": csv_a[tid].get(field),
                    "b": csv_b[tid].get(field),
                })

    result = {
        "version": "semantic-fingerprint-comparison-v1",
        "scope": "synthetic-only",
        "semantic_equal": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "diagnostic_raw_container_hash_equal": a.get("raw_container_hashes") == b.get("raw_container_hashes"),
        "a_semantic_authority_sha256": a.get("semantic_authority_sha256"),
        "b_semantic_authority_sha256": b.get("semantic_authority_sha256"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if mismatches:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
