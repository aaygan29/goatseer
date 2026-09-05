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
from .behavior import (
    BehaviorMarkovModel,
    OccupancyModel,
    analyze_state_sequences,
    analyze_within_subject,
    class_log_likelihood,
    evaluate_behavior_markov_model,
    evaluate_occupancy_model,
    fit_behavior_markov_model,
    fit_occupancy_model,
    predict_behavior,
    predict_occupancy,
    subject_disjoint_split,
)
from .calibration import SplitConformalCalibration
from .circuit import (
    DirectedCircuit,
    DirectedEdge,
    ExogenousEffector,
    build_directed_circuit,
)
from .contract import (
    COGNITIVE_DARK_MATTER_DOMAINS,
    FIELD_GATES,
    NotYetGatedError,
    Thought,
    field_is_ready,
)
from .discretize import (
    SupervisedTangentDiscretizer,
    assign_states,
    discriminant_axis,
    quantile_edges,
)
from .dynamics import (
    TrajectorySummary,
    absorption_probabilities,
    committor,
    entropy_rate,
    estimate_transition_matrix,
    expected_steps_to_absorption,
    mean_first_passage_time,
    perron_cluster_analysis,
    spectral_gap,
    stationary_distribution,
    summarize_trajectory,
)
from .harness import Neurospine, ProviderGates
from .hmm import GaussianHMM
from .intervention import (
    PURPOSE_REGISTRY,
    ChannelScore,
    Intervention,
    InterventionChannel,
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
    airm_geodesic_min_distance,
    airm_inner,
    airm_log_map,
    airm_parallel_transport,
    grassmann_chordal_distance,
    grassmann_distance,
    grassmann_principal_angles,
    spd_expm,
    spd_invsqrtm,
    spd_logm,
    spd_sqrtm,
    spd_tangent_embedding,
    spd_tangent_vector,
)
from .sequence_decode import (
    SupervisedSequenceDecoder,
    transition_gain,
)
from .signed_dynamics import (
    SignedLinearSystem,
    build_signed_system,
)
from .effective_connectivity import (
    directed_influence,
    discrete_steady_state,
    edge_group_stats,
    fit_var1,
    group_effective_connectivity,
    spectral_radius,
)
from .propagation import (
    ActivationChain,
    AtlasPropagation,
    activation_chain,
    connectome_to_markov,
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
    "GaussianHMM",
    "GoltermannHuthAbstention",
    "NotYetGatedError",
    "Neurospine",
    "ProviderGates",
    "SplitConformalCalibration",
    "Thought",
    "TriadResult",
    "evaluate_triad",
    "BehaviorMarkovModel",
    "OccupancyModel",
    "analyze_state_sequences",
    "analyze_within_subject",
    "class_log_likelihood",
    "evaluate_behavior_markov_model",
    "evaluate_occupancy_model",
    "fit_behavior_markov_model",
    "fit_occupancy_model",
    "predict_behavior",
    "predict_occupancy",
    "subject_disjoint_split",
    # Geometry-preserving discretization (ADR-017)
    "SupervisedTangentDiscretizer",
    "assign_states",
    "discriminant_axis",
    "quantile_edges",
    "field_is_ready",
    "sign_concordance_binomial_p",
    # Manifold primitives (ADR-008)
    "Family",
    "LatentState",
    "airm_distance",
    "airm_exp_map",
    "airm_frechet_mean",
    "airm_geodesic",
    "airm_geodesic_min_distance",
    "airm_inner",
    "airm_log_map",
    "airm_parallel_transport",
    "grassmann_chordal_distance",
    "grassmann_distance",
    "grassmann_principal_angles",
    "spd_expm",
    "spd_invsqrtm",
    "spd_logm",
    "spd_sqrtm",
    "spd_tangent_embedding",
    "spd_tangent_vector",
    # Directed circuits + effectors (ADR-014)
    "DirectedCircuit",
    "DirectedEdge",
    "ExogenousEffector",
    "build_directed_circuit",
    "absorption_probabilities",
    "expected_steps_to_absorption",
    # Signed linear dynamics for inhibitory regulation (ADR-015)
    "SignedLinearSystem",
    "build_signed_system",
    # Supervised sequence decoding (ADR-019)
    "SupervisedSequenceDecoder",
    "transition_gain",
    # Effective connectivity from real BOLD (ADR-016)
    "directed_influence",
    "discrete_steady_state",
    "edge_group_stats",
    "fit_var1",
    "group_effective_connectivity",
    "spectral_radius",
    # Anatomical propagation (ADR-013)
    "ActivationChain",
    "AtlasPropagation",
    "activation_chain",
    "connectome_to_markov",
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
    # Thought-trajectory dynamics (ADR-009)
    "TrajectorySummary",
    "committor",
    "entropy_rate",
    "estimate_transition_matrix",
    "mean_first_passage_time",
    "perron_cluster_analysis",
    "spectral_gap",
    "stationary_distribution",
    "summarize_trajectory",
]
