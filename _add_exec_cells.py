"""Append genuinely-executed cells for the ROCKET same-rep baseline and the delay
experiment to Phase8 (output captured by actually running the display code), and
drop the trailing empty cell. Keeps the existing (already-executed) pipeline outputs."""
import json, io, contextlib

NB = "Phase8_PhysioNet2017_ECG.ipynb"
nb = json.load(open(NB))
nb["cells"] = [c for c in nb["cells"]
               if not (c["cell_type"]=="code" and not "".join(c["source"]).strip())
               and not str(c.get("id","")).startswith("appx_")]      # idempotent

rocket_code = """\
# Same-representation control: ROCKET on the RAW 3-channel ECG (no quantum encoding).
# Isolates what the quantum step adds. Full runner: run_ecg_rawbaseline.py (5 seeds,
# 10k kernels, class-balanced ridge, identical split + N/A/O macro-F1). Cached below.
import json, numpy as np
d = json.load(open('_ecg_rawbaseline.json')); S = d['seeds']
f = [v['macro_f1_nao'] for v in S.values()]
print(f"ROCKET on raw 3-channel ECG  ({len(f)} seeds, {d['config']['n_kernels']} kernels)")
print(f"  macro-F1 (N/A/O) = {np.mean(f):.4f} +/- {np.std(f):.4f}")
pc = {k: round(float(np.mean([v['per_class_f1'][k] for v in S.values()])),3) for k in ['N','A','O','noise']}
print("  per-class F1   :", pc)
cm = np.mean([np.array(v['confusion']) for v in S.values()], axis=0).round(1)
print("  mean confusion (rows=true N/A/O/noise, cols=pred):")
print(cm)
print("  vs QPIE-CNN best (PA-CSE) 0.670 | challenge SOTA 0.83  ->  encoding is LOSSY")
"""

delay_code = """\
# Time-delay (Takens) re-alignment: feed the qubits x[t], x[t-tau], x[t-2tau] so the
# data-conditional schemes condition on lag-autocorrelation (rhythm) instead of the
# class-empty inter-channel correlation of the derived ECG channels. Diagnosis test.
# Runner: run_ecg_delay.py (3000-recording subset, 3 seeds, Phase-1B CNN).
import json
for fn, label in [('_ecg_delay_t32_w250.json',  'tau=32  (morphology scale, 0.11 s)'),
                  ('_ecg_delay_t150_w750.json', 'tau=150 (rhythm scale, 0.50 s)')]:
    d = json.load(open(fn)); cfg = d['config']
    print(f"=== {label}   subset N={cfg['N_sub']}, {cfg['seeds']} seeds ===")
    print("  %-18s %-9s %-9s %-9s" % ('mode', 'Sep', 'CSE', 'PA-CSE'))
    for mode in ['derived_channels', 'delay_embedding']:
        vals = "".join(f"{d[mode][s]['macro_f1_mean']:<9.3f}" for s in ['Sep','CSE','PA-CSE'])
        print("  %-18s %s" % (mode, vals))
print()
print("Verdict: re-alignment does NOT improve absolute accuracy. Only at rhythm scale does")
print("a data-conditional scheme (PA-CSE 0.472) exceed Sep (0.431) -> consistent with the")
print("mechanism, but the bottleneck is the FIXED ENCODING, not the entanglement axis.")
"""

def run_capture(code):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<cell>", "exec"), {"__name__": "__main__"})
    return buf.getvalue()

def md(idx, text):
    return {"cell_type": "markdown", "id": f"appx_{idx}", "metadata": {}, "source": text.splitlines(keepends=True)}

def code_cell(idx, src, out, n):
    return {"cell_type": "code", "id": f"appx_{idx}", "metadata": {}, "execution_count": n,
            "outputs": [{"output_type": "stream", "name": "stdout", "text": out.splitlines(keepends=True)}],
            "source": src.splitlines(keepends=True)}

# run for real (reads the committed JSONs), capture genuine output
rocket_out = run_capture(rocket_code)
delay_out  = run_capture(delay_code)
print("=== ROCKET cell output ===\n" + rocket_out)
print("=== delay cell output ===\n" + delay_out)

nb["cells"] += [
    md("rocket_md", "## Cell 12 — Same-representation baseline: ROCKET on the raw 3-channel ECG\n"
                    "\nStrong classical control on the identical channels and split, to quantify the "
                    "quantum encoding's information loss.\n"),
    code_cell("rocket", rocket_code, rocket_out, 12),
    md("delay_md", "## Cell 13 — Time-delay re-alignment experiment (diagnosis follow-up)\n"
                   "\nTests whether re-pointing the encoder input to temporal-delay coordinates makes the "
                   "data-conditional entanglement useful. It does not recover accuracy.\n"),
    code_cell("delay", delay_code, delay_out, 13),
]
json.dump(nb, open(NB, "w"), indent=1)
print(f"\nnotebook now {len(nb['cells'])} cells (added 4, dropped empty)")
