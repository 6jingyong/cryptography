#!/usr/bin/env python3
"""Physical NPZ structural-damage experiment for current deterministic V18 + V20.

Synthetic-only. This experiment freezes package damage before results and does
not tune locator, q/delta, or RS geometry in response to damaged outcomes.

The only execution gate is the clean control. Damaged conditions are evidence,
not pass/fail targets.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
import runpy
from collections import Counter
from pathlib import Path

import numpy as np

BURST_SIGMA_DELTA = 4.0
BURST_WIDTHS = (4, 6)
NEAR_DECOY_FRACTION = 0.01
BURST_RNG_DOMAIN = 23_000_000
CORPUS_RNG_DOMAIN = 24_000_000


def load_npz_arrays(b_bytes: bytes) -> dict[str, np.ndarray]:
    with np.load(io.BytesIO(b_bytes)) as z:
        return {name: np.asarray(z[name]).copy() for name in z.files}


def save_npz_arrays(arrays: dict[str, np.ndarray]) -> bytes:
    out = io.BytesIO()
    np.savez_compressed(out, **arrays)
    return out.getvalue()


def logical_first_table(B: dict) -> dict:
    return min(
        B["tables"],
        key=lambda t: (int(t["payload_bit_offset"]), int(t["table_id"])),
    )


def damage_drop_table(b_bytes: bytes, table_id: int) -> bytes:
    arrays = load_npz_arrays(b_bytes)
    arrays.pop(f"table_{table_id}_x")
    arrays.pop(f"table_{table_id}_y")
    return save_npz_arrays(arrays)


def damage_truncate_tail_segment(b_bytes: bytes, table: dict) -> bytes:
    arrays = load_npz_arrays(b_bytes)
    tid = int(table["table_id"])
    n = int(table["points_per_block"])
    key = f"table_{tid}_y"
    y = arrays[key]
    if y.shape[0] <= n:
        raise RuntimeError("table has no removable tail segment")
    arrays[key] = y[:-n, :].copy()
    return save_npz_arrays(arrays)


def _to_transform_space(y: np.ndarray, transform: str) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    if transform == "log":
        if np.any(y <= 0):
            raise RuntimeError("log-domain burst requires positive published values")
        return np.log(y)
    return y.copy()


def _from_transform_space(z: np.ndarray, transform: str) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    if transform == "log":
        return np.exp(z)
    return z.copy()


def damage_localized_burst(
    b_bytes: bytes,
    table: dict,
    payload_seed: int,
    width_segments: int,
) -> bytes:
    arrays = load_npz_arrays(b_bytes)
    tid = int(table["table_id"])
    n = int(table["points_per_block"])
    segments = int(table["segments"])
    delta = float(table["delta"])
    transform = str(table["transform"])
    key = f"table_{tid}_y"
    if width_segments <= 0 or width_segments >= segments:
        raise RuntimeError("burst width must be positive and smaller than table segment count")

    # Keep segment 0 untouched because the current locator derives morphology
    # from the first public block. The experiment is intended to isolate a
    # shape-preserving numeric disturbance after successful location.
    start_segment = max(1, (segments - width_segments) // 2)
    if start_segment + width_segments > segments:
        start_segment = segments - width_segments
    row0 = start_segment * n
    row1 = (start_segment + width_segments) * n

    y = arrays[key]
    block = y[row0:row1, :].copy()
    z = _to_transform_space(block, transform)
    rng = np.random.default_rng(
        BURST_RNG_DOMAIN
        + int(payload_seed) * 1009
        + int(width_segments) * 37
        + tid
    )
    noise = rng.normal(0.0, BURST_SIGMA_DELTA * delta, size=z.shape)
    y2 = _from_transform_space(z + noise, transform)
    if not np.all(np.isfinite(y2)):
        raise RuntimeError("localized burst produced non-finite values")
    arrays[key][row0:row1, :] = y2
    return save_npz_arrays(arrays)


def damaged_record(A, clean_record: dict, damaged_b: bytes) -> dict:
    out = dict(clean_record)
    out[A.field_payload] = base64.b64encode(damaged_b).decode()
    return out


def safe_locator_score(V20: dict, A, record: dict):
    try:
        return float(V20["locator_score"](A, record)), None
    except Exception as exc:
        return None, type(exc).__name__


def corpus_fixture(V20: dict, A, payload_seed: int, corpus_size: int):
    rng = np.random.default_rng(CORPUS_RNG_DOMAIN + int(payload_seed))
    target_index = int(rng.integers(0, corpus_size))
    candidates = [i for i in range(corpus_size) if i != target_index]
    near_count = int(round((corpus_size - 1) * NEAR_DECOY_FRACTION))
    near_ids = set(
        int(x)
        for x in rng.choice(candidates, size=near_count, replace=False)
    )
    decoy_scores = {}
    for i in candidates:
        d = V20["make_d_descriptor"](A, rng, i in near_ids)
        decoy_scores[i] = float(V20["locator_score"](A, d))
    return target_index, decoy_scores


def rank_from_score(target_index: int, decoy_scores: dict[int, float], target_score):
    score = -1.0 if target_score is None else float(target_score)
    all_scores = []
    size = len(decoy_scores) + 1
    for i in range(size):
        all_scores.append(score if i == target_index else decoy_scores[i])
    order = np.argsort(-np.asarray(all_scores), kind="stable")
    return int(next(j + 1 for j, idx in enumerate(order) if int(idx) == target_index))


def candidate_error_geometry(payload: bytes, candidate: bytes, B: dict):
    if len(candidate) != len(payload):
        return {
            "candidate_byte_errors": None,
            "shard_byte_errors": None,
            "max_shard_byte_errors": None,
            "any_shard_over_capacity": None,
        }

    total_errors = int(sum(a != b for a, b in zip(payload, candidate)))
    cfg = B["outer_reliability"]
    shard_lengths = [int(x) for x in cfg["shard_lengths"]]
    capacity = int(cfg["parity_bytes_per_shard"]) // 2
    shard_errors = []
    off = 0
    for n in shard_lengths:
        p = payload[off:off+n]
        c = candidate[off:off+n]
        shard_errors.append(int(sum(a != b for a, b in zip(p, c))))
        off += n
    mx = int(max(shard_errors)) if shard_errors else 0
    return {
        "candidate_byte_errors": total_errors,
        "shard_byte_errors": shard_errors,
        "max_shard_byte_errors": mx,
        "any_shard_over_capacity": bool(mx > capacity),
    }


def classify_first_failure(locator_score, locator_error, candidate_error, direct_ok, opened):
    if locator_error is not None:
        return "A_LOCATOR_EXCEPTION"
    if locator_score is None or locator_score < 1.0:
        return "A_LOCATOR_DEGRADED"
    if candidate_error is not None:
        return "B_OR_b_DECODE_FAILED_BEFORE_CANDIDATE"
    if bool(direct_ok):
        return "DIRECT_EXACT"
    if opened.get("accepted") and opened.get("repair_success"):
        return "V20_REPAIR_SUCCESS"
    if opened.get("accepted"):
        return "V20_ACCEPTED_OTHER"
    return "V20_OR_FINAL_VERIFY_FAILURE"


def run_condition(
    V20: dict,
    engine: dict,
    built: dict,
    payload_seed: int,
    condition: str,
    damaged_b: bytes,
    target_index: int,
    decoy_scores: dict[int, float],
):
    A = built["A"]
    B = built["B"]
    record = damaged_record(A, built["c"], damaged_b)
    locator_score, locator_error = safe_locator_score(V20, A, record)
    target_rank = rank_from_score(target_index, decoy_scores, locator_score)

    B_bytes = V20["serialize_B"](B)
    candidate = None
    candidate_sha = None
    direct_ok = None
    candidate_error = None
    try:
        candidate, candidate_sha, direct_ok = V20["V18"]["decode_package"](
            engine, B_bytes, damaged_b
        )
    except Exception as exc:
        candidate_error = type(exc).__name__

    geometry = {
        "candidate_byte_errors": None,
        "shard_byte_errors": None,
        "max_shard_byte_errors": None,
        "any_shard_over_capacity": None,
    }
    if candidate is not None:
        geometry = candidate_error_geometry(built["payload"], candidate, B)

    opened = V20["try_open_v20"](A, engine, record)
    first_failure = classify_first_failure(
        locator_score, locator_error, candidate_error, direct_ok, opened
    )

    cfg = B["outer_reliability"]
    capacity = int(cfg["parity_bytes_per_shard"]) // 2
    comparable = (
        candidate is not None
        and geometry["any_shard_over_capacity"] is not None
    )
    capacity_rule_mismatch = None
    if comparable:
        predicted_final_failure = bool(geometry["any_shard_over_capacity"])
        actual_final_failure = not bool(opened.get("accepted"))
        capacity_rule_mismatch = predicted_final_failure != actual_final_failure

    return {
        "payload_seed": int(payload_seed),
        "condition": condition,
        "target_locator_score": locator_score,
        "locator_error": locator_error,
        "target_rank": target_rank,
        "candidate_produced": candidate is not None,
        "candidate_decode_error": candidate_error,
        "candidate_sha256": candidate_sha,
        "direct_exact": bool(direct_ok) if direct_ok is not None else None,
        **geometry,
        "rs_byte_error_capacity_per_shard": capacity,
        "v20_accepted": bool(opened.get("accepted")),
        "v20_reason": opened.get("reason"),
        "repair_attempted": bool(opened.get("repair_attempted", False)),
        "repair_success": bool(opened.get("repair_success", False)),
        "corrected_shards": opened.get("corrected_shards"),
        "first_failure_layer": first_failure,
        "capacity_rule_comparable": comparable,
        "capacity_rule_mismatch": capacity_rule_mismatch,
    }


def summarize_condition(rows: list[dict]):
    n = len(rows)
    stage_counts = Counter(r["first_failure_layer"] for r in rows)
    comparable = [r for r in rows if r["capacity_rule_comparable"]]
    byte_errors = [
        int(r["candidate_byte_errors"])
        for r in rows
        if r["candidate_byte_errors"] is not None
    ]
    max_shard_errors = [
        int(r["max_shard_byte_errors"])
        for r in rows
        if r["max_shard_byte_errors"] is not None
    ]
    return {
        "runs": n,
        "stage_counts": dict(sorted(stage_counts.items())),
        "locator_score_1_runs": sum(r["target_locator_score"] == 1.0 for r in rows),
        "recall_at_20": float(np.mean([r["target_rank"] <= 20 for r in rows])),
        "recall_at_100": float(np.mean([r["target_rank"] <= 100 for r in rows])),
        "median_target_rank": float(np.median([r["target_rank"] for r in rows])),
        "max_target_rank": int(max(r["target_rank"] for r in rows)),
        "candidate_produced_runs": sum(r["candidate_produced"] for r in rows),
        "direct_exact_runs": sum(r["direct_exact"] is True for r in rows),
        "v20_accepted_runs": sum(r["v20_accepted"] for r in rows),
        "repair_attempts": sum(r["repair_attempted"] for r in rows),
        "repair_successes": sum(r["repair_success"] for r in rows),
        "candidate_byte_errors_median": (
            float(np.median(byte_errors)) if byte_errors else None
        ),
        "candidate_byte_errors_max": max(byte_errors) if byte_errors else None,
        "max_shard_byte_errors_max": max(max_shard_errors) if max_shard_errors else None,
        "capacity_rule_comparable_runs": len(comparable),
        "capacity_rule_mismatches": sum(
            r["capacity_rule_mismatch"] is True for r in comparable
        ),
    }


def write_markdown(result: dict, path: Path):
    lines = [
        "# Physical structural damage v1",
        "",
        "Synthetic-only frozen experiment. Damaged outcomes are observations, not pass/fail targets.",
        "",
        f"- clean execution gate: **{'PASS' if result['execution_gate_pass'] else 'FAIL'}**",
        f"- seeds: {result['frozen_contract']['seeds']}",
        f"- engine: `{result['frozen_contract']['engine']}`",
        f"- burst sigma: {result['frozen_contract']['burst_sigma_delta']} × delta",
        "",
        "| condition | locator 1.0 | R@100 | candidate | direct exact | V20 accept | repairs | cap-rule mismatches |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in result["summary"].items():
        lines.append(
            f"| {name} | {row['locator_score_1_runs']}/{row['runs']} "
            f"| {row['recall_at_100']:.3f} "
            f"| {row['candidate_produced_runs']}/{row['runs']} "
            f"| {row['direct_exact_runs']}/{row['runs']} "
            f"| {row['v20_accepted_runs']}/{row['runs']} "
            f"| {row['repair_successes']}/{row['repair_attempts']} "
            f"| {row['capacity_rule_mismatches']}/{row['capacity_rule_comparable_runs']} |"
        )
    lines += ["", "## First-failure layers", ""]
    for name, row in result["summary"].items():
        lines.append(f"- **{name}**: `{json.dumps(row['stage_counts'], sort_keys=True)}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--engine",
        type=Path,
        default=Path("src/noisy_host_package_v18_deterministic.py"),
    )
    ap.add_argument("--v20", type=Path, default=Path("protocol/real-package-v20.py"))
    ap.add_argument(
        "--seeds",
        default="1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,1012,"
        "1013,1014,1015,1016,1017,1018,1019,1020,1021,1022,1023,1024",
    )
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--corpus-size", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=Path("physical-structural-damage-v1.json"))
    ap.add_argument(
        "--summary-out",
        type=Path,
        default=Path("physical-structural-damage-v1.md"),
    )
    args = ap.parse_args()

    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    V20 = runpy.run_path(str(args.v20))
    engine = V20["load_engine"](args.engine)

    rows = []
    clean_gate_rows = []
    target_metadata = []

    for seed in seeds:
        built = V20["build_v20_package"](
            engine, seed, args.payload_bytes, args.channels
        )
        table = logical_first_table(built["B"])
        tid = int(table["table_id"])
        target_metadata.append({
            "payload_seed": seed,
            "public_table_id": tid,
            "payload_bit_offset": int(table["payload_bit_offset"]),
            "points_per_block": int(table["points_per_block"]),
            "segments": int(table["segments"]),
            "q": int(table["q"]),
            "delta": float(table["delta"]),
            "transform": str(table["transform"]),
        })
        target_index, decoy_scores = corpus_fixture(
            V20, built["A"], seed, args.corpus_size
        )

        variants = [
            ("clean", built["b"]),
            ("drop_logical_first_table", damage_drop_table(built["b"], tid)),
            (
                "truncate_tail_segment_logical_first_table",
                damage_truncate_tail_segment(built["b"], table),
            ),
        ]
        for width in BURST_WIDTHS:
            variants.append((
                f"localized_burst_{width}_segments_sigma4delta",
                damage_localized_burst(built["b"], table, seed, width),
            ))

        for condition, damaged_b in variants:
            row = run_condition(
                V20,
                engine,
                built,
                seed,
                condition,
                damaged_b,
                target_index,
                decoy_scores,
            )
            rows.append(row)
            if condition == "clean":
                clean_gate_rows.append(row)

    conditions = sorted({r["condition"] for r in rows})
    summary = {
        condition: summarize_condition([r for r in rows if r["condition"] == condition])
        for condition in conditions
    }

    execution_gate_pass = all(
        r["target_locator_score"] == 1.0
        and r["target_rank"] == 1
        and r["candidate_produced"]
        and r["direct_exact"] is True
        and r["v20_accepted"]
        and not r["repair_attempted"]
        for r in clean_gate_rows
    )

    result = {
        "version": "physical-structural-damage-v1",
        "scope": "synthetic-only",
        "status": "EXECUTION_GATE_PASS" if execution_gate_pass else "EXECUTION_GATE_FAIL",
        "execution_gate_definition": (
            "clean controls only; damaged conditions never gate pass/fail"
        ),
        "execution_gate_pass": execution_gate_pass,
        "frozen_contract": {
            "engine": str(args.engine),
            "v20": str(args.v20),
            "seeds": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "corpus_size": args.corpus_size,
            "near_decoy_fraction": NEAR_DECOY_FRACTION,
            "burst_sigma_delta": BURST_SIGMA_DELTA,
            "burst_width_segments": list(BURST_WIDTHS),
            "target_table_rule": "minimum payload_bit_offset, then minimum public table_id",
            "v20_geometry": {
                "data_shard_bytes": V20["DATA_SHARD_BYTES"],
                "parity_bytes_per_shard": V20["PARITY_BYTES_PER_SHARD"],
                "byte_error_capacity_per_shard": V20["PARITY_BYTES_PER_SHARD"] // 2,
            },
            "no_tuning": [
                "A locator unchanged",
                "deterministic V18 q/delta unchanged",
                "V20 RS geometry unchanged",
                "damaged outcomes are not acceptance criteria",
            ],
        },
        "target_table_metadata": target_metadata,
        "summary": summary,
        "runs": rows,
    }
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_markdown(result, args.summary_out)
    print(json.dumps({
        "status": result["status"],
        "summary": summary,
    }, indent=2))

    if not execution_gate_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
