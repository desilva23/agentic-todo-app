import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(db_path):
    return TestClient(app)


def test_starting_the_app_creates_the_database_file(tmp_path, monkeypatch):
    # Deliberately NOT using the db_path fixture: it creates the file itself and would hide a bug.
    path = tmp_path / "not_there_yet.db"
    monkeypatch.setenv("TODO_DB_PATH", str(path))
    assert not path.exists()
    with TestClient(app):
        assert path.exists()


# --- POST /todos and GET /todos (User Story 1) --------------------------------------------

def make(client, title="Task", **extra):
    response = client.post("/todos", json={"title": title, **extra})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_with_only_a_title(client):
    todo = make(client, "Buy milk")
    assert todo["id"] >= 1
    assert todo["priority"] == "medium"
    assert todo["status"] == "active" and todo["completed"] is False


def test_create_with_every_field(client):
    todo = make(client, "Pay rent", description="March", due_date="2026-03-01T09:00:00", priority="high")
    assert (todo["description"], todo["due_date"], todo["priority"]) == ("March", "2026-03-01T09:00:00", "high")


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_bad_titles_give_422_naming_title_and_save_nothing(client, title):
    response = client.post("/todos", json={"title": title})
    assert response.status_code == 422
    assert "title" in response.text
    assert client.get("/todos").json() == []


def test_a_200_character_title_is_accepted(client):
    assert len(make(client, "x" * 200)["title"]) == 200


def test_unknown_priority_gives_422_naming_priority_and_listing_the_allowed_values(client):
    response = client.post("/todos", json={"title": "A", "priority": "urgent"})
    assert response.status_code == 422
    for word in ("priority", "low", "medium", "high"):
        assert word in response.text


def test_unreadable_due_date_gives_422_naming_due_date(client):
    response = client.post("/todos", json={"title": "A", "due_date": "someday"})
    assert response.status_code == 422 and "due_date" in response.text


def test_a_due_date_ending_in_z_is_accepted_and_returned_unchanged(client):
    todo = make(client, "Zoned", due_date="2026-10-20T17:00:00Z")
    assert todo["due_date"] == "2026-10-20T17:00:00Z"
    assert client.get("/todos").json()[0]["due_date"] == "2026-10-20T17:00:00Z"


def test_list_is_empty_when_there_are_no_todos(client):
    response = client.get("/todos")
    assert response.status_code == 200 and response.json() == []


def test_list_returns_todos_in_creation_order(client):
    for name in ("A", "B", "C"):
        make(client, name)
    assert [t["title"] for t in client.get("/todos").json()] == ["A", "B", "C"]


def test_rejected_requests_leave_saved_todos_unchanged(client):
    make(client, "Keep A", priority="high")
    before = client.get("/todos").json()
    client.post("/todos", json={"title": ""})
    client.post("/todos", json={"title": "A", "priority": "urgent"})
    client.post("/todos", json={"title": "A", "due_date": "someday"})
    assert client.get("/todos").json() == before


# --- GET one, PATCH and DELETE (User Story 2) -----------------------------------------------

HUGE_ID = 99999999999999999999


def test_view_one_todo_and_unknown_id(client):
    todo = make(client, "A")
    assert client.get(f"/todos/{todo['id']}").json()["title"] == "A"
    response = client.get("/todos/9999")
    assert response.status_code == 404 and response.json()["detail"] == "Todo 9999 not found"


def test_change_a_due_date_and_see_it_in_the_list(client):
    todo = make(client, "A", due_date="2026-03-01T09:00:00")
    response = client.patch(f"/todos/{todo['id']}", json={"due_date": "2026-04-02T10:30:00"})
    assert response.status_code == 200 and response.json()["due_date"] == "2026-04-02T10:30:00"
    assert client.get("/todos").json()[0]["due_date"] == "2026-04-02T10:30:00"


def test_a_due_date_can_be_cleared_with_null(client):
    todo = make(client, "A", due_date="2026-03-01T09:00:00")
    assert client.patch(f"/todos/{todo['id']}", json={"due_date": None}).json()["due_date"] is None


@pytest.mark.parametrize("body", [{"title": ""}, {"priority": "urgent"}, {"title": None}, {"completed": None}])
def test_an_invalid_edit_gives_422_and_the_old_values_stay(client, body):
    todo = make(client, "Original", priority="high")
    assert client.patch(f"/todos/{todo['id']}", json=body).status_code == 422
    assert client.get(f"/todos/{todo['id']}").json() == todo


