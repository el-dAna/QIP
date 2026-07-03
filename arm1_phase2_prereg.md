# Arm 1 — Phase 2 decisive experiment: PRE-REGISTRATION
Locked 2026-06-18, before any model run. No baseline moves after results are seen.

## The claim this tests (the thesis spine)
Thesis title promises "...Governed by **Data Structure**." The falsifiable claim:
**entanglement in a fixed quantum encoding helps a biomedical task ONLY when the data
carries matching multi-channel joint structure (cross-channel coupling).**

Right now this half of the thesis is UNPROVEN. It rests on:
- ECG (single-lead → zero cross-channel coupling by construction) → entanglement-null. One anchor.
- Multivariate per-scheme Δ_ent: tiny, single-run, NO confidence intervals, and CONFOUNDED
  with accuracy headroom. (Phase-0 adversarial finding: a metric that "predicts" Δ_ent only
  because it tracks task difficulty is not an entanglement result.)

So we have a 2-point curve plus a noisy cloud. Phase 2 closes it.

## Definitions (locked)
- **Δ_ent (the readout):** for one dataset, on one classifier rung, with ≥5 seeds,
  Δ_ent = acc(entangling scheme) − acc(Sep). Sep = the separable / no-entanglement encoding.
  Δ_ent is a WITHIN-DATA difference: entangling scheme and Sep see the *same* input, so the
  difference isolates the entanglement-specific effect at that operating point.
  Report per-scheme (Δ for CRyE, CSE, GBE, CP-2L vs Sep) AND the best-entangling Δ, each with CI.
