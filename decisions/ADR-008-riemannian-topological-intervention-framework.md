# ADR-008: NEUROSPINE as a Riemannian-topological cognitive-state cartography with intervention scoring

## Status

Accepted, 2026-09-04.

## Context

The prior ticks built a decoder and a study protocol. Aayush's
2026-09-04 correction:

> Make the actual product mathematically accurate and valid and
> complex enough that it will actually work for a broader analysis.
> What we want to do here is use Riemannian and topology and the
> broader computational skills we have to figure out what people are
> thinking and whether this can be altered in some way, for a specific
> purpose. As it stands, it feels like you've just made another
> behavioral prediction tool. It needs to be something new and unique
> that extends the scientific research field in some way.

The behavioral-prediction framing is a floor, not a ceiling. NEUROSPINE
needs to (a) live on the correct mathematical objects (Riemannian SPD
manifolds for covariance-derived neural state, learned latent
manifolds for high-dim activity, persistent-homology invariants for
trajectory topology), and (b) treat intervention as a first-class
output alongside prediction. Reading cognitive state without asking
"can this be altered, along what geodesic, via what channel, at what
cost, under what purpose constraint" is exactly the shortfall.

## Decision

Restructure the instrument as a **Riemannian-topological cognitive-state
cartography with purpose-constrained intervention scoring**. Three
concrete additions to the v0 contract, each mathematically grounded:

### 1. Neural state lives on a manifold, not in a flat vector

Every prediction is anchored to a point `M ∈ M` on a cognitive-state
manifold M. For NEUROSPINE v1, M is one of:

- **SPD manifold** (`Sym++(n)`): covariance or cross-spectral density
  matrices from EEG / MEG / iEEG; equipped with the affine-invariant
  Riemannian metric (AIRM), whose geodesic between P, Q is
  `gamma(t) = P^{1/2} (P^{-1/2} Q P^{-1/2})^t P^{1/2}` and whose
  distance is `||log(P^{-1/2} Q P^{-1/2})||_F`. Positive-definiteness
  is preserved by construction; classical Euclidean averaging is
  known to swell covariance eigenvalues, AIRM does not.
- **Grassmann manifold** (`Gr(k, n)`): k-dimensional linear subspaces
  of R^n, for representations that live in a subspace rather than a
  point (e.g. shared response models).
- **Learned latent manifold**: a low-dimensional manifold recovered
  by a variational autoencoder or a normalizing flow, with the
  pullback metric induced from the decoder Jacobian. Anchor: the
  Whitney/Takens embedding framework of O'Reilly-Shah + Selvitella
  2026 (pubmed-42599379) bounds the required intrinsic dimension.

Every provider in the harness takes `M ∈ M` as its first neural input
and returns a prediction that is equivariant under the manifold's
group action where meaningful (SPD: `P -> A P A^T` for invertible A;
Grassmann: rotations within the subspace).

### 2. Trajectory topology is a first-class invariant

Per-subject replicability is measured on the topological invariants
of the state trajectory, not only on per-timepoint predictions. For a
session's trajectory `M(t)`:

- Persistent homology of the point cloud gives a persistence diagram
  per Betti dimension. Two sessions from the same subject should
  have similar diagrams under bottleneck distance, even if
  per-timepoint predictions diverge.
- Betti curves over the filtration scale give a subject fingerprint.
- Reeb graphs of a scalar summary (e.g. affect valence) capture the
  qualitative-mode structure of the trajectory.

The topological signature is a per-subject invariant that lives above
per-timepoint reads and is the primary substrate of Aim 1
replicability. Anchors: arxiv-2210.09092 (dynamic TDA of brain
networks), arxiv-2512.08637 (persistent homology of neural spike
trains), pubmed-41570814 (Han + Bonner high-dim naturalistic
individual differences).

### 3. Intervention is a first-class output, gated by purpose

NEUROSPINE returns an `Intervention` alongside a `Thought` when the
caller declares a purpose. Given current state `P` and target state
`Q` on M:

- The geodesic `gamma(t)` from `P` to `Q` and its tangent
  `gamma'(0) ∈ T_P M` define the direction of alteration.
- For each intervention channel `c` (attention capture, stimulus
  choice, closed-loop biofeedback, TMS pulse, pharmacological), the
  channel's linearized pushforward `df_c` at `P` is a tangent vector.
  Rank channels by the affine-invariant inner product
  `<df_c, gamma'(0)>_P` normalized by `||df_c||_P`; the highest is
  the best-aligned channel.
- Predict the intervention effect via first-order expansion on M and
  a calibrated correction from held-out data.
- Compute a **safety margin**: the geodesic distance the intervention
  keeps between the trajectory and the subject's declared out-of-
  scope subregion (see the Cognitive Dark Matter frontier in `AIMS.md`
  Aim 3).

