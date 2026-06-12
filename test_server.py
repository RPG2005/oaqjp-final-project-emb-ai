"""Basic integration tests for the Flask routes."""

import os
import unittest

from server import app


class TestServer(unittest.TestCase):
    """Validate the HTML page, detector route, and blank-input handling."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configure the local backend for deterministic integration tests."""
        cls.previous_backend = os.environ.get("EMOTION_BACKEND")
        os.environ["EMOTION_BACKEND"] = "local"
        app.config.update(TESTING=True)
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls) -> None:
        """Restore the previous backend setting."""
        if cls.previous_backend is None:
            os.environ.pop("EMOTION_BACKEND", None)
        else:
            os.environ["EMOTION_BACKEND"] = cls.previous_backend

    def test_index(self) -> None:
        """The root route must render the supplied page."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NLP - Emotion Detection", response.data)

    def test_detector(self) -> None:
        """The detector route must report joy for the deployment phrase."""
        response = self.client.get(
            "/emotionDetector", query_string={"textToAnalyze": "I am having fun"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"dominant emotion is joy", response.data)

    def test_blank_detector(self) -> None:
        """The detector route must return the required invalid-text message."""
        response = self.client.get(
            "/emotionDetector", query_string={"textToAnalyze": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Invalid text! Please try again!")


if __name__ == "__main__":
    unittest.main()
