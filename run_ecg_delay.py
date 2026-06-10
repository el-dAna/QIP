"""SPACE-SHUTTLE TEST: does re-aligning the QPIE input from signal-derived CHANNELS
to a time-delay (Takens) embedding make the data-conditional entanglement useful on ECG?

First-principles claim: QPIE's image advantage = CSE conditions entanglement on
inter-CHANNEL correlation (label-relevant colour structure). Ported to ECG with
channels=[amplitude,derivative,envelope], those correlations are ~deterministic/
constant -> no class info -> entanglement-null. The time-series analogue of
"cross-channel correlation" is "cross-TIME correlation" (autocorrelation = rhythm
regularity), which DOES separate AF from Normal. So feed the 3 qubits x[t],x[t-tau],
x[t-2tau]; CSE then conditions on lag-autocorrelation. Circuits/measurement unchanged.

Clean test on one subset/split: {Sep, CSE} x {derived-channels (as-is), delay-embed}.
Reuses Phase8 encoders/CNN verbatim via AST-extraction; only the channel builder changes.
Env: msc_venv. SMOKE=1 -> tiny. Results -> _ecg_delay_results.json.
"""
import os, ast, json, time, numpy as np

SMOKE = os.environ.get("SMOKE") == "1"
NB = "Phase8_PhysioNet2017_ECG.ipynb"
TAU = int(os.environ.get("TAU", "32"))
N_SUB = 300 if SMOKE else 3000
SEEDS = 1 if SMOKE else 3
SCHEMES = ["Sep", "CSE", "PA-CSE"]  # Sep = no-entangle baseline; CSE/PA-CSE = data-conditional

# ---- AST-extract defs/constants from the notebook, skip heavy executors ----
nb = json.load(open(NB)); cells = nb["cells"]; G = {"__name__": "__main__"}
EXP = {"load_all","build_dataset","make_three_channel_dataset","encode_dataset",
       "run_phase1a","run_phase1b","run_phase2","train_one","summarise","to_latex_table",
       "paired_t_vs_sep","fig_phase1_results","fig_three_channels","fig_attention",
       "fig_sota_compare","get_attention","savez_compressed","savefig","show",
       "read_csv","mkdir","rdrecord"}
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
for i in [2,4,6,8,10,12,14,16]:
    src="".join(cells[i]["source"])
    for node in ast.parse(src).body:
        if not keep(node): continue
        seg=ast.get_source_segment(src,node)
        if not seg: continue
        hard=isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))
        try: exec(compile(seg,f"<c{i}>","exec"),G)
        except Exception:
            if hard: raise

if os.environ.get("WIN"):    G["WIN"]    = int(os.environ["WIN"])
if os.environ.get("STRIDE"): G["STRIDE"] = int(os.environ["STRIDE"])
three_channels        = G["three_channels"]            # as-is (derived channels)
RobustChannelScaler   = G["RobustChannelScaler"]
windowize             = G["windowize"]
stratified_split      = G["stratified_split"]
run_phase1b           = G["run_phase1b"]
DATA_DIR              = G["DATA_DIR"]
from sklearn.model_selection import StratifiedShuffleSplit

def three_channels_delay(x, tau=TAU):
    """x:(N,) -> (N,3) time-delay coords [x[t], x[t-tau], x[t-2tau]] (causal)."""
    c1 = x.astype(np.float32)
    c2 = np.empty_like(c1); c2[:tau] = c1[0]; c2[tau:] = c1[:-tau]
    c3 = np.empty_like(c1); c3[:2*tau] = c1[0]; c3[2*tau:] = c1[:-2*tau]
    return np.stack([c1, c2, c3], axis=-1)

def build(Xr, builder):
    X3 = np.stack([builder(x) for x in Xr], axis=0)
    return X3

print(f"[{'SMOKE' if SMOKE else 'FULL'}] tau={TAU} N_sub={N_SUB} seeds={SEEDS}", flush=True)
d = np.load(DATA_DIR / "cached.npz"); X_raw, y = d["X"], d["y"]
sub, _ = next(StratifiedShuffleSplit(1, train_size=N_SUB, random_state=0).split(np.zeros_like(y), y))
Xr, ys = X_raw[sub], y[sub]
itr, iva, ite = stratified_split(ys, seed=0)
print(f"subset {len(ys)}  test-class-counts {np.bincount(ys[ite], minlength=4)}", flush=True)

RES = f"_ecg_delay_t{TAU}_w{G['WIN']}.json"
results = json.load(open(RES)) if os.path.exists(RES) else {}
results.setdefault("config", {"tau": TAU, "N_sub": N_SUB, "seeds": SEEDS, "smoke": SMOKE})

def run_mode(mode, builder):
    t = time.time()
    X3 = build(Xr, builder)
    sc = RobustChannelScaler().fit(X3[itr]); X3 = sc.transform(X3)
    data = {"X_win": windowize(X3), "y": ys, "idx_tr": itr, "idx_va": iva, "idx_te": ite}
    res = run_phase1b(data, schemes=SCHEMES, seeds=SEEDS)        # {scheme:[{macro_f1,...}]}
    out = {s: {"macro_f1_mean": float(np.mean([r["macro_f1"] for r in res[s]])),
               "macro_f1_std":  float(np.std([r["macro_f1"] for r in res[s]])),
               "per_seed":      [round(r["macro_f1"], 4) for r in res[s]]}
           for s in SCHEMES}
    results[mode] = out; json.dump(results, open(RES, "w"), indent=2)
    print(f"\n[{mode}] ({(time.time()-t)/60:.1f}min)", flush=True)
    for s in SCHEMES:
        print(f"   {s:<5} macro-F1 = {out[s]['macro_f1_mean']:.4f} ± {out[s]['macro_f1_std']:.4f}", flush=True)
    return out

print("\n=== MODE A: derived channels (as-is, the failing transfer) ===", flush=True)
a = run_mode("derived_channels", three_channels)
print("\n=== MODE B: time-delay embedding (the fix) ===", flush=True)
b = run_mode("delay_embedding", three_channels_delay)

print("\n" + "="*60)
print("VERDICT (does delay-embedding make entanglement useful?)")
print(f"  CSE: derived {a['CSE']['macro_f1_mean']:.4f} -> delay {b['CSE']['macro_f1_mean']:.4f}  "
      f"(Δ {b['CSE']['macro_f1_mean']-a['CSE']['macro_f1_mean']:+.4f})")
print(f"  CSE vs Sep under delay: {b['CSE']['macro_f1_mean']-b['Sep']['macro_f1_mean']:+.4f} "
      f"(positive => entanglement now helps)")
print("="*60)
