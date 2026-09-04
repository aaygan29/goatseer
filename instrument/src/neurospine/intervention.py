"""Purpose-constrained intervention scoring on the Riemannian manifold.

Given a current cognitive state `P` and a target state `Q` on the SPD
manifold, `score_intervention_channels` computes the AIRM geodesic
tangent `X = airm_log_map(P, Q)` and ranks a set of intervention
channels by the affine-invariant cosine alignment of each channel's
pushforward with X. The best-aligned channel is the one that most
directly moves the subject toward the target along the geodesic.

**No intervention without a purpose.** `Intervention` construction
requires a `purpose` from the ADR-managed purpose registry. The
registry is a whitelist. Attempting to score an intervention for an
unregistered purpose raises `PurposeNotRegisteredError`; new purposes
are added by ADR, never at call time. This is the ethics primitive.

External anchors (see ADR-008):

- Miller, Brincat, Roy 2026 (pubmed-42618509): wave-mediated
  top-down control as the mechanism substrate for the channel-
  pushforward argument.
- O'Reilly-Shah + Selvitella 2026 (pubmed-42599379): prediction-
  separation bound sets the resolution below which channel alignment
  is meaningful.
- Barachant et al. 2012 (Riemannian geometry BCI) for the AIRM
  channel-scoring convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .manifold import (
    LatentState,
    airm_distance,
    airm_inner,
    airm_log_map,
)


class PurposeNotRegisteredError(ValueError):
    """Raised when an intervention is scored under a purpose not in
    the ADR-managed registry."""


# Purpose registry. Extend only via ADR (see ADR-008 and the future
# ADR-009 for the registry proper). Keys are purpose ids; values are
# short human-readable descriptions.
PURPOSE_REGISTRY: dict[str, str] = {
    "reduce_anxiety_preserve_cognition": (
        "Move the subject toward a lower-anxiety state without "
        "degrading the decision-related dimensions."
    ),
    "sustained_attention": (
        "Increase and sustain focal attention on a declared task "
        "without altering affective dimensions."
    ),
    "recall_specific_memory": (
        "Reinstate the neural signature associated with a specific "
        "encoded event without altering other memory content."
    ),
    "restore_baseline": (
        "Return the subject to a preregistered baseline state after "
        "a perturbation. Only usable when the baseline has been "
        "measured for this subject."
    ),
}


@dataclass(frozen=True)
class InterventionChannel:
    """One candidate intervention channel.

    `pushforward` is a callable mapping a `LatentState.matrix` to a
    tangent vector at that state, representing the linearized effect
    of the channel. Concrete channels (attention capture, TMS pulse,
    stimulus injection, biofeedback loop) each have their own
    calibrated pushforward.
    """

    name: str
    pushforward: Callable[[np.ndarray], np.ndarray]
    modality: str
    calibration_note: str = ""


@dataclass(frozen=True)
class ChannelScore:
    name: str
    modality: str
    airm_cosine_alignment: float
    pushforward_norm: float


@dataclass(frozen=True)
class Intervention:
    """Result of scoring interventions from `current_state` to
    `target_state` under a declared `purpose`.

    - `channels_by_efficacy`: channels sorted descending by AIRM cosine
      alignment with the geodesic tangent.
    - `geodesic_length`: AIRM distance between the two states.
    - `safety_margin`: AIRM distance from the geodesic midpoint to
      the subject's out-of-scope subregion, expressed as a scalar (
      `float("inf")` when no out-of-scope subregion is declared).
    """

    purpose: str
    current_state: LatentState
    target_state: LatentState
    channels_by_efficacy: tuple[ChannelScore, ...]
    geodesic_length: float
    safety_margin: float

    def __post_init__(self) -> None:
        if self.purpose not in PURPOSE_REGISTRY:
            raise PurposeNotRegisteredError(
                f"purpose {self.purpose!r} is not in PURPOSE_REGISTRY. "
                "Add via ADR; do not add at call time."
            )
        if self.current_state.family != self.target_state.family:
            raise ValueError(
                "current and target states must be on the same manifold "
                "family; got "
                f"{self.current_state.family!r} vs "
                f"{self.target_state.family!r}"
            )
        if self.geodesic_length < 0:
            raise ValueError(
                f"geodesic_length must be non-negative; got "
                f"{self.geodesic_length}"
            )
        if self.safety_margin < 0:
            raise ValueError(
                f"safety_margin must be non-negative; got "
                f"{self.safety_margin}"
            )


def score_intervention_channels(
    current_state: LatentState,
    target_state: LatentState,
    channels: list[InterventionChannel],
    purpose: str,
    out_of_scope_region: LatentState | None = None,
) -> Intervention:
    """Score `channels` by their AIRM cosine alignment with the
    geodesic tangent from `current_state` to `target_state`.

    Requires SPD family for both states. Grassmann and learned-latent
    families are queued for follow-up ADRs and raise NotImplementedError
    here.
    """
    if purpose not in PURPOSE_REGISTRY:
        raise PurposeNotRegisteredError(
            f"purpose {purpose!r} not registered; add via ADR."
        )
    if current_state.family != "spd" or target_state.family != "spd":
        raise NotImplementedError(
            "score_intervention_channels currently supports SPD family "
            "only; Grassmann and learned-latent scoring will land in "
            "later ADRs."
        )

    P = current_state.matrix
    Q = target_state.matrix
    geo_tangent = airm_log_map(P, Q)
    geo_norm = np.sqrt(airm_inner(P, geo_tangent, geo_tangent))
    geo_length = airm_distance(P, Q)

    scored: list[ChannelScore] = []
    for ch in channels:
        push = ch.pushforward(P)
        push_norm = np.sqrt(airm_inner(P, push, push))
        if push_norm == 0.0 or geo_norm == 0.0:
            cos_align = 0.0
        else:
            cos_align = (
                airm_inner(P, push, geo_tangent) / (push_norm * geo_norm)
            )
        cos_align = float(max(-1.0, min(1.0, cos_align)))
        scored.append(
            ChannelScore(
                name=ch.name,
                modality=ch.modality,
                airm_cosine_alignment=cos_align,
                pushforward_norm=float(push_norm),
            )
        )
    scored.sort(key=lambda s: -s.airm_cosine_alignment)

    if out_of_scope_region is None:
        margin = float("inf")
    else:
        if out_of_scope_region.family != "spd":
            raise NotImplementedError(
                "out_of_scope_region SPD-only for now."
            )
        # Distance from midpoint of the geodesic to the out-of-scope point.
        from .manifold import airm_geodesic  # local import avoids cycle

        midpoint = airm_geodesic(P, Q, 0.5)
        margin = float(airm_distance(midpoint, out_of_scope_region.matrix))

    return Intervention(
        purpose=purpose,
        current_state=current_state,
        target_state=target_state,
        channels_by_efficacy=tuple(scored),
        geodesic_length=float(geo_length),
        safety_margin=margin,
    )
