# Quantum-Enhanced Feature Extraction for Biomedical Imaging

**Speaker:** Eldana Atadana
**Venue:** 10th International Students Science Congress (sciencecon.org)
**Date:** Thursday 14 May 2026
**Length:** 15 minutes (12 min content + 2 min Q&A buffer + 1 min slack)

---

## Master timing budget

| Block | Slide | Duration | Cumulative |
|---|---|---|---|
| Hook (no title) | 1 | 1:30 | 1:30 |
| Quantum primitives | 2 | 2:00 | 3:30 |
| PCA vs entanglement | 3 | 2:00 | 5:30 |
| Entanglement knob | 4 | 3:00 | 8:30 |
| What we found | 5 | 3:00 | 11:30 |
| What's next | 6 | 1:00 | 12:30 |
| Q&A | — | 2:30 | 15:00 |

Total content: 12:30. Q&A buffer: 2:30.

---

## Slide 1 — Hook (1:30)

### On screen

- **No title, no name, no logos.** A single PathMNIST tile fills the frame.
- **Image to use:** pull one colorectal-epithelium (class "TUM" — tumor epithelium) tile from `Phase7_PathMNIST.ipynb` cell 1. 28×28 upsampled to 800×800 with nearest-neighbour, so the pixels are visible.

### You say (verbatim — ~140 words, 60s natural pace)

> *(point at the image, pause 2 seconds)*
>
> "What is this?
>
> *(let the room try to guess. 4-second pause.)*
>
> It is colorectal cancer epithelium. Twenty-eight pixels by twenty-eight pixels.
>
> A standard convolutional network — a ResNet-18 — classifies images like this with 91% accuracy on a nine-class pathology benchmark. It uses about 11 million trainable parameters to do so.
>
> Today I want to show you something different. We encoded the same kind of image as a quantum state, with **no trainable quantum parameters at all**, and then handed it to a small classical network.
>
> On a sibling dataset — blood cells — that approach reached 95.6% accuracy, within 0.2 points of the ResNet, with roughly one twenty-seventh of the parameters.
>
> So the question is: what is quantum encoding actually doing here? And does it always help? Those are the two questions I'll answer."

### Cue

- *(advance to Slide 2 — title now appears for the first time, top corner, small)*
- **Title-appearance line (spoken):** "Quantum-enhanced feature extraction for biomedical imaging."

### Why this works

- Audience commits to the problem before they know the speaker. The unknown image is a hook anyone in a science congress engages with — including non-imaging folks.
- The 95.6% number lands once, with the framing "near SOTA at 1/27th parameters." You don't need to repeat the ratio.

---

## Slide 2 — Three quantum primitives, no math (2:00)

### On screen

- Three icons in a row, large, with a one-word label under each:
  - **Left:** a continuous dial — label **SUPERPOSITION**
  - **Centre:** two sine waves overlapping (one crest, one cancellation point) — label **INTERFERENCE**
  - **Right:** two filled circles joined by a thick line, single rounded outline around both — label **ENTANGLEMENT**
- Optional: title at top "Three things classical computers cannot do."

### You say (~190 words, 110s natural pace)

> "Classical computers process bits — zero or one, on or off. Everything they do reduces to deterministic flips.
>
> Quantum systems can do three things classical bits cannot.
>
> **One.** A qubit can be in a superposition of states. It is not just zero or one — it holds a continuum, weighted by probability amplitude.
>
> **Two.** Those amplitudes interfere. They add up like waves on water — sometimes constructive, sometimes destructive. Calculations that would take a classical computer trillions of steps can be solved by *arranging* interference correctly.
>
> **Three.** Two qubits can be entangled. Their joint state is not the product of two independent states. The information lives between them — neither one carries it alone.
>
> *(pause)*
>
> Now, I am not going to claim quantum computers will replace classical ones tomorrow. They will not. But for *certain* problems — and image encoding is one of them — these three properties give us tools that classical preprocessing simply cannot reach. Let me show you why."

### Cue

- Hand gesture pointing right toward Slide 3.
- **Drop entirely from the original draft:** "drop a pebble in water, characterise the wave, escape the local minimum." Different paper class. Cut clean.

---

## Slide 3 — Why entanglement, not PCA (2:00)

### On screen

