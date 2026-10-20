"""The Reminder agent's logic. It is plain code on purpose: the list and the wording must be exact
(nothing missed, nothing invented, overdue always marked), so no AI is involved."""

from datetime import datetime, timedelta
from typing import Optional

from app.agents.schemas import ReminderItem

WINDOW = timedelta(hours=24)
MAX_SUMMARY_LINES = 10
NOTHING_DUE = "Nothing is overdue or due in the next 24 hours."


def parse_iso(value: str) -> Optional[datetime]:
    try:
        # Python 3.10 cannot read a trailing "Z", so spell it as an explicit offset.
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def to_local(value: datetime) -> datetime:
    """Todo dates are local times, but the todo API also accepts dates with a time zone. Convert those
    to local time so they can be compared with `now` without an error."""
    if value.tzinfo is not None:
        return value.astimezone().replace(tzinfo=None)
    return value


def find_due(todos: list[dict], now: datetime) -> list[ReminderItem]:
    """Active todos that are overdue (due before now) or due from now up to and including 24 hours
    ahead: overdue first (oldest first), then due soon (soonest first). Completed and undated todos
    are ignored."""
    items = []
    for todo in todos:
        if todo.get("completed") or not todo.get("due_date"):
            continue
        parsed = parse_iso(todo["due_date"])
        if parsed is None:
            continue
        due = to_local(parsed)
        if due < now:
            overdue = True
        elif due <= now + WINDOW:
            overdue = False
        else:
            continue
        items.append(ReminderItem(id=todo["id"], title=todo["title"], due_date=due, overdue=overdue))
    items.sort(key=lambda item: (not item.overdue, item.due_date))
    return items


def _when(due: datetime, now: datetime) -> str:
    clock = due.strftime("%H:%M")
    if due.date() == now.date():
        return f"today, {clock}"
    if due.date() == now.date() + timedelta(days=1):
        return f"tomorrow, {clock}"
    if due.date() == now.date() - timedelta(days=1):
        return f"yesterday, {clock}"
    return f"{due.day} {due.strftime('%b')}, {clock}"


def build_summary(items: list[ReminderItem], now: datetime) -> str:
    """A short readable summary: a count line, then one line per todo (at most 10, then '- and N more')."""
    if not items:
        return NOTHING_DUE
    overdue = sum(1 for item in items if item.overdue)
    noun = "todo needs" if len(items) == 1 else "todos need"
    lines = [f"{len(items)} {noun} attention: {overdue} overdue, {len(items) - overdue} due soon."]
    for item in items[:MAX_SUMMARY_LINES]:
        title = " ".join(item.title.split())
        if item.overdue:
            lines.append(f"- Overdue: {title} (was due {_when(item.due_date, now)})")
        else:
            lines.append(f"- Due soon: {title} (due {_when(item.due_date, now)})")
    if len(items) > MAX_SUMMARY_LINES:
        lines.append(f"- and {len(items) - MAX_SUMMARY_LINES} more")
    return "\n".join(lines)
