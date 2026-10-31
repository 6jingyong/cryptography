#!/usr/bin/env python3
"""q=5 block-shaping benchmark v9.

Synthetic-only experiment. It borrows two abstract ideas:
1) wet-paper style feasibility: a cell/symbol pair may be unavailable;
2) STC-like shaping: one Hamming information dimension can be left free so the
   encoder can choose the lowest-cost legal codeword for a block.

No real-world carrier or covert-data workflow is implemented.
"""
from __future__ import annotations

import collections
import json
import math
import random
from pathlib import Path

import numpy as np

Q = 5
BLOCK = 6
SUBSET_COUNT = 16
COLOR = (4, 4, 3, 1)
H = np.asarray([[1, 1, 1, 1, 1, 0], [0, 1, 2, 3, 4, 1]], dtype=int)


def latent(x):
    return 40.0 + 1.9*x + 7.5*np.sin(x/2.7) + 2.7*np.cos(x/1.25)


def generate_pool(seed, n=2400):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        x = rng.uniform(0.0, 20.0)
        y = float(latent(x))
        y += rng.choice([-0.7, 0.0, 0.45])
        y += 0.16 * max(0.0, x - 11.0)
        y += rng.gauss(0.0, 1.3 + 0.10*x)
        if rng.random() < 0.055:
            y += rng.choice([-1, 1]) * rng.uniform(7, 18)
        p = rng.random()
        y = round(y, 1 if p < .12 else (2 if p < .28 else 3))
        rows.append((i, x, max(y, 0.1)))
    for j, idx in enumerate(rng.sample(range(n), 24), start=n):
        _, x, y = rows[idx]
        rows.append((j, x, y))
    return rows


def bucketize(rows):
    out = collections.defaultdict(list)
    for r in rows:
        out[int(math.floor(r[1]))].append(r)
    return {k: out[k] for k in sorted(out) if len(out[k]) >= 20}


def skewness(a):
    a = np.asarray(a, dtype=float)
    sd = float(a.std())
    if sd < 1e-12:
        return 0.0
    return float(np.mean(((a-a.mean())/sd)**3))


def features(points):
    ly = np.log(np.asarray([r[2] for r in points], dtype=float))
    return float(ly.mean()), float(ly.var()), skewness(ly)


def state(v, cuts):
    return 0 if v <= cuts[0] else (1 if v <= cuts[1] else 2)


def train_thresholds(seeds=6, samples=120):
    center, logvar, skew = [], [], []
    for i in range(seeds):
        seed = 20250011 + i*173
        buckets = bucketize(generate_pool(seed))
        rng = random.Random(seed + 555)
        for pts in buckets.values():
            pm, pv, ps = features(pts)
            for _ in range(samples):
                sub = rng.sample(pts, SUBSET_COUNT)
                m, v, s = features(sub)
                center.append(m-pm)
                logvar.append(math.log((v+1e-12)/(pv+1e-12)))
                skew.append(s-ps)
    return {
        "center": tuple(np.quantile(center, [1/3, 2/3])),
        "logvar": tuple(np.quantile(logvar, [1/3, 2/3])),
        "skew": tuple(np.quantile(skew, [1/3, 2/3])),
        "scales": (
            float(np.std(center)), float(np.std(logvar)), float(np.std(skew))
        ),
    }


def color_of(st):
    a, b, d, e = COLOR
    c, v, s = st
    return (a*c + b*v + d*s + e) % Q


def build_candidates(seed, thresholds, trials=550, keep_per_state=6, keep_per_color=8):
    buckets = bucketize(generate_pool(seed))
    keys = sorted(buckets)
    parent = {}
    by_cell = {}
    rng = random.Random(seed + 444)
    sc_c, sc_v, sc_s = thresholds["scales"]

    for k in keys:
        pts = buckets[k]
        pm, pv, ps = features(pts)
        parent[k] = (pm, pv, ps)
        by_state = collections.defaultdict(list)
        for _ in range(trials):
            ids = rng.sample(range(len(pts)), SUBSET_COUNT)
            sub = [pts[i] for i in ids]
            m, v, s = features(sub)
            cr = m-pm
            vr = math.log((v+1e-12)/(pv+1e-12))
            sr = s-ps
            st = (
                state(cr, thresholds["center"]),
                state(vr, thresholds["logvar"]),
                state(sr, thresholds["skew"]),
            )
            cost = (cr/sc_c)**2 + .20*(vr/sc_v)**2 + .08*(sr/sc_s)**2
            dc = min(abs(cr-thresholds["center"][0]), abs(cr-thresholds["center"][1]))/sc_c
            dv = min(abs(vr-thresholds["logvar"][0]), abs(vr-thresholds["logvar"][1]))/sc_v
            ds = min(abs(sr-thresholds["skew"][0]), abs(sr-thresholds["skew"][1]))/sc_s
            cost -= .04*(dc+dv+ds)
            by_state[st].append({"ids": ids, "m": m, "cost": float(cost), "state": st})

        colors = collections.defaultdict(list)
        for st, arr in by_state.items():
            for cand in sorted(arr, key=lambda z: z["cost"])[:keep_per_state]:
                colors[color_of(st)].append(cand)
        by_cell[k] = {
            c: sorted(arr, key=lambda z: z["cost"])[:keep_per_color]
            for c, arr in colors.items()
        }
    return buckets, keys, parent, by_cell


