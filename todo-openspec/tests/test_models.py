import pytest
from pydantic import TypeAdapter, ValidationError

from app.models import StatusFilter, Todo, TodoCreate, TodoUpdate


def test_status_filter_rejects_unknown_value_and_lists_allowed():
    adapter = TypeAdapter(StatusFilter)
    for ok in ("all", "active", "completed"):
        assert adapter.validate_python(ok) == ok
    with pytest.raises(ValidationError) as err:
        adapter.validate_python("done")
    message = str(err.value)
    assert "all" in message and "active" in message and "completed" in message


def test_create_defaults_to_medium_priority():
    assert TodoCreate(title="Buy milk").priority == "medium"


def test_empty_title_rejected():
    with pytest.raises(ValidationError) as err:
        TodoCreate(title="")
    assert "title" in str(err.value)


def test_blank_title_rejected():
    with pytest.raises(ValidationError):
        TodoCreate(title="   ")


def test_title_of_200_accepted_and_201_rejected():
    assert TodoCreate(title="x" * 200)
    with pytest.raises(ValidationError):
        TodoCreate(title="x" * 201)


def test_unknown_priority_rejected_and_allowed_values_listed():
    with pytest.raises(ValidationError) as err:
        TodoCreate(title="A", priority="urgent")
    message = str(err.value)
    assert "low" in message and "medium" in message and "high" in message


def test_unreadable_due_date_rejected():
    with pytest.raises(ValidationError):
        TodoCreate(title="A", due_date="not a date")


def test_update_allows_partial_fields():
    update = TodoUpdate(priority="high")
    assert update.model_dump(exclude_unset=True) == {"priority": "high"}


def test_update_can_clear_due_date_with_null():
    update = TodoUpdate(due_date=None)
    assert update.model_dump(exclude_unset=True) == {"due_date": None}


def test_update_rejects_empty_title_and_null_title():
    with pytest.raises(ValidationError):
        TodoUpdate(title="")
    with pytest.raises(ValidationError):
        TodoUpdate(title=None)


def test_update_rejects_null_completed():
    with pytest.raises(ValidationError):
        TodoUpdate(completed=None)


def test_status_is_derived_from_completed():
    base = dict(
        id=1, title="A", description=None, due_date=None,
        priority="medium", created_at="2026-01-01T00:00:00",
    )
    assert Todo(**base, completed=False).status == "active"
    assert Todo(**base, completed=True).status == "completed"
