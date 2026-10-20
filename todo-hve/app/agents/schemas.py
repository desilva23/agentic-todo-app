"""The shapes of what goes in and out of the assistant."""

from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints

from app.models import Priority, TodoCreate

Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class Intent(str, Enum):
    create_todo = "create_todo"
    suggest_priority = "suggest_priority"
    show_due = "show_due"
    unknown = "unknown"


class ChatRequest(BaseModel):
    message: Message


class TodoPreview(TodoCreate):
    """A todo the assistant proposes. It follows exactly the rules of a todo the user types in."""


class PrioritySuggestion(BaseModel):
    priority: Priority
    reason: str = Field(max_length=200)
    todo_id: Optional[int] = None
    todo_title: Optional[str] = None


class ReminderItem(BaseModel):
    id: int
    title: str
    due_date: str
    overdue: bool


class ChatResponse(BaseModel):
    intent: Intent
    reply: str
    preview: Optional[TodoPreview] = None
    suggestion: Optional[PrioritySuggestion] = None
    reminders: Optional[list[ReminderItem]] = None