- Two cartoon plots, side by side, large.
  - **Left:** correlated 2D scatter (e.g. tilted ellipse of points). Title: **CLASSICAL — DECORRELATE.** Arrow shows PCA rotation onto axes labelled PC1, PC2.
  - **Right:** same correlated scatter, but a single big curly bracket pulls the whole cloud into a quantum-state symbol |ψ⟩. Title: **QUANTUM — ENTANGLE.**
- Bottom strip, one line: *"Correlation: a cost to flatten, or a feature to store?"*

### You say (~180 words, 105s)

> "Here is where classical machine learning meets a wall.
>
> When two features in your data are correlated — say, the red and green channels of a tissue image, which are nearly always correlated — classical preprocessing **decorrelates** them. Principal component analysis rotates the data onto axes where the features are independent. We do this because in classical computation, redundant dimensions cost data, and data is expensive.
>
> Quantum encoding goes the opposite direction. Entanglement *keeps* the correlation. It stores the joint relationship between two features as a single quantum amplitude — one number that knows about both channels at once.
>
> *(pause, point at right panel)*
>
> Correlation is not a cost any more. It is a feature you encode directly.
>
> This is the core intuition behind my work. **Instead of flattening correlation away, we ask: can we use it?**
>
> The next slide tests that question."

### Cue

- Emphasise "ask: can we use it?" — that's the bridge to Slide 4.

### Words to avoid

- "Discard." PCA *rotates*, doesn't discard. Say "decorrelate" or "flatten."
- "Leverage." Buzzword. Say "use" or "encode."

---

## Slide 4 — The entanglement knob (3:00)

### On screen

- Horizontal bar across the slide, left → right gradient (light grey → dark blue), labelled **ENTANGLEMENT** with arrow.
- Six labelled tick marks along the bar, left to right:
  - **Sep** (no entanglement, product state)
  - **CRyE** (controlled Y-rotations)
  - **GBE** (GHZ-style entanglement)
  - **PA-CSE** (pixel-adaptive correlation encoding)
  - **CP-2L** (controlled-phase, 2-layer data re-uploading)
  - **CSE** (continuous-α correlation-sensitive encoding)
- Below the bar: a grey box labelled **SAME CLASSICAL MLP**. Arrow goes from each tick into the box.
- Top right corner: a small inset showing the three measurement bases X, Y, Z as three coloured axes.

### You say (~280 words, 170s)

> "To test whether entanglement actually helps, I designed six different ways to encode an image as a quantum state.
>
> Think of this as a tuning knob.
>
> *(point left)*
>
> On the left end of the knob: **separable encoding** — each pixel becomes a qubit, no entanglement between them. This is our quantum-but-unentangled control.
>
> *(point right)*
>
> On the right end: **data-dependent entangling schemes** — encoders where the entanglement structure between qubits depends on the actual pixel values of the image. The strongest of these is what we call CSE, **continuous-alpha correlation-sensitive encoding**. It uses controlled rotations whose angles depend on per-image colour correlations.
>
> *(point at the gradient bar)*
>
> Between those two ends sit four intermediate schemes — increasing entanglement in different structural ways. Some use phase gates, some use rotation gates, some use GHZ-style cascades.
>
> *(pause, point at the bottom grey box)*
>
> The crucial point: **the downstream classical model is the same for all six.** Same multilayer perceptron, same training procedure, same number of features. **The only thing that changes is the quantum encoder.**
>
> That isolation is what makes this a fair test. If we see a performance difference between schemes, we know it comes from the quantum part — from entanglement structure — and not from a better classifier or extra parameters.
>
> Also — we measure each quantum state in three bases, X, Y, and Z. Different bases reveal different information about the same state, so we lose nothing.
>
> *(pause)*
>
> Now: what did we actually find?"

### Cue

- "What did we actually find?" → advance to Slide 5.
- Take a breath before Slide 5. This is your most content-dense slide; pace matters.

---

## Slide 5 — What we found (3:00)

### On screen

- Two-panel figure, full width.
  - **Left panel:** bar chart, three bars — *Our quantum encoder (CP-2L) 95.6%*, *Classical SOTA ResNet-18 95.8%*, *Raw RGB baseline 92.7%*. Annotate "~400K params" under our bar and "~11M params" under the ResNet bar. Dataset label: **BloodMNIST.**
  - **Right panel:** quintile bar chart from `paper/figures/fig_mechanism.pdf` panel B — CSE accuracy gain over Sep, stratified by per-image correlation ρ, five bins. Dataset label: **PathMNIST.**
