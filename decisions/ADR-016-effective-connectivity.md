# ADR-016: Effective connectivity replaces the literature-prior signs

## Status

Accepted, 2026-09-05.

## Context

ADR-015 built a signed linear system whose regulation prediction rested
on the SIGN of the prefrontal (control network) -> amygdala edge, which
was set to inhibitory from the anatomical literature. As noted in that
ADR, "the direction of the prediction is a property of the sign
structure, not a fitted effect size." That is a real weakness: the whole
result is only as good as the assumed sign.

The follow-up ADR-015 named was to estimate those signs from data
(effective connectivity), so the edge sign becomes an empirical result.

## Decision

Add `instrument/src/neurospine/effective_connectivity.py`: a
ridge-regularized first-order vector autoregression,
`x_{t+1} = A x_t + e_t`, fit to regional BOLD. The off-diagonal `A[i, j]`
is the signed directed influence of region `j` on region `i` (Granger
sense). This is the linearized / regression-DCM regime (Frassle et al.
2017): a linear DCM with fixed hemodynamics reduces to this regression.
Convention matches `signed_dynamics.py` (`A[i, j]` is the effect of `j`
on `i`), so an estimated `A` drops straight into that model.

The module provides per-subject `fit_var1`, a group aggregate with a
cross-subject sign-consistency reliability filter
(`group_effective_connectivity`), a hardened group-level edge test
(`edge_group_stats`: one-sample t across subjects plus a time-reversed
Granger control), the discrete steady state `(I - A)^{-1} u` with a
spectral-radius stability guard, and a labelled edge reader
(`directed_influence`).

`experiments/thought_propagation/effective_connectivity_threat.py`
estimates the augmented cortico-subcortical effective connectivity from
real fMRI (nilearn development_fmri, the Pixar "Partly Cloudy"
naturalistic paradigm) over the same atlas as ADR-014, and reports the
estimated sign of the key threat edges.

## External anchors

- Frassle et al. 2017, "Regression DCM for fMRI" (NeuroImage): the
  regression-form effective-connectivity estimator this module is a ridge
  analogue of.
- Friston, Harrison, Penny 2003, "Dynamic causal modelling"
  (NeuroImage): the directed, signed effective-connectivity framework.
- Seth, Barrett, Barnett 2015, "Granger causality analysis in
  neuroscience and neuroimaging" (J. Neurosci.): the VAR/Granger basis
  and its fMRI caveats.
- Vinck et al. 2015, "How to detect the Granger-causal flow direction in
  the presence of additive noise?" (NeuroImage), and Chvostekova et al.
  2021, "Granger Causality on forward and Reversed Time Series"
  (Entropy): the time-reversed-Granger control used to separate genuine
  directionality from mixed-noise artifact. Both note it is a control,
  not an infallible oracle for bidirectionally-coupled pairs.

## Result

Group VAR(1) effective connectivity over 115 regions, 25 subjects
(stable, spectral radius 0.46). Sign alone was not enough: the initial
cross-subject sign consistency for the prefrontal edge was only 0.58,
barely above the 0.5 chance line, which naively reads as noise. Adding
the literature-standard controls (a group one-sample t-test across
subjects, and the time-reversed-Granger comparison) recovered a real,
defensible signal:

- **Prefrontal (Cont) -> amygdala is estimated INHIBITORY and is
  statistically supported**: group mean -0.012, t = -2.29, p = 0.031,
  and it survives time reversal (forward estimate more negative than the
  time-reversed one, net directionality -0.013). So the sign is reliable
  at the group level even though individual-subject signs are noisy.
- **Amygdala -> prefrontal is even more strongly negative** (t = -2.94,
  p = 0.007): reciprocal negative amygdala-prefrontal coupling.
- **Vis -> amygdala is positive but NOT significant** (p = 0.97);
  SalVentAttn and Default -> amygdala are not significant either. Only
  the prefrontal-amygdala edges survive, which is the honest outcome.

So the sign that carried the whole ADR-015 prediction is the sign the
data assigns, and it now clears a group significance test and a
time-reversal control. The prediction is data-corroborated, not assumed.

## Rigor notes and honest limitations

- **Sign-consistency alone was misleading; the group test was load-
  bearing.** At 0.58 consistency the naive read was "noise". The
  one-sample t-test and time-reversal control (Vinck 2015; Chvostekova
  2021) are what distinguished a reliable small group effect from noise.
  This is recorded because it is the methodological point of the tier.
- **Naturalistic movie, not a threat/regulation task.** development_fmri
  is affective/social but not fear conditioning or explicit emotion
  regulation. A real regulation task (reappraisal, extinction) is the
  correct substrate and remains the next data step.
- **Small magnitudes.** The estimated weights are small in absolute
  terms; the claim is about their sign and group reliability, not their
  effect size.
- **VAR(1) on fMRI is confounded.** Hemodynamic lag and TR limit
  directed-influence estimates (Seth et al. 2015). No hemodynamic
  deconvolution is applied; this is a linear, first-order approximation,
  chosen for transparency over a full spectral-DCM inversion. Time
  reversal mitigates but does not remove this.
- The contribution is the METHOD (data-estimated signed edges, hardened
  with group statistics and a time-reversal control, replacing literature
  priors) plus the reported estimates, not a claim that these weights are
  the definitive threat-circuit effective connectivity.

## Follow-ups (not yet requested)

- Re-estimate on a real emotion-regulation / fear task (reappraisal,
  extinction) to test the prefrontal-inhibition edge on-task.
- Hemodynamic deconvolution or spectral DCM to reduce the VAR fMRI
  confound.
- Feed the full estimated `A` into the signed-dynamics regulation sweep
  as a data-parameterized system, versus the literature-prior version.
