# First scoring pass: 2026-09-03

All 18 NEUROSPINE portfolio projects scored against `gates/gate-ladder-v0.md` for the
first time. Every `portfolio/<slug>/evaluation.md` is updated with `Last scored:
2026-09-03` and a `Next re-score due:` of 2026-09-17 for projects with real evidence, or
2026-09-10 for projects still fully or mostly unscored. This report is the cross-cutting
summary; per-project detail and citations live in each `evaluation.md`.

## Portfolio table

| Project | Overall state | Headline gate gap | Proposed next action |
| --- | --- | --- | --- |
| tribe-neuroprint | red | G4/G5/G12 fail: Paper 1's core claim is retracted for an uncontrolled stimulus-length confound. | Re-derive the manipulation signature with length as a covariate, or retire the claim via ADR-004. |
| ism-v1 | yellow | G1: no real (non-mock) run exists yet; T1 is NaN on the mock target. | Run `modal run modal_app.py --corpus 8 --p0-only` to de-risk TRIBE-adapter timing before a full run. |
| anesthesia-bridge | green | G-fMRI.2: per-participant sign-concordance binomial not explicitly computed, blocking G7/G8/G12 upgrades. | Compute and report the binomial test for Pillar A LZc across the 26 subjects. |
| memoryprint | yellow | G1/G8: apparatus validated on simulator only; no real data pulled yet. | Wire the BOLD Moments adapter (no agreement gate) and run H1+H2 for a first real result. |
| behavioral-decoding | yellow | G1/G4: strong infrastructure, but no headline dissociation number has been reported yet. | Run a real brain-only/behavior-only/combined comparison on NARPS or DEAP and report it. |
| decision-phenotype | green | G-fMRI.2: sign-concordance binomial not formalized for the NAcc/insula loss channel at n=40. | Compute the binomial test; it is the single missing leg of an otherwise strong result. |
| jspace-loyalty | yellow | G8 fail: second-model replication attempted (Qwen2.5-1.5B) and abandoned on hardware. | Replicate on a smaller/more efficient second model to actually clear G8. |
| mats-jlens | yellow | G6 partial/null: confound-controlled causal effect (C3) is inconclusive (CI includes 0). | Add more low-linearity-similarity items the model can solve to make C3 conclusive. |
| cultist | yellow | G8 fail: apparatus validated on synthetic ground truth only; real corpus not yet run. | Make the described "2-line change" to a real public corpus loader + learned encoder. |
| wiring-not-weights | green | G-fMRI.3 honest fail: reconstruction claim null at N=8 (underpowered, not disconfirmed). | Obtain a many-subject stimulus-evoked reconstruction dataset; this is the program's stated gap. |
| cortex-of-anyone | green | G6 honest fail: the Hopf dynamical-twin mechanism model does not reproduce the validated consciousness signature. | Replace the Hopf twin with an anesthesia-parameterized neural-mass model, or open a retirement ADR. |
| nacc-anticipation | yellow | External-home record is stale (`aaygan29/NAcc_benchmark` does not resolve); active work is a PR on a fork. | Point `ORGANIZATION.md` at the fork/PR and track PR #721 to merge. |
| bio-toolkit | yellow | Scope: does not map onto any NEUROSPINE tuple field; contents not inspected this pass. | Inspect subproject contents, and settle whether it belongs in this portfolio at all. |
| warden | yellow | G7/G1: pilot real-data results explicitly excluded from the citable-evidence whitelist. | Take H1 (best literature-grounded head) to a validated real-data result end to end. |
| affectprint | red | No code exists; proposal only. | Resolve overlap with `cortex-of-anyone`'s G3 result before building a parallel apparatus. |
| spikeprint | yellow | G8 fail: choices13k dataset deferred for lack of a license; only NARPS run. | Run the already-built CSI-via-TRIBE pipeline once A100 compute is available. |
| globalsouthai | yellow | G11 unverified: double-blind anonymization mirror not independently confirmed this pass. | Confirm the `anonymous.4open.science` mirror before the Sep 5 2026 AoE deadline. |
| pereverzev-neuro-extension | red | No code exists; discussed only. | Write a one-page plan naming the target modality and dataset before any code. |

Counts: **4 green** (anesthesia-bridge, decision-phenotype, wiring-not-weights,
cortex-of-anyone), **11 yellow**, **3 red** (tribe-neuroprint, affectprint,
pereverzev-neuro-extension).

