from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, StringConstraints, computed_field, field_validator

Priority = Literal["low", "medium", "high"]
StatusFilter = Literal["all", "active", "completed"]

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class TodoCreate(BaseModel):
    title: Title
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Priority = "medium"


class TodoUpdate(BaseModel):
    """Every field is optional; only fields the client sends are changed."""

    title: Optional[Title] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

    @field_validator("title", "priority", "completed")
    @classmethod
    def not_null_when_sent(cls, value):
        # These fields may be left out, but cannot be set to null.
        if value is None:
            raise ValueError("cannot be null")
        return value


class Todo(BaseModel):
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
