"""Per-prediction contract for NEUROSPINE.

NEUROSPINE reads a subject's cognitive state from neural recordings and
behavioral signals. Given `(subject, recordings, context)`, it returns a
`Thought`: a structured prediction of what the subject is perceiving,
feeling, deciding, remembering, and anticipating.

Every field is gated. A prediction that fails its acceptance gate returns
`None` and lifts `abstention_flag`; the harness never invents a value.

External anchors (see `decisions/ADR-002-citation-doctrine.md`):

- `perceived_stimulus`: MEIcoder (Sobotka et al., arXiv:2510.20762).
  Subject-conditional decoder that reconstructs stimuli from small neural
  populations.
- `predicted_affect`: Cognitive Dark Matter (Mineault, Griffiths, Escola,
  arXiv:2603.03414) for the taxonomy of unmeasured domains including
  emotional intelligence.
- `predicted_decision`: standard drift-diffusion literature (Ratcliff,
  1978); NEUROSPINE reports the DDM parameters, not just the choice.
- `predicted_memory_state`: hippocampal backward-shifted reward (Yaghoubi
  et al., Nature 2026, doi 10.1038/s41586-025-09958-0) provides the
  temporal ground truth for recall / encoding shifts.
- `predicted_reward_signal`: same hippocampal anchor; NAcc anticipation
  literature as engineering pedigree only.
- `confidence`: conformal prediction (Vovk, Gammerman, Shafer, 2005;
  Angelopoulos and Bates, 2021).
- `abstention_flag`: selective classification (El-Yaniv and Wiener, 2010),
  triggered when the Goltermann/Huth/Buchel triad (eLife 111743) fails on
  any fMRI-grounded field.
- `unmeasured_domains`: Cognitive Dark Matter taxonomy. The instrument
  must declare which of the six domains it did not attempt to read.
- `is_subject_specific`: RAVEN weak-to-strong under shift (Jeon, Sobotka,
  Choi, Brbic, arXiv:2510.21332). When a subject-specific decoder is
  unavailable we fall back to a group model and record it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


FIELD_GATES: dict[str, list[str]] = {
    # Perception passes G1 (provenance), G6 (mechanism / necessity, via
    # ablation of the identified circuit), and the fMRI triad when neural
    # input is fMRI.
    "perceived_stimulus": ["G1", "G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"],
    # Affect: measurement reliability (test-retest) plus calibration.
    "predicted_affect": ["G7", "G9"],
    # Decision: calibration plus external validity across at least two
    # tasks or subjects.
    "predicted_decision": ["G7", "G8"],
    # Memory: mechanism (backward-shift specificity ablation) plus fMRI
    # triad when memory is read from BOLD.
    "predicted_memory_state": ["G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"],
    # Reward anticipation: mechanism plus fMRI triad.
    "predicted_reward_signal": ["G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"],
    # Confidence itself must be calibrated on held-out data.
    "confidence": ["G7"],
    # Abstention: calibration plus measurement reliability plus the
    # Goltermann/Huth triad, because the abstention rule uses BOLD reliability.
    "abstention_flag": ["G7", "G9", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"],
    # Unmeasured-domains declaration: analytic integrity.
    "unmeasured_domains": ["G12"],
    # Subject specificity flag: external validity (RAVEN-style shift).
    "is_subject_specific": ["G8"],
    # Latent state: manifold correctness (G14) plus measurement reliability.
    "latent_state": ["G9", "G14"],
    # Intervention: manifold correctness (G14) plus purpose gate (G15).
    "intervention": ["G14", "G15"],
    # Trajectory summary: calibration + reliability + manifold correctness.
    # See ADR-009.
    "trajectory_summary": ["G7", "G9", "G14"],
}


COGNITIVE_DARK_MATTER_DOMAINS: tuple[str, ...] = (
    "metacognition",
    "cognitive_flexibility",
    "lifelong_learning",
    "reasoning",
    "social_reasoning",
    "emotional_intelligence",
)


class NotYetGatedError(NotImplementedError):
    """Raised when a NEUROSPINE field is emitted before its gate passes."""

    def __init__(self, field_name: str, gates: list[str]) -> None:
        self.field_name = field_name
        self.gates = list(gates)
        super().__init__(
            f"Field {field_name!r} requires gates {gates} to pass first. "
            f"See gates/gate-ladder-v0.md and portfolio/*/evaluation.md."
        )


@dataclass(frozen=True)
class Thought:
    """A prediction of a subject's cognitive state at one moment.

    All rich fields are `Optional`: `None` means "not predicted" (either the
    gate did not pass or the input modality was absent). The instrument
    never fabricates. `confidence` is always populated per prediction dim
    that was attempted; keys with no attempt are absent.
    """

    subject: str
    perceived_stimulus: Any | None = None
    predicted_affect: dict[str, float] | None = None
    predicted_decision: dict[str, Any] | None = None
    predicted_memory_state: dict[str, float] | None = None
    predicted_reward_signal: float | None = None
    confidence: dict[str, float] = field(default_factory=dict)
    abstention_flag: bool = False
    unmeasured_domains: list[str] = field(default_factory=list)
    is_subject_specific: bool = False
    # Riemannian-topological cartography (ADR-008).
    # `latent_state` is a `neurospine.manifold.LatentState` when the
    # harness ran its manifold estimator, else None. Typed as Any to
    # avoid a hard import in the contract module.
    latent_state: Any | None = None
    # Thought-trajectory transition-kernel summary (ADR-009).
    # `trajectory_summary` is a dict of scalar invariants describing
    # the subject's Markov process on the state manifold this session:
    # {stationary_entropy, entropy_rate, spectral_gap, effective_dimension,
    # optionally mfpt_to_current_state and metastable_basin_id}.
    trajectory_summary: dict[str, float] | None = None

    def __post_init__(self) -> None:
        for name, value in self.confidence.items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"confidence[{name!r}] must be in [0, 1]; got {value!r}"
                )
        for domain in self.unmeasured_domains:
            if domain not in COGNITIVE_DARK_MATTER_DOMAINS:
                raise ValueError(
                    f"unmeasured_domains contains {domain!r}, not in the "
                    "Cognitive Dark Matter taxonomy: "
                    f"{list(COGNITIVE_DARK_MATTER_DOMAINS)}"
                )
        predicted_any = any(
            v is not None
            for v in (
                self.perceived_stimulus,
                self.predicted_affect,
                self.predicted_decision,
                self.predicted_memory_state,
                self.predicted_reward_signal,
            )
        )
        if self.abstention_flag and predicted_any:
            raise ValueError(
                "abstention_flag=True forbids populating any prediction field; "
                "the instrument abstained."
            )


def field_is_ready(field_name: str, passed_gates: set[str]) -> bool:
    """Return True iff every gate required by `field_name` is in `passed_gates`."""
    required = FIELD_GATES.get(field_name)
    if required is None:
        raise KeyError(f"unknown field: {field_name!r}")
    return all(g in passed_gates for g in required)
