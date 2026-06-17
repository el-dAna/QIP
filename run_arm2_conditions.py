"""Arm 2 — the 6 init conditions on the locked scaffold (Phase 1).

Mapping (signed off 2026-06-17): the first-layer weight matrix fc1 (H x 24) is drawn so
each hidden unit's 24-weight vector ~ N(0, Sigma). Sigma encodes "which weights move
together". A 3-qubit circuit (the SAME ladder as Arm 1) sets a 3x3 channel-correlation
matrix C from the qubit-qubit connected correlators; we expand it to the 24x24 weight
covariance by the same-statistic rule  Sigma = I_8 (kron) C  (8 stats x 3 channels, so
same-statistic weights across channels correlate by C, different statistics independent).
Every condition is rescaled to He per-weight std, so the ONLY thing that varies is the
correlation structure (the entanglement signature), never the spread.

Conditions:
  he        - kaiming_normal (independent Gaussian, He var) ............. reference / no-corr
  xavier    - xavier_normal ............................................. classical baseline
  orthogonal- orthogonal_ ............................................... classical baseline
  sep       - covariance sampler with C=I .............................. VALIDATION (expect ~ he)
  blind     - entangling circuit, FIXED angles (corr not from data) .... data-blind entangled
  aware     - entangling circuit, angles = (pi/2)|rho_ij| from data .... DATA-AWARE (headline)

Because spread is held at He, He/Sep/marginal-matched coincide -> He IS the marginal-matched
control. Deciders: aware vs he (do correlations help?), aware vs blind (does data-matching help?).

DATASET=uwave (headline, coupling 0.44) | ecg (null anchor, coupling ~0.12).
Env: msc_venv. Results -> _arm2_cond_<ds>.json. SMOKE=1 -> tiny.
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
DS = os.environ.get("DATASET", "uwave")
PROJECT = Path("/Users/eldana/Documents/Quantum/Thesis/QIP")
ECG_CACHE = PROJECT / "data/af-classification-from-a-short-single-lead-ecg-recording-the-physionet-computing-in-cardiology-challenge-2017-1.0.0/cached.npz"
RES = PROJECT / f"_arm2_cond_{DS}.json"
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
H, EPOCHS, BATCH, LR = 64, (15 if SMOKE else 120), 128, 1e-3
N_SEEDS = 2 if SMOKE else 5
CONDS = ["he", "xavier", "orthogonal", "sep", "blind", "aware"]

# ---------- shared pipeline pieces ----------
def three_channels(x):
    c1 = x.astype(np.float32); c2 = np.diff(c1, prepend=c1[0]).astype(np.float32)
    co = pywt.wavedec(c1, "db4", level=5); rec = [np.zeros_like(c) for c in co]; rec[4] = co[4]
    band = pywt.waverec(rec, "db4")[: len(c1)]; c3 = np.abs(hilbert(band)).astype(np.float32)
    return np.stack([c1, c2, c3], axis=-1)

class RobustChannelScaler:
    def fit(self, X):
        f = X.reshape(-1, X.shape[-1])
        self.q5 = np.quantile(f, 0.05, axis=0); self.q95 = np.quantile(f, 0.95, axis=0); return self
    def transform(self, X):
        return np.clip((X - self.q5) / (self.q95 - self.q5 + 1e-8), 0.0, 1.0).astype(np.float32)

def stratified_split(y, frac=(0.6, 0.2, 0.2), seed=0):
    s1 = StratifiedShuffleSplit(1, test_size=frac[1]+frac[2], random_state=seed)
    itr, irest = next(s1.split(np.zeros_like(y), y))
    s2 = StratifiedShuffleSplit(1, test_size=frac[2]/(frac[1]+frac[2]), random_state=seed)
    iva, ite = next(s2.split(np.zeros_like(y[irest]), y[irest]))
    return itr, irest[iva], irest[ite]

def feats(X3):                                            # X3 (n, T, 3) -> (n, 24)
    m = X3.mean(1); sd = X3.std(1); med = np.median(X3, 1)
    q = np.quantile(X3, [0.10, 0.25, 0.75, 0.90], axis=1)
    rms = np.sqrt((X3 ** 2).mean(1))
    skew = (((X3 - m[:, None, :]) / (sd[:, None, :] + 1e-8)) ** 3).mean(1)
    return np.concatenate([m, sd, med, q[2]-q[1], q[0], q[3], rms, skew], axis=1).astype(np.float32)

def load_dataset(ds):
    """returns X3 (n,T,3) scaled-per-train-later? no: raw 3-channel; y int; metric_labels; chan_corr."""
    if ds == "ecg":
        d = np.load(ECG_CACHE); X_raw, y = d["X"], d["y"].astype(int)
        X3 = np.stack([three_channels(x) for x in X_raw], axis=0)
        labels = [0, 1, 2]                                # macro-F1 over N/A/O (exclude noise)
    elif ds == "uwave":
        from aeon.datasets import load_classification
        X, ys = load_classification("UWaveGestureLibrary")   # (n,3,L) str labels
        X3 = np.transpose(X, (0, 2, 1)).astype(np.float32)   # (n,L,3)
        uniq = sorted(set(ys)); y = np.array([uniq.index(v) for v in ys])
        labels = list(range(len(uniq)))
    else:
        raise ValueError(ds)
    return X3, y, labels

# ---------- 3-qubit statevector -> 3x3 correlation matrix C ----------
I2 = np.eye(2); P0 = np.diag([1., 0]); P1 = np.diag([0, 1.]); Z = np.diag([1., -1.])
def ry(t): c, s = np.cos(t/2), np.sin(t/2); return np.array([[c, -s], [s, c]])
def place(mats): return np.kron(np.kron(mats[0], mats[1]), mats[2])
def cry(alpha, c, t):
    m0 = [I2, I2, I2]; m0[c] = P0
    m1 = [I2, I2, I2]; m1[c] = P1; m1[t] = ry(alpha)
    return place(m0) + place(m1)

def circuit_C(alphas):
    """alphas: dict for pairs (0,1),(0,2),(1,2) or None -> separable. Returns 3x3 corr matrix."""
    psi = np.zeros(8); psi[0] = 1.0
    for q in range(3):                                    # equal superposition, <Z>=0
        mats = [I2, I2, I2]; mats[q] = ry(np.pi/2); psi = place(mats) @ psi
    if alphas is not None:
        for (c, t), a in alphas.items():
            psi = cry(a, c, t) @ psi
    def expZ(qs):                                         # <product of Z over qs>
        mats = [I2, I2, I2]
        for q in qs: mats[q] = Z
        return float(psi.conj() @ (place(mats) @ psi)).real
    zi = [expZ([i]) for i in range(3)]
    M = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            zz = 1.0 if i == j else expZ([i, j])
            M[i, j] = zz - zi[i]*zi[j]
    d = np.sqrt(np.clip(np.diag(M), 1e-9, None))
    C = M / np.outer(d, d); np.fill_diagonal(C, 1.0)
    return C

def sigma_from_C(C):                                      # 24x24 = I_8 (kron) C
    return np.kron(np.eye(8), C)

# ---------- model ----------
class MLP(nn.Module):
    def __init__(s, d, H, k): super().__init__(); s.fc1 = nn.Linear(d, H); s.fc2 = nn.Linear(H, k)
    def forward(s, x): return s.fc2(torch.relu(s.fc1(x)))

def cov_sample(H, d, Sigma, he_std, rng):
    L = np.linalg.cholesky(Sigma + 1e-6*np.eye(d))
    return ((rng.standard_normal((H, d)) @ L.T) * he_std).astype(np.float32)

def init_fc1(model, cond, seed, d, Sigma_blind, Sigma_aware):
    he_std = float(np.sqrt(2.0 / d))
    with torch.no_grad():
        if cond == "he": nn.init.kaiming_normal_(model.fc1.weight, nonlinearity="relu")
        elif cond == "xavier": nn.init.xavier_normal_(model.fc1.weight)
        elif cond == "orthogonal":                        # QR unimplemented on MPS -> init on CPU
            w = torch.empty_like(model.fc1.weight, device="cpu"); nn.init.orthogonal_(w)
            model.fc1.weight.copy_(w.to(model.fc1.weight.device))
        else:
            rng = np.random.RandomState(seed)
            Sig = {"sep": np.eye(d), "blind": Sigma_blind, "aware": Sigma_aware}[cond]
            model.fc1.weight.copy_(torch.tensor(cov_sample(model.fc1.weight.shape[0], d, Sig, he_std, rng)))
        model.fc1.bias.zero_()
    return model

def macro_f1(yt, yp, labels): return f1_score(yt, yp, labels=labels, average="macro", zero_division=0)

def train_eval(Xtr, ytr, Xva, yva, Xte, yte, cond, seed, cls_w, labels, Sb, Sa, nk):
    torch.manual_seed(seed); np.random.seed(seed)
    model = MLP(Xtr.shape[1], H, nk).to(DEVICE)
    model = init_fc1(model, cond, seed, Xtr.shape[1], Sb, Sa)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    lossf = nn.CrossEntropyLoss(weight=cls_w.to(DEVICE))
    Xtr_t = torch.tensor(Xtr, device=DEVICE); ytr_t = torch.tensor(ytr, device=DEVICE)
    Xva_t = torch.tensor(Xva, device=DEVICE); Xte_t = torch.tensor(Xte, device=DEVICE)
    n = len(Xtr_t); vc, best, btest, bep = [], -1.0, -1.0, -1
    for ep in range(EPOCHS):
        model.train(); perm = torch.randperm(n, device=DEVICE)
        for i in range(0, n, BATCH):
            idx = perm[i:i+BATCH]; opt.zero_grad()
            lossf(model(Xtr_t[idx]), ytr_t[idx]).backward(); opt.step()
        model.eval()
        with torch.no_grad(): vp = model(Xva_t).argmax(1).cpu().numpy()
        vf = macro_f1(yva, vp, labels); vc.append(float(vf))
        if vf > best:
            best, bep = float(vf), ep
            with torch.no_grad(): tp = model(Xte_t).argmax(1).cpu().numpy()
            btest = float(macro_f1(yte, tp, labels))
    return {"val_curve": vc, "best_val": best, "best_ep": bep, "test_f1": btest}

# ---------- run ----------
print(f"[{'SMOKE' if SMOKE else 'FULL'}] ds={DS} dev={DEVICE}", flush=True)
X3, y, labels = load_dataset(DS)
itr, iva, ite = stratified_split(y, seed=0)
if SMOKE: itr = itr[:300]; iva = iva[:120]; ite = ite[:120]
sc = RobustChannelScaler().fit(X3[itr]); X3s = sc.transform(X3)

# data channel correlation (train) -> data-aware angles
rho = np.nanmean([np.corrcoef(X3s[i].T) for i in itr[:800]], axis=0)
pairs = [(0, 1), (0, 2), (1, 2)]
C_blind = circuit_C({p: np.pi/4 for p in pairs})
C_aware = circuit_C({p: (np.pi/2)*abs(rho[p[0], p[1]]) for p in pairs})
Sb, Sa = sigma_from_C(C_blind), sigma_from_C(C_aware)

Xf = feats(X3s); fsc = StandardScaler().fit(Xf[itr]); Xf = fsc.transform(Xf).astype(np.float32)
Xtr, ytr = Xf[itr], y[itr]; Xva, yva = Xf[iva], y[iva]; Xte, yte = Xf[ite], y[ite]
nk = int(y.max())+1
counts = np.bincount(ytr, minlength=nk)
cls_w = torch.tensor(len(ytr)/(nk*np.maximum(counts, 1)), dtype=torch.float32)
print(f"train {Xtr.shape} val {Xva.shape} test {Xte.shape} | classes {nk} | counts {counts}")
print(f"data 3x3 channel corr (off-diag): {rho[0,1]:.3f} {rho[0,2]:.3f} {rho[1,2]:.3f}")
np.set_printoptions(precision=3, suppress=True)
print("C_aware off-diag:", C_aware[0,1], C_aware[0,2], C_aware[1,2],
      "| C_blind off-diag:", C_blind[0,1], C_blind[0,2], C_blind[1,2])

res = json.load(open(RES)) if RES.exists() else {"runs": {}, "meta": {}}
res["meta"] = {"ds": DS, "H": H, "epochs": EPOCHS, "seeds": N_SEEDS, "labels": labels,
               "chan_corr_offdiag": [float(rho[0,1]), float(rho[0,2]), float(rho[1,2])],
               "C_aware": C_aware.tolist(), "C_blind": C_blind.tolist(), "smoke": SMOKE}
for cond in CONDS:
    for s in range(N_SEEDS):
        key = f"{cond}_s{s}"
        if key in res["runs"]: continue
        t = time.time()
        r = train_eval(Xtr, ytr, Xva, yva, Xte, yte, cond, s, cls_w, labels, Sb, Sa, nk)
        r["sec"] = time.time()-t; res["runs"][key] = r
        json.dump(res, open(RES, "w"), indent=2)
        print(f"{key:16s} val={r['best_val']:.4f}@{r['best_ep']:3d} test={r['test_f1']:.4f} ({r['sec']:.1f}s)", flush=True)

print(f"\n=== {DS} summary (test macro-F1, 5 seeds) ===")
for cond in CONDS:
    tf = [res["runs"][f"{cond}_s{s}"]["test_f1"] for s in range(N_SEEDS)]
    print(f"  {cond:11s} {np.mean(tf):.4f} +/- {np.std(tf):.4f}")
print(f"DONE -> {RES.name}")
