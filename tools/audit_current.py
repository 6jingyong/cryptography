#!/usr/bin/env python3
"""Machine audit for the current synthetic-only protocol evidence.

This script does not extend the carrier or optimize capacity. It checks the
current audit gate: code compilation, recorded E5 integrity, and two fresh
Protocol-v3 full re-encode/recovery seeds.
"""
from __future__ import annotations

import compileall
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> None:
    # 1) Current Python code must at least compile.
    for rel in ("protocol", "src", "tools"):
        ok = compileall.compile_dir(ROOT / rel, quiet=1, force=True)
        require(ok, f"compileall failed: {rel}")

    # 2) Recorded E5 file must match the claims made in current docs.
    e5 = json.loads((ROOT / "results/e5-multiseed-final.json").read_text())
    runs = e5["runs"]
    hashes = [r["payload_sha256"] for r in runs]
    require(len(runs) == 8, "E5 must contain exactly 8 recorded runs")
    require(len(set(hashes)) == 8, "E5 payload hashes are not all unique")
    require(all(r["exact_recovery"] for r in runs), "E5 contains a non-exact run")
    require(e5["summary"]["exact_recovery_rate"] == 1.0, "E5 exact recovery summary mismatch")
    require(e5["summary"]["recall_at_20"] == 1.0, "E5 Recall@20 mismatch")
    require(e5["summary"]["recall_at_100"] == 1.0, "E5 Recall@100 mismatch")

    # 3) Fresh independent seeds on the repository implementation itself.
    v3 = runpy.run_path(str(ROOT / "protocol/real-package-v3.py"))
    run_seed = v3["run_seed"]
    engine = ROOT / "src/adaptive_q_package_v12.py"
    fresh = []
    for seed in (101, 102):
        r = run_seed(
            engine_path=engine,
            payload_seed=seed,
            payload_bytes=512,
            channels=2,
            corpus_size=2000,
            near_decoy_fraction=0.01,
            top_k=100,
        )
        require(r["exact_recovery"] is True, f"fresh seed {seed} failed exact recovery")
        require(r["target_rank"] <= 100, f"fresh seed {seed} fell outside Top-100")
        fresh.append(r)
    require(
        fresh[0]["payload_sha256"] != fresh[1]["payload_sha256"],
        "fresh seeds generated identical payload hashes",
    )

    result = {
        "status": "PASS",
        "scope": "synthetic-only",
        "recorded_e5": {
            "runs": 8,
            "unique_payload_hashes": 8,
            "exact_recovery_rate": 1.0,
            "recall_at_20": 1.0,
            "recall_at_100": 1.0,
        },
        "fresh_protocol_v3": [
            {
                "payload_seed": r["payload_seed"],
                "payload_sha256": r["payload_sha256"],
                "target_rank": r["target_rank"],
                "accepted_rank": r["accepted_rank"],
                "exact_recovery": r["exact_recovery"],
                "target_locator_score": r["target_locator_score"],
            }
            for r in fresh
        ],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
