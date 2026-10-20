from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, StringConstraints

from app.models import Priority, Title

Intent = Literal["create_todo", "suggest_priority", "show_due", "unknown"]

Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class ChatRequest(BaseModel):
    message: Message


class TodoPreview(BaseModel):
    """A todo the Task agent proposes. It follows the same rules as a hand-made todo."""

    title: Title
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Priority = "medium"


class PrioritySuggestion(BaseModel):
    """A priority the Priority agent suggests. `todo_id`/`todo_title` are set only when the
    suggestion is about a saved todo; the title always comes from our data, not the model."""

    priority: Priority
    reason: str
    todo_id: Optional[int] = None
    todo_title: Optional[str] = None


class ReminderItem(BaseModel):
    """One overdue or due-soon todo. `due_date` is in local time."""

    id: int
    title: str
    due_date: datetime
    overdue: bool


class ChatResponse(BaseModel):
    intent: Intent
    reply: str
    preview: Optional[TodoPreview] = None
    suggestion: Optional[PrioritySuggestion] = None
    reminders: Optional[list[ReminderItem]] = None
