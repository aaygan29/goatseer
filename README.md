# NEUROSPINE

**A mathematical instrument for tracking a thought as it moves through the brain, grounded on a real connectome.**

NEUROSPINE represents cognition as geometry and probability: a cognitive
state is a point on a curved manifold, a thought is a path across it, and a
stimulus-to-behavior response is a probability flow over real brain regions.
Every claim is tied to published external work and gated behind a test.

Owner: Aayush Gandhi (`aaygan29`). License: see `LICENSE`.

---

## 1. What it does, in one minute

Given neural recordings (EEG covariance, fMRI regional time series), the
instrument answers three kinds of question with the same mathematics:

| Question | Layer | Where |
|---|---|---|
| Where does a cognitive state sit, and how do two states differ? | **Cartography** (Riemannian geometry on the SPD manifold) | `manifold.py`, `topology.py` |
| Where does a thought travel, how long does it dwell, which basin does it commit to? | **Trajectory** (Markov dynamics, HMM) | `dynamics.py`, `hmm.py` |
| A scary stimulus hits the visual field: what is the region-by-region cascade to a behavioral reaction, and can prefrontal cortex regulate it? | **Propagation** (directed circuits on a real connectome) | `propagation.py`, `circuit.py`, `signed_dynamics.py`, `effective_connectivity.py` |

The through-line the project is actually chasing: *stimulus -> regional
processing chain -> behavior*, written as a probability structure on the
connectome, with the parts imaging cannot see (autonomic, endocrine, motor
output) represented explicitly rather than faked.

---

## 2. How it works, at a glance

```
recordings ──► covariance / regional signals
                   │
   (Cartography)   ▼   AIRM geodesics, log/exp maps, Frechet mean, persistent homology
             point on a manifold  +  topological signature
                   │
   (Trajectory)    ▼   discretize to states, estimate transition matrix
             stationary dist · MFPT · committor · PCCA · entropy rate · HMM
                   │
   (Propagation)   ▼   map states/regions onto a real connectome (Schaefer-100 + Harvard-Oxford)
             directed cascade  →  signed linear dynamics  →  effective connectivity from real BOLD
                   │
                   ▼
             stimulus → region chain → behavior, with an explicit observability boundary
```

Each layer is a small, separately-testable module. Nothing ships as a claim
until its identity tests pass and its result clears a null or a baseline.

---

## 3. Repo map (where to look)

| Path | What lives there |
|---|---|
| `instrument/src/neurospine/` | The package. One module per idea (see the module map below). |
| `instrument/tests/verification/` | One test file per module. Every test checks a math identity or an analytically-known value. |
| `experiments/` | Runnable studies on real public data, one folder each, with their own READMEs and results. Start here to see what the instrument *does*. |
| `decisions/` | ADRs 000-016. The decision trail: why each tier exists, what it fixed, what it deliberately does not claim. Read these to understand *why* the code looks the way it does. |
| `literature/` | Per-paper notes, `references.bib`, and `SYNTHESIS_*.md` (the external anchors, organized into load-bearing pillars). |
| `study/` | The research-study framing: aims, methods, analysis plan, preregistration, ethics. |
| `gates/` | The versioned gate ladder a claim must climb before it counts. |
| `portfolio/`, `reports/` | Per-project scoring dossiers and weekly scorecards. |

### Module map (`instrument/src/neurospine/`)

| Module | Role | ADR |
|---|---|---|
| `manifold.py` | AIRM geometry on SPD covariance matrices; Grassmann; tangent embeddings | 008 |
| `topology.py` | Vietoris-Rips persistent homology, Betti curves, bottleneck distance | 008 |
| `dynamics.py` | Markov transition analysis: stationary, MFPT, committor, PCCA, entropy rate, absorption | 009 |
| `hmm.py` | Gaussian hidden Markov model on the AIRM tangent embedding | 012 |
| `propagation.py` | Random-walk propagation on an atlas connectome | 013 |
| `circuit.py` | Directed circuits with un-imaged exogenous effectors | 014 |
| `signed_dynamics.py` | Signed linear rate model (inhibition, controllability, control energy) | 015 |
| `effective_connectivity.py` | Signed directed edges estimated from real BOLD (ridge VAR / regression-DCM) | 016 |
| `behavior.py` | Behavior-from-state-sequence prediction + occupancy ablation + reusable engine | - |
| `contract.py`, `harness.py`, `intervention.py` | The `Thought` output contract, the gated harness, purpose-constrained intervention scoring | 008 |

