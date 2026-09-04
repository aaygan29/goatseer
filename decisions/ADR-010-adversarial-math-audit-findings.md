# ADR-010: Adversarial math audit findings and fixes (2026-09-04)

## Status

Accepted, 2026-09-04.

## Context

A multi-agent adversarial audit was run against the four mathematical
modules (`manifold.py`, `topology.py`, `dynamics.py`,
`intervention.py`). Each module was reviewed by a hostile reviewer
with a domain lens (Riemannian geometry, computational topology,
Markov chain theory, differential geometry of the tangent space).
Every candidate finding was then handed to an independent verifier
whose instruction was to REFUTE it, with a numerical check, and to
default to "refuted" when it could not demonstrate a real failure.

Two findings survived adversarial verification. Both are recorded and
fixed here.

The audit was cut short by a session limit: 12 of 47 planned agents
completed, and the literature sweep did not run at all. The two
findings below are therefore a lower bound on what a complete audit
would surface, not a clean bill of health for the modules. A full
re-audit is queued.

## Finding 1 (critical): `safety_margin` measured clearance at one point

`score_intervention_channels` computed `safety_margin` as the AIRM
distance from the geodesic MIDPOINT `gamma(0.5)` to the declared
out-of-scope region. The intervention moves the subject along the
entire geodesic, so a clearance evaluated at one interior point
certifies nothing about the rest of the path.

The verifier's numerical counterexamples, on `P = random_spd(3, 15)`,
`Q = random_spd(3, 16)`, `d(P, Q) = 2.4499`:

- **Out-of-scope region set to `Q` itself** (the declared target is
  the forbidden state): reported margin `1.2249` (exactly `L/2`). The
  trajectory TERMINATES in the forbidden state. True margin is `0`.
- **Out-of-scope region placed exactly on the path** at
  `gamma(0.15)`: reported margin `0.8575`, a comfortable positive
  number. True minimum over 2001 sampled `t` was `0` to within
  `1e-12`. The instrument reported a healthy margin for the
  maximally unsafe intervention.
- **Generic third point**: reported `1.8816` at `t = 0.5`, but the
  true minimum was `1.8358` at `t = 0.666`. The midpoint is not the
  minimizer even in the benign case, so the old value was not even a
  consistent conservative estimate.

This is the one field in the module that is ethics-facing, which is
what makes a silent overestimate critical rather than cosmetic.

**Fix.** New `airm_geodesic_min_distance(P, Q, R, n_samples)` in
`manifold.py` returns `(min_distance, argmin_t)` by sampling the
geodesic uniformly. `safety_margin` now uses that minimum, and
`Intervention` gains a `closest_approach_t` field so the caller can
see WHERE the trajectory comes closest to the forbidden region.
Sampling density is the accuracy knob and is documented: the returned
value is an upper bound on the true minimum that tightens with
`n_samples`.

Six regression tests in `test_intervention.py` encode the verifier's
counterexamples directly, including the invariant the old code
violated: the minimum over the path can never exceed the distance at
the midpoint.

## Finding 2 (major): `grassmann_distance` docstring named the wrong metric

The docstring read "Geodesic (chordal) Grassmann distance". Those are
two different metrics on `Gr(k, n)`, not two names for one:

- Geodesic (arc-length), which the code computes:
  `sqrt(sum theta_i^2)`, bounded by `sqrt(k) * pi / 2`.
- Chordal (projection Frobenius): `sqrt(sum sin^2 theta_i)`, bounded
  by `sqrt(k)`, equal to the Euclidean distance between the
  orthogonal projectors.

The verifier established that this is load-bearing rather than
cosmetic:

- The ratio `d_geo / d_chord` ranged `1.083` to `1.480` over 1560
  pairs of random 3-planes in `R^8`, so they are not related by any
  fixed scale. They coincide only in the small-angle limit.
- On 40 random subspaces, the centered Gram matrix built from the
  geodesic distances had minimum eigenvalue `-1.3174`, i.e. it is
  indefinite and not of negative type. The chordal Gram had minimum
  eigenvalue `-7.8e-16`, PSD to machine precision.

So any consumer that trusted the word "chordal" to justify a PSD
kernel, a classical-MDS embedding, or the `sqrt(k)` bound would have
been silently wrong.

The verifier also noted the defect was latent rather than active: the
only in-repo consumers were two loose test assertions that pass under
either metric. That bears on severity, not on correctness.

**Fix.** Docstring corrected to name the arc-length distance
explicitly, cite Edelman, Arias, Smith (1998), state the bound, and
warn that it is not of negative type. New
`grassmann_chordal_distance` added for the cases that need a Hilbert
embedding. Four regression tests encode the distinction, including
the negative-type check that separates them.

## Consequences

- `Intervention` gains `closest_approach_t: float | None`. Existing
  callers are unaffected (it defaults to `None`).
- `score_intervention_channels` gains a `geodesic_samples: int = 201`
  parameter controlling the margin's accuracy.
- Any previously computed safety margin is invalid and must be
  recomputed. No such value has been reported anywhere, so there is
  nothing to retract.
- Test count rises from 124 to 143.

## Process lesson

Both findings were in code that had passing tests. The tests asserted
weaker properties than the docstrings claimed: `test_finite_when_out_of_scope_declared`
only checked that the margin was a finite non-negative number, and
the Grassmann tests only checked "zero for identical subspaces,
positive for distinct ones". Both pass under the buggy implementation.

The audit instruction that produced these findings included the line
"flag tests that assert something WEAKER than the docstring claims (a
test passing does not mean the math is right)". That instruction is
now part of the standing review protocol for any new math module.

## Follow-ups

- Re-run the remaining adversarial audit; 35 of 47 agents were cut
  by a session limit. The `topology.py` reduction has since been
  verified directly (see below), but the `dynamics.py` verifiers and
  the entire literature sweep still did not run.
- The `topology.py` H1 boundary-matrix reduction was flagged by the
  reviewer as "easy to get subtly wrong" and its verifiers never ran
  during the audit. RESOLVED 2026-09-04 by direct stress-testing
  against spaces with analytically-known first Betti numbers (single
  circle with finite-death pairing at full scale, figure-eight with
  b1 = 2, two disjoint circles with b1 = 2, filled disk with no
  dominant loop). The reduction is correct: an apparent
  infinite-persistence class turned out to be a scale-cutoff artifact
  (a loop needing edges of length L reads as essential at any
  max_scale below L, which is the correct convention), not a pairing
  error. Four hard-case regression tests added to
  `test_topology.py`. The `topology.py` module is no longer
  unaudited.

Still outstanding:
