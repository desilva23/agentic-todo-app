import time

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app

HUGE_ID = 99999999999999999999


@pytest.fixture
def client(db_path):
    return TestClient(app)


def add(client, title="Task", **fields):
    response = client.post("/todos", json={"title": title, **fields})
    assert response.status_code == 201, response.text
    return response.json()


def test_given_the_app_when_asking_for_its_description_then_the_title_names_this_build(client):
    # Arrange / Act
    title = client.get("/openapi.json").json()["info"]["title"]

    # Assert
    assert title == "Todo App (HVE build)"


def test_given_only_a_title_when_creating_then_it_is_active_with_medium_priority(client):
    # Arrange / Act
    response = client.post("/todos", json={"title": "Buy milk"})

    # Assert
    body = response.json()
    assert response.status_code == 201
    assert (body["title"], body["priority"], body["completed"], body["status"]) == ("Buy milk", "medium", False, "active")


@pytest.mark.parametrize("title", ["", "   ", "a" * 201])
def test_given_a_bad_title_when_creating_then_it_is_rejected_naming_the_field_and_nothing_is_saved(client, title):
    # Arrange / Act
    response = client.post("/todos", json={"title": title})

    # Assert
    assert response.status_code == 422
    assert "title" in response.text
    assert client.get("/todos").json() == []


def test_given_an_unknown_priority_when_creating_then_it_is_rejected_naming_the_field(client):
    # Arrange / Act
    response = client.post("/todos", json={"title": "x", "priority": "urgent"})

    # Assert
    assert response.status_code == 422 and "priority" in response.text


def test_given_an_unreadable_due_date_when_creating_then_it_is_rejected_naming_the_field(client):
    # Arrange / Act
    response = client.post("/todos", json={"title": "x", "due_date": "tomorrow"})

    # Assert
    assert response.status_code == 422 and "due_date" in response.text


def test_given_two_todos_when_listing_then_both_show_title_status_due_date_and_priority(client):
    # Arrange
    add(client, "a", due_date="2026-10-23T17:00", priority="high")
    add(client, "b")

    # Act
    todos = client.get("/todos").json()

    # Assert
    assert [(t["title"], t["status"], t["due_date"], t["priority"]) for t in todos] == [
        ("a", "active", "2026-10-23T17:00", "high"), ("b", "active", None, "medium")]


def test_given_active_and_completed_when_filtering_by_completed_then_only_completed_show(client):
    # Arrange
    done = add(client, "done")
    add(client, "open")
    client.patch(f"/todos/{done['id']}", json={"completed": True})

    # Act
    titles = [t["title"] for t in client.get("/todos", params={"status": "completed"}).json()]

    # Assert
    assert titles == ["done"]


def test_given_mixed_priorities_when_filtering_by_priority_then_only_that_priority_shows(client):
    # Arrange
    add(client, "lo", priority="low")
    add(client, "hi", priority="high")

    # Act
    titles = [t["title"] for t in client.get("/todos", params={"priority": "high"}).json()]

    # Assert
    assert titles == ["hi"]


def test_given_an_unknown_status_filter_when_listing_then_it_is_rejected_listing_the_allowed_values(client):
    # Arrange / Act
    response = client.get("/todos", params={"status": "done"})

    # Assert
    assert response.status_code == 422 and "active" in response.text and "completed" in response.text


def test_given_a_saved_todo_when_getting_it_then_it_is_returned(client):
    # Arrange
    todo = add(client, "x")

    # Act
    response = client.get(f"/todos/{todo['id']}")

    # Assert
    assert response.status_code == 200 and response.json() == todo


def test_given_no_such_todo_when_getting_it_then_the_message_names_the_id(client):
    # Arrange / Act
    response = client.get("/todos/42")

    # Assert
    assert (response.status_code, response.json()) == (404, {"detail": "Todo 42 not found"})


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
@pytest.mark.parametrize("bad_id", [HUGE_ID, 0, -5])
def test_given_an_id_that_can_never_exist_when_using_it_then_it_is_a_404_not_a_server_error(client, method, bad_id):
    # Arrange / Act
    kwargs = {"json": {"title": "x"}} if method == "patch" else {}
    response = getattr(client, method)(f"/todos/{bad_id}", **kwargs)

    # Assert
    assert response.status_code == 404


def test_given_an_existing_todo_when_changing_its_due_date_then_the_list_shows_the_new_date(client):
    # Arrange
    todo = add(client, "x", due_date="2026-10-23T17:00")

    # Act
    client.patch(f"/todos/{todo['id']}", json={"due_date": "2026-11-01T09:00"})

    # Assert
    assert client.get("/todos").json()[0]["due_date"] == "2026-11-01T09:00"


def test_given_a_due_date_when_patching_it_to_null_then_it_is_cleared(client):
    # Arrange
    todo = add(client, "x", due_date="2026-10-23T17:00")

    # Act
    response = client.patch(f"/todos/{todo['id']}", json={"due_date": None})

    # Assert
    assert response.json()["due_date"] is None


def test_given_an_active_todo_when_completed_then_it_shows_completed_and_reopening_returns_it_to_active(client):
    # Arrange
    todo = add(client, "x")

    # Act
    done = client.patch(f"/todos/{todo['id']}", json={"completed": True}).json()
    reopened = client.patch(f"/todos/{todo['id']}", json={"completed": False}).json()

    # Assert
    assert (done["status"], reopened["status"]) == ("completed", "active")


def test_given_a_patch_with_only_priority_when_applied_then_other_fields_are_unchanged(client):
    # Arrange
    todo = add(client, "keep", description="d")

    # Act
    body = client.patch(f"/todos/{todo['id']}", json={"priority": "low"}).json()

    # Assert
    assert (body["title"], body["description"], body["priority"]) == ("keep", "d", "low")


@pytest.mark.parametrize("payload", [{"title": ""}, {"title": None}, {"priority": "urgent"}, {"completed": None}])
def test_given_an_invalid_change_when_patching_then_it_is_rejected_and_the_todo_is_unchanged(client, payload):
    # Arrange
    todo = add(client, "keep")

    # Act
    response = client.patch(f"/todos/{todo['id']}", json=payload)

    # Assert
    assert response.status_code == 422 and client.get(f"/todos/{todo['id']}").json() == todo


def test_given_no_such_todo_when_patching_then_it_is_a_404(client):
    # Arrange / Act
    response = client.patch("/todos/42", json={"title": "x"})

    # Assert
    assert response.status_code == 404 and response.json() == {"detail": "Todo 42 not found"}


def test_given_an_existing_todo_when_deleting_then_it_no_longer_appears(client):
    # Arrange
    todo = add(client, "x")

    # Act
    response = client.delete(f"/todos/{todo['id']}")

    # Assert
    assert response.status_code == 204 and client.get("/todos").json() == []


def test_given_no_such_todo_when_deleting_then_it_is_a_404(client):
    # Arrange / Act
    response = client.delete("/todos/42")

    # Assert
    assert response.status_code == 404


def test_given_saved_todos_when_the_app_restarts_then_they_are_all_still_listed(client):
    # Arrange
    add(client, "one")
    add(client, "two")

    # Act (a restart runs the start-up step again)
    with TestClient(app) as restarted:
        titles = [t["title"] for t in restarted.get("/todos").json()]

    # Assert
    assert titles == ["one", "two"]


def test_given_1000_saved_todos_when_listing_then_the_call_answers_in_under_500_ms(client):
    # Arrange
    for i in range(1000):
        storage.create_todo({"title": f"todo {i}"})

    # Act
    started = time.perf_counter()
    response = client.get("/todos")
    elapsed_ms = (time.perf_counter() - started) * 1000

    # Assert
    assert len(response.json()) == 1000 and elapsed_ms < 500
