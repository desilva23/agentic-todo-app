import pytest

from app import storage


@pytest.fixture(autouse=True)
def no_provider_settings(monkeypatch):
    """Remove any AI-provider settings from the environment for every test (constitution IV), so
    a test can never reach a real provider by accident, whatever the developer's shell holds."""
    for name in ("GROQ_API_KEY", "GROQ_MODEL", "GROQ_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Give every test its own empty database file, so tests never share or touch real data."""
    path = tmp_path / "test_todos.db"
    monkeypatch.setenv("TODO_DB_PATH", str(path))
    storage.init_db()
    return path
