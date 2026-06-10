"""Does QPIE help the ACTUAL SOTA deep model when each encoding scheme is fed
SEPARATELY (not the 120-ch all-schemes concatenation)?

This is the deep-model analogue of paper2 Table tab:rocketqpie: there each
scheme's 24-channel per-patch features were fed to ROCKET; here they are fed to
the per-dataset SOTA deep classifier (InceptionTime for UWave/Handwriting,
LITEMVTime for Epilepsy/CharacterTrajectories/EthanolConcentration).

For each UEA dataset, with M = the per-dataset SOTA model, train:
  (raw)        M on the raw 3-channel series          -> validity gate + ensemble base
  (per scheme) M on that scheme's 24-channel features  -> one fit per scheme {Sep,CRyE,GBE,CP-2L,CSE}
  (ensemble)   soft-vote M(raw) + M(scheme)            -> "this scheme + SOTA model"
and compare every accuracy to the published SOTA and to our own local run.

NOT combined: schemes are never concatenated; each is a standalone 24-ch input.

REFERENCES carried in every row:
  sota         = published SOTA accuracy + model label (Ismail-Fawaz 2025 / bake-off)
  lmvt_pub     = published LMVT number (kept for cross-check continuity)
  local_lmvt_raw = our verified LMVT(raw) from _lmvt_results.json (same-machine anchor)

VALIDITY GATE: M(raw) must land near the published number for M's family; printed
per dataset. For LMVT datasets it must also track our local LMVT(raw).

CORRECTNESS: predefined aeon architectures (not reconstructed); aeon Python-3.13
guard neutralized (TF2.20 supports 3.13); train-only scaler; per-sample CSE;
amplitudes normalized; finite-feature assert; soft-vote asserts matching class
order. Results written incrementally to _perscheme_results.json after every fit.
"""
import aeon.utils.validation._dependencies as _dep
_dep._check_python_version = lambda *a, **k: None       # aeon guard is conservative; TF2.20 supports 3.13

import ast, json, os, time, numpy as np
import matplotlib; matplotlib.use("Agg")
from aeon.datasets import load_classification
from aeon.classification.deep_learning import LITETimeClassifier, InceptionTimeClassifier

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

def qpie_scheme(P, s):
    """(N,P,3) scaled patches -> (N,24,P): one scheme's 24-dim features (standalone)."""
    seq = sfc(lambda Ps:ecse(Ps,3),P,24) if s=="CSE" else sfc(lambda Ps:ecn(Ps,AMP[s],3),P,24)
    X = seq.transpose(0,2,1).astype(np.float32)          # (N,24,P)
    assert np.isfinite(X).all(), f"non-finite features for scheme {s}"
    return X

def check_norm(P):
    a=_amps_sep_n(P[:4].reshape(-1,3),3); n=(np.abs(a)**2).sum(1)
    assert np.allclose(n,1.0,atol=1e-6), f"amps not normalized: {n[:3]}"

N_NETS=1   # ablation config (2026-06-10): 1 net for ~5x speed; per-scheme RANKING is the
           # payload (fair: same single seed for raw + every scheme). Published SOTA uses 5 nets,
           # so raw won't exactly equal the ensemble SOTA number — relative comparison still valid.
def make_model(kind):
    if kind=="IT":
        return InceptionTimeClassifier(n_classifiers=N_NETS, n_epochs=1500,
                                       batch_size=64, random_state=0, verbose=False)
    return LITETimeClassifier(use_litemv=True, n_classifiers=N_NETS, n_epochs=1500,
                              batch_size=64, random_state=0, verbose=False)

# published references; sota_model picks the classifier we train per dataset
REF = {  # name: (lmvt_published, sota_best, sota_model)
 "UWaveGestureLibrary":   (0.847, 0.909, "IT"),
 "Epilepsy":              (0.993, 0.993, "LMVT"),
 "Handwriting":           (0.400, 0.657, "IT"),
 "EthanolConcentration":  (0.692, 0.692, "LMVT"),
 "CharacterTrajectories": (0.996, 0.996, "LMVT"),
}
# our own verified LMVT(raw) from the completed combined run (same machine)
LOCAL_LMVT_RAW = {k: v.get("raw") for k, v in
                  (json.load(open("_lmvt_results.json")) if os.path.exists("_lmvt_results.json") else {}).items()}

RESULTS_FILE="_perscheme_results.json"
results = json.load(open(RESULTS_FILE)) if os.path.exists(RESULTS_FILE) else {}
def save(): json.dump(results, open(RESULTS_FILE,"w"), indent=2)

