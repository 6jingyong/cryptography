#!/usr/bin/env python3
"""Net robust-capacity benchmark v8.

Synthetic-only benchmark built on v7. It freezes thresholds on disjoint training
seeds, reconstructs adaptive multichannel subsets on held-out seeds, then
measures:
- construction capacity proxy;
- state recovery after row loss / bootstrap resampling;
- an optimistic q-ary channel-capacity estimate after symbol errors;
- detectability versus matched random subsets using grouped cross-seed CV.

This is not a complete communication protocol and does not claim security.
"""
from __future__ import annotations
import json, math, random
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import feature_independence_v6 as fi
import active_multichannel_v7 as v7


def construct_detailed(seed, thresholds, n=2400, subset_count=24,
                       trials=1000, beam_width=30, min_candidates=2):
    buckets, keys, x, base_g, base_slope, candidates = v7.build_candidates(
        seed, thresholds, n=n, subset_count=subset_count, trials=trials
    )
    full = [v7.local_features(buckets[k]) for k in keys]
    rng = random.Random(seed + 909)

    first = {}
    for lv in range(3):
        for sk in range(3):
            arr = [c for c in candidates[keys[0]]
                   if c["lv_state"] == lv and c["sk_state"] == sk]
            if len(arr) >= min_candidates:
                first[(lv, sk)] = sorted(arr, key=lambda c: c["cost"])[:300]
    if not first:
        return None

    chosen0 = rng.choice(sorted(first))
    beam = sorted(
        [(c["cost"], [c], [("NA", chosen0[0], chosen0[1])])
         for c in first[chosen0]],
        key=lambda z: z[0],
    )[:beam_width]
    feasible_counts = [len(first)]

    for j in range(1, len(keys)):
        transitions = {}
        dx = x[j] - x[j - 1]
        for lv in range(3):
            for sk in range(3):
                curr = [c for c in candidates[keys[j]]
                        if c["lv_state"] == lv and c["sk_state"] == sk]
                if len(curr) < min_candidates:
                    continue
                curr = sorted(curr, key=lambda c: c["cost"])[:300]
                tmp = {0: [], 1: [], 2: []}
                for cost, path, sts in beam:
                    prev = path[-1]
                    for c in curr:
                        residual = (c["gm"] - prev["gm"]) / dx - base_slope[j - 1]
                        ss = v7.state(residual, thresholds["slope_resid"])
                        scale = max(
                            abs(thresholds["slope_resid"][0]),
                            abs(thresholds["slope_resid"][1]),
                            0.4,
                        )
                        nc = cost + c["cost"] + 0.02 * (residual / scale) ** 2
                        tmp[ss].append((nc, path + [c], sts + [(ss, lv, sk)]))
                for ss, arr in tmp.items():
                    if arr:
                        transitions[(ss, lv, sk)] = sorted(
                            arr, key=lambda z: z[0]
                        )[:beam_width]
        if not transitions:
            return None
        chosen = rng.choice(sorted(transitions))
        beam = transitions[chosen]
        feasible_counts.append(len(transitions))

    cost, path, states = beam[0]
    selected = {
        k: [buckets[k][i] for i in path[j]["ids"]]
        for j, k in enumerate(keys)
    }
    g = np.asarray([path[j]["gm"] for j in range(len(keys))])
    sp = CubicSpline(x, g, bc_type="natural")
    sp0 = CubicSpline(x, base_g, bc_type="natural")
    grid = np.linspace(x.min(), x.max(), 800)
    rough = float(np.trapezoid(sp(grid, 2) ** 2, grid))
    rough0 = float(np.trapezoid(sp0(grid, 2) ** 2, grid))

    return {
        "seed": seed,
        "buckets": buckets,
        "keys": keys,
        "x": x,
        "full": full,
        "base_g": base_g,
        "base_slope": base_slope,
        "selected": selected,
        "states": states,
        "feasible_counts": feasible_counts,
        "bits_per_cell": float(
            sum(math.log2(c) for c in feasible_counts) / len(keys)
        ),
        "gmean_shift": float(np.mean(np.abs(g / base_g - 1.0))),
        "roughness_ratio": float(rough / rough0),
    }


