"""The Reminder agent's logic. It is plain code on purpose: the list and the wording must be exact
(nothing missed, nothing invented, overdue always marked), so no AI is involved."""

from datetime import datetime, timedelta
from typing import Optional

from app.agents.schemas import ReminderItem
from app.models import parse_datetime

WINDOW = timedelta(hours=24)
MAX_LINES = 10
NOTHING_DUE = "Nothing is overdue or due in the next 24 hours."


def local_due(value: str) -> Optional[datetime]:
    """Read a stored due date as local time. A date with a time zone is converted to local time so it
    can be compared with `now`. An unreadable date gives None."""
    try:
        parsed = parse_datetime(value)
    except ValueError:
        return None
    return parsed.astimezone().replace(tzinfo=None) if parsed.tzinfo else parsed


def find_due(todos: list[dict], now: datetime) -> list[ReminderItem]:
    """Active todos that are overdue (due before now) or due from now up to and including 24 hours ahead:
    overdue first (oldest first), then due soon (soonest first). Completed and undated todos are ignored."""
    selected = []
    for todo in todos:
        if todo.get("completed") or not todo.get("due_date"):
            continue
        due = local_due(todo["due_date"])
        if due is None or due > now + WINDOW:
            continue
        selected.append((due < now, due, todo["id"], todo))
    selected.sort(key=lambda row: (not row[0], row[1], row[2]))  # overdue first, then by time
    return [
        ReminderItem(id=todo["id"], title=todo["title"], due_date=todo["due_date"], overdue=overdue)
        for overdue, _due, _id, todo in selected
    ]


def _when(due: datetime, now: datetime) -> str:
    day = (due.date() - now.date()).days
    clock = due.strftime("%H:%M")
    if day == 0:
        return f"today, {clock}"
    if day == 1:
        return f"tomorrow, {clock}"
    if day == -1:
        return f"yesterday, {clock}"
    return f"{due.day} {due.strftime('%b')}, {clock}"


def build_summary(items: list[ReminderItem], now: datetime) -> str:
    """A short readable summary: a count line, then one line per todo (at most 10, then '- and N more')."""
    if not items:
        return NOTHING_DUE
    overdue = sum(1 for item in items if item.overdue)
    noun = "todo needs" if len(items) == 1 else "todos need"
    lines = [f"{len(items)} {noun} attention: {overdue} overdue, {len(items) - overdue} due soon."]
    for item in items[:MAX_LINES]:
        due = local_due(item.due_date) or now
        title = " ".join(item.title.split())
        if item.overdue:
            lines.append(f"Overdue: {title} (was due {_when(due, now)})")
        else:
            lines.append(f"Due soon: {title} (due {_when(due, now)})")
    if len(items) > MAX_LINES:
        lines.append(f"- and {len(items) - MAX_LINES} more")
    return "\n".join(lines)
