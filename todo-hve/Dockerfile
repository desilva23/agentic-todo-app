# Container image for Google Cloud Run. Only the app code goes in: no .env, no tests, no docs.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TODO_DB_PATH=/tmp/todos.db

WORKDIR /app

# Install the runtime packages only (the test and coverage tools are not needed in the image).
COPY requirements.txt .
RUN grep -viE '^(pytest|coverage)' requirements.txt > requirements-runtime.txt \
    && pip install -r requirements-runtime.txt

COPY app ./app
COPY static ./static

# Run as a normal user, not root.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Cloud Run tells the app which port to use through the PORT variable (8080 by default).
EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
