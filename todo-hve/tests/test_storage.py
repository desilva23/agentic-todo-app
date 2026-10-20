import sqlite3
from contextlib import closing

import pytest

from app import storage

HUGE_ID = 99999999999999999999  # above 2**63 - 1, which SQLite cannot store


def make(title="Task", **fields):
    return storage.create_todo({"title": title, "description": None, "due_date": None, "priority": "medium", **fields})


def test_given_only_a_title_when_creating_then_defaults_and_server_fields_are_filled(db_path):
    # Arrange / Act
    todo = storage.create_todo({"title": "Buy milk"})

    # Assert
    assert (todo["id"], todo["title"], todo["priority"], todo["completed"]) == (1, "Buy milk", "medium", False)
    assert todo["description"] is None and todo["due_date"] is None and todo["created_at"]


def test_given_all_fields_when_creating_then_they_are_stored(db_path):
    # Arrange / Act
    todo = make("Call mom", description="about dinner", due_date="2026-10-23T17:00:00", priority="high")

    # Assert
    assert storage.get_todo(todo["id"]) == todo
    assert (todo["description"], todo["due_date"], todo["priority"]) == ("about dinner", "2026-10-23T17:00:00", "high")


def test_given_a_title_with_sql_characters_when_creating_then_it_is_stored_verbatim(db_path):
    # Arrange
    title = "Robert'); DROP TABLE todos;--"

    # Act
    todo = make(title)

    # Assert
    assert storage.get_todo(todo["id"])["title"] == title


def test_given_no_such_id_when_getting_then_returns_none(db_path):
    # Arrange / Act / Assert
    assert storage.get_todo(42) is None


def test_given_several_todos_when_listing_then_all_come_back_oldest_first(db_path):
    # Arrange
    for name in ("a", "b", "c"):
        make(name)

    # Act
    titles = [t["title"] for t in storage.list_todos()]

    # Assert
    assert titles == ["a", "b", "c"]


def test_given_active_and_completed_when_filtering_by_status_then_only_that_status_returns(db_path):
    # Arrange
    done = make("done")
    make("open")
    storage.update_todo(done["id"], {"completed": True})

    # Act
    completed = [t["title"] for t in storage.list_todos(status="completed")]
    active = [t["title"] for t in storage.list_todos(status="active")]

    # Assert
    assert (completed, active) == (["done"], ["open"])


def test_given_mixed_priorities_when_filtering_by_priority_then_only_that_priority_returns(db_path):
    # Arrange
    make("lo", priority="low")
    make("hi", priority="high")

    # Act
    titles = [t["title"] for t in storage.list_todos(priority="high")]

    # Assert
    assert titles == ["hi"]


def test_given_status_and_priority_together_when_filtering_then_both_apply(db_path):
    # Arrange
    a = make("a", priority="high")
    make("b", priority="high")
    make("c", priority="low")
    storage.update_todo(a["id"], {"completed": True})

    # Act
    titles = [t["title"] for t in storage.list_todos(status="active", priority="high")]

    # Assert
    assert titles == ["b"]


def test_given_a_partial_change_when_updating_then_other_fields_stay(db_path):
    # Arrange
    todo = make("keep", description="d", due_date="2026-10-23T17:00:00", priority="low")

    # Act
    updated = storage.update_todo(todo["id"], {"priority": "high"})

    # Assert
    assert (updated["title"], updated["description"], updated["due_date"], updated["priority"]) == (
        "keep", "d", "2026-10-23T17:00:00", "high")


def test_given_a_due_date_when_updating_it_to_none_then_it_is_cleared(db_path):
    # Arrange
    todo = make("x", due_date="2026-10-23T17:00:00")

    # Act
    updated = storage.update_todo(todo["id"], {"due_date": None})

    # Assert
    assert updated["due_date"] is None


def test_given_an_active_todo_when_completed_and_reopened_then_status_follows(db_path):
    # Arrange
    todo = make("x")

    # Act
    done = storage.update_todo(todo["id"], {"completed": True})
    reopened = storage.update_todo(todo["id"], {"completed": False})

    # Assert
    assert (done["completed"], reopened["completed"]) == (True, False)


def test_given_no_such_todo_when_updating_then_returns_none(db_path):
    # Arrange / Act / Assert
    assert storage.update_todo(42, {"title": "x"}) is None


def test_given_a_column_that_may_not_change_when_updating_then_it_is_refused(db_path):
    # Arrange
    todo = make("x")

    # Act / Assert
    with pytest.raises(ValueError):
        storage.update_todo(todo["id"], {"id; DROP TABLE todos": 1})


def test_given_an_existing_todo_when_deleting_then_it_is_gone(db_path):
    # Arrange
    todo = make("x")

    # Act
    removed = storage.delete_todo(todo["id"])

    # Assert
    assert removed is True and storage.get_todo(todo["id"]) is None


def test_given_no_such_todo_when_deleting_then_returns_false(db_path):
    # Arrange / Act / Assert
    assert storage.delete_todo(42) is False


@pytest.mark.parametrize("bad_id", [HUGE_ID, 2**63, 0, -1])
def test_given_an_id_that_can_never_exist_when_using_it_then_it_is_simply_not_found(db_path, bad_id):
    # Arrange / Act
    results = (storage.get_todo(bad_id), storage.update_todo(bad_id, {"title": "x"}), storage.delete_todo(bad_id))

    # Assert
    assert results == (None, None, False)


def test_given_the_largest_possible_id_when_getting_then_it_is_a_normal_miss(db_path):
    # Arrange / Act / Assert
    assert storage.get_todo(2**63 - 1) is None


def test_given_saved_todos_when_the_app_restarts_then_they_are_still_there(db_path):
    # Arrange
    make("survivor")

    # Act (a restart runs the start-up step again against the same file)
    storage.init_db()

    # Assert
    assert [t["title"] for t in storage.list_todos()] == ["survivor"]


def test_given_saved_todos_when_reading_the_file_directly_then_the_rows_are_on_disk(db_path):
    # Arrange
    make("on disk")

    # Act
    with closing(sqlite3.connect(db_path)) as conn:
        count = conn.execute("SELECT COUNT(*) FROM todos").fetchone()[0]

    # Assert
    assert count == 1


@pytest.mark.parametrize("operation", [
    lambda: storage.init_db(),
    lambda: storage.create_todo({"title": "x"}),
    lambda: storage.get_todo(1),
    lambda: storage.list_todos(),
    lambda: storage.update_todo(1, {"title": "y"}),
    lambda: storage.delete_todo(1),
])
def test_given_any_storage_operation_when_it_finishes_then_its_database_connection_is_closed(db_path, mocker, operation):
    # Arrange
    opened = []
    real_connect = sqlite3.connect

    def recording_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        opened.append(conn)
        return conn

    storage.create_todo({"title": "seed"})
    mocker.patch.object(sqlite3, "connect", side_effect=recording_connect)

    # Act
    operation()

    # Assert: a closed connection refuses any further use
    assert opened, "the operation should have opened a connection"
    for conn in opened:
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")
