#!/usr/bin/env python3
from __future__ import annotations
import json, random
from pathlib import Path
import numpy as np
import blind_partition_validation as bp

seeds=[20261031+i*137 for i in range(12)]
records=[]
for seed in seeds:
    rows=bp.generate_pool(seed,1200)
    buckets=bp.bucketize(rows,1.0)
    _,_,_,target=bp.robust_target(buckets)
    opt=bp.select_optimized(buckets,12,target,seed=seed+101,trials=1200)
    full=bp.full_stats(buckets); os=bp.center_stats(opt); oc=bp.comparison(os,full,target)
    rng=random.Random(seed+202)
    rr=[]
    for _ in range(120):
        s=bp.center_stats(bp.select_random(buckets,12,rng)); c=bp.comparison(s,full,target)
        rr.append((s,c))
    rand_rough=np.array([s['roughness'] for s,c in rr])
    rand_rmse=np.array([c['rmse_to_observable_smooth_target'] for s,c in rr])
    rand_corr=np.array([c['slope_corr_to_full'] for s,c in rr])
    records.append({
        'seed':seed,
        'optimized_roughness':os['roughness'],
        'random_roughness_median':float(np.median(rand_rough)),
        'roughness_ratio_vs_random_median':float(os['roughness']/np.median(rand_rough)),
        'optimized_rmse_target':oc['rmse_to_observable_smooth_target'],
        'random_rmse_target_median':float(np.median(rand_rmse)),
        'rmse_ratio_vs_random_median':float(oc['rmse_to_observable_smooth_target']/np.median(rand_rmse)),
        'optimized_slope_corr_to_full':oc['slope_corr_to_full'],
        'random_slope_corr_median':float(np.median(rand_corr)),
        'roughness_better_than_all_random':bool(os['roughness']<rand_rough.min()),
        'rmse_better_than_all_random':bool(oc['rmse_to_observable_smooth_target']<rand_rmse.min()),
        'slope_corr_above_random_p95':bool(oc['slope_corr_to_full']>np.quantile(rand_corr,.95)),
    })
summary={
    'seeds':len(records),
    'roughness_ratio_median':float(np.median([r['roughness_ratio_vs_random_median'] for r in records])),
    'roughness_ratio_range':[float(min(r['roughness_ratio_vs_random_median'] for r in records)),float(max(r['roughness_ratio_vs_random_median'] for r in records))],
    'rmse_ratio_median':float(np.median([r['rmse_ratio_vs_random_median'] for r in records])),
    'rmse_ratio_range':[float(min(r['rmse_ratio_vs_random_median'] for r in records)),float(max(r['rmse_ratio_vs_random_median'] for r in records))],
    'slope_corr_median':float(np.median([r['optimized_slope_corr_to_full'] for r in records])),
    'slope_corr_range':[float(min(r['optimized_slope_corr_to_full'] for r in records)),float(max(r['optimized_slope_corr_to_full'] for r in records))],
    'roughness_better_than_all_random_count':sum(r['roughness_better_than_all_random'] for r in records),
    'rmse_better_than_all_random_count':sum(r['rmse_better_than_all_random'] for r in records),
    'slope_corr_above_random_p95_count':sum(r['slope_corr_above_random_p95'] for r in records),
}
out={'configuration':{'n':1200,'bins':20,'center_count':12,'candidate_trials':1200,'random_baselines_per_seed':120},'summary':summary,'runs':records}
Path('results/blind_partition_multiseed_metrics_v2.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