def hamming_encode4(data):
    x = [int(z) % Q for z in data] + [0, 0]
    x[4] = (-sum(x[:4])) % Q
    x[5] = (-(x[1] + 2*x[2] + 3*x[3] + 4*x[4])) % Q
    return tuple(x)


def hamming_correct(received):
    r = np.asarray(received, dtype=int) % Q
    syndrome = H.dot(r) % Q
    if np.all(syndrome == 0):
        return tuple(r)
    for i in range(BLOCK):
        for e in range(1, Q):
            if np.all((e*H[:, i]) % Q == syndrome):
                rr = r.copy()
                rr[i] = (rr[i]-e) % Q
                return tuple(rr)
    return tuple(r)


def optimize_symbols(keys6, symbols, parent, candidates, center_scale, cap=None, pair_weight=.35):
    layers = []
    for k, sym in zip(keys6, symbols):
        arr = candidates.get(k, {}).get(int(sym), [])
        if cap is not None:
            arr = [z for z in arr if z["cost"] <= cap]
        if not arr:
            return math.inf, None
        layers.append(arr)

    dp = np.asarray([z["cost"] for z in layers[0]], dtype=float)
    back = []
    for j in range(1, BLOCK):
        ndp = np.full(len(layers[j]), np.inf)
        nb = np.full(len(layers[j]), -1, dtype=int)
        parent_delta = parent[keys6[j]][0] - parent[keys6[j-1]][0]
        for b, cur in enumerate(layers[j]):
            vals = []
            for a, prev in enumerate(layers[j-1]):
                residual = (cur["m"]-prev["m"]) - parent_delta
                vals.append(dp[a] + cur["cost"] + pair_weight*(residual/center_scale)**2)
            a = int(np.argmin(vals))
            ndp[b], nb[b] = vals[a], a
        dp, back = ndp, back + [nb]

    idx = int(np.argmin(dp))
    path = [None]*BLOCK
    path[-1] = layers[-1][idx]
    for j in range(BLOCK-1, 0, -1):
        idx = int(back[j-1][idx])
        path[j-1] = layers[j-1][idx]
    return float(np.min(dp)), path


def choose_codeword(keys6, parent, candidates, payload, thresholds, mode, cap=None):
    scale = thresholds["scales"][0]
    if mode == "4P0S":
        cw = hamming_encode4(payload[:4])
        cost, path = optimize_symbols(keys6, cw, parent, candidates, scale, cap)
        return cw, cost, path, tuple(payload[:4])
    if mode == "3P1S_fixed":
        cw = hamming_encode4(tuple(payload[:3]) + (0,))
        cost, path = optimize_symbols(keys6, cw, parent, candidates, scale, cap)
        return cw, cost, path, tuple(payload[:3])
    if mode == "3P1S_shaped":
        best = (math.inf, None, None)
        for shaping_symbol in range(Q):
            cw = hamming_encode4(tuple(payload[:3]) + (shaping_symbol,))
            cost, path = optimize_symbols(keys6, cw, parent, candidates, scale, cap)
            if path is not None and cost < best[0]:
                best = (cost, cw, path)
        cost, cw, path = best
        return cw, cost, path, tuple(payload[:3])
    raise ValueError(mode)


def decode_color(points, parent_feature, thresholds):
    pm, pv, ps = parent_feature
    m, v, s = features(points)
    st = (
        state(m-pm, thresholds["center"]),
        state(math.log((v+1e-12)/(pv+1e-12)), thresholds["logvar"]),
        state(s-ps, thresholds["skew"]),
    )
    return color_of(st)


