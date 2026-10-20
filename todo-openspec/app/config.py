import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_PATH = "todos.db"
DEFAULT_GROQ_TIMEOUT_SECONDS = 15.0
# Chosen from the models listed for the project's key; fast, accurate on the todo prompts.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"


def get_db_path() -> str:
    """Return the SQLite file path, read at call time so tests can override it."""
    return os.environ.get("TODO_DB_PATH", DEFAULT_DB_PATH)


def get_groq_api_key() -> Optional[str]:
    """The Groq key, or None when it is missing or blank. Never log or return this value."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    return key or None


def get_groq_model() -> str:
    return os.environ.get("GROQ_MODEL", "").strip() or DEFAULT_GROQ_MODEL


def get_groq_timeout() -> float:
    """Seconds to wait for Groq. Falls back to the default if unset or not a positive number."""
    raw = os.environ.get("GROQ_TIMEOUT_SECONDS", "").strip()
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_GROQ_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_GROQ_TIMEOUT_SECONDS