def decode_states(run, groups, thresholds):
    keys = run["keys"]
    g, lv_states, sk_states = [], [], []
    for j, k in enumerate(keys):
        gm, lv, sk = v7.local_features(groups[k])
        g.append(gm)
        _, flv, fsk = run["full"][j]
        lv_states.append(v7.state(
            math.log((lv + 1e-12) / (flv + 1e-12)),
            thresholds["logvar_rel"],
        ))
        sk_states.append(v7.state(sk - fsk, thresholds["skew_delta"]))

    g = np.asarray(g)
    decoded = []
    for j in range(len(keys)):
        if j == 0:
            ss = "NA"
        else:
            residual = (
                (g[j] - g[j - 1]) / (run["x"][j] - run["x"][j - 1])
                - run["base_slope"][j - 1]
            )
            ss = v7.state(residual, thresholds["slope_resid"])
        decoded.append((ss, lv_states[j], sk_states[j]))
    return decoded


def perturb_loss(run, frac, rng):
    out = {}
    for k in run["keys"]:
        pts = run["selected"][k]
        kept = [p for p in pts if rng.random() >= frac]
        if len(kept) < 8:
            kept = rng.sample(pts, 8)
        out[k] = kept
    return out


def perturb_bootstrap(run, rng):
    return {
        k: [rng.choice(run["selected"][k])
            for _ in range(len(run["selected"][k]))]
        for k in run["keys"]
    }


def robustness(runs, thresholds, reps=50):
    result = {}
    for label in ("loss_0.01", "loss_0.05", "loss_0.10", "bootstrap"):
        joint = slope = logvar = skew = total = slope_total = 0
        for run in runs:
            for rep in range(reps):
                rng = random.Random(run["seed"] * 100000 + rep + sum(map(ord, label)))
                if label.startswith("loss"):
                    groups = perturb_loss(run, float(label.split("_")[1]), rng)
                else:
                    groups = perturb_bootstrap(run, rng)
                decoded = decode_states(run, groups, thresholds)
                for j, (target, got) in enumerate(zip(run["states"], decoded)):
                    total += 1
                    logvar += int(target[1] == got[1])
                    skew += int(target[2] == got[2])
                    if j > 0:
                        slope_total += 1
                        slope += int(target[0] == got[0])
                    joint += int(target == got)
        result[label] = {
            "joint_symbol_recovery": joint / total,
            "slope_state_recovery": slope / slope_total,
            "logvar_state_recovery": logvar / total,
            "skew_state_recovery": skew / total,
        }
    return result


def observable_features(points, parent):
    y = np.asarray([r[2] for r in points], dtype=float)
    py = np.asarray([r[2] for r in parent], dtype=float)
    ly, ply = np.log(y), np.log(py)
    gm, pgm = np.exp(ly.mean()), np.exp(ply.mean())
    var, pvar = ly.var(), ply.var()
    iqr = np.quantile(ly, .75) - np.quantile(ly, .25)
    piqr = np.quantile(ply, .75) - np.quantile(ply, .25)
    q10, q90 = np.quantile(ly, [.1, .9])
    pq10, pq90 = np.quantile(ply, [.1, .9])
    return [
        math.log(gm / pgm),
        math.log((var + 1e-12) / (pvar + 1e-12)),
        fi.skewness(ly) - fi.skewness(ply),
        math.log((iqr + 1e-12) / (piqr + 1e-12)),
        q10 - pq10,
        q90 - pq90,
        float(np.std(ly)),
        float(np.mean(np.abs(ly - np.median(ly)))),
    ]


def detector_dataset(runs):
    X, y, groups = [], [], []
    for run in runs:
        rng = random.Random(run["seed"] + 3333)
        for k in run["keys"]:
            parent = run["buckets"][k]
            selected = run["selected"][k]
            X.append(observable_features(selected, parent))
            y.append(1)
            groups.append(run["seed"])
            random_subset = rng.sample(parent, len(selected))
            X.append(observable_features(random_subset, parent))
            y.append(0)
            groups.append(run["seed"])
    return np.asarray(X), np.asarray(y), np.asarray(groups)


