"""All SQLite access lives here. SQL is always parameterised."""

import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Optional

from app.config import get_db_path

# Columns a caller may change. Names come from this fixed list, never from user input.
UPDATABLE_COLUMNS = ("title", "description", "due_date", "priority", "completed")

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


# SQLite integers are 64-bit. Ids outside this range cannot exist, and passing them
# to SQLite raises OverflowError, so they are treated as "not found" instead.
MAX_ID = 2**63 - 1


def _id_can_exist(todo_id: int) -> bool:
    return 0 < todo_id <= MAX_ID


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _to_dict(row: sqlite3.Row) -> dict:
    todo = dict(row)
    todo["completed"] = bool(todo["completed"])
    return todo


def init_db() -> None:
    """Create the table if it does not exist yet (safe to call on every start)."""
    with closing(_connect()) as conn, conn:
        conn.execute(SCHEMA)


def create_todo(
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: str = "medium",
) -> dict:
    with closing(_connect()) as conn, conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, description, due_date, priority, completed, created_at) "
            "VALUES (?, ?, ?, ?, 0, ?)",
            (title, description, due_date, priority, datetime.now().isoformat(timespec="seconds")),
        )
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_dict(row)


def get_todo(todo_id: int) -> Optional[dict]:
    if not _id_can_exist(todo_id):
        return None
    with closing(_connect()) as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _to_dict(row) if row else None


def list_todos(status: str = "all", priority: Optional[str] = None) -> list[dict]:
    query = "SELECT * FROM todos"
    conditions: list[str] = []
    params: list = []
    if status == "active":
        conditions.append("completed = 0")
    elif status == "completed":
        conditions.append("completed = 1")
    if priority is not None:
        conditions.append("priority = ?")
        params.append(priority)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id"
    with closing(_connect()) as conn:
        rows = conn.execute(query, params).fetchall()
    return [_to_dict(row) for row in rows]


def update_todo(todo_id: int, changes: dict) -> Optional[dict]:
    """Apply the given column changes. Returns the updated todo, or None if the id is unknown."""
    if not _id_can_exist(todo_id):
        return None
    columns = [name for name in changes if name in UPDATABLE_COLUMNS]
    with closing(_connect()) as conn, conn:
        if columns:
            assignments = ", ".join(f"{name} = ?" for name in columns)
            values = [int(changes[n]) if n == "completed" else changes[n] for n in columns]
            conn.execute(f"UPDATE todos SET {assignments} WHERE id = ?", (*values, todo_id))
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _to_dict(row) if row else None


def delete_todo(todo_id: int) -> bool:
    if not _id_can_exist(todo_id):
        return False
    with closing(_connect()) as conn, conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    return cursor.rowcount > 0
