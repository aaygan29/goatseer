"""NEUROSPINE: individual and group scale thought / behavior prediction.

Given a subject's neural recordings (fMRI, EEG, spikes where available)
and behavioral signals (choices, response times, face, physiology), the
harness returns a `Thought`: a structured prediction of the subject's
perceived stimulus, affect, decision, memory state, and reward
anticipation, each with calibrated confidence and abstention support.

The public entry point is `Neurospine.predict(subject, recordings, context)`.
Every prediction field is gated per `FIELD_GATES` in `contract.py`. See
`study/PROTOCOL.md` for the research study this instrument implements.
"""

from .contract import (
    COGNITIVE_DARK_MATTER_DOMAINS,
    FIELD_GATES,
    NotYetGatedError,
    Thought,
    field_is_ready,
)
from .harness import Neurospine, ProviderGates

__all__ = [
    "COGNITIVE_DARK_MATTER_DOMAINS",
    "FIELD_GATES",
    "NotYetGatedError",
    "Neurospine",
    "ProviderGates",
    "Thought",
    "field_is_ready",
]
