#!/usr/bin/env python3
"""Final packaging audit for paper bundle v7.

Runs only after paper_bundle_v7.py has finished. It does not alter figures,
data, claims, or technical evidence; it verifies the complete output directory
and writes a final manifest that covers every pre-existing paper-v7 file,
including validation_result.json and paper_v7_manifest.json.

Synthetic/mock benchmark only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

LABEL = "MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS"
SYNTHETIC = "SYNTHETIC BENCHMARK / SIMULATED DATA ONLY"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper-dir", type=Path, required=True)
    args = ap.parse_args()
    root = args.paper_dir

    required = [
        "paper_v7.md",
        "paper_v7_manifest.json",
        "validation_result.json",
        "figure_plan.json",
        "figure_manifest.json",
        "data_manifest.json",
        "traceability.json",
        "figures/fig1_overview.svg",
        "figures/fig2_morphology_examples.svg",
        "figures/fig3_fit_ablation.svg",
        "figures/fig4_e5_control.svg",
    ]
    missing = [p for p in required if not (root / p).is_file()]
    if missing:
        raise SystemExit(f"missing required paper-v7 outputs: {missing}")

    validation = load_json(root / "validation_result.json")
    paper_manifest = load_json(root / "paper_v7_manifest.json")
    figure_manifest = load_json(root / "figure_manifest.json")
    data_manifest = load_json(root / "data_manifest.json")
    trace = load_json(root / "traceability.json")
    paper = (root / "paper_v7.md").read_text(encoding="utf-8")

    if validation.get("gate_pass") is not True or paper_manifest.get("gate_pass") is not True:
        raise SystemExit("upstream paper-v7 gate did not pass")
    if LABEL not in paper or SYNTHETIC not in paper:
        raise SystemExit("required synthetic/mock labels missing")
    if set(trace.get("claims", {})) != {"C1", "C2", "C4", "C5"}:
        raise SystemExit("traceability claim set mismatch")

    # Re-verify nested manifest hashes before creating the complete manifest.
    mismatches = []
    for entry in figure_manifest["figures"]:
        p = root / entry["path"]
        if not p.exists() or sha256_file(p) != entry["sha256"]:
            mismatches.append(entry["path"])
    for entry in data_manifest["tables"]:
        p = root / entry["path"]
        if not p.exists() or sha256_file(p) != entry["sha256"]:
            mismatches.append(entry["path"])
    for entry in paper_manifest["files"]:
        p = root / entry["path"]
        if not p.exists() or p.stat().st_size != int(entry["bytes"]) or sha256_file(p) != entry["sha256"]:
            mismatches.append(entry["path"])
    if mismatches:
        raise SystemExit(f"nested manifest mismatch: {sorted(set(mismatches))}")

    final_name = "paper_v7_bundle_manifest.json"
    entries = []
    for p in sorted(x for x in root.rglob("*") if x.is_file() and x.name != final_name):
        entries.append({
            "path": p.relative_to(root).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        })

    required_covered = all(any(e["path"] == p for e in entries) for p in required)
    if not required_covered:
        raise SystemExit("final manifest did not cover every required output")

    final = {
        "version": "paper-v7-complete-bundle-manifest-v1",
        "scope": "synthetic-only",
        "label": LABEL,
        "gate_pass": True,
        "source_npz_sha256": validation["source_npz_sha256"],
        "figure_count": validation["figure_count"],
        "raw_data_table_count": validation["raw_data_table_count"],
        "required_claims_traced": validation["required_claims_traced"],
        "covers_validation_result": True,
        "covers_paper_v7_manifest": True,
        "nested_manifest_mismatch_count": 0,
        "file_count": len(entries),
        "files": entries,
    }
    (root / final_name).write_text(json.dumps(final, indent=2), encoding="utf-8")
    print(json.dumps({
        "gate_pass": True,
        "file_count": len(entries),
        "covers_validation_result": True,
        "covers_paper_v7_manifest": True,
        "nested_manifest_mismatch_count": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
