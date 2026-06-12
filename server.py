"""Flask web server for the Emotion Detection final project."""

from flask import Flask, Response, render_template, request

from EmotionDetection import EmotionDetectionError, emotion_detector

app = Flask(__name__)


@app.get("/")
def index() -> str:
    """Render the supplied Emotion Detection interface."""
    return render_template("index.html")


@app.get("/emotionDetector")
def detect_emotion() -> Response:
    """Analyze the text passed in the textToAnalyze query parameter."""
    text_to_analyze = request.args.get("textToAnalyze", "")

    try:
        result = emotion_detector(text_to_analyze)
    except EmotionDetectionError as exc:
        return Response(
            f"Emotion detection service unavailable: {exc}",
            status=503,
            mimetype="text/plain",
        )

    if result["dominant_emotion"] is None:
        return Response(
            "Invalid text! Please try again!",
            status=200,
            mimetype="text/plain",
        )

    message = (
        "For the given statement, the system response is "
        f"'anger': {result['anger']}, "
        f"'disgust': {result['disgust']}, "
        f"'fear': {result['fear']}, "
        f"'joy': {result['joy']} and "
        f"'sadness': {result['sadness']}. "
        f"The dominant emotion is {result['dominant_emotion']}."
    )
    return Response(message, status=200, mimetype="text/plain")


@app.get("/health")
def health() -> Response:
    """Return a lightweight health-check response for Docker."""
    return Response("ok", status=200, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
