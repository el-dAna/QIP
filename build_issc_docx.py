"""Build the ISSC full-paper .docx from the ECG paper, matching the template:
A4, 2.5cm margins, single column, Times New Roman 11pt justified, 1.1 spacing,
6pt after; Tahoma bold title; APA 7th references; real Word tables; embedded PNGs."""
from docx import Document
from docx.shared import Pt, Cm, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FIG = "paper_aeon/figures"
doc = Document()

# ---- page + base style ----
sec = doc.sections[0]
sec.page_width, sec.page_height = Mm(210), Mm(297)
sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Cm(2.5)
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"; normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = normal.paragraph_format
pf.line_spacing = 1.1; pf.space_after = Pt(6); pf.space_before = Pt(0)
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def _set_font(run, name="Times New Roman", size=11, bold=False, italic=False):
    run.font.name = name; run.font.size = Pt(size); run.bold = bold; run.italic = italic
    run.element.rPr.rFonts.set(qn("w:eastAsia"), name)

def para(text="", align="justify", size=11, bold=False, italic=False, name="Times New Roman",
         space_after=6, space_before=0):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                                     "left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
    p.paragraph_format.line_spacing = 1.1
    p.paragraph_format.space_after = Pt(space_after); p.paragraph_format.space_before = Pt(space_before)
    if text:
        r = p.add_run(text); _set_font(r, name, size, bold, italic)
    return p

def h1(text):  para(text, align="center", bold=True, space_before=6)      # main heading: TNR 11 bold centered
def h2(text):  para(text, align="left", bold=True, space_before=4)        # subheading: TNR 11 bold left

def no_vert_borders(table):
    tbl = table._tbl; borders = OxmlElement("w:tblBorders")
    for edge in ("top","left","bottom","right","insideH"):
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"),"single"); e.set(qn("w:sz"),"4"); e.set(qn("w:color"),"000000")
        borders.append(e)
    iv = OxmlElement("w:insideV"); iv.set(qn("w:val"),"none"); borders.append(iv)
    table._tbl.tblPr.append(borders)

