# ADR-011: Council review of the Markov claim, and the discretization confound

## Status

Accepted, 2026-09-04.

## Context

The user requested a council review (the twelve-seat adversarial gate
ladder) of NEUROSPINE's mathematical robustness, with the standing
assumption that there was an error somewhere. There was, and it was in
the empirical inference, not the primitives.

## Verdict

MAJOR REVISION. The AIRM, topology, and Markov-invariant PRIMITIVES
passed Gate T (theoretical soundness): they were re-verified against
analytic identities and known-homology spaces this same session. The
EMPIRICAL claim failed Gate 4 (confound), Gate 6 (calibration), and
Gate 8 (measurement validity).

## The error

The claim "EEG covariance trajectories are genuinely not first-order
Markov, which rules out statistical power" was confounded and
overclaimed.

A function of a Markov process is generically not Markov (lumpability
requires special conditions on the partition). Discretizing a
continuous SPD trajectory into k prototype states is exactly such a
function. The pipeline never controlled for this.

The decisive control (`markov_confound_control.py`): an AIRM
autoregression, first-order Markov by construction, run through the
identical discretization + Chapman-Kolmogorov + implied-timescale
pipeline, produces the SAME signature the EEG showed:

| k | obs/param | CK TV | CK pass | plateau |
| --- | --- | --- | --- | --- |
| 2 | 62 | 0.073 | yes | no |
| 3 | 20.7 | 0.215 | no | no |
| 4 | 10.3 | 0.223 | no | no |
| 6 | 4.1 | 0.280 | no | no |

Consequences established:

1. The implied-timescale plateau detector is NON-DIAGNOSTIC. It fires
   zero plateaus even on genuinely Markov data, because for
   fast-mixing chains the subdominant eigenvalue is near zero and the
   implied timescale `-lag / log|lambda_2|` is noise-dominated below
   the lag spacing. "0/40 plateaus" is evidence of nothing.
2. The k >= 3 CK failures are CONFOUNDED. The known-Markov control
   fails identically at k >= 3.
3. The only non-confounded test is k = 2 against a construction-
   matched Markov null. Against that null (CK TV 95th percentile
   0.247, 25 realizations), 3 of 8 EEG subjects exceed it
   (seed-averaged over 5 discretizations). The other 5 are
   indistinguishable from a first-order Markov process.

## What survives

Claim A, "EEG covariance trajectories carry temporal structure beyond
marginal occupancy", is UNAFFECTED. The shuffle null permutes the
state sequence, destroying temporal order while preserving marginal
occupancy exactly, so its rejection (z up to -35, sign concordance
p = 0.021) validly demonstrates temporal dependence exists. The
confound attacks only the stronger "not first-order Markov" claim,
not the existence of structure.

## Corrected claim

The discretized EEG state sequence deviates from a first-order Markov
process for a MINORITY of subjects (3 of 8), at k = 2 only, against a
construction-matched Markov null. The earlier "not first-order Markov
at any resolution, rules out power" is withdrawn.

## Decision

1. Ship `markov_confound_control.py` as a required control; no Markov
   claim is admissible without it.
2. Restrict the Markov-deviation claim to the k = 2 vs Markov-null
   test, seed-averaged, reported as a subject count.
3. Correct ADR-009, README, study/ANALYSIS_PLAN.md, and the
   experiment README. Done in the same commit as this ADR.
4. Add a standing analysis-plan rule: any Markov-structure test on a
   discretized continuous process must be run against a
   construction-matched Markov null, never a fixed threshold.

## Process lesson

The code already hedged correctly (ADR-009 Tier1/Tier2 split, the
state-count sweep reported "MIXED" not "mis-specification"). The
overclaim entered at the PROSE level: the commit message and the
user-facing summary said "rules out power / genuinely not Markov at
any resolution", contradicting the code's own hedge. The lesson: the
narrative layer needs the same gate as the artifact layer. A control
that would have caught this (the known-Markov null) is cheap and was
not run until the review forced it.

## Follow-ups

- ADR-012 (queued): hidden Markov model. A latent chain can be Markov
  even when the observed prototype sequence is not, which is the
  standard resolution in the MEG/EEG brain-state literature and the
  natural next model given this result.
- Complete the interrupted literature sweep (Markov state models,
  transition-path theory, EEG microstates/HMM, diffusion maps).
