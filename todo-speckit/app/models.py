from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, StringConstraints, computed_field, field_validator

Priority = Literal["low", "medium", "high"]
StatusFilter = Literal["all", "active", "completed"]

# Whitespace trimmed; 1 to 200 characters after trimming.
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class TodoCreate(BaseModel):
    """What a client sends to create a todo. Unknown extra fields are ignored."""

    title: Title
    description: Optional[str] = None
    due_date: Optional[datetime] = None  # ISO 8601 date-time; a value with a time zone is accepted
    priority: Priority = "medium"


class TodoUpdate(BaseModel):
    """What a client sends to change a todo. Every field is optional; only the fields that are
    sent are changed. `description` and `due_date` may be null (clearing them); `title`,
    `priority` and `completed` cannot be set to null."""

    title: Optional[Title] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

    @field_validator("title", "priority", "completed")
    @classmethod
    def cannot_be_null(cls, value):
        if value is None:
            raise ValueError("cannot be null")
        return value


class Todo(BaseModel):
    """A saved todo as returned to clients."""

    id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: Priority
    completed: bool
    created_at: datetime

    @computed_field
    @property
    def status(self) -> Literal["active", "completed"]:
        return "completed" if self.completed else "active"
