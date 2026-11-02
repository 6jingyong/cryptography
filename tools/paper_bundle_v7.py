#!/usr/bin/env python3
"""Render a traceable multi-figure synthetic paper bundle from the current E2E bundle.

This is presentation downstream of current machine evidence. It does not alter
or retune the V18/V20 carrier, locator, or reliability layers.

Synthetic/mock benchmark only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

LABEL = "MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS"
SYNTHETIC = "SYNTHETIC BENCHMARK / SIMULATED DATA ONLY"
MANDATORY_LIMITATION = (
    "Field framing, morphology labels, narrative archetypes, and generic fits are "
    "descriptive presentation choices; they are not evidence of real provenance or physical mechanism."
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def r2(y, pred) -> float:
    """Fixed-order R² for paper-plan numbers.

    The inputs are already float64 arrays from the current package. Convert to
    Python floats and use math.fsum so the paper-side comparison does not depend
    on BLAS/vector-reduction order across independent CI runners.
    """
    ys = [float(v) for v in np.asarray(y, float).reshape(-1)]
    ps = [float(v) for v in np.asarray(pred, float).reshape(-1)]
    if len(ys) != len(ps) or not ys:
        raise ValueError("r2 requires non-empty equal-length inputs")
    mean_y = math.fsum(ys) / len(ys)
    ss = math.fsum((a - b) * (a - b) for a, b in zip(ys, ps))
    den = math.fsum((a - mean_y) * (a - mean_y) for a in ys) + 1e-12
    return 1.0 - ss / den


def deterministic_linear_r2(x, y) -> float:
    """Analytic one-variable linear-regression R² with fixed scalar reductions."""
    xs = [float(v) for v in np.asarray(x, float).reshape(-1)]
    ys = [float(v) for v in np.asarray(y, float).reshape(-1)]
    if len(xs) != len(ys) or not xs:
        raise ValueError("linear fit requires non-empty equal-length inputs")
    mean_x = math.fsum(xs) / len(xs)
    mean_y = math.fsum(ys) / len(ys)
    sxx = math.fsum((v - mean_x) * (v - mean_x) for v in xs)
    if sxx <= 0.0:
        pred = [mean_y] * len(xs)
    else:
        sxy = math.fsum((a - mean_x) * (b - mean_y) for a, b in zip(xs, ys))
        slope = sxy / sxx
        intercept = mean_y - slope * mean_x
        pred = [intercept + slope * v for v in xs]
    return r2(ys, pred)


def visible_curves(package_path: Path, manifest_path: Path):
    B = load_json(manifest_path)
    z = np.load(package_path)
    curves = {}
    for table in sorted(B["tables"], key=lambda x: int(x["table_id"])):
        tid = int(table["table_id"])
        n = int(table["points_per_block"])
        x = np.asarray(z[f"table_{tid}_x"], float)[:n]
        y = np.asarray(z[f"table_{tid}_y"], float)[:n]
        if y.ndim == 1:
            y = y[:, None]
        curves[tid] = {"x": x, "y": y, "table": table}
    return B, curves


def save_svg(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_overview(curves, fit_rows_by_id, path: Path):
    ids = sorted(curves)
    cols = 4
    rows = int(math.ceil(len(ids) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(13, 2.8 * rows), squeeze=False)
    for ax, tid in zip(axes.flat, ids):
        c = curves[tid]
        row = fit_rows_by_id[tid]
        ax.plot(c["x"], c["y"][:, 0], marker="o", markersize=2.6, linewidth=1.2)
        ax.set_title(f"Table {tid} · {row['morphology']}", fontsize=9)
        ax.set_xlabel("synthetic x")
        ax.set_ylabel("synthetic response")
        ax.grid(alpha=0.2)
    for ax in axes.flat[len(ids):]:
        ax.axis("off")
    fig.suptitle("Synthetic response overview — current V20 package", fontsize=14)
    save_svg(fig, path)


def select_representatives(fit_rows):
    selected = {}
    for row in fit_rows:
        m = row["morphology"]
        if m == "other":
            continue
        current = selected.get(m)
        key = (float(row["confidence"]), -int(row["table_id"]))
        if current is None:
            selected[m] = row
        else:
            old_key = (float(current["confidence"]), -int(current["table_id"]))
            if key > old_key:
                selected[m] = row
    return {m: int(row["table_id"]) for m, row in sorted(selected.items())}


def plot_morphology_examples(curves, fit_rows_by_id, selected, path: Path):
    items = list(selected.items())
    cols = 2
    rows = int(math.ceil(len(items) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(10, 3.7 * rows), squeeze=False)
    for ax, (m, tid) in zip(axes.flat, items):
        c = curves[tid]
        meta = fit_rows_by_id[tid]
        ax.plot(c["x"], c["y"][:, 0], marker="o", markersize=3.0, linewidth=1.4)
        ax.set_title(
            f"{m} · table {tid}\nconfidence={float(meta['confidence']):.3f}, descriptive R²={float(meta['fit_r2']):.4f}",
            fontsize=10,
        )
        ax.set_xlabel("synthetic x")
        ax.set_ylabel("synthetic response")
        ax.grid(alpha=0.2)
    for ax in axes.flat[len(items):]:
        ax.axis("off")
    fig.suptitle("Morphology-selected synthetic examples", fontsize=14)
    save_svg(fig, path)


def fit_ablation(curves, fit_rows):
    rows = []
    for row in fit_rows:
        if row["morphology"] in ("linear", "other"):
            continue
        tid = int(row["table_id"])
        x = curves[tid]["x"]
        y = curves[tid]["y"][:, 0]
        linear = deterministic_linear_r2(x, y)
        rows.append({
            "table_id": tid,
            "morphology": row["morphology"],
            "matched_fit_r2": float(row["fit_r2"]),
            "linear_baseline_r2": float(linear),
            "delta_r2": float(row["fit_r2"] - linear),
        })
    return rows


def plot_fit_ablation(rows, path: Path):
    ids = [r["table_id"] for r in rows]
    matched = [r["matched_fit_r2"] for r in rows]
    linear = [r["linear_baseline_r2"] for r in rows]
    x = np.arange(len(ids))
    w = 0.38
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(x - w/2, matched, width=w, label="morphology-matched descriptive fit")
    ax.bar(x + w/2, linear, width=w, label="linear baseline")
    ax.set_xticks(x, [str(i) for i in ids])
    ax.set_xlabel("table id")
    ax.set_ylabel("R²")
    ax.set_ylim(min(-0.05, min(linear + matched) - 0.05), 1.03)
    ax.set_title("Descriptive fit ablation on current synthetic curves")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    save_svg(fig, path)


def plot_e5_control(e5, path: Path):
    runs = e5["runs"]
    seeds = [int(r["seed"]) for r in runs]
    ranks = [int(r["target_rank"]) for r in runs]
    exact = [1 if r["exact_recovery"] else 0 for r in runs]
    x = np.arange(len(seeds))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].bar(x, ranks)
    axes[0].set_xticks(x, [str(s) for s in seeds], rotation=45)
    axes[0].set_ylabel("target rank")
    axes[0].set_title("A-layer locator rank")
    axes[0].set_ylim(0, max(2, max(ranks) + 1))
    axes[0].grid(axis="y", alpha=0.2)

    axes[1].bar(x, exact)
    axes[1].set_xticks(x, [str(s) for s in seeds], rotation=45)
    axes[1].set_ylabel("exact recovery")
    axes[1].set_yticks([0, 1])
    axes[1].set_ylim(0, 1.1)
    axes[1].set_title("Current V20 exact recovery")
    axes[1].grid(axis="y", alpha=0.2)
    fig.suptitle("Current technical control — same result used for paper E5", fontsize=14)
    save_svg(fig, path)


def export_data(curves, data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for tid in sorted(curves):
        c = curves[tid]
        data = {"x": c["x"]}
        for ch in range(c["y"].shape[1]):
            data[f"channel_{ch}"] = c["y"][:, ch]
        out = data_dir / f"table_{tid:02d}.csv"
        pd.DataFrame(data).to_csv(out, index=False)
        entries.append({
            "table_id": tid,
            "path": f"data/{out.name}",
            "rows": int(len(c["x"])),
            "channels": int(c["y"].shape[1]),
            "sha256": sha256_file(out),
        })
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-bundle", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    base = args.base_bundle
    out = args.out_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    fig_dir = out / "figures"
    data_dir = out / "data"
    fig_dir.mkdir()

    integration = load_json(base / "integration_result.json")
    if integration.get("gate_pass") is not True:
        raise SystemExit("current end-to-end base bundle did not pass")

    package = base / "published_v20.npz"
    manifest = base / "manifest_v20.json"
    e5_path = base / "e5_current_v20.json"
    summary_path = base / "technical_summary.json"
    paper6 = base / "paper_v6_output"
    fit_path = paper6 / "fit_results.json"
    domain_path = paper6 / "domain_archetype.json"
    story_path = paper6 / "story_plan.json"
    claims_path = paper6 / "claim_evidence_map.json"
    experiments_path = paper6 / "experiment_results_v6.json"
    paper6_manifest_path = paper6 / "paper_manifest.json"

    B, curves = visible_curves(package, manifest)
    fit_rows = load_json(fit_path)
    fit_rows_by_id = {int(r["table_id"]): r for r in fit_rows}
    domain = load_json(domain_path)
    story = load_json(story_path)
    claims = {c["claim_id"]: c for c in load_json(claims_path)}
    e5 = load_json(e5_path)
    tech = load_json(summary_path)
    experiments = load_json(experiments_path)
    paper6_manifest = load_json(paper6_manifest_path)

    paper_e5 = next(x for x in experiments["results"] if x["experiment_id"] == "E5")
    if not paper6_manifest.get("e5_completed") or paper_e5.get("pass") is not True:
        raise SystemExit("paper-v6 E5 is not a completed passing current result")
    if paper_e5.get("machine_result") != e5.get("summary"):
        raise SystemExit("paper-v6 E5 does not equal the current E5 machine summary")

    npz_sha = sha256_file(package)
    manifest_sha = sha256_file(manifest)
    e5_sha = sha256_file(e5_path)
    fit_sha = sha256_file(fit_path)

    data_entries = export_data(curves, data_dir)
    data_manifest = {
        "version": "paper-v7-data-manifest-v1",
        "scope": "synthetic-only",
        "source_npz_sha256": npz_sha,
        "source_manifest_sha256": manifest_sha,
        "tables": data_entries,
    }
    (out / "data_manifest.json").write_text(json.dumps(data_manifest, indent=2), encoding="utf-8")

    selected = select_representatives(fit_rows)
    ablation_rows = fit_ablation(curves, fit_rows)

    figure_plan = {
        "version": "paper-v7-figure-plan-v1",
        "scope": "synthetic-only",
        "source_npz_sha256": npz_sha,
        "figures": [
            {"figure_id": "F1", "path": "figures/fig1_overview.svg", "role": "response_breadth", "table_ids": sorted(curves), "claim_ids": ["C1"]},
            {"figure_id": "F2", "path": "figures/fig2_morphology_examples.svg", "role": "morphology_examples", "selected_by": "highest confidence within each non-other morphology; tie -> lowest table id", "selected": selected, "claim_ids": ["C1"]},
            {"figure_id": "F3", "path": "figures/fig3_fit_ablation.svg", "role": "descriptive_fit_ablation", "rows": ablation_rows, "claim_ids": ["C2"]},
            {"figure_id": "F4", "path": "figures/fig4_e5_control.svg", "role": "current_technical_control", "e5_summary": e5["summary"], "claim_ids": ["C4"]},
        ],
    }
    (out / "figure_plan.json").write_text(json.dumps(figure_plan, indent=2), encoding="utf-8")

    plot_overview(curves, fit_rows_by_id, fig_dir / "fig1_overview.svg")
    plot_morphology_examples(curves, fit_rows_by_id, selected, fig_dir / "fig2_morphology_examples.svg")
    plot_fit_ablation(ablation_rows, fig_dir / "fig3_fit_ablation.svg")
    plot_e5_control(e5, fig_dir / "fig4_e5_control.svg")

    captions = {
        "F1": "Synthetic figure. Overview of all visible response curves from the representative current V20 package; morphology labels are descriptive presentation metadata.",
        "F2": "Synthetic figure. One automatically selected high-confidence example per available morphology class; selection is rule-based and does not imply real provenance.",
        "F3": "Synthetic figure. Morphology-matched descriptive fit R² versus a linear baseline for non-linear synthetic curves; fit quality is not mechanism proof.",
        "F4": "Synthetic figure. Current-V20 technical control using the same seeds and machine result that complete paper E5: locator rank and exact recovery.",
    }
    source_map = {
        "F1": {"npz": npz_sha, "manifest": manifest_sha, "fit_results": fit_sha},
        "F2": {"npz": npz_sha, "manifest": manifest_sha, "fit_results": fit_sha},
        "F3": {"npz": npz_sha, "manifest": manifest_sha, "fit_results": fit_sha},
        "F4": {"e5_current_v20": e5_sha},
    }
    figure_entries = []
    for fig in figure_plan["figures"]:
        p = out / fig["path"]
        if not p.exists() or p.stat().st_size < 1000:
            raise SystemExit(f"missing/empty figure: {p}")
        figure_entries.append({
            "figure_id": fig["figure_id"],
            "path": fig["path"],
            "sha256": sha256_file(p),
            "bytes": p.stat().st_size,
            "source_hashes": source_map[fig["figure_id"]],
            "claim_ids": fig["claim_ids"],
            "caption": captions[fig["figure_id"]],
        })
    figure_manifest = {
        "version": "paper-v7-figure-manifest-v1",
        "scope": "synthetic-only",
        "label": LABEL,
        "figures": figure_entries,
    }
    (out / "figure_manifest.json").write_text(json.dumps(figure_manifest, indent=2), encoding="utf-8")

    required_claims = ["C1", "C2", "C4", "C5"]
    for cid in required_claims:
        if cid not in claims:
            raise SystemExit(f"required paper-v6 claim missing: {cid}")

    traceability = {
        "version": "paper-v7-traceability-v1",
        "scope": "synthetic-only",
        "source_current_bundle": {
            "published_npz_sha256": npz_sha,
            "manifest_sha256": manifest_sha,
            "e5_sha256": e5_sha,
            "fit_results_sha256": fit_sha,
        },
        "claims": {
            "C1": {
                "claim": claims["C1"]["claim"],
                "role": claims["C1"]["role"],
                "figures": ["F1", "F2"],
                "data_tables": [e["table_id"] for e in data_entries],
                "evidence": ["paper_v6_output/fit_results.json", "data_manifest.json"],
            },
            "C2": {
                "claim": claims["C2"]["claim"],
                "role": claims["C2"]["role"],
                "figures": ["F3"],
                "data_tables": [r["table_id"] for r in ablation_rows],
                "evidence": ["paper_v6_output/fit_results.json", "figure_plan.json"],
            },
            "C4": {
                "claim": claims["C4"]["claim"],
                "role": claims["C4"]["role"],
                "figures": ["F4"],
                "machine_result": e5["summary"],
                "evidence": ["e5_current_v20.json", "technical_summary.json"],
            },
            "C5": {
                "claim": claims["C5"]["claim"],
                "role": claims["C5"]["role"],
                "figures": [],
                "evidence": ["paper_v7.md", "paper_v7_manifest.json"],
            },
        },
    }
    (out / "traceability.json").write_text(json.dumps(traceability, indent=2), encoding="utf-8")

    archetype = domain["selected_archetype"]["display_name"]
    story_type = story["story_type"]
    morph_counts = domain["morphology_counts"]
    fit_median = float(np.median([float(r["fit_r2"]) for r in fit_rows]))
    e5s = e5["summary"]

    paper = f"""# {LABEL}

