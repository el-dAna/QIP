"""Arm 2 scaffold + He baseline (Phase 1, locked design from thesis_spine_2026.md).

Purpose: stand up the FIXED classical scaffold for the weight-init study and run the
He baseline so we can lock (a) first-hidden-layer width H and (b) the macro-F1 threshold
for the epochs-to-threshold metric. NO quantum here yet — the only thing Arm 2 will vary
later is the fc1 (first hidden layer) init; everything in this file is held fixed.

Design choices (pre-registered):
- Input = a FIXED classical feature vector (24 = 8 robust stats x 3 channels), NOT the
  QPIE-encoded features. Keeps Arm 2 pure: the only quantum element later is the init
  sampler, so any effect is attributable to initialization alone (encoding is Arm 1).
- 3-channel rep + RobustChannelScaler + stratified split reused VERBATIM from
  run_ecg_rawbaseline.py (cells 4/6/8/14 of Phase8 notebook). Split seed FIXED at 0 across
  everything; the experiment seed varies ONLY init RNG + minibatch shuffling.
- Metric = macro-F1 over N/A/O (noise excluded), matching the ECG paper.

Env: msc_venv (torch 2.9 + MPS). Results -> _arm2_scaffold.json (resumable per (H,seed)).
SMOKE=1 -> tiny config to validate plumbing.
"""
import os, json, time, numpy as np
from pathlib import Path
from scipy.signal import hilbert
import pywt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, balanced_accuracy_score
import torch, torch.nn as nn

SMOKE = os.environ.get("SMOKE") == "1"
PROJECT = Path("/Users/eldana/Documents/Quantum/Thesis/QIP")
CACHE = PROJECT / "data/af-classification-from-a-short-single-lead-ecg-recording-the-physionet-computing-in-cardiology-challenge-2017-1.0.0/cached.npz"
FEAT_CACHE = PROJECT / "_arm2_features.npz"
RES = PROJECT / "_arm2_scaffold.json"
NAO = [0, 1, 2]
CLASS_NAMES = ["N", "A", "O", "noise"]
N_CLS = 4
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

H_GRID = [32] if SMOKE else [32, 64, 128]
N_SEEDS = 2 if SMOKE else 5
EPOCHS = 15 if SMOKE else 120
BATCH = 128
LR = 1e-3

# ---- pipeline pieces, verbatim from run_ecg_rawbaseline.py ----
def three_channels(x):
    c1 = x.astype(np.float32)
    c2 = np.diff(c1, prepend=c1[0]).astype(np.float32)
    coeffs = pywt.wavedec(c1, "db4", level=5)
    rec = [np.zeros_like(c) for c in coeffs]; rec[4] = coeffs[4]
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

# ---- 24-d fixed feature vector: 8 robust stats x 3 channels ----
def features(X3):                                          # X3: (B, T, 3) scaled
    m = X3.mean(1); sd = X3.std(1); med = np.median(X3, 1)
    q = np.quantile(X3, [0.10, 0.25, 0.75, 0.90], axis=1)  # (4, B, 3)
    iqr = q[2] - q[1]; q10 = q[0]; q90 = q[3]
    rms = np.sqrt((X3 ** 2).mean(1))
    skew = (((X3 - m[:, None, :]) / (sd[:, None, :] + 1e-8)) ** 3).mean(1)
    return np.concatenate([m, sd, med, iqr, q10, q90, rms, skew], axis=1).astype(np.float32)  # (B, 24)

def build_features():
    if FEAT_CACHE.exists():
        d = np.load(FEAT_CACHE); return d["Xf"], d["y"], d["itr"], d["iva"], d["ite"]
    print("building 24-d features from raw ECG ...", flush=True)
    d = np.load(CACHE); X_raw, y = d["X"], d["y"]
    itr, iva, ite = stratified_split(y, seed=0)
    t0 = time.time()
    X3 = np.stack([three_channels(x) for x in X_raw], axis=0)      # (B, 9000, 3)
    sc = RobustChannelScaler().fit(X3[itr]); X3 = sc.transform(X3)
    Xf = features(X3)                                              # (B, 24)
    np.savez(FEAT_CACHE, Xf=Xf, y=y, itr=itr, iva=iva, ite=ite)
    print(f"features {Xf.shape} built in {time.time()-t0:.0f}s -> {FEAT_CACHE.name}", flush=True)
    return Xf, y, itr, iva, ite

# ---- small MLP; fc1 (first hidden layer) is the only thing Arm 2 will re-init ----
class MLP(nn.Module):
    def __init__(self, d_in, H, n_cls):
        super().__init__()
        self.fc1 = nn.Linear(d_in, H)
        self.fc2 = nn.Linear(H, n_cls)
    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))

