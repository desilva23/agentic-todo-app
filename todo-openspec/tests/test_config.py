import pytest

from app import config


def test_default_db_path(monkeypatch):
    monkeypatch.delenv("TODO_DB_PATH", raising=False)
    assert config.get_db_path() == "todos.db"


def test_db_path_can_be_overridden(monkeypatch):
    monkeypatch.setenv("TODO_DB_PATH", "/tmp/other.db")
    assert config.get_db_path() == "/tmp/other.db"


def test_unset_or_blank_groq_key_is_none(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert config.get_groq_api_key() is None
    monkeypatch.setenv("GROQ_API_KEY", "   ")
    assert config.get_groq_api_key() is None


def test_groq_key_can_be_set_and_is_trimmed(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "  fake-key-for-test \n")
    assert config.get_groq_api_key() == "fake-key-for-test"


def test_groq_model_setting(monkeypatch):
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    assert config.get_groq_model() == config.DEFAULT_GROQ_MODEL
    monkeypatch.setenv("GROQ_MODEL", "  ")
    assert config.get_groq_model() == config.DEFAULT_GROQ_MODEL
    monkeypatch.setenv("GROQ_MODEL", "some-model")
    assert config.get_groq_model() == "some-model"


@pytest.mark.parametrize("raw, expected", [
    (None, 15.0),
    ("", 15.0),
    ("abc", 15.0),
    ("0", 15.0),
    ("-3", 15.0),
    ("30", 30.0),
    ("7.5", 7.5),
])
def test_groq_timeout(monkeypatch, raw, expected):
    if raw is None:
        monkeypatch.delenv("GROQ_TIMEOUT_SECONDS", raising=False)
    else:
        monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", raw)
    assert config.get_groq_timeout() == expected