## Three highest-leverage next actions across the portfolio

1. **Compute the missing G-fMRI.2 sign-concordance binomial for `anesthesia-bridge` and
   `decision-phenotype`.** Both projects already have the raw per-subject directional
   data needed; this is a cheap statistical add-on, not new data collection, and it is
   the single gate blocking a G7/G8/G12 upgrade on the portfolio's two strongest
   fMRI-grounded claims (cortex-of-anyone already clears this triad and is the reference
   example of what "done" looks like).
2. **Get a second-model replication for `jspace-loyalty`.** The paper pipeline is
   active (multi-venue plan A-D) and the only reason G8 fails is an abandoned hardware
   attempt, not a real negative result. This is the fastest path to strengthening a
   project that already has a completed, real-model headline study.
3. **Unblock `memoryprint`'s BOLD Moments path.** Of the three data-stalled projects
   (memoryprint, behavioral-decoding, cultist), memoryprint has the fastest unblock (no
   agreement gate, data already fetched for the stimulus side) and the most complete
   preregistration already in place, making it the best next real-data win.

## Retirement / inversion ADR candidates

- `tribe-neuroprint`: Paper 1's zero-shot dlPFC/PBI manipulation-detection claim is
  explicitly retracted in the memory itself for an uncontrolled stimulus-length
  confound. Proposed: `decisions/ADR-004-retire-tribe-neuroprint-paper1-claim.md`
  (scope: retire the Paper 1 claim and the API's current calibration only; the Corpus
  A/B/C pipeline design and Paper 2 are unaffected).
- `cortex-of-anyone`: the Hopf/Stuart-Landau dynamical-twin submodule fails to
  reproduce the project's own validated consciousness signature, moving in the wrong
  direction under its own arousal knob. Proposed:
  `decisions/ADR-005-retire-cortex-of-anyone-hopf-dynamical-twin.md` (scope: this
  submodule only; the individuation/G3 result is real and unaffected).

No other project meets the ladder's retirement rule (same gate failing twice, more than
14 days apart, no viable fix in the tree) on this first pass, since this is the first
real scoring: the rule cannot yet be triggered by definition. These two are flagged
because the *memory itself* already documents the failure as settled, not because the
gate ladder's two-strikes rule has fired.

## Gates that look consistently under-defined (v1 ladder candidates)

- **G2 (seed variance, n>=5)** does not fit cleanly onto deterministic analyses of fixed
  real datasets, which is most of this portfolio. Several strong projects (NARPS-based
  work, ABIDE fingerprinting) have real robustness evidence (cross-validation folds,
  cross-dataset replication, multi-model panels) that is not literally "5 seeds of a
  stochastic point estimate." The ladder should either define an equivalent
  resampling-axis requirement for non-stochastic pipelines or explicitly mark G2 `n/a`
  for that class of claim.
- **G-fMRI.2 (sign-concordance binomial)** is the gate most often left unscored even
  when the underlying per-subject directional data already exists (anesthesia-bridge,
  decision-phenotype, wiring-not-weights all have the ingredients but not the named
  statistic). The ladder should require this as a specific named output artifact
  wherever per-subject directions are already computed, not leave it implicit.
- **Naming collision**: the ladder's own "WARDEN honesty gate" addendum (H1-H3) shares
  a name with the portfolio project `warden`, which is a different, specific
  cognitive-security instrument. This caused real ambiguity while scoring `warden`'s
  evaluation. Recommend renaming the addendum (e.g. "honesty addendum") in a v1 ladder.
- **No whole-project scope gate.** `bio-toolkit` scores mostly `n/a`/unscored on every
  empirical gate not because it fails them but because it is biology infrastructure that
  does not map onto any of NEUROSPINE's seven tuple fields at all. The ladder has no way
  to flag "this project is out of instrument scope" as a single decision; it currently
  forces gate-by-gate `n/a` scoring that obscures the real question.
- **G10's "under an hour" threshold** is rarely reported as an actual wall-clock number.
  Most projects report "tests pass" or "CI green," which is necessary but not the same
  claim; only `decision-phenotype` (`reproduce.py`, ~100s) and `cortex-of-anyone`
  (`validate_all.py`, one command) give a concrete, checkable reproduce path.