def init_fc1(model, kind, seed):
    torch.manual_seed(seed)
    if kind == "he":
        nn.init.kaiming_normal_(model.fc1.weight, nonlinearity="relu")
        nn.init.zeros_(model.fc1.bias)
    else:
        raise ValueError(kind)
    return model

def train_eval(Xtr, ytr, Xte, yte, Xva, yva, H, seed, cls_w):
    torch.manual_seed(seed); np.random.seed(seed)
    model = MLP(Xtr.shape[1], H, N_CLS).to(DEVICE)
    model = init_fc1(model, "he", seed)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    lossf = nn.CrossEntropyLoss(weight=cls_w.to(DEVICE))
    Xtr_t = torch.tensor(Xtr, device=DEVICE); ytr_t = torch.tensor(ytr, device=DEVICE)
    Xva_t = torch.tensor(Xva, device=DEVICE); Xte_t = torch.tensor(Xte, device=DEVICE)
    n = len(Xtr_t)
    val_curve, best_val, best_test, best_ep = [], -1.0, -1.0, -1
    for ep in range(EPOCHS):
        model.train()
        perm = torch.randperm(n, device=DEVICE)
        for i in range(0, n, BATCH):
            idx = perm[i:i+BATCH]
            opt.zero_grad()
            loss = lossf(model(Xtr_t[idx]), ytr_t[idx])
            loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            vp = model(Xva_t).argmax(1).cpu().numpy()
            vf1 = macro_f1_nao(yva, vp)
        val_curve.append(float(vf1))
        if vf1 > best_val:
            best_val = float(vf1); best_ep = ep
            with torch.no_grad():
                tp = model(Xte_t).argmax(1).cpu().numpy()
            best_test = float(macro_f1_nao(yte, tp))
            best_test_bacc = float(balanced_accuracy_score(yte, tp))
    return {"val_curve": val_curve, "best_val_f1": best_val, "best_ep": best_ep,
            "test_f1": best_test, "test_bacc": best_test_bacc}

# ---- run ----
Xf, y, itr, iva, ite = build_features()
fsc = StandardScaler().fit(Xf[itr])
Xf = fsc.transform(Xf).astype(np.float32)
if SMOKE:
    itr = itr[:600]; iva = iva[:200]; ite = ite[:200]
Xtr, ytr = Xf[itr], y[itr]; Xva, yva = Xf[iva], y[iva]; Xte, yte = Xf[ite], y[ite]
counts = np.bincount(ytr, minlength=N_CLS)
cls_w = torch.tensor(len(ytr) / (N_CLS * np.maximum(counts, 1)), dtype=torch.float32)
print(f"[{'SMOKE' if SMOKE else 'FULL'}] dev={DEVICE} train {Xtr.shape} val {Xva.shape} "
      f"test {Xte.shape} | train counts {counts}", flush=True)

results = json.load(open(RES)) if RES.exists() else {"runs": {}, "config": {}}
results["config"] = {"init": "he", "feat": "24=8stats x 3ch", "epochs": EPOCHS, "batch": BATCH,
                     "lr": LR, "H_grid": H_GRID, "n_seeds": N_SEEDS, "smoke": SMOKE,
                     "split": "stratified seed0 60/20/20", "metric": "macro_f1_nao"}
for H in H_GRID:
    for s in range(N_SEEDS):
        key = f"H{H}_s{s}"
        if key in results["runs"]:
            print(f"{key} cached, skip"); continue
        t = time.time()
        r = train_eval(Xtr, ytr, Xte, yte, Xva, yva, H, s, cls_w)
        r["sec"] = time.time() - t
        results["runs"][key] = r
        json.dump(results, open(RES, "w"), indent=2)
        print(f"{key}: best_val_f1={r['best_val_f1']:.4f}@ep{r['best_ep']} "
              f"test_f1={r['test_f1']:.4f} bacc={r['test_bacc']:.4f} ({r['sec']:.1f}s)", flush=True)

# ---- summary: pick H by mean test_f1, report threshold candidates ----
print("\n=== He baseline summary ===")
for H in H_GRID:
    tf = [results["runs"][f"H{H}_s{s}"]["test_f1"] for s in range(N_SEEDS)]
    bv = [results["runs"][f"H{H}_s{s}"]["best_val_f1"] for s in range(N_SEEDS)]
    print(f"H={H:3d}: test_f1 {np.mean(tf):.4f} +/- {np.std(tf):.4f} | best_val {np.mean(bv):.4f}")
print("DONE -> _arm2_scaffold.json")
