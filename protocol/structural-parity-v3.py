#!/usr/bin/env python3
"""Frozen candidate: 11 data tables + 1 XOR structural-parity table.

Synthetic/mock benchmark only. Current A-v3/V18/V20 remain unchanged.
This candidate reuses the deterministic V18 carrier and unchanged V20
repair field, while adding one table-level XOR erasure layer inside the
existing 12 public numeric tables.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import io
import json
import runpy
from collections import Counter
from pathlib import Path

import numpy as np

DATA_TABLES = 11
TOTAL_TABLES = 12
XLENS = tuple(range(24, 48, 2))
NEAR = 0.01
CORPUS_DOMAIN = 26_000_000
TOP_K = 20


def load_npz(data: bytes) -> dict[str, np.ndarray]:
    with np.load(io.BytesIO(data)) as z:
        return {k: np.asarray(z[k]).copy() for k in z.files}


def save_npz(arrays: dict[str, np.ndarray]) -> bytes:
    out = io.BytesIO()
    np.savez_compressed(out, **arrays)
    return out.getvalue()


def split_payload_bits(bits: np.ndarray):
    n = len(bits)
    starts = [round(i * n / DATA_TABLES) for i in range(DATA_TABLES + 1)]
    chunks = [np.asarray(bits[starts[i]:starts[i + 1]], dtype=np.uint8) for i in range(DATA_TABLES)]
    lengths = [len(c) for c in chunks]
    return chunks, starts[:-1], lengths


def xor_parity(chunks: list[np.ndarray]) -> np.ndarray:
    width = max(len(c) for c in chunks)
    parity = np.zeros(width, dtype=np.uint8)
    for c in chunks:
        parity[:len(c)] ^= c
    return parity


def A4(V3):
    Root = V3["RootCodebookA"]
    return Root(
        version="A-v4-erasure-xlen",
        root_key_hex=hashlib.sha256(b"synthetic-root-A-v4-erasure-xlen").hexdigest(),
        table_profile="v18-12table-xlen-erasure-v1",
        expected_table_count=len(XLENS),
        field_manifest="m",
        field_payload="p",
        field_tag="t",
    )


def expected_map(A):
    return {i: XLENS[j] for i, j in enumerate(A.keyed_permutation(len(XLENS)))}


def observed_map(data: bytes):
    with np.load(io.BytesIO(data)) as z:
        return {
            int(k.split("_")[1]): int(len(np.asarray(z[k])))
            for k in z.files
            if k.startswith("table_") and k.endswith("_x")
        }


def locator(A, record: dict) -> float:
    if "public_rank_sequence" in record:
        seq = list(record["public_rank_sequence"])
        exp = A.keyed_permutation(len(seq))
        return float(np.mean(np.asarray(seq) == np.asarray(exp))) if seq else 0.0
    try:
        obs = observed_map(base64.b64decode(record[A.field_payload], validate=True))
    except Exception:
        return 0.0
    exp = expected_map(A)
    return sum(obs.get(i) == n for i, n in exp.items()) / len(exp)


def custom_generate_B_b(V20: dict, engine: dict, payload_bytes: int, channels: int, seed: int):
    V20["set_seed"](engine, seed)
    payload = engine["synthetic_payload"](payload_bytes)
    bits = engine["bytes_to_bits"](payload)
    chunks, offsets, lengths = split_payload_bits(bits)
    parity = xor_parity(chunks)

    blueprint = list(engine["TABLE_BLUEPRINT"])
    if len(blueprint) != TOTAL_TABLES:
        raise RuntimeError("candidate assumes exactly 12 current V18 tables")

    selected = []
    calibrations = []
    for i, (family, budget) in enumerate(blueprint):
        chosen, trials = engine["choose_mode"](i, family, budget, channels)
        calibrations.append({"table_id": i, "family": family, "budget": budget, "trials": trials})
        if chosen is None:
            raise RuntimeError(f"V18 calibration failed for table {i}")
        selected.append((family, chosen))

    logical_chunks = list(chunks) + [parity]
    arrays = {}
    tables = []
    basis_version = engine.get("BASIS_VERSION")
    for i, ((family, chosen), chunk) in enumerate(zip(selected, logical_chunks)):
        x, pub, tm = engine["encode_table"](chunk, i, family, chosen, channels)
        if basis_version is not None:
            tm["basis_version"] = basis_version
        if i < DATA_TABLES:
            tm["structural_role"] = "data"
            tm["structural_data_index"] = i
            tm["payload_bit_offset"] = int(offsets[i])
            tm["structural_chunk_bits"] = int(lengths[i])
        else:
            tm["structural_role"] = "xor_parity"
            tm["structural_data_index"] = None
            tm["payload_bit_offset"] = 0
            tm["structural_chunk_bits"] = int(len(parity))
        arrays[f"table_{i}_x"] = x
        arrays[f"table_{i}_y"] = pub
        tables.append(tm)

    B = {
        "version": "structural-parity-v3-candidate",
        "scope": "synthetic-only",
        "payload_bytes": payload_bytes,
        "payload_bit_length": len(bits),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "basis_version": basis_version,
        "q_candidates": [4, 2],
        "host_sigma_multiple": engine.get("HOST_SIGMA_MULTIPLE"),
        "tables": tables,
        "structural_reliability": {
            "version": "xor-single-table-erasure-v1",
            "data_table_count": DATA_TABLES,
            "physical_table_count": TOTAL_TABLES,
            "data_chunk_offsets": [int(x) for x in offsets],
            "data_chunk_bit_lengths": [int(x) for x in lengths],
            "parity_bit_length": int(len(parity)),
            "padding": "right-zero-to-parity-width",
            "guarantee_target": "one whole data-table erasure when xor parity table is available; parity-table loss needs no reconstruction",
        },
    }
    return B, save_npz(arrays), payload, calibrations


def permute_A4(A, B: dict, data: bytes):
    arrays = load_npz(data)
    ids = sorted(int(k.split("_")[1]) for k in arrays if k.startswith("table_") and k.endswith("_x"))
    lens = {i: int(len(arrays[f"table_{i}_x"])) for i in ids}
    if tuple(sorted(lens.values())) != XLENS or len(set(lens.values())) != len(lens):
        raise RuntimeError("unexpected/non-unique x-grid profile")
    by_len = {n: i for i, n in lens.items()}
    pub_old = {p: by_len[XLENS[j]] for p, j in enumerate(A.keyed_permutation(len(XLENS)))}
    old_pub = {o: p for p, o in pub_old.items()}

    out = {}
    for p, o in pub_old.items():
        out[f"table_{p}_x"] = arrays[f"table_{o}_x"]
        out[f"table_{p}_y"] = arrays[f"table_{o}_y"]

    B2 = json.loads(json.dumps(B))
    for t in B2["tables"]:
        t["table_id"] = old_pub[int(t["table_id"])]
    B2["tables"] = sorted(B2["tables"], key=lambda t: int(t["table_id"]))

    sr = B2["structural_reliability"]
    sr["data_public_table_ids"] = [
        int(next(t["table_id"] for t in B2["tables"] if t.get("structural_role") == "data" and int(t["structural_data_index"]) == i))
        for i in range(DATA_TABLES)
    ]
    sr["parity_public_table_id"] = int(
        next(t["table_id"] for t in B2["tables"] if t.get("structural_role") == "xor_parity")
    )
    return B2, save_npz(out)


def build(V20: dict, engine: dict, seed: int, payload_bytes: int, channels: int):
    V3 = V20["V3"]
    A = A4(V3)
    B0, b0, payload, calibrations = custom_generate_B_b(V20, engine, payload_bytes, channels, seed)
    B1, b = permute_A4(A, B0, b0)
    parity, shard_lengths = V20["rs_parity"](payload)
    B = V20["add_v20_manifest"](B1, payload_bytes, shard_lengths)
    c = V20["make_c_v20"](A, B, b, parity)
    return {"A": A, "B": B, "b": b, "c": c, "payload": payload, "calibrations": calibrations}


def drop_table(data: bytes, tid: int) -> bytes:
    arrays = load_npz(data)
    arrays.pop(f"table_{tid}_x")
    arrays.pop(f"table_{tid}_y")
    return save_npz(arrays)


def truncate_tail(data: bytes, table: dict) -> bytes:
    arrays = load_npz(data)
    tid = int(table["table_id"])
    block = int(table["points_per_block"])
    key = f"table_{tid}_y"
    y = arrays[key]
    if y.shape[0] <= block:
        raise RuntimeError("no removable tail segment")
    arrays[key] = y[:-block, :].copy()
    return save_npz(arrays)


def record_with_b(A, c: dict, data: bytes) -> dict:
    r = dict(c)
    r[A.field_payload] = base64.b64encode(data).decode()
    return r


def corpus(V20: dict, A, seed: int, size: int):
    rng = np.random.default_rng(CORPUS_DOMAIN + seed)
    target = int(rng.integers(0, size))
    others = [i for i in range(size) if i != target]
    near_n = int(round((size - 1) * NEAR))
    near = set(int(x) for x in rng.choice(others, size=near_n, replace=False))
    scores = {i: locator(A, V20["make_d_descriptor"](A, rng, i in near)) for i in others}
    return target, scores


def rank(target: int, decoys: dict[int, float], score: float) -> int:
    vals = [score if i == target else decoys[i] for i in range(len(decoys) + 1)]
    order = np.argsort(-np.asarray(vals), kind="stable")
    return int(next(j + 1 for j, i in enumerate(order) if int(i) == target))


def decode_table_prefix(engine: dict, table: dict, pub: np.ndarray):
    channels = int(table["channels"])
    block = int(table["points_per_block"])
    segments = int(table["segments"])
    chunk_bits = int(table["structural_chunk_bits"])
    if pub.ndim != 2 or pub.shape[1] != channels:
        raise RuntimeError("unsupported table shape")
    full_segments = min(segments, int(pub.shape[0] // block))
    valid_codewords = min(int(table["valid_codewords"]), full_segments * channels)
    prefix_bits = min(
        chunk_bits,
        valid_codewords * int(table["payload_symbols_per_codeword"]) * int(table["m"]),
    )
    out = np.zeros(chunk_bits, dtype=np.uint8)
    erased = np.ones(chunk_bits, dtype=bool)
    if prefix_bits:
        tt = dict(table)
        tt["segments"] = full_segments
        tt["valid_codewords"] = valid_codewords
        tt["payload_bit_length"] = prefix_bits
        got = engine["decode_table"](pub[:full_segments * block, :], tt)
        out[:prefix_bits] = got[:prefix_bits]
        erased[:prefix_bits] = False
    return out, erased, full_segments, prefix_bits


def structural_decode(engine: dict, B_bytes: bytes, data: bytes):
    B = json.loads(B_bytes.decode())
    sr = B["structural_reliability"]
    chunks = [None] * DATA_TABLES
    erased = [None] * DATA_TABLES
    parity_bits = np.zeros(int(sr["parity_bit_length"]), dtype=np.uint8)
    parity_erased = np.ones(len(parity_bits), dtype=bool)
    table_reports = []

    with np.load(io.BytesIO(data)) as z:
        for table in B["tables"]:
            tid = int(table["table_id"])
            role = table["structural_role"]
            width = int(table["structural_chunk_bits"])
            key = f"table_{tid}_y"
            if key not in z.files:
                bits = np.zeros(width, dtype=np.uint8)
                mask = np.ones(width, dtype=bool)
                status = "MISSING_TABLE"
                prefix = 0
            else:
                bits, mask, _full_segments, prefix = decode_table_prefix(engine, table, np.asarray(z[key], dtype=float))
                status = "COMPLETE" if not np.any(mask) else "TAIL_ERASURE"
            if role == "data":
                idx = int(table["structural_data_index"])
                chunks[idx] = bits
                erased[idx] = mask
            elif role == "xor_parity":
                parity_bits = bits
                parity_erased = mask
            else:
                raise RuntimeError("unknown structural role")
            table_reports.append({
                "table_id": tid,
                "role": role,
                "data_index": table.get("structural_data_index"),
                "status": status,
                "decoded_prefix_bits": int(prefix),
                "erased_bits_before_structural_recovery": int(np.sum(mask)),
            })

    if any(c is None for c in chunks) or any(m is None for m in erased):
        raise RuntimeError("missing data-table metadata")

    before = int(sum(np.sum(m) for m in erased))
    recovered = 0
    for pos in range(len(parity_bits)):
        unknown = []
        known_xor = 0
        for i in range(DATA_TABLES):
            if pos >= len(chunks[i]):
                continue
            if erased[i][pos]:
                unknown.append(i)
            else:
                known_xor ^= int(chunks[i][pos])
        if len(unknown) == 1 and not parity_erased[pos]:
            i = unknown[0]
            chunks[i][pos] = int(parity_bits[pos]) ^ known_xor
            erased[i][pos] = False
            recovered += 1

    after = int(sum(np.sum(m) for m in erased))
    payload_bits = np.concatenate(chunks)
    payload = engine["bits_to_bytes"](payload_bits)[:int(B["payload_bytes"])]
    sha = hashlib.sha256(payload).hexdigest()
    direct_ok = hmac.compare_digest(sha, str(B["payload_sha256"]))
    all_erased = np.concatenate(erased)
    erased_byte_indices = [
        i for i in range(len(payload))
        if np.any(all_erased[i * 8:(i + 1) * 8])
    ]
    return payload, sha, direct_ok, {
        "data_erased_bits_before": before,
        "structurally_recovered_bits": recovered,
        "data_erased_bits_after": after,
        "data_erased_bytes_after": len(erased_byte_indices),
        "parity_erased_bits": int(np.sum(parity_erased)),
        "tables": table_reports,
    }


def open_candidate(V20: dict, A, B_bytes: bytes, candidate: bytes, direct_ok: bool, record: dict):
    try:
        rb = base64.b64decode(record[A.field_manifest], validate=True)
        masked = base64.b64decode(record[V20["FIELD_REPAIR"]], validate=True)
        tag = str(record[A.field_tag])
    except Exception:
        return {"accepted": False, "reason": "A_bootstrap_parse_failed"}
    if rb != B_bytes or not hmac.compare_digest(tag, V20["package_tag_v20"](A, rb, masked)):
        return {"accepted": False, "reason": "v20_envelope_integrity_failed"}
    B = json.loads(rb.decode())
    parity = V20["decode_repair_field"](A, B, masked)
    if direct_ok:
        return {"accepted": True, "reason": "strict_verify_pass_no_v20_repair", "repair_attempted": False, "repair_success": False}
    try:
        repaired, corrected = V20["repair_payload"](B, candidate, parity)
    except Exception as exc:
        return {"accepted": False, "reason": "v20_repair_failed", "detail": type(exc).__name__, "repair_attempted": True, "repair_success": False}
    sha = hashlib.sha256(repaired).hexdigest()
    ok = hmac.compare_digest(sha, str(B["payload_sha256"]))
    return {
        "accepted": ok,
        "reason": "strict_verify_pass_after_v20_repair" if ok else "v20_repaired_payload_hash_failed",
        "repair_attempted": True,
        "repair_success": ok,
        "corrected_shards": corrected,
    }


def geometry(payload: bytes, candidate: bytes, B: dict):
    total = int(sum(a != b for a, b in zip(payload, candidate)))
    off = 0
    shards = []
    for n in map(int, B["outer_reliability"]["shard_lengths"]):
        shards.append(int(sum(a != b for a, b in zip(payload[off:off+n], candidate[off:off+n]))))
        off += n
    return total, shards, max(shards) if shards else 0


def run_variant(V20: dict, engine: dict, built: dict, seed: int, condition: str, data: bytes, target: int, decoys: dict[int, float], damaged_table: dict | None):
    A, B = built["A"], built["B"]
    record = record_with_b(A, built["c"], data)
    score = locator(A, record)
    target_rank = rank(target, decoys, score)
    B_bytes = V20["serialize_B"](B)
    try:
        candidate, _candidate_sha, direct_ok, report = structural_decode(engine, B_bytes, data)
        decode_error = None
    except Exception as exc:
        candidate = direct_ok = report = None
        decode_error = type(exc).__name__

    opened = {"accepted": False, "reason": "candidate_decode_failed", "repair_attempted": False, "repair_success": False}
    byte_errors = shard_errors = max_shard = None
    if candidate is not None:
        byte_errors, shard_errors, max_shard = geometry(built["payload"], candidate, B)
        opened = open_candidate(V20, A, B_bytes, candidate, bool(direct_ok), record)

    return {
        "payload_seed": seed,
        "condition": condition,
        "damaged_table_id": None if damaged_table is None else int(damaged_table["table_id"]),
        "damaged_table_role": None if damaged_table is None else damaged_table["structural_role"],
        "damaged_data_index": None if damaged_table is None else damaged_table.get("structural_data_index"),
        "target_locator_score": score,
        "target_rank": target_rank,
        "candidate_produced": candidate is not None,
        "candidate_decode_error": decode_error,
        "direct_exact": bool(direct_ok) if direct_ok is not None else None,
        "structural_report": report,
        "candidate_byte_errors": byte_errors,
        "shard_byte_errors": shard_errors,
        "max_shard_byte_errors": max_shard,
        "v20_accepted": bool(opened.get("accepted")),
        "v20_reason": opened.get("reason"),
        "repair_attempted": bool(opened.get("repair_attempted", False)),
        "repair_success": bool(opened.get("repair_success", False)),
    }


def summarize(rows: list[dict]):
    ranks = [r["target_rank"] for r in rows]
    scores = [r["target_locator_score"] for r in rows]
    after = [
        r["structural_report"]["data_erased_bits_after"]
        for r in rows if r["structural_report"] is not None
    ]
    return {
        "runs": len(rows),
        "locator_score_median": float(np.median(scores)),
        "recall_at_20": float(np.mean([r <= TOP_K for r in ranks])),
        "median_target_rank": float(np.median(ranks)),
        "max_target_rank": int(max(ranks)),
        "candidate_produced_runs": sum(r["candidate_produced"] for r in rows),
        "direct_exact_runs": sum(r["direct_exact"] is True for r in rows),
        "v20_accepted_runs": sum(r["v20_accepted"] for r in rows),
        "repair_attempts": sum(r["repair_attempted"] for r in rows),
        "repair_successes": sum(r["repair_success"] for r in rows),
        "unresolved_structural_bits_max": max(after) if after else None,
        "v20_reason_counts": dict(sorted(Counter(r["v20_reason"] for r in rows).items())),
    }


def write_md(result: dict, path: Path):
    s = result["summary"]
    lines = [
        "# Structural parity v3 candidate",
        "",
        "Synthetic-only frozen experiment. Current A-v3/V18/V20 are not replaced by this candidate.",
        "",
        f"Promotion gate: **{'PASS' if result['promotion_gate_pass'] else 'FAIL'}**",
        "",
        "| condition | runs | R@20 | median rank | max rank | candidates | direct exact | V20 accepted | unresolved structural bits max |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in s.items():
        lines.append(
            f"| {name} | {row['runs']} | {row['recall_at_20']:.3f} | {row['median_target_rank']:.1f} | "
            f"{row['max_target_rank']} | {row['candidate_produced_runs']}/{row['runs']} | "
            f"{row['direct_exact_runs']}/{row['runs']} | {row['v20_accepted_runs']}/{row['runs']} | "
            f"{row['unresolved_structural_bits_max']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18_deterministic.py"))
    p.add_argument("--v20", type=Path, default=Path("protocol/real-package-v20.py"))
    p.add_argument("--seeds", default=",".join(map(str, range(1201, 1225))))
    p.add_argument("--payload-bytes", type=int, default=512)
    p.add_argument("--channels", type=int, default=2)
    p.add_argument("--corpus-size", type=int, default=2000)
    p.add_argument("--out", type=Path, default=Path("structural-parity-v3.json"))
    p.add_argument("--summary-out", type=Path, default=Path("structural-parity-v3.md"))
    a = p.parse_args()

    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    V20 = runpy.run_path(str(a.v20))
    engine = V20["load_engine"](a.engine)
    rows = []
    package_meta = []

    for seed in seeds:
        built = build(V20, engine, seed, a.payload_bytes, a.channels)
        A, B = built["A"], built["B"]
        target, decoys = corpus(V20, A, seed, a.corpus_size)
        tables = list(B["tables"])
        sr = B["structural_reliability"]
        package_meta.append({
            "payload_seed": seed,
            "payload_sha256": B["payload_sha256"],
            "data_chunk_bit_lengths": sr["data_chunk_bit_lengths"],
            "parity_bit_length": sr["parity_bit_length"],
            "parity_public_table_id": sr["parity_public_table_id"],
        })

        rows.append(run_variant(V20, engine, built, seed, "clean", built["b"], target, decoys, None))
        for table in tables:
            rows.append(run_variant(
                V20, engine, built, seed, "drop_one_table",
                drop_table(built["b"], int(table["table_id"])),
                target, decoys, table,
            ))
            rows.append(run_variant(
                V20, engine, built, seed, "truncate_one_tail_segment",
                truncate_tail(built["b"], table),
                target, decoys, table,
            ))

    summary = {
        name: summarize([r for r in rows if r["condition"] == name])
        for name in ("clean", "drop_one_table", "truncate_one_tail_segment")
    }

    clean = [r for r in rows if r["condition"] == "clean"]
    drop = [r for r in rows if r["condition"] == "drop_one_table"]
    trunc = [r for r in rows if r["condition"] == "truncate_one_tail_segment"]
    promotion_gate_pass = bool(
        all(r["target_rank"] <= TOP_K and r["candidate_produced"] and r["direct_exact"] is True and r["v20_accepted"] for r in clean)
        and all(r["target_rank"] <= TOP_K and r["candidate_produced"] and r["structural_report"]["data_erased_bits_after"] == 0 and r["direct_exact"] is True and r["v20_accepted"] for r in drop)
        and all(r["target_rank"] <= TOP_K and r["candidate_produced"] and r["structural_report"]["data_erased_bits_after"] == 0 and r["direct_exact"] is True and r["v20_accepted"] for r in trunc)
    )

    max_chunk_bits = max(max(m["data_chunk_bit_lengths"]) for m in package_meta)
    result = {
        "version": "structural-parity-v3-candidate",
        "scope": "synthetic-only",
        "status": "PROMOTION_GATE_PASS" if promotion_gate_pass else "PROMOTION_GATE_FAIL",
        "promotion_gate_pass": promotion_gate_pass,
        "frozen_contract": {
            "seeds": seeds,
            "payload_bytes": a.payload_bytes,
            "channels": a.channels,
            "corpus_size": a.corpus_size,
            "top_k": TOP_K,
            "A_candidate": "A-v4-erasure-xlen",
            "carrier": str(a.engine),
            "V20": str(a.v20),
            "structural_code": "11 data tables + 1 XOR parity table inside existing 12 public tables",
            "data_table_count": DATA_TABLES,
            "physical_table_count": TOTAL_TABLES,
            "structural_overhead_bits": max_chunk_bits,
            "structural_overhead_fraction_of_payload": max_chunk_bits / (a.payload_bytes * 8),
            "V20_geometry_unchanged": True,
            "q_delta_unchanged": True,
            "rank_gate": "Top-20, not strict rank-1, because exact A-visible descriptor collisions are information-theoretically indistinguishable before authenticated open",
            "damage_matrix": "every public table deleted once and tail-truncated once for every seed",
        },
        "package_meta": package_meta,
        "summary": summary,
        "runs": rows,
    }
    a.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result, a.summary_out)
    print(json.dumps({"status": result["status"], "summary": summary}, indent=2))
    if not promotion_gate_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
