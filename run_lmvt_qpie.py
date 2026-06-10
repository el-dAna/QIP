"""Does QPIE augment the ACTUAL SOTA model (LITEMVTime / LMVT) past SOTA?

For each UEA dataset, train the predefined aeon LITEMVTime classifier
(LITETimeClassifier(use_litemv=True), 5 nets x 1500 epochs) on three inputs:
  (raw)        raw 3-channel series                      -> must reproduce published LMVT
  (qpie_all)   ALL 5 QPIE schemes concatenated (120 ch)  -> the full QPIE representation
  (ensemble)   soft-vote of LMVT(raw) + LMVT(qpie_all)   -> "QPIE + SOTA model"
and compare to the published per-dataset SOTA.

VALIDITY GATE: LMVT(raw) must reproduce the published LMVT number; printed every
dataset. If it does, the QPIE/ensemble comparison is sound; if not, flagged.

CORRECTNESS: predefined architecture (not reconstructed); aeon Python-3.13 guard
neutralized (TF 2.20 supports 3.13); train-only scaler; per-sample CSE (audited);
amplitudes normalized; finite-feature assert; soft-vote asserts matching class order.
Results written incrementally to _lmvt_results.json after every config.
"""
import aeon.utils.validation._dependencies as _dep
_dep._check_python_version = lambda *a, **k: None       # aeon guard is conservative; TF2.20 supports 3.13

import ast, json, os, time, numpy as np
import matplotlib; matplotlib.use("Agg")
from aeon.datasets import load_classification
from aeon.classification.deep_learning import LITETimeClassifier

# ---------------- load + audit QPIE encoders from the notebook ----------------
nb = json.load(open("Phase7_UWave.ipynb")); cells = nb["cells"]; G = {"__name__": "__main__"}
EXP = {"load_uwave","load_classification","to_patches","run_dataset","train_cnn","train_gpu",
       "train_lr_bootstrap","agg","label_binarize","multi_basis","multi_basis_n","fit","transform",
       "show","savefig","_ext_and_agg","_ext_cse","_ext_concat","_ext_cse_concat",
       "_ext_and_agg_n","_ext_concat_n","_ext_cse_n_concat"}
def _calls(n):
    s=set()
    for x in ast.walk(n):
        if isinstance(x,ast.Call):
            f=x.func; s.add(f.id if isinstance(f,ast.Name) else getattr(f,"attr",""))
    return s
def keep(n):
    if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): return True
    if isinstance(n,ast.Assign): return not (_calls(n)&EXP)
    return False
for i in [2,3,5,6,7,13,25,27]:
    src="".join(cells[i]["source"])
    for node in ast.parse(src).body:
        if not keep(node): continue
        seg=ast.get_source_segment(src,node)
        if not seg: continue
        hard=isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))
        try: exec(compile(seg,f"<c{i}>","exec"),G)
        except NameError:
            if hard: raise
import torch; G.setdefault("STRIDE_FINE",4)
RCS=G["RobustChannelScaler"]; to_patches=G["to_patches"]; SF=G["STRIDE_FINE"]
sfc=G["_seq_from_concat_n"]; ecn=G["_ext_concat_n"]; ecse=G["_ext_cse_n_concat"]
AMP={"Sep":G["_amps_sep_n"],"CRyE":G["_amps_crye_n"],"GBE":G["_amps_gbe_n"],"CP-2L":G["_amps_cp_2L_n"]}
_amps_sep_n=G["_amps_sep_n"]; SCHEMES=["Sep","CRyE","GBE","CP-2L","CSE"]

def qpie_all(P):
    """(N,P,3) scaled patches -> (N,120,P): all 5 schemes' 24-dim features stacked."""
    parts=[]
    for s in SCHEMES:
        seq = sfc(lambda Ps:ecse(Ps,3),P,24) if s=="CSE" else sfc(lambda Ps:ecn(Ps,AMP[s],3),P,24)
        parts.append(seq.transpose(0,2,1))               # (N,24,P)
    X=np.concatenate(parts,axis=1).astype(np.float32)     # (N,120,P)
    assert np.isfinite(X).all(), "non-finite QPIE-all features"
    return X

def check_norm(P):
    a=_amps_sep_n(P[:4].reshape(-1,3),3); n=(np.abs(a)**2).sum(1)
    assert np.allclose(n,1.0,atol=1e-6), f"amps not normalized: {n[:3]}"

