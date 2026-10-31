#!/usr/bin/env python3
"""Detectability benchmark for the synthetic V11 mixed package.

Generic detector: sees only residual-shape summary features.
Oracle detector: additionally knows the q=8 transform/delta and can test lattice /
Hamming-code consistency.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier


def load_core(path):
    spec=importlib.util.spec_from_file_location('v11core',path)
    m=importlib.util.module_from_spec(spec); sys.modules['v11core']=m; spec.loader.exec_module(m); return m


def skew_kurt(r):
    r=np.asarray(r,float); sd=np.std(r)
    if sd<1e-15: return 0.0,0.0
    z=(r-np.mean(r))/sd
    return float(np.mean(z**3)), float(np.mean(z**4)-3.0)


def generic_features(r):
    r=np.asarray(r,float)
    sd=float(np.std(r)); sk,ku=skew_kurt(r)
    d1=np.diff(r); d2=np.diff(r,2)
    lag=0.0
    if np.std(r[:-1])>1e-15 and np.std(r[1:])>1e-15:
        lag=float(np.corrcoef(r[:-1],r[1:])[0,1])
    p=np.abs(np.fft.rfft(r-np.mean(r)))**2
    hf=float(np.sum(p[len(p)//2:])/max(np.sum(p),1e-15))
    zc=float(np.mean(np.signbit(r[:-1])!=np.signbit(r[1:])))
    return [sd,sk,ku,float(np.std(d1)),float(np.std(d2)),lag,hf,float(np.max(np.abs(r))),float(np.median(np.abs(r))),zc]


def syndrome_zero(core, word):
    s0=s1=0
    for v,(h0,h1) in zip(word,core.H_COLS):
        s0 ^= core.gf_mul(int(v),h0); s1 ^= core.gf_mul(int(v),h1)
    return (s0==0 and s1==0)


def oracle_features(core, coeff, delta, groups):
    vals=[]; valid=[]
    for g in range(groups):
        c=coeff[g*9:(g+1)*9]
        scaled=c/delta
        dist=np.min(np.abs(scaled[:,None]-core.LEVELS[None,:]),axis=1)
        vals.extend(dist.tolist())
        raw=np.argmin(np.abs(scaled[:,None]-core.LEVELS[None,:]),axis=1).astype(np.uint8)
        valid.append(float(syndrome_zero(core,raw)))
    return [float(np.mean(vals)),float(np.max(vals)),float(np.mean(valid))]


def collect(core, package_path, manifest_path, samples_per_family=700, seed=20261101):
    rng=np.random.default_rng(seed)
    mani=json.loads(Path(manifest_path).read_text())
    data=np.load(package_path)
    Xg=[]; Xo=[]; y=[]; fams=[]

    for t in mani['tables']:
        mode=core.Mode(t['mode'],t['transform'],t['params'],t['fit_nrmse'],0,int(t['groups']),float(t['delta']),int(t['decimals']))
        B,S=core.mode_basis(mode.name,mode.params); U=core.free_basis(B,S)[:,:mode.groups*9]
        pub=data[f"table_{t['table_id']}_y"]; channels=int(t['channels']); segments=int(t['segments']); family=t['family']
        base=core.baselines(family,channels); zbase=np.asarray([core.ty(v,mode.transform) for v in base])
        pairs=[(s,c) for s in range(segments) for c in range(channels)]
        take=min(samples_per_family,len(pairs))
        picks=rng.choice(len(pairs),size=take,replace=False)
        encoded=[]; coeffs=[]
        for k in picks:
            s,c=pairs[int(k)]; yy=pub[s*core.N:(s+1)*core.N,c]; z=core.ty(yy,mode.transform); beta,*_=np.linalg.lstsq(B,z,rcond=None); r=z-B@beta; coeff=r@U
            encoded.append((r,coeff)); coeffs.append(coeff)
        C=np.asarray(coeffs)
        mu=np.mean(C,axis=0); cov=np.cov(C,rowvar=False)+np.eye(C.shape[1])*1e-9
        for r,coeff in encoded:
            Xg.append(generic_features(r)); Xo.append(generic_features(r)+oracle_features(core,coeff,mode.delta,mode.groups)); y.append(1); fams.append(family)
        controls=rng.multivariate_normal(mu,cov,size=take)
        for j,coeff0 in enumerate(controls):
            c=j%channels; z=zbase[c]+U@coeff0; yy=np.round(core.ity(z,mode.transform),mode.decimals); zz=core.ty(yy,mode.transform); beta,*_=np.linalg.lstsq(B,zz,rcond=None); r=zz-B@beta; coeff=r@U
            Xg.append(generic_features(r)); Xo.append(generic_features(r)+oracle_features(core,coeff,mode.delta,mode.groups)); y.append(0); fams.append(family)
    return np.asarray(Xg,float),np.asarray(Xo,float),np.asarray(y,int),np.asarray(fams)


def eval_models(X,y,seed=7):
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.30,random_state=seed,stratify=y)
    models={
        'logistic':make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)),
        'random_forest':RandomForestClassifier(n_estimators=250,min_samples_leaf=4,random_state=seed,n_jobs=-1),
        'hist_gb':HistGradientBoostingClassifier(max_iter=180,max_leaf_nodes=31,random_state=seed),
    }
    out={}
    for name,m in models.items():
        m.fit(Xtr,ytr); p=m.predict_proba(Xte)[:,1]; out[name]=float(roc_auc_score(yte,p))
    return out


def family_holdout_auc(X,y,fams):
    vals=[]
    for fam in sorted(set(fams.tolist())):
        tr=fams!=fam; te=fams==fam
        model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000))
        model.fit(X[tr],y[tr]); p=model.predict_proba(X[te])[:,1]; vals.append((fam,float(roc_auc_score(y[te],p))))
    return {'by_family':dict(vals),'mean':float(np.mean([v for _,v in vals]))}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--core',default='src/q8_mixed_package_v11.py'); ap.add_argument('--package',default='v11_out/published_package_v11.npz'); ap.add_argument('--manifest',default='v11_out/manifest_v11.json'); ap.add_argument('--samples-per-family',type=int,default=700); ap.add_argument('--out',default='v11_out/detectability_v11.json'); a=ap.parse_args()
    core=load_core(a.core); Xg,Xo,y,f=collect(core,a.package,a.manifest,a.samples_per_family)
    res={'samples':int(len(y)),'generic_features':10,'oracle_features':13,'generic_auc':eval_models(Xg,y),'oracle_auc':eval_models(Xo,y),'generic_family_holdout_logistic':family_holdout_auc(Xg,y,f),'oracle_family_holdout_logistic':family_holdout_auc(Xo,y,f)}
    Path(a.out).write_text(json.dumps(res,indent=2)); print(json.dumps(res,indent=2))

if __name__=='__main__': main()
