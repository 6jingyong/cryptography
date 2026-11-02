#!/usr/bin/env python3
"""Create a semantic fingerprint of one current E2E + paper-v7 bundle.

The fingerprint deliberately separates semantic numeric content from container
bytes. NPZ/ZIP byte identity is reported but is not the authority: canonical B,
per-table float64 arrays, exported CSVs, E5, and paper-v7 numeric plans are.

Synthetic/mock benchmark only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_json_hash(obj) -> str:
    return sha256_bytes(canonical_json_bytes(obj))


def canonicalize_float_array(a: np.ndarray) -> np.ndarray:
    """Return C-contiguous little-endian float64 semantic bytes.

    This avoids depending on host endian/layout while preserving exact float64
    values. NaN payloads are not expected in the current benchmark.
    """
    arr = np.asarray(a, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise RuntimeError("semantic fingerprint encountered non-finite numeric data")
    return np.ascontiguousarray(arr.astype("<f8", copy=False))


def array_record(name: str, a: np.ndarray):
    arr = canonicalize_float_array(a)
    return {
        "name": name,
        "shape": list(arr.shape),
        "dtype": "<f8",
        "sha256": sha256_bytes(arr.tobytes(order="C")),
        "min": float(np.min(arr)) if arr.size else None,
        "max": float(np.max(arr)) if arr.size else None,
    }


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def numeric_figure_plan(plan: dict) -> dict:
    """Extract the semantic numeric/selection content from paper-v7 plan.

    File paths and prose captions are intentionally excluded from the authority.
    """
    out = {
        "version": plan.get("version"),
        "source_npz_sha256": plan.get("source_npz_sha256"),
        "figures": [],
    }
    for fig in plan.get("figures", []):
        rec = {
            "figure_id": fig.get("figure_id"),
            "role": fig.get("role"),
            "claim_ids": fig.get("claim_ids"),
        }
        if "table_ids" in fig:
            rec["table_ids"] = fig["table_ids"]
        if "selected" in fig:
            rec["selected"] = fig["selected"]
        if "rows" in fig:
            rec["rows"] = fig["rows"]
        if "e5_summary" in fig:
            rec["e5_summary"] = fig["e5_summary"]
        out["figures"].append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    root = args.bundle
    paper = root / "paper_v7_output"
    required = [
        root / "published_v20.npz",
        root / "manifest_v20.json",
        root / "technical_summary.json",
        root / "e5_current_v20.json",
        root / "integration_result.json",
        paper / "figure_plan.json",
        paper / "data_manifest.json",
        paper / "validation_result.json",
        paper / "paper_v7_manifest.json",
        paper / "paper_v7_bundle_manifest.json",
    ]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit(f"missing current bundle inputs: {missing}")

    B = load_json(root / "manifest_v20.json")
    technical = load_json(root / "technical_summary.json")
    e5 = load_json(root / "e5_current_v20.json")
    integration = load_json(root / "integration_result.json")
    figure_plan = load_json(paper / "figure_plan.json")
    validation = load_json(paper / "validation_result.json")
    data_manifest = load_json(paper / "data_manifest.json")

    if integration.get("gate_pass") is not True or validation.get("gate_pass") is not True:
        raise SystemExit("upstream current E2E or paper-v7 gate did not pass")

    # Canonical B semantics: JSON object ordering/whitespace are irrelevant.
    canonical_B_hash = canonical_json_hash(B)

    # Current NPZ semantic arrays, sorted by table id and x/y role.
    z = np.load(root / "published_v20.npz")
    arrays = []
    table_ids = sorted(int(t["table_id"]) for t in B["tables"])
    for tid in table_ids:
        for suffix in ("x", "y"):
            key = f"table_{tid}_{suffix}"
            if key not in z.files:
                raise SystemExit(f"missing NPZ array {key}")
            rec = array_record(key, z[key])
            rec["table_id"] = tid
            rec["role"] = suffix
            arrays.append(rec)

    # CSV bytes are authoritative presentation inputs; paper-v7 writes them
    # deterministically from the same current visible arrays.
    csvs = []
    for entry in sorted(data_manifest["tables"], key=lambda x: int(x["table_id"])):
        path = paper / entry["path"]
        if not path.is_file():
            raise SystemExit(f"missing paper-v7 CSV: {path}")
        csvs.append({
            "table_id": int(entry["table_id"]),
            "path": entry["path"],
            "sha256": sha256_file(path),
            "rows": int(entry["rows"]),
            "channels": int(entry["channels"]),
        })

    numeric_plan = numeric_figure_plan(figure_plan)

    fingerprint = {
        "version": "current-bundle-semantic-fingerprint-v1",
        "scope": "synthetic-only",
        "payload_sha256": B["payload_sha256"],
        "basis_version_top_level": B.get("basis_version"),
        "basis_versions_tables": sorted(set(t.get("basis_version") for t in B["tables"])),
        "raw_container_hashes": {
            "published_v20_npz": sha256_file(root / "published_v20.npz"),
            "manifest_v20_json": sha256_file(root / "manifest_v20.json"),
        },
        "canonical_B_sha256": canonical_B_hash,
        "technical_summary_canonical_sha256": canonical_json_hash(technical),
        "e5_current_v20_canonical_sha256": canonical_json_hash(e5),
        "integration_result_canonical_sha256": canonical_json_hash(integration),
        "npz_semantic_arrays": arrays,
        "paper_v7_csvs": csvs,
        "paper_v7_numeric_figure_plan_canonical_sha256": canonical_json_hash(numeric_plan),
        "paper_v7_numeric_figure_plan": numeric_plan,
        "selected_morphology_examples": validation.get("selected_morphology_examples"),
        "presentation_archetype": validation.get("presentation_archetype"),
        "story_type": validation.get("story_type"),
        "current_e5": validation.get("current_e5"),
    }

    # Aggregate semantic hash intentionally excludes raw NPZ/manifest container
    # hashes and path/prose metadata.
    semantic_authority = {
        "payload_sha256": fingerprint["payload_sha256"],
        "basis_version_top_level": fingerprint["basis_version_top_level"],
        "basis_versions_tables": fingerprint["basis_versions_tables"],
        "canonical_B_sha256": fingerprint["canonical_B_sha256"],
        "technical_summary_canonical_sha256": fingerprint["technical_summary_canonical_sha256"],
        "e5_current_v20_canonical_sha256": fingerprint["e5_current_v20_canonical_sha256"],
        "integration_result_canonical_sha256": fingerprint["integration_result_canonical_sha256"],
        "npz_semantic_arrays": [
            {k: r[k] for k in ("name", "shape", "dtype", "sha256", "table_id", "role")}
            for r in arrays
        ],
        "paper_v7_csvs": [
            {k: r[k] for k in ("table_id", "sha256", "rows", "channels")}
            for r in csvs
        ],
        "paper_v7_numeric_figure_plan_canonical_sha256": fingerprint["paper_v7_numeric_figure_plan_canonical_sha256"],
        "selected_morphology_examples": fingerprint["selected_morphology_examples"],
        "presentation_archetype": fingerprint["presentation_archetype"],
        "story_type": fingerprint["story_type"],
    }
    fingerprint["semantic_authority_sha256"] = canonical_json_hash(semantic_authority)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(fingerprint, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "semantic_authority_sha256": fingerprint["semantic_authority_sha256"],
        "canonical_B_sha256": canonical_B_hash,
        "table_count": len(table_ids),
        "csv_count": len(csvs),
        "basis_version": fingerprint["basis_version_top_level"],
    }, indent=2))


if __name__ == "__main__":
    main()
