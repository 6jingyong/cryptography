#!/usr/bin/env python3
"""Two-channel validation: smooth center line + coarse distribution codebook.

Channel A:
- choose a fixed-size subset per x-bin whose geometric means follow an
  observable smooth target.

Channel B:
- from the remaining points in each bin, choose a second fixed-size subset
  whose y-distribution matches one of three coarse tertile patterns.

All optimization uses only observable x/y values. The remaining rows are
labeled interference for analysis.
"""
from __future__ import annotations
import argparse, csv, json, math, random
from pathlib import Path
import numpy as np
import blind_partition_validation as bp

PATTERNS = {
    0: (6, 5, 4),
    1: (5, 5, 5),
    2: (4, 5, 6),
}


def choose_codebook(points, excluded_ids, state, rng, trials=700):
    remaining = [r for r in points if r[0] not in excluded_ids]
    ys_all = np.asarray([r[2] for r in points], dtype=float)
    q1, q2 = np.quantile(ys_all, [1/3, 2/3])

    tiers = [[], [], []]
    for r in remaining:
        idx = 0 if r[2] <= q1 else (1 if r[2] <= q2 else 2)
        tiers[idx].append(r)

    target = PATTERNS[state]
    if not all(len(tiers[i]) >= target[i] for i in range(3)):
        return None, False

    full_logs = np.log(ys_all)
    best, best_score = None, float("inf")
    for _ in range(trials):
        cand = []
        for i, count in enumerate(target):
            cand.extend(rng.sample(tiers[i], count))
        logs = np.log([r[2] for r in cand])
        score = (
            0.5 * (float(logs.mean()) - float(full_logs.mean())) ** 2
            + (float(logs.std()) - float(full_logs.std())) ** 2
        )
        if score < best_score:
            best_score = score
            best = cand
    return best, True


def js_divergence(p, q):
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)

    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log(a[mask] / b[mask])))

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def codebook_stats(buckets, codebooks, target_states):
    hits = 0
    js_vals, gm_shifts, spread_ratios = [], [], []

    for k in sorted(buckets):
        pts = buckets[k]
        cb = codebooks[k]
        y_all = np.asarray([r[2] for r in pts], dtype=float)
        q1, q2 = np.quantile(y_all, [1/3, 2/3])

        def counts(rows):
            c = np.zeros(3, dtype=int)
            for r in rows:
                c[0 if r[2] <= q1 else (1 if r[2] <= q2 else 2)] += 1
            return c

        c_cb = counts(cb)
        c_all = counts(pts)
        inferred = min(
            PATTERNS,
            key=lambda s: int(np.sum((c_cb - np.asarray(PATTERNS[s])) ** 2)),
        )
        hits += int(inferred == target_states[k])

        js_vals.append(js_divergence(c_cb, c_all))
        gm_shifts.append(
            abs(bp.gmean([r[2] for r in cb]) / bp.gmean(y_all) - 1.0)
        )
        spread_ratios.append(
            float(np.std(np.log([r[2] for r in cb])) / np.std(np.log(y_all)))
        )

    return {
        "target_hit_rate": hits / len(buckets),
        "mean_js_to_full_tertile_hist": float(np.mean(js_vals)),
        "mean_abs_gmean_shift": float(np.mean(gm_shifts)),
        "mean_logspread_ratio": float(np.mean(spread_ratios)),
    }


