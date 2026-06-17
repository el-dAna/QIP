# MSc Thesis Spine — locked 2026-06-17

## Title (working)
**Entanglement as an Inductive-Bias Injector in Biomedical Learning: Encoding and Initialization, Governed by Data Structure**

## Thesis claim (falsifiable)
Quantum entanglement improves a biomedical learning task *only when the data carries
matching multi-channel joint structure*. We test this on two fronts that share one
ablation methodology — remove the entanglement, measure what is lost — and one theory:
quantum inductive bias helps iff it matches data structure (Huang et al. 2021;
Kübler et al. 2021).

This is an **extension / application** study, not a new method (paper rule #1).
The expected result on the advantage axis is null-or-marginal; the contribution is
the *predictive principle*, not a supremacy claim.

## Theory backbone (citations — kill our own dangles)
- Schuld, Sweke, Meyer, PRA 103, 032430 (2021) — encoding sets the Fourier spectrum.
- Holmes, Sharma, Cerezo, Coles, PRX Quantum (2022) — expressibility ↔ trainability tension.
- McClean et al., Nat. Commun. (2018) — barren plateaus.
- Huang et al., Nat. Commun. (2021) — power of data; advantage needs geometry alignment.
- Kübler, Buchholz, Schölkopf, NeurIPS (2021) — inductive bias of quantum kernels.
- Mari et al., Quantum (2020) — hybrid transfer learning (prior art for Arm 2).
- Benedetti et al. (2019); Liu & Wang (2018) — quantum circuit Born machine (init sampler).

---

## Arm 1 — Entanglement in the ENCODING (consolidation of existing results)
**Question:** Why did the joint Pauli correlator carry signal on UWave (0.976) but
not on ECG (cross-domain entanglement null)?

**Hypothesis:** entanglement benefit tracks the data's intrinsic multi-channel joint
dependence. Gesture trajectories have real cross-axis structure; ECG morphology is
dominated by separable/local single-lead features a product encoding already captures.

**Design:**
- Define a measurable data-correlation-structure metric (candidate: cross-channel
  mutual information / cross-channel covariance rank / joint-vs-marginal divergence).
- Datasets: UWave (positive), ECG (null), MedMNIST subset (held-out test of the metric).
- **Falsifiable kill:** if the metric does NOT rank-order the observed entanglement
  benefit across the three datasets, the predictive principle fails — report as such.

Source results already on disk — do not re-run from scratch, pull from Paper 2 + Paper 3.

---

## Arm 2 — Entanglement in the INITIALIZATION (new bounded swing)
**Question:** Does a quantum-correlated weight-init distribution plant a small classical
biomedical classifier in a better-conditioned region than He/Xavier?

**Why it is clean:** circuit used as a FIXED SAMPLER, not trained → no barren plateau.

**Pre-registered init conditions:**
1. He
2. Xavier
3. Orthogonal
4. Entangled-circuit-sampled weights
5. Product-circuit-sampled (entanglement ABLATION — same circuit, entangling gates off)
6. **Classical-distribution-matched-to-quantum-marginals** ← the deciding control

**Pre-registered metrics:** epochs-to-accuracy-threshold; final test accuracy;
loss-landscape sharpness at init (Hessian-trace or SAM-style); across-seed variance
(≥3 seeds).

**Hypotheses:**
- H1 (speed): entangled init reaches threshold in fewer epochs than He.
- H2 (mechanism, decisive): entangled beats BOTH product-circuit (5) AND
  marginal-matched classical (6). If it does not beat (6), the effect is classically
  reproducible → quantum-ness null.
- H3 (landscape): entangled init lands in flatter region (lower Hessian trace).

**Dataset:** ECG features (reuse Paper 3 pipeline) — lets Arm 2 speak to Arm 1's null.

**KILL CRITERION:** by ~mid-July, if condition 6 matches condition 4 within noise across
≥3 seeds × the ECG set, declare quantum-correlation null, freeze Arm 2 at current scope,
write it up as a clean negative. Do not expand to more datasets/architectures chasing a win.

---

## Summer timeline (anchored to TODO: confirm defence date)
- **Phase 0 — now → ~Jun 24 (1 wk):** lock spine (done); pull UWave + ECG results into
  one table; pre-register Arm 2 conditions + metrics in this file.
- **Phase 1 — ~Jun 24 → ~Jul 15 (3 wk):** Arm 2 build + condition-6 deciding experiment.
  HARD KILL DATE ~Jul 15.
- **Phase 2 — ~Jul 15 → ~Aug 5:** Arm 1 predictive-metric study across UWave/ECG/MedMNIST.
- **Phase 3 — ~Aug 5 → ~Aug 25:** synthesis + weld both arms into thesis chapters.
  **Taper hard the last week of Aug — Schwarzman personal deadline 30 Aug outranks.**
- **September:** revision mode; Seriti manufacturer deadline 30 Sept competes for attention.

## Standing rules
- Mechanism/ablation framing from day one. Never need the result to "win."
- Every number traces to a notebook cell (paper rule #2).
- Pre-register before running. No moving the baseline after seeing results.
- Auto-save progress to project_qpie_*.md without being asked.