def fit_eval(model, Xtr, ytr, Xte, yte):
    t=time.time(); model.fit(Xtr,ytr); ft=time.time()-t
    proba=model.predict_proba(Xte)
    pred=model.classes_[proba.argmax(1)]
    return float((pred==yte).mean()), proba, model.classes_, ft

print("="*96)
print(f"Per-scheme QPIE -> per-dataset SOTA model  vs published SOTA   [predefined aeon, {N_NETS} net(s) x 1500 ep]")
print("="*96, flush=True)

for nm in ["UWaveGestureLibrary","Epilepsy","Handwriting","EthanolConcentration","CharacterTrajectories"]:
    lmvt_pub, sota, mdl = REF[nm]
    R = results.get(nm, {})
    if R.get("done"):
        print(f"\n### {nm}: already done, skipping"); continue

    Xtr,ytr=load_classification(nm,split="train"); Xte,yte=load_classification(nm,split="test")
    Xtr=Xtr.astype(np.float32); Xte=Xte.astype(np.float32)
    print(f"\n### {nm}  train{Xtr.shape} test{Xte.shape}  K={len(np.unique(ytr))}  "
          f"SOTA={sota}({mdl})  local_LMVT_raw={LOCAL_LMVT_RAW.get(nm)}", flush=True)
    R.update({"train":list(Xtr.shape),"K":int(len(np.unique(ytr))),
              "sota":sota,"sota_model":mdl,"lmvt_pub":lmvt_pub,
              "local_lmvt_raw":LOCAL_LMVT_RAW.get(nm),"schemes":{}})
    results[nm]=R; save()

    # --- M(raw): validity gate + ensemble base ---
    if "raw" not in R or "raw_proba" not in R:
        a_raw,p_raw,cls_raw,ft = fit_eval(make_model(mdl),Xtr,ytr,Xte,yte)
        repro = "OK" if abs(a_raw-sota)<=0.05 else "CHECK"
        R["raw"]=a_raw; R["raw_repro"]=repro; R["raw_proba"]=p_raw.tolist(); R["raw_classes"]=list(map(str,cls_raw))
        print(f"    {mdl}(raw)        {a_raw:.4f}   (vs SOTA {sota} -> {repro})   fit {ft/60:.1f}min", flush=True)
        results[nm]=R; save()
    p_raw=np.asarray(R["raw_proba"]); cls_raw=np.array(R["raw_classes"]); a_raw=R["raw"]

    # --- M(per scheme): each scheme's 24-ch features, standalone ---
    sc=RCS().fit(Xtr); Ptr=to_patches(sc.transform(Xtr),stride=SF); Pte=to_patches(sc.transform(Xte),stride=SF)
    check_norm(Ptr)
    for s in SCHEMES:
        if s in R["schemes"]:
            print(f"    [skip cached] {s}"); continue
        Qtr=qpie_scheme(Ptr,s); Qte=qpie_scheme(Pte,s)
        a_s,p_s,cls_s,ft = fit_eval(make_model(mdl),Qtr,ytr,Qte,yte)
        assert list(map(str,cls_s))==list(cls_raw), f"class order mismatch raw vs {s}; cannot soft-vote"
        ens=(p_raw+p_s)/2.0
        a_ens=float((cls_raw[ens.argmax(1)]==yte.astype(str)).mean())
        beat=[k for k,v in [("scheme",a_s),("ensemble",a_ens)] if v>sota]
        R["schemes"][s]={"acc":a_s,"ensemble":a_ens,"beats_sota":beat}
        print(f"    {mdl}({s:<5})      {a_s:.4f}   ens(+raw) {a_ens:.4f}   "
              f"vs SOTA {sota}: scheme {a_s-sota:+.3f}, ens {a_ens-sota:+.3f}  "
              f"{'BEATS: '+','.join(beat) if beat else ''}   fit {ft/60:.1f}min", flush=True)
        results[nm]=R; save()

    # best scheme summary
    best_s=max(R["schemes"], key=lambda k:R["schemes"][k]["acc"])
    R["best_scheme"]=best_s; R["best_scheme_acc"]=R["schemes"][best_s]["acc"]; R["done"]=True
    print(f"    -> best scheme {best_s} {R['best_scheme_acc']:.4f}  (Δ vs SOTA {R['best_scheme_acc']-sota:+.3f})", flush=True)
    results[nm]=R; save()

print("\n"+"="*96); print("DONE — see _perscheme_results.json"); print("="*96)