def lmvt():
    return LITETimeClassifier(use_litemv=True, n_classifiers=5, n_epochs=1500,
                              batch_size=64, random_state=0, verbose=False)

# published LMVT (reproduction target) and best SOTA (verdict bar) per dataset
REF = {  # name: (lmvt_published, sota_best, sota_label)
 "UWaveGestureLibrary":   (0.847, 0.909, "IT"),
 "Epilepsy":              (0.993, 0.993, "LMVT/IT"),
 "Handwriting":           (0.400, 0.657, "IT bake-off"),
 "EthanolConcentration":  (0.692, 0.692, "LMVT"),
 "CharacterTrajectories": (0.996, 0.996, "LMVT"),
}
RESULTS_FILE="_lmvt_results.json"
results = json.load(open(RESULTS_FILE)) if os.path.exists(RESULTS_FILE) else {}

def save():
    json.dump(results, open(RESULTS_FILE,"w"), indent=2)

def acc_proba(clf, Xtr, ytr, Xte, yte):
    t=time.time(); clf.fit(Xtr,ytr); ft=time.time()-t
    proba=clf.predict_proba(Xte)
    pred=clf.classes_[proba.argmax(1)]
    return float((pred==yte).mean()), proba, clf.classes_, ft

print("="*96); print("LMVT (LITEMVTime) + QPIE-all  vs published SOTA   [predefined aeon, 5 nets x 1500 ep]"); print("="*96, flush=True)
for nm in ["UWaveGestureLibrary","Epilepsy","Handwriting","EthanolConcentration","CharacterTrajectories"]:
    if nm in results and results[nm].get("done"):
        print(f"\n### {nm}: already done, skipping"); continue
    lmvt_pub, sota, sota_lab = REF[nm]
    Xtr,ytr=load_classification(nm,split="train"); Xte,yte=load_classification(nm,split="test")
    Xtr=Xtr.astype(np.float32); Xte=Xte.astype(np.float32)
    print(f"\n### {nm}  train{Xtr.shape} test{Xte.shape}  K={len(np.unique(ytr))}  "
          f"LMVT_pub={lmvt_pub}  SOTA={sota}({sota_lab})", flush=True)
    R={"train":list(Xtr.shape),"K":int(len(np.unique(ytr))),"lmvt_pub":lmvt_pub,"sota":sota}

    # --- LMVT(raw): validity gate ---
    a_raw,p_raw,cls_raw,ft = acc_proba(lmvt(),Xtr,ytr,Xte,yte)
    repro = "OK" if abs(a_raw-lmvt_pub)<=0.03 else "MISMATCH"
    R["raw"]=a_raw; R["raw_repro"]=repro
    print(f"    LMVT(raw)       {a_raw:.4f}   (vs published {lmvt_pub} -> {repro})   fit {ft/60:.1f}min", flush=True)
    save_partial = dict(results); save_partial[nm]=R; results[nm]=R; save()

    # --- LMVT(QPIE-all 120ch) ---
    sc=RCS().fit(Xtr); Ptr=to_patches(sc.transform(Xtr),stride=SF); Pte=to_patches(sc.transform(Xte),stride=SF)
    check_norm(Ptr)
    Qtr=qpie_all(Ptr); Qte=qpie_all(Pte)
    a_q,p_q,cls_q,ft = acc_proba(lmvt(),Qtr,ytr,Qte,yte)
    R["qpie_all"]=a_q
    print(f"    LMVT(QPIE-all)  {a_q:.4f}   (120ch x P={Ptr.shape[1]})   fit {ft/60:.1f}min", flush=True)
    results[nm]=R; save()

    # --- soft-vote ensemble (QPIE + SOTA model) ---
    assert list(cls_raw)==list(cls_q), "class order mismatch; cannot soft-vote"
    ens=(p_raw+p_q)/2.0
    a_ens=float((cls_raw[ens.argmax(1)]==yte).mean())
    R["ensemble"]=a_ens
    beat=[k for k,v in [("qpie_all",a_q),("ensemble",a_ens)] if v>sota]
    R["beats_sota"]=beat; R["done"]=True
    print(f"    ENSEMBLE        {a_ens:.4f}   vs SOTA {sota}: qpie {a_q-sota:+.3f}, ens {a_ens-sota:+.3f}  "
          f"{'BEATS: '+','.join(beat) if beat else 'none beat SOTA'}", flush=True)
    results[nm]=R; save()

print("\n"+"="*96); print("DONE — see _lmvt_results.json"); print("="*96)