# Synthetic Multi-Figure Response Characterization — Paper Bundle v7

**{SYNTHETIC}**

**Presentation archetype:** {archetype}  
**Important:** this archetype is selected from synthetic curve morphology for presentation only; it is not provenance inference.

## Abstract

This mock paper renders the same representative current-V20 numeric package used by the current end-to-end benchmark. The presentation planner selected the `{story_type}` story from visible synthetic response morphology. The package contains {tech['payload_bytes']} synthetic payload bytes. Current technical control uses {e5s['seed_count']} fresh payload seeds with exact recovery rate {e5s['exact_recovery_rate']:.3f}, Recall@100 {e5s['recall_at_100']:.3f}, and {str(e5s['all_payload_hashes_unique']).lower()} unique-payload-hash status. All scientific-looking figures and tables in this bundle are synthetic benchmark artifacts.

## 1. Response-regime breadth

The representative package contains the following morphology counts: `{morph_counts}`.

![Figure 1](figures/fig1_overview.svg)

**Figure 1.** {captions['F1']}

![Figure 2](figures/fig2_morphology_examples.svg)

**Figure 2.** {captions['F2']}

The bounded presentation claim is: **{claims['C1']['claim']}**

## 2. Descriptive quantification

Median morphology-matched descriptive-fit R² across current visible curves is **{fit_median:.4f}**.

