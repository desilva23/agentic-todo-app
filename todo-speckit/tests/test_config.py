import pytest

from app import config


def test_default_db_path_is_todos_db(monkeypatch):
    monkeypatch.delenv("TODO_DB_PATH", raising=False)
    assert config.get_db_path() == "todos.db"


def test_db_path_is_read_at_call_time_so_it_can_be_overridden(monkeypatch):
    monkeypatch.setenv("TODO_DB_PATH", "/tmp/other.db")
    assert config.get_db_path() == "/tmp/other.db"
    monkeypatch.setenv("TODO_DB_PATH", "/tmp/another.db")
    assert config.get_db_path() == "/tmp/another.db"  # no module reload needed


def test_tests_never_see_a_provider_key():
    """Constitution IV: a real key in the environment must not be visible to any test, so a test
    can never reach a real provider by accident (conftest.py strips these for every test)."""
    import os

    for name in ("GROQ_API_KEY", "GROQ_MODEL", "GROQ_TIMEOUT_SECONDS"):
        assert name not in os.environ


# --- AI assistant settings (feature 002) ---------------------------------------------------

def test_a_missing_blank_or_spaces_only_groq_key_counts_as_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert config.get_groq_api_key() is None
    for blank in ("", "   "):
        monkeypatch.setenv("GROQ_API_KEY", blank)
        assert config.get_groq_api_key() is None


def test_the_groq_key_is_trimmed(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "  fake-key-for-test \n")
    assert config.get_groq_api_key() == "fake-key-for-test"


def test_the_groq_model_defaults_when_unset_or_blank(monkeypatch):
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    assert config.get_groq_model() == "openai/gpt-oss-20b"
    monkeypatch.setenv("GROQ_MODEL", "  ")
    assert config.get_groq_model() == "openai/gpt-oss-20b"
    monkeypatch.setenv("GROQ_MODEL", "some-model")
    assert config.get_groq_model() == "some-model"


@pytest.mark.parametrize("raw, expected", [
    (None, 15.0), ("", 15.0), ("abc", 15.0), ("0", 15.0), ("-3", 15.0), ("30", 30.0), ("7.5", 7.5),
])
def test_the_groq_timeout_falls_back_to_15_when_invalid(monkeypatch, raw, expected):
    if raw is None:
        monkeypatch.delenv("GROQ_TIMEOUT_SECONDS", raising=False)
    else:
        monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", raw)
    assert config.get_groq_timeout() == expected


def test_groq_settings_are_read_at_call_time(monkeypatch):
    monkeypatch.setenv("GROQ_MODEL", "first")
    assert config.get_groq_model() == "first"
    monkeypatch.setenv("GROQ_MODEL", "second")
    assert config.get_groq_model() == "second"
