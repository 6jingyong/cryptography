#!/usr/bin/env python3
"""Frozen residual-model falsification matrix for rebuilt V18.

Synthetic-only.  This harness intentionally leaves the V18 carrier and q/QIM
policy unchanged.  It replaces only the host residual generator, normalizes
challenge models to comparable free-subspace RMS energy, and then runs the
existing calibration and current-protocol paths.

Experimental failure is a valid result: this script writes the result and exits
normally unless the harness itself crashes.
"""
from __future__ import annotations

import argparse
import json
import math
import runpy
from pathlib import Path

import numpy as np

MODELS = [
    "iid_gaussian",
    "heteroscedastic_gaussian",
    "ar1_rho_0p85",
    "low_frequency_drift",
    "gaussian_sparse_outliers",
]

MODEL_PARAMETERS = {
    "iid_gaussian": {"kind": "pointwise iid Gaussian projected to free subspace"},
    "heteroscedastic_gaussian": {
        "kind": "pointwise heteroscedastic Gaussian projected to free subspace",
        "std_envelope_start": 0.5,
        "std_envelope_end": 1.5,
    },
    "ar1_rho_0p85": {
        "kind": "pointwise stationary AR(1)-like residual projected to free subspace",
        "rho": 0.85,
    },
    "low_frequency_drift": {
        "kind": "low-frequency sinusoidal/drift mixture projected to free subspace",
        "cycles": [0.35, 0.8, 1.2],
    },
    "gaussian_sparse_outliers": {
        "kind": "pointwise Gaussian plus sparse signed outliers projected to free subspace",
        "outlier_fraction": 0.02,
        "outlier_magnitude_sigma": 6.0,
    },
}


def load(path: Path):
    return runpy.run_path(str(path))


def table_map(engine: dict):
    out = {}
    for tid, (family, budget) in enumerate(engine["TABLE_BLUEPRINT"]):
        spec = engine["family_spec"](family)
        n = engine["table_n"](tid)
        x = engine["local_x"](n)
        B = engine["basis_for"](spec, x)
        U = engine["smooth_free_basis"](B)
        fd = int(U.shape[1])
        if fd in out:
            raise RuntimeError(f"free-dimension collision: {fd}")
        out[fd] = {
            "table_id": tid,
            "family": family,
            "budget": float(budget),
            "x": x,
            "U": U,
            "n": n,
        }
    return out


def smooth_reference_target_rms(sigma: float, n: int, free_dims: int, active_limit: int):
    active = min(int(active_limit), int(free_dims))
    decay = 1.0 / (1.0 + 0.18*np.arange(active, dtype=float))
    # Existing smooth model has independent coefficient variance
    # sigma^2 * decay^2 and U is orthonormal.  This is its expected signal RMS.
    return float(sigma * math.sqrt(float(np.sum(decay*decay)) / n))


def normalize_projected(coeff: np.ndarray, U: np.ndarray, target_rms: float):
    residual = coeff @ U.T
    rms = np.sqrt(np.mean(residual*residual, axis=1))
    if np.any(rms <= 1e-14):
        raise RuntimeError("challenge residual projected to near-zero free-subspace energy")
    return coeff * (target_rms / rms)[:, None]


def raw_residual(model: str, rng: np.random.Generator, slots: int, x: np.ndarray):
    n = len(x)
    if model == "iid_gaussian":
        return rng.normal(0.0, 1.0, size=(slots, n))

    if model == "heteroscedastic_gaussian":
        envelope = np.linspace(0.5, 1.5, n, dtype=float)
        return rng.normal(0.0, 1.0, size=(slots, n)) * envelope[None, :]

    if model == "ar1_rho_0p85":
        rho = 0.85
        eps = rng.normal(0.0, 1.0, size=(slots, n))
        out = np.empty_like(eps)
        out[:, 0] = eps[:, 0]
        innovation = math.sqrt(1.0-rho*rho)
        for j in range(1, n):
            out[:, j] = rho*out[:, j-1] + innovation*eps[:, j]
        return out

    if model == "low_frequency_drift":
        # Use fixed frequencies not matched to any one carrier macro family;
        # protected components are removed by projection below.
        u = (x-x.min()) / max(float(np.ptp(x)), 1e-12)
        basis = np.column_stack([
            np.sin(2*np.pi*0.35*u),
            np.cos(2*np.pi*0.35*u),
            np.sin(2*np.pi*0.8*u),
            np.cos(2*np.pi*0.8*u),
            np.sin(2*np.pi*1.2*u),
            u*u*u,
        ])
        a = rng.normal(0.0, 1.0, size=(slots, basis.shape[1]))
        return a @ basis.T

    if model == "gaussian_sparse_outliers":
        out = rng.normal(0.0, 1.0, size=(slots, n))
        mask = rng.random((slots, n)) < 0.02
        signs = np.where(rng.random((slots, n)) < 0.5, -1.0, 1.0)
        out = out + mask * signs * 6.0
        return out

    raise ValueError(model)


