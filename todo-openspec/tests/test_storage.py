from app import storage


def test_first_start_returns_empty_list(tmp_path, monkeypatch):
    """Spec: storage is created automatically on first start."""
    path = tmp_path / "does_not_exist_yet.db"
    monkeypatch.setenv("TODO_DB_PATH", str(path))
    assert not path.exists()
    storage.init_db()
    assert path.exists()
    assert storage.list_todos() == []


def test_init_db_is_safe_to_repeat(db_path):
    storage.create_todo("Keep me")
    storage.init_db()
    assert len(storage.list_todos()) == 1


def test_create_with_defaults(db_path):
    todo = storage.create_todo("Buy milk")
    assert todo["id"] >= 1
    assert todo["title"] == "Buy milk"
    assert todo["priority"] == "medium"
    assert todo["completed"] is False
    assert todo["description"] is None
    assert todo["due_date"] is None


def test_create_with_all_fields(db_path):
    todo = storage.create_todo("Pay rent", "March rent", "2026-03-01T09:00:00", "high")
    assert todo["description"] == "March rent"
    assert todo["due_date"] == "2026-03-01T09:00:00"
    assert todo["priority"] == "high"


def test_get_existing_and_unknown(db_path):
    created = storage.create_todo("A")
    assert storage.get_todo(created["id"])["title"] == "A"
    assert storage.get_todo(9999) is None


def test_list_filters(db_path):
    a = storage.create_todo("A", priority="high")
    storage.create_todo("B", priority="low")
    c = storage.create_todo("C", priority="high")
    storage.update_todo(c["id"], {"completed": True})

    assert [t["title"] for t in storage.list_todos()] == ["A", "B", "C"]
    assert [t["title"] for t in storage.list_todos(status="completed")] == ["C"]
    assert [t["title"] for t in storage.list_todos(status="active")] == ["A", "B"]
    assert [t["title"] for t in storage.list_todos(priority="high")] == ["A", "C"]
    assert [t["title"] for t in storage.list_todos("active", "high")] == ["A"]
    assert a["id"] != c["id"]


def test_update_changes_only_given_fields(db_path):
    todo = storage.create_todo("Old", priority="low")
    updated = storage.update_todo(todo["id"], {"title": "New"})
    assert updated["title"] == "New"
    assert updated["priority"] == "low"


def test_update_can_clear_due_date(db_path):
    todo = storage.create_todo("A", due_date="2026-03-01T09:00:00")
    updated = storage.update_todo(todo["id"], {"due_date": None})
    assert updated["due_date"] is None


def test_update_complete_and_reopen(db_path):
    todo = storage.create_todo("A")
    assert storage.update_todo(todo["id"], {"completed": True})["completed"] is True
    assert storage.update_todo(todo["id"], {"completed": False})["completed"] is False


def test_update_unknown_id_returns_none(db_path):
    assert storage.update_todo(9999, {"title": "x"}) is None


def test_update_ignores_unknown_columns(db_path):
    todo = storage.create_todo("A")
    updated = storage.update_todo(todo["id"], {"id": 500, "title; DROP TABLE todos": "x"})
    assert updated["id"] == todo["id"]
    assert len(storage.list_todos()) == 1


def test_delete(db_path):
    todo = storage.create_todo("A")
    assert storage.delete_todo(todo["id"]) is True
    assert storage.get_todo(todo["id"]) is None
    assert storage.delete_todo(todo["id"]) is False


def test_titles_with_quotes_are_stored_safely(db_path):
    nasty = "Robert'); DROP TABLE todos;--"
    todo = storage.create_todo(nasty)
    assert storage.get_todo(todo["id"])["title"] == nasty


def test_unexpected_database_error_leaves_data_unchanged(db_path):
    """Spec: an unexpected error while handling a request must not damage saved todos."""
    import sqlite3

    import pytest

    todo = storage.create_todo("Original", priority="low")
    with pytest.raises(sqlite3.Error):
        # The second value cannot be stored by SQLite, so the write fails part-way.
        storage.update_todo(todo["id"], {"title": "Changed", "priority": object()})
    assert storage.get_todo(todo["id"]) == todo


def test_ids_outside_the_database_range_do_not_exist(db_path):
    huge = 99999999999999999999
    assert storage.get_todo(huge) is None
    assert storage.update_todo(huge, {"title": "x"}) is None
    assert storage.delete_todo(huge) is False


def test_data_survives_restart(db_path, monkeypatch):
    """Spec: todos survive a restart. A restart = init_db again with a fresh connection."""
    first = storage.create_todo("Stay", "kept", "2026-03-01T09:00:00", "high")
    storage.create_todo("Other")
    storage.create_todo("Third")

    storage.init_db()  # the app starting again
    todos = storage.list_todos()
    assert len(todos) == 3
    assert storage.get_todo(first["id"]) == first


def test_deleted_stays_deleted_after_restart(db_path):
    todo = storage.create_todo("Gone")
    storage.delete_todo(todo["id"])
    storage.init_db()
    assert storage.get_todo(todo["id"]) is None