def grouped_auc(model, X, y, groups):
    aucs = []
    for train, test in GroupKFold(n_splits=4).split(X, y, groups):
        model.fit(X[train], y[train])
        p = model.predict_proba(X[test])[:, 1]
        aucs.append(float(roc_auc_score(y[test], p)))
    return aucs


def qary_capacity(raw_bits, error_rate):
    q = 2 ** raw_bits
    p = float(error_rate)
    if p <= 0:
        return raw_bits
    if p >= 1 - 1 / q:
        return 0.0
    h2 = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    return max(0.0, raw_bits - h2 - p * math.log2(q - 1))


def main():
    train_seeds = [20240011 + i * 173 for i in range(10)]
    test_seeds = [20270031 + i * 137 for i in range(12)]
    # Thresholds were trained once on the disjoint `train_seeds` schedule
    # shown above and then frozen for every held-out test seed.
    thresholds = {
        "logvar_rel": (-0.4212049312065179, 0.11676187903528823),
        "skew_delta": (-0.29769487155815744, 0.9140050840143593),
        "slope_resid": (-0.4233904493665972, 0.4251615935738613),
    }

    runs = [construct_detailed(seed, thresholds) for seed in test_seeds]
    runs = [r for r in runs if r is not None]
    rob = robustness(runs, thresholds, reps=50)
    raw = float(np.median([r["bits_per_cell"] for r in runs]))

    X, y, groups = detector_dataset(runs)
    models = {
        "logistic": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000)
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=4, min_samples_leaf=5, random_state=1
        ),
        "hist_gb": HistGradientBoostingClassifier(
            max_depth=3, learning_rate=.05, max_iter=200, random_state=1
        ),
    }
    auc = {}
    for name, model in models.items():
        folds = grouped_auc(model, X, y, groups)
        auc[name] = {
            "mean": float(np.mean(folds)),
            "sd": float(np.std(folds)),
            "folds": folds,
        }

    construction = {
        "successful_runs": len(runs),
        "raw_bits_per_cell_median": raw,
        "raw_bits_range": [
            float(min(r["bits_per_cell"] for r in runs)),
            float(max(r["bits_per_cell"] for r in runs)),
        ],
        "gmean_shift_median": float(np.median([r["gmean_shift"] for r in runs])),
        "roughness_ratio_median": float(
            np.median([r["roughness_ratio"] for r in runs])
        ),
    }
    for label, rec in rob.items():
        construction[label + "_qary_net_bits_per_cell"] = qary_capacity(
            raw, 1 - rec["joint_symbol_recovery"]
        )

    output = {
        "configuration": {
            "train_seeds": 10,
            "test_seeds": 12,
            "generated_rows": 2400,
            "rows_after_duplicates": 2424,
            "bins": 20,
            "selected_rows_per_cell": 24,
            "candidate_trials_per_cell": 1000,
            "beam_width": 30,
            "min_candidates_per_local_state": 2,
            "features": ["slope_residual", "logvar_relative", "skew_delta"],
            "state_quantization": "frozen global tertiles trained on disjoint pools",
            "robustness_repetitions": 50,
            "detector_cv": "4-fold GroupKFold by seed",
        },
        "frozen_thresholds": {k: list(v) for k, v in thresholds.items()},
        "construction": construction,
        "robustness": rob,
        "detector_auc": auc,
        "parameter_only_codebook_floor": {
            "assumption": (
                "6 float32 thresholds + 64-bit seed + four uint16 integer "
                "parameters; excludes implementation/protocol description"
            ),
            "bits": 320,
            "amortized_bits_per_cell": {
                "20": 16.0,
                "300": 320 / 300,
                "1000": 0.32,
                "3000": 320 / 3000,
            },
        },
        "notes": [
            "q-ary net bits/cell is an optimistic channel-capacity approximation",
            "bootstrap is a deliberately harsh perturbation",
            "AUC above 0.5 indicates learnable selection artifacts",
        ],
    }
    path = Path("results/net_robust_capacity_metrics_v8.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