def make_host_generator(engine: dict, model: str):
    info = table_map(engine)
    active_limit = int(engine["HOST_ACTIVE_DIMS"])

    def generator(rng: np.random.Generator, slots: int, free_dims: int, sigma: float):
        meta = info[int(free_dims)]
        U = meta["U"]
        x = meta["x"]
        raw = raw_residual(model, rng, slots, x)
        coeff = raw @ U
        target = smooth_reference_target_rms(sigma, meta["n"], free_dims, active_limit)
        return normalize_projected(coeff, U, target)

    return generator


def patch_host(engine: dict, model: str):
    gen = make_host_generator(engine, model)
    # runpy mappings are not guaranteed to be the callable globals object.
    for name in ["run_package", "calibration", "choose_mode", "encode_table"]:
        if name in engine:
            engine[name].__globals__["host_coefficients"] = gen
    engine["host_coefficients"] = gen


def calibration_gate(engine: dict, model: str, channels: int):
    patch_host(engine, model)
    rows = []
    q_counts = {"2": 0, "4": 0}
    unsupported = []
    for tid, (family, budget) in enumerate(engine["TABLE_BLUEPRINT"]):
        chosen, trials = engine["choose_mode"](tid, family, budget, channels)
        row = {
            "table_id": tid,
            "family": family,
            "budget_nrmse": float(budget),
            "selected_q": None if chosen is None else int(chosen["q"]),
            "selected_host_adjustment_nrmse": None if chosen is None else float(chosen["host_adjustment_nrmse"]),
            "selected_exact_block_recovery": None if chosen is None else float(chosen["exact_block_recovery"]),
            "selected_adjustment_to_host_rms_ratio": None if chosen is None else float(chosen["adjustment_to_host_rms_ratio"]),
            "trials": [
                {
                    "q": int(t["q"]),
                    "feasible": bool(t["feasible"]),
                    "exact_block_recovery": float(t["exact_block_recovery"]),
                    "raw_symbol_error_rate": float(t["raw_symbol_error_rate"]),
                    "host_adjustment_nrmse": float(t["host_adjustment_nrmse"]),
                    "adjustment_to_host_rms_ratio": float(t["adjustment_to_host_rms_ratio"]),
                }
                for t in trials
            ],
        }
        rows.append(row)
        if chosen is None:
            unsupported.append(tid)
        else:
            q_counts[str(int(chosen["q"]))] += 1
    selected_nrmse = [r["selected_host_adjustment_nrmse"] for r in rows if r["selected_q"] is not None]
    ratios = [r["selected_adjustment_to_host_rms_ratio"] for r in rows if r["selected_q"] is not None]
    return {
        "pass": len(unsupported) == 0,
        "unsupported_table_ids": unsupported,
        "q_distribution": q_counts,
        "min_selected_host_adjustment_nrmse": None if not selected_nrmse else float(min(selected_nrmse)),
        "max_selected_host_adjustment_nrmse": None if not selected_nrmse else float(max(selected_nrmse)),
        "median_selected_adjustment_to_host_rms_ratio": None if not ratios else float(np.median(ratios)),
        "max_selected_adjustment_to_host_rms_ratio": None if not ratios else float(max(ratios)),
        "tables": rows,
    }


def patch_protocol_B_model(protocol: dict, model: str):
    original = protocol["generate_B_b"]
    metadata = MODEL_PARAMETERS[model]

    def wrapped(engine, payload_bytes, channels, seed):
        B, b, result = original(engine, payload_bytes, channels, seed)
        for table in B.get("tables", []):
            hm = dict(table.get("host_model", {}))
            hm["kind"] = model
            hm["matrix_definition"] = metadata
            hm["energy_normalization"] = "match expected free-subspace RMS of smooth reference at same table/step"
            table["host_model"] = hm
        return B, b, result

    protocol["run_seed_with_engine"].__globals__["generate_B_b"] = wrapped


