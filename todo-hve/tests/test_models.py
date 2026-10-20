import pytest
from pydantic import ValidationError

from app.models import Priority, StatusFilter, TodoCreate, TodoUpdate


def test_given_only_a_title_when_creating_then_defaults_are_filled():
    # Arrange / Act
    todo = TodoCreate(title="Buy milk")

    # Assert
    assert (todo.title, todo.description, todo.due_date, todo.priority) == ("Buy milk", None, None, Priority.medium)


def test_given_padded_title_when_creating_then_it_is_trimmed():
    # Arrange / Act
    todo = TodoCreate(title="   Buy milk  ")

    # Assert
    assert todo.title == "Buy milk"


@pytest.mark.parametrize("title", ["", "   ", "\n\t"])
def test_given_empty_or_blank_title_when_creating_then_it_is_rejected(title):
    # Arrange / Act / Assert
    with pytest.raises(ValidationError) as error:
        TodoCreate(title=title)
    assert "title" in str(error.value)


def test_given_title_of_200_characters_when_creating_then_it_is_accepted():
    # Arrange / Act
    todo = TodoCreate(title="a" * 200)

    # Assert
    assert len(todo.title) == 200


def test_given_title_of_201_characters_when_creating_then_it_is_rejected():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        TodoCreate(title="a" * 201)


def test_given_unknown_priority_when_creating_then_it_is_rejected():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError) as error:
        TodoCreate(title="x", priority="urgent")
    assert "priority" in str(error.value)


@pytest.mark.parametrize("value", ["low", "medium", "high"])
def test_given_each_known_priority_when_creating_then_it_is_accepted(value):
    # Arrange / Act
    todo = TodoCreate(title="x", priority=value)

    # Assert
    assert todo.priority.value == value


@pytest.mark.parametrize("due", [
    "2026-10-23T17:00",
    "2026-10-23T17:00:00",
    "2026-10-23T17:00:00Z",
    "2026-10-23T17:00:00+05:30",
])
def test_given_a_readable_date_time_when_creating_then_it_is_kept_as_written(due):
    # Arrange / Act
    todo = TodoCreate(title="x", due_date=due)

    # Assert
    assert todo.due_date == due


@pytest.mark.parametrize("due", ["tomorrow", "2026-13-40T10:00", "2026-10-23", "17:00", "   "])
def test_given_an_unreadable_due_date_when_creating_then_it_is_rejected_naming_the_field(due):
    # Arrange / Act / Assert
    with pytest.raises(ValidationError) as error:
        TodoCreate(title="x", due_date=due)
    assert "due_date" in str(error.value)


def test_given_blank_description_when_creating_then_it_becomes_none():
    # Arrange / Act
    todo = TodoCreate(title="x", description="   ")

    # Assert
    assert todo.description is None


def test_given_only_some_fields_when_updating_then_only_those_are_reported_as_set():
    # Arrange / Act
    update = TodoUpdate(priority="high")

    # Assert
    assert update.model_fields_set == {"priority"}


def test_given_null_title_when_updating_then_it_is_rejected():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        TodoUpdate(title=None)


def test_given_null_due_date_when_updating_then_it_means_clear_the_date():
    # Arrange / Act
    update = TodoUpdate(due_date=None)

    # Assert
    assert "due_date" in update.model_fields_set and update.due_date is None


@pytest.mark.parametrize("value", ["all", "active", "completed"])
def test_given_a_known_status_when_building_the_filter_then_it_is_accepted(value):
    # Arrange / Act
    status = StatusFilter(value)

    # Assert
    assert status.value == value


def test_given_an_unknown_status_when_building_the_filter_then_it_is_rejected():
    # Arrange / Act / Assert
    with pytest.raises(ValueError):
        StatusFilter("done")
