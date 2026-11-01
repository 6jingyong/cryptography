#!/usr/bin/env python3
"""
One-command synthetic demo for the dual-codebook pipeline.

What it demonstrates:
1. generate an internal synthetic payload;
2. encode it into an adaptive-q multi-table numeric package;
3. build a structural locator fingerprint from (family, q);
4. rank the true package among synthetic candidates;
5. reject a plausible decoy with a strict verifier;
6. independently decode the published package + manifest;
7. verify SHA-256 equality;
8. write a tiny before/after SVG for one periodic table.

The demo never accepts an arbitrary payload file. It is intentionally
synthetic-only and pedagogical.

Quick mode reduces calibration blocks so the example runs faster. The benchmark
scripts keep the larger calibration used for reported results.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import runpy
import shutil
from pathlib import Path

import numpy as np


def load_engine(repo_root: Path, quick: bool):
    engine_path = repo_root / "src" / "adaptive_q_package_v12.py"
    if not engine_path.exists():
        raise FileNotFoundError(
            f"Could not find {engine_path}. Run demo.py from the repository."
        )

    ns = runpy.run_path(str(engine_path))

    if quick:
        original_calibrate = ns["calibrate"]

        def quick_calibrate(family, q, budget, channels, blocks=256):
            return original_calibrate(
                family, q, budget, channels, blocks=blocks
            )

        # Functions created by runpy share this globals dictionary.
        ns["calibrate"] = quick_calibrate

    return ns


def decode_published_package(ns, package_path: Path, manifest_path: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    loaded = np.load(package_path)

    recovered_bits = np.zeros(
        int(manifest["payload_bit_length"]), dtype=np.uint8
    )

    for table in manifest["tables"]:
        table_id = int(table["table_id"])
        bits = ns["decode_table"](
            loaded[f"table_{table_id}_y"], table
        )
        offset = int(table["payload_bit_offset"])
        recovered_bits[offset:offset + len(bits)] = bits

    recovered = ns["bits_to_bytes"](recovered_bits)[
        : int(manifest["payload_bytes"])
    ]
    decoded_sha = hashlib.sha256(recovered).hexdigest()
    return manifest, loaded, decoded_sha


def make_locator_fingerprint(manifest):
    families = sorted({t["family"] for t in manifest["tables"]})
    qs = sorted({int(t["q"]) for t in manifest["tables"]})
    vocab = [(family, q) for family in families for q in qs]
    to_id = {value: idx for idx, value in enumerate(vocab)}

    fingerprint = np.asarray(
        [
            to_id[(table["family"], int(table["q"]))]
            for table in manifest["tables"]
        ],
        dtype=np.int16,
    )
    return fingerprint, vocab


def corrupt_signature(signature, rate, alphabet, rng):
    out = signature.copy()
    mask = rng.random(len(out)) < rate
    for i in np.where(mask)[0]:
        choices = np.arange(alphabet, dtype=np.int16)
        choices = choices[choices != out[i]]
        out[i] = rng.choice(choices)
    return out


def make_near_decoy(signature, shared_fraction, alphabet, rng):
    out = rng.integers(
        0, alphabet, size=len(signature), dtype=np.int16
    )
    k = int(round(shared_fraction * len(signature)))
    if k:
        idx = rng.choice(len(signature), size=k, replace=False)
        out[idx] = signature[idx]
    return out


def locator_demo(
    fingerprint,
    candidates=1000,
    target_noise=0.10,
    near_decoys=25,
    near_shared_fraction=0.50,
):
    rng = np.random.default_rng(20261101)
    alphabet = int(np.max(fingerprint)) + 1

    target_id = int(rng.integers(0, candidates))
    descriptors = rng.integers(
        0,
        alphabet,
        size=(candidates, len(fingerprint)),
        dtype=np.int16,
    )

    possible_decoys = np.asarray(
        [i for i in range(candidates) if i != target_id],
        dtype=int,
    )
    near_ids = rng.choice(
        possible_decoys,
        size=min(near_decoys, len(possible_decoys)),
        replace=False,
    )
    for candidate_id in near_ids:
        descriptors[candidate_id] = make_near_decoy(
            fingerprint,
            near_shared_fraction,
            alphabet,
            rng,
        )

    descriptors[target_id] = corrupt_signature(
        fingerprint, target_noise, alphabet, rng
    )

    scores = np.mean(
        descriptors == fingerprint[None, :],
        axis=1,
    )
    order = np.argsort(-scores, kind="stable")
    target_rank = int(np.where(order == target_id)[0][0] + 1)

    best_decoy_id = int(next(i for i in order if i != target_id))
    return {
        "target_id": target_id,
        "target_rank": target_rank,
        "target_score": float(scores[target_id]),
        "best_decoy_id": best_decoy_id,
        "best_decoy_score": float(scores[best_decoy_id]),
        "top5_ids": [int(i) for i in order[:5]],
        "top5_scores": [float(scores[i]) for i in order[:5]],
    }


def strict_verifier_demo(payload_sha_hex, target_id, decoy_id):
    key = hashlib.sha256(b"synthetic-demo-verifier-key").digest()
    target_hash = bytes.fromhex(payload_sha_hex)

    target_tag = hmac.new(
        key, target_hash + target_id.to_bytes(8, "big"), hashlib.sha256
    ).digest()

    decoy_hash = hashlib.sha256(
        f"synthetic-decoy-{decoy_id}".encode()
    ).digest()
    wrong_key = hashlib.sha256(b"wrong-demo-key").digest()
    decoy_tag = hmac.new(
        wrong_key,
        decoy_hash + decoy_id.to_bytes(8, "big"),
        hashlib.sha256,
    ).digest()

    target_ok = hmac.compare_digest(
        target_tag,
        hmac.new(
            key,
            target_hash + target_id.to_bytes(8, "big"),
            hashlib.sha256,
        ).digest(),
    )
    decoy_ok = hmac.compare_digest(
        decoy_tag,
        hmac.new(
            key,
            decoy_hash + decoy_id.to_bytes(8, "big"),
            hashlib.sha256,
        ).digest(),
    )
    return target_ok, decoy_ok


def svg_polyline(points, width, height, pad, x_min, x_max, y_min, y_max):
    def sx(x):
        return pad + (x - x_min) / (x_max - x_min) * (width - 2 * pad)

    def sy(y):
        return height - pad - (y - y_min) / (y_max - y_min) * (
            height - 2 * pad
        )

    return " ".join(
        f"{sx(float(x)):.2f},{sy(float(y)):.2f}"
        for x, y in points
    )


def write_curve_svg(ns, manifest, loaded, out_path: Path):
    periodic = next(
        table
        for table in manifest["tables"]
        if table["family"] == "periodic"
    )

    table_id = int(periodic["table_id"])
    q = int(periodic["q"])
    channels = int(periodic["channels"])
    n = int(periodic["points_per_block"])

    x = loaded[f"table_{table_id}_x"]
    encoded = loaded[f"table_{table_id}_y"][:n, 0]

    spec = ns["family_spec"]("periodic")
    baseline = ns["baseline"](spec, q, 0, channels)[4]

    width = 860
    height = 420
    pad = 50
    x_min, x_max = float(np.min(x)), float(np.max(x))
    y_min = float(min(np.min(baseline), np.min(encoded)))
    y_max = float(max(np.max(baseline), np.max(encoded)))
    span = max(y_max - y_min, 1e-12)
    y_min -= 0.08 * span
    y_max += 0.08 * span

    before_points = svg_polyline(
        zip(x, baseline),
        width, height, pad,
        x_min, x_max, y_min, y_max,
    )
    after_points = svg_polyline(
        zip(x, encoded),
        width, height, pad,
        x_min, x_max, y_min, y_max,
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}"
      stroke="#555" stroke-width="1"/>
<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height-pad}"
      stroke="#555" stroke-width="1"/>
<text x="{pad}" y="28" font-family="sans-serif" font-size="18">
Synthetic periodic table: baseline vs published carrier
</text>
<polyline points="{before_points}" fill="none"
          stroke="#1f77b4" stroke-width="3"/>
<polyline points="{after_points}" fill="none"
          stroke="#d62728" stroke-width="2" stroke-dasharray="7 5"/>
<line x1="{width-260}" y1="28" x2="{width-225}" y2="28"
      stroke="#1f77b4" stroke-width="3"/>
<text x="{width-215}" y="33" font-family="sans-serif" font-size="13">
baseline
</text>
<line x1="{width-145}" y1="28" x2="{width-110}" y2="28"
      stroke="#d62728" stroke-width="2" stroke-dasharray="7 5"/>
<text x="{width-100}" y="33" font-family="sans-serif" font-size="13">
published
</text>
<text x="{width/2-40}" y="{height-12}" font-family="sans-serif"
      font-size="13">x</text>
<text x="12" y="{height/2}" font-family="sans-serif"
      font-size="13">y</text>
</svg>
"""
    out_path.write_text(svg, encoding="utf-8")
    return {
        "table_id": table_id,
        "family": "periodic",
        "q": q,
        "channel": 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run the synthetic dual-codebook quick demo."
    )
    parser.add_argument(
        "--payload-bytes",
        type=int,
        default=4096,
        help="Internal synthetic payload size. Default: 4096.",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=8,
        help="Synthetic y-series per table. Default: 8.",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=1000,
        help="Synthetic locator corpus size. Default: 1000.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("demo_output"),
        help="Output directory. Default: demo_output.",
    )
    parser.add_argument(
        "--full-calibration",
        action="store_true",
        help="Use benchmark-size calibration instead of quick demo calibration.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    out_dir = (repo_root / args.out_dir).resolve()

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    print("[1/6] Loading the adaptive-q synthetic engine")
    ns = load_engine(repo_root, quick=not args.full_calibration)

    print(
        f"[2/6] Encoding {args.payload_bytes:,} synthetic bytes "
        f"into a 12-table package"
    )
    result = ns["run_package"](
        payload_bytes=args.payload_bytes,
        channels=args.channels,
        out_dir=out_dir,
    )

    manifest_path = out_dir / "manifest_adaptive_q_v12.json"
    package_path = out_dir / "published_adaptive_q_v12.npz"

    manifest, loaded, decoded_sha = decode_published_package(
        ns, package_path, manifest_path
    )

    fingerprint, vocab = make_locator_fingerprint(manifest)
    print(
        "[3/6] Building Codebook-B locator fingerprint "
        f"from {len(fingerprint)} labeled table descriptors"
    )
    locator = locator_demo(
        fingerprint,
        candidates=args.candidates,
    )

    print(
        f"[4/6] Locator target rank: {locator['target_rank']} / "
        f"{args.candidates}"
    )

    target_verified, decoy_verified = strict_verifier_demo(
        manifest["payload_sha256"],
        locator["target_id"],
        locator["best_decoy_id"],
    )
    print(
        "[5/6] Strict verifier: "
        f"best decoy={'ACCEPT' if decoy_verified else 'REJECT'}, "
        f"target={'ACCEPT' if target_verified else 'REJECT'}"
    )

    exact = (
        decoded_sha == manifest["payload_sha256"]
        and bool(result["exact_recovery"])
    )
    print(
        "[6/6] Published package decode + SHA-256: "
        f"{'PASS' if exact else 'FAIL'}"
    )

    plot_meta = write_curve_svg(
        ns,
        manifest,
        loaded,
        out_dir / "curve_before_after.svg",
    )

    q_schedule = [
        {
            "table_id": int(t["table_id"]),
            "family": t["family"],
            "q": int(t["q"]),
            "transform": t["transform"],
        }
        for t in manifest["tables"]
    ]

    compact_manifest = {
        "scope": "synthetic-only quick demo",
        "payload_bytes": int(manifest["payload_bytes"]),
        "payload_sha256": manifest["payload_sha256"],
        "decoded_sha256": decoded_sha,
        "exact_recovery": exact,
        "q_distribution": result["q_distribution"],
        "tables": q_schedule,
    }
    (out_dir / "demo_manifest_summary.json").write_text(
        json.dumps(compact_manifest, indent=2),
        encoding="utf-8",
    )

    summary = {
        "scope": "synthetic-only quick demo",
        "quick_calibration": not args.full_calibration,
        "payload_bytes": args.payload_bytes,
        "table_count": int(result["table_count"]),
        "channels_per_table": int(result["channels_per_table"]),
        "q_distribution": result["q_distribution"],
        "published_rows": int(result["published_rows_total"]),
        "gross_bits_per_numeric_value": float(
            result["gross_bits_per_numeric_value"]
        ),
        "locator": locator,
        "locator_vocabulary": [
            {"family": family, "q": int(q)}
            for family, q in vocab
        ],
        "strict_verifier": {
            "best_decoy": "ACCEPT" if decoy_verified else "REJECT",
            "target": "ACCEPT" if target_verified else "REJECT",
        },
        "decoded_sha256": decoded_sha,
        "expected_sha256": manifest["payload_sha256"],
        "exact_recovery": exact,
        "curve_example": plot_meta,
    }
    (out_dir / "demo_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print()
    print("Artifacts:")
    print(f"  {out_dir / 'curve_before_after.svg'}")
    print(f"  {out_dir / 'demo_manifest_summary.json'}")
    print(f"  {out_dir / 'demo_summary.json'}")
    print()
    if not args.full_calibration:
        print(
            "Note: quick demo calibration is intentionally smaller than "
            "the benchmark calibration used for reported results."
        )

    if not exact or not target_verified or decoy_verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
