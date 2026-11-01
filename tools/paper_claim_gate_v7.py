#!/usr/bin/env python3
"""Machine-backed claim gate for the synthetic/mock paper line.

The gate does not generate new scientific claims. It checks whether the bounded
claim roles named by the audit handoff are supported by checked-in machine
results plus an explicit structural-v4 result supplied at runtime.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def by_id(experiments: dict) -> dict[str, dict]:
    return {x["experiment_id"]: x for x in experiments["results"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v4-result", type=Path, required=True)
    ap.add_argument("--json-out", type=Path, default=Path("paper-claim-audit-v7.json"))
    ap.add_argument("--md-out", type=Path, default=Path("paper-claim-audit-v7.md"))
    args = ap.parse_args()

    ex = json.loads((ROOT / "results/paper-v6-experiments.json").read_text())
    e5 = json.loads((ROOT / "results/e5-multiseed-final.json").read_text())
    v4 = json.loads(args.v4_result.read_text())
    paper_source = (ROOT / "tools/paper_v6.py").read_text()
    E = by_id(ex)
    v4_rows = {x["scenario"]: x for x in v4["results"]}

    c1 = bool(E["E1"]["pass"] and E["E2"]["pass"])
    c2 = bool(
        E["E3"]["pass"]
        and E["E3"]["matched_fit_beats_linear_fraction"] == 1.0
        and E["E3"]["median_delta_r2"] > 0
    )
    c3 = bool(E["E4"]["pass"] and E["E4"]["leave_one_out_archetype_retention_rate"] >= 0.8)
    c4 = bool(
        E["E5"]["pass"]
        and e5["summary"]["exact_recovery_rate"] == 1.0
        and e5["summary"]["recall_at_100"] == 1.0
        and e5["summary"]["all_payload_hashes_unique"] is True
    )
    limitation_text = "not evidence of real provenance or mechanism"
    c5 = bool(
        E["E6"]["pass"]
        and E["E6"].get("present_in_paper") is True
        and limitation_text in paper_source
        and "Mandatory limitation" in paper_source
    )

    # C6 is deliberately bounded to the explicit descriptor-level v4 model.
    # We require the heavy-damage failures to remain visible rather than only
    # checking successful conditions.
    c6 = bool(
        v4["important_boundary"]["current_v3_npz_deletion_support_claimed"] is False
        and v4["important_boundary"]["current_v3_split_merge_support_claimed"] is False
        and v4_rows["baseline"]["recall_at_100"] == 1.0
        and v4_rows["deletion_25pct"]["recall_at_100"] == 1.0
        and v4_rows["deletion_50pct"]["recall_at_1000"] == 0.0
        and v4_rows["deletion_50pct_plus_substitution_20pct"]["recall_at_1000"] == 0.0
    )

    claims = [
        {
            "claim_id": "C1",
            "pass": c1,
            "bounded_claim": "Multiple synthetic response regimes are stable only under the tested perturbation and leave-one-out conditions.",
            "evidence": {"E1_pass": E["E1"]["pass"], "E2_pass": E["E2"]["pass"]},
        },
        {
            "claim_id": "C2",
            "pass": c2,
            "bounded_claim": "Morphology-matched descriptive fits beat the tested linear baseline on the tested nonlinear tables.",
            "evidence": {
                "matched_fit_beats_linear_fraction": E["E3"]["matched_fit_beats_linear_fraction"],
                "median_delta_r2": E["E3"]["median_delta_r2"],
            },
        },
        {
            "claim_id": "C3",
            "pass": c3,
            "bounded_claim": "The morphology-based presentation archetype is stable under the tested leave-one-out analysis; it is not provenance evidence.",
            "evidence": {"leave_one_out_archetype_retention_rate": E["E4"]["leave_one_out_archetype_retention_rate"]},
        },
        {
            "claim_id": "C4",
            "pass": c4,
            "bounded_claim": "The recorded clean-host V12 multi-seed benchmark has exact recovery and Top-100 retrieval under its tested nominal configuration.",
            "evidence": e5["summary"],
        },
        {
            "claim_id": "C5",
            "pass": c5,
            "bounded_claim": "Field framing and fits remain descriptive presentation choices, not real provenance or mechanism evidence.",
            "mandatory": True,
        },
        {
            "claim_id": "C6",
            "pass": c6,
            "bounded_claim": "Structural locator robustness is claimed only for the explicit synthetic descriptor v4 model, with its heavy-damage failure boundary visible.",
            "evidence": {
                "baseline": v4_rows["baseline"],
                "deletion_25pct": v4_rows["deletion_25pct"],
                "deletion_50pct": v4_rows["deletion_50pct"],
                "substitution_20pct": v4_rows["substitution_20pct"],
                "combined": v4_rows["deletion_50pct_plus_substitution_20pct"],
            },
        },
    ]

    result = {
        "version": "paper-claim-audit-v7",
        "scope": "synthetic-only",
        "gate_pass": all(x["pass"] for x in claims),
        "claims": claims,
        "never_upgrade": [
            "domain archetype -> real provenance",
            "high R2 -> proven physical mechanism",
            "synthetic locator benchmark -> universal undetectability/security",
            "requested experiment -> completed evidence",
            "descriptor-level v4 canonicalization -> current v3 NPZ parser support",
        ],
    }
    args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Paper claim audit v7",
        "",
        "**SYNTHETIC/MOCK BENCHMARK ONLY.**",
        "",
        f"Gate: **{'PASS' if result['gate_pass'] else 'FAIL'}**",
        "",
        "| claim | status | bounded interpretation |",
        "|---|---|---|",
    ]
    for c in claims:
        lines.append(f"| {c['claim_id']} | {'PASS' if c['pass'] else 'FAIL'} | {c['bounded_claim']} |")
    lines += [
        "",
        "## Mandatory limitation",
        "",
        "Field framing, morphology labels, domain archetypes, and generic fits are descriptive",
        "presentation choices in a synthetic benchmark. They are not evidence of real provenance",
        "or a physical mechanism.",
        "",
        "C6 refers only to the explicit synthetic descriptor v4 model. It does not assert that",
        "the current Protocol-v3 NPZ parser survives actual table deletion or physical split/merge.",
    ]
    args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

    if not result["gate_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
