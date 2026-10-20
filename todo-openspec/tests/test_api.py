import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(db_path):
    return TestClient(app)


def make(client, title="Task", **extra):
    response = client.post("/todos", json={"title": title, **extra})
    assert response.status_code == 201, response.text
    return response.json()


# --- Create (spec: Create a todo / Reject invalid todo input) -----------------

def test_create_with_only_a_title(client):
    todo = make(client, "Buy milk")
    assert todo["id"] >= 1
    assert todo["priority"] == "medium"
    assert todo["status"] == "active"
    assert todo["completed"] is False


def test_create_with_all_fields(client):
    todo = make(
        client, "Pay rent", description="March", due_date="2026-03-01T09:00:00", priority="high"
    )
    assert todo["description"] == "March"
    assert todo["due_date"] == "2026-03-01T09:00:00"
    assert todo["priority"] == "high"


def test_create_empty_title_rejected_and_names_field(client):
    response = client.post("/todos", json={"title": ""})
    assert response.status_code == 422
    assert "title" in response.text
    assert client.get("/todos").json() == []


def test_create_title_too_long_rejected(client):
    response = client.post("/todos", json={"title": "x" * 201})
    assert response.status_code == 422
    assert "title" in response.text


def test_create_unknown_priority_lists_allowed_values(client):
    response = client.post("/todos", json={"title": "A", "priority": "urgent"})
    assert response.status_code == 422
    for allowed in ("low", "medium", "high"):
        assert allowed in response.text


def test_create_bad_due_date_rejected(client):
    response = client.post("/todos", json={"title": "A", "due_date": "someday"})
    assert response.status_code == 422
    assert "due_date" in response.text


# --- List / view / filters (spec: List todos, View one, Filter) ---------------

def test_list_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_all(client):
    for name in ("A", "B", "C"):
        make(client, name)
    assert [t["title"] for t in client.get("/todos").json()] == ["A", "B", "C"]


def test_view_existing_and_unknown(client):
    todo = make(client, "A")
    assert client.get(f"/todos/{todo['id']}").json()["title"] == "A"
    response = client.get("/todos/9999")
    assert response.status_code == 404


def test_filter_by_status(client):
    make(client, "Active one")
    done = make(client, "Done one")
    client.patch(f"/todos/{done['id']}", json={"completed": True})

    completed = client.get("/todos", params={"status": "completed"}).json()
    assert [t["title"] for t in completed] == ["Done one"]
    active = client.get("/todos", params={"status": "active"}).json()
    assert [t["title"] for t in active] == ["Active one"]
    assert len(client.get("/todos", params={"status": "all"}).json()) == 2


def test_filter_by_priority(client):
    make(client, "H", priority="high")
    make(client, "L", priority="low")
    result = client.get("/todos", params={"priority": "high"}).json()
    assert [t["title"] for t in result] == ["H"]


def test_combined_filters(client):
    make(client, "active high", priority="high")
    done_high = make(client, "done high", priority="high")
    make(client, "active low", priority="low")
    client.patch(f"/todos/{done_high['id']}", json={"completed": True})

    result = client.get("/todos", params={"status": "active", "priority": "high"}).json()
    assert [t["title"] for t in result] == ["active high"]


def test_invalid_status_filter_lists_allowed_values(client):
    response = client.get("/todos", params={"status": "done"})
    assert response.status_code == 422
    for allowed in ("all", "active", "completed"):
        assert allowed in response.text


# --- Edit / complete / reopen (spec: Edit a todo, Complete and reopen) --------

def test_change_due_date(client):
    todo = make(client, "A", due_date="2026-03-01T09:00:00")
    response = client.patch(f"/todos/{todo['id']}", json={"due_date": "2026-04-02T10:30:00"})
    assert response.status_code == 200
    assert response.json()["due_date"] == "2026-04-02T10:30:00"
    listed = client.get("/todos").json()[0]
    assert listed["due_date"] == "2026-04-02T10:30:00"


def test_clear_due_date_with_null(client):
    todo = make(client, "A", due_date="2026-03-01T09:00:00")
    response = client.patch(f"/todos/{todo['id']}", json={"due_date": None})
    assert response.json()["due_date"] is None


def test_invalid_edit_keeps_old_value(client):
    todo = make(client, "Original")
    response = client.patch(f"/todos/{todo['id']}", json={"title": ""})
    assert response.status_code == 422
    assert client.get(f"/todos/{todo['id']}").json()["title"] == "Original"


def test_edit_unknown_id(client):
    response = client.patch("/todos/9999", json={"title": "x"})
    assert response.status_code == 404


def test_edit_only_changes_sent_fields(client):
    todo = make(client, "A", priority="high")
    updated = client.patch(f"/todos/{todo['id']}", json={"title": "B"}).json()
    assert updated["title"] == "B"
    assert updated["priority"] == "high"


def test_complete_then_reopen(client):
    todo = make(client, "A")
    done = client.patch(f"/todos/{todo['id']}", json={"completed": True}).json()
    assert done["status"] == "completed"
    reopened = client.patch(f"/todos/{todo['id']}", json={"completed": False}).json()
    assert reopened["status"] == "active"


# --- Delete (spec: Delete a todo) ---------------------------------------------

def test_delete_existing(client):
    todo = make(client, "A")
    assert client.delete(f"/todos/{todo['id']}").status_code == 204
    assert client.get("/todos").json() == []


def test_delete_unknown_id(client):
    assert client.delete("/todos/9999").status_code == 404


# --- Whole-app checks ----------------------------------------------------------

HUGE_ID = 99999999999999999999  # larger than SQLite can store


@pytest.mark.parametrize("method, kwargs", [
    ("get", {}),
    ("patch", {"json": {"title": "x"}}),
    ("delete", {}),
])
def test_ids_too_large_for_the_database_are_not_found_not_a_crash(client, method, kwargs):
    """Found by /opsx:verify: these used to return 500 instead of the spec's not-found."""
    response = getattr(client, method)(f"/todos/{HUGE_ID}", **kwargs)
    assert response.status_code == 404


def test_listing_1000_todos_is_fast(client):
    """NFR-1: core API calls respond in under 500 ms with 1,000 todos."""
    import time

    from app import storage

    for i in range(1000):
        storage.create_todo(f"Todo {i}", priority=("low", "medium", "high")[i % 3])
    for path in ("/todos", "/todos?status=active&priority=high", "/todos/500"):
        start = time.perf_counter()
        response = client.get(path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        assert elapsed_ms < 500, f"{path} took {elapsed_ms:.0f} ms"

def test_everything_works_without_a_groq_key(client, monkeypatch):
    """Spec: core features work without AI (no key, no network)."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    todo = make(client, "No AI needed", priority="low")
    assert client.get("/todos").json()[0]["id"] == todo["id"]
    assert client.patch(f"/todos/{todo['id']}", json={"title": "Edited"}).status_code == 200
    assert client.patch(f"/todos/{todo['id']}", json={"completed": True}).status_code == 200
    assert len(client.get("/todos", params={"status": "completed"}).json()) == 1
    assert client.delete(f"/todos/{todo['id']}").status_code == 204


def test_rejected_requests_leave_saved_data_unchanged(client):
    a = make(client, "Keep A", priority="high")
    b = make(client, "Keep B")
    before = client.get("/todos").json()

    client.post("/todos", json={"title": ""})
    client.patch(f"/todos/{a['id']}", json={"priority": "urgent"})
    client.patch(f"/todos/{b['id']}", json={"title": "x" * 201})
    client.get("/todos", params={"status": "nonsense"})

    assert client.get("/todos").json() == before
