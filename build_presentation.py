"""Generate a single-file, offline-proof HTML presentation deck for BME519 (figures base64-embedded)."""
import base64, pathlib

FIG = pathlib.Path("paper_aeon/figures")
def b64(name):
    return "data:image/png;base64," + base64.b64encode((FIG/name).read_bytes()).decode()

img_channels = b64("fig_three_channels.png")
img_results  = b64("fig_phase1_results.png")
img_sota     = b64("fig_sota_compare.png")

SLIDES = [
# 1 title
f"""<section class="slide title">
  <div class="kicker">BME 519 · Computer-Aided Diagnosis Methods for Biomedical Applications</div>
  <h1>Quantum-Enhanced ML for<br><span class="accent">ECG Arrhythmia Diagnosis</span></h1>
  <h2>An image-to-ECG transfer study on PhysioNet&nbsp;2017</h2>
  <div class="byline">Sogodam Atadana &nbsp;·&nbsp; Supervisor: Dr.&nbsp;Özlem&nbsp;Karabiber&nbsp;Cura</div>
  <div class="byline small">İzmir Kâtip Çelebi University · Department of Biomedical Engineering</div>
  <div class="tag">Project Option B — Signal-Based Anomaly Detection</div>
</section>""",

# 2 problem
"""<section class="slide">
  <h3>The clinical problem</h3>
  <ul class="big">
    <li><b>Atrial fibrillation (AF)</b> — the most common sustained cardiac arrhythmia, a major cause of stroke.</li>
    <li><b>Single-lead wearable ECG</b> makes low-cost screening realistic — but needs automated interpretation.</li>
    <li><b>The CAD task:</b> classify a short single-lead ECG as Normal / AF / Other / Noise.</li>
  </ul>
  <div class="callout">Goal of a CAD system here: flag rhythm abnormality early, cheaply, at scale.</div>
</section>""",

# 3 the question
"""<section class="slide">
  <h3>The question this project asks</h3>
  <p class="lead">A quantum image encoder (QPIE) was shown — in companion work — to capture label-relevant
  colour structure in RGB medical images.</p>
  <div class="qbox">Does that image-domain quantum encoding <span class="accent">transfer</span> to a 1D
  physiological signal — single-lead ECG — and does a quantum-measurement-aware classifier beat standard ones?</div>
  <p class="muted">A narrow, falsifiable question. We answer it honestly — including where it fails.</p>
</section>""",

# 4 dataset
"""<section class="slide">
  <h3>Dataset — PhysioNet/CinC 2017 AF Challenge</h3>
  <div class="two">
    <ul class="big">
      <li><b>8528</b> single-lead ECG recordings, 300&nbsp;Hz, 9–60&nbsp;s</li>
      <li>Labels: Normal · AF · Other · Noise</li>
      <li>Official metric: <b>macro-F1 over N/A/O</b></li>
      <li>Public benchmark; rescored REFERENCE-v3 labels</li>
    </ul>
    <div class="statbox">
      <div class="stat"><span>60%</span>Normal</div>
      <div class="stat"><span>9%</span>AF</div>
      <div class="stat"><span>28%</span>Other</div>
      <div class="stat"><span>3%</span>Noise</div>
      <div class="note">Strong imbalance → AF &amp; Other dominate the macro average.</div>
    </div>
  </div>
</section>""",

# 5 method 1 channels
f"""<section class="slide">
  <h3>Method · 1 — From one ECG to three channels</h3>
  <p class="lead">The RGB encoder needs three channels. We manufacture them from the ECG itself:</p>
  <div class="two">
    <ul class="big">
      <li><b>c1</b> — bandpassed amplitude (0.5–40&nbsp;Hz)</li>
      <li><b>c2</b> — first difference</li>
      <li><b>c3</b> — Hilbert envelope of the 9–18&nbsp;Hz wavelet detail</li>
    </ul>
    <img src="{img_channels}" alt="three channels"/>
  </div>
  <div class="callout small">A reusable recipe for porting a 3-channel image encoder to any 1D biosignal.</div>
</section>""",

# 6 method 2 encoding
"""<section class="slide">
  <h3>Method · 2 — Quantum encoding per window</h3>
  <ul class="big">
    <li>Window the signal (250 samples ≈ 0.83&nbsp;s, one cardiac cycle).</li>
    <li>Map each sample's 3 channels onto a <b>3-qubit state</b> via angle encoding.</li>
    <li><b>Six schemes</b> vary the entanglement: Sep (none), CRyE, GBE, CSE, PA-CSE, CP-2L.</li>
    <li><b>Multi-basis Z+X+Y measurement</b> → 24 features per window.</li>
  </ul>
  <div class="callout">The encoders are reused <i>unchanged</i> from the image work — that is what makes the
  transfer test clean.</div>
</section>""",

# 7 method 3 heads
"""<section class="slide">
  <h3>Method · 3 — Three classification heads</h3>
  <div class="cards">
    <div class="card"><h4>Aggregated MLP</h4><p>492-d statistical summary → MLP. Pools away time.</p></div>
    <div class="card"><h4>1D CNN</h4><p>(W×24) per-window sequence → dilated 1D CNN. Keeps temporal order.</p></div>
    <div class="card"><h4>QMBC-Net</h4><p>Cross-<b>basis</b> attention over (Z,X,Y) → temporal attention. Quantum-aware.</p></div>
  </div>
  <div class="callout small">Evaluated over 5 seeds, against published baselines and a same-representation
  classical control (ROCKET on the raw 3 channels).</div>
</section>""",

# 8 results entanglement null
f"""<section class="slide">
  <h3>Result · 1 — Entanglement does not help</h3>
  <div class="two">
    <img src="{img_results}" alt="per-scheme results"/>
    <ul class="big">
      <li>The <b>separable</b> scheme (Sep) is best or tied in <b>every</b> head.</li>
      <li>The global Bell entangler (GBE) is <b>consistently worst</b> (−5 to −7 pts).</li>
      <li>Data-conditional schemes (CSE/PA-CSE) add nothing.</li>
    </ul>
  </div>
  <div class="callout">Entanglement — fixed or data-conditional — provides no benefit on ECG.</div>
</section>""",

# 9 results SOTA / lossy
f"""<section class="slide">
  <h3>Result · 2 — The encoding is lossy</h3>
  <div class="two">
    <table class="res">
      <tr><th>Method</th><th>macro-F1</th></tr>
      <tr><td>Challenge SOTA (features+GBT)</td><td>0.83</td></tr>
      <tr class="hl"><td>ROCKET on raw 3-ch (same-rep)</td><td>0.719</td></tr>
      <tr><td>QPIE → 1D CNN (best)</td><td>0.670</td></tr>
      <tr><td>QPIE → QMBC-Net (best)</td><td>0.562</td></tr>
      <tr><td>QPIE → MLP (best)</td><td>0.533</td></tr>
    </table>
    <ul class="big">
      <li>A fast classical model on the <b>same channels</b> beats every quantum config by ~5 pts.</li>
      <li>QMBC-Net — the quantum-aware head — <b>trails the plain CNN</b> by 10 pts.</li>
      <li>16 pts below the challenge state of the art.</li>
    </ul>
  </div>
</section>""",

# 10 diagnosis + fix
"""<section class="slide">
  <h3>Why it fails — and a tested fix</h3>
  <p class="lead"><b>Diagnosis:</b> the data-conditional schemes condition entanglement on inter-<i>channel</i>
  correlation. On ECG those channels are deterministic transforms → that correlation is class-empty.</p>
  <p class="lead"><b>Fix tested:</b> re-align the qubits to a <i>time-delay</i> embedding so entanglement
  conditions on <b>autocorrelation</b> (rhythm regularity) instead.</p>
  <div class="qbox small">Result: at rhythm-scale, a data-conditional scheme finally beats Sep — but absolute
  accuracy does <b>not</b> improve. The bottleneck is the <span class="accent">fixed encoding</span>, not the
  entanglement axis.</div>
</section>""",

# 11 key findings
"""<section class="slide">
  <h3>Key findings</h3>
  <ul class="big check">
    <li>The image-domain quantum encoding <b>does not transfer</b> to single-lead ECG.</li>
    <li>No entangling scheme beats the separable baseline; the encoding is <b>lossy</b> vs ROCKET.</li>
    <li>A quantum-measurement-structured head <b>does not beat</b> a plain 1D CNN.</li>
    <li>Re-aligning the input geometry changes which scheme wins, <b>not the ceiling</b>.</li>
  </ul>
  <div class="callout">An honest, mechanistic negative result — with the bottleneck localized.</div>
</section>""",

# 12 discussion
"""<section class="slide">
  <h3>Discussion — limits, impact, future work</h3>
  <div class="two">
    <div>
      <h4>Limitations</h4>
      <ul><li>Single-lead, 4-class, imbalanced</li><li>Classically simulable (no advantage claim)</li>
      <li>Recording-level (not patient) split</li></ul>
    </div>
    <div>
      <h4>Clinical impact &amp; future work</h4>
      <ul><li>Use classical CNN / feature baselines for ECG screening today</li>
      <li>Map where quantum encoding can/can't help</li>
      <li><b>Trainable</b> (variational) encoding, not fixed circuits</li></ul>
    </div>
  </div>
</section>""",

# 13 conclusion
"""<section class="slide title end">
  <div class="kicker">Conclusion</div>
  <h1>Honest transfer study,<br><span class="accent">complete arc</span></h1>
  <p class="lead center">Negative result · mechanistic diagnosis · tested fix · same-rep baseline · forward path.</p>
  <div class="byline">Report (IEEE) + code: <span class="accent">github.com/el-dAna/QIP</span></div>
  <div class="tag">Thank you — questions?</div>
</section>""",
]

