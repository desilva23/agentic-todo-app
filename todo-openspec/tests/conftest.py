import pytest

from app import storage


@pytest.fixture(autouse=True)
def no_real_groq_settings(monkeypatch):
    """config.py loads .env, which may hold a real key. Remove it for every test so a test
    can never reach the real Groq by accident. Tests that need a key set a fake one."""
    for name in ("GROQ_API_KEY", "GROQ_MODEL", "GROQ_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Give every test its own empty database file."""
    path = tmp_path / "test_todos.db"
    monkeypatch.setenv("TODO_DB_PATH", str(path))
    storage.init_db()
    return path