def protocol_gate(protocol_path: Path, engine_path: Path, model: str, seeds, payload_bytes: int, channels: int, corpus_size: int, top_k: int):
    protocol = load(protocol_path)
    engine = protocol["load_engine"](engine_path)
    patch_host(engine, model)
    patch_protocol_B_model(protocol, model)
    runs = [
        protocol["run_seed_with_engine"](
            engine,
            payload_seed=int(seed),
            payload_bytes=payload_bytes,
            channels=channels,
            corpus_size=corpus_size,
            top_k=top_k,
        )
        for seed in seeds
    ]
    hashes = [r["payload_sha256"] for r in runs]
    summary = {
        "seeds": len(runs),
        "all_payload_hashes_unique": len(set(hashes)) == len(hashes),
        "exact_recovery_rate": float(np.mean([r["exact_recovery"] for r in runs])),
        "recall_at_20": float(np.mean([r["target_rank"] <= 20 for r in runs])),
        "recall_at_100": float(np.mean([r["target_rank"] <= 100 for r in runs])),
        "median_target_rank": float(np.median([r["target_rank"] for r in runs])),
        "max_target_rank": int(max(r["target_rank"] for r in runs)),
        "B_settings_present_all_runs": bool(all(r["B_contains_v18_settings"] for r in runs)),
        "median_adjustment_to_host_rms_ratio": float(np.median([r["median_adjustment_to_host_rms_ratio"] for r in runs])),
        "max_adjustment_to_host_rms_ratio": float(max(r["max_adjustment_to_host_rms_ratio"] for r in runs)),
    }
    passed = bool(
        summary["all_payload_hashes_unique"]
        and summary["exact_recovery_rate"] == 1.0
        and summary["recall_at_100"] == 1.0
        and summary["B_settings_present_all_runs"]
    )
    return {"pass": passed, "summary": summary, "runs": runs}


def run(args):
    engine_path = args.engine
    protocol_path = args.protocol
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    results = []
    for model in MODELS:
        engine = load(engine_path)
        cal = calibration_gate(engine, model, args.channels)
        row = {
            "model": model,
            "definition": MODEL_PARAMETERS[model],
            "calibration": cal,
            "protocol": None,
            "model_pass": False,
        }
        if cal["pass"]:
            prot = protocol_gate(
                protocol_path,
                engine_path,
                model,
                seeds,
                args.payload_bytes,
                args.channels,
                args.corpus_size,
                args.top_k,
            )
            row["protocol"] = prot
            row["model_pass"] = bool(prot["pass"])
        results.append(row)

    all_pass = bool(all(r["model_pass"] for r in results))
    passing = [r["model"] for r in results if r["model_pass"]]
    failing = [r["model"] for r in results if not r["model_pass"]]
    out = {
        "version": "v18-residual-model-matrix-v1",
        "scope": "synthetic-only",
        "frozen_plan": "results/v18-residual-matrix-plan.md",
        "configuration": {
            "models": MODELS,
            "seeds_per_supported_model": seeds,
            "payload_bytes": args.payload_bytes,
            "channels": args.channels,
            "candidate_corpus": args.corpus_size,
            "top_k": args.top_k,
            "carrier_policy": "unchanged q4-first/q2-fallback host-aware modulo-QIM",
            "energy_normalization": "free-subspace RMS matched to expected smooth-reference RMS at same table/step",
        },
        "general_v18_supported": all_pass,
        "classification": "GENERAL_V18_SUPPORTED" if all_pass else "MODEL_SPECIFIC_V18",
        "passing_models": passing,
        "failing_models": failing,
        "results": results,
    }
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "version": out["version"],
        "classification": out["classification"],
        "general_v18_supported": all_pass,
        "passing_models": passing,
        "failing_models": failing,
        "models": [
            {
                "model": r["model"],
                "calibration_pass": r["calibration"]["pass"],
                "q_distribution": r["calibration"]["q_distribution"],
                "max_nrmse": r["calibration"]["max_selected_host_adjustment_nrmse"],
                "protocol_pass": None if r["protocol"] is None else r["protocol"]["pass"],
                "recall_at_100": None if r["protocol"] is None else r["protocol"]["summary"]["recall_at_100"],
                "exact_recovery_rate": None if r["protocol"] is None else r["protocol"]["summary"]["exact_recovery_rate"],
            }
            for r in results
        ],
    }, indent=2))
    # Do not fail CI because a scientific hypothesis failed.  Harness crashes,
    # missing files, or Python errors still fail normally.
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", type=Path, default=Path("src/noisy_host_package_v18.py"))
    ap.add_argument("--protocol", type=Path, default=Path("protocol/real-package-v18.py"))
    ap.add_argument("--seeds", default="201,202,203,204")
    ap.add_argument("--payload-bytes", type=int, default=512)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--corpus-size", type=int, default=2000)
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--out", type=Path, default=Path("v18-residual-matrix.json"))
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
