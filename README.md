# Final project

Dockerized Flask application for the **AI-Based Web Application Development and Deployment** final project. It analyzes English text and returns scores for anger, disgust, fear, joy, and sadness, together with the dominant emotion.

## Project structure

```text
.
+-- EmotionDetection/
¦   +-- __init__.py
¦   +-- emotion_detection.py
+-- static/
¦   +-- mywebscript.js
+-- templates/
¦   +-- index.html
+-- .dockerignore
+-- .env.example
+-- .gitignore
+-- .pylintrc
+-- compose.yaml
+-- Dockerfile
+-- requirements-dev.txt
+-- requirements.txt
+-- server.py
+-- test_emotion_detection.py
+-- test_server.py
```

## Start with Docker Compose

```bash
docker compose up --build
```

Open:

```text
http://localhost:5000
```

Stop the application:

```bash
docker compose down
```

## Backend modes

The course endpoint is designed for the Skills Network environment. The Docker configuration therefore starts with `EMOTION_BACKEND=auto`:

1. It tries the Watson NLP endpoint required by the project.
2. If that endpoint is unreachable, it uses a deterministic local development fallback so the interface remains testable.

Use strict course behavior:

```bash
EMOTION_BACKEND=watson docker compose up --build
```

Use only the offline development backend:

```bash
EMOTION_BACKEND=local docker compose up --build
```

On Windows PowerShell:

```powershell
$env:EMOTION_BACKEND="local"
docker compose up --build
```

## Run tests

The test suite switches to the local deterministic backend and does not require internet access.

```bash
docker compose run --rm emotion-detection \
  python -m unittest -v test_emotion_detection.py test_server.py
```

## Run Pylint

```bash
docker compose run --rm emotion-detection sh -c \
  "python -m pip install -r requirements-dev.txt && pylint server.py EmotionDetection test_emotion_detection.py test_server.py"
```

## Run without Docker

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
EMOTION_BACKEND=local python server.py
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
$env:EMOTION_BACKEND="local"
python server.py
```
