from datetime import datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from app.models import Priority, StatusFilter, Title, Todo, TodoCreate, TodoUpdate


def test_priority_accepts_only_low_medium_high():
    adapter = TypeAdapter(Priority)
    for ok in ("low", "medium", "high"):
        assert adapter.validate_python(ok) == ok
    with pytest.raises(ValidationError):
        adapter.validate_python("urgent")


def test_status_filter_accepts_only_all_active_completed_and_lists_them_in_the_error():
    adapter = TypeAdapter(StatusFilter)
    for ok in ("all", "active", "completed"):
        assert adapter.validate_python(ok) == ok
    with pytest.raises(ValidationError) as err:
        adapter.validate_python("done")
    message = str(err.value)
    assert "all" in message and "active" in message and "completed" in message


def test_title_is_trimmed_and_must_be_1_to_200_characters_after_trimming():
    adapter = TypeAdapter(Title)
    assert adapter.validate_python("  Buy milk  ") == "Buy milk"
    assert len(adapter.validate_python("x" * 200)) == 200
    for bad in ("", "   ", "x" * 201):
        with pytest.raises(ValidationError):
            adapter.validate_python(bad)


# --- TodoCreate and Todo (User Story 1) -----------------------------------------------


def test_create_defaults_to_medium_and_other_fields_are_optional():
    todo = TodoCreate(title="Buy milk")
    assert todo.priority == "medium"
    assert todo.description is None and todo.due_date is None


def test_create_trims_the_title_and_rejects_empty_blank_and_too_long_titles_naming_the_field():
    assert TodoCreate(title="  Buy milk ").title == "Buy milk"
    for bad in ("", "   ", "x" * 201):
        with pytest.raises(ValidationError) as err:
            TodoCreate(title=bad)
        assert "title" in str(err.value)
    assert len(TodoCreate(title="x" * 200).title) == 200


def test_create_rejects_an_unknown_priority_and_lists_the_allowed_values():
    with pytest.raises(ValidationError) as err:
        TodoCreate(title="A", priority="urgent")
    message = str(err.value)
    assert "priority" in message and "low" in message and "medium" in message and "high" in message


def test_create_due_date_must_be_readable_and_accepts_a_value_ending_in_z():
    assert TodoCreate(title="A", due_date="2026-10-20T17:00:00").due_date == datetime(2026, 10, 20, 17, 0)
    assert TodoCreate(title="A", due_date="2026-10-20T17:00:00Z").due_date is not None
    with pytest.raises(ValidationError) as err:
        TodoCreate(title="A", due_date="someday")
    assert "due_date" in str(err.value)


def test_todo_status_is_derived_from_completed():
    base = dict(id=1, title="A", description=None, due_date=None, priority="medium",
                created_at="2026-10-19T09:00:00")
    assert Todo(**base, completed=False).status == "active"
    assert Todo(**base, completed=True).status == "completed"


# --- TodoUpdate (User Story 2) --------------------------------------------------------------

def test_update_fields_are_all_optional_and_only_sent_fields_are_reported():
    assert TodoUpdate().model_dump(exclude_unset=True) == {}
    assert TodoUpdate(priority="high").model_dump(exclude_unset=True) == {"priority": "high"}


def test_update_may_clear_description_and_due_date_with_null():
    update = TodoUpdate(description=None, due_date=None)
    assert update.model_dump(exclude_unset=True) == {"description": None, "due_date": None}


@pytest.mark.parametrize("field", ["title", "priority", "completed"])
def test_update_cannot_set_title_priority_or_completed_to_null(field):
    with pytest.raises(ValidationError) as err:
        TodoUpdate(**{field: None})
    assert field in str(err.value)


def test_update_rejects_an_empty_or_over_long_title_and_a_non_boolean_completed():
    for bad in ("", "   ", "x" * 201):
        with pytest.raises(ValidationError):
            TodoUpdate(title=bad)
    with pytest.raises(ValidationError):
        TodoUpdate(completed="maybe")
