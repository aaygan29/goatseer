"""ADR-003 external re-verification for `SplitConformalCalibration`.

External anchor: Vovk, Gammerman, Shafer (2005) and Angelopoulos + Bates
(2021). The conformal p-value has three properties any implementation
must satisfy:

1. **Exchangeability -> uniform p-values under H_0.** If the query
   nonconformity score is drawn from the same distribution as the
   calibration set, its p-value is (approximately) uniform on (0, 1].
2. **Extreme scores get low p-values.** A query with a nonconformity
   score much larger than any calibration score should get p ~ 1/(N+1).
3. **Low-nonconformity queries get p ~ 1.** A query at or below the
   minimum calibration score should get p == 1.

Tolerance: these are qualitative properties of the recipe, not
point-estimate reproductions of any published number. The refactor of
the calibrator's interface (accepting a scalar nonconformity from
upstream) is documented in `../../src/neurospine/calibration.py`.
"""

from __future__ import annotations

import statistics

import pytest

from neurospine.calibration import SplitConformalCalibration


class TestConformalPValueProperties:
    def test_query_far_above_calibration_gets_minimum_p(self) -> None:
        cal = list(range(100))  # 0..99
        p = SplitConformalCalibration({"perceived_stimulus": cal}).calibrate(
            "s", "perceived_stimulus", 10_000.0
        )
        # Only the +1 continuity survives
        assert p == pytest.approx(1 / 101)

    def test_query_below_min_gets_p_of_one(self) -> None:
        cal = list(range(100))
        p = SplitConformalCalibration({"perceived_stimulus": cal}).calibrate(
            "s", "perceived_stimulus", -1.0
        )
        assert p == pytest.approx(1.0)

    def test_query_at_median_gets_p_around_half(self) -> None:
        cal = list(range(100))
        p = SplitConformalCalibration({"perceived_stimulus": cal}).calibrate(
            "s", "perceived_stimulus", 50.0
        )
        # 50 calibration scores are >= 50 (i.e. 50..99).
        # p = (50 + 1) / (100 + 1) = 51 / 101 ~ 0.505
        assert p == pytest.approx(51 / 101)

    def test_uniform_p_values_when_query_from_same_distribution(self) -> None:
        # Draw many "query" points from the calibration distribution;
        # p-values should be roughly uniform in (0, 1].
        import random

        random.seed(0)
        cal = [random.gauss(0, 1) for _ in range(500)]
        calibrator = SplitConformalCalibration({"predicted_reward_signal": cal})
        queries = [random.gauss(0, 1) for _ in range(500)]
        p_values = [
            calibrator.calibrate("s", "predicted_reward_signal", q) for q in queries
        ]
        mean = statistics.mean(p_values)
        assert 0.4 < mean < 0.6

    def test_unknown_dimension_returns_zero(self) -> None:
        p = SplitConformalCalibration({}).calibrate(
            "s", "predicted_affect", 0.3
        )
        assert p == 0.0

    def test_nonnumeric_raw_output_returns_zero(self) -> None:
        cal = [0.1, 0.2, 0.3]
        cal_by = {"predicted_affect": cal}
        c = SplitConformalCalibration(cal_by)
        assert c.calibrate("s", "predicted_affect", "not-a-number") == 0.0
        assert c.calibrate("s", "predicted_affect", None) == 0.0
        assert c.calibrate("s", "predicted_affect", True) == 0.0

    def test_dict_with_nonconformity_key_accepted(self) -> None:
        cal = list(range(100))
        c = SplitConformalCalibration({"predicted_affect": cal})
        p_scalar = c.calibrate("s", "predicted_affect", 50.0)
        p_dict = c.calibrate("s", "predicted_affect", {"nonconformity_score": 50.0})
        assert p_scalar == p_dict


class TestPredictionIntervalWidth:
    def test_returns_appropriate_quantile(self) -> None:
        cal = list(range(100))
        c = SplitConformalCalibration({"predicted_reward_signal": cal})
        # (1 - 0.1) * (100 + 1) = 90.9, rank = 90 -> sorted[89] = 89
        width = c.prediction_interval_width("predicted_reward_signal", alpha=0.1)
        assert width == 89

    def test_no_calibration_returns_none(self) -> None:
        c = SplitConformalCalibration({})
        assert c.prediction_interval_width("predicted_reward_signal") is None

    def test_invalid_alpha_raises(self) -> None:
        c = SplitConformalCalibration({"x": [1.0, 2.0, 3.0]})
        with pytest.raises(ValueError):
            c.prediction_interval_width("x", alpha=0.0)
        with pytest.raises(ValueError):
            c.prediction_interval_width("x", alpha=1.0)


class TestIntegrationWithAbstention:
    """The interval width feeds the AbstentionProvider's threshold."""

    def test_narrow_interval_permits_prediction(self) -> None:
        from neurospine.abstention import GoltermannHuthAbstention

        cal = [0.01, 0.02, 0.03, 0.04, 0.05]
        c = SplitConformalCalibration({"predicted_affect": cal})
        width = c.prediction_interval_width("predicted_affect", alpha=0.1)
        abstain = GoltermannHuthAbstention(
            interval_width_by_dim={"predicted_affect": width},
            interval_width_threshold=0.5,
        )
        assert abstain.should_abstain(
            "sub-01", {}, {}, "predicted_affect"
        ) is False

    def test_wide_interval_triggers_abstention(self) -> None:
        from neurospine.abstention import GoltermannHuthAbstention

        cal = [1.0, 2.0, 3.0, 4.0, 5.0]  # wide calibration set
        c = SplitConformalCalibration({"predicted_affect": cal})
        width = c.prediction_interval_width("predicted_affect", alpha=0.1)
        abstain = GoltermannHuthAbstention(
            interval_width_by_dim={"predicted_affect": width},
            interval_width_threshold=0.5,
        )
        assert abstain.should_abstain(
            "sub-01", {}, {}, "predicted_affect"
        ) is True