def random_codebook_baseline(buckets, centers, count, reps, seed):
    rng = random.Random(seed)
    records = []
    for _ in range(reps):
        js_vals, gm_shifts, spread_ratios = [], [], []
        for k in sorted(buckets):
            excluded = {r[0] for r in centers[k]}
            remaining = [r for r in buckets[k] if r[0] not in excluded]
            cb = rng.sample(remaining, count)

            y_all = np.asarray([r[2] for r in buckets[k]], dtype=float)
            q1, q2 = np.quantile(y_all, [1/3, 2/3])

            def counts(rows):
                c = np.zeros(3, dtype=int)
                for r in rows:
                    c[0 if r[2] <= q1 else (1 if r[2] <= q2 else 2)] += 1
                return c

            js_vals.append(js_divergence(counts(cb), counts(buckets[k])))
            gm_shifts.append(
                abs(bp.gmean([r[2] for r in cb]) / bp.gmean(y_all) - 1.0)
            )
            spread_ratios.append(
                float(np.std(np.log([r[2] for r in cb])) / np.std(np.log(y_all)))
            )

        records.append(
            (
                float(np.mean(js_vals)),
                float(np.mean(gm_shifts)),
                float(np.mean(spread_ratios)),
            )
        )
    return np.asarray(records, dtype=float)


def write_roles(path, buckets, centers, codebooks, states):
    center_ids = {r[0] for rows in centers.values() for r in rows}
    codebook_ids = {r[0] for rows in codebooks.values() for r in rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row_id", "x", "y", "bin", "role", "codebook_target_state"])
        for k in sorted(buckets):
            for i, x, y in buckets[k]:
                if i in center_ids:
                    role, state = "center", ""
                elif i in codebook_ids:
                    role, state = "codebook", states[k]
                else:
                    role, state = "interference", ""
                w.writerow([i, f"{x:.6f}", y, k, role, state])


def run(seed=20261031, n=1200, center_count=12, codebook_count=15,
        center_trials=2000, codebook_trials=700, random_baselines=500):
    rows = bp.generate_pool(seed, n)
    buckets = bp.bucketize(rows, 1.0)
    _, _, _, target = bp.robust_target(buckets)

    centers = bp.select_optimized(
        buckets, center_count, target, seed=seed + 101, trials=center_trials
    )

    rng = random.Random(seed + 202)
    states = {k: rng.randrange(3) for k in sorted(buckets)}
    codebooks, feasible = {}, {}
    for k in sorted(buckets):
        excluded = {r[0] for r in centers[k]}
        cb, ok = choose_codebook(
            buckets[k], excluded, states[k], rng, trials=codebook_trials
        )
        if not ok:
            remaining = [r for r in buckets[k] if r[0] not in excluded]
            cb = rng.sample(remaining, codebook_count)
        codebooks[k] = cb
        feasible[k] = ok

    full = bp.center_stats(buckets)
    center = bp.center_stats(centers)
    code = codebook_stats(buckets, codebooks, states)
    rb = random_codebook_baseline(
        buckets, centers, codebook_count, random_baselines, seed + 303
    )

    metrics = {
        "configuration": {
            "seed": seed,
            "rows": len(rows),
            "bins": len(buckets),
            "center_count_per_bin": center_count,
            "codebook_count_per_bin": codebook_count,
            "codebook_patterns": {str(k): list(v) for k, v in PATTERNS.items()},
            "random_baselines": random_baselines,
        },
        "center_channel": {
            "roughness": center["roughness"],
            "full_pool_roughness": full["roughness"],
            "slope_corr_to_full": float(
                np.corrcoef(center["slope"], full["slope"])[0, 1]
            ),
        },
        "codebook_channel": {
            **code,
            "feasible_bin_rate": sum(feasible.values()) / len(feasible),
            "random_mean_js_median": float(np.median(rb[:, 0])),
            "random_mean_abs_gmean_shift_median": float(np.median(rb[:, 1])),
            "random_logspread_ratio_median": float(np.median(rb[:, 2])),
        },
    }
    return rows, buckets, centers, codebooks, states, metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--n", type=int, default=1200)
    ap.add_argument("--roles-output", type=Path,
                    default=Path("results/two_channel_roles_v3.csv"))
    ap.add_argument("--metrics-output", type=Path,
                    default=Path("results/two_channel_metrics_v3.json"))
    args = ap.parse_args()

    _, buckets, centers, codebooks, states, metrics = run(seed=args.seed, n=args.n)
    write_roles(args.roles_output, buckets, centers, codebooks, states)
    args.metrics_output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