![Figure 3](figures/fig3_fit_ablation.svg)

**Figure 3.** {captions['F3']}

The bounded quantification claim is: **{claims['C2']['claim']}**

## 3. Current technical control

![Figure 4](figures/fig4_e5_control.svg)

**Figure 4.** {captions['F4']}

Current E5 machine result:

```text
seeds                 {e5s['seed_count']}
exact recovery rate   {e5s['exact_recovery_rate']:.3f}
Recall@20             {e5s['recall_at_20']:.3f}
Recall@100            {e5s['recall_at_100']:.3f}
median target rank    {e5s['median_target_rank']}
max target rank       {e5s['max_target_rank']}
all payload hashes unique  {e5s['all_payload_hashes_unique']}
```

The bounded technical-control claim is: **{claims['C4']['claim']}**

## 4. Synthetic raw-data package and traceability

The visible response data used for Figures 1–3 are exported as one CSV per current table under [`data/`](data/). Hashes and source table IDs are recorded in [`data_manifest.json`](data_manifest.json).

Figure hashes, source hashes, captions, and claim bindings are recorded in [`figure_manifest.json`](figure_manifest.json). Claim-to-figure/data/machine mappings are recorded in [`traceability.json`](traceability.json).

The representative machine package itself is not re-generated for presentation: this bundle consumes the current end-to-end `published_v20.npz`, `manifest_v20.json`, `technical_summary.json`, and `e5_current_v20.json`.

