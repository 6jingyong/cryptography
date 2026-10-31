#!/usr/bin/env python3
"""
dual_codebook_pipeline_v14.py

Synthetic-only integration benchmark.

Pipeline:
  synthetic payload
    -> adaptive-q package encoder
    -> published numeric package + manifest
    -> structural fingerprint extraction
    -> keyed Top-K retrieval from a synthetic candidate corpus
    -> strict keyed verification
    -> actual package decoder
    -> SHA-256 equality check

The retrieval codebook is only a locator. It does not authenticate a package.
False positives are allowed and are rejected by the final verification stage.

This benchmark intentionally operates on synthetic/mock packages only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import shutil
from pathlib import Path

import numpy as np


def auth_tag(key: bytes, candidate_id: int, payload_sha: bytes) -> bytes:
    h = hashlib.blake2s(key=key, digest_size=16)
    h.update(int(candidate_id).to_bytes(8, "big"))
    h.update(payload_sha)
    return h.digest()


def corrupt_signature(sig, rate, alphabet, rng):
    out = np.asarray(sig, dtype=np.int16).copy()
    mask = rng.random(len(out)) < rate
    for i in np.where(mask)[0]:
        choices = np.arange(alphabet)
        choices = choices[choices != out[i]]
        out[i] = rng.choice(choices)
    return out


def near_decoy(sig, shared_fraction, alphabet, rng):
    out = rng.integers(0, alphabet, size=len(sig), dtype=np.int16)
    k = int(round(shared_fraction * len(sig)))
    if k:
        idx = rng.choice(len(sig), size=k, replace=False)
        out[idx] = sig[idx]
    return out


def locator_trials(
    expected,
    alphabet,
    *,
    seeds=200,
    corpus_size=10_000,
    extraction_noise=0.20,
    near_decoy_fraction=0.01,
    near_shared_fraction=0.50,
):
    expected = np.asarray(expected, dtype=np.int16)
    ranks = []
    target_scores = []
    max_decoy_scores = []

    for seed_i in range(seeds):
        rng = np.random.default_rng(14000 + seed_i)
        target_id = int(rng.integers(0, corpus_size))

        sigs = rng.integers(
            0, alphabet, size=(corpus_size, len(expected)), dtype=np.int16
        )

        non_targets = np.asarray(
            [i for i in range(corpus_size) if i != target_id], dtype=int
        )
        near_n = int(round((corpus_size - 1) * near_decoy_fraction))
        near_ids = rng.choice(non_targets, size=near_n, replace=False)
        for pid in near_ids:
            sigs[pid] = near_decoy(
                expected, near_shared_fraction, alphabet, rng
            )

        sigs[target_id] = corrupt_signature(
            expected, extraction_noise, alphabet, rng
        )

        scores = np.mean(sigs == expected[None, :], axis=1)
        order = np.argsort(-scores, kind="stable")
        rank = int(np.where(order == target_id)[0][0] + 1)

        ranks.append(rank)
        target_scores.append(float(scores[target_id]))
        max_decoy_scores.append(
            float(np.max(np.delete(scores, target_id)))
        )

    ranks = np.asarray(ranks)

    return {
        "alphabet": int(alphabet),
        "fingerprint_positions": int(len(expected)),
        "seeds": int(seeds),
        "corpus_size": int(corpus_size),
        "extraction_noise": float(extraction_noise),
        "near_decoy_fraction": float(near_decoy_fraction),
        "near_decoy_shared_positions": float(near_shared_fraction),
        "p_target_top1": float(np.mean(ranks <= 1)),
        "p_target_top5": float(np.mean(ranks <= 5)),
        "p_target_top10": float(np.mean(ranks <= 10)),
        "p_target_top20": float(np.mean(ranks <= 20)),
        "p_target_top50": float(np.mean(ranks <= 50)),
        "p_target_top100": float(np.mean(ranks <= 100)),
        "median_rank": float(np.median(ranks)),
        "p90_rank": float(np.percentile(ranks, 90)),
        "p99_rank": float(np.percentile(ranks, 99)),
        "max_rank": int(np.max(ranks)),
        "mean_verification_attempts": float(np.mean(ranks)),
        "mean_target_similarity": float(np.mean(target_scores)),
        "mean_max_decoy_similarity": float(np.mean(max_decoy_scores)),
    }


def run(
    adaptive_source: Path,
    out_dir: Path,
    payload_bytes=131_072,
    channels=16,
):
    ns = runpy.run_path(str(adaptive_source))
    run_package = ns["run_package"]
    decode_table = ns["decode_table"]
    bits_to_bytes = ns["bits_to_bytes"]

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    run_package(
        payload_bytes=payload_bytes,
        channels=channels,
        out_dir=out_dir,
    )

    manifest_path = out_dir / "manifest_adaptive_q_v12.json"
    package_path = out_dir / "published_adaptive_q_v12.npz"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    loaded = np.load(package_path)

    recovered_bits = np.zeros(
        manifest["payload_bit_length"], dtype=np.uint8
    )
    for table in manifest["tables"]:
        rb = decode_table(loaded[f"table_{table['table_id']}_y"], table)
        offset = int(table["payload_bit_offset"])
        recovered_bits[offset:offset+len(rb)] = rb

    decoded = bits_to_bytes(recovered_bits)[:manifest["payload_bytes"]]
    decoded_sha = hashlib.sha256(decoded).hexdigest()

    q_to_id = {8: 0, 16: 1, 32: 2}
    q_only = np.asarray(
        [q_to_id[int(t["q"])] for t in manifest["tables"]],
        dtype=np.int16,
    )

    families = sorted({t["family"] for t in manifest["tables"]})
    vocab = [(family, q) for family in families for q in (8, 16, 32)]
    vocab_to_id = {v: i for i, v in enumerate(vocab)}
    joint = np.asarray(
        [
            vocab_to_id[(t["family"], int(t["q"]))]
            for t in manifest["tables"]
        ],
        dtype=np.int16,
    )

    q_locator = locator_trials(q_only, alphabet=3)
    joint_locator = locator_trials(joint, alphabet=len(vocab))

    shared_key = hashlib.sha256(
        b"synthetic-v14-shared-locator-key"
    ).digest()
    payload_sha_bytes = bytes.fromhex(manifest["payload_sha256"])

    rng = np.random.default_rng(20261101)
    corpus = 10_000
    target_id = int(rng.integers(0, corpus))

    sigs = rng.integers(
        0, len(vocab), size=(corpus, len(joint)), dtype=np.int16
    )
    non_targets = np.asarray(
        [i for i in range(corpus) if i != target_id], dtype=int
    )
    near_ids = rng.choice(
        non_targets, size=int(round((corpus-1)*0.01)), replace=False
    )
    for pid in near_ids:
        sigs[pid] = near_decoy(joint, 0.50, len(vocab), rng)

    sigs[target_id] = corrupt_signature(
        joint, 0.20, len(vocab), rng
    )
    scores = np.mean(sigs == joint[None, :], axis=1)
    order = np.argsort(-scores, kind="stable")

    target_tag = auth_tag(
        shared_key, target_id, payload_sha_bytes
    )
    attempts = 0
    accepted_id = None

    for pid in order:
        pid = int(pid)
        attempts += 1

        if pid == target_id:
            candidate_sha = payload_sha_bytes
            candidate_tag = target_tag
        else:
            candidate_sha = hashlib.sha256(
                f"synthetic-decoy-{pid}".encode()
            ).digest()
            wrong_key = hashlib.sha256(
                f"wrong-key-{pid}".encode()
            ).digest()
            candidate_tag = auth_tag(
                wrong_key, pid, candidate_sha
            )

        if auth_tag(
            shared_key, pid, candidate_sha
        ) == candidate_tag:
            accepted_id = pid
            break

    result = {
        "scope": "synthetic-only dual-codebook integration",
        "actual_target_package": {
            "payload_bytes": manifest["payload_bytes"],
            "payload_sha256": manifest["payload_sha256"],
            "decoder_sha256": decoded_sha,
            "exact_decode":
                decoded_sha == manifest["payload_sha256"],
            "tables": len(manifest["tables"]),
            "q_schedule":
                [int(t["q"]) for t in manifest["tables"]],
            "family_schedule":
                [t["family"] for t in manifest["tables"]],
        },
        "locator_q_only": q_locator,
        "locator_joint_family_q": joint_locator,
        "strict_verification": {
            "representative_target_rank":
                int(np.where(order == target_id)[0][0] + 1),
            "verification_attempts_until_accept": attempts,
            "accepted_is_target": accepted_id == target_id,
            "actual_target_decoder_sha256_match":
                decoded_sha == manifest["payload_sha256"],
        },
    }

    result_path = out_dir / "dual_codebook_pipeline_v14_results.json"
    result_path.write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def main():
    default_adaptive = Path(__file__).resolve().parent / "adaptive_q_package_v12.py"
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--adaptive-source",
        type=Path,
        default=default_adaptive,
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("v14_out"),
    )
    ap.add_argument("--payload-bytes", type=int, default=131_072)
    ap.add_argument("--channels", type=int, default=16)
    args = ap.parse_args()

    result = run(
        args.adaptive_source,
        args.out_dir,
        args.payload_bytes,
        args.channels,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
