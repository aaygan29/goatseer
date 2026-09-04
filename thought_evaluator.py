"""Consent-based thought text evaluator.

This module does not read minds. It evaluates sentiment from text that a person
voluntarily provides.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict

POSITIVE_WORDS = {
    "good",
    "great",
    "happy",
    "love",
    "hopeful",
    "excited",
    "calm",
    "grateful",
}

NEGATIVE_WORDS = {
    "bad",
    "sad",
    "angry",
    "hate",
    "anxious",
    "afraid",
    "upset",
    "tired",
}


@dataclass(frozen=True)
class ThoughtEvaluation:
    sentiment: str
    score: int
    matched_positive_words: int
    matched_negative_words: int


def evaluate_thought_text(text: str, *, consent: bool) -> ThoughtEvaluation:
    """Evaluate sentiment from user-provided text.

    Args:
        text: A person's voluntarily shared thoughts.
        consent: Must be True to run evaluation.

    Returns:
        ThoughtEvaluation with a simple sentiment score.
    """
    if not consent:
        raise PermissionError("Explicit consent is required to evaluate thoughts.")

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Thought text cannot be empty.")

    words = [token.strip(".,!?;:\"'()[]{}").lower() for token in cleaned.split()]
    positive_matches = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_matches = sum(1 for word in words if word in NEGATIVE_WORDS)
    score = positive_matches - negative_matches

    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return ThoughtEvaluation(
        sentiment=sentiment,
        score=score,
        matched_positive_words=positive_matches,
        matched_negative_words=negative_matches,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate sentiment from voluntarily shared thought text. "
            "This tool does not read minds."
        )
    )
    parser.add_argument("--text", required=True, help="Thought text to evaluate")
    parser.add_argument(
        "--consent",
        action="store_true",
        help="Confirm the person explicitly consented to analysis",
    )
    args = parser.parse_args()

    try:
        result = evaluate_thought_text(args.text, consent=args.consent)
    except (PermissionError, ValueError) as exc:
        parser.error(str(exc))

    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
