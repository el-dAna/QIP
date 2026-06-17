"""Arm 2 grouped comparison figure (reads _arm2_cond_{uwave,ecg}.json)."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT = Path("/Users/eldana/Documents/Quantum/Thesis/QIP")
CONDS = ["he", "xavier", "orthogonal", "sep", "blind", "aware"]
COL = {"he": "#888", "xavier": "#888", "orthogonal": "#888", "sep": "#bbb",
       "blind": "#e08214", "aware": "#2166ac"}
DSETS = [("uwave", "UWave  (channel coupling 0.44)"), ("ecg", "ECG  (channel coupling ~0.12)")]

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for c, (ds, title) in enumerate(DSETS):
    r = json.load(open(PROJECT / f"_arm2_cond_{ds}.json"))["runs"]
    g = lambda cd: np.array([r[f"{cd}_s{s}"]["test_f1"] for s in range(5)])
    means = [g(cd).mean() for cd in CONDS]; stds = [g(cd).std() for cd in CONDS]
    # --- top: grouped bars, test macro-F1 ---
    ax = axes[0, c]
    bars = ax.bar(CONDS, means, yerr=stds, capsize=4,
                  color=[COL[cd] for cd in CONDS], edgecolor="k", linewidth=0.6)
    ax.axhline(g("he").mean(), ls="--", c="#444", lw=1, label="He mean")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_ylabel("test macro-F1 (5 seeds)")
    he, aware, blind = g("he"), g("aware"), g("blind")
    from scipy import stats
    p_ab = stats.ttest_1samp(aware - blind, 0).pvalue
    p_ah = stats.ttest_1samp(aware - he, 0).pvalue
    ax.text(0.5, 0.02, f"aware vs blind: Δ={(aware-blind).mean():+.3f} (p={p_ab:.2f})   "
                       f"aware vs he: Δ={(aware-he).mean():+.3f} (p={p_ah:.2f})",
            transform=ax.transAxes, ha="center", fontsize=8.5,
            bbox=dict(boxstyle="round", fc="#fff3cd", ec="#c69500"))
    ax.tick_params(axis="x", rotation=30)
    # --- bottom: validation learning curves (mean +/- std), key 3 conditions ---
    ax = axes[1, c]
    for cd in ["he", "blind", "aware"]:
        curves = np.array([r[f"{cd}_s{s}"]["val_curve"] for s in range(5)])
        m, sd = curves.mean(0), curves.std(0); x = np.arange(len(m))
        ax.plot(x, m, color=COL[cd], lw=1.8, label=cd)
        ax.fill_between(x, m - sd, m + sd, color=COL[cd], alpha=0.15)
    ax.set_xlabel("epoch"); ax.set_ylabel("val macro-F1"); ax.legend(fontsize=9, loc="lower right")
    ax.set_title("learning curves (he / blind / aware)", fontsize=10)

fig.suptitle("Arm 2 — data-aware entangled weight init vs baselines  (NULL: aware ≈ baselines)",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.97])
for ext in ["png", "pdf"]:
    fig.savefig(PROJECT / f"_arm2_comparison.{ext}", dpi=150, bbox_inches="tight")
print("saved _arm2_comparison.png / .pdf")
