"""Unit tests required by the Emotion Detection final project."""

import os
import unittest

from EmotionDetection import emotion_detector


class TestEmotionDetector(unittest.TestCase):
    """Validate the dominant emotion for the five required statements."""

    @classmethod
    def setUpClass(cls) -> None:
        """Use the deterministic backend so unit tests do not require a network."""
        cls.previous_backend = os.environ.get("EMOTION_BACKEND")
        os.environ["EMOTION_BACKEND"] = "local"

    @classmethod
    def tearDownClass(cls) -> None:
        """Restore the environment after the tests finish."""
        if cls.previous_backend is None:
            os.environ.pop("EMOTION_BACKEND", None)
        else:
            os.environ["EMOTION_BACKEND"] = cls.previous_backend

    def test_joy(self) -> None:
        """The statement must be classified as joy."""
        result = emotion_detector("I am glad this happened")
        self.assertEqual(result["dominant_emotion"], "joy")

    def test_anger(self) -> None:
        """The statement must be classified as anger."""
        result = emotion_detector("I am really mad about this")
        self.assertEqual(result["dominant_emotion"], "anger")

    def test_disgust(self) -> None:
        """The statement must be classified as disgust."""
        result = emotion_detector("I feel disgusted just hearing about this")
        self.assertEqual(result["dominant_emotion"], "disgust")

    def test_sadness(self) -> None:
        """The statement must be classified as sadness."""
        result = emotion_detector("I am so sad about this")
        self.assertEqual(result["dominant_emotion"], "sadness")

    def test_fear(self) -> None:
        """The statement must be classified as fear."""
        result = emotion_detector("I am really afraid that this will happen")
        self.assertEqual(result["dominant_emotion"], "fear")

    def test_blank_input(self) -> None:
        """Blank input must return None for every output field."""
        result = emotion_detector("")
        self.assertTrue(all(value is None for value in result.values()))


if __name__ == "__main__":
    unittest.main()
