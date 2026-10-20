import sqlite3

import pytest

from app import storage


def tables_in(path):
    with sqlite3.connect(path) as conn:
        return [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]


def test_first_start_creates_the_file_and_the_todos_table(tmp_path, monkeypatch):
    path = tmp_path / "new.db"
    monkeypatch.setenv("TODO_DB_PATH", str(path))
    assert not path.exists()
    storage.init_db()
    assert path.exists()
    assert "todos" in tables_in(path)
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM todos").fetchone()[0] == 0


def test_init_db_twice_is_safe_and_keeps_existing_rows(tmp_path, monkeypatch):
    path = tmp_path / "again.db"
    monkeypatch.setenv("TODO_DB_PATH", str(path))
    storage.init_db()
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT INTO todos (title, priority, completed, created_at) VALUES ('Keep me', 'low', 0, 'now')")
    storage.init_db()
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT title FROM todos").fetchall() == [("Keep me",)]


# --- create / get / list (User Story 1) ---------------------------------------------------

def test_create_with_defaults(db_path):
    todo = storage.create_todo("Buy milk")
    assert todo["id"] >= 1
    assert todo["title"] == "Buy milk"
    assert todo["priority"] == "medium"
    assert todo["completed"] is False
    assert todo["description"] is None and todo["due_date"] is None
    assert todo["created_at"]  # set by the system


def test_create_with_every_field(db_path):
    todo = storage.create_todo("Pay rent", "March rent", "2026-03-01T09:00:00", "high")
    assert (todo["description"], todo["due_date"], todo["priority"]) == ("March rent", "2026-03-01T09:00:00", "high")


def test_get_returns_the_todo_or_none(db_path):
    created = storage.create_todo("A")
    assert storage.get_todo(created["id"]) == created
    assert storage.get_todo(9999) is None


def test_list_returns_todos_in_creation_order(db_path):
    for name in ("A", "B", "C"):
        storage.create_todo(name)
    assert [t["title"] for t in storage.list_todos()] == ["A", "B", "C"]


def test_a_title_that_looks_like_sql_is_stored_as_plain_text(db_path):
    nasty = "Robert'); DROP TABLE todos;--"
    todo = storage.create_todo(nasty)
    assert storage.get_todo(todo["id"])["title"] == nasty
    assert len(storage.list_todos()) == 1  # the table is still there


def test_data_survives_a_restart(db_path):
    first = storage.create_todo("Stay", "kept", "2026-03-01T09:00:00", "high")
    storage.create_todo("Other")
    storage.init_db()  # the app starting again
    assert len(storage.list_todos()) == 2
    assert storage.get_todo(first["id"]) == first


# --- update / delete and ids that cannot exist (User Story 2) ----------------------------------

HUGE_ID = 99999999999999999999  # above 2**63 - 1, which SQLite cannot store


def test_update_changes_only_the_given_columns(db_path):
    todo = storage.create_todo("Old", priority="low")
    updated = storage.update_todo(todo["id"], {"title": "New"})
    assert updated["title"] == "New" and updated["priority"] == "low"


def test_update_can_clear_the_due_date_and_description(db_path):
    todo = storage.create_todo("A", "notes", "2026-03-01T09:00:00")
    updated = storage.update_todo(todo["id"], {"due_date": None, "description": None})
    assert updated["due_date"] is None and updated["description"] is None


def test_complete_and_reopen(db_path):
    todo = storage.create_todo("A")
    assert storage.update_todo(todo["id"], {"completed": True})["completed"] is True
    assert storage.update_todo(todo["id"], {"completed": False})["completed"] is False


def test_update_ignores_columns_outside_the_allow_list(db_path):
    todo = storage.create_todo("A")
    updated = storage.update_todo(todo["id"], {"id": 500, "title; DROP TABLE todos": "x", "created_at": "hacked"})
    assert updated["id"] == todo["id"] and updated["created_at"] == todo["created_at"]
    assert len(storage.list_todos()) == 1


def test_unknown_ids_give_none_or_false(db_path):
    assert storage.update_todo(9999, {"title": "x"}) is None
    assert storage.delete_todo(9999) is False


def test_delete_removes_the_todo_and_it_stays_gone_after_a_restart(db_path):
    todo = storage.create_todo("A")
    assert storage.delete_todo(todo["id"]) is True
    assert storage.get_todo(todo["id"]) is None
    storage.init_db()
    assert storage.list_todos() == []


@pytest.mark.parametrize("bad_id", [0, -5, HUGE_ID])
def test_regression_ids_that_can_never_exist_are_simply_not_found(db_path, bad_id):
    """R-7: a huge id used to make SQLite raise an error (a server crash). It must mean 'not found'."""
    storage.create_todo("A")
    assert storage.get_todo(bad_id) is None
    assert storage.update_todo(bad_id, {"title": "x"}) is None
    assert storage.delete_todo(bad_id) is False


# --- filters (User Story 3) -------------------------------------------------------------------

def titles(todos):
    return [t["title"] for t in todos]


@pytest.fixture
def mixed(db_path):
    """A active/high, B active/low, C completed/high, D completed/medium."""
    storage.create_todo("A", priority="high")
    storage.create_todo("B", priority="low")
    c = storage.create_todo("C", priority="high")
    d = storage.create_todo("D", priority="medium")
    storage.update_todo(c["id"], {"completed": True})
    storage.update_todo(d["id"], {"completed": True})


def test_status_filter_all_active_completed(mixed):
    assert titles(storage.list_todos(status="all")) == ["A", "B", "C", "D"]
    assert titles(storage.list_todos(status="active")) == ["A", "B"]
    assert titles(storage.list_todos(status="completed")) == ["C", "D"]


def test_priority_filter(mixed):
    assert titles(storage.list_todos(priority="high")) == ["A", "C"]
    assert titles(storage.list_todos(priority="low")) == ["B"]


def test_both_filters_together(mixed):
    assert titles(storage.list_todos(status="active", priority="high")) == ["A"]
    assert titles(storage.list_todos(status="completed", priority="high")) == ["C"]


def test_a_filter_with_no_match_gives_an_empty_list_and_order_is_creation_order(mixed):
    assert storage.list_todos(status="active", priority="medium") == []
    assert titles(storage.list_todos(status="completed")) == sorted(titles(storage.list_todos(status="completed")))
