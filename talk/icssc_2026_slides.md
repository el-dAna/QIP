---
marp: true
theme: default
paginate: true
size: 16:9
footer: 'Eldana Atadana — ICSSC 2026'
style: |
  section {
    font-family: 'Helvetica Neue', sans-serif;
    font-size: 28px;
    padding: 50px 80px;
  }
  h1 { font-size: 44px; color: #1a1a1a; }
  h2 { font-size: 36px; color: #2c3e50; }
  .hook { font-size: 64px; text-align: center; margin-top: 30%; }
  .number { font-size: 56px; color: #c0392b; font-weight: bold; }
  .small { font-size: 20px; color: #666; }
  .center { text-align: center; }
  table { font-size: 22px; }
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _footer: '' -->

<div class="hook">

# *what is this?*

</div>

<!--
SLIDE 1 — HOOK (1:30)

Open with a single PathMNIST tile filling the entire slide.
Replace the placeholder text above with: ![bg](../paper/figures/pathmnist_tile.png)
or import a 28x28 PathMNIST TUM-class tile, upsampled to 800x800 nearest-neighbour.

NO TITLE. NO NAME. Just the image.

SPEAK (~140 words):
(point at the image, 2s pause)
"What is this?"
(let the room guess. 4s pause.)
"It is colorectal cancer epithelium. Twenty-eight pixels by twenty-eight pixels.
A standard convolutional network — a ResNet-18 — classifies images like this with 
91% accuracy on a nine-class pathology benchmark. It uses about 11 million trainable 
parameters to do so.
Today I want to show you something different. We encoded the same kind of image 
as a quantum state, with no trainable quantum parameters at all, and then handed it 
to a small classical network.
On a sibling dataset — blood cells — that approach reached 95.6% accuracy, within 
0.2 points of the ResNet, with roughly one twenty-seventh of the parameters.
So the question is: what is quantum encoding actually doing here? And does it always 
help? Those are the two questions I'll answer."
-->

---

# Quantum-Enhanced Feature Extraction for Biomedical Imaging

**Eldana Atadana**
10th International Students Science Congress · 14 May 2026

<br/>

<div class="small">

QPIE — Quantum Probability Image Encoding · MSc thesis work, IEEE QCE 2026 (submitted)

</div>

<!--
TITLE appears here, AFTER the hook lands. Brief - 5 seconds tops.
"Quantum-enhanced feature extraction for biomedical imaging."
-->

---

# Three things classical bits cannot do

<div style="display: flex; justify-content: space-around; margin-top: 60px;">

<div class="center">

### ⊙
**Superposition**

one qubit holds a continuum

</div>

<div class="center">

### ≋
**Interference**

amplitudes add and cancel

</div>

<div class="center">

### ⊗
**Entanglement**

joint state, not separable

</div>

</div>

<!--
SLIDE 3 — Three quantum primitives (2:00)

Replace symbols with proper icons in Keynote:
- left: a continuous dial sliding 0→1
- centre: two sine waves with one constructive crest and one destructive cancellation
- right: two filled qubits joined by a thick line, encircled

SPEAK (~190 words):
"Classical computers process bits — zero or one, on or off. Everything they do reduces 
to deterministic flips.
Quantum systems can do three things classical bits cannot.
One. A qubit can be in a superposition of states. It is not just zero or one — it holds 
a continuum, weighted by probability amplitude.
Two. Those amplitudes interfere. They add up like waves on water — sometimes constructive, 
sometimes destructive. Calculations that would take a classical computer trillions of 
steps can be solved by arranging interference correctly.
Three. Two qubits can be entangled. Their joint state is not the product of two 
independent states. The information lives between them — neither one carries it alone.
(pause)
Now, I am not going to claim quantum computers will replace classical ones tomorrow. 
They will not. But for certain problems — and image encoding is one of them — these 
three properties give us tools that classical preprocessing simply cannot reach. Let 
me show you why."

DO NOT use "drop a pebble / characterise the wave / escape the local minimum" framing.
That describes variational QML (QAOA, VQE), not this work.
-->

---

# Correlation: cost to flatten, or feature to store?

<div style="display: flex; justify-content: space-around; align-items: center; margin-top: 40px;">

<div style="width: 45%;">

### Classical: **decorrelate**

PCA rotates correlated features
onto independent axes.

Redundant dimensions cost data.

</div>

<div style="width: 45%;">

### Quantum: **entangle**

The joint distribution becomes
a single amplitude.

Correlation is encoded directly.

</div>

</div>

<!--
SLIDE 4 — Why entanglement, not PCA (2:00)

Visual to build: two cartoon scatter plots side-by-side.
- LEFT: correlated 2D scatter (tilted ellipse), arrow showing PCA rotation
  onto PC1/PC2 axes where points become independent.
- RIGHT: same correlated scatter, but wrapped in a |ψ⟩ ket symbol.

SPEAK (~180 words):
"Here is where classical machine learning meets a wall.
When two features in your data are correlated — say, the red and green channels of 
a tissue image, which are nearly always correlated — classical preprocessing decorrelates 
them. Principal component analysis rotates the data onto axes where the features are 
independent. We do this because in classical computation, redundant dimensions cost 
data, and data is expensive.
Quantum encoding goes the opposite direction. Entanglement keeps the correlation. 
It stores the joint relationship between two features as a single quantum amplitude — 
one number that knows about both channels at once.
(pause, point at right panel)
Correlation is not a cost any more. It is a feature you encode directly.
This is the core intuition behind my work. Instead of flattening correlation away, 
we ask: can we use it?
The next slide tests that question."

AVOID: "discard" (PCA rotates, not discards), "leverage" (buzzword).
-->

---

# The entanglement knob

```
  ◯─────●─────●─────●─────●─────●
 Sep   CRyE  GBE  PA-CSE CP-2L  CSE
  no                       continuous-α
 entanglement              correlation-sensitive
                                                            
           ↓        ↓        ↓        ↓        ↓        ↓
          ┌──────────────────────────────────────┐
          │      SAME CLASSICAL MLP              │
          └──────────────────────────────────────┘
                       ↓
                  prediction
```

**Six encoders · zero → high entanglement · same downstream model · X/Y/Z measurement**

<!--
SLIDE 5 — Entanglement knob (3:00)

Visual to build in Keynote:
- horizontal gradient bar (light grey → dark blue) labelled ENTANGLEMENT, arrow pointing right
- six tick marks: Sep | CRyE | GBE | PA-CSE | CP-2L | CSE
- below: grey box "SAME CLASSICAL MLP" with arrows from each tick to it
- top-right small inset: three coloured axes for X/Y/Z measurement bases

SPEAK (~280 words):
"To test whether entanglement actually helps, I designed six different ways to encode 
an image as a quantum state.
Think of this as a tuning knob.
(point left) On the left end: separable encoding — each pixel becomes a qubit, no 
entanglement between them. Our quantum-but-unentangled control.
(point right) On the right end: data-dependent entangling schemes — encoders where 
the entanglement structure between qubits depends on the actual pixel values of the 
image. The strongest of these is CSE, continuous-alpha correlation-sensitive encoding. 
It uses controlled rotations whose angles depend on per-image colour correlations.
(point at gradient) Between those two ends sit four intermediate schemes — increasing 
entanglement in different structural ways.
(pause, point at grey box) The crucial point: the downstream classical model is the 
same for all six. Same multilayer perceptron, same training procedure, same number 
of features. The only thing that changes is the quantum encoder.
That isolation is what makes this a fair test. If we see a performance difference 
between schemes, we know it comes from the quantum part — from entanglement structure — 
and not from a better classifier or extra parameters.
Also — we measure each quantum state in three bases, X, Y, and Z. Different bases 
reveal different information about the same state, so we lose nothing.
(pause)
Now: what did we actually find?"
-->

---

# Two findings

<div style="display: flex; justify-content: space-around; margin-top: 30px;">

<div style="width: 47%;">

### BloodMNIST · 8 classes

| Model | Accuracy | Params |
|---|---|---|
| ResNet-18 (SOTA) | 95.8% | ~11M |
| **Our encoder (CP-2L)** | **95.6%** | **~400K** |
| Raw RGB baseline | 92.7% | — |

**Near-SOTA at ~1/27 the parameters.**
No trainable quantum parameters.

</div>

<div style="width: 47%;">

### PathMNIST · 9 classes

Per-image CSE gain over Sep,
stratified by colour correlation ρ

```
  +6%  ┤
  +4%  ┤        ▇▇▇   ▇▇▇
  +2%  ┤              
   0%  ┤  ▇▇▇                ▇▇▇
  −2%  ┤        ▇▇▇    
        Q1   Q2   Q3   Q4   Q5
              per-image ρ →
```

**β_ρ = +0.46** for CSE;  ≈ 0 for CRyE, CP-2L

</div>

</div>

<!--
SLIDE 6 — What we found (3:00)

VISUALS — replace these markdown stand-ins with actual figures from the paper:
- LEFT panel: paper/figures/fig_results_bar.pdf (BloodMNIST bars)
- RIGHT panel: paper/figures/fig_mechanism.pdf panel B (CSE quintile bar chart)

Numbers locked from paper/main.tex — audit before Thursday:
- 95.6% CP-2L BloodMNIST, ~400K params
- 95.8% ResNet-18 SOTA, ~11M params  
- 92.7% Raw RGB
- β_ρ = +0.46 (CSE)
- Quintile gap: +4 to +5% in Q3-Q4 of ρ

SPEAK (~290 words):
"Two findings — one positive, one nuanced.
(point at left panel) Finding one. On a blood-cell dataset — where colour channels 
carry strong diagnostic information — our quantum encoding reached 95.6% classification 
accuracy. The ResNet-18 baseline reaches 95.8% — a 0.2 percentage point difference, 
statistically insignificant.
The ResNet uses 11 million trainable parameters. Our system uses about 400,000.
That is the headline: near-classical accuracy, dramatically fewer parameters. Encoding 
alone — no quantum training — is doing the work.
(turn, point at right panel) Finding two — and this is where it gets interesting. 
On a harder dataset — colorectal pathology, the image I showed you at the start — 
the average difference between entangling and non-entangling encoders is small. Almost 
nothing.
So I asked a different question. Not: does entanglement help on average? But: does 
entanglement help per image?
(point at the bars) When I stratified by how correlated the colour channels were in 
each individual image — that is what the five bins on the right are — one encoder, 
CSE, started behaving differently. On the high-correlation tissues — bins three and 
four — CSE outperformed the non-entangling baseline by 4 to 5 percentage points.
The others — the gates without continuous correlation sensitivity — show no effect. 
Flat zero across all bins.
(pause, emphasise)
So entanglement is not a universal advantage. It is a conditional advantage, and we 
can now say which condition: when the data carries the kind of correlation structure 
the encoder is built to use.
This is, to my knowledge, the first per-image mechanism verification for a quantum 
encoder."
-->

---

# What's next

<div style="display: flex; justify-content: space-around; margin-top: 60px;">

<div class="center" style="width: 30%;">

### ⌁
**ECG · temporal signals**

does it transfer
beyond images?

</div>

<div class="center" style="width: 30%;">

### ⊞
**Symmetry-aware encoders**

design beyond
the pooling limit

</div>

<div class="center" style="width: 30%;">

### ▣
**Hardware-aware design**

real device constraints
in the encoder

</div>

</div>

<br/>
<br/>

<div class="center" style="font-size: 32px; margin-top: 40px;">

*Quantum doesn't always help. Knowing when it does — and why — is the work.*

</div>

<br/>
<div class="center small">

eldana · atadanas@gmail.com · QPIE · QCE26

</div>

<!--
SLIDE 7 — What's next (1:00)

Visual: three labelled lanes, equal width, with simple icons (replace the ASCII 
symbols ⌁ ⊞ ▣ with proper SVG icons in Keynote — ECG trace, circuit, chip).

The last line is the close. Do NOT add a "Thank you" slide. The last sentence is 
the thank you.

SPEAK (~120 words):
"Where this goes.
(point left) First — does this transfer beyond images? I am running a follow-on study 
on single-lead ECG, where the channels are not colour but morphology, slew, and 
envelope. Same encoder family, different physical signal.
(point centre) Second — the encoders that failed tell us something specific about 
the mathematical structure of the pooling operation. We can design future encoders 
to break that symmetry on purpose.
(point right) Third — none of this has run on actual quantum hardware yet. The next 
step is bringing real device constraints into the encoder design itself.
(pause, slow)
Quantum doesn't always help. Knowing when it does — and why — is the work.
Thank you."

Wait for applause to settle, then: "I'm happy to take questions."
-->

---

<!-- _backgroundColor: '#1a1a1a' -->
<!-- _color: white -->
<!-- _paginate: false -->

<div class="center" style="margin-top: 30%;">

## Questions?

<br/>

<div style="font-size: 20px; opacity: 0.7;">

backup slides follow — only shown if asked

</div>

</div>

<!--
Q&A buffer — 2:30 total.

ANTICIPATED QUESTIONS WITH ~30S ANSWERS:

Q1: "Did you run this on a real quantum computer?"
A: "Not yet. Everything I showed runs in classical simulation — six qubits is small 
enough to simulate exactly. The next step is testing on actual NISQ hardware. The 
challenge is that the encoders use continuous rotations, and current hardware has 
gate-fidelity limits that will degrade the per-image correlation signal. So part of 
the future work is asking: is this advantage robust to gate noise?"

Q2: "Is this faster than classical?"
A: "No. Quantum simulation is slower than direct classical computation today. The 
argument is not speed. It is representational efficiency — fewer parameters carrying 
more information. If you can do as well with 400,000 parameters as a classical model 
does with 11 million, that matters for low-power edge applications — implantable 
diagnostics, medical robotics, anything bandwidth-limited."

Q3: "Why didn't all six entangling encoders show the same effect?"
A: "Excellent question — that IS the architectural finding. Most of the encoders use 
fixed gates whose pooled output is symmetric under a relabelling of measurement outcomes. 
That symmetry makes them invisible to the downstream classifier — like a particle moving 
in a periodic potential, where certain energies are forbidden by symmetry. The CSE 
encoder breaks that symmetry because its rotation angles are continuous functions of 
the data."
(This is the Kronig-Penney intuition — deliver only if asked.)

Q4: "What is this for, practically?"
A: "Two near-term applications: medical-image classification at the edge — handheld 
devices, low-power diagnostic tools — and low-photon imaging, where the input is noisy 
and correlations between pixels carry the signal. Both regimes are bottlenecked by 
classical model size, and both have the kind of correlation structure our encoder is 
built to use."

Q5 (hostile): "Isn't quantum machine learning overhyped?"
A: "Yes, often. Most claims of quantum advantage in ML are about asymptotic complexity 
arguments that don't survive contact with real datasets. That's why I structured this 
work as a falsifiable test — six encoders along an entanglement axis, same classifier, 
per-image mechanism verification. I'd rather find a small, defensible result than claim 
a large one I can't reproduce. The headline isn't 'quantum wins'; it's 'here is the 
precise condition under which quantum encoding helps.'"

Q6: "How long did training take?"
A: "About 20 minutes per scheme on a laptop GPU. The expensive part is the quantum 
simulation — encoding 90,000 images through the multi-basis observation pipeline — 
which we cache once. After that, the classical MLP trains in under five minutes per 
seed."
-->

---

<!-- _class: lead -->

## Backup · How β_ρ is measured

For each test image *i*, fit a logistic regression:

$$
P(\text{scheme correct on } i) = \sigma\!\left( \alpha + \beta_\rho \cdot \rho_i + \gamma \cdot \mathbb{1}[\text{Sep correct on } i] \right)
$$

ρ_i = average pairwise channel correlation in image *i*.
γ controls for "Sep already got it right."
**β_ρ measures how much entanglement helps as a function of correlation.**

| Encoder | β_ρ | Interpretation |
|---|---|---|
| **CSE** | **+0.46** | high-correlation images favour entanglement |
| CRyE | −0.02 | indistinguishable from zero |
| CP-2L | −0.11 | indistinguishable from zero |

<!--
BACKUP slide — only display if a reviewer asks "how did you measure β_ρ?"

This is the per-image mechanism test from the QCE26 submission.

SPEAK (if asked):
"We ran a logistic regression per encoder. For each test image, we predict whether 
the encoder classified it correctly. The two inputs to the regression are: the image's 
per-channel correlation ρ, and whether the separable baseline got it right. The 
coefficient on ρ — β_ρ — measures how much entanglement helps as a function of 
correlation, while controlling for image hardness through the separable-correct 
indicator. CSE: +0.46. The others: indistinguishable from zero."
-->
