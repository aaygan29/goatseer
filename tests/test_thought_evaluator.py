import unittest

from thought_evaluator import evaluate_thought_text


class ThoughtEvaluatorTests(unittest.TestCase):
    def test_requires_consent(self):
        with self.assertRaises(PermissionError):
            evaluate_thought_text("I feel great", consent=False)

    def test_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            evaluate_thought_text("   ", consent=True)

    def test_positive_sentiment(self):
        result = evaluate_thought_text("I feel happy and grateful today", consent=True)

        self.assertEqual(result.sentiment, "positive")
        self.assertGreater(result.score, 0)

    def test_counts_repeated_words(self):
        result = evaluate_thought_text("happy happy sad", consent=True)

        self.assertEqual(result.matched_positive_words, 2)
        self.assertEqual(result.matched_negative_words, 1)
        self.assertEqual(result.score, 1)

    def test_negative_sentiment(self):
        result = evaluate_thought_text("I am upset and anxious", consent=True)

        self.assertEqual(result.sentiment, "negative")
        self.assertLess(result.score, 0)


if __name__ == "__main__":
    unittest.main()
