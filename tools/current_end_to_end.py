#!/usr/bin/env python3
"""Build one reproducible synthetic end-to-end bundle from current protocol pieces.

This runner is intentionally integration-focused. It does not tune V18/V20
carrier parameters or paper claims. It verifies that the current technical
pipeline and the current mock-paper renderer consume the same current package.

Synthetic/mock benchmark only.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np

LABEL = "MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_corpus(v20: dict, built: dict, seed: int, corpus_size: int, near_fraction: float):
    A = built["A"]
    c = built["c"]
    rng_seed = 9_000_000 + int(seed)
    rng = np.random.default_rng(rng_seed)
    target_index = int(rng.integers(0, corpus_size))
    near_count = int(round((corpus_size - 1) * near_fraction))
    ids = [i for i in range(corpus_size) if i != target_index]
    near_ids = set(int(x) for x in rng.choice(ids, size=near_count, replace=False))
    corpus = [
        c if i == target_index else v20["make_d_descriptor"](A, rng, i in near_ids)
        for i in range(corpus_size)
    ]
    return corpus, {
        "rng_seed": rng_seed,
        "target_index": target_index,
        "corpus_size": corpus_size,
        "near_decoy_fraction": near_fraction,
        "near_decoy_count": near_count,
    }


def run_one(v20: dict, engine: dict, seed: int, payload_bytes: int, channels: int,
            corpus_size: int, near_fraction: float, top_k: int):
    built = v20["build_v20_package"](engine, seed, payload_bytes, channels)
    corpus, recipe = build_corpus(v20, built, seed, corpus_size, near_fraction)
    ranked = v20["rank_candidates"](built["A"], corpus)
    target_index = recipe["target_index"]
    target_rank = next(i + 1 for i, row in enumerate(ranked) if row["index"] == target_index)
    target_score = next(row["score"] for row in ranked if row["index"] == target_index)

    accepted = None
    accepted_rank = None
    rejected_before_target = 0
    for rank, row in enumerate(ranked[:top_k], start=1):
        opened = v20["try_open_v20"](built["A"], engine, corpus[row["index"]])
        if opened["accepted"]:
            accepted = opened
            accepted_rank = rank
            break
        rejected_before_target += 1

    exact = bool(
        accepted
        and accepted["payload_sha256"] == built["B"]["payload_sha256"]
        and accepted.get("payload") == built["payload"]
    )
    return {
        "seed": int(seed),
        "payload_sha256": built["B"]["payload_sha256"],
        "target_rank": int(target_rank),
        "target_locator_score": float(target_score),
        "accepted_rank": accepted_rank,
        "exact_recovery": exact,
        "rejected_candidates_before_accept": int(rejected_before_target),
        "recipe": recipe,
        "built": built,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v20", type=Path, default=Path("protocol/real-package-v20.py"))
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--paper-tool", type=Path, default=Path("tools/paper_v6.py"))
    ap.add_argument("--seeds", default="901,902,903,904,905,906,907,908")
    ap.add_argument("--representative-seed", type=int, default=901)
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--corpus-size", type=int, default=2000)
    ap.add_argument("--near-decoy-fraction", type=float, default=0.01)
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--out-dir", type=Path, default=Path("current_e2e_bundle"))
    args = ap.parse_args()

    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    if args.representative_seed not in seeds:
        raise SystemExit("representative seed must be in --seeds")

    v20 = runpy.run_path(str(args.v20))
    engine = v20["load_engine"](args.engine)

    if args.out_dir.exists():
        import shutil
        shutil.rmtree(args.out_dir)
    args.out_dir.mkdir(parents=True)

    rows = []
    representative = None
    for seed in seeds:
        row = run_one(
            v20, engine, seed,
            args.payload_bytes, args.channels,
            args.corpus_size, args.near_decoy_fraction, args.top_k,
        )
        if seed == args.representative_seed:
            representative = row
        rows.append({k: v for k, v in row.items() if k != "built"})

    assert representative is not None
    hashes = [r["payload_sha256"] for r in rows]
    all_unique = len(set(hashes)) == len(hashes)
    exact_rate = float(np.mean([r["exact_recovery"] for r in rows]))
    recall20 = float(np.mean([r["target_rank"] <= 20 for r in rows]))
    recall100 = float(np.mean([r["target_rank"] <= 100 for r in rows]))
    if not (all_unique and exact_rate == 1.0 and recall100 == 1.0):
        raise SystemExit("current technical E5 gate failed")

    built = representative["built"]
    B = built["B"]
    b = built["b"]
    c = built["c"]
    A = built["A"]

    # Explicit wrong-candidate control.
    control_rng = np.random.default_rng(99_000_000 + args.representative_seed)
    decoy = v20["make_d_descriptor"](A, control_rng, True)
    decoy_open = v20["try_open_v20"](A, engine, decoy)
    if decoy_open["accepted"]:
        raise SystemExit("decoy unexpectedly accepted")

    # Explicit authenticated-envelope tamper control.
    tampered = copy.deepcopy(c)
    raw_r = bytearray(base64.b64decode(tampered[v20["FIELD_REPAIR"]], validate=True))
    if not raw_r:
        raise SystemExit("empty repair field")
    raw_r[0] ^= 0x01
    tampered[v20["FIELD_REPAIR"]] = base64.b64encode(bytes(raw_r)).decode()
    tamper_open = v20["try_open_v20"](A, engine, tampered)
    if tamper_open["accepted"] or tamper_open["reason"] != "v20_envelope_integrity_failed":
        raise SystemExit("repair-field tamper control did not reject at envelope")

    package_path = args.out_dir / "published_v20.npz"
    manifest_path = args.out_dir / "manifest_v20.json"
    candidate_path = args.out_dir / "candidate_c.json"
    recipe_path = args.out_dir / "collection_recipe.json"
    summary_path = args.out_dir / "technical_summary.json"
    e5_path = args.out_dir / "e5_current_v20.json"
    paper_dir = args.out_dir / "paper_v6_output"

    package_path.write_bytes(b)
    manifest_path.write_text(json.dumps(B, indent=2, sort_keys=True), encoding="utf-8")
    candidate_path.write_text(json.dumps(c, indent=2, sort_keys=True), encoding="utf-8")

    recipe = dict(representative["recipe"])
    recipe.update({
        "seed": args.representative_seed,
        "target_rank": representative["target_rank"],
        "target_locator_score": representative["target_locator_score"],
        "rule": "synthetic d records are regenerated from this deterministic recipe",
    })
    recipe_path.write_text(json.dumps(recipe, indent=2), encoding="utf-8")

    summary = {
        "version": "current-e2e-summary-v1",
        "scope": "synthetic-only",
        "payload_bytes": args.payload_bytes,
        "payload_sha256": B["payload_sha256"],
        "exact_recovery": True,
        "protocol": "current V18 carrier + current bounded V20 logical repair envelope",
        "locator": {
            "target_rank": representative["target_rank"],
            "candidate_count": args.corpus_size,
            "target_score": representative["target_locator_score"],
            "top_k": args.top_k,
        },
        "strict_verification": {
            "best_decoy": "REJECTED",
            "target": "ACCEPTED",
            "repair_field_tamper": tamper_open["reason"],
        },
        "paper_input_package_sha256": sha256_bytes(b),
        "paper_input_manifest_semantic_payload_sha256": B["payload_sha256"],
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    e5 = {
        "version": "current-v20-e5-v1",
        "scope": "synthetic-only",
        "runs": rows,
        "summary": {
            "seed_count": len(rows),
            "exact_recovery_rate": exact_rate,
            "recall_at_20": recall20,
            "recall_at_100": recall100,
            "all_payload_hashes_unique": all_unique,
            "median_target_rank": float(np.median([r["target_rank"] for r in rows])),
            "max_target_rank": int(max(r["target_rank"] for r in rows)),
        },
    }
    e5_path.write_text(json.dumps(e5, indent=2), encoding="utf-8")

    subprocess.run([
        sys.executable, str(args.paper_tool),
        "--package", str(package_path),
        "--manifest", str(manifest_path),
        "--summary", str(summary_path),
        "--e5-result", str(e5_path),
        "--out-dir", str(paper_dir),
    ], check=True)

    paper_manifest = json.loads((paper_dir / "paper_manifest.json").read_text(encoding="utf-8"))
    paper_text = (paper_dir / "paper_v6.md").read_text(encoding="utf-8")
    experiments = json.loads((paper_dir / "experiment_results_v6.json").read_text(encoding="utf-8"))
    e5_row = next(x for x in experiments["results"] if x["experiment_id"] == "E5")
    if not paper_manifest.get("e5_completed"):
        raise SystemExit("paper E5 did not consume current V20 integration result")
    if e5_row.get("status") != "COMPLETED" or e5_row.get("pass") is not True:
        raise SystemExit("paper E5 is not a completed passing machine result")
    if LABEL not in paper_text or "SYNTHETIC BENCHMARK / SIMULATED DATA ONLY" not in paper_text:
        raise SystemExit("paper synthetic/mock labels missing")
    if "not evidence of real provenance or mechanism" not in paper_text:
        raise SystemExit("mandatory non-provenance limitation missing")

    result = {
        "version": "current-e2e-integration-result-v1",
        "scope": "synthetic-only",
        "gate_pass": True,
        "technical": e5["summary"],
        "representative": {
            "seed": args.representative_seed,
            "payload_sha256": B["payload_sha256"],
            "target_rank": representative["target_rank"],
            "target_locator_score": representative["target_locator_score"],
            "decoy_rejected": not decoy_open["accepted"],
            "repair_field_tamper_rejected": not tamper_open["accepted"],
        },
        "paper": {
            "e5_completed": True,
            "synthetic_labels_present": True,
            "mandatory_limitation_present": True,
            "paper_path": "paper_v6_output/paper_v6.md",
        },
        "interpretation": "current technical and mock-paper pipelines consume one current V20 package and one current multi-seed machine result",
    }
    result_path = args.out_dir / "integration_result.json"
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    manifest_entries = []
    for path in sorted(p for p in args.out_dir.rglob("*") if p.is_file() and p.name != "bundle_manifest.json"):
        manifest_entries.append({
            "path": path.relative_to(args.out_dir).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    bundle_manifest = {
        "version": "current-e2e-bundle-manifest-v1",
        "scope": "synthetic-only",
        "label": LABEL,
        "files": manifest_entries,
    }
    (args.out_dir / "bundle_manifest.json").write_text(json.dumps(bundle_manifest, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