Purpose is a required argument. The caller declares a purpose class
(e.g. `reduce_anxiety_preserve_cognition`, `sustained_attention`,
`recall_specific_memory`). NEUROSPINE refuses to score interventions
on unlisted purposes; new purposes are added via ADR, never at call
time. This is the ethics primitive: no intervention without a named,
reviewed goal.

## What NEUROSPINE now contributes to the field

- **A principled instrument for cognitive-state cartography** on
  manifolds that respect the geometry of the data (SPD, Grassmann,
  learned), not on flat vectors that lose positive-definiteness or
  subspace identity.
- **Topological replicability**, not per-timepoint replicability, as
  the primary target for A1. Two sessions can look different pointwise
  and still be "the same" topologically.
- **Purpose-constrained intervention scoring** on the same manifold
  as the read. To our knowledge, no published tool ranks
  intervention channels by their alignment with a Riemannian
  geodesic from current to target cognitive state under a declared
  ethical purpose.
- **A retirement-first instrument**: the harness refuses to emit
  interventions on ungated channels or unlisted purposes, and the
  gate ladder + ADR flow institutionalizes that refusal.

This is the scientific contribution. Prior tickets built the
scaffolding. This ADR sets the direction the scaffolding is for.

## Consequences

- `contract.py` gets a `latent_state` field on `Thought` (the current
  neural state as a point on M, plus its manifold-family tag), and a
  new `Intervention` dataclass with `{target_state,
  channels_by_efficacy, geodesic_length, predicted_effect,
  safety_margin, purpose}`.
- New modules: `manifold.py` (SPD + Grassmann primitives, AIRM
  geodesic, log/exp maps, parallel transport), `topology.py`
  (Vietoris-Rips persistent homology, Betti curves, bottleneck
  distance), `intervention.py` (channel scoring, purpose registry).
- `Neurospine.predict(...)` now returns `Thought`; a new
  `Neurospine.propose_intervention(subject, current_state,
  target_state, purpose) -> Intervention` runs the intervention
  scorer.
- Dependencies: numpy + scipy for linear algebra. Documented in
  `pyproject.toml`. Pure-Python fallback for the topology of small
  point clouds; large-scale TDA calls out to `gudhi` or `ripser` when
  available.
- The reference `SubjectConditionalPerceptionDecoder` (perception.py
  from earlier tick 5) becomes a "flat linear baseline" for
  comparison; production decoders live on the manifold.
- Aims add A4: purpose-constrained intervention scoring, with its
  own preregistered success and failure criteria.
- Gate ladder v1 addendum extends with G14 (manifold correctness:
  every claim about geodesic distance or parallel transport survives
  a numerical identity check) and G15 (purpose gate: no intervention
  ships without a purpose declared in the ADR registry).

## Consequences NOT accepted

- We do not commit to a single manifold family for all data. SPD,
  Grassmann, and learned latent all remain first-class; the
  `latent_state.family` tag disambiguates.
- We do not attempt to score interventions on Cognitive Dark Matter
  domains. Aim 3's declaration stands: metacognition, cognitive
  flexibility, lifelong learning, reasoning, social reasoning,
  emotional intelligence are out of scope for intervention scoring
  as well as prediction.
- We do not build a real-time TMS/stimulation controller. NEUROSPINE
  scores the alignment and safety margin of a proposed intervention;
  execution is out of scope and requires separate IRB.

## External anchors (canonical, from `literature/`)

- pubmed-42618509 Miller, Brincat, Roy 2026: wave-mediated top-down
  control as the mesoscale substrate for the intervention channels.
- pubmed-42599379 O'Reilly-Shah + Selvitella 2026: embedding theorems
  bound the internal manifold dimension; prediction-separation gives
  the resolution below which distinct-future states must be separated
  in neural state space.
- pubmed-40502061 Schmutz et al. 2025: low-dim latents generating
  high-dim activity; Neural Cross-Encoder as a diagnostic for
  latent-vs-Euclidean tension.
- pubmed-38452763 Manley et al. 2024: dimensionality scales
  unboundedly with neuron count; latent claims are paired with the
  recording scale.
- pubmed-41570814 Han + Bonner 2026: naturalistic individual
  differences on a high-dim visual manifold.
- arxiv-2210.09092, arxiv-2512.08637, arxiv-2509.14634: TDA anchors
  for the topological invariants layer.
- pyRiemann convention for SPD manifold operations (Barachant et al.
  literature to be added).

## Follow-ups (this tick and next)

- Write `manifold.py`, `topology.py`, `intervention.py` and their
  verification tests. This tick.
- Extend `contract.py` with `latent_state` and `Intervention`. This
  tick.
- Add Aim 4 to `study/AIMS.md` and a Riemannian-topological methods
  section to `study/METHODS.md`. This tick.
- Add G14 and G15 to `gates/gate-ladder-v1-addendum.md`. This tick.
- Next tick: pubmed round-4 for the intervention-neuroscience side
  (targeted state control, closed-loop biofeedback replicability),
  and a purpose registry as its own ADR (ADR-009).
