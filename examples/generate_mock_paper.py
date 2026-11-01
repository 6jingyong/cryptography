#!/usr/bin/env python3
"""Generate a clearly labeled synthetic/mock paper benchmark package."""

from __future__ import annotations
import argparse, csv, json, runpy, shutil
from pathlib import Path

LABEL = "MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS"


def svg_schedule(manifest):
    bars = []
    for i, t in enumerate(manifest["tables"]):
        q = int(t["q"])
        x = 45 + i * 68
        h = {8:55, 16:90, 32:125}.get(q, 70)
        bars.append(
            f'<rect x="{x}" y="{250-h}" width="58" height="{h}" fill="none" stroke="black"/>'
            f'<text x="{x+29}" y="280" text-anchor="middle" font-size="11">T{i+1}</text>'
            f'<text x="{x+29}" y="{242-h}" text-anchor="middle" font-size="11">q={q}</text>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="340">'
        '<rect width="100%" height="100%" fill="white"/>'
        '<text x="45" y="28" font-size="18">SYNTHETIC BENCHMARK — adaptive-q schedule</text>'
        + "".join(bars)
        + f'<text x="45" y="325" font-size="11">{LABEL}</text></svg>'
    )


def svg_locator(locator):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="260">
<rect width="100%" height="100%" fill="white"/>
<text x="40" y="28" font-size="18">SYNTHETIC BENCHMARK — FIND then VERIFY</text>
<text x="60" y="115" font-size="16">{locator['candidate_count']} mock candidates</text>
<text x="300" y="115" font-size="30">→</text>
<text x="360" y="100" font-size="16">locator</text>
<text x="360" y="125" font-size="14">target rank = {locator['target_rank']}</text>
<text x="525" y="115" font-size="30">→</text>
<text x="590" y="100" font-size="16">strict verifier</text>
<text x="590" y="125" font-size="14">decoy REJECT / target ACCEPT</text>
<text x="40" y="240" font-size="11">{LABEL}</text>
</svg>"""


def write_samples(manifest, loaded, data_dir):
    for family in ("periodic", "gaussian"):
        t = next(x for x in manifest["tables"] if x["family"] == family)
        tid, n = int(t["table_id"]), int(t["points_per_block"])
        x, y = loaded[f"table_{tid}_x"], loaded[f"table_{tid}_y"]
        with (data_dir / f"{family}_table_sample.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["SYNTHETIC_BENCHMARK","table_id","x_index","x","y_ch0","y_ch1","y_ch2","y_ch3"])
            for i in range(n):
                w.writerow(["SIMULATED_DATA",tid,i,f"{x[i]:.8f}",*[f"{y[i,c]:.8f}" for c in range(min(4,y.shape[1]))]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("examples/mock-paper-config.json"))
    ap.add_argument("--out-dir", type=Path, default=Path("mock_paper_output"))
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    cfg_path = args.config if args.config.is_absolute() else root / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    label = cfg.get("label", LABEL)
    if "MOCK" not in label and "SYNTHETIC" not in label:
        raise ValueError("Visible mock/synthetic label may not be removed.")

    out = args.out_dir if args.out_dir.is_absolute() else root / args.out_dir
    if out.exists(): shutil.rmtree(out)
    (out / "figures").mkdir(parents=True)
    (out / "data").mkdir(parents=True)

    demo = runpy.run_path(str(root / "demo.py"))
    engine = demo["load_engine"](root, quick=False)
    result = engine["run_package"](
        payload_bytes=int(cfg.get("payload_bytes", 8192)),
        channels=int(cfg.get("channels_per_table", 8)),
        out_dir=out / "carrier",
    )

    mp = out / "carrier" / "manifest_adaptive_q_v12.json"
    pp = out / "carrier" / "published_adaptive_q_v12.npz"
    manifest, loaded, decoded_sha = demo["decode_published_package"](engine, pp, mp)
    exact = decoded_sha == manifest["payload_sha256"]

    fp, _ = demo["make_locator_fingerprint"](manifest)
    lc = cfg.get("locator", {})
    locator = demo["locator_demo"](
        fp,
        candidates=int(lc.get("candidate_count", 1000)),
        target_noise=int(lc.get("target_substitutions", 1))/max(1,len(fp)),
        near_decoys=int(lc.get("near_decoys", 20)),
        near_shared_fraction=float(lc.get("shared_structure_fraction", 0.5)),
    )
    locator["candidate_count"] = int(lc.get("candidate_count", 1000))
    target_ok, decoy_ok = demo["strict_verifier_demo"](
        manifest["payload_sha256"], locator["target_id"], locator["best_decoy_id"]
    )

    figure1 = out/"figures"/"figure_1_periodic_before_after.svg"
    demo["write_curve_svg"](engine, manifest, loaded, figure1)
    svg1 = figure1.read_text(encoding="utf-8")
    if label not in svg1:
        svg1 = svg1.replace(
            "</svg>",
            f'<text x="55" y="405" font-size="11">{label}</text></svg>',
        )
        figure1.write_text(svg1, encoding="utf-8")
    (out/"figures"/"figure_2_adaptive_q_schedule.svg").write_text(svg_schedule(manifest), encoding="utf-8")
    (out/"figures"/"figure_3_locator_verifier.svg").write_text(svg_locator(locator), encoding="utf-8")
    write_samples(manifest, loaded, out/"data")

    readable = {
        "label": label,
        "payload_bytes": manifest["payload_bytes"],
        "payload_sha256": manifest["payload_sha256"],
        "decoded_sha256": decoded_sha,
        "exact_recovery": exact,
        "published_rows": result["published_rows_total"],
        "gross_bits_per_numeric_value": result["gross_bits_per_numeric_value"],
        "q_distribution": result["q_distribution"],
        "locator": {
            "candidate_count": locator["candidate_count"],
            "target_rank": locator["target_rank"],
            "target_similarity": locator["target_score"],
            "best_decoy_similarity": locator["best_decoy_score"],
        },
        "strict_verification": {
            "best_decoy": "ACCEPT" if decoy_ok else "REJECT",
            "target": "ACCEPT" if target_ok else "REJECT",
        },
        "tables": [
            {"table_id":t["table_id"],"family":t["family"],"q":t["q"],"transform":t["transform"]}
            for t in manifest["tables"]
        ],
    }
    (out/"manifest_readable.json").write_text(json.dumps(readable, indent=2), encoding="utf-8")
    (out/"verification.json").write_text(json.dumps({
        "label":"SYNTHETIC BENCHMARK",
        "exact_payload_recovery":exact,
        "payload_sha256":manifest["payload_sha256"],
        "decoded_sha256":decoded_sha,
        "locator_target_rank":locator["target_rank"],
        "best_decoy_verification":"ACCEPT" if decoy_ok else "REJECT",
        "target_verification":"ACCEPT" if target_ok else "REJECT",
    }, indent=2), encoding="utf-8")

    rows = "\n".join(
        f'| {int(t["table_id"])+1} | {t["family"]} | {int(t["q"])} | {t["transform"]} |'
        for t in manifest["tables"]
    )
    paper = f"""# {label}

