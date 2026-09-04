# wiring-not-weights: evaluation

- External home: `~/Desktop/Research/projects/Neuroscience/Neuro-AI/wiring-not-weights/`
  (confirmed present: HCP_DATA_INSTRUCTIONS.md, PREREG_exp01_apparatus.md, README.md, RESULTS.md,
  SCOPE_exp04_real_mve.md, exp01-exp06 scripts, paper/, results/). Note: `aaygan29/wiring-not-weights`
  does not resolve via `gh repo view` (checked this pass); the memory's claim of a pushed personal
  GitHub repo could not be confirmed live: treat as unverified until re-checked with a working
  `gh` auth or by asking the user for the current remote status.
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Exploratory: identity is carried by the weights up to functional-degeneracy equivalence,
not by wiring alone; a synthetic apparatus and a nonlinear (Marder-style) degeneracy test
both confirm the thesis, a real powered ABIDE connectome-fingerprint result (n=248)
confirms wiring suffices for identification (a different, already-conceded axis), and the
decisive real-data reconstruction test (NSD, n=8) is honestly null for lack of power.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | ABIDE pulled via anonymous unsigned S3 from the public fcp-indi bucket; NSD data traced to local `algonauts_shared268_features.npy` and `_n8work/matrices/subjNN.npz`; `HCP_DATA_INSTRUCTIONS.md` documents the gated path honestly as blocked rather than faked. |
| G2 seed variance (n>=5)      | pass | exp06 is explicitly a seed-robustness script; the apparatus-validation result replicates across R=20 cohorts and the identity-sufficiency curve across R=15 repeats. |
| G3 specification robustness  | pass | The predicted FULL~WITHIN >> OUTSIDE~WIRING~NULL~chance ordering replicates 100% across 6 SNR x signal regimes. |
| G4 specificity ablation      | pass | The exact-null-space degeneracy control is perfectly flat (functional-equivalence confirmed) and the FUNC_RAND arm sits at chance, exactly the ladder's matched-control-removes-mechanism test. |
| G5 confound control          | partial | Capacity-matching directly addresses the council-flagged "capacity masquerading as identity" confound; the ABIDE result honestly flags an uncontrolled multi-site scanner confound and a within-session (not cross-session) split-half inflation risk rather than hiding them. |
| G6 mechanism/necessity       | pass | exp03b's Marder nonlinear test: hidden-unit permutation+rescaling symmetry changes weights by ||dW||/||W||=1.57 with identity unchanged, while an equal-magnitude functional perturbation collapses identity (d=33): a clean necessity intervention. |
| G7 calibration                | unscored (no evidence available; no ECE/conformal reported for this project's identity scores) | |
| G8 external validity          | partial | Two real, independent datasets are used (ABIDE n=248 for identification, NSD n=8 for reconstruction), but they test different senses of the thesis (identification vs. reconstruction); the core reconstruction claim is real-data-tested on only one, underpowered dataset. |
| G9 measurement reliability    | pass | Split-half fingerprinting on ABIDE: FULL_weighted 0.980, WIRING_binarized 0.972 (chance 0.004): a direct, real-data measurement-reliability check. |
| G10 reproducibility            | partial | Efficiency work is documented (vectorized ABIDE perm-null: 100s to 6.85s, identical result), and scripts are organized per-experiment (exp01-exp06); no single top-level `make reproduce` target was found. |
| G11 ethics/safety              | pass | Public data only (ABIDE, NSD); no PHI; explicit statement to engage related external work (Nectome) on science only and never the associated fatal procedure. |
| G12 analytic integrity         | pass | `PREREGISTRATION.md` (exp01) and `SCOPE_exp04_real_mve.md` are written before those runs; the N=8 NSD null is reported honestly as underpowered rather than as a negative finding, and the council's MAJOR REVISION critique (thesis sound, first experiment broken) is folded into the design rather than hidden. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; NSD reconstruction is tested at the group level with subject-level fingerprints, not a formal held-out-subject predictive CV) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | fail (honestly reported) | At N=8 (chance 0.125), neither functional (acc 0.175, 0/25 ROIs p<.05) nor weight fingerprint (acc 0.205, 1/25 uncorrected) individuates above chance; this is the decisive, underpowered null the project itself flags rather than downplays. |

Because the fMRI triad is not established for the reconstruction claim, no G7/G8/G12
upgrade is applied to that specific claim; the pass scores above for G7-adjacent gates
rest on the ABIDE identification axis and the synthetic apparatus, not on the
reconstruction result.

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not an LLM-decision instrument. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `neural_alignment_score` (identity-sufficiency
curve), `sparse_circuit_id` (weight-function equivalence class as a mechanism handle).
Methodologically the strongest-evidenced project in the portfolio; the one open gap is a
powered real-data reconstruction dataset.

## Open action items

- [ ] Obtain a many-subject stimulus-evoked reconstruction dataset (the project's own
  stated gap; HCP-identification would only reproduce the already-conceded ABIDE
  identification result, not adjudicate the reconstruction thesis): the single highest-
  leverage next step for this project.
- [ ] Re-verify the `aaygan29/wiring-not-weights` GitHub remote status; `gh repo view`
  could not resolve it this pass, which conflicts with the memory's "pushed" record.
- [ ] Report an explicit per-participant sign-concordance binomial (G-fMRI.2) once a
  powered reconstruction dataset is available, to actually complete the fMRI triad.
