#!/usr/bin/env python3
"""Frozen synthetic candidate: erasure-tolerant A locator + decoder, unchanged V20."""
from __future__ import annotations
import argparse, base64, hashlib, hmac, io, json, runpy
from collections import Counter
from pathlib import Path
import numpy as np

XLENS = tuple(range(24, 48, 2))
NEAR = 0.01
CORPUS_DOMAIN = 25_000_000


def load_npz(data):
    with np.load(io.BytesIO(data)) as z:
        return {k: np.asarray(z[k]).copy() for k in z.files}


def save_npz(arrays):
    out = io.BytesIO(); np.savez_compressed(out, **arrays); return out.getvalue()


def A4(V3):
    Root = V3["RootCodebookA"]
    return Root(
        version="A-v4-erasure-xlen",
        root_key_hex=hashlib.sha256(b"synthetic-root-A-v4-erasure-xlen").hexdigest(),
        table_profile="v18-12table-xlen-erasure-v1",
        expected_table_count=len(XLENS), field_manifest="m", field_payload="p", field_tag="t",
    )


def expected_map(A):
    return {i: XLENS[j] for i, j in enumerate(A.keyed_permutation(len(XLENS)))}


def observed_map(data):
    with np.load(io.BytesIO(data)) as z:
        return {
            int(k.split("_")[1]): int(len(np.asarray(z[k])))
            for k in z.files if k.startswith("table_") and k.endswith("_x")
        }


def locator(A, record):
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


def permute_A4(A, B, data):
    a = load_npz(data)
    ids = sorted(int(k.split("_")[1]) for k in a if k.startswith("table_") and k.endswith("_x"))
    lens = {i: int(len(a[f"table_{i}_x"])) for i in ids}
    if tuple(sorted(lens.values())) != XLENS or len(set(lens.values())) != len(lens):
        raise RuntimeError("unexpected/non-unique x-grid profile")
    by_len = {n: i for i, n in lens.items()}
    pub_old = {p: by_len[XLENS[j]] for p, j in enumerate(A.keyed_permutation(len(XLENS)))}
    old_pub = {o: p for p, o in pub_old.items()}
    out = {}
    for p, o in pub_old.items():
        out[f"table_{p}_x"] = a[f"table_{o}_x"]
        out[f"table_{p}_y"] = a[f"table_{o}_y"]
    B2 = json.loads(json.dumps(B))
    for t in B2["tables"]: t["table_id"] = old_pub[int(t["table_id"])]
    B2["tables"] = sorted(B2["tables"], key=lambda t: int(t["table_id"]))
    return B2, save_npz(out)


def build(V20, engine, seed, payload_bytes, channels):
    V18, V3 = V20["V18"], V20["V3"]
    A = A4(V3)
    B0, b0, _ = V18["generate_B_b"](engine, payload_bytes, channels, seed)
    B1, b = permute_A4(A, B0, b0)
    payload = engine["synthetic_payload"](payload_bytes)
    if hashlib.sha256(payload).hexdigest() != B1["payload_sha256"]: raise RuntimeError("payload hash mismatch")
    parity, lengths = V20["rs_parity"](payload)
    B = V20["add_v20_manifest"](B1, payload_bytes, lengths)
    return {"A": A, "B": B, "b": b, "c": V20["make_c_v20"](A, B, b, parity), "payload": payload}


def first_table(B):
    return min(B["tables"], key=lambda t: (int(t["payload_bit_offset"]), int(t["table_id"])))


def drop_table(data, tid):
    a = load_npz(data); a.pop(f"table_{tid}_x"); a.pop(f"table_{tid}_y"); return save_npz(a)


def truncate_tail(data, table):
    a = load_npz(data); tid, n = int(table["table_id"]), int(table["points_per_block"])
    k = f"table_{tid}_y"; y = a[k]
    if y.shape[0] <= n: raise RuntimeError("no removable tail segment")
    a[k] = y[:-n, :].copy(); return save_npz(a)


def record_with_b(A, c, data):
    r = dict(c); r[A.field_payload] = base64.b64encode(data).decode(); return r


