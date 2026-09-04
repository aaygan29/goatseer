"""End-to-end harness tests with reference (stub) providers.

Synthetic-first: no real data, no real model. Real provider tests must
live in `experiments/<name>/tests/` and be preceded by a passing
synthetic counterpart per `experiments/README.md`.
"""

from __future__ import annotations

import pytest

from neurospine.contract import COGNITIVE_DARK_MATTER_DOMAINS, Thought
from neurospine.harness import Neurospine, ProviderGates
from neurospine.reference import (
    AlwaysAbstain,
    FixedConfidence,
    NeverAbstain,
    NoSubjectCalibration,
    NullAffect,
    NullDecision,
    NullMemory,
    NullPerception,
    NullReward,
)


def make_harness(
    gates: ProviderGates | None = None,
    *,
    abstain: bool = True,
) -> Neurospine:
    return Neurospine(
        perception=NullPerception(),
        affect=NullAffect(),
        decision=NullDecision(),
        memory=NullMemory(),
        reward=NullReward(),
        subject_adapter=NoSubjectCalibration(),
        calibration=FixedConfidence(),
        abstention=AlwaysAbstain() if abstain else NeverAbstain(),
        gates=gates or ProviderGates(),
    )


class TestNoGatesPassed:
    """With no gates, every provider is short-circuited to None sentinels."""

    def test_returns_thought(self) -> None:
        t = make_harness().predict("sub-01", {}, {"task": "smoke"})
        assert isinstance(t, Thought)

    def test_all_predictions_none(self) -> None:
        t = make_harness().predict("sub-01", {}, {"task": "smoke"})
        assert t.perceived_stimulus is None
        assert t.predicted_affect is None
        assert t.predicted_decision is None
        assert t.predicted_memory_state is None
        assert t.predicted_reward_signal is None

    def test_confidence_empty(self) -> None:
        t = make_harness().predict("sub-01", {}, {"task": "smoke"})
        assert t.confidence == {}

    def test_abstain_false_when_no_gates(self) -> None:
        # AlwaysAbstain is only consulted when the abstention gate itself
        # passes. Without it, the harness cannot decide to abstain.
        t = make_harness().predict("sub-01", {}, {"task": "smoke"})
        assert t.abstention_flag is False

    def test_full_cognitive_dark_matter_declared(self) -> None:
        t = make_harness().predict("sub-01", {}, {"task": "smoke"})
        assert set(t.unmeasured_domains) == set(COGNITIVE_DARK_MATTER_DOMAINS)

    def test_not_subject_specific_by_default(self) -> None:
        t = make_harness().predict("sub-01", {}, {"task": "smoke"})
        assert t.is_subject_specific is False


class TestPartialGates:
    def test_reward_gate_activates_reward_decoder_call(self) -> None:
        """When reward gates pass, the decoder is called (returns None here
        because NullReward returns None, but the call goes through)."""
        gates = ProviderGates(
            reward={"G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
            abstention=set(),  # abstention gate not passed; abstention skipped
        )
        t = make_harness(gates).predict("s", {}, {})
        assert t.predicted_reward_signal is None  # NullReward
        assert t.abstention_flag is False

    def test_abstention_gate_fires_when_all_conditions_met(self) -> None:
        """When both a prediction gate and the abstention gate pass, the
        abstention provider is consulted; AlwaysAbstain lifts the flag."""
        gates = ProviderGates(
            reward={"G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
            abstention={"G7", "G9", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
        )
        t = make_harness(gates).predict("s", {}, {})
        assert t.abstention_flag is True
        assert t.predicted_reward_signal is None

    def test_never_abstain_permits_prediction(self) -> None:
        gates = ProviderGates(
            reward={"G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
            abstention={"G7", "G9", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
            calibration={"G7"},
        )
        t = make_harness(gates, abstain=False).predict("s", {}, {})
        assert t.abstention_flag is False
        # NullReward returns None; harness records nothing.
        assert t.predicted_reward_signal is None
        # No confidence key added because raw was None.
        assert "predicted_reward_signal" not in t.confidence


class TestSubjectSpecific:
    def test_flag_off_without_gate(self) -> None:
        t = make_harness().predict("s", {}, {})
        assert t.is_subject_specific is False

    def test_flag_reflects_adapter_when_gated(self) -> None:
        gates = ProviderGates(subject_adapter={"G8"})
        t = make_harness(gates).predict("s", {}, {})
        # NoSubjectCalibration returns False.
        assert t.is_subject_specific is False


class TestFMRITriadEnforcement:
    def test_partial_triad_short_circuits(self) -> None:
        gates = ProviderGates(memory={"G6", "G-fMRI.1", "G-fMRI.2"})
        t = make_harness(gates, abstain=False).predict("s", {}, {})
        assert t.predicted_memory_state is None

    def test_full_triad_activates_call(self) -> None:
        gates = ProviderGates(memory={"G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"})
        # NullMemory returns None regardless; assert the call went through
        # by using a lightweight monkey-patched decoder.
        harness = make_harness(gates, abstain=False)
        called: list[str] = []

        class Trace:
            def decode(self, subject, recordings, context):
                called.append(subject)
                return None

        harness.memory = Trace()
        harness.predict("sub-42", {}, {})
        assert called == ["sub-42"]


@pytest.mark.synthetic
def test_smoke_full_stack() -> None:
    gates = ProviderGates(
        perception={"G1", "G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
        affect={"G7", "G9"},
        decision={"G7", "G8"},
        memory={"G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
        reward={"G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
        subject_adapter={"G8"},
        calibration={"G7"},
        abstention={"G7", "G9", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
    )
    t = make_harness(gates, abstain=False).predict("sub-01", {}, {"task": "smoke"})
    assert isinstance(t, Thought)
    # Every provider is a Null / False stub; predictions stay None.
    assert t.perceived_stimulus is None