CSS = """
:root{--bg:#0b1020;--panel:#121a31;--ink:#eaf0ff;--muted:#9fb0d0;--accent:#36e3c2;--accent2:#5b8bff;--line:#243154;}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,Segoe UI,Inter,Roboto,Helvetica,Arial,sans-serif;overflow:hidden}
.deck{height:100vh;width:100vw;position:relative}
.slide{position:absolute;inset:0;display:none;flex-direction:column;justify-content:center;
  padding:6vh 8vw;animation:fade .45s ease}
.slide.active{display:flex}
@keyframes fade{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
h1{font-size:4.2vw;line-height:1.08;letter-spacing:-.5px;margin:.2em 0}
h2{font-size:1.7vw;font-weight:500;color:var(--muted);margin:.2em 0 .8em}
h3{font-size:2.5vw;color:#fff;margin-bottom:.6em;border-left:5px solid var(--accent);padding-left:.5em}
h4{font-size:1.4vw;color:var(--accent);margin:.3em 0}
.kicker{color:var(--accent);font-weight:700;letter-spacing:2px;text-transform:uppercase;font-size:1.05vw;margin-bottom:1em}
.accent{color:var(--accent)}
.byline{color:var(--muted);font-size:1.25vw;margin-top:1.2em}.byline.small{font-size:1vw;margin-top:.3em}
.tag{margin-top:1.6em;display:inline-block;background:var(--panel);border:1px solid var(--line);
  color:var(--accent);padding:.5em 1.1em;border-radius:999px;font-size:1vw;width:max-content}
ul.big{font-size:1.6vw;line-height:1.9;list-style:none}
ul.big li{padding-left:1.4em;position:relative;margin:.15em 0}
ul.big li:before{content:"▸";color:var(--accent);position:absolute;left:0}
ul.big.check li:before{content:"✓";color:var(--accent)}
ul li{font-size:1.25vw;line-height:1.7;margin-left:1.2em}
.lead{font-size:1.6vw;line-height:1.6;margin:.4em 0;color:#dfe7ff}
.lead.center{text-align:center}
.muted{color:var(--muted)}
.small{font-size:.95em}
.callout{margin-top:1.2em;background:linear-gradient(90deg,rgba(54,227,194,.14),rgba(91,139,255,.10));
  border:1px solid var(--line);border-left:5px solid var(--accent);padding:.9em 1.2em;border-radius:10px;font-size:1.3vw}
.qbox{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1.1em 1.3em;
  font-size:1.9vw;line-height:1.45;margin:.6em 0}
.qbox.small{font-size:1.5vw}
.two{display:grid;grid-template-columns:1fr 1fr;gap:3vw;align-items:center}
.two img,.slide img{max-width:100%;max-height:52vh;border-radius:12px;background:#fff;padding:10px;border:1px solid var(--line)}
.statbox{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1.4em;display:grid;
  grid-template-columns:1fr 1fr;gap:.8em}
.stat{font-size:1.1vw;color:var(--muted);display:flex;flex-direction:column}
.stat span{font-size:2.6vw;color:var(--accent);font-weight:800}
.statbox .note{grid-column:1/3;color:var(--muted);font-size:1vw;border-top:1px solid var(--line);padding-top:.6em}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5vw;margin:.5em 0}
.card{background:var(--panel);border:1px solid var(--line);border-top:4px solid var(--accent);
  border-radius:12px;padding:1.2em}.card p{font-size:1.1vw;color:var(--muted);line-height:1.5;margin-top:.4em}
table.res{width:100%;border-collapse:collapse;font-size:1.35vw}
table.res th,table.res td{text-align:left;padding:.55em .7em;border-bottom:1px solid var(--line)}
table.res th{color:var(--accent)}
table.res tr.hl td{background:rgba(54,227,194,.12);font-weight:700;color:#fff}
.end h1{font-size:3.6vw}
.progress{position:fixed;bottom:0;left:0;height:5px;background:var(--accent);transition:width .3s;z-index:10}
.counter{position:fixed;bottom:14px;right:20px;color:var(--muted);font-size:14px;z-index:10}
.brand{position:fixed;bottom:12px;left:22px;color:var(--muted);font-size:13px;letter-spacing:1px;z-index:10}
"""