## 5. Mandatory limitation

{MANDATORY_LIMITATION}

This artifact does not establish real experimental evidence, real provenance, a physical mechanism, real-publication deployment, undetectability, or cryptographic security of the numeric carrier.

**{LABEL}**  
**{SYNTHETIC}**
"""
    (out / "paper_v7.md").write_text(paper, encoding="utf-8")

    # Recompute all data/figure hashes from disk as a local gate.
    for entry in data_entries:
        if sha256_file(out / entry["path"]) != entry["sha256"]:
            raise SystemExit(f"data hash mismatch: {entry['path']}")
    for entry in figure_entries:
        if sha256_file(out / entry["path"]) != entry["sha256"]:
            raise SystemExit(f"figure hash mismatch: {entry['path']}")

    paper_text = (out / "paper_v7.md").read_text(encoding="utf-8")
    if LABEL not in paper_text or SYNTHETIC not in paper_text:
        raise SystemExit("required synthetic/mock labels missing")
    if MANDATORY_LIMITATION not in paper_text:
        raise SystemExit("mandatory limitation missing")
    for fig in ["fig1_overview.svg", "fig2_morphology_examples.svg", "fig3_fit_ablation.svg", "fig4_e5_control.svg"]:
        if fig not in paper_text:
            raise SystemExit(f"paper does not embed {fig}")
    if len(data_entries) != len(B["tables"]):
        raise SystemExit("raw-data export count does not match current table count")
    if set(traceability["claims"]) != set(required_claims):
        raise SystemExit("claim traceability set mismatch")

    output_files = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "paper_v7_manifest.json"):
        output_files.append({
            "path": path.relative_to(out).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    manifest_v7 = {
        "version": "paper-v7-manifest-v1",
        "scope": "synthetic-only",
        "label": LABEL,
        "source_current_npz_sha256": npz_sha,
        "source_current_manifest_sha256": manifest_sha,
        "source_current_e5_sha256": e5_sha,
        "presentation_archetype": archetype,
        "story_type": story_type,
        "figure_count": len(figure_entries),
        "raw_data_table_count": len(data_entries),
        "required_claims_traced": required_claims,
        "current_e5_equal_to_paper_v6_e5": True,
        "gate_pass": True,
        "files": output_files,
    }
    (out / "paper_v7_manifest.json").write_text(json.dumps(manifest_v7, indent=2), encoding="utf-8")

    result = {
        "version": "paper-bundle-v7-result-v1",
        "scope": "synthetic-only",
        "gate_pass": True,
        "figure_count": len(figure_entries),
        "raw_data_table_count": len(data_entries),
        "selected_morphology_examples": selected,
        "nonlinear_fit_ablation_tables": len(ablation_rows),
        "current_e5": e5s,
        "presentation_archetype": archetype,
        "story_type": story_type,
        "source_npz_sha256": npz_sha,
        "paper_v6_e5_matches_current_e5": True,
        "required_claims_traced": required_claims,
        "synthetic_labels_present": True,
        "mandatory_limitation_present": True,
    }
    (out / "validation_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
