#!/usr/bin/env python3
"""Blind partition validation for dirty-channel curve construction.

The optimizer is intentionally denied access to the latent data-generating
function. It sees only x/y observations from a synthetic dirty pool.

Goal: test whether a fixed-size subset chosen within each x-bin can produce a
smooth, plausible geometric-mean center line while the full observed pool
remains noisy and natural-looking. Remaining observations are treated as
non-center roles (distribution/interference) for this benchmark; no complete
encoding protocol is implemented.
"""
from __future__ import annotations

import argparse, csv, json, math, random
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline, UnivariateSpline


def latent(x: float) -> float:
    return 40.0 + 1.9*x + 7.5*math.sin(x/2.7) + 2.7*math.cos(x/1.25)


def generate_pool(seed=20261031, n=1200):
    rng = random.Random(seed)
    rows=[]
    for i in range(n):
        x = rng.uniform(0.0, 20.0)
        base = latent(x)
        # batch/source effects not exposed as optimization hints
        batch_shift = rng.choice([-0.7, 0.0, 0.45])
        drift = 0.16*max(0.0,x-11.0)
        sigma = 1.3 + 0.10*x
        # mostly additive measurement noise, occasional multiplicative-ish disturbance
        y = base + batch_shift + drift + rng.gauss(0,sigma)
        if rng.random() < 0.055:
            y += rng.choice([-1,1])*rng.uniform(7,18)
        # mixed precision
        p = rng.random()
        if p < 0.12: y=round(y,1)
        elif p < 0.28: y=round(y,2)
        else: y=round(y,3)
        if y <= 0: y = 0.1
        rows.append((i,x,y))
    # duplicate-like records
    for j, idx in enumerate(rng.sample(range(n), 24), start=n):
        _,x,y = rows[idx]
        rows.append((j,x,y))
    return rows


def bucketize(rows, bin_width=1.0):
    b={}
    for row in rows:
        _,x,y=row
        k=int(math.floor(x/bin_width))
        b.setdefault(k,[]).append(row)
    return {k:b[k] for k in sorted(b)}


def gmean(vals):
    a=np.asarray(vals,dtype=float)
    return float(np.exp(np.mean(np.log(a))))


def robust_target(buckets):
    bins=sorted(buckets)
    xs=np.array([np.mean([r[1] for r in buckets[k]]) for k in bins])
    centers=np.array([gmean([r[2] for r in buckets[k]]) for k in bins])
    # Low-complexity target from observable full-bin geometric means only.
    # The modest smoothing budget reduces bin noise without flattening broad structure.
    s=max(1.0, len(xs) * 0.40**2)
    sp=UnivariateSpline(xs,centers,k=3,s=s)
    return bins,xs,centers,sp(xs)


def choose_subset_for_target(points, k, target, rng, trials=2500):
    if len(points) <= k:
        return list(points)
    # candidate pool trimmed only by very broad quantiles to avoid one extreme dominating
    ys=np.array([r[2] for r in points])
    lo,hi=np.quantile(ys,[0.03,0.97])
    eligible=[r for r in points if lo <= r[2] <= hi]
    if len(eligible)<k: eligible=list(points)
    best=None; best_score=float('inf')
    logt=math.log(max(target,1e-12))
    for _ in range(trials):
        cand=rng.sample(eligible,k)
        logs=np.log([r[2] for r in cand])
        gm_log=float(np.mean(logs))
        # target fit + mild penalty for implausibly narrow subset scatter
        spread=float(np.std(logs))
        fullspread=float(np.std(np.log([r[2] for r in points])))
        score=(gm_log-logt)**2 + 0.04*(spread-fullspread)**2
        if score<best_score:
            best_score=score; best=cand
    return best


def select_optimized(buckets,k,target_vals,seed=11,trials=2500):
    rng=random.Random(seed)
    selected={}
    for key,t in zip(sorted(buckets),target_vals):
        selected[key]=choose_subset_for_target(buckets[key],k,float(t),rng,trials)
    return selected


def select_random(buckets,k,rng):
    out={}
    for key,pts in buckets.items():
        out[key]=list(pts) if len(pts)<=k else rng.sample(pts,k)
    return out


def center_stats(groups):
    keys=sorted(groups)
    x=np.array([np.mean([r[1] for r in groups[k]]) for k in keys])
    y=np.array([gmean([r[2] for r in groups[k]]) for k in keys])
    slope=np.diff(y)/np.diff(x)
    sp=CubicSpline(x,y,bc_type='natural')
    grid=np.linspace(x.min(),x.max(),2500)
    d1=sp(grid,1); d2=sp(grid,2)
    return {
        'keys':keys,'x':x,'g':y,'slope':slope,
        'roughness':float(np.trapezoid(d2*d2,grid)),
        'derivative_tv':float(np.trapezoid(np.abs(d2),grid)),
        'max_abs_spline_slope':float(np.max(np.abs(d1))),
        'slope_sd':float(np.std(slope)),
    }


