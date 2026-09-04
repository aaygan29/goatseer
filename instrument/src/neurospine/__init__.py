"""NEUROSPINE: Riemannian-topological cognitive-state cartography with
purpose-constrained intervention scoring.

Public entry points:

- `Neurospine.predict(subject, recordings, context) -> Thought` reads
  a subject's cognitive state at one moment.
- `score_intervention_channels(current_state, target_state, channels,
  purpose) -> Intervention` scores intervention channels by their AIRM
  cosine alignment with the geodesic tangent from current to target
  state on the SPD manifold.

Manifold and topology primitives live in `manifold.py` and
`topology.py`; both are directly importable for study-level analysis
outside the harness (e.g. computing per-subject persistence diagrams
across an entire session).
"""

from .abstention import (
    GoltermannHuthAbstention,
    TriadResult,
    evaluate_triad,
    sign_concordance_binomial_p,
)
from .calibration import SplitConformalCalibration
from .contract import (
    COGNITIVE_DARK_MATTER_DOMAINS,
    FIELD_GATES,
    NotYetGatedError,
    Thought,
    field_is_ready,
)
from .harness import Neurospine, ProviderGates
from .intervention import (
    ChannelScore,
    Intervention,
    InterventionChannel,
    PURPOSE_REGISTRY,
    PurposeNotRegisteredError,
    score_intervention_channels,
)
from .manifold import (
    Family,
    LatentState,
    airm_distance,
    airm_exp_map,
    airm_frechet_mean,
    airm_geodesic,
    airm_inner,
    airm_log_map,
    airm_parallel_transport,
    grassmann_distance,
    grassmann_principal_angles,
    spd_expm,
    spd_invsqrtm,
    spd_logm,
    spd_sqrtm,
)
from .topology import (
    PersistencePair,
    betti_curve,
    bottleneck_distance,
    pairwise_distances,
    vietoris_rips_h0,
    vietoris_rips_h1,
)

__all__ = [
    # Cognitive-Dark-Matter taxonomy + contract
    "COGNITIVE_DARK_MATTER_DOMAINS",
    "FIELD_GATES",
    "NotYetGatedError",
    "Thought",
    "field_is_ready",
    # Harness + providers
    "GoltermannHuthAbstention",
    "Neurospine",
    "ProviderGates",
    "SplitConformalCalibration",
    "TriadResult",
    "evaluate_triad",
    "sign_concordance_binomial_p",
    # Manifold primitives (ADR-008)
    "Family",
    "LatentState",
    "airm_distance",
    "airm_exp_map",
    "airm_frechet_mean",
    "airm_geodesic",
    "airm_inner",
    "airm_log_map",
    "airm_parallel_transport",
    "grassmann_distance",
    "grassmann_principal_angles",
    "spd_expm",
    "spd_invsqrtm",
    "spd_logm",
    "spd_sqrtm",
    # Topology primitives (ADR-008)
    "PersistencePair",
    "betti_curve",
    "bottleneck_distance",
    "pairwise_distances",
    "vietoris_rips_h0",
    "vietoris_rips_h1",
    # Intervention (ADR-008)
    "ChannelScore",
    "Intervention",
    "InterventionChannel",
    "PURPOSE_REGISTRY",
    "PurposeNotRegisteredError",
    "score_intervention_channels",
]
