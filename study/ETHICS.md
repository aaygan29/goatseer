# Ethics

NEUROSPINE uses only public, consented data. There is no primary data
collection in the study as designed. This document names the ethical
considerations that persist even so.

## Consent and data governance

- Every dataset (NSD, BMD, HCP-YA, DEAP, NATVIEW, ds005479, ds003171)
  was collected under an IRB-approved protocol with informed consent
  for the specific research use.
- The NEUROSPINE research use is compatible with each dataset's
  data-use agreement. Compatibility is verified per dataset in
  `experiments/<name>/README.md` before any download.
- No PHI is present in the repository. Any derived artifact that
  could identify a subject (e.g. per-subject decoder weights) is
  stored under a subject id that maps back only through the original
  dataset's key.

## Red-team notes

The instrument is a thought-prediction system. Even under the aim
restriction (five in-scope cognitive-state dimensions plus a declared
Cognitive Dark Matter frontier), the following risks warrant
documentation:

1. **Dual use.** A subject-conditional decoder that reads perceived
   stimulus or predicted decision from neural recordings is
   dual-use-adjacent. NEUROSPINE mitigates by: requiring per-subject
   calibration (no zero-shot readout), gating every prediction behind
   the Goltermann/Huth triad, defaulting the abstention flag to True
   under reliability failure, and licensing under AGPL-3.0 (any
   network-hosted derivative must publish source).
2. **Confounding as manipulation.** Any decoder that appears to
   predict a Cognitive Dark Matter domain is either recharacterized
   or retracted per Aim 3's ablation rule. This rules out repackaging
   a low-level pattern as a "reads intent" claim.
3. **Individual-scale replicability failures.** A decoder that fails
   test-retest on a particular subject must be reported per that
   subject, not averaged into a group summary that hides the
   individual failure.

## Cognitive Dark Matter frontier

The instrument does not attempt to predict metacognition, cognitive
flexibility, lifelong learning, reasoning, social reasoning, or
emotional intelligence. This is a soft frontier, not a hard one.
Anyone extending the study to add a Cognitive Dark Matter domain must
open an ADR revising Aim 3 and add a fresh red-team pass for the new
domain.

## Publication

- Every failed aim carries the exact numbers as the primary result.
- File and figure captions never overstate the reliability of a
  prediction whose Goltermann/Huth triad passed at the minimum
  threshold; report the numbers.
- For any double-blind venue, ship the anonymous.4open.science mirror
  per anonymization doctrine.