---

## 4. Quickstart

```bash
make install-dev        # install the package + dev deps
make test               # full verification suite (identity / known-value tests)
make lint
```

Run a real-data experiment (each folder has its own README and Makefile
target; public data auto-downloads via MNE / nilearn on first run):

```bash
python experiments/hmm_eeg/run.py                     # HMM vs VAR(1) on PhysioNet EEG
python experiments/thought_propagation/threat_response.py          # the threat cascade
python experiments/thought_propagation/signed_threat_response.py   # inhibitory regulation
python experiments/thought_propagation/effective_connectivity_threat.py  # edges from real fMRI
```

Bring your own data to the behavior pipeline (any modality, once discretized
into integer state sequences):

```python
from neurospine.behavior import analyze_state_sequences
result = analyze_state_sequences(sequences, labels, subject_ids, n_states=6)
```

---

## 5. What has actually been shown (honest results)

The instrument's discipline is that a negative result is reported as a
negative result. Highlights, each reproducible under `experiments/`:

- **Latent state structure in EEG (positive).** A Gaussian HMM beats VAR(1)
  on held-out EEG in **8/8 subjects** beyond a VAR(1) surrogate null
  (p=0.00 each). Confound-controlled. `experiments/hmm_eeg/`, ADR-012.
- **Cross-session identity is anatomy, not dynamics (disciplined negative).**
  Subjects are identifiable across sessions, but the dynamics do no better
  than the static marginal covariance. A specificity ablation caught the
  fingerprinting overclaim before it shipped. `experiments/hmm_replicability/`.
- **The threat cascade + observability boundary.** A visual threat routed
  through a directed cortico-subcortical circuit terminates in un-imaged
  effectors (motor 0.53, autonomic 0.25, endocrine 0.23): the entire
  terminal readout is in systems fMRI never sees. ADR-014.
- **Inhibitory regulation, as a testable prediction.** A signed linear model
  makes prefrontal regulation *lower* amygdala and effector drive
  monotonically, resolving a limitation of the excitatory-only walk. ADR-015.
- **The regulation sign, corroborated by real data.** Ridge-VAR effective
  connectivity on real fMRI estimates prefrontal -> amygdala as inhibitory,
  group-significant (t=-2.29, p=0.031), surviving a time-reversed-Granger
  control. The assumption became a measurement. ADR-016.
- **Behavior from state trajectories (honest cross-subject negative).** With
  leakage removed (subject-disjoint split) and an occupancy ablation added,
  connectome-state trajectories do **not** predict motor imagery across
  subjects at n=20. Reported as-is. `experiments/connectome_behavior_prediction/`.

---

## 6. Ground rules (how this repo stays honest)

- **External anchors only** (ADR-002). Every load-bearing method is tied to a
  published paper in `literature/`. The owner's prior projects are treated as
  engineering provenance, never as authority, so an undetected bug in old
  work cannot silently prop up a claim here.
- **Gate before claim.** Every `Thought` field is gated in `contract.py`;
  reference providers fail every gate by construction, so a stubbed harness
  cannot emit a prediction as a finding.
- **Null or baseline, always.** No decoding or prediction number ships
  without a surrogate/shuffle null and a baseline it must beat.
- **Decision trail.** Every tier is an ADR in `decisions/`, including its
  stated limitations and what it does *not* claim.
- **Working conventions.** No em dashes; branch-and-PR only (never push to
  `main`); README updates ship with the code they document.

---

## 7. Status and where to go next

- **18 modules, 230 verification tests passing**, all math-identity or
  analytically-known-value checks. ADRs 000-016 accepted.
- **Reading order for a newcomer:** this file, then `experiments/README.md`
  (what runs), then `decisions/` from ADR-008 forward (why), then
  `literature/SYNTHESIS_math_neuro.md` (the seven pillars of external
  grounding).
- **Open threads:** effective-connectivity priors from a real
  emotion-regulation task (to test prefrontal inhibition on-task, not on
  movie-watching); within-subject behavior decoding (where the signal is
  real and individuation is the hard part).

For the full derivation of any single result, the ADR and the experiment
folder named beside it above are the ground truth; this README is the map,
not the territory.
