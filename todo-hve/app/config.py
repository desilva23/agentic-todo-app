"""Settings, read from the environment (and a local .env file) at the moment they are used,
so a test can change a setting without reloading any module."""

import math
import os
from typing import Optional

from dotenv import load_dotenv

# Load .env once; values already in the real environment win.
load_dotenv()

DEFAULT_DB_PATH = "todos.db"


def get_db_path() -> str:
    """Where the todos are saved."""
    value = os.environ.get("TODO_DB_PATH", "").strip()
    return value or DEFAULT_DB_PATH


DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"
DEFAULT_GROQ_TIMEOUT = 15


def get_groq_api_key() -> Optional[str]:
    """The Groq key, or None when it is not set (a blank value counts as not set)."""
    value = os.environ.get("GROQ_API_KEY", "").strip()
    return value or None


def get_groq_model() -> str:
    """Which Groq model to use. It is a setting, not a constant."""
    return os.environ.get("GROQ_MODEL", "").strip() or DEFAULT_GROQ_MODEL


def get_groq_timeout() -> float:
    """Seconds to wait for one model call. A value that is not a positive number falls back to 15."""
    try:
        seconds = float(os.environ.get("GROQ_TIMEOUT_SECONDS", ""))
    except ValueError:
        return DEFAULT_GROQ_TIMEOUT
    if not math.isfinite(seconds) or seconds <= 0:
        return DEFAULT_GROQ_TIMEOUT
    return seconds
