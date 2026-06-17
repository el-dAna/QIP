# Arm 1 substrate — Phase 0 table (built 2026-06-17)

Source of truth: `_perscheme_results.json` (per-scheme, single run, NO seeds/CI) +
`_ecg_rawbaseline.json` (ECG raw ROCKET baseline, 5 seeds). ECG QPIE per-scheme numbers
still need tracing from `Phase8_PhysioNet2017_ECG.ipynb` (memory: Sep/PA-CSE ~0.669/0.670,
QMBC-Net −10.7 vs CNN — TRACE BEFORE CITING).

## Per-scheme single-run accuracy (multivariate, all 3-channel)
Δ_ent = best entangling single-scheme acc − Sep (separable) acc.

| Dataset                | K  | channels | raw   | Sep    | best entangling (scheme) | Δ_ent   | headroom (1−raw) |
|------------------------|----|----------|-------|--------|--------------------------|---------|------------------|
| Handwriting            | 26 | 3 (x,y,force) | 0.593 | 0.401  | 0.428 (CRyE)             | **+0.027** | 0.407 |
| Epilepsy               | 4  | 3        | 1.000 | 0.949  | 0.957 (CP-2L)            | +0.007  | 0.000 |
| CharacterTrajectories  | 20 | 3        | 0.997 | 0.9937 | 0.9944 (GBE)             | +0.0007 | 0.003 |
| UWaveGestureLibrary    | 8  | 3 (x,y,z)| 0.888 | 0.9125 | 0.9094 (CRyE)            | **−0.003** | 0.112 |
| EthanolConcentration   | 4  | 3        | 0.293 | 0.308  | 0.300 (CSE)              | −0.008  | 0.707 (all near chance) |

Schemes present: Sep, CRyE, GBE, CP-2L, CSE.
ASSUMED ordering (CONFIRM WITH USER): Sep = separable/no-entanglement baseline;
CRyE / GBE / CP-2L / CSE = entangling variants of varying strength.

## ECG anchor (PhysioNet2017) — single channel
- 1 lead → ZERO cross-channel structure by construction.
- Hypothesis predicts entanglement-null here (no joint structure to exploit). Memory says
  the ECG run confirmed this (QMBC-Net hard fail, schemes ≈ tied near 0.67). This is the
  zero-coupling anchor of the Arm 1 curve.

## ADVERSARIAL FINDINGS — read before building the metric
1. **The clean "entanglement helps UWave, fails ECG" headline is FALSE on canonical splits.**
   On UWave per-scheme, Sep (separable) is the BEST single scheme (0.9125); entanglement
   is −0.003. The 0.976 UWave "positive" in memory was a cross-scheme ENSEMBLE on an
   expanded split — not single-scheme entanglement on the canonical split. Do not build the
   thesis on the ensemble number and call it an entanglement effect.
2. **All Δ_ent are tiny and have NO error bars.** Range +0.027 to −0.008, single runs.
   These are plausibly within seed noise. RIGOR GATE: re-run per-scheme with ≥5 seeds and
   report CIs BEFORE asserting any entanglement effect. The ECG json already has 5 seeds;
   the multivariate per-scheme does not.
3. **Two competing explanatory variables, currently confounded:**
   - (a) cross-channel coupling (the hypothesis we wanted: entanglement helps when channels
     are jointly informative — Handwriting x/y/force is highly coupled, biggest Δ);
   - (b) accuracy headroom / task difficulty (entanglement only has ROOM to help where
     accuracy isn't saturated — Δ→0 on CharTraj/Epilepsy ceilings, noise on Ethanol floor).
   Arm 1's real job is to DISENTANGLE (a) from (b). A metric that predicts Δ_ent only because
   it correlates with difficulty is not an entanglement-structure result.

## Revised Arm 1 hypothesis (sharper, honest)
Entanglement benefit Δ_ent is a function of BOTH cross-channel coupling C and available
headroom H. Predict Δ_ent from a coupling metric C *after controlling for H*. Single-channel
ECG (C=0) anchors the low end. Falsify if C adds no predictive power over H alone.
