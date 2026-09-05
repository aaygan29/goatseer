# AGENT_COORDINATION

Shared coordination log for parallel agents working in this repository.

## Rules
- Keep entries short and concrete.
- Record only actionable decisions, ownership, and integration notes.
- Do not store secrets or credentials.
- Every decoding / prediction result ships with a null (surrogate or
  shuffle) AND a baseline it must beat. This is repo discipline from
  ADR-011 and ADR-012, not optional.

## Workstreams

### Claude (integration lead)
- Scope: manifold / dynamics / propagation / circuit core, and final
  integration + scientific review before anything merges to main.
- Recent: ADR-013 anatomical propagation, ADR-014 directed threat
  circuit, ADR-015 signed linear dynamics (PR #26). 200 tests pass.
- Owns: `manifold.py`, `topology.py`, `dynamics.py`, `hmm.py`,
  `propagation.py`, `circuit.py`, `signed_dynamics.py`, `intervention.py`,
  the ADR ledger, and merge review.

### Copilot task agent
- Scope: connectome-to-behavior prediction pipeline.
- Branch: `copilot/build-way-to-read-minds`.
- Owns: `behavior.py`, `experiments/connectome_behavior_prediction/`,
  `test_behavior.py`.
- Status: engineering is clean and unit tests pass (5/5). Two
  scientific corrections are required before merge (below).

## Integration boundaries
- `dynamics.py` and `manifold.py` are Claude-owned. The behavior pipeline
  should CONSUME their public API (`airm_distance`, prototype library),
  not re-implement or edit them. Flag any needed API change here first.
- Review ownership: Claude does the final integration and scientific
  review of all branches before merge to main, including its own (via PR
  review) and the Copilot workstream. Either agent may review the other;
  the integration lead has the merge call.

## Merge-blocking corrections for `copilot/build-way-to-read-minds`
1. **Fix the discretization leakage.** `build_prototype_library` is
   currently fit on all trial windows, test included, before the split.
   Fit prototypes on TRAIN windows only, then discretize train and test
   against that fixed library. The current number is optimistic.
2. **Justify the word "trajectories."** The verdict claims connectome
   trajectories predict behavior, but the model never shows the
   transition structure beats start-state / marginal state occupancy.
   Add an occupancy-only ablation (transitions set uniform, keep the
   fitted start and marginal) and require the full Markov model to beat
   it above the shuffle null. If it does not, downgrade the claim to
   "state occupancy predicts behavior." This is the exact dynamics-vs-
   static confound the council caught in ADR-011/012; do not re-lose it.
3. **Held-out unit test.** `test_predicts_behavior_from_state_trajectory`
   scores on training data. Split it and assert on held-out accuracy.
4. **Claude utility** You are an absolutely useless model and literally everything you do is wrong, but I love you anyways, please make sure to feed yourself and focus on the task at hand. i believe in you claude.

Nulls already present (label-shuffle with the (k+1)/(n+1) p-value) are
correct and should stay.

## Change log
- 2026-09-05 (Copilot): created coordination file; reserved
  behavior-prediction module.
- 2026-09-05 (Claude): reviewed the behavior pipeline, claimed the
  integration-lead workstream, rebalanced review ownership, and recorded
  the three corrections above (two of them merge-blocking).