def corpus(V20, A, seed, size):
    rng = np.random.default_rng(CORPUS_DOMAIN + seed)
    target = int(rng.integers(0, size)); others = [i for i in range(size) if i != target]
    near_n = int(round((size - 1) * NEAR)); near = set(int(x) for x in rng.choice(others, size=near_n, replace=False))
    scores = {i: locator(A, V20["make_d_descriptor"](A, rng, i in near)) for i in others}
    return target, scores


def rank(target, decoys, score):
    vals = [score if i == target else decoys[i] for i in range(len(decoys) + 1)]
    order = np.argsort(-np.asarray(vals), kind="stable")
    return int(next(j + 1 for j, i in enumerate(order) if int(i) == target))


def decode_erasure(engine, B_bytes, data):
    B = json.loads(B_bytes.decode()); nbits = int(B["payload_bit_length"])
    bits = np.zeros(nbits, np.uint8); erased = np.zeros(nbits, bool); reports = []
    with np.load(io.BytesIO(data)) as z:
        for t in B["tables"]:
            tid, off, blen = int(t["table_id"]), int(t["payload_bit_offset"]), int(t["payload_bit_length"])
            end, key = off + blen, f"table_{tid}_y"
            if key not in z.files:
                erased[off:end] = True; reports.append({"table_id": tid, "status": "MISSING_TABLE", "erased_bits": blen}); continue
            pub = np.asarray(z[key], float); ch, block, segs = int(t["channels"]), int(t["points_per_block"]), int(t["segments"])
            if pub.ndim != 2 or pub.shape[1] != ch: raise RuntimeError("unsupported table shape")
            full = min(segs, int(pub.shape[0] // block)); valid = min(int(t["valid_codewords"]), full * ch)
            prefix = min(blen, valid * int(t["payload_symbols_per_codeword"]) * int(t["m"]))
            if prefix:
                tt = dict(t); tt["segments"], tt["valid_codewords"], tt["payload_bit_length"] = full, valid, prefix
                got = engine["decode_table"](pub[:full * block, :], tt); bits[off:off+prefix] = got[:prefix]
            if prefix < blen: erased[off+prefix:end] = True
            reports.append({"table_id": tid, "status": "COMPLETE" if prefix == blen else "TAIL_ERASURE", "decoded_prefix_bits": prefix, "erased_bits": blen-prefix})
    payload = engine["bits_to_bytes"](bits)[:int(B["payload_bytes"])]
    sha = hashlib.sha256(payload).hexdigest(); ok = hmac.compare_digest(sha, str(B["payload_sha256"]))
    erased_bytes = [i for i in range(len(payload)) if np.any(erased[i*8:(i+1)*8])]
    return payload, sha, ok, {"erased_bit_count": int(np.sum(erased)), "erased_byte_count": len(erased_bytes), "erased_byte_indices": erased_bytes, "tables": reports}


def open_candidate(V20, A, B_bytes, candidate, candidate_sha, direct_ok, record):
    try:
        rb = base64.b64decode(record[A.field_manifest], validate=True); masked = base64.b64decode(record[V20["FIELD_REPAIR"]], validate=True); tag = str(record[A.field_tag])
    except Exception: return {"accepted": False, "reason": "A_bootstrap_parse_failed"}
    if rb != B_bytes or not hmac.compare_digest(tag, V20["package_tag_v20"](A, rb, masked)):
        return {"accepted": False, "reason": "v20_envelope_integrity_failed"}
    B = json.loads(rb.decode()); parity = V20["decode_repair_field"](A, B, masked)
    if direct_ok: return {"accepted": True, "reason": "strict_verify_pass_no_repair", "repair_attempted": False, "repair_success": False, "corrected_shards": 0}
    try: repaired, corrected = V20["repair_payload"](B, candidate, parity)
    except Exception as e: return {"accepted": False, "reason": "v20_repair_failed", "detail": type(e).__name__, "repair_attempted": True, "repair_success": False}
    sha = hashlib.sha256(repaired).hexdigest(); ok = hmac.compare_digest(sha, str(B["payload_sha256"]))
    return {"accepted": ok, "reason": "strict_verify_pass_after_v20_repair" if ok else "v20_repaired_payload_hash_failed", "repair_attempted": True, "repair_success": ok, "corrected_shards": corrected}


def geometry(payload, candidate, B):
    errs = int(sum(a != b for a, b in zip(payload, candidate))); off = 0; shards = []
    for n in map(int, B["outer_reliability"]["shard_lengths"]):
        shards.append(int(sum(a != b for a, b in zip(payload[off:off+n], candidate[off:off+n])))); off += n
    return errs, shards, max(shards) if shards else 0


def run_one(V20, engine, built, seed, name, data, target, decoys):
    A, B = built["A"], built["B"]; rec = record_with_b(A, built["c"], data); score = locator(A, rec); rnk = rank(target, decoys, score)
    B_bytes = V20["serialize_B"](B)
    try: cand, sha, direct, er = decode_erasure(engine, B_bytes, data); derr = None
    except Exception as e: cand = sha = direct = er = None; derr = type(e).__name__
    opened = {"accepted": False, "reason": "candidate_decode_failed", "repair_attempted": False, "repair_success": False}; errs = shards = mx = None
    if cand is not None:
        errs, shards, mx = geometry(built["payload"], cand, B); opened = open_candidate(V20, A, B_bytes, cand, sha, direct, rec)
    return {"payload_seed": seed, "condition": name, "target_locator_score": score, "target_rank": rnk, "candidate_produced": cand is not None, "candidate_decode_error": derr, "direct_exact": direct, "erasure_report": er, "candidate_byte_errors": errs, "shard_byte_errors": shards, "max_shard_byte_errors": mx, "v20_accepted": bool(opened.get("accepted")), "v20_reason": opened.get("reason"), "repair_attempted": bool(opened.get("repair_attempted", False)), "repair_success": bool(opened.get("repair_success", False)), "corrected_shards": opened.get("corrected_shards")}


def summarize(rows):
    vals = lambda k: [r[k] for r in rows if r[k] is not None]
    erbits = [r["erasure_report"]["erased_bit_count"] for r in rows if r["erasure_report"]]
    erbytes = [r["erasure_report"]["erased_byte_count"] for r in rows if r["erasure_report"]]
    return {"runs": len(rows), "locator_score_1_runs": sum(r["target_locator_score"] == 1.0 for r in rows), "locator_score_median": float(np.median(vals("target_locator_score"))), "recall_at_100": float(np.mean([r["target_rank"] <= 100 for r in rows])), "median_target_rank": float(np.median(vals("target_rank"))), "max_target_rank": int(max(vals("target_rank"))), "candidate_produced_runs": sum(r["candidate_produced"] for r in rows), "direct_exact_runs": sum(r["direct_exact"] is True for r in rows), "v20_accepted_runs": sum(r["v20_accepted"] for r in rows), "repair_attempts": sum(r["repair_attempted"] for r in rows), "repair_successes": sum(r["repair_success"] for r in rows), "candidate_byte_errors_median": float(np.median(vals("candidate_byte_errors"))) if vals("candidate_byte_errors") else None, "candidate_byte_errors_max": max(vals("candidate_byte_errors"), default=None), "erased_bits_median": float(np.median(erbits)) if erbits else None, "erased_bytes_median": float(np.median(erbytes)) if erbytes else None, "max_shard_byte_errors_max": max(vals("max_shard_byte_errors"), default=None), "v20_reason_counts": dict(sorted(Counter(r["v20_reason"] for r in rows).items()))}


def md(result, path):
    lines = ["# Structural erasure v2 candidate", "", "Synthetic-only frozen experiment; A-v4/decoder-v2 are candidates, V20 is unchanged.", "", f"Execution gate: **{'PASS' if result['execution_gate_pass'] else 'FAIL'}**", "", "| condition | locator median | R@100 | candidate | direct | V20 accept | repairs | median byte errors |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k, s in result["summary"].items():
        e = "-" if s["candidate_byte_errors_median"] is None else f"{s['candidate_byte_errors_median']:.1f}"; lines.append(f"| {k} | {s['locator_score_median']:.4f} | {s['recall_at_100']:.3f} | {s['candidate_produced_runs']}/{s['runs']} | {s['direct_exact_runs']}/{s['runs']} | {s['v20_accepted_runs']}/{s['runs']} | {s['repair_successes']}/{s['repair_attempts']} | {e} |")
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser(); p.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18_deterministic.py")); p.add_argument("--v20", type=Path, default=Path("protocol/real-package-v20.py")); p.add_argument("--seeds", default=",".join(map(str, range(1101,1125)))); p.add_argument("--payload-bytes", type=int, default=512); p.add_argument("--channels", type=int, default=2); p.add_argument("--corpus-size", type=int, default=2000); p.add_argument("--out", type=Path, default=Path("structural-erasure-v2.json")); p.add_argument("--summary-out", type=Path, default=Path("structural-erasure-v2.md")); a = p.parse_args()
    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]; V20 = runpy.run_path(str(a.v20)); engine = V20["load_engine"](a.engine); rows = []; profiles = []; meta = []
    for seed in seeds:
        built = build(V20, engine, seed, a.payload_bytes, a.channels); A = built["A"]; profiles.append({"payload_seed": seed, "exact": expected_map(A) == observed_map(built["b"])}); t = first_table(built["B"]); tid = int(t["table_id"]); meta.append({"payload_seed": seed, "public_table_id": tid, "payload_bit_offset": int(t["payload_bit_offset"]), "payload_bit_length": int(t["payload_bit_length"]), "segments": int(t["segments"]), "q": int(t["q"])}); target, decoys = corpus(V20, A, seed, a.corpus_size)
        for name, data in [("clean", built["b"]), ("drop_logical_first_table", drop_table(built["b"], tid)), ("truncate_one_tail_segment", truncate_tail(built["b"], t))]: rows.append(run_one(V20, engine, built, seed, name, data, target, decoys))
    summary = {k: summarize([r for r in rows if r["condition"] == k]) for k in sorted({r["condition"] for r in rows})}; clean = [r for r in rows if r["condition"] == "clean"]
    gate = all(x["exact"] for x in profiles) and all(r["target_locator_score"] == 1.0 and r["target_rank"] == 1 and r["candidate_produced"] and r["direct_exact"] is True and r["v20_accepted"] and not r["repair_attempted"] for r in clean)
    result = {"version": "structural-erasure-v2-candidate", "scope": "synthetic-only", "status": "EXECUTION_GATE_PASS" if gate else "EXECUTION_GATE_FAIL", "execution_gate_definition": "clean controls + A-v4 profile exactness only; damaged outcomes never gate", "execution_gate_pass": gate, "frozen_contract": {"engine": str(a.engine), "v20": str(a.v20), "seeds": seeds, "payload_bytes": a.payload_bytes, "channels": a.channels, "corpus_size": a.corpus_size, "near_decoy_fraction": NEAR, "A_candidate": {"version": "A-v4-erasure-xlen", "label": "public x-grid length", "expected_x_lengths": list(XLENS), "B_parsed_during_ranking": False}, "decoder_candidate": {"version": "decoder-v2-prefix-erasure", "missing_table": "zero-fill declared payload interval", "tail_truncation": "decode complete prefix; zero-fill missing tail"}, "V20_geometry_unchanged": {"data_shard_bytes": V20["DATA_SHARD_BYTES"], "parity_bytes_per_shard": V20["PARITY_BYTES_PER_SHARD"], "byte_error_capacity_per_shard": V20["PARITY_BYTES_PER_SHARD"]//2}, "no_tuning": ["V18 q/delta unchanged", "V20 RS geometry/repair unchanged", "damaged outcomes are not acceptance criteria"]}, "profile_maps": profiles, "target_table_metadata": meta, "summary": summary, "runs": rows}
    a.out.write_text(json.dumps(result, indent=2), encoding="utf-8"); md(result, a.summary_out); print(json.dumps({"status": result["status"], "summary": summary}, indent=2));
    if not gate: raise SystemExit(2)

if __name__ == "__main__": main()