def benchmark():
    thresholds = train_thresholds()
    seeds = [20271031 + i*137 for i in range(6)]
    modes = ["4P0S", "3P1S_fixed", "3P1S_shaped"]
    runs = []

    for mode in modes:
        for seed in seeds:
            buckets, keys, parent, candidates = build_candidates(seed, thresholds)
            keys = keys[:18]
            rng = random.Random(seed + 9999)
            blocks = []
            for b in range(3):
                bk = keys[b*6:(b+1)*6]
                payload = [rng.randrange(Q) for _ in range(4)]
                cw, cost, path, msg = choose_codeword(
                    bk, parent, candidates, payload, thresholds, mode
                )
                blocks.append((bk, cw, cost, path, msg))

            if any(path is None for _, _, _, path, _ in blocks):
                runs.append({"seed": seed, "mode": mode, "feasible": False})
                continue

            selected_m = np.asarray([z["m"] for block in blocks for z in block[3]])
            parent_m = np.asarray([parent[k][0] for block in blocks for k in block[0]])
            rough = float(np.sum(np.diff(selected_m, 2)**2) /
                          max(np.sum(np.diff(parent_m, 2)**2), 1e-12))

            recovery = {}
            for drop in (.01, .05, .10):
                block_ok = whole_ok = 0
                total_blocks = 0
                reps = 60
                for rep in range(reps):
                    whole = True
                    rr = random.Random(seed*100000 + rep + int(drop*1000))
                    for bk, cw, cost, path, msg in blocks:
                        received = []
                        for k, cand in zip(bk, path):
                            pts = [buckets[k][i] for i in cand["ids"]]
                            kept = [p for p in pts if rr.random() >= drop]
                            if len(kept) < 6:
                                kept = rr.sample(pts, 6)
                            received.append(decode_color(kept, parent[k], thresholds))
                        corrected = hamming_correct(received)
                        got = tuple(corrected[:4]) if mode == "4P0S" else tuple(corrected[:3])
                        good = got == msg
                        block_ok += int(good)
                        total_blocks += 1
                        whole = whole and good
                    whole_ok += int(whole)
                recovery[str(drop)] = {
                    "block": block_ok/total_blocks,
                    "whole_18_cell_message": whole_ok/reps,
                }

            runs.append({
                "seed": seed,
                "mode": mode,
                "feasible": True,
                "payload_bits_per_cell": (
                    (4 if mode == "4P0S" else 3) * math.log2(Q) / BLOCK
                ),
                "mean_block_cost": float(np.mean([b[2] for b in blocks])),
                "roughness_ratio": rough,
                "recovery": recovery,
            })

    feasibility = {}
    for cap in (.05, .08, .12, .20, .30):
        acc = {"4P0S": [], "3P1S_shaped": []}
        for seed in seeds[:5]:
            buckets, keys, parent, candidates = build_candidates(seed, thresholds, trials=450)
            keys = keys[:18]
            rng = random.Random(seed + 12345)
            counts = {m: 0 for m in acc}
            total = 0
            for b in range(3):
                bk = keys[b*6:(b+1)*6]
                for _ in range(100):
                    payload = [rng.randrange(Q) for _ in range(4)]
                    for mode in acc:
                        _, _, path, _ = choose_codeword(
                            bk, parent, candidates, payload, thresholds, mode, cap=cap
                        )
                        counts[mode] += int(path is not None)
                    total += 1
            for mode in acc:
                acc[mode].append(counts[mode]/total)
        feasibility[str(cap)] = {
            mode: float(np.mean(vals)) for mode, vals in acc.items()
        }

    summary = {}
    for mode in modes:
        good = [r for r in runs if r["mode"] == mode and r["feasible"]]
        summary[mode] = {
            "successful_seeds": len(good),
            "payload_bits_per_cell": float(np.mean([r["payload_bits_per_cell"] for r in good])),
            "mean_block_cost": float(np.mean([r["mean_block_cost"] for r in good])),
            "mean_roughness_ratio": float(np.mean([r["roughness_ratio"] for r in good])),
            "block_recovery_5pct_loss": float(np.mean([
                r["recovery"]["0.05"]["block"] for r in good
            ])),
        }

    output = {
        "configuration": {
            "q": Q,
            "hamming_code": "[6,4,3]_5",
            "subset_count": SUBSET_COUNT,
            "test_seeds": len(seeds),
            "global_color_rule": "color=(4*center_state+4*logvar_state+3*skew_state+1) mod 5",
            "note": "synthetic-only shared-reference benchmark",
        },
        "summary": summary,
        "wet_cost_cap_feasibility": feasibility,
        "runs": runs,
    }
    out = Path("results/block_shaping_metrics_v9.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(json.dumps(output["wet_cost_cap_feasibility"], indent=2))


if __name__ == "__main__":
    benchmark()
