"""Real `CalibrationProvider` implementations for NEUROSPINE.

Split-conformal calibration is the reference method. Given a
held-out calibration set of nonconformity scores per prediction
dimension, `SplitConformalCalibration.calibrate` returns the
standard conformal p-value for a query point: the fraction of
calibration scores at least as extreme as the query's score, plus
the standard `+1` continuity correction. This value is in `(0, 1]`
and is interpretable as calibrated confidence under the exchangeability
assumption of conformal prediction.

External anchors:

- Vovk, Gammerman, Shafer, "Algorithmic Learning in a Random
  World", Springer 2005 (conformal prediction foundations).
- Angelopoulos, Bates, "A Gentle Introduction to Conformal
  Prediction and Distribution-Free Uncertainty Quantification",
  arXiv:2107.07511 (2021).

The reference implementation is dependency-free by design. The
caller supplies a scalar nonconformity score for the query point;
computing that score from a raw prediction is the decoder's
responsibility, so the calibrator stays free of decoder-specific
details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SplitConformalCalibration:
    """Split-conformal calibration provider.

    `calibration_scores_by_dim` maps each prediction dimension to a
    list of nonconformity scores from a held-out calibration split.
    Higher score means "more anomalous"; the provider expects the
    same convention for the query point.

    `calibrate(subject, dimension, raw_output)` returns
    `(count_of_calibration_scores_at_least_as_large + 1) / (N + 1)`,
    the standard conformal p-value, capped to `(0, 1]`.

    Contract on `raw_output`:
    - If `raw_output` is a real number, it is treated as the query
      point's nonconformity score directly.
    - If `raw_output` is a mapping that carries a
      `"nonconformity_score"` key with a real value, that value is
      used.
    - Otherwise, or if the dimension has no calibration set, the
      provider returns `0.0`: no confidence available.

    This design forces decoders to explicitly emit a scalar
    nonconformity, rather than letting the calibrator guess.
    """

    calibration_scores_by_dim: dict[str, list[float]] = field(default_factory=dict)

    def calibrate(self, subject: str, dimension: str, raw_output: Any) -> float:
        cal = self.calibration_scores_by_dim.get(dimension)
        if not cal:
            return 0.0
        score = _extract_nonconformity(raw_output)
        if score is None:
            return 0.0
        count_at_least = sum(1 for c in cal if c >= score)
        p_value = (count_at_least + 1) / (len(cal) + 1)
        return max(0.0, min(1.0, p_value))

    def prediction_interval_width(
        self, dimension: str, alpha: float = 0.1
    ) -> float | None:
        """Return the (1 - alpha) split-conformal interval half-width
        for `dimension`, or `None` if the dimension has no calibration
        set.

        This is the width the `AbstentionProvider` uses when deciding
        whether the prediction interval is too wide to ship.
        """
        cal = self.calibration_scores_by_dim.get(dimension)
        if not cal:
            return None
        if not (0.0 < alpha < 1.0):
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        n = len(cal)
        rank = min(n, max(1, int((1.0 - alpha) * (n + 1))))
        return sorted(cal)[rank - 1]


def _extract_nonconformity(raw_output: Any) -> float | None:
    """Extract a scalar nonconformity score from `raw_output`, or None."""
    if isinstance(raw_output, bool):
        # Booleans subclass int; explicit rejection to avoid confusion.
        return None
    if isinstance(raw_output, (int, float)):
        return float(raw_output)
    if isinstance(raw_output, dict) and "nonconformity_score" in raw_output:
        val = raw_output["nonconformity_score"]
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val)
    return None
