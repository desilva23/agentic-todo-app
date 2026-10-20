"""All SQLite access. Every query uses ? placeholders; column names come from fixed lists, never from input."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from app.config import get_db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS todos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT,
    due_date    TEXT,
    priority    TEXT    NOT NULL DEFAULT 'medium',
    completed   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL
)
"""

# Columns a caller may change. Names come from this fixed list, never from user input.
UPDATABLE_COLUMNS = ("title", "description", "due_date", "priority", "completed")

# SQLite integers are 64-bit. An id outside 1..MAX_ID can never exist, and handing one to SQLite raises
# an error, so such ids are treated as "not found" instead.
MAX_ID = 2**63 - 1


def _id_can_exist(todo_id: int) -> bool:
    return 0 < todo_id <= MAX_ID


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def _session():
    """One database connection for one operation: committed if it worked, rolled back if it failed, and
    always closed. (`with sqlite3.connect(...)` alone commits but never closes the connection.)"""
    conn = _connect()
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def _to_dict(row: sqlite3.Row) -> dict:
    todo = dict(row)
    todo["completed"] = bool(todo["completed"])
    return todo


def init_db() -> None:
    """Create the table if it is missing. Safe to run on every start."""
    with _session() as conn:
        conn.execute(SCHEMA)


def create_todo(data: dict) -> dict:
    """Save a new todo. `data` needs a title; the other fields default."""
    created_at = datetime.now().isoformat(timespec="seconds")
    with _session() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, description, due_date, priority, completed, created_at) "
            "VALUES (?, ?, ?, ?, 0, ?)",
            (data["title"], data.get("description"), data.get("due_date"), data.get("priority", "medium"), created_at),
        )
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_dict(row)


def get_todo(todo_id: int) -> Optional[dict]:
    if not _id_can_exist(todo_id):
        return None
    with _session() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _to_dict(row) if row else None


def list_todos(status: str = "all", priority: Optional[str] = None) -> list[dict]:
    """Todos oldest first, optionally only active or completed ones and/or one priority."""
    clauses, params = [], []
    if status == "active":
        clauses.append("completed = 0")
    elif status == "completed":
        clauses.append("completed = 1")
    if priority:
        clauses.append("priority = ?")
        params.append(priority)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with _session() as conn:
        rows = conn.execute(f"SELECT * FROM todos{where} ORDER BY id", params).fetchall()  # nosec: fixed clauses
    return [_to_dict(row) for row in rows]


def update_todo(todo_id: int, changes: dict) -> Optional[dict]:
    """Change any subset of fields. Returns the updated todo, or None if it does not exist."""
    unknown = set(changes) - set(UPDATABLE_COLUMNS)
    if unknown:
        raise ValueError(f"cannot change: {sorted(unknown)}")
    if not _id_can_exist(todo_id):
        return None
    if changes:
        assignments = ", ".join(f"{column} = ?" for column in changes)  # names are from the fixed list
        values = [int(v) if column == "completed" else v for column, v in changes.items()]
        with _session() as conn:
            conn.execute(f"UPDATE todos SET {assignments} WHERE id = ?", [*values, todo_id])
    return get_todo(todo_id)


def delete_todo(todo_id: int) -> bool:
    if not _id_can_exist(todo_id):
        return False
    with _session() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    return cursor.rowcount > 0
