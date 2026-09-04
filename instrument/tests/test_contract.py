"""Tests for the Thought contract."""

from __future__ import annotations

import pytest

from neurospine.contract import (
    COGNITIVE_DARK_MATTER_DOMAINS,
    FIELD_GATES,
    NotYetGatedError,
    Thought,
    field_is_ready,
)


class TestFieldGates:
    def test_all_fields_registered(self) -> None:
        expected = {
            "perceived_stimulus",
            "predicted_affect",
            "predicted_decision",
            "predicted_memory_state",
            "predicted_reward_signal",
            "confidence",
            "abstention_flag",
            "unmeasured_domains",
            "is_subject_specific",
        }
        assert set(FIELD_GATES.keys()) == expected

    def test_every_field_has_at_least_one_gate(self) -> None:
        for name, gates in FIELD_GATES.items():
            assert gates, f"field {name!r} has no gate"

    def test_fmri_grounded_fields_require_triad(self) -> None:
        for name in (
            "perceived_stimulus",
            "predicted_memory_state",
            "predicted_reward_signal",
            "abstention_flag",
        ):
            gates = set(FIELD_GATES[name])
            assert {"G-fMRI.1", "G-fMRI.2", "G-fMRI.3"}.issubset(gates), (
                f"{name} must require the full Goltermann/Huth triad"
            )


class TestCognitiveDarkMatter:
    def test_six_domains(self) -> None:
        assert len(COGNITIVE_DARK_MATTER_DOMAINS) == 6

    def test_includes_emotional_intelligence(self) -> None:
        assert "emotional_intelligence" in COGNITIVE_DARK_MATTER_DOMAINS


class TestFieldIsReady:
    def test_ready_when_all_required_pass(self) -> None:
        assert field_is_ready("confidence", {"G7"}) is True

    def test_not_ready_when_any_required_missing(self) -> None:
        assert field_is_ready("perceived_stimulus", {"G1", "G6"}) is False
        assert (
            field_is_ready(
                "perceived_stimulus",
                {"G1", "G6", "G-fMRI.1", "G-fMRI.2", "G-fMRI.3"},
            )
            is True
        )

    def test_unknown_field_raises_key_error(self) -> None:
        with pytest.raises(KeyError):
            field_is_ready("not_a_field", set())


class TestThoughtValidation:
    def test_minimal_valid_construction(self) -> None:
        t = Thought(subject="sub-01")
        assert t.subject == "sub-01"
        assert t.perceived_stimulus is None
        assert t.abstention_flag is False
        assert t.confidence == {}

    def test_confidence_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError, match="confidence"):
            Thought(subject="s", confidence={"perceived_stimulus": 1.5})
        with pytest.raises(ValueError, match="confidence"):
            Thought(subject="s", confidence={"predicted_affect": -0.01})

    def test_unmeasured_domain_must_be_in_taxonomy(self) -> None:
        with pytest.raises(ValueError, match="Cognitive Dark Matter"):
            Thought(subject="s", unmeasured_domains=["not_a_real_domain"])

    def test_abstain_forbids_populated_prediction(self) -> None:
        with pytest.raises(ValueError, match="abstention_flag"):
            Thought(
                subject="s",
                abstention_flag=True,
                predicted_reward_signal=0.4,
            )

    def test_abstain_with_all_null_predictions_accepted(self) -> None:
        t = Thought(subject="s", abstention_flag=True)
        assert t.abstention_flag is True

    def test_can_carry_full_predictions_without_abstain(self) -> None:
        t = Thought(
            subject="sub-02",
            perceived_stimulus="cat_image_042",
            predicted_affect={"valence": 0.7, "arousal": 0.3},
            predicted_decision={"choice": 1, "rt": 0.62, "drift": 1.4},
            predicted_memory_state={"recall_p": 0.55, "shift_ms": -280.0},
            predicted_reward_signal=0.8,
            confidence={
                "perceived_stimulus": 0.75,
                "predicted_affect": 0.6,
                "predicted_decision": 0.8,
                "predicted_memory_state": 0.4,
                "predicted_reward_signal": 0.65,
            },
            is_subject_specific=True,
            unmeasured_domains=list(COGNITIVE_DARK_MATTER_DOMAINS),
        )
        assert t.is_subject_specific is True
        assert t.perceived_stimulus == "cat_image_042"


class TestNotYetGatedError:
    def test_message_names_field_and_gates(self) -> None:
        err = NotYetGatedError("perceived_stimulus", ["G1", "G6"])
        assert "perceived_stimulus" in str(err)
        assert "G1" in str(err)
        assert "gate-ladder-v0.md" in str(err)

    def test_is_not_implemented(self) -> None:
        assert isinstance(
            NotYetGatedError("x", ["G1"]), NotImplementedError
        )