def add_table(caption, header, rows):
    para(caption, align="center", size=11)                                # caption above
    t = doc.add_table(rows=1, cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for j,htext in enumerate(header):
        c = t.rows[0].cells[j]; c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.paragraphs[0].add_run(htext); _set_font(r, size=11, bold=True)
    for row in rows:
        cells = t.add_row().cells
        for j,val in enumerate(row):
            cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = cells[j].paragraphs[0].add_run(val); _set_font(r, size=11)
    no_vert_borders(t)
    para("", space_after=2)

def add_figure(png, caption, width_cm=11):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(f"{FIG}/{png}", width=Cm(width_cm))
    para(caption, align="center", size=11)

# ================= TITLE / AUTHORS =================
para("Quantum-Enhanced Machine Learning for Biomedical Diagnostics: "
     "An Image-to-ECG Transfer Study on PhysioNet 2017",
     align="center", name="Tahoma", size=12, bold=True, space_before=0, space_after=10)
para("Sogodam Atadana1, Özlem Karabiber Cura2*", align="center", size=10, italic=True, space_after=0)
para("1,2 İzmir Kâtip Çelebi University, Department of Biomedical Engineering, İzmir, Türkiye",
     align="center", size=10, italic=True, space_after=0)
para("*Corresponding author: ozlem.karabiber@ikcu.edu.tr", align="center", size=10, italic=True, space_after=10)

# ================= ABSTRACT =================
h1("Abstract")
para("A 3-qubit channel-entangled Quantum Probability Image Encoding (QPIE) pipeline that captures "
     "label-relevant colour structure on RGB medical images has been reported in companion work. We test "
     "whether that image-domain encoding transfers to a clinical time-series task: single-lead "
     "electrocardiogram (ECG) arrhythmia classification on the PhysioNet/CinC 2017 AF Challenge. The three "
     "colour channels are replaced by three signals manufactured from the ECG itself — bandpassed "
     "amplitude, first difference, and the Hilbert envelope of a db4 wavelet-detail band. Six encoding "
     "schemes (Sep, CRyE, GBE, CSE, PA-CSE, CP-2L) map each ~0.83 s window to a 3-qubit state, and Z+X+Y "
     "multi-basis measurement yields 24 features per window. We evaluate three classification heads over "
     "five seeds — an aggregated MLP, a per-window 1D CNN, and QMBC-Net, a cross-attention head built "
     "around the (Z, X, Y) measurement structure — against the published challenge baselines and a "
     "same-representation ROCKET baseline on the raw three channels. The strongest configuration, a 1D CNN "
     "on the per-window features, reaches macro-F1 0.670 on the official N/A/O metric, 16 points below the "
     "0.83 challenge state of the art and 5 points below ROCKET on the identical three channels. Three "
     "results hold across every head: the separable encoder matches or beats all entangling schemes, the "
     "global Bell entangler is the weakest by 5–7 points, and QMBC-Net trails the plain 1D CNN by ten "
     "points. The quantum feature map that helps on RGB MedMNIST does not transfer to single-lead ECG; the "
     "advantage on images appears specific to spatial channel correlations that physiological time series "
     "lack. We report the negative result, a reusable recipe for porting the encoder to a 1D biosignal, "
     "and the regime it delineates.")
p = doc.add_paragraph(); p.paragraph_format.line_spacing=1.1; p.paragraph_format.space_after=Pt(10)
r=p.add_run("Keywords: "); _set_font(r, bold=True)
r=p.add_run("Quantum machine learning, electrocardiogram, atrial fibrillation, multi-basis measurement, "
            "PhysioNet 2017, biomedical signal classification, negative result."); _set_font(r)

# ================= INTRODUCTION =================
h1("Introduction")
para("Atrial fibrillation (AF) is the most common sustained cardiac arrhythmia and a major cause of "
     "stroke. Single-lead wearable ECG has made low-cost screening realistic, and the PhysioNet/CinC 2017 "
     "AF Challenge (Clifford et al., 2017) released 8528 short single-lead recordings as a public "
     "benchmark. Top entries reach macro-F1 around 0.83 over the three clinical classes (Normal, AF, "
     "Other) (Clifford et al., 2017; Andreotti et al., 2017; Goodfellow et al., 2018).")
para("Quantum feature extractors are a less explored route, and the evidence on whether they help is thin "
     "and domain-specific. In companion work (Atadana & Karabiber Cura, 2026) we extended QPIE to RGB "
     "images by assigning one qubit per colour channel and varying the entangling structure across six "
     "schemes; a data-conditional scheme captured label-relevant pixel correlations on PathMNIST. That "
     "result is the motivation, not the claim, of this paper. The question here is narrow and falsifiable: "
     "does an encoding designed for the spatial channel correlations of RGB images carry over to a 1D "
     "physiological signal once the three colour channels are replaced by three engineered signal "
     "channels, and does a head built around the structure of multi-basis quantum measurements improve on "
     "the standard classical heads?")
para("The answer, on PhysioNet 2017, is no on both counts, and the way it fails is informative. We port "
     "the six 3-qubit encoders from (Atadana & Karabiber Cura, 2026) unchanged, manufacture three signal "
     "channels from each recording, and run three classification heads — an MLP on aggregated features, a "
     "1D CNN on per-window features, and QMBC-Net, a cross-basis-to-temporal attention head designed for "
     "multi-basis features. We benchmark against the published challenge baselines and against ROCKET "
     "(Dempster et al., 2020) on the raw three channels, the same-representation control that isolates "
     "what the quantum step adds.")
para("The contributions are three. (1) A 1D adaptation of the channel-entangled QPIE encoder: a reusable "
     "recipe for porting the 3-channel RGB encoder to any 1D biosignal — bandpassed amplitude, first "
     "difference, and a band-limited envelope as the three channels. (2) A controlled transfer test on a "
     "clinical benchmark: six encoders × three heads × five seeds on PhysioNet 2017, scored on the "
     "official N/A/O macro-F1, against published baselines and a same-representation ROCKET control. (3) A "
     "negative, mechanistic result: the encoding is lossy (16 points below the challenge state of the art, "
     "5 below same-representation ROCKET), entanglement provides no benefit (the separable scheme is best, "
     "the global Bell entangler worst), and QMBC-Net underperforms a plain 1D CNN; a time-delay "
     "re-alignment of the encoder input, motivated by the diagnosis, changes which scheme wins but does "
     "not recover accuracy, which isolates the fixed encoding — not the entanglement structure — as the "
     "bottleneck.")

# ================= RELATED WORK =================
h1("Related Work")
h2("ECG arrhythmia classification on PhysioNet 2017")
para("The 2017 AF Challenge released 8528 single-lead ECG recordings sampled at 300 Hz, 9 to 60 seconds "
     "long, labelled Normal (N), AF (A), Other (O), or Noise (~). The official metric is macro-F1 over "
     "N/A/O. Class balance is roughly 60/9/28/3 percent, so AF and the heterogeneous Other class dominate "
     "the macro average. The challenge winner used hand-crafted heart-rate-variability and morphology "
     "features fed to a gradient-boosted tree, reaching macro-F1 0.83 (Clifford et al., 2017). Andreotti "
     "et al. (2017) compared feature-engineered and convolutional entries and reported 0.79–0.83; "
     "Goodfellow et al. (2018) trained a multi-scale CNN. Hannun et al. (2019) reached F1 0.83 over 12 "
     "rhythm classes on a different and larger single-lead dataset, reported here only for context.")
h2("Quantum image and signal encodings")
para("Quantum image representations include FRQI (Le et al., 2011), NEQR (Zhang et al., 2013), MCQI (Sun "
     "et al., 2011), and QPIE (Yao et al., 2017); none target temporal signals directly. Adaptations to "
     "time series have used amplitude encoding of the signal or angle encoding of windowed features "
     "(Kyriienko et al., 2022). In (Atadana & Karabiber Cura, 2026) the six 3-qubit encoders below were "
     "validated on MedMNIST, where multi-basis measurement and statistical aggregation produced a "
     "492-dimensional feature vector competitive with a small CNN. This paper reuses those encoders and "
     "the measurement pipeline without modification, which is what makes the transfer question clean.")
h2("Attention over quantum measurements")
para("Standard heads treat quantum-feature outputs as plain vectors and discard the (Z, X, Y) basis "
     "structure. QMBC-Net attends across measurement bases as named tokens before attending across time; "
     "the closest prior design is multi-modal cross-attention (Vaswani et al., 2017). We include it as a "
     "candidate head to test, not as an established method.")

# ================= METHOD =================
h1("Method")
h2("From single-lead ECG to three signal channels")
para("A recording x[n] is bandpass-filtered to 0.5–40 Hz and centre-cropped or zero-padded to 30 s "
     "(N = 9000 at 300 Hz). For each recording we form three channels: c1[n] = bandpassed amplitude; "
     "c2[n] = first difference x_bp[n] − x_bp[n−1]; and c3[n] = the Hilbert envelope of the level-2 "
     "detail of a five-level db4 decomposition (nominal 37.5–75 Hz octave, limited by the 0.5–40 Hz "
     "passband). Each channel is robust-scaled per-recording with the q5/q95 mapping from "
     "(Atadana & Karabiber Cura, 2026) into [0,1]. Figure 1 shows the three channels on a sample "
     "recording.")
add_figure("fig_three_channels.png",
           "Figure 1. The three signal channels built from one ECG recording: bandpassed amplitude, first "
           "difference, and the db4 wavelet-detail envelope. These replace the three colour channels "
           "of the RGB encoder.")
h2("Per-window 3-qubit encoding")
para("The signal is split into windows of 250 samples (~0.83 s, near one cardiac cycle) with stride 125, "
     "giving W = 71 windows. We reuse all six encoders from (Atadana & Karabiber Cura, 2026): Sep "
     "(separable, per-channel angle encoding only), CRyE and GBE (controlled-Ry and global Bell "
     "entanglers), CSE and PA-CSE (data-conditional schemes whose entangling angles depend on pairwise "
     "channel correlations), and CP-2L (a two-layer encode–entangle circuit). Each takes a 3-channel "
     "sample in [0,1]^3 and returns a 3-qubit amplitude vector; shared angle encoding θc = π·c̄c; the "
     "schemes differ only in the entangling gates. We project each per-sample state onto Z, X, and Y "
     "(24 features) and aggregate over the window. The per-window mean gives a (W × 24) sequence; full "
     "per-sample aggregation gives a 492-dimensional recording vector (9×24 statistics + C(24,2) "
     "correlations).")
h2("Three classification heads")
para("Phase-1A: aggregated MLP. The 492-dimensional recording vector through the MedMNIST MLP head "
     "(512→256→128→4 with BatchNorm, ReLU, Dropout 0.3). Phase-1B: 1D CNN over windows. The (W × 24) "
     "per-window sequence through a three-block 1D CNN with dilations {1,2,4}, adaptive average pooling, "
     "and a linear classifier; the CNN sees temporal order. Phase-2: QMBC-Net. Per window, the 24 "
     "features split into three basis tokens of 8 (Z, X, Y), embed to dimension 64, and pass through one "
     "cross-basis multi-head attention layer; a learned per-basis gate pools the three tokens to a window "
     "vector. Sinusoidal positional encoding over windows precedes two layers of temporal self-attention; "
     "a CLS token feeds a linear classifier.")

# ================= EXPERIMENTAL SETUP =================
h1("Experimental Setup")
para("PhysioNet/CinC 2017 AF Challenge (Clifford et al., 2017), 8528 recordings, 4 classes, loaded via "
     "wfdb with the rescored REFERENCE-v3 labels. Stratified 60/20/20 split across N/A/O/~. All heads use "
     "AdamW (lr 1e-3, weight decay 1e-4), cosine annealing, square-root class-weighted cross-entropy, "
     "batch 256, up to 100 epochs, early stopping on validation macro-F1 with patience 20; five seeds; "
     "Apple M4, MPS backend. The primary metric is macro-F1 over N/A/O (Noise excluded), the official "
     "challenge metric; secondary metrics are macro AUC (one-vs-rest) and balanced accuracy. We compare "
     "against the published baselines (Table 4) and against multivariate ROCKET (Dempster et al., 2020) on "
     "the raw three channels with the identical split and metric — the same-representation control that "
     "separates the encoding's contribution from the representation's.")

# ================= RESULTS =================
h1("Results")
para("The headline is in Table 4: the best quantum configuration reaches macro-F1 0.670, well below both "
     "the published baselines and same-representation ROCKET. Within that ceiling, three patterns recur "
     "across the three heads.")
h2("Across heads: the separable scheme is not beaten")
para("Tables 1–3 report all six schemes through each head over five seeds; Figure 2 plots the two Phase-1 "
     "heads. No entangling scheme beats the separable baseline (Sep) on any head. On the strongest head "
     "(1D CNN) Sep (0.669) and the data-conditional PA-CSE (0.670) are tied best, while the global Bell "
     "entangler GBE is worst at 0.598 — a 7-point entanglement penalty. In QMBC-Net the ordering is the "
     "same, with GBE the weakest scheme (9 points below Sep); in the aggregated MLP the six schemes fall "
     "within roughly one point of each other, so that head is too coarse to separate them. Entanglement, "
     "fixed or data-conditional, adds nothing here.")
hdr = ["Scheme", "macro-F1", "AUC", "BAcc"]
add_table("Table 1. Phase-1A — aggregated MLP, PhysioNet 2017, 5 seeds.", hdr, [
    ["Sep","0.533 ± 0.012","0.801 ± 0.003","0.594 ± 0.015"],
    ["CRyE","0.521 ± 0.004","0.786 ± 0.002","0.565 ± 0.008"],
    ["GBE","0.522 ± 0.006","0.799 ± 0.001","0.591 ± 0.004"],
    ["CSE","0.522 ± 0.007","0.786 ± 0.003","0.568 ± 0.008"],
    ["PA-CSE","0.526 ± 0.006","0.792 ± 0.005","0.580 ± 0.009"],
    ["CP-2L","0.526 ± 0.006","0.799 ± 0.002","0.593 ± 0.005"]])
add_table("Table 2. Phase-1B — 1D CNN over windows, PhysioNet 2017, 5 seeds (best head).", hdr, [
    ["Sep","0.669 ± 0.005","0.891 ± 0.001","0.688 ± 0.009"],
    ["CRyE","0.642 ± 0.012","0.878 ± 0.005","0.662 ± 0.008"],
    ["GBE","0.598 ± 0.006","0.855 ± 0.003","0.614 ± 0.018"],
    ["CSE","0.621 ± 0.009","0.872 ± 0.002","0.651 ± 0.007"],
    ["PA-CSE","0.670 ± 0.004","0.887 ± 0.001","0.682 ± 0.007"],
    ["CP-2L","0.659 ± 0.013","0.886 ± 0.003","0.665 ± 0.013"]])
h2("Aggregation discards temporal order")
para("The MLP on aggregated features tops out at 0.533 (Sep), 14 points below the same encoder through "
     "the 1D CNN (0.669). Pooling per-sample statistics over the recording removes the temporal structure "
     "that distinguishes rhythms, and the CNN recovers it, locating the useful signal in window order "
     "rather than in the per-window statistics.")
h2("QMBC-Net does not beat a plain CNN")
para("QMBC-Net was included to test whether a head built around the measurement bases helps. It does not "
     "(Table 3). Its best scheme reaches 0.562 (Sep), ten points below the 1D CNN. The basis-token "
     "attention adds parameters and structure without accuracy, and the per-basis gates do not concentrate "
     "on any single projection axis. The architectural claim is not supported.")
add_table("Table 3. Phase-2 — QMBC-Net, PhysioNet 2017, 5 seeds.", hdr, [
    ["Sep","0.562 ± 0.005","0.829 ± 0.001","0.584 ± 0.007"],
    ["CRyE","0.511 ± 0.011","0.800 ± 0.002","0.536 ± 0.001"],
    ["GBE","0.473 ± 0.009","0.767 ± 0.004","0.516 ± 0.016"],
    ["CSE","0.532 ± 0.011","0.815 ± 0.007","0.561 ± 0.023"],
    ["PA-CSE","0.547 ± 0.009","0.822 ± 0.005","0.569 ± 0.008"],
    ["CP-2L","0.534 ± 0.012","0.817 ± 0.003","0.567 ± 0.017"]])
add_figure("fig_phase1_results.png",
           "Figure 2. Macro-F1 (N/A/O) per scheme for the aggregated MLP (Phase-1A) and the 1D CNN "
           "(Phase-1B), 5 seeds. The CNN lifts every scheme by recovering temporal order; the separable "
           "Sep is best or tied, and the global Bell entangler GBE is consistently weakest.")
h2("Same-representation baseline and the published state of the art")
para("Multivariate ROCKET on the raw three channels reaches macro-F1 0.719 ± 0.007 (5 seeds), above the "
     "best quantum configuration by 5 points on the identical representation and split. Per-class F1 for "
     "ROCKET is 0.85 (N), 0.70 (AF), 0.61 (Other); the heterogeneous Other class is the hardest for every "
     "method. A fast random-convolution baseline on the same channels is therefore stronger than the "
     "quantum encoding, and all of these sit below the 0.83 challenge state of the art, which used richer "
     "hand-crafted morphology and rhythm features. The encoding does not reach competitive accuracy and "
     "loses to a strong classical baseline on equal footing; the contribution of this work is the transfer "
     "behaviour and the boundary it marks, not accuracy.")
add_table("Table 4. PhysioNet 2017 macro-F1 (N/A/O) — published baselines, a same-representation control, "
          "and ours.",
          ["System","Backbone","macro-F1"], [
    ["Clifford 2017","GBT + features","0.83"],
    ["Andreotti 2017","CNN","0.79–0.83"],
    ["Goodfellow 2018","multi-scale CNN","0.83"],
    ["Hannun 2019 †","34-layer 1D ResNet","0.83"],
    ["ROCKET (raw 3-ch, this work) §","random conv.","0.719"],
    ["Ours, Phase-1A (Sep)","MLP-agg","0.533"],
    ["Ours, Phase-2 (Sep)","QMBC-Net","0.562"],
    ["Ours, Phase-1B (PA-CSE)","1D CNN","0.670"]])
para("† Different dataset (12 rhythm classes); context only. § Multivariate ROCKET (Dempster et al., 2020) "
     "on the raw three channels, identical split and metric (this work).", size=10)

# ================= DISCUSSION =================
h1("Discussion")
h2("Why the transfer fails")
para("On RGB MedMNIST the data-conditional schemes helped because adjacent colour channels carry "
     "label-relevant correlations that the entangling angles can encode (Atadana & Karabiber Cura, 2026). "
     "Single-lead ECG has no analogue. The three channels here are deterministic transforms of one signal "
     "(amplitude, derivative, envelope), so their cross-channel correlations are fixed by construction and "
     "carry little class information. The encoder's representational budget — which on images is spent on "
     "inter-channel structure — has little to act on, and the entangling schemes collapse toward the "
     "separable baseline or below it. The global Bell entangler, which forces correlation regardless of "
     "the data, is consistently the worst head: imposed entanglement disrupts rather than helps. This is "
     "the image result read in reverse, and it bounds where the encoding is useful: domains with genuine, "
     "label-relevant channel correlation, not arbitrary multichannel signals.")
h2("The encoding is lossy")
para("The same-representation ROCKET baseline is the sharper statement. Given the identical three "
     "channels, a random-convolution model extracts 5 more points of macro-F1 than the best quantum "
     "pipeline. The quantum feature map discards label-relevant structure that a cheap classical transform "
     "keeps. Aggregation compounds the loss — the MLP path drops a further 14 points by pooling away "
     "temporal order — which is why the 1D CNN, the head that preserves window order, is the only one to "
     "approach ROCKET.")
h2("Re-aligning the input geometry does not rescue it")
para("If the entanglement conditions on the wrong correlation axis, the natural correction is to feed the "
     "three qubits a time-delay (Takens) embedding x[t], x[t−τ], x[t−2τ] of the signal rather than the "
     "three derived channels; the data-conditional schemes then condition on lag-τ autocorrelation, which "
     "on ECG tracks rhythm regularity — the structure that separates AF from sinus rhythm. We tested this "
     "on a 3000-recording stratified subset at two lag scales. Morphology-scale lags (τ ≈ 0.1 s) left the "
     "ordering unchanged: the separable scheme stayed best. At rhythm scale (τ ≈ 0.5 s, multi-beat "
     "windows) the data-conditional PA-CSE became the only entangling scheme in any of our experiments to "
     "exceed the separable baseline (0.47 vs. 0.43 macro-F1, three seeds), consistent with the mechanism "
     "above. The re-alignment did not improve absolute accuracy, however: every delay configuration "
     "trailed the simpler channel pipeline. Re-pointing the encoding's conditioning axis changes which "
     "scheme wins but not the ceiling. The limitation therefore sits in the fixed encoding itself, not in "
     "the entanglement structure or the input geometry, and a trainable, data-driven encoding rather than "
     "a fixed circuit is the route a future study should take.")
h2("What the negative result is good for")
para("The 1D channel recipe is reusable and the protocol is a template for testing any image-domain "
     "quantum encoder on a biosignal before assuming transfer. The ablation also behaves as a diagnostic: "
     "the separable-versus-entangled gap measures whether a dataset's channel correlations are "
     "label-relevant, and on ECG it reads near zero, consistent with the signal's structure. The honest "
     "reading is that the image-domain advantage is modality-specific, and that single-lead ECG "
     "diagnostics are better served by classical convolutional or feature-engineered baselines. "
     "Clinically, this is a useful caution: a screening tool built on this encoding would underperform a "
     "fast classical baseline on the same signal, so the contribution is to map where quantum encoding can "
     "and cannot help as such tools are developed, rather than to deploy it now.")
h2("Limitations")
para("Single-lead only; PhysioNet 2017 is four-class with strong imbalance, and the macro average is "
     "dominated by AF and Other. The three qubits are classically simulable and we make no "
     "quantum-advantage claim. Windows are fixed at 250 samples and the split is recording-level, not "
     "patient-stratified. The same-representation control uses ROCKET; a deeper classical baseline on the "
     "raw channels would tighten the ceiling but not change the direction of the result.")

# ================= CONCLUSION =================
h1("Conclusion")
para("We tested whether a quantum image-encoding pipeline transfers to single-lead ECG arrhythmia "
     "classification. It does not. The best configuration, a 1D CNN on the multi-basis features, reaches "
     "macro-F1 0.670 on PhysioNet 2017 — 16 points below the challenge state of the art and 5 below "
     "ROCKET on the identical three channels — no entangling scheme beats the separable baseline, and a "
     "measurement-structured attention head underperforms a plain CNN. The advantage the encoder shows on "
     "RGB images depends on label-relevant channel correlations that single-lead ECG lacks. Re-aligning "
     "the encoder input to temporal-delay coordinates changes which scheme wins but not the accuracy "
     "ceiling, which points to a trainable encoding, rather than a fixed circuit, as the next step. We "
     "contribute a reusable 1D-adaptation recipe, a controlled transfer protocol, and a clear delineation "
     "of the regime in which this class of quantum encoding helps.")

# ================= ACK =================
h1("Acknowledgment")
para("The authors used a large language model to assist with editing and proofreading of the manuscript "
     "text. All experiments, results, analysis, and scientific claims are the authors' own and were "
     "verified against the source code and data.")

# ================= REFERENCES (APA 7th, alphabetical) =================
h1("References")
refs = [
 "Andreotti, F., Carr, O., Pimentel, M. A. F., Mahdi, A., & De Vos, M. (2017). Comparing feature-based "
 "classifiers and convolutional neural networks to detect arrhythmia from short segments of ECG. "
 "Computing in Cardiology, 44, 1–4.",
 "Atadana, S., & Karabiber Cura, Ö. (2026). When does entanglement help in quantum image encoding? A "
 "per-image mechanism test on MedMNIST. Proceedings of the IEEE International Conference on Quantum "
 "Computing and Engineering (QCE). (in press)",
 "Clifford, G. D., Liu, C., Moody, B., Lehman, L.-W. H., Silva, I., Li, Q., Johnson, A. E., & Mark, R. G. "
 "(2017). AF classification from a short single lead ECG recording: The PhysioNet/Computing in Cardiology "
 "Challenge 2017. Computing in Cardiology, 44, 1–4.",
 "Dempster, A., Petitjean, F., & Webb, G. I. (2020). ROCKET: Exceptionally fast and accurate time series "
 "classification using random convolutional kernels. Data Mining and Knowledge Discovery, 34(5), "
 "1454–1495.",
 "Goodfellow, S. D., Goodwin, A., Greer, R., Laussen, P. C., Mazwi, M., & Eytan, D. (2018). Towards "
 "understanding ECG rhythm classification using convolutional neural networks and attention mappings. "
 "Proceedings of Machine Learning for Healthcare.",
 "Hannun, A. Y., Rajpurkar, P., Haghpanahi, M., Tison, G. H., Bourn, C., Turakhia, M. P., & Ng, A. Y. "
 "(2019). Cardiologist-level arrhythmia detection and classification in ambulatory electrocardiograms "
 "using a deep neural network. Nature Medicine, 25(1), 65–69.",
 "Kyriienko, O., Paine, A. E., & Elfving, V. E. (2022). Protocols for trainable and differentiable "
 "quantum generative modelling. Physical Review Research, 4, 043067.",
 "Le, P. Q., Dong, F., & Hirota, K. (2011). A flexible representation of quantum images for polynomial "
 "preparation, image compression, and processing operations. Quantum Information Processing, 10(1), "
 "63–84.",
 "Sun, B., Iliyasu, A. M., Yan, F., Dong, F., & Hirota, K. (2011). Multi-channel representation for images "
 "on quantum computers using the RGBα color space. Proceedings of the IEEE 7th International Symposium on "
 "Intelligent Signal Processing, 1–6.",
 "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, "
 "I. (2017). Attention is all you need. Advances in Neural Information Processing Systems, 30.",
 "Yao, X.-W., Wang, H., Liao, Z., Chen, M.-C., et al. (2017). Quantum image processing and its "
 "application to edge detection: Theory and experiment. Physical Review X, 7, 031041.",
 "Zhang, Y., Lu, K., Gao, Y., & Wang, M. (2013). NEQR: A novel enhanced quantum representation of digital "
 "images. Quantum Information Processing, 12(8), 2833–2860.",
]
for r in refs:
    p = para(r, align="justify", size=11, space_after=6)
    p.paragraph_format.left_indent = Cm(0.75); p.paragraph_format.first_line_indent = Cm(-0.75)  # hanging

OUT = "paper_aeon/ISSC_Atadana_ECG_QPIE.docx"
doc.save(OUT)
print("saved", OUT)
