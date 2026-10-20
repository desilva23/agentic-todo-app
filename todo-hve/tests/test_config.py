import pytest

from app import config


def test_given_no_setting_when_getting_db_path_then_returns_default(monkeypatch):
    # Arrange
    monkeypatch.delenv("TODO_DB_PATH", raising=False)

    # Act
    path = config.get_db_path()

    # Assert
    assert path == "todos.db"


def test_given_setting_when_getting_db_path_then_returns_it(monkeypatch):
    # Arrange
    monkeypatch.setenv("TODO_DB_PATH", "/tmp/other.db")

    # Act
    path = config.get_db_path()

    # Assert
    assert path == "/tmp/other.db"


def test_given_blank_setting_when_getting_db_path_then_returns_default(monkeypatch):
    # Arrange
    monkeypatch.setenv("TODO_DB_PATH", "   ")

    # Act
    path = config.get_db_path()

    # Assert
    assert path == "todos.db"


def test_given_setting_changed_later_when_getting_db_path_then_reads_the_new_value(monkeypatch):
    # Arrange
    monkeypatch.setenv("TODO_DB_PATH", "first.db")
    config.get_db_path()

    # Act
    monkeypatch.setenv("TODO_DB_PATH", "second.db")

    # Assert
    assert config.get_db_path() == "second.db"


def test_given_no_key_when_getting_the_groq_key_then_it_is_missing():
    # Arrange / Act / Assert
    assert config.get_groq_api_key() is None


def test_given_a_blank_key_when_getting_the_groq_key_then_it_counts_as_missing(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", "   ")

    # Act / Assert
    assert config.get_groq_api_key() is None


def test_given_a_key_when_getting_the_groq_key_then_it_is_returned_trimmed(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", " fake-key ")

    # Act / Assert
    assert config.get_groq_api_key() == "fake-key"


def test_given_no_model_setting_when_getting_the_model_then_the_default_is_used():
    # Arrange / Act / Assert
    assert config.get_groq_model() == "openai/gpt-oss-20b"


def test_given_a_model_setting_when_getting_the_model_then_it_is_used(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_MODEL", "some/model")

    # Act / Assert
    assert config.get_groq_model() == "some/model"


def test_given_no_timeout_setting_when_getting_the_timeout_then_it_is_15_seconds():
    # Arrange / Act / Assert
    assert config.get_groq_timeout() == 15


@pytest.mark.parametrize("value", ["abc", "", "0", "-3", "nan", "inf"])
def test_given_an_unusable_timeout_when_getting_the_timeout_then_it_falls_back_to_15(monkeypatch, value):
    # Arrange
    monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", value)

    # Act / Assert
    assert config.get_groq_timeout() == 15


@pytest.mark.parametrize("value, expected", [("9", 9.0), ("2.5", 2.5)])
def test_given_a_valid_timeout_when_getting_the_timeout_then_it_is_used(monkeypatch, value, expected):
    # Arrange
    monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", value)

    # Act / Assert
    assert config.get_groq_timeout() == expected
