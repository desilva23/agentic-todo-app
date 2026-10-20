import pytest


@pytest.fixture(autouse=True)
def no_provider_settings(monkeypatch):
    """Remove every AI-provider setting from the environment for every test, so a test can never
    reach a real provider by accident, whatever the developer's shell holds."""
    for name in ("GROQ_API_KEY", "GROQ_MODEL", "GROQ_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Give every test its own empty database file, so tests never share or touch real data."""
    from app import storage

    path = tmp_path / "test_todos.db"
    monkeypatch.setenv("TODO_DB_PATH", str(path))
    storage.init_db()
    return path