- Title strip across top: **Two findings.**
- Bottom strip, small text under right panel: *β_ρ = +0.46 (CSE),  ≈ 0 (CRyE, CP-2L)*

### You say (~290 words, 175s)

> "Two findings — one positive, one nuanced.
>
> *(point at left panel)*
>
> **Finding one.** On a blood-cell dataset — where colour channels carry strong diagnostic information — our quantum encoding reached 95.6% classification accuracy. The ResNet-18 baseline reaches 95.8% — a 0.2 percentage point difference, statistically insignificant.
>
> The ResNet uses 11 million trainable parameters. Our system uses about 400,000.
>
> That is the headline: **near-classical accuracy, dramatically fewer parameters.** Encoding alone — *no quantum training* — is doing the work.
>
> *(turn, point at right panel)*
>
> **Finding two — and this is where it gets interesting.** On a harder dataset — colorectal pathology, the image I showed you at the start — the *average* difference between entangling and non-entangling encoders is small. Almost nothing.
>
> So I asked a different question. Not: does entanglement help on average? But: does entanglement help **per image**?
>
> *(point at the bars)*
>
> When I stratified by how correlated the colour channels were in each individual image — that is what the five bins on the right are — one encoder, CSE, started behaving differently. On the high-correlation tissues — bins three and four — CSE outperformed the non-entangling baseline by 4 to 5 percentage points.
>
> The others — the gates without continuous correlation sensitivity — show no effect. Flat zero across all bins.
>
> *(pause, emphasise)*
>
> So entanglement is not a universal advantage. It is a **conditional** advantage, and we can now say *which* condition: **when the data carries the kind of correlation structure the encoder is built to use.**
>
> This is, to my knowledge, the first per-image mechanism verification for a quantum encoder."

### Cue

- "First per-image mechanism verification for a quantum encoder" — let it land. Pause. Then move to Slide 6.
- **Numbers locked from `paper/main.tex`:** 95.6% (CP-2L BloodMNIST), 95.8% (ResNet-18), 91% (PathMNIST ResNet-18, mentioned in hook), β_ρ = +0.46. Audit these against the submitted paper Tuesday night.

### Backup slide (only if asked)

- Title: *How β_ρ is measured.*
- Single panel: scatter from `fig_mechanism.pdf` panel A (binned scatter of scheme-correct probability vs ρ).
- Spoken if asked: "We ran a logistic regression — does this scheme classify image *i* correctly — with two predictors: the image's per-channel correlation ρ, and whether the separable baseline got it right. The coefficient on ρ — β_ρ — measures how much entanglement helps as a function of correlation, controlling for hardness. CSE: +0.46. The others: indistinguishable from zero."

---

## Slide 6 — What's next (1:00)

### On screen

- Three labelled lanes, equal width, no body text:
  - **ECG / temporal signals** (icon: ECG trace)
  - **Symmetry-aware encoders** (icon: a circuit diagram with a coloured node)
  - **Hardware-aware design** (icon: a chip)
- Bottom of slide, one line: **Quantum doesn't always help. Knowing when it does — and why — is the work.**
- Bottom-right corner, small: your name + email + acknowledgements line.

### You say (~120 words, 60s)

> "Where this goes.
>
> *(point at left lane)*
>
> First — does this transfer beyond images? I am running a follow-on study on single-lead ECG, where the channels are not colour but morphology, slew, and envelope. Same encoder family, different physical signal.
>
> *(point at centre lane)*
>
> Second — the encoders that *failed* tell us something specific about the mathematical structure of the pooling operation. We can design future encoders to break that symmetry on purpose.
>
> *(point at right lane)*
>
> Third — none of this has run on actual quantum hardware yet. The next step is bringing real device constraints into the encoder design itself.
>
> *(pause)*
>
> **Quantum doesn't always help. Knowing when it does — and why — is the work.**
>
> Thank you."

### Cue

- Title slide stays. Don't put up a "Thank you" slide. The last sentence *is* the thank you.
- Wait for applause to settle, then: "I'm happy to take questions."

---

## Q&A preparation (likely questions + ~30s answers)

### Q1: "Did you run this on a real quantum computer?"

> "Not yet. Everything I showed runs in classical simulation — six qubits is small enough to simulate exactly. The next step is testing on actual NISQ hardware. The challenge is that the encoders use continuous rotations, and current hardware has gate-fidelity limits that will degrade the per-image correlation signal. So part of the future work is asking: is this advantage robust to gate noise?"

