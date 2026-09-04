# Protocol

Top-level protocol for the NEUROSPINE study. Individual and group scale
thought / behavior prediction from neural + behavioral recordings.

## Phase 0: Instrument freeze (weeks 1 to 2)

- Freeze `instrument/specs/contract-v0.md`, the `Thought` tuple, and the
  gate ladder v0.
- Reference harness passes all synthetic-first tests.
- Extraction protocol (ADR-003) documented and adopted.
- Literature index at ~50 to 80 external anchors covering the seven
  provider components, the reliability gate, and the topological /
  physics framing.

## Phase 1: Individual-scale pipeline (weeks 3 to 8)

Data: Natural Scenes Dataset (NSD, 8 subjects, ~30 hours per subject of
7T fMRI on natural image viewing) and BOLD Moments Dataset (BMD, 10
subjects, 3T fMRI on natural video viewing). Rationale: high per-subject
data volume is what makes replicable per-subject decoders feasible; NSD
and BMD are the highest-per-subject-data public fMRI datasets currently
available.

Per subject, per session:

1. Preprocess with a fixed pipeline (fMRIPrep, HRF-deconvolved).
2. Fit each of the five decoders (perception, affect, decision, memory,
   reward) on session 1 data using leave-one-run-out CV.
3. Evaluate on session 2 data (held out).
4. Compute the Goltermann/Huth triad on the fitted decoder.
5. Report per-dimension test-retest correlation.

Extraction targets (per ADR-003) from portfolio into the decoders:

- `PerceptionDecoder`: engineering from tribe-neuroprint and
  memoryprint; external anchor MEIcoder (Sobotka et al.).
- `AffectDecoder`: engineering from affectprint (proposed) and
  behavioral-decoding; external anchors from
  `literature/SYNTHESIS_biomedical.md` affect section.
- `DecisionDecoder`: engineering from decision-phenotype AIM-DDM;
  external anchor Ratcliff (1978) DDM + recent extensions from lit
  scan.
- `MemoryDecoder`: engineering from memoryprint; external anchor
  hippocampal backward-shifted reward (Yaghoubi et al., Nature 2026).
- `RewardDecoder`: engineering from nacc-anticipation; external anchor
  same as `MemoryDecoder`.

Each extraction gets its external re-verification test per ADR-003
before it can raise any gate above `unscored`.

## Phase 2: Individual-scale replicability (weeks 9 to 12)

- For each subject in NSD and BMD, run the full A1 replicability test:
  session A vs session B correlation.
- Apply the Goltermann/Huth correction.
- Report per-dimension test-retest with 95 percent CI.
- Failed dimensions are either retired for that subject, or the subject
  is flagged as needing additional data.
- Aim 1 pass or fail is decided here.

## Phase 3: Group-scale transfer (weeks 13 to 20)

Data: HCP-YA (~1200 subjects, task-fMRI battery) as a wide but
per-subject-shallow supplement; DEAP (32 subjects, EEG + physio on
video-elicited affect) for the affect side; ds005479 (or updated MID
task dataset) for the reward side; NAcc benchmark task from
`portfolio/nacc-anticipation`.

Per dimension:

1. Train A1 pipeline on N subjects with full per-subject calibration.
2. Fine-tune on K < 10 minutes of a held-out subject's data using the
   RAVEN weak-to-strong protocol.
3. Predict on the held-out subject's remaining data.
4. Compare to A1 within-subject performance; compute degradation ratio.
5. Aim 2 pass or fail is decided per dimension.

## Phase 4: Specificity and Cognitive Dark Matter check (weeks 21 to 24)

- For each of the six Cognitive Dark Matter domains, run the G4
  specificity ablation: does a matched control that removes the
  in-scope dimension prediction also remove the apparent Cognitive
  Dark Matter prediction?
- If yes: rename the in-scope prediction to what the control also
  produces.
- If no: the in-scope prediction is orthogonal to the Cognitive Dark
  Matter domain, and the `unmeasured_domains` declaration stands.
- Aim 3 pass or fail is decided here.

## Phase 5: Reporting (weeks 25 to 28)

- Write up per-aim results.
- Every fMRI-grounded claim in the writeup carries its Goltermann/Huth
  numbers.
- Every prediction dimension carries its calibrated confidence
  distribution.
- Every failed aim carries the exact numbers and the recharacterized or
  retired prediction.
- All code, configs, and derived datasets released under AGPL-3.0.
- For any double-blind venue, ship the `anonymous.4open.science`
  mirror per anonymization doctrine.

## Decision points

- End of Phase 2: if A1 fails on more than three subjects, narrow scope
  to the two dimensions that survive and rewrite the paper.
- End of Phase 3: if A2 fails on four or more dimensions, publish as an
  "individual scale only" paper and open a separate roadmap for
  group-scale future work.
- End of Phase 4: if A3 reveals a Cognitive Dark Matter confound on the
  headline dimension, retract that dimension and re-run Phase 5 on the
  surviving four.