- **C — cross-channel coupling (the predictor):** how statistically dependent the channels are
  within a sample. **PRIMARY = mean absolute pairwise cross-channel correlation |ρ|** (averaged
  over time and samples), LOCKED 2026-06-18. Cross-channel mutual information kept only as a
  robustness check. C is a per-dataset scalar.

  **WHY correlation is primary (MUST go in the next manuscript — user instruction 2026-06-18):**
  1. **Mechanism-matched.** The entangling encodings condition on *linear* cross-channel
     correlation — CSE/PA-CSE apply ρ-conditioned angle shifts, and Paper 1's β_ρ mechanism is
     defined directly on the per-image channel correlation ρ. |ρ| is therefore the predictor that
     matches what the gates actually exploit; an arbitrary dependence measure would not connect the
     coupling axis to the established mechanism.
  2. **Continuity / traceability.** |ρ| is already computed and reported in the pipeline
     (Phase7_UWave `agg` C(24,2) correlation block; Paper 1 β_ρ). Reusing it keeps the coupling
     axis consistent with published numbers and every value traces to an existing cell (paper rule #2).
  3. **Estimator robustness.** Correlation is a single bounded scalar with no free parameters.
     Mutual-information estimation on continuous multivariate series is estimator-dependent
     (binning / kNN-k choices) and high-variance at these sample sizes (N_train as low as 120–150);
     using it as primary would inject a noisy, hard-to-defend quantity. MI is robustness only.
- **H — headroom (the confounder to control):** H = 1 − acc(Sep). How far the separable
  baseline sits below the perfect-accuracy ceiling. A saturated dataset (Sep ≈ 0.99, H ≈ 0)
  leaves no room for ANY encoding to show a benefit, so Δ_ent is mechanically squeezed toward 0
  regardless of coupling. H must be controlled or it masquerades as the coupling effect.

---

## PRIMARY TEST — within-dataset channel-decoupling ablation (CAUSAL)
The cross-dataset correlation (below) is weak on its own (only 5–6 datasets). The decisive
test is causal and within-dataset, so headroom is held fixed by construction.

**Manipulation — coupling-destroying surrogate.** For each sample, shift each channel in time
*independently* by a random circular offset (per-sample, per-channel random circular time-shift).
- Destroys cross-channel SYNCHRONY at matched timesteps — exactly the joint structure the
  entangling gates act on when QPIE encodes the channels of one patch into one quantum state.
- PRESERVES each channel's marginal distribution and its own within-channel temporal content.
- PRESERVES the label (still the same sample's three channels, just desynchronised).

**Prediction (H1, decisive):** on the surrogate, Δ_ent collapses toward 0 on every dataset that
showed Δ_ent > 0 on real data. Sep should be ~unchanged or only mildly degraded (it never used
cross-channel coupling), so any Δ_ent shrinkage is attributable to lost coupling, not lost info
in general.

**Falsification:** if Δ_ent does NOT shrink on the decoupled surrogate (i.e. entanglement helps
just as much with the cross-channel structure destroyed), the coupling hypothesis is WRONG.
Report it as a failed principle. Do not rescue it.

**Control for the floor:** the surrogate also lowers absolute accuracy; if it pushes a dataset to
the chance floor, Δ_ent is compressed mechanically (no room for any scheme to differ) and the
test is uninformative there. Pre-commit: only datasets whose surrogate Sep-accuracy stays
≥ (chance + 0.10) count toward H1; others reported as floor-censored, not as confirmations.

**Seeds & stats:** ≥5 seeds per (dataset × scheme × {real, surrogate}). Paired t-test of
Δ_ent(real) vs Δ_ent(surrogate) per dataset; report effect size + CI, not just p.

---

## SECONDARY TEST — cross-dataset C-vs-Δ_ent, controlling for H (CORRELATIONAL, supporting only)
Across the 5–6 datasets (UWave, Epilepsy, CharacterTrajectories, Handwriting,
EthanolConcentration, + MedMNIST/ECG as coupling extremes), regress:
  Δ_ent  ~  C  +  H
Test the partial effect of C (does coupling predict entanglement benefit AFTER removing the
headroom effect?). 

**HONEST LIMITATION, stated up front:** n ≈ 5–6 datasets. Two correlated predictors on 6 points
is badly underpowered — this regression CANNOT cleanly separate C from H. It is reported as
SUPPORTING / suggestive evidence only, never as the decisive result. The primary causal test
above carries the claim. (Writing this down now so we don't over-read a lucky p-value later.)

---

## ANCHOR (already done, no re-run)
- PathMNIST dose-response (Paper 1, 5 seeds, paired t-tests): CSE +0.0164 p=0.0003 helps →
  PA-CSE −0.0137 p=0.0075 hurts. This is the ENCODING-DOSE axis (how much entanglement),
  distinct from the DATA-COUPLING axis tested here. Both axes together = the full principle.
- ECG (single-lead, C ≡ 0): entanglement-null. The zero-coupling endpoint of the C axis.

## Scope discipline (pre-committed)
- Classifier rung: the 1D CNN soft-vote ensemble (the rung Δ_ent is currently reported on),
  to keep the readout comparable to existing tables. Optionally confirm top hits on the SOTA
  deep model, but CNN is the registered primary.
- Encoders: the 5 canonical schemes only (Sep, CRyE, GBE, CP-2L, CSE). No new scheme #6+.
- Datasets: the existing 5 UEA + the two coupling extremes already on disk. No new datasets
  added to chase a cleaner curve (Holmes 2022 expressibility-trainability tension makes "more
  knobs" self-defeating; we are testing a principle, not tuning).
- Environment: msc_venv (`/Users/eldana/Documents/Quantum/msc_venv/bin/python`); aeon-deep-net
  python-version guard neutralised as in prior runs.

## Decision gate
- H1 confirmed (Δ_ent shrinks on decoupled surrogate, on the non-floor-censored datasets)
  → the data-structure half of the thesis is proven; write it up. Arm 1 complete.
- H1 fails → principle falsified on the coupling axis; the thesis becomes a narrower
  dose-response + boundary story. Honest, still a thesis, but reframe.

---

## REVISION 2026-06-18/19 — SUBSTRATE PIVOT to the image domain (pre-result, design refinement)
Decided from the smoke + the EXISTING Phase-0 Δ_ent table, BEFORE seeing any decoupling result —
so this is a legitimate design refinement, not a post-hoc baseline move.

**Why the UEA substrate is near-powerless for the PRIMARY test.** The within-dataset decoupling test
asks "does the entanglement benefit Δ_ent shrink when coupling is destroyed?" But on every UEA/TSC
dataset Δ_ent ≈ 0 ALREADY (Phase-0: +0.027 → −0.008, all ~noise). You cannot shrink an effect that is
already zero. Smoke confirms the substrate is wrong two ways: (a) Epilepsy real Δ_ent ≈ +0.007; (b)
the decoupling barely moves coupling there (|ρ| 0.21 → 0.18 — Epilepsy has almost no genuine
cross-channel coupling to destroy).

**The right substrate = images, where entanglement demonstrably helps.** PathMNIST: CSE +0.0164,
p=0.0003, β_ρ=+0.46 (real RGB channel mechanism). Smoke + full run confirm huge manipulation range:
per-image |ρ| **0.93 → 0.085** under decoupling (genuine coupling 0.85).

**Revised roles:**
- **PRIMARY (causal):** channel-decoupling on PathMNIST (+ BloodMNIST replication). Surrogate =
  per-image, per-channel independent 2-D circular spatial roll. Readout Δ_ent = acc(scheme) − acc(Sep),
  5 seeds, paired, real vs decoupled. H1: CSE Δ_ent>0 collapses toward 0 on decoupled. Bonus: PA-CSE
  *hurt* should also be coupling-dependent.
- **NEGATIVE CONTROL:** the UEA within-dataset decoupling (expect NO shrink — nothing to remove;
  guards against the surrogate manufacturing artifacts).
- **SECONDARY (observational):** cross-domain gradient PathMNIST (high coupling, helps) → UEA (low,
  no effect) → ECG (zero, null).

**Code home (logged 2026-06-19):** `Thesis_Mechanism_Spine.ipynb` cells — design md, DECISIVE image
run (cell writes `_arm1_img_decouple.json`), result md, UEA negative-control (writes `_arm1_decouple.json`).
Image encoders AST-extracted from `Phase7_PathMNIST.ipynb` (raw uint8 [0,255]); UEA from `Phase7_UWave.ipynb`.
