#!/usr/bin/env python3
"""
Protocol Harness v3 — actual-package structural fingerprint.

Synthetic-only.

Changes from v2:
- A no longer relies on an extra synthetic 32-slot fingerprint attached to c.
- The locator fingerprint is derived from PUBLIC structure of the published V12
  numeric package itself.
- A defines a keyed ordering rule over canonical public table classes.
- B remains the per-package manifest and contains concrete decoder settings.
- Optional payload_seed monkey-patches the benchmark engine's synthetic payload
  generator before each full encode, enabling true multi-seed re-encoding
  without changing V12 carrier code.

Current public table class:
    (numeric morphology class, local x-grid length)

The class is extracted from the NPZ only. No B field is used for locator
scoring.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import io
import json
import math
import runpy
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class RootCodebookA:
    version: str
    root_key_hex: str
    table_profile: str
    expected_table_count: int
    field_manifest: str
    field_payload: str
    field_tag: str

    @property
    def root_key(self):
        return bytes.fromhex(self.root_key_hex)

    def keyed_permutation(self, n: int) -> list[int]:
        keyed = []
        for i in range(n):
            digest = hmac.new(
                self.root_key,
                f"public-table-position-{i}".encode(),
                hashlib.sha256,
            ).digest()
            keyed.append((digest, i))
        return [i for _, i in sorted(keyed)]


def default_A():
    return RootCodebookA(
        version="A-v3-public-structure",
        root_key_hex=hashlib.sha256(
            b"synthetic-root-A-v3-public-structure"
        ).hexdigest(),
        table_profile="v12-12table-morphology-xlen-v1",
        expected_table_count=12,
        field_manifest="m",
        field_payload="p",
        field_tag="t",
    )


def load_engine(engine_path: Path):
    ns = runpy.run_path(str(engine_path))
    required = ["run_package", "decode_table", "bits_to_bytes"]
    missing = [x for x in required if x not in ns]
    if missing:
        raise RuntimeError(f"engine missing: {missing}")
    return ns


def set_payload_seed(engine: dict, seed: int):
    seed_bytes = int(seed).to_bytes(8, "big", signed=False)

    def seeded_payload(nbytes: int):
        return hashlib.shake_256(
            b"adaptive-q-v12-synthetic-seeded|" + seed_bytes
        ).digest(nbytes)

    # runpy may return a mapping that is not the exact function globals object.
    # Patch the callable's real global namespace explicitly.
    engine["synthetic_payload"] = seeded_payload
    engine["run_package"].__globals__["synthetic_payload"] = seeded_payload


def linear_r2(x, y):
    p = np.polyfit(x, y, 1)
    pred = np.polyval(p, x)
    den = float(np.sum((y - np.mean(y))**2)) + 1e-12
    return 1.0 - float(np.sum((y-pred)**2)) / den


def extrema_count(y):
    y = np.asarray(y, float)
    if len(y) < 7:
        return 0
    ys = np.convolve(y, np.ones(3)/3.0, mode="same")
    d = np.diff(ys)
    threshold = 0.02 * (float(np.ptp(ys)) + 1e-12)
    sign = np.sign(np.where(np.abs(d) >= threshold, d, 0.0))
    for i in range(1, len(sign)):
        if sign[i] == 0:
            sign[i] = sign[i-1]
    nz = sign[sign != 0]
    return 0 if len(nz) < 2 else int(np.sum(nz[1:] != nz[:-1]))


def public_morphology(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    turns = extrema_count(y)
    r2 = linear_r2(x, y)
    imax = int(np.argmax(y))
    if r2 >= 0.97:
        return "linear"
    if turns >= 2:
        return "periodic"
    if 1 < imax < len(y)-2:
        edge = 0.5*(y[0]+y[-1])
        if (y[imax]-edge) >= 0.55*(float(np.ptp(y))+1e-12):
            return "peak"
    return "saturating"


def public_table_classes_from_npz_bytes(b_bytes: bytes):
    z = np.load(io.BytesIO(b_bytes))
    ids = sorted({
        int(name.split("_")[1])
        for name in z.files
        if name.startswith("table_") and name.endswith("_x")
    })
    out = []
    for tid in ids:
        x = np.asarray(z[f"table_{tid}_x"], float)
        y = np.asarray(z[f"table_{tid}_y"], float)
        n = len(x)
        visible = y[:n, 0]
        out.append({
            "public_id": tid,
            "class": [public_morphology(x, visible), int(n)],
            "rows": int(y.shape[0]),
            "channels": int(y.shape[1]),
        })
    return out


def fingerprint_sequence_from_public_package(A, b_bytes):
    tables = public_table_classes_from_npz_bytes(b_bytes)
    if len(tables) != A.expected_table_count:
        return None
    classes = [tuple(t["class"]) for t in tables]
    if len(set(classes)) != len(classes):
        return None
    canonical = sorted(classes)
    rank = {cls: i for i, cls in enumerate(canonical)}
    return [rank[cls] for cls in classes]


def expected_sequence_for_candidate(A, b_bytes):
    tables = public_table_classes_from_npz_bytes(b_bytes)
    if len(tables) != A.expected_table_count:
        return None
    classes = [tuple(t["class"]) for t in tables]
    if len(set(classes)) != len(classes):
        return None
    return A.keyed_permutation(len(classes))


def structural_score(A, b_bytes):
    actual = fingerprint_sequence_from_public_package(A, b_bytes)
    expected = expected_sequence_for_candidate(A, b_bytes)
    if actual is None or expected is None:
        return 0.0
    return float(np.mean(np.asarray(actual) == np.asarray(expected)))


def permute_package_to_A(A, B: dict, b_bytes: bytes):
    """Renumber public table IDs so public NPZ structure follows A's keyed order."""
    z = np.load(io.BytesIO(b_bytes))
    old = public_table_classes_from_npz_bytes(b_bytes)
    classes = [tuple(x["class"]) for x in old]
    if len(set(classes)) != len(classes):
        raise RuntimeError("public table classes are not unique")
    canonical = sorted(classes)
    class_to_old = {tuple(x["class"]): x["public_id"] for x in old}
    desired = A.keyed_permutation(len(canonical))
    pub_to_old = {
        pub_id: class_to_old[canonical[canon_idx]]
        for pub_id, canon_idx in enumerate(desired)
    }
    old_to_pub = {old_id: pub_id for pub_id, old_id in pub_to_old.items()}
    arrays = {}
    for pub_id, old_id in pub_to_old.items():
        arrays[f"table_{pub_id}_x"] = z[f"table_{old_id}_x"]
        arrays[f"table_{pub_id}_y"] = z[f"table_{old_id}_y"]
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    new_b = buf.getvalue()
    new_B = json.loads(json.dumps(B))
    for table in new_B["tables"]:
        table["table_id"] = old_to_pub[int(table["table_id"])]
    new_B["tables"] = sorted(new_B["tables"], key=lambda t: int(t["table_id"]))
    return new_B, new_b


