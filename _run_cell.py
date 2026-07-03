"""Headless harness: exec a Thesis_Mechanism_Spine.ipynb code cell by index.
No experiment logic lives here — the notebook cell is the single source of truth.
Usage: python _run_cell.py <cell_index>   (run with msc_venv, from the QIP dir)
"""
import json, sys
idx = int(sys.argv[1])
nb = json.load(open("Thesis_Mechanism_Spine.ipynb"))
src = "".join(nb["cells"][idx]["source"])
print(f"--- exec Thesis_Mechanism_Spine.ipynb cell {idx} ({len(src.splitlines())} lines) ---", flush=True)
exec(compile(src, f"<cell{idx}>", "exec"), {"__name__": "__main__"})
