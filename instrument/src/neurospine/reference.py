"""Reference (stub) providers for smoke tests and synthetic experiments.

Every provider here is deterministic and requires no data. They exist so
the harness has something to wire against before real providers land,
and so the synthetic ground-truth tests pass. None of these should be
used in a real study run. See `experiments/` for real experiment
scaffolds.

All reference providers fail their acceptance gates by construction.
The `ProviderGates` for a `Neurospine` built from `reference` providers
should be empty; the harness will then short-circuit every prediction
to None (or an empty dict) and lift `abstention_flag` if the
`AbstentionProvider` says so.
"""

from __future__ import annotations

from typing import Any


class NullPerception:
    """Always returns None. Correct behavior when no perception decoder
    is wired."""

    def decode(self, subject: str, recordings: dict, context: dict) -> Any | None:
        return None


class NullAffect:
    def decode(
        self, subject: str, recordings: dict, context: dict
    ) -> dict[str, float] | None:
        return None


class NullDecision:
    def decode(
        self, subject: str, recordings: dict, context: dict
    ) -> dict[str, Any] | None:
        return None


class NullMemory:
    def decode(
        self, subject: str, recordings: dict, context: dict
    ) -> dict[str, float] | None:
        return None


class NullReward:
    def decode(self, subject: str, recordings: dict, context: dict) -> float | None:
        return None


class NoSubjectCalibration:
    """No subject-specific decoder ever available. Fails G8 by construction."""

    def has_subject_calibration(self, subject: str) -> bool:
        return False


class FixedConfidence:
    """Always returns 0.0. Fails G7 by construction; guarantees the
    harness never asserts a confident prediction from stub providers."""

    def calibrate(self, subject: str, dimension: str, raw_output: Any) -> float:
        return 0.0


class AlwaysAbstain:
    """Always abstains. Correct default when the reliability triad has
    not been established; ensures a stubbed harness cannot ship a
    prediction as a claim."""

    def should_abstain(
        self, subject: str, recordings: dict, context: dict, dimension: str
    ) -> bool:
        return True


class NeverAbstain:
    """For testing the non-abstaining branch of the harness. Do NOT use
    in a real run without a passing G7 + G9 + Goltermann/Huth triad."""

    def should_abstain(
        self, subject: str, recordings: dict, context: dict, dimension: str
    ) -> bool:
        return False
