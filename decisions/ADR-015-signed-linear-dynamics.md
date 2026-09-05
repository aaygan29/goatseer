# ADR-015: Signed linear dynamics for inhibitory regulation

## Status

Accepted, 2026-09-05.

## Context

ADR-014's threat circuit ran on a row-stochastic random walk. Its
ablation 2 was left as an explicit, documented limitation: adding a
prefrontal (Cont) -> amygdala edge INCREASED autonomic and endocrine
drive, the opposite of real top-down downregulation.

The cause is structural, not a tuning problem. A row-stochastic matrix
conserves probability: every edge can only MOVE activation mass, never
remove it. Inhibition is subtraction. No probability-flow random walk,
at any weighting, can express it. Representing prefrontal regulation of a
threat response therefore requires a different dynamical regime.

## Decision

Add `instrument/src/neurospine/signed_dynamics.py`: a continuous-time
leaky linear rate model (a linear dynamical system) that lives beside the
random-walk `dynamics.py` rather than replacing it.

    dx/dt = (W - gamma * I) x + B u

- `W` carries SIGNED weights: excitatory edges positive, inhibitory
  edges (prefrontal -> amygdala) negative. `W[i, j]` is the effect of
  region `j` on region `i`.
- `gamma` is a scalar leak that guarantees stability. The dynamics
  matrix is `A = W - gamma I`, stable iff `gamma > max(Re(eig(W)))`.
- For a sustained stimulus the system relaxes to a steady state
  `x_ss = (gamma I - W)^{-1} B u`, the equilibrium activation across
  every region.
- Effectors (autonomic, endocrine, peripheral motor) are LINEAR READOUTS
  of the steady state, not absorbing nodes. An effector's drive is a
  weighted sum of the neural activation it receives, which is the honest
  representation for a linear system and imposes no
  probability-conservation constraint on the effector.

The module also carries the network-control-theory machinery on the same
matrix: the controllability Gramian (via the continuous Lyapunov
equation) and the minimum control energy to steer the system to a target
state, so the "can prefrontal cortex regulate the amygdala, and at what
cost" question is answerable quantitatively.

## External anchors

- Gu et al. 2015, "Controllability of structural brain networks"
  (Nat. Commun.): the linear-system-on-a-brain-graph formulation with
  the controllability Gramian and minimum control energy. Permits and
  uses signed weights.
- Galan 2008, "On how network architecture determines the dominant
  patterns of spontaneous neural activity" (PLoS ONE): a linear
  stochastic rate model of resting-state dynamics on the connectome.

## Result

`experiments/thought_propagation/signed_threat_response.py`, on the same
augmented cortico-subcortical connectome as ADR-014 (100 cortical + 15
subcortical regions), with the prefrontal -> amygdala edge now inhibitory:

Increasing prefrontal regulatory gain monotonically LOWERS amygdala
steady-state activation and every effector readout (with the leak held
fixed across the sweep):

    inh gain   amygdala  Autonomic  Endocrine   MotorOut
        0.0     3.077      6.744      6.154      6.562
        1.0     1.490      3.280      2.980      4.046
        2.0     0.855      1.893      1.710      3.038

This is ADR-014's ablation 2 with the sign corrected: inhibition now
SUBTRACTS, so prefrontal regulation dampens the threat response rather
than amplifying it. The limitation is resolved into a testable,
correct-direction prediction.

## Rigor notes

- **Leak-drift confound, controlled.** `build_signed_system` picks
  `gamma` from `max(Re(eig(W)))` by default, which drifts as the
  inhibitory weight changes and would confound a sweep. An early run with
  the drifting leak showed MotorOutput moving the wrong way. Holding
  `gamma` fixed at the baseline value across the sweep (a `gamma`
  override was added for exactly this) removes the confound, and all four
  readouts then decrease monotonically. The wrong-direction MotorOutput
  was the artifact; the corrected run is clean.
- **Stability is enforced, not assumed.** `steady_state` and the Gramian
  raise if `A` is not Hurwitz, and `build_signed_system` raises if a
  supplied `gamma` fails to stabilize the system.
- **Control cost is expensive and that is the point.** The minimum
  control energy for the cortical control set to halve the amygdala is
  very large, consistent with the network-control-theory finding that
  deep, weakly-coupled nodes are costly to control from cortex. Reported
  as a relative magnitude, not to its exact digits.

## What this does NOT claim

- The signed weights are anatomical-literature priors (LeDoux
  dual-route; prefrontal downregulation), not effective-connectivity
  estimates fit to a threat-task dataset. The direction of the
  prediction is a property of the sign structure, not a fitted effect
  size.
- A linear model has no threshold, saturation, or oscillation. It is the
  minimal dynamical regime that can express inhibition, chosen for
  exactly that reason, not a claim that threat dynamics are linear.

## Follow-ups (not yet requested)

- Effective-connectivity priors (DCM / Granger) from a real threat-task
  dataset to replace the literature weights with fitted signed edges.
- A bilinear / threshold-nonlinear extension if saturation or
  state-dependent gain becomes load-bearing.