JS = """
const slides=[...document.querySelectorAll('.slide')];let i=0;
const prog=document.querySelector('.progress'),cnt=document.querySelector('.counter');
function show(n){i=Math.max(0,Math.min(slides.length-1,n));
  slides.forEach((s,k)=>s.classList.toggle('active',k===i));
  prog.style.width=((i+1)/slides.length*100)+'%';cnt.textContent=(i+1)+' / '+slides.length;}
document.addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown',' ','PageDown'].includes(e.key)){show(i+1);e.preventDefault();}
  else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){show(i-1);e.preventDefault();}
  else if(e.key==='Home')show(0); else if(e.key==='End')show(slides.length-1);
  else if(e.key.toLowerCase()==='f'){document.documentElement.requestFullscreen?.();}});
document.addEventListener('click',e=>{if(e.clientX>window.innerWidth*0.35)show(i+1);else show(i-1);});
show(0);
"""

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BME519 — Quantum ML for ECG Arrhythmia Diagnosis</title>
<style>{CSS}</style></head><body>
<div class="deck">{''.join(SLIDES)}</div>
<div class="progress"></div><div class="counter"></div>
<div class="brand">IKCU · Biomedical Engineering</div>
<script>{JS}</script></body></html>"""

out = "bme519_presentation.html"
open(out, "w").write(html)
print(f"saved {out}  ({len(html)//1024} KB, {len(SLIDES)} slides)")