def generate_real_B_b(engine, payload_bytes, channels, payload_seed):
    set_payload_seed(engine, payload_seed)
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        result = engine["run_package"](
            payload_bytes=payload_bytes,
            channels=channels,
            out_dir=out,
        )
        B = json.loads((out / "manifest_adaptive_q_v12.json").read_text())
        b = (out / "published_adaptive_q_v12.npz").read_bytes()
    return B, b, result


def serialize_B(B):
    return json.dumps(B, separators=(",", ":"), sort_keys=True).encode()


def package_tag(A, B_bytes, b_bytes):
    return hmac.new(
        A.root_key,
        b"c-v3|" + B_bytes + b"|" + b_bytes,
        hashlib.sha256,
    ).hexdigest()


def make_c(A, B, b_bytes):
    B_bytes = serialize_B(B)
    return {
        "record_type": "synthetic-v12-package",
        A.field_manifest: base64.b64encode(B_bytes).decode(),
        A.field_payload: base64.b64encode(b_bytes).decode(),
        A.field_tag: package_tag(A, B_bytes, b_bytes),
    }


def make_d_descriptor(A, rng, near=False):
    n = A.expected_table_count
    expected = A.keyed_permutation(n)
    seq = list(rng.permutation(n))
    if near:
        preserve = set(int(x) for x in rng.choice(n, size=n//2, replace=False))
        remaining_pos = [i for i in range(n) if i not in preserve]
        remaining_vals = [expected[i] for i in remaining_pos]
        rng.shuffle(remaining_vals)
        seq = expected.copy()
        for p, v in zip(remaining_pos, remaining_vals):
            seq[p] = v
    return {
        "record_type": "synthetic-public-structure-only",
        "public_rank_sequence": seq,
        "invalid_outer_tag": True,
    }


def locator_score(A, record):
    if "public_rank_sequence" in record:
        seq = record["public_rank_sequence"]
        expected = A.keyed_permutation(len(seq))
        return float(np.mean(np.asarray(seq) == np.asarray(expected)))
    try:
        b_bytes = base64.b64decode(record[A.field_payload], validate=True)
    except Exception:
        return 0.0
    return structural_score(A, b_bytes)


def rank_candidates(A, corpus):
    scores = [locator_score(A, r) for r in corpus]
    order = np.argsort(-np.asarray(scores), kind="stable")
    return [{"index": int(i), "score": float(scores[i])} for i in order]


def decode_v12(engine, B_bytes, b_bytes):
    B = json.loads(B_bytes.decode())
    z = np.load(io.BytesIO(b_bytes))
    bits = np.zeros(int(B["payload_bit_length"]), dtype=np.uint8)
    for table in B["tables"]:
        tid = int(table["table_id"])
        decoded = engine["decode_table"](z[f"table_{tid}_y"], table)
        off = int(table["payload_bit_offset"])
        bits[off:off+len(decoded)] = decoded
    payload = engine["bits_to_bytes"](bits)[:int(B["payload_bytes"])]
    sha = hashlib.sha256(payload).hexdigest()
    return payload, sha, sha == B["payload_sha256"]


def try_open(A, engine, record):
    if record.get("invalid_outer_tag"):
        return {"accepted": False, "reason": "c_outer_integrity_failed"}
    try:
        B_bytes = base64.b64decode(record[A.field_manifest], validate=True)
        b_bytes = base64.b64decode(record[A.field_payload], validate=True)
        tag = record[A.field_tag]
    except Exception:
        return {"accepted": False, "reason": "A_bootstrap_parse_failed"}
    if not hmac.compare_digest(str(tag), package_tag(A, B_bytes, b_bytes)):
        return {"accepted": False, "reason": "c_outer_integrity_failed"}
    try:
        payload, sha, ok = decode_v12(engine, B_bytes, b_bytes)
    except Exception as exc:
        return {"accepted": False, "reason": "B_or_b_decode_failed", "detail": type(exc).__name__}
    if not ok:
        return {"accepted": False, "reason": "a_final_verification_failed"}
    return {"accepted": True, "reason": "strict_verify_pass", "payload": payload, "payload_sha256": sha}


def run_seed(
    engine_path,
    payload_seed,
    payload_bytes=512,
    channels=2,
    corpus_size=2000,
    near_decoy_fraction=0.01,
    top_k=100,
):
    engine = load_engine(engine_path)
    A = default_A()
    rng = np.random.default_rng(5_000_000 + payload_seed)
    B, b0, engine_result = generate_real_B_b(engine, payload_bytes, channels, payload_seed)
    B2, b = permute_package_to_A(A, B, b0)
    c = make_c(A, B2, b)
    target_index = int(rng.integers(0, corpus_size))
    near_count = int(round((corpus_size-1)*near_decoy_fraction))
    candidates = [i for i in range(corpus_size) if i != target_index]
    near_ids = set(int(x) for x in rng.choice(candidates, size=near_count, replace=False))
    corpus = []
    for i in range(corpus_size):
        corpus.append(c if i == target_index else make_d_descriptor(A, rng, i in near_ids))
    ranked = rank_candidates(A, corpus)
    target_rank = next(i+1 for i, r in enumerate(ranked) if r["index"] == target_index)
    attempts = []
    accepted = None
    accepted_rank = None
    for rank, item in enumerate(ranked[:top_k], start=1):
        opened = try_open(A, engine, corpus[item["index"]])
        attempts.append({"rank": rank, "score": item["score"], "accepted": opened["accepted"], "reason": opened["reason"]})
        if opened["accepted"]:
            accepted = opened
            accepted_rank = rank
            break
    expected_sha = B2["payload_sha256"]
    exact = bool(accepted and accepted["payload_sha256"] == expected_sha)
    return {
        "payload_seed": int(payload_seed),
        "target_rank": int(target_rank),
        "accepted_rank": accepted_rank,
        "exact_recovery": exact,
        "target_locator_score": float(next(r["score"] for r in ranked if r["index"] == target_index)),
        "payload_sha256": expected_sha,
        "B_manifest_bytes": len(serialize_B(B2)),
        "b_npz_bytes": len(b),
        "public_table_classes": public_table_classes_from_npz_bytes(b),
        "engine": {
            "published_rows_total": engine_result.get("published_rows_total"),
            "gross_bits_per_numeric_value": engine_result.get("gross_bits_per_numeric_value"),
        },
        "attempt_count": len(attempts),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--corpus-size", type=int, default=2000)
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--out", type=Path, default=Path("protocol-v3-result.json"))
    args = ap.parse_args()
    result = run_seed(
        args.engine,
        args.seed,
        args.payload_bytes,
        args.channels,
        args.corpus_size,
        0.01,
        args.top_k,
    )
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "seed": result["payload_seed"],
        "target_rank": result["target_rank"],
        "accepted_rank": result["accepted_rank"],
        "exact_recovery": result["exact_recovery"],
        "target_locator_score": result["target_locator_score"],
    }, indent=2))
    if not result["exact_recovery"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
