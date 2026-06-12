"""Emotion detection client used by the Flask application.

The primary backend calls the Watson NLP endpoint required by the course.
A small deterministic local backend is included only so that the Docker
project can be demonstrated outside the Skills Network environment.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

import requests

EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")
DEFAULT_API_URL = (
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
DEFAULT_MODEL_ID = "emotion_aggregated-workflow_lang_en_stock"


class EmotionDetectionError(RuntimeError):
    """Raised when an emotion backend cannot return a valid result."""


def _empty_result() -> dict[str, float | str | None]:
    """Return the response structure required for invalid input."""
    return {
        "anger": None,
        "disgust": None,
        "fear": None,
        "joy": None,
        "sadness": None,
        "dominant_emotion": None,
    }


def _format_result(scores: Mapping[str, Any]) -> dict[str, float | str | None]:
    """Normalize emotion scores and determine the dominant emotion."""
    normalized_scores: dict[str, float] = {}

    for emotion in EMOTIONS:
        try:
            normalized_scores[emotion] = float(scores[emotion])
        except (KeyError, TypeError, ValueError) as exc:
            raise EmotionDetectionError(
                f"The backend response does not contain a valid '{emotion}' score."
            ) from exc

    dominant_emotion = max(normalized_scores, key=normalized_scores.get)
    return {**normalized_scores, "dominant_emotion": dominant_emotion}


def _extract_scores(response_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Extract the emotion score object from a Watson NLP response."""
    try:
        predictions = response_payload["emotionPredictions"]
        first_prediction = predictions[0]
        scores = first_prediction["emotion"]
    except (KeyError, IndexError, TypeError) as exc:
        raise EmotionDetectionError(
            "The Watson NLP response has an unexpected structure."
        ) from exc

    if not isinstance(scores, Mapping):
        raise EmotionDetectionError("The Watson NLP emotion value is not an object.")

    return scores


def _watson_emotion_detector(
    text_to_analyze: str,
) -> dict[str, float | str | None]:
    """Call the Watson NLP EmotionPredict service."""
    api_url = os.getenv("EMOTION_API_URL", DEFAULT_API_URL)
    model_id = os.getenv("EMOTION_MODEL_ID", DEFAULT_MODEL_ID)
    timeout_seconds = float(os.getenv("EMOTION_API_TIMEOUT", "20"))

    payload = {"raw_document": {"text": text_to_analyze}}
    headers = {"grpc-metadata-mm-model-id": model_id}

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        raise EmotionDetectionError(
            "The Watson NLP emotion service could not be reached."
        ) from exc

    if response.status_code == 400:
        return _empty_result()

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise EmotionDetectionError(
            f"Watson NLP returned HTTP status {response.status_code}."
        ) from exc

    try:
        response_payload = response.json()
    except requests.JSONDecodeError as exc:
        raise EmotionDetectionError(
            "Watson NLP returned a response that is not valid JSON."
        ) from exc

    return _format_result(_extract_scores(response_payload))


_LOCAL_LEXICON: dict[str, set[str]] = {
    "anger": {
        "angry",
        "annoyed",
        "furious",
        "hate",
        "mad",
        "outraged",
        "rage",
    },
    "disgust": {
        "disgust",
        "disgusted",
        "disgusting",
        "gross",
        "nasty",
        "repulsed",
        "revolting",
    },
    "fear": {
        "afraid",
        "anxious",
        "fear",
        "frightened",
        "scared",
        "terrified",
        "worried",
    },
    "joy": {
        "delighted",
        "enjoy",
        "fun",
        "glad",
        "happy",
        "joy",
        "love",
        "pleased",
    },
    "sadness": {
        "depressed",
        "down",
        "miserable",
        "sad",
        "sadness",
        "unhappy",
        "upset",
    },
}


def _local_emotion_detector(
    text_to_analyze: str,
) -> dict[str, float | str | None]:
    """Return deterministic scores for local development and offline tests."""
    words = re.findall(r"[a-zA-Z']+", text_to_analyze.lower())
    matches = {
        emotion: sum(word in emotion_words for word in words)
        for emotion, emotion_words in _LOCAL_LEXICON.items()
    }
    total_matches = sum(matches.values())

    if total_matches == 0:
        return _empty_result()

    # Keep every score numeric while making matched emotions clearly dominant.
    baseline = 0.01
    available_probability = 1.0 - baseline * len(EMOTIONS)
    scores = {
        emotion: baseline + available_probability * count / total_matches
        for emotion, count in matches.items()
    }
    return _format_result(scores)


def emotion_detector(text_to_analyze: str) -> dict[str, float | str | None]:
    """Analyze text and return five emotion scores plus the dominant emotion.

    ``EMOTION_BACKEND`` accepts:
    - ``watson``: use only Watson NLP (course-compatible behavior);
    - ``local``: use the deterministic offline development backend;
    - ``auto``: try Watson NLP first and use the local backend if unavailable.
    """
    if not isinstance(text_to_analyze, str) or not text_to_analyze.strip():
        return _empty_result()

    backend = os.getenv("EMOTION_BACKEND", "watson").strip().lower()

    if backend == "local":
        return _local_emotion_detector(text_to_analyze)

    if backend == "watson":
        return _watson_emotion_detector(text_to_analyze)

    if backend == "auto":
        try:
            return _watson_emotion_detector(text_to_analyze)
        except EmotionDetectionError:
            return _local_emotion_detector(text_to_analyze)

    raise EmotionDetectionError(
        "EMOTION_BACKEND must be one of: watson, local, auto."
    )