### Q2: "Is this faster than classical?"

> "No. Quantum simulation is slower than direct classical computation today. The argument is not speed. It is **representational efficiency** — fewer parameters carrying more information. If you can do as well with 400,000 parameters as a classical model does with 11 million, that matters for low-power edge applications — implantable diagnostics, medical robotics, anything bandwidth-limited."

### Q3: "Why didn't all six entangling encoders show the same effect?"

> "Excellent question — that *is* the architectural finding. Most of the encoders use fixed gates whose pooled output is symmetric under a relabelling of measurement outcomes. That symmetry makes them invisible to the downstream classifier — like a particle moving in a periodic potential, where certain energies are forbidden by symmetry. The CSE encoder breaks that symmetry because its rotation angles are continuous functions of the data."
> *(This is the Kronig-Penney intuition — only deliver if asked.)*

### Q4: "What is this for, practically?"

> "Two near-term applications: medical-image classification at the edge — handheld devices, low-power diagnostic tools — and low-photon imaging, where the input is noisy and correlations between pixels carry the signal. Both regimes are bottlenecked by classical model size, and both have the kind of correlation structure our encoder is built to use."

### Q5 (hostile): "Isn't quantum machine learning overhyped?"

> "Yes, often. Most claims of quantum advantage in ML are about asymptotic complexity arguments that don't survive contact with real datasets. That's why I structured this work as a falsifiable test — six encoders along an entanglement axis, same classifier, per-image mechanism verification. I'd rather find a small, defensible result than claim a large one I can't reproduce. The headline isn't 'quantum wins'; it's 'here is the precise condition under which quantum encoding helps.'"

### Q6: "How long did training take?"

> "About 20 minutes per scheme on a laptop GPU. The expensive part is the quantum simulation — encoding 90,000 images through the multi-basis observation pipeline — which we cache once. After that, the classical MLP trains in under five minutes per seed."

---

## Pre-talk checklist (Wednesday 13 May)

- [ ] Pull the PathMNIST hook image: open `Phase7_PathMNIST.ipynb`, run cell 1, screenshot one TUM-class tile, upsample to 800×800 nearest-neighbour
- [ ] Verify `paper/figures/fig_results_bar.pdf` opens cleanly and the BloodMNIST panel is usable as-is (or extract just that panel into a separate image)
- [ ] Verify `paper/figures/fig_mechanism.pdf` panel B is the quintile bar chart for Slide 5 right panel
- [ ] Verify `paper/figures/fig_mechanism.pdf` panel A is the binned scatter for the backup Q-and-A slide
- [ ] Audit numeric claims against `paper/main.tex`: 95.6, 95.8, 91, ~11M, ~400K, β_ρ = +0.46
- [ ] Rehearse the 90-second hook three times out loud — pacing is everything
- [ ] Rehearse Slide 5 once — three minutes is the longest single segment
- [ ] Time a full pass — target 12:00–12:30. If over 13:30, cut 30 seconds from Slide 4 (the longest descriptive slide)
- [ ] Charge laptop. Carry a USB stick with the slides and a backup PDF.

---

## What NOT to do

1. **Don't open with the title slide.** Open with the image. Title appears after the hook.
2. **Don't show equations.** Not one. If someone asks, you can write β_ρ on a whiteboard during Q&A.
3. **Don't say "QPIE."** Say "the quantum encoder" or "our encoding scheme."
4. **Don't promise quantum supremacy.** Conditional advantage, defensible. That's the voice.
5. **Don't apologise.** No "I'm just a student," no "this is very preliminary." State results, take questions.
6. **Don't read your slides.** Slides have visuals + one line of text at most. The speaking is yours.

---

## File references

- Canonical numbers: `/Users/eldana/Documents/Quantum/Thesis/QIP/paper/main.tex`
- Slide 5 left panel source: `paper/figures/fig_results_bar.pdf`
- Slide 5 right panel + Q-backup source: `paper/figures/fig_mechanism.pdf`
- Hook tile source: `Phase7_PathMNIST.ipynb` cell 1
- This script: `/Users/eldana/Documents/Quantum/Thesis/QIP/talk/icssc_2026_talk.md`
- Research-angle queue (NOT for this talk): `~/.claude/projects/-Users/memory/project_qpie_research_angles.md`
