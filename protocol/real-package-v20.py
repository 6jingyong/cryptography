#!/usr/bin/env python3
"""Bounded V20 outer-reliability wrapper around the current V18 carrier.

Synthetic-only. This is a protocol experiment, not a restoration of historical
V20 results.

V20 authenticates the per-package manifest B plus masked repair bytes r. Raw b
is intentionally excluded from the V20 envelope tag so post-seal numeric
publication transforms can still be decoded/repaired. Final acceptance requires
that the recovered payload hash exactly match the authenticated target in B.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import runpy
from pathlib import Path

from reedsolo import RSCodec, ReedSolomonError

HERE = Path(__file__).resolve().parent
V18 = runpy.run_path(str(HERE / "real-package-v18.py"))
V3 = V18["V3"]

FIELD_REPAIR = "r"
SCHEME = "rs-gf256-shard-v1"
DATA_SHARD_BYTES = 128
PARITY_BYTES_PER_SHARD = 8


def load_engine(path: Path):
    return V18["load_engine"](path)


def set_seed(engine: dict, seed: int):
    return V18["set_seed"](engine, seed)


def serialize_B(B: dict) -> bytes:
    return V3["serialize_B"](B)


def rs_parity(payload: bytes, shard_bytes: int = DATA_SHARD_BYTES, parity_bytes: int = PARITY_BYTES_PER_SHARD):
    codec = RSCodec(parity_bytes)
    parts = []
    lengths = []
    for start in range(0, len(payload), shard_bytes):
        shard = payload[start:start+shard_bytes]
        encoded = bytes(codec.encode(shard))
        parts.append(encoded[-parity_bytes:])
        lengths.append(len(shard))
    return b"".join(parts), lengths


def repair_keystream(A, payload_sha256: str, n: int) -> bytes:
    ctx = payload_sha256.encode("ascii")
    out = bytearray()
    counter = 0
    while len(out) < n:
        out.extend(hmac.new(
            A.root_key,
            b"v20-repair-mask|" + ctx + b"|" + counter.to_bytes(4, "big"),
            hashlib.sha256,
        ).digest())
        counter += 1
    return bytes(out[:n])


def mask_repair(A, payload_sha256: str, repair: bytes) -> bytes:
    ks = repair_keystream(A, payload_sha256, len(repair))
    return bytes(a ^ b for a, b in zip(repair, ks))


def package_tag_v20(A, B_bytes: bytes, masked_repair: bytes) -> str:
    return hmac.new(
        A.root_key,
        b"c-v20-logical|" + B_bytes + b"|" + masked_repair,
        hashlib.sha256,
    ).hexdigest()


def add_v20_manifest(B: dict, payload_bytes: int, shard_lengths: list[int]) -> dict:
    out = json.loads(json.dumps(B))
    out["outer_reliability"] = {
        "version": "v20-bounded-rs-v1",
        "scheme": SCHEME,
        "data_shard_bytes": DATA_SHARD_BYTES,
        "parity_bytes_per_shard": PARITY_BYTES_PER_SHARD,
        "shard_count": len(shard_lengths),
        "shard_lengths": shard_lengths,
        "payload_bytes": payload_bytes,
        "repair_field": FIELD_REPAIR,
        "repair_mask": "hmac-sha256-stream-A-v1",
        "integrity_mode": "authenticate-B-and-masked-r; final-authenticated-payload-hash",
        "raw_b_in_envelope_tag": False,
    }
    return out


def make_c_v20(A, B: dict, b_bytes: bytes, repair_plain: bytes) -> dict:
    B_bytes = serialize_B(B)
    masked = mask_repair(A, B["payload_sha256"], repair_plain)
    return {
        "record_type": "synthetic-v20-package",
        A.field_manifest: base64.b64encode(B_bytes).decode(),
        A.field_payload: base64.b64encode(b_bytes).decode(),
        FIELD_REPAIR: base64.b64encode(masked).decode(),
        A.field_tag: package_tag_v20(A, B_bytes, masked),
    }


def build_v20_package(engine: dict, payload_seed: int, payload_bytes: int = 512, channels: int = 2):
    A = V3["default_A"]()
    B0, b0, engine_result = V18["generate_B_b"](engine, payload_bytes, channels, payload_seed)
    B1, b = V3["permute_package_to_A"](A, B0, b0)
    payload = engine["synthetic_payload"](payload_bytes)
    sha = hashlib.sha256(payload).hexdigest()
    if sha != B1["payload_sha256"]:
        raise RuntimeError("payload hash mismatch while building V20 package")
    parity, shard_lengths = rs_parity(payload)
    B = add_v20_manifest(B1, payload_bytes, shard_lengths)
    c = make_c_v20(A, B, b, parity)
    return {
        "A": A,
        "B": B,
        "b": b,
        "c": c,
        "payload": payload,
        "repair_plain": parity,
        "engine_result": engine_result,
    }


def decode_repair_field(A, B: dict, masked_repair: bytes) -> bytes:
    return mask_repair(A, B["payload_sha256"], masked_repair)


def repair_payload(B: dict, candidate_payload: bytes, repair_plain: bytes):
    cfg = B.get("outer_reliability") or {}
    if cfg.get("scheme") != SCHEME:
        raise RuntimeError("unsupported outer reliability scheme")
    shard_lengths = [int(x) for x in cfg["shard_lengths"]]
    parity_bytes = int(cfg["parity_bytes_per_shard"])
    if sum(shard_lengths) != len(candidate_payload):
        raise RuntimeError("candidate payload length does not match V20 manifest")
    if len(repair_plain) != len(shard_lengths) * parity_bytes:
        raise RuntimeError("repair parity length mismatch")

    codec = RSCodec(parity_bytes)
    repaired_parts = []
    corrected_shards = 0
    offset = 0
    for i, n in enumerate(shard_lengths):
        shard = candidate_payload[offset:offset+n]
        parity = repair_plain[i*parity_bytes:(i+1)*parity_bytes]
        codeword = shard + parity
        try:
            decoded_result = codec.decode(codeword)
        except ReedSolomonError as exc:
            raise RuntimeError("rs_decode_failed") from exc
        decoded = bytes(decoded_result[0] if isinstance(decoded_result, tuple) else decoded_result)
        if len(decoded) != n:
            decoded = decoded[:n]
        if decoded != shard:
            corrected_shards += 1
        repaired_parts.append(decoded)
        offset += n
    return b"".join(repaired_parts), corrected_shards


def try_open_v20(A, engine: dict, record: dict):
    if record.get("invalid_outer_tag"):
        return {"accepted": False, "reason": "v20_envelope_integrity_failed"}
    try:
        B_bytes = base64.b64decode(record[A.field_manifest], validate=True)
        b_bytes = base64.b64decode(record[A.field_payload], validate=True)
        masked_repair = base64.b64decode(record[FIELD_REPAIR], validate=True)
        tag = str(record[A.field_tag])
    except Exception:
        return {"accepted": False, "reason": "A_bootstrap_parse_failed"}

    if not hmac.compare_digest(tag, package_tag_v20(A, B_bytes, masked_repair)):
        return {"accepted": False, "reason": "v20_envelope_integrity_failed"}

    try:
        B = json.loads(B_bytes.decode())
        repair_plain = decode_repair_field(A, B, masked_repair)
    except Exception as exc:
        return {"accepted": False, "reason": "v20_envelope_parse_failed", "detail": type(exc).__name__}

    try:
        candidate, candidate_sha, direct_ok = V18["decode_package"](engine, B_bytes, b_bytes)
    except Exception as exc:
        return {"accepted": False, "reason": "B_or_b_decode_failed_before_repair", "detail": type(exc).__name__}

    if direct_ok:
        return {
            "accepted": True,
            "reason": "strict_verify_pass_no_repair",
            "payload": candidate,
            "payload_sha256": candidate_sha,
            "repair_attempted": False,
            "repair_success": False,
            "corrected_shards": 0,
        }

    try:
        repaired, corrected_shards = repair_payload(B, candidate, repair_plain)
    except Exception as exc:
        return {
            "accepted": False,
            "reason": "v20_repair_failed",
            "detail": type(exc).__name__,
            "repair_attempted": True,
            "repair_success": False,
            "candidate_sha256": candidate_sha,
        }

    repaired_sha = hashlib.sha256(repaired).hexdigest()
    ok = hmac.compare_digest(repaired_sha, str(B["payload_sha256"]))
    if not ok:
        return {
            "accepted": False,
            "reason": "v20_repaired_payload_hash_failed",
            "repair_attempted": True,
            "repair_success": False,
            "corrected_shards": corrected_shards,
            "candidate_sha256": candidate_sha,
            "repaired_sha256": repaired_sha,
        }
    return {
        "accepted": True,
        "reason": "strict_verify_pass_after_v20_repair",
        "payload": repaired,
        "payload_sha256": repaired_sha,
        "repair_attempted": True,
        "repair_success": True,
        "corrected_shards": corrected_shards,
        "candidate_sha256": candidate_sha,
    }


def locator_score(A, record: dict) -> float:
    return V3["locator_score"](A, record)


def rank_candidates(A, corpus):
    return V3["rank_candidates"](A, corpus)


def make_d_descriptor(A, rng, near=False):
    return V3["make_d_descriptor"](A, rng, near)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--seed", type=int, default=701)
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    args = ap.parse_args()
    engine = load_engine(args.engine)
    built = build_v20_package(engine, args.seed, args.payload_bytes, args.channels)
    opened = try_open_v20(built["A"], engine, built["c"])
    print(json.dumps({
        "accepted": opened["accepted"],
        "reason": opened["reason"],
        "repair_attempted": opened.get("repair_attempted"),
        "parity_bytes": len(built["repair_plain"]),
        "payload_bytes": args.payload_bytes,
        "parity_overhead": len(built["repair_plain"]) / args.payload_bytes,
    }, indent=2))
    if not opened["accepted"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