def test_complete_then_reopen(client):
    todo = make(client, "A")
    assert client.patch(f"/todos/{todo['id']}", json={"completed": True}).json()["status"] == "completed"
    assert client.patch(f"/todos/{todo['id']}", json={"completed": False}).json()["status"] == "active"


def test_edit_changes_only_the_fields_that_were_sent(client):
    todo = make(client, "A", priority="high")
    updated = client.patch(f"/todos/{todo['id']}", json={"title": "B"}).json()
    assert updated["title"] == "B" and updated["priority"] == "high"


def test_an_empty_body_changes_nothing(client):
    todo = make(client, "A")
    assert client.patch(f"/todos/{todo['id']}", json={}).json() == todo


def test_edit_unknown_id_is_404(client):
    assert client.patch("/todos/9999", json={"title": "x"}).status_code == 404


def test_delete_gives_204_and_the_todo_is_gone_and_a_second_delete_is_404(client):
    todo = make(client, "A")
    assert client.delete(f"/todos/{todo['id']}").status_code == 204
    assert client.get("/todos").json() == []
    assert client.delete(f"/todos/{todo['id']}").status_code == 404


@pytest.mark.parametrize("bad_id", ["0", "-5", str(HUGE_ID)])
@pytest.mark.parametrize("method, kwargs", [("get", {}), ("patch", {"json": {"title": "x"}}), ("delete", {})])
def test_regression_ids_that_can_never_exist_give_404_not_a_crash(client, bad_id, method, kwargs):
    """R-7: a huge id used to return 500. It must be a clear 'not found'."""
    response = getattr(client, method)(f"/todos/{bad_id}", **kwargs)
    assert response.status_code == 404


# --- filters (User Story 3) -------------------------------------------------------------------

@pytest.fixture
def mixed(client):
    make(client, "A", priority="high")
    make(client, "B", priority="low")
    c = make(client, "C", priority="high")
    client.patch(f"/todos/{c['id']}", json={"completed": True})


def listed(client, **params):
    response = client.get("/todos", params=params)
    assert response.status_code == 200, response.text
    return [t["title"] for t in response.json()]


def test_filter_by_each_status(client, mixed):
    assert listed(client, status="all") == ["A", "B", "C"]
    assert listed(client, status="active") == ["A", "B"]
    assert listed(client, status="completed") == ["C"]


def test_filter_by_each_priority(client, mixed):
    assert listed(client, priority="high") == ["A", "C"]
    assert listed(client, priority="low") == ["B"]


def test_both_filters_combined(client, mixed):
    assert listed(client, status="active", priority="high") == ["A"]


def test_no_filter_returns_everything(client, mixed):
    assert listed(client) == ["A", "B", "C"]


def test_a_filter_with_no_matches_is_an_empty_list_not_an_error(client, mixed):
    assert listed(client, status="completed", priority="low") == []


def test_an_unknown_status_gives_422_naming_status_and_listing_the_allowed_values(client, mixed):
    response = client.get("/todos", params={"status": "done"})
    assert response.status_code == 422
    for word in ("status", "all", "active", "completed"):
        assert word in response.text


def test_an_unknown_priority_filter_gives_422_naming_priority(client, mixed):
    response = client.get("/todos", params={"priority": "urgent"})
    assert response.status_code == 422 and "priority" in response.text


# --- performance (NFR-1, spec FR-014 / SC-002) ----------------------------------------------------

def test_every_operation_is_fast_with_1000_todos(client):
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
    start = time.perf_counter()
    assert client.post("/todos", json={"title": "one more"}).status_code == 201
    assert (time.perf_counter() - start) * 1000 < 500


def test_post_ignores_unknown_extra_fields(client):
    """Contract: unknown extra fields are ignored, so a client cannot set system-controlled values."""
    response = client.post("/todos", json={
        "title": "A", "id": 99, "completed": True, "status": "completed",
        "created_at": "1999-01-01T00:00:00", "made_up": "x",
    })
    assert response.status_code == 201
    todo = response.json()
    assert todo["id"] != 99 and todo["completed"] is False and todo["status"] == "active"
    assert todo["created_at"] != "1999-01-01T00:00:00"
    assert "made_up" not in todo
