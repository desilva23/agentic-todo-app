"""What a valid todo looks like. FastAPI uses these shapes, so a bad value gets a 422 that names the field."""

from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, StringConstraints, field_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class StatusFilter(str, Enum):
    all = "all"
    active = "active"
    completed = "completed"


def parse_datetime(value: str) -> datetime:
    """Read an ISO 8601 date and time. A trailing Z is spelled as +00:00 so Python 3.10 can read it."""
    text = value.strip()
    if len(text) <= 10:  # a bare date has no time of day
        raise ValueError("not a date and time")
    return datetime.fromisoformat(text.replace("Z", "+00:00").replace("z", "+00:00"))


def _check_due_date(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        parse_datetime(value)
    except ValueError:
        raise ValueError("due_date must be a date and time such as 2026-10-23T17:00") from None
    return value.strip()


def _blank_to_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


class TodoCreate(BaseModel):
    title: Title
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Priority = Priority.medium

    _clean_description = field_validator("description")(_blank_to_none)
    _check_due = field_validator("due_date")(_check_due_date)


class TodoUpdate(BaseModel):
    """Any subset of fields. A field that is not sent stays as it is; description and due_date may be
    sent as null to clear them."""

    title: Optional[Title] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

    _clean_description = field_validator("description")(_blank_to_none)
    _check_due = field_validator("due_date")(_check_due_date)

    @field_validator("title", "priority", "completed", mode="before")
    @classmethod
    def _not_null(cls, value):
        if value is None:
            raise ValueError("this field cannot be empty")
        return value
