"""
Generate the two diagnostic figures for the multivariate-TSC QPIE paper.
Values are the paper's own reported results (Tables: regime, cse), which trace
to the Phase7_UWave.ipynb 10-seed runs. No retraining here -- this only plots
already-reported accuracies/deltas.

Output: figures/fig_regime.pdf, figures/fig_cse_beta.pdf  (vector, for Overleaf)
Run: /Users/eldana/Documents/Quantum/msc_venv/bin/python make_figures.py
"""
import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

os.makedirs('figures', exist_ok=True)
plt.rcParams.update({'font.size': 10, 'font.family': 'serif',
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.dpi': 150})

C_STAT = '#2c7fb8'   # temporal-statistics regime
C_ORD  = '#d95f0e'   # temporal-order regime

# ----- Table: regime (Sep scheme, native split) -----
# dataset, pooled, cnn_ens, regime
regime = [
    ('Epilepsy',              0.937, 0.964, 'stat'),
    ('CharacterTraj.',        0.960, 0.995, 'stat'),
    ('UWave (native)',        0.569, 0.828, 'ord'),
    ('Handwriting',           0.157, 0.539, 'ord'),
]

# =========================================================
# Figure 1 -- regime diagnostic (dumbbell: pooled -> CNN ens)
# =========================================================
fig, ax = plt.subplots(figsize=(5.0, 3.0))
order = sorted(regime, key=lambda r: (r[2] != 'stat', r[2]))  # stat first
ys = list(range(len(order)))[::-1]
for y, (name, pooled, cnn, reg) in zip(ys, order):
    col = C_STAT if reg == 'stat' else C_ORD
    ax.axhspan(y - 0.5, y + 0.5, color=col, alpha=0.06, zorder=0)  # per-row, matches markers
    ax.plot([pooled, cnn], [y, y], color=col, lw=2, zorder=1)
    ax.scatter([pooled], [y], color='white', edgecolor=col, s=55, zorder=2)
    ax.scatter([cnn], [y], color=col, s=55, zorder=2)
    gap = (cnn - pooled) * 100
    ax.annotate(f'+{gap:.1f}', ((pooled + cnn) / 2, y + 0.16),
                ha='center', va='bottom', fontsize=8.5, color=col)
ax.set_yticks(ys)
ax.set_yticklabels([r[0] for r in order])
ax.set_ylim(-0.6, len(order) - 0.4)
ax.set_xlabel('Accuracy (native split, Sep scheme)')
ax.set_xlim(0.05, 1.04)
legend = [Line2D([0], [0], marker='o', color='w', markerfacecolor='white',
                 markeredgecolor='gray', label='Pooled (L2-LR)', markersize=7),
          Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                 label='CNN ensemble', markersize=7),
          Line2D([0], [0], color=C_STAT, lw=2, label='temporal-statistics'),
          Line2D([0], [0], color=C_ORD, lw=2, label='temporal-order')]
ax.legend(handles=legend, fontsize=7.5, loc='lower left', frameon=True,
          framealpha=0.9, edgecolor='none')
fig.tight_layout()
fig.savefig('figures/fig_regime.pdf', bbox_inches='tight')
print('wrote figures/fig_regime.pdf')

# =========================================================
# Figure 2 -- CSE - Sep delta at CNN rung (beta_rho domain specificity)
# =========================================================
# Table: cse  (delta in ppts, all four time-series datasets)
cse = [
    ('Epilepsy',       -0.87),
    ('CharacterTraj.', -0.08),
    ('UWave (native)', -2.91),
    ('Handwriting',    -12.97),
]
fig, ax = plt.subplots(figsize=(5.0, 2.9))
cse_sorted = sorted(cse, key=lambda r: r[1])  # most negative at bottom
names = [r[0] for r in cse_sorted]
vals = [r[1] for r in cse_sorted]
ys = range(len(names))
ax.barh(list(ys), vals, color=C_ORD, alpha=0.85, height=0.6)
for y, v in zip(ys, vals):
    ax.annotate(f'{v:+.1f}', (v - 0.4, y), ha='right', va='center', fontsize=8.5)
ax.axvline(0, color='black', lw=0.8)
ax.set_yticks(list(ys))
ax.set_yticklabels(names)
ax.set_xlabel(r'CSE $-$ Sep accuracy at CNN rung (percentage points)')
ax.set_xlim(-15, 4)
# image-domain contrast (sign flip; qualitative -- no fabricated value)
ax.annotate('On PathMNIST (RGB images):\nCSE $>$ Sep (sign flips)',
            xy=(2.0, len(names) - 0.5), ha='center', va='center', fontsize=7.5,
            color=C_STAT, bbox=dict(boxstyle='round', fc='white', ec=C_STAT, lw=0.8))
fig.tight_layout()
fig.savefig('figures/fig_cse_beta.pdf', bbox_inches='tight')
print('wrote figures/fig_cse_beta.pdf')
