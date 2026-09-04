"""Real `AbstentionProvider` implementations for NEUROSPINE.

The Goltermann / Huth / Buchel reliability triad (eLife 111743) is the
external anchor. That paper reports that under a common BOLD-CMRO2
coupling assumption, 77.2 percent of voxels are unrobustly classified
and CMRO2 variability is 127.8 percent higher than BOLD variability.
The practical consequence for NEUROSPINE: an fMRI-grounded prediction
that cannot demonstrate per-subject cross-validation stability, cross-
participant sign concordance, and group-level significance is
unreliable and should be abstained on, not shipped as a claim.

`GoltermannHuthAbstention` implements the check. Its inputs are
per-subject and per-participant statistics that a real decoder must
report before it can be gated in. When those statistics are absent
(the default in a stubbed run), the provider abstains, which is the
safe default.

Selective classification (El-Yaniv and Wiener, 2010) is the framing:
refusal is a first-class output. Conformal risk control (Angelopoulos
and Bates, 2021) provides the interval-width leg of the rule.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class TriadResult:
    """Outcome of the Goltermann/Huth triad on one fitted decoder.

    Each leg is (passed, p_or_value). `all_pass` is convenient for
    callers that only care about the aggregate.
    """

    g_fmri_1: bool
    g_fmri_2: bool
    g_fmri_3: bool
    per_participant_cv_score: float
    sign_concordance_p: float
    group_level_p: float

    @property
    def all_pass(self) -> bool:
        return self.g_fmri_1 and self.g_fmri_2 and self.g_fmri_3


def sign_concordance_binomial_p(positive_count: int, total: int) -> float:
    """Two-sided binomial test against p = 0.5.

    Vectorized-safe reference implementation. Matches
    `scipy.stats.binomtest(k, n, 0.5, alternative='two-sided').pvalue`
    within numerical tolerance for reasonable n. Avoids the scipy
    dependency for the reference provider so `neurospine` stays
    dependency-free.
    """
    if total <= 0:
        raise ValueError(f"total must be positive; got {total}")
    if not (0 <= positive_count <= total):
        raise ValueError(
            f"positive_count must be in [0, {total}]; got {positive_count}"
        )
    # For p=0.5 the sum of PMFs at least as extreme is 2 * one-sided.
    k = min(positive_count, total - positive_count)
    # Sum P(X <= k) under Binomial(total, 0.5)
    log_half = -math.log(2.0)
    log_pmf_terms = []
    for i in range(k + 1):
        # log C(total, i) + total * log(0.5)
        log_choose = (
            math.lgamma(total + 1)
            - math.lgamma(i + 1)
            - math.lgamma(total - i + 1)
        )
        log_pmf_terms.append(log_choose + total * log_half)
    m = max(log_pmf_terms)
    tail = sum(math.exp(x - m) for x in log_pmf_terms)
    one_sided = math.exp(m) * tail
    two_sided = min(1.0, 2.0 * one_sided)
    return two_sided


def evaluate_triad(
    per_participant_cv_scores: list[float],
    per_participant_directional_signs: list[int],
    group_level_p: float,
    cv_score_threshold: float = 0.0,
    concordance_alpha: float = 0.05,
    group_alpha: float = 0.05,
) -> TriadResult:
    """Score the Goltermann/Huth triad on a fitted decoder's outputs.

    - `per_participant_cv_scores`: for each subject, a held-out CV
      score (correlation, R^2, or similar), higher-is-better. G-fMRI.1
      passes when the mean is above `cv_score_threshold`.
    - `per_participant_directional_signs`: for each subject, +1 if the
      decoder's effect points in the hypothesized direction, else -1
      (or 0; zeros are excluded from the concordance test). G-fMRI.2
      is the two-sided binomial against p=0.5, passes when p is below
      `concordance_alpha`.
    - `group_level_p`: p-value from the group-level test the caller
      already ran (e.g. one-sample t-test, Wilcoxon, mixed model).
      G-fMRI.3 passes when it is below `group_alpha`.
    """
    if not per_participant_cv_scores:
        raise ValueError("per_participant_cv_scores must not be empty")
    if not per_participant_directional_signs:
        raise ValueError("per_participant_directional_signs must not be empty")

    mean_cv = sum(per_participant_cv_scores) / len(per_participant_cv_scores)
    g1_pass = mean_cv > cv_score_threshold

    nonzero = [s for s in per_participant_directional_signs if s != 0]
    if not nonzero:
        # All signs are exactly zero; treat as null and abstain.
        return TriadResult(
            g_fmri_1=g1_pass,
            g_fmri_2=False,
            g_fmri_3=group_level_p < group_alpha,
            per_participant_cv_score=mean_cv,
            sign_concordance_p=1.0,
            group_level_p=group_level_p,
        )
    positive = sum(1 for s in nonzero if s > 0)
    concordance_p = sign_concordance_binomial_p(positive, len(nonzero))
    g2_pass = concordance_p < concordance_alpha

    g3_pass = group_level_p < group_alpha

    return TriadResult(
        g_fmri_1=g1_pass,
        g_fmri_2=g2_pass,
        g_fmri_3=g3_pass,
        per_participant_cv_score=mean_cv,
        sign_concordance_p=concordance_p,
        group_level_p=group_level_p,
    )


@dataclass
class GoltermannHuthAbstention:
    """AbstentionProvider that enforces the Goltermann/Huth triad on
    fMRI-grounded prediction dimensions.

    The caller supplies, per dimension, the triad outcome from the most
    recent fitted decoder. If the triad has not been computed for a
    dimension, the provider abstains (safe default). Non-fMRI
    dimensions are not gated by the triad and abstain only when the
    conformal interval width exceeds `interval_width_threshold`.

    `should_abstain` returns True when abstention should fire.
    """

    fmri_grounded_dimensions: frozenset[str] = frozenset(
        {
            "perceived_stimulus",
            "predicted_memory_state",
            "predicted_reward_signal",
        }
    )
    latest_triad: dict[str, TriadResult] | None = None
    interval_width_by_dim: dict[str, float] | None = None
    interval_width_threshold: float = 0.5
    motion_rejection_by_subject: dict[str, float] | None = None
    motion_rejection_threshold: float = 0.20

    def should_abstain(
        self, subject: str, recordings: dict, context: dict, dimension: str
    ) -> bool:
        if (
            self.motion_rejection_by_subject
            and self.motion_rejection_by_subject.get(subject, 0.0)
            > self.motion_rejection_threshold
        ):
            return True

        if dimension in self.fmri_grounded_dimensions:
            if self.latest_triad is None or dimension not in self.latest_triad:
                return True
            if not self.latest_triad[dimension].all_pass:
                return True

        if self.interval_width_by_dim:
            width = self.interval_width_by_dim.get(dimension)
            if width is not None and width > self.interval_width_threshold:
                return True

        return False
