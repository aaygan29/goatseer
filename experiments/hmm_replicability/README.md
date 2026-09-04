# hmm_replicability

> SETTLED BATTLE (guardrail, not a finding). Cross-session subject
> individuation via neural pattern is a KNOWN, retracted/null battle in
> this program: BOLD5000 fingerprint overclaim (RETRACTED, synthetic
> subjects were seeds), "encoding is not identity" (digital-brain,
> individuation stays open as gap G1), and "encoder as moat is dead".
> See the neuroai-failure-archaeology skill. This experiment was run
> before consulting that chronicle; it re-derived the settled result
> (identity is carried by the MARGINAL covariance, not the dynamics).
> It is kept ONLY as a reusable specificity-ablation harness and as a
> guardrail that confirms the settled battle. It is not a NEUROSPINE
> contribution. Do not extend it (e.g. more subjects to "sharpen" the
> individuation gap): that gap is open program-wide and is not closed
> by fingerprinting.


A1 replicability test (ADR-012): do a subject's HMM dynamics replicate
across sessions BEYOND their marginal covariance?

## Why the ablation is the whole point

"I can identify a subject cross-session" is nearly vacuous. Anatomy,
skull geometry, and electrode placement make each subject's MARGINAL
covariance distinctive, so any method fingerprints subjects above chance
without saying anything about dynamics. The user's own prior work
includes a retracted fingerprinting overclaim of exactly this kind
(a synthetic-subject artifact archived as DO_NOT_CITE). So the static
baseline is not optional: it is the specificity ablation that decides
whether the dynamics claim is real.

The real A1 claim: a subject's LATENT-STATE DYNAMICS identify them
better than their marginal covariance alone.

## Method

- Two separate sessions per subject: imagined-fist runs 4 (A) and 8 (B).
- Per-epoch SPD covariance, embedded to the AIRM tangent space at a
  SINGLE global reference (Frechet mean of all session-A covariances),
  so scores are comparable across subjects.
- Per subject, fit on session A: (a) a K-state Gaussian HMM, and (b) a
  static single Gaussian (marginal only, no dynamics).
- Score every subject's session B under every model. Identification
  accuracy = fraction of subjects whose own model best explains their
  session B. Chance = 1/N.
- The dynamics claim holds only if HMM identification EXCEEDS static.

## Result (2026-09-04, n=8)

| method | cross-session ID accuracy | binomial p vs chance |
| --- | --- | --- |
| static Gaussian (marginal only) | 5/8 = 0.625 | 0.0012 |
| HMM (dynamics + geometry) | 5/8 = 0.625 | 0.0012 |

**NEGATIVE for the dynamics claim.** Subjects are identifiable
cross-session well above chance, but the HMM does no better than the
static marginal. The cross-session identity is carried by static
covariance geometry (anatomy, electrode placement), not by the
dynamics. The specificity ablation removes the effect. A1, as the claim
"subject dynamics replicate as an identifying signal," is NOT supported
at this N.

This does NOT contradict the within-session HMM result (`hmm_eeg/`,
8/8 subjects show latent structure beyond first-order). That was about
MODELING structure within a session. This is about IDENTIFYING subjects
by dynamics across sessions. The within-session structure is real; it
is simply not subject-specific enough to fingerprint beyond the
marginal. A plausible reason: motor-imagery state-switching statistics
are similar across people, so the HMM's identifying power collapses to
its emission means, which is essentially the marginal.

## Honest limits

n=8 makes the binomial coarse (each subject is 12.5 percent). The point
estimates are exactly equal (5/8 vs 5/8), so there is no evidence the
dynamics add identifying information; a larger cohort would be needed to
detect a small gap if one exists. The negative result is reported as a
negative result, not spun.

## Running

    python experiments/hmm_replicability/run.py --subjects 1 2 3 4 5 6 7 8 \
        --hmm-states 3
