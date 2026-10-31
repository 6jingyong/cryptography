#!/usr/bin/env python3
"""Synthetic-only V11 mixed-package q=8 benchmark.

Features:
- six heterogeneous macro families
- automatic transform selection from published-style x/y structure
- GF(8) Hamming [9,7,3]
- 6 payload + 1 shaping + 2 parity symbols
- compact manifest
- decoder uses only published NPZ + manifest
- manifest overhead counted in net rate

The benchmark payload is generated internally. This script does not read arbitrary
external payload files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

# ---------- GF(8) ----------
GF_MOD = 0b1011
LEVELS = np.asarray([-0.5, 0.5, -1.5, 1.5, -2.5, 2.5, -3.5, 3.5], float)
H_COLS = [(1, a) for a in range(8)] + [(0, 1)]
N = 24
X = np.linspace(-1.0, 1.0, N)
CODE_N = 9
PAYLOAD_SYMS = 6
PAYLOAD_BITS_PER_CW = 18


def gf_mul(a, b):
    out = 0
    a = int(a); b = int(b)
    while b:
        if b & 1: out ^= a
        b >>= 1
        a <<= 1
        if a & 0b1000: a ^= GF_MOD
    return out & 7


MUL = np.asarray([[gf_mul(a,b) for b in range(8)] for a in range(8)], dtype=np.uint8)
CORR_POS = np.full((8,8), -1, dtype=np.int8)
CORR_ERR = np.zeros((8,8), dtype=np.uint8)
for pos,(h0,h1) in enumerate(H_COLS):
    for e in range(1,8):
        CORR_POS[gf_mul(e,h0), gf_mul(e,h1)] = pos
        CORR_ERR[gf_mul(e,h0), gf_mul(e,h1)] = e


def hamming_encode(info6, shaping):
    info6 = np.asarray(info6, dtype=np.uint8)
    shaping = np.asarray(shaping, dtype=np.uint8)
    info7 = np.empty((len(info6),7), dtype=np.uint8)
    info7[:,:6] = info6
    info7[:,6] = shaping
    cw = np.zeros((len(info6),9), dtype=np.uint8)
    cw[:,:7] = info7
    p7 = np.bitwise_xor.reduce(info7, axis=1)
    cw[:,7] = p7
    p8 = np.zeros(len(info6), dtype=np.uint8)
    for i in range(7): p8 ^= MUL[i, info7[:,i]]
    p8 ^= MUL[7,p7]
    cw[:,8] = p8
    return cw


def hamming_correct(r):
    out = np.asarray(r, dtype=np.uint8).copy()
    s0 = np.bitwise_xor.reduce(out[:,:8], axis=1)
    s1 = out[:,8].copy()
    for i in range(8): s1 ^= MUL[i,out[:,i]]
    pos = CORR_POS[s0,s1]
    err = CORR_ERR[s0,s1]
    rows = np.nonzero(pos >= 0)[0]
    if len(rows): out[rows,pos[rows]] ^= err[rows]
    return out


# ---------- byte packing ----------
def bytes_to_symbols(data: bytes):
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder='big')
    bit_len = len(bits)
    if len(bits)%3: bits = np.pad(bits, (0, (-len(bits))%3))
    tri = bits.reshape(-1,3)
    syms = (4*tri[:,0] + 2*tri[:,1] + tri[:,2]).astype(np.uint8)
    return syms, bit_len


def symbols_to_bytes(syms, bit_len):
    s = np.asarray(syms, dtype=np.uint8).reshape(-1)
    bits = np.column_stack(((s>>2)&1,(s>>1)&1,s&1)).reshape(-1)[:bit_len]
    if len(bits)%8: bits = np.pad(bits, (0, (-len(bits))%8))
    return np.packbits(bits, bitorder='big').tobytes()[:math.ceil(bit_len/8)]


def synthetic_payload(nbytes):
    return hashlib.shake_256(b'q8-mixed-v11').digest(nbytes)


# ---------- macros ----------
FAMILIES = ['affine','periodic','harmonic','saturation','gaussian','symmetric']


def macro(family, c, channels):
    u = X
    ph = 2*np.pi*c/max(channels,1)
    if family == 'affine':
        return 50 + 0.3*c + (8 + 0.5*np.sin(ph))*u
    if family == 'periodic':
        w = 3*np.pi
        return 55 + 7.5*np.sin(w*u+ph) + 1.8*np.cos(w*u-0.3*ph)
    if family == 'harmonic':
        w = 3*np.pi
        return 55 + 7*np.sin(w*u+ph) + 1.5*np.cos(w*u-0.25*ph) + (1.6+0.3*np.cos(ph))*np.sin(2*w*u+0.2+0.4*ph)
    if family == 'saturation':
        t = 2*(u+1)
        tau = 0.80
        return 30 + 0.3*c + 25*(1-np.exp(-t/tau))
    if family == 'gaussian':
        mu = 0.15*np.sin(ph); sigma = 0.52 + 0.03*np.cos(ph); amp = 48 + 2*np.sin(ph)
        return amp*np.exp(-0.5*((u-mu)/sigma)**2)
    if family == 'symmetric':
        return 45 + 0.25*c + (7+0.5*np.cos(ph))*u*u + (2+0.2*np.sin(ph))*u**4
    raise ValueError(family)


def baselines(family, channels):
    return np.asarray([macro(family,c,channels) for c in range(channels)])


@dataclass
class Mode:
    name: str
    transform: str
    params: dict
    fit_nrmse: float
    free_dims: int
    groups: int
    delta: float
    decimals: int = 3


def ty(y, transform):
    if transform == 'identity': return np.asarray(y,float)
    if transform == 'log':
        if np.any(np.asarray(y)<=0): raise ValueError('nonpositive log input')
        return np.log(np.asarray(y,float))
    raise ValueError(transform)


def ity(z, transform):
    return np.asarray(z,float) if transform == 'identity' else np.exp(np.asarray(z,float))


def mode_basis(name, params):
    u = X
    if name == 'affine': return np.column_stack([np.ones(N),u]), None
    if name == 'periodic1':
        w = float(params['w']); return np.column_stack([np.ones(N),np.sin(w*u),np.cos(w*u)]), None
    if name == 'periodic2':
        w = float(params['w']); return np.column_stack([np.ones(N),np.sin(w*u),np.cos(w*u),np.sin(2*w*u),np.cos(2*w*u)]), None
    if name == 'saturation':
        t = 2*(u+1); tau = float(params['tau']); return np.column_stack([np.ones(N),np.exp(-t/tau)]), None
    if name == 'gaussian_log': return np.column_stack([np.ones(N),u,u*u]), None
    if name == 'symmetric_even':
        E = np.zeros((N,N//2),float)
        for j in range(N//2): E[j,j]=E[N-1-j,j]=1/math.sqrt(2)
        B = np.column_stack([np.ones(N),u*u,u**4])
        return B,E
    raise ValueError(name)


def d2mat(n):
    D=np.zeros((n-2,n),float)
    for i in range(n-2): D[i,i:i+3]=(1,-2,1)
    return D


def free_basis(B, subspace=None):
    if subspace is None:
        Q,_=np.linalg.qr(B,mode='complete'); r=np.linalg.matrix_rank(B); U0=Q[:,r:]
    else:
        C=subspace.T@B; Q,_=np.linalg.qr(C,mode='complete'); r=np.linalg.matrix_rank(C); U0=subspace@Q[:,r:]
    D=d2mat(N); G=(D@U0).T@(D@U0); vals,V=np.linalg.eigh(G); U=U0@V[:,np.argsort(vals)]
    for j in range(U.shape[1]):
        k=np.argmax(np.abs(U[:,j]));
        if U[k,j]<0: U[:,j]*=-1
    return U


def nrmse(a,b):
    den=np.ptp(a) or np.std(a) or 1.0
    return float(np.sqrt(np.mean((a-b)**2))/den)


def candidate_modes(Y):
    configs=[('affine','identity',{}),('periodic1','identity',{'w':3*np.pi}),('periodic2','identity',{'w':3*np.pi}),('gaussian_log','log',{}),('symmetric_even','identity',{})]
    for tau in [0.70,0.75,0.80,0.85,0.90]: configs.append(('saturation','identity',{'tau':tau}))
    out=[]
    for name,tr,params in configs:
        try:
            B,S=mode_basis(name,params); U=free_basis(B,S); errs=[]
            for y in Y:
                z=ty(y,tr); beta,*_=np.linalg.lstsq(B,z,rcond=None); yhat=ity(B@beta,tr); errs.append(nrmse(y,yhat))
            g=U.shape[1]//9
            if g:
                out.append(Mode(name,tr,params,float(np.mean(errs)),U.shape[1],g,0.010 if tr=='identity' else 0.004))
        except Exception:
            pass
    return out


def choose_mode(Y, threshold=5e-4):
    c=candidate_modes(Y); feasible=[m for m in c if m.fit_nrmse<=threshold]
    if not feasible: feasible=[min(c,key=lambda m:m.fit_nrmse)]
    feasible.sort(key=lambda m:(-m.groups,-m.free_dims,m.fit_nrmse,m.name))
    return feasible[0]


# ---------- shaping ----------
def shape_metric(U):
    D=d2mat(N); return U.T@U + 0.25*(D@U).T@(D@U)


def choose_shaped(info6,U,delta,batch=50000):
    M=shape_metric(U); out=np.empty((len(info6),9),dtype=np.uint8)
    for st in range(0,len(info6),batch):
        en=min(st+batch,len(info6)); b=info6[st:en]; best=np.full(len(b),np.inf); bestcw=np.empty((len(b),9),dtype=np.uint8)
        for sh in range(8):
            cw=hamming_encode(b,np.full(len(b),sh,dtype=np.uint8)); coeff=LEVELS[cw]*delta
            cost=np.einsum('bi,ij,bj->b',coeff,M,coeff,optimize=True); take=cost<best; best[take]=cost[take]; bestcw[take]=cw[take]
        out[st:en]=bestcw
    return out


def encode_table(info6, family, channels, mode):
    B,S=mode_basis(mode.name,mode.params); U=free_basis(B,S); groups=mode.groups; U=U[:,:groups*9]
    slots_per_segment=channels*groups; segments=math.ceil(len(info6)/slots_per_segment); total_slots=segments*slots_per_segment
    pad=np.zeros((total_slots,6),dtype=np.uint8); pad[:len(info6)]=info6
    code=np.empty((total_slots,9),dtype=np.uint8)
    for g in range(groups):
        mask=(np.arange(total_slots)%groups)==g; code[mask]=choose_shaped(pad[mask],U[:,g*9:(g+1)*9],mode.delta)
    coeff=LEVELS[code]*mode.delta; idx=np.arange(total_slots); gid=idx%groups; cid=(idx//groups)%channels
    perturb=np.zeros((total_slots,N),float)
    for g in range(groups):
        mask=gid==g; perturb[mask]=coeff[mask]@U[:,g*9:(g+1)*9].T
    base=baselines(family,channels); zbase=np.asarray([ty(y,mode.transform) for y in base]); z=zbase[cid]+perturb; y=np.round(ity(z,mode.transform),mode.decimals)
    pub=np.empty((segments*N,channels),float)
    for s in range(segments):
        for c in range(channels):
            slots=[(s*channels+c)*groups+g for g in range(groups)]
            zz=zbase[c].copy()
            for g,slot in enumerate(slots): zz += perturb[slot]
            pub[s*N:(s+1)*N,c]=np.round(ity(zz,mode.transform),mode.decimals)
    rawerr=rawtot=0
    for s in range(segments):
        for c in range(channels):
            yseg=pub[s*N:(s+1)*N,c]; zz=ty(yseg,mode.transform); beta,*_=np.linalg.lstsq(B,zz,rcond=None); res=zz-B@beta
            for g in range(groups):
                coeffhat=res@U[:,g*9:(g+1)*9]; raw=np.argmin(np.abs((coeffhat/mode.delta)[:,None]-LEVELS[None,:]),axis=1)
                slot=(s*channels+c)*groups+g
                if slot < len(info6): rawerr += int(np.sum(raw!=code[slot])); rawtot += 9
    return pub,segments,rawerr/max(rawtot,1)


def decode_table(pub, mode, channels, segments, valid_codewords):
    B,S=mode_basis(mode.name,mode.params); U=free_basis(B,S)[:,:mode.groups*9]; rec=[]
    for s in range(segments):
        for c in range(channels):
            y=pub[s*N:(s+1)*N,c]; z=ty(y,mode.transform); beta,*_=np.linalg.lstsq(B,z,rcond=None); res=z-B@beta
            for g in range(mode.groups):
                coeff=res@U[:,g*9:(g+1)*9]; raw=np.argmin(np.abs((coeff/mode.delta)[:,None]-LEVELS[None,:]),axis=1).astype(np.uint8)
                rec.append(hamming_correct(raw[None,:])[0,:6])
    return np.asarray(rec[:valid_codewords],dtype=np.uint8)


def decode_saved_package(npz_path, manifest_path):
    manifest=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    data=np.load(npz_path)
    total_words=sum(int(t['valid_codewords']) for t in manifest['tables'])
    recovered=np.empty((total_words,6),dtype=np.uint8)
    for t in manifest['tables']:
        mode=Mode(t['mode'],t['transform'],t['params'],t['fit_nrmse'],0,int(t['groups']),float(t['delta']),int(t['decimals']))
        pub=data[f"table_{t['table_id']}_y"]
        got=decode_table(pub,mode,int(t['channels']),int(t['segments']),int(t['valid_codewords']))
        st=int(t['codeword_start']); recovered[st:st+len(got)]=got
    return symbols_to_bytes(recovered.reshape(-1), int(manifest['payload_bit_length']))


def benchmark(payload_bytes,channels,outdir,threshold):
    outdir.mkdir(parents=True,exist_ok=True); payload=synthetic_payload(payload_bytes); syms,bitlen=bytes_to_symbols(payload); nwords=math.ceil(len(syms)/6); padded=np.pad(syms,(0,nwords*6-len(syms))).reshape(nwords,6)
    base=nwords//len(FAMILIES); rem=nwords%len(FAMILIES); counts=[base+(i<rem) for i in range(len(FAMILIES))]
    arrays={}; tables=[]; cursor=0; total_rows=0; raw_ser=[]; structural=[]
    for i,fam in enumerate(FAMILIES):
        Y0=baselines(fam,channels); mode=choose_mode(Y0,threshold); cnt=int(counts[i]); local=padded[cursor:cursor+cnt]; pub,segments,ser=encode_table(local,fam,channels,mode); arrays[f'table_{i}_x']=np.tile(X,segments); arrays[f'table_{i}_y']=pub
        cursor+=cnt; total_rows+=len(pub); raw_ser.append(ser)
        err=[]; rough=[]; drift=[]
        B,_=mode_basis(mode.name,mode.params)
        for s in range(segments):
            Y=pub[s*N:(s+1)*N].T
            for c in range(channels):
                err.append(nrmse(Y0[c],Y[c])); d0=np.diff(Y0[c],2); d1=np.diff(Y[c],2); base_r=float(np.sqrt(np.mean(d0*d0))); got_r=float(np.sqrt(np.mean(d1*d1))); rough.append((got_r/base_r) if base_r>1e-8 else float('nan')); z0=ty(Y0[c],mode.transform); z1=ty(Y[c],mode.transform); b0,*_=np.linalg.lstsq(B,z0,rcond=None); b1,*_=np.linalg.lstsq(B,z1,rcond=None); drift.append(np.linalg.norm(b1-b0)/max(np.linalg.norm(b0),1e-15))
        structural.append({'family':fam,'selected_mode':mode.name,'fit_nrmse':mode.fit_nrmse,'groups':mode.groups,'payload_bits_per_value_nominal':mode.groups*18/N,'mean_nrmse':float(np.mean(err)),'mean_roughness_ratio':(None if np.all(np.isnan(rough)) else float(np.nanmean(rough))),'mean_macro_drift':float(np.mean(drift)),'raw_symbol_error_rate':float(ser)})
        tables.append({'table_id':i,'family':fam,'mode':mode.name,'transform':mode.transform,'params':mode.params,'fit_nrmse':mode.fit_nrmse,'channels':channels,'points_per_block':N,'groups':mode.groups,'segments':segments,'valid_codewords':cnt,'codeword_start':cursor-cnt,'delta':mode.delta,'decimals':mode.decimals})
    np.savez_compressed(outdir/'published_package_v11.npz',**arrays)
    manifest={'version':'q8-mixed-package-v11','scope':'synthetic-only','q':8,'field':'GF(8)','code':'[9,7,3]_8','payload_bit_length':bitlen,'payload_bytes':payload_bytes,'payload_sha256':hashlib.sha256(payload).hexdigest(),'fit_threshold_nrmse':threshold,'tables':tables,'total_published_rows':total_rows,'total_published_numeric_values':total_rows*channels}
    (outdir/'manifest_v11.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    recovered=decode_saved_package(outdir/'published_package_v11.npz', outdir/'manifest_v11.json')
    mbytes=(outdir/'manifest_v11.json').stat().st_size; pbits=payload_bytes*8
    result={'version':'v11','payload_bytes':payload_bytes,'payload_sha256':hashlib.sha256(payload).hexdigest(),'decoded_sha256':hashlib.sha256(recovered).hexdigest(),'exact_recovery':recovered==payload,'channels_per_table':channels,'manifest_bytes':mbytes,'manifest_overhead_percent':100*mbytes/payload_bytes,'published_package_npz_bytes':(outdir/'published_package_v11.npz').stat().st_size,'total_published_rows':total_rows,'gross_bits_per_row':pbits/total_rows,'net_bits_per_row_after_manifest':(pbits-8*mbytes)/total_rows,'gross_bits_per_value':pbits/(total_rows*channels),'net_bits_per_value_after_manifest':(pbits-8*mbytes)/(total_rows*channels),'mean_raw_symbol_error_rate':float(np.mean(raw_ser)),'tables':structural}
    (outdir/'benchmark_v11_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); return result


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--payload-bytes',type=int,default=262144); ap.add_argument('--channels',type=int,default=16); ap.add_argument('--fit-threshold',type=float,default=5e-4); ap.add_argument('--out-dir',type=Path,default=Path('v11_out')); a=ap.parse_args(); print(json.dumps(benchmark(a.payload_bytes,a.channels,a.out_dir,a.fit_threshold),indent=2))

if __name__=='__main__': main()