## Adaptive-Q Numeric Carrier in a Synthetic Multi-Table Package

**SYNTHETIC BENCHMARK / SIMULATED DATA ONLY**

A {manifest["payload_bytes"]:,}-byte deterministic synthetic payload was encoded
into 12 synthetic numeric tables and independently decoded from the published
package plus manifest. SHA-256 exact recovery: **{str(exact).upper()}**.

```text
WRITE   synthetic payload -> numeric carrier
FIND    structural fingerprint -> candidate ranking
VERIFY  strict integrity -> accept / reject
```

| table | family | q | transform |
|---:|---|---:|---|
{rows}

![baseline vs published](figures/figure_1_periodic_before_after.svg)

![adaptive q](figures/figure_2_adaptive_q_schedule.svg)

![locator and verifier](figures/figure_3_locator_verifier.svg)

- candidates: **{locator["candidate_count"]:,}**
- target rank: **{locator["target_rank"]}**
- best decoy: **{"ACCEPT" if decoy_ok else "REJECT"}**
- true target: **{"ACCEPT" if target_ok else "REJECT"}**
- gross bit/value: **{result["gross_bits_per_numeric_value"]:.3f}**
- payload SHA-256: `{manifest["payload_sha256"]}`
- decoded SHA-256: `{decoded_sha}`

All data and results are synthetic. This is not real experimental evidence.

**{label}**
"""
    (out/"paper.md").write_text(paper, encoding="utf-8")
    (out/"README.md").write_text(
        f"# Synthetic Paper Benchmark — generated example\n\n**{label}**\n\n"
        f"Start with `paper.md`.\n\n"
        f"- exact recovery: {exact}\n"
        f"- target rank: {locator['target_rank']}/{locator['candidate_count']}\n"
        f"- best decoy: {'ACCEPT' if decoy_ok else 'REJECT'}\n"
        f"- target: {'ACCEPT' if target_ok else 'REJECT'}\n",
        encoding="utf-8",
    )

    print(f"Generated: {out}")
    print(f"Exact recovery: {exact}")
    print(f"Locator target rank: {locator['target_rank']}/{locator['candidate_count']}")
    print(f"Best decoy: {'ACCEPT' if decoy_ok else 'REJECT'}")
    print(f"Target: {'ACCEPT' if target_ok else 'REJECT'}")
    if not exact or decoy_ok or not target_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
