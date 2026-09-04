# NEUROSPINE Instrument

Not yet implemented. Every field in the per-decision contract must pass its
corresponding gate before landing on main.

## Assembly plan

The instrument will be built in seven sequential steps:

1. **Contract v0 frozen** (specs/contract-v0.md): tuple fields locked, gate dependencies
   declared.
2. **Honesty and calibration tests**: pytest suite with synthetic ground truth and seed
   sweeps (n>=5).
3. **Answer and confidence**: dummy model stub that outputs a decision tuple.
4. **Loyalty vector**: encode model operating characteristics from portfolio projects.
5. **Sparse circuit id**: map decision to a minimal causal circuit in the supporting model.
6. **Neural alignment score**: rate neural congruence to the decision (requires real fMRI or
   simulator).
7. **Full contract on held-out subject and model**: produce real tuple with all seven fields,
   scored on new subject and a held-out model.

Each step must pass its gate ladder (gates/gate-ladder-v0.md) before the next begins.
