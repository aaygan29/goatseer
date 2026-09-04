"""The top-level NEUROSPINE harness.

Given a subject, a `recordings` dict (neural + behavioral inputs), and a
`context` dict (task metadata, stimulus history, session id), the
harness assembles a `Thought` by calling each provider and packaging the
results into the immutable tuple.

The harness enforces three invariants that no provider can bypass:

1. **Gate short-circuit.** Every prediction dimension is only attempted
   when the caller declares (via `ProviderGates`) that the gates for
   that dimension have passed. Otherwise the dimension is set to
   `None` and no provider is called.
2. **Abstention absorbs claims.** If `AbstentionProvider.should_abstain`
   returns True for any dimension, that dimension is set to `None` and
   `abstention_flag` is lifted. A `Thought` with `abstention_flag=True`
   cannot carry any populated prediction.
3. **Unmeasured domains are always declared.** Every returned `Thought`
   carries the full Cognitive Dark Matter taxonomy in
   `unmeasured_domains`, unless the caller has explicitly opted in to
   measuring one of them (out of scope for v0).

External anchors: see `providers.py`. The short-circuit design implements
"refuse to answer when you cannot justify it" per selective classification
(El-Yaniv and Wiener, 2010).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .contract import (
    COGNITIVE_DARK_MATTER_DOMAINS,
    FIELD_GATES,
    Thought,
)
from .providers import (
    AbstentionProvider,
    AffectDecoder,
    CalibrationProvider,
    DecisionDecoder,
    MemoryDecoder,
    PerceptionDecoder,
    RewardDecoder,
    SubjectAdapter,
)


@dataclass
class ProviderGates:
    """The set of gate ids that each provider has passed.

    Sourced from `portfolio/<slug>/evaluation.md` at instrument-init time.
    Immutable after construction. To bump a provider's gates, rebuild the
    `Neurospine` object; do not patch in place.
    """

    perception: set[str] = field(default_factory=set)
    affect: set[str] = field(default_factory=set)
    decision: set[str] = field(default_factory=set)
    memory: set[str] = field(default_factory=set)
    reward: set[str] = field(default_factory=set)
    subject_adapter: set[str] = field(default_factory=set)
    calibration: set[str] = field(default_factory=set)
    abstention: set[str] = field(default_factory=set)


@dataclass
class Neurospine:
    """The reference harness."""

    perception: PerceptionDecoder
    affect: AffectDecoder
    decision: DecisionDecoder
    memory: MemoryDecoder
    reward: RewardDecoder
    subject_adapter: SubjectAdapter
    calibration: CalibrationProvider
    abstention: AbstentionProvider
    gates: ProviderGates = field(default_factory=ProviderGates)

    def predict(self, subject: str, recordings: dict, context: dict) -> Thought:
        subject_specific = (
            self.subject_adapter.has_subject_calibration(subject)
            if self._ready("is_subject_specific", self.gates.subject_adapter)
            else False
        )

        raw_predictions: dict[str, object] = {}
        confidence: dict[str, float] = {}
        any_abstain = False

        for dim, gate_set, decoder in [
            ("perceived_stimulus", self.gates.perception, self.perception),
            ("predicted_affect", self.gates.affect, self.affect),
            ("predicted_decision", self.gates.decision, self.decision),
            ("predicted_memory_state", self.gates.memory, self.memory),
            ("predicted_reward_signal", self.gates.reward, self.reward),
        ]:
            if not self._ready(dim, gate_set):
                raw_predictions[dim] = None
                continue
            if self._ready("abstention_flag", self.gates.abstention) and (
                self.abstention.should_abstain(subject, recordings, context, dim)
            ):
                raw_predictions[dim] = None
                any_abstain = True
                continue
            raw = decoder.decode(subject, recordings, context)
            raw_predictions[dim] = raw
            if raw is not None and self._ready("confidence", self.gates.calibration):
                confidence[dim] = self.calibration.calibrate(subject, dim, raw)

        if any_abstain:
            for dim in list(raw_predictions):
                raw_predictions[dim] = None
            confidence = {}

        return Thought(
            subject=subject,
            perceived_stimulus=raw_predictions["perceived_stimulus"],
            predicted_affect=raw_predictions["predicted_affect"],
            predicted_decision=raw_predictions["predicted_decision"],
            predicted_memory_state=raw_predictions["predicted_memory_state"],
            predicted_reward_signal=raw_predictions["predicted_reward_signal"],
            confidence=confidence,
            abstention_flag=any_abstain,
            unmeasured_domains=list(COGNITIVE_DARK_MATTER_DOMAINS),
            is_subject_specific=subject_specific,
        )

    @staticmethod
    def _ready(field_name: str, passed: set[str]) -> bool:
        required = FIELD_GATES.get(field_name, [])
        return bool(required) and all(g in passed for g in required)
