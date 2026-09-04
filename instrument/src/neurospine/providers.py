"""Provider protocols for each NEUROSPINE prediction dimension.

Each provider is a thin interface. Concrete implementations live under
`experiments/<name>/`, or as plug-ins extracted from portfolio projects
that have passed their gates and their ADR-003 re-verification test.
This module only fixes the shape of the interface so the harness can
wire arbitrary providers together.

External anchors (see `decisions/ADR-002-citation-doctrine.md`):

- `PerceptionDecoder`: MEIcoder (Sobotka et al., arXiv:2510.20762).
- `AffectDecoder`: anchors from `literature/SYNTHESIS_biomedical.md`
  affect section; Cognitive Dark Matter (arXiv:2603.03414) for the
  emotional intelligence declaration.
- `DecisionDecoder`: Ratcliff (1978) DDM + recent extensions from the
  literature scan.
- `MemoryDecoder`: hippocampal backward-shifted reward (Yaghoubi et al.,
  Nature 2026, doi 10.1038/s41586-025-09958-0).
- `RewardDecoder`: same hippocampal anchor for the temporal shift;
  NAcc anticipation literature as engineering pedigree.
- `SubjectAdapter`: RAVEN weak-to-strong under shift (Jeon et al.,
  arXiv:2510.21332).
- `CalibrationProvider`: Vovk et al. (2005); Angelopoulos and Bates
  (2021).
- `AbstentionProvider`: El-Yaniv and Wiener (2010); Goltermann/Huth/Buchel
  (eLife 111743) for the fMRI reliability triad.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class PerceptionDecoder(Protocol):
    """Predicts the subject's perceived stimulus from neural + behavioral input."""

    def decode(self, subject: str, recordings: dict, context: dict) -> Any | None: ...


@runtime_checkable
class AffectDecoder(Protocol):
    """Predicts valence, arousal, and discrete emotion labels."""

    def decode(
        self, subject: str, recordings: dict, context: dict
    ) -> dict[str, float] | None: ...


@runtime_checkable
class DecisionDecoder(Protocol):
    """Predicts choice and drift-diffusion parameters from neural + behavioral input."""

    def decode(
        self, subject: str, recordings: dict, context: dict
    ) -> dict[str, Any] | None: ...


@runtime_checkable
class MemoryDecoder(Protocol):
    """Predicts recall probability and temporal-shift-of-encoding metrics."""

    def decode(
        self, subject: str, recordings: dict, context: dict
    ) -> dict[str, float] | None: ...


@runtime_checkable
class RewardDecoder(Protocol):
    """Predicts anticipation strength / reward-signal magnitude."""

    def decode(self, subject: str, recordings: dict, context: dict) -> float | None: ...


@runtime_checkable
class SubjectAdapter(Protocol):
    """Cross-subject calibration adapter.

    Returns `True` iff a subject-specific decoder is available for
    `subject`; `False` means the harness must fall back to a group
    model, and the returned `Thought` will have `is_subject_specific =
    False`.
    """

    def has_subject_calibration(self, subject: str) -> bool: ...


@runtime_checkable
class CalibrationProvider(Protocol):
    """Turns raw decoder outputs into calibrated probabilities in [0, 1].

    Implementations must hold a passing G7 gate on a held-out set.
    Split-conformal is the reference method.
    """

    def calibrate(
        self, subject: str, dimension: str, raw_output: Any
    ) -> float: ...


@runtime_checkable
class AbstentionProvider(Protocol):
    """Decides whether the harness should abstain from a specific prediction.

    The rule integrates conformal interval width, the Goltermann/Huth
    triad for any fMRI-grounded dimension, and preregistered thresholds
    on motion / artifact rejection rates.
    """

    def should_abstain(
        self, subject: str, recordings: dict, context: dict, dimension: str
    ) -> bool: ...
