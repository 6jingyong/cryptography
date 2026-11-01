#!/usr/bin/env python3
"""
Acceptance tests for Protocol Harness v2 with a real synthetic V12 package.

Synthetic-only.
"""

from __future__ import annotations

import base64
import copy
import json
import runpy
from pathlib import Path

import numpy as np


def main():
    repo_root = Path(__file__).resolve().parents[1]
    harness = runpy.run_path(
        str(repo_root / "protocol" / "real-package-v2.py")
    )
    engine = harness["load_engine"](
        repo_root / "src" / "adaptive_q_package_v12.py"
    )
    A = harness["default_A"]()
    rng = np.random.default_rng(424242)

    B, B_bytes, b_bytes, _ = harness["generate_real_B_b"](
        engine,
        payload_bytes=1024,
        channels=4,
    )
    c = harness["make_c"](
        A,
        B_bytes,
        b_bytes,
        rng,
        erase_rate=0.25,
        substitute_rate=0.10,
    )

    tests = []

    opened = harness["try_open"](
        A, engine, c
    )
    tests.append({
        "test": "real_v12_direct_open",
        "pass": bool(
            opened["accepted"]
            and opened["payload_sha256"]
            == B["payload_sha256"]
        ),
        "observed": opened["reason"],
    })

    c_bad_B = copy.deepcopy(c)
    raw = bytearray(base64.b64decode(
        c_bad_B[A.field_manifest]
    ))
    raw[len(raw)//2] ^= 1
    c_bad_B[A.field_manifest] = base64.b64encode(
        bytes(raw)
    ).decode()
    opened = harness["try_open"](
        A, engine, c_bad_B
    )
    tests.append({
        "test": "corrupt_real_B",
        "pass": opened["reason"] == "c_outer_integrity_failed",
        "observed": opened["reason"],
    })

    c_bad_b = copy.deepcopy(c)
    raw = bytearray(base64.b64decode(
        c_bad_b[A.field_payload]
    ))
    raw[len(raw)//2] ^= 1
    c_bad_b[A.field_payload] = base64.b64encode(
        bytes(raw)
    ).decode()
    opened = harness["try_open"](
        A, engine, c_bad_b
    )
    tests.append({
        "test": "corrupt_real_b",
        "pass": opened["reason"] == "c_outer_integrity_failed",
        "observed": opened["reason"],
    })

    decoy = harness["make_d"](
        A,
        rng,
        near=False,
    )
    decoy["structure"] = copy.deepcopy(
        c["structure"]
    )
    corpus = [decoy, c]
    for _ in range(300):
        corpus.append(
            harness["make_d"](
                A,
                rng,
                near=False,
            )
        )

    received = harness["receive"](
        A,
        engine,
        corpus,
        top_k=20,
    )
    tests.append({
        "test": "real_package_false_positive_then_verify",
        "pass": bool(
            received.get("accepted")
            and received.get("rank", 0) >= 2
            and received["attempts"][0]["accepted"] is False
            and received["payload_sha256"] == B["payload_sha256"]
        ),
        "accepted_rank": received.get("rank"),
        "attempts": received.get("attempts", [])[:3],
    })

    A_bad = harness["RootCodebookA"](
        version="A-wrong",
        root_key_hex="00"*32,
        fingerprint_length=A.fingerprint_length,
        fingerprint_alphabet=A.fingerprint_alphabet,
        field_manifest=A.field_manifest,
        field_payload=A.field_payload,
        field_tag=A.field_tag,
        manifest_format=A.manifest_format,
        payload_format=A.payload_format,
    )
    opened = harness["try_open"](
        A_bad,
        engine,
        c,
    )
    tests.append({
        "test": "wrong_A_real_package",
        "pass": not opened["accepted"],
        "observed": opened["reason"],
    })

    result = {
        "scope": "synthetic-only V12 protocol acceptance",
        "all_pass": all(t["pass"] for t in tests),
        "real_B_manifest_bytes": len(B_bytes),
        "real_b_npz_bytes": len(b_bytes),
        "payload_sha256": B["payload_sha256"],
        "tests": tests,
    }

    out = repo_root / "results" / "protocol-real-package-v2-tests-result.json"
    out.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