def full_stats(buckets):
    return center_stats(buckets)


def comparison(sel,full,target):
    return {
        'rmse_to_observable_smooth_target':float(np.sqrt(np.mean((sel['g']-target)**2))),
        'rmse_to_full_geomean':float(np.sqrt(np.mean((sel['g']-full['g'])**2))),
        'slope_corr_to_full':float(np.corrcoef(sel['slope'],full['slope'])[0,1]),
    }


def percentile_rank(value, samples, lower_is_better=True):
    a=np.asarray(samples)
    if lower_is_better:
        return float(100*np.mean(a <= value))
    return float(100*np.mean(a >= value))


def write_pool(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['row_id','x','y']);
        for i,x,y in rows: w.writerow([i,f'{x:.6f}',y])


def write_groups(path,buckets,selected):
    selected_ids={r[0] for pts in selected.values() for r in pts}
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['row_id','x','y','role'])
        for k in sorted(buckets):
            for i,x,y in buckets[k]:
                w.writerow([i,f'{x:.6f}',y,'center' if i in selected_ids else 'remaining'])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=20261031)
    ap.add_argument('--n',type=int,default=1200)
    ap.add_argument('--bin-width',type=float,default=1.0)
    ap.add_argument('--center-count',type=int,default=12)
    ap.add_argument('--candidate-trials',type=int,default=2500)
    ap.add_argument('--random-baselines',type=int,default=500)
    ap.add_argument('--pool-output',type=Path,default=Path('data/blind_dirty_pool_v2.csv'))
    ap.add_argument('--roles-output',type=Path,default=Path('results/blind_partition_roles_v2.csv'))
    ap.add_argument('--metrics-output',type=Path,default=Path('results/blind_partition_metrics_v2.json'))
    args=ap.parse_args()

    rows=generate_pool(args.seed,args.n)
    buckets=bucketize(rows,args.bin_width)
    bins,xs,meds,target=robust_target(buckets)
    opt=select_optimized(buckets,args.center_count,target,seed=args.seed+101,trials=args.candidate_trials)
    full=full_stats(buckets); optstat=center_stats(opt)
    optcmp=comparison(optstat,full,target)

    rng=random.Random(args.seed+202)
    rand=[]
    for _ in range(args.random_baselines):
        s=center_stats(select_random(buckets,args.center_count,rng))
        c=comparison(s,full,target)
        rand.append({**{k:s[k] for k in ['roughness','derivative_tv','max_abs_spline_slope','slope_sd']},**c})

    def summarize(key):
        a=np.array([r[key] for r in rand],dtype=float)
        return {'mean':float(a.mean()),'sd':float(a.std()),'p05':float(np.quantile(a,.05)),'median':float(np.median(a)),'p95':float(np.quantile(a,.95))}

    metrics={
        'configuration':{'seed':args.seed,'rows':len(rows),'bins':len(buckets),'bin_width':args.bin_width,'center_count_per_bin':args.center_count,'candidate_trials_per_bin':args.candidate_trials,'random_baselines':args.random_baselines},
        'full_pool':{k:full[k] for k in ['roughness','derivative_tv','max_abs_spline_slope','slope_sd']},
        'optimized':{**{k:optstat[k] for k in ['roughness','derivative_tv','max_abs_spline_slope','slope_sd']},**optcmp},
        'random_baseline':{k:summarize(k) for k in rand[0]},
        'optimized_percentile_vs_random':{
            'roughness_lower_tail_pct':percentile_rank(optstat['roughness'],[r['roughness'] for r in rand]),
            'derivative_tv_lower_tail_pct':percentile_rank(optstat['derivative_tv'],[r['derivative_tv'] for r in rand]),
            'rmse_target_lower_tail_pct':percentile_rank(optcmp['rmse_to_observable_smooth_target'],[r['rmse_to_observable_smooth_target'] for r in rand]),
            'slope_corr_upper_tail_pct':percentile_rank(optcmp['slope_corr_to_full'],[r['slope_corr_to_full'] for r in rand],lower_is_better=False),
        }
    }
    write_pool(args.pool_output,rows)
    write_groups(args.roles_output,buckets,opt)
    args.metrics_output.parent.mkdir(parents=True,exist_ok=True)
    args.metrics_output.write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2))

if __name__=='__main__': main()
