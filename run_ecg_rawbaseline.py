"""Same-representation classical baseline for the ECG paper (harden-the-null).

Feeds the RAW 3-channel ECG (the representation BEFORE the quantum encoding) to
multivariate ROCKET, identical splits/scaler/metric to the QPIE pipeline, and
reports the official N/A/O macro-F1 + per-class F1 + confusion. This is the
ceiling the QPIE-CNN (best PA-CSE 0.670) is measured against: if ROCKET-on-raw
>> 0.670, the quantum feature map is lossy (the UWave verdict, now on ECG).

Channels, RobustChannelScaler, stratified seed-0 split, and macro_f1_nao are
re-implemented verbatim from Phase8_PhysioNet2017_ECG.ipynb (cells 4/6/8/14).
ROCKET trained on train+val (all non-test), evaluated on the same test split.
SMOKE=1 -> tiny config (200 kernels, 400-case subset, 1 seed) to validate plumbing.

Env: msc_venv (aeon 1.4). Results -> _ecg_rawbaseline.json (resumable per-seed).
"""
import os, json, time, numpy as np
from pathlib import Path
from scipy.signal import butter, filtfilt, hilbert
import pywt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeClassifierCV
from sklearn.metrics import f1_score, balanced_accuracy_score, confusion_matrix
from aeon.transformations.collection.convolution_based import Rocket

SMOKE = os.environ.get("SMOKE") == "1"
PROJECT = Path("/Users/eldana/Documents/Quantum/Thesis/QIP")
CACHE = PROJECT / "data/af-classification-from-a-short-single-lead-ecg-recording-the-physionet-computing-in-cardiology-challenge-2017-1.0.0/cached.npz"
FS, TARGET_LEN = 300, 9000
NAO = [0, 1, 2]                         # N, A, O ; 3 = noise (excluded from macro-F1)
CLASS_NAMES = ["N", "A", "O", "noise"]
N_KERNELS = 200 if SMOKE else 10000
N_SEEDS = 1 if SMOKE else 5

# ---- pipeline pieces, verbatim from the notebook ----
def three_channels(x):
    c1 = x.astype(np.float32)
    c2 = np.diff(c1, prepend=c1[0]).astype(np.float32)
    coeffs = pywt.wavedec(c1, "db4", level=5)
    rec = [np.zeros_like(c) for c in coeffs]; rec[4] = coeffs[4]      # cD4 ~9-18 Hz
    band = pywt.waverec(rec, "db4")[: len(c1)]
    c3 = np.abs(hilbert(band)).astype(np.float32)
    return np.stack([c1, c2, c3], axis=-1)

class RobustChannelScaler:
    def fit(self, X):
        flat = X.reshape(-1, X.shape[-1])
        self.q5 = np.quantile(flat, 0.05, axis=0); self.q95 = np.quantile(flat, 0.95, axis=0)
        return self
    def transform(self, X):
        return np.clip((X - self.q5) / (self.q95 - self.q5 + 1e-8), 0.0, 1.0).astype(np.float32)

def stratified_split(y, frac=(0.6, 0.2, 0.2), seed=0):
    s1 = StratifiedShuffleSplit(1, test_size=frac[1]+frac[2], random_state=seed)
    itr, irest = next(s1.split(np.zeros_like(y), y))
    s2 = StratifiedShuffleSplit(1, test_size=frac[2]/(frac[1]+frac[2]), random_state=seed)
    iva, ite = next(s2.split(np.zeros_like(y[irest]), y[irest]))
    return itr, irest[iva], irest[ite]

def macro_f1_nao(yt, yp):
    return f1_score(yt, yp, labels=NAO, average="macro", zero_division=0)

# ---- build raw 3-channel representation (channels-first for aeon) ----
print(f"[{'SMOKE' if SMOKE else 'FULL'}] loading cache ...", flush=True)
d = np.load(CACHE); X_raw, y = d["X"], d["y"]
itr, iva, ite = stratified_split(y, seed=0)
if SMOKE:
    keep = np.concatenate([itr[:250], ite[:150]]);
    itr = itr[:250]; ite = ite[:150]; iva = iva[:50]

t0 = time.time()
X3 = np.stack([three_channels(x) for x in X_raw], axis=0)            # (B, 9000, 3)
sc = RobustChannelScaler().fit(X3[itr]); X3 = sc.transform(X3)
Xcf = np.transpose(X3, (0, 2, 1))                                    # (B, 3, 9000) channels-first
print(f"channels built {X3.shape} in {time.time()-t0:.0f}s", flush=True)

itrva = np.concatenate([itr, iva])
Xtr, ytr = Xcf[itrva], y[itrva]
Xte, yte = Xcf[ite], y[ite]
print(f"train {Xtr.shape} test {Xte.shape}  | test class counts {np.bincount(yte, minlength=4)}", flush=True)

RES = PROJECT / "_ecg_rawbaseline.json"
results = json.load(open(RES)) if RES.exists() else {"seeds": {}, "config": {}}
results["config"] = {"n_kernels": N_KERNELS, "model": "Rocket+RidgeClassifierCV(balanced)",
                     "train": "tr+va", "smoke": SMOKE, "channels": "raw bandpass/diff/hilbert-cD4"}

for s in range(N_SEEDS):
    if str(s) in results["seeds"]:
        print(f"seed {s} cached, skip"); continue
    t = time.time()
    rk = Rocket(n_kernels=N_KERNELS, random_state=s, n_jobs=-1)
    Ftr = rk.fit_transform(Xtr); Fte = rk.transform(Xte)
    ss = StandardScaler(with_mean=False).fit(Ftr)
    clf = RidgeClassifierCV(alphas=np.logspace(-3, 3, 10), class_weight="balanced")
    clf.fit(ss.transform(Ftr), ytr)
    pred = clf.predict(ss.transform(Fte))
    mf1 = macro_f1_nao(yte, pred)
    bacc = balanced_accuracy_score(yte, pred)
    per = f1_score(yte, pred, labels=[0, 1, 2, 3], average=None, zero_division=0)
    cm = confusion_matrix(yte, pred, labels=[0, 1, 2, 3])
    results["seeds"][str(s)] = {"macro_f1_nao": float(mf1), "bacc": float(bacc),
                                "per_class_f1": {CLASS_NAMES[i]: float(per[i]) for i in range(4)},
                                "confusion": cm.tolist(), "fit_min": (time.time()-t)/60}
    json.dump(results, open(RES, "w"), indent=2)
    print(f"seed {s}: macro-F1(N/A/O)={mf1:.4f}  BAcc={bacc:.4f}  "
          f"perF1 N/A/O/noise={[f'{per[i]:.3f}' for i in range(4)]}  ({(time.time()-t)/60:.1f}min)", flush=True)

f1s = [v["macro_f1_nao"] for v in results["seeds"].values()]
print(f"\n=== ROCKET on raw 3-ch ECG: macro-F1(N/A/O) = {np.mean(f1s):.4f} ± {np.std(f1s):.4f}  "
      f"(n={len(f1s)} seeds) ===")
print(f"   vs QPIE-CNN best (PA-CSE) 0.670 | published SOTA 0.83")
print("DONE -> _ecg_rawbaseline.json")
