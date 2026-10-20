from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.agents.due import NOTHING_DUE, build_summary, find_due
from app.agents.schemas import ChatResponse, PrioritySuggestion, ReminderItem

NOW = datetime(2026, 10, 19, 14, 0, 0)  # Monday 14:00


def todo(id, title, due=None, completed=False):
    return {"id": id, "title": title, "due_date": due.isoformat() if due else None, "completed": completed}


def hours(n):
    return NOW + timedelta(hours=n)


# --- schemas (task 1.1) ---------------------------------------------------------------

def test_new_intents_are_valid_and_invented_ones_are_not():
    for name in ("create_todo", "suggest_priority", "show_due", "unknown"):
        assert ChatResponse(intent=name, reply="x").intent == name
    with pytest.raises(ValidationError):
        ChatResponse(intent="delete_todo", reply="x")


def test_a_plain_response_still_validates_and_new_fields_are_optional():
    response = ChatResponse(intent="unknown", reply="hi")
    assert response.preview is None and response.suggestion is None and response.reminders is None


def test_suggestion_and_reminder_shapes():
    s = PrioritySuggestion(priority="high", reason="Due tomorrow.", todo_id=3, todo_title="Tax")
    assert (s.todo_id, s.todo_title) == (3, "Tax")
    assert PrioritySuggestion(priority="low", reason="Not urgent.").todo_id is None
    with pytest.raises(ValidationError):
        PrioritySuggestion(priority="urgent", reason="x")
    item = ReminderItem(id=1, title="A", due_date=NOW, overdue=True)
    assert item.overdue is True


# --- selection (task 1.2) -----------------------------------------------------------

def test_overdue_and_due_in_3_hours_overdue_first():
    todos = [todo(1, "Soon", hours(3)), todo(2, "Late", hours(-5))]
    items = find_due(todos, NOW)
    assert [i.title for i in items] == ["Late", "Soon"]
    assert [i.overdue for i in items] == [True, False]


def test_due_in_25_hours_is_not_selected_and_exactly_24_is():
    assert find_due([todo(1, "Far", hours(25))], NOW) == []
    assert [i.title for i in find_due([todo(1, "Edge", hours(24))], NOW)] == ["Edge"]


def test_due_exactly_now_counts_as_due_soon_not_overdue():
    (item,) = find_due([todo(1, "Now", NOW)], NOW)
    assert item.overdue is False


def test_completed_and_undated_todos_are_ignored():
    todos = [todo(1, "Done late", hours(-5), completed=True), todo(2, "No date")]
    assert find_due(todos, NOW) == []


def test_ordering_of_several_items():
    todos = [
        todo(1, "soon-b", hours(10)), todo(2, "late-new", hours(-1)),
        todo(3, "soon-a", hours(2)), todo(4, "late-old", hours(-30)),
    ]
    assert [i.title for i in find_due(todos, NOW)] == ["late-old", "late-new", "soon-a", "soon-b"]


def test_a_date_with_a_z_time_zone_is_compared_correctly_and_does_not_crash():
    real_now = datetime.now()
    in_3h_utc = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat().replace("+00:00", "Z")
    long_ago_utc = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat().replace("+00:00", "Z")
    todos = [
        {"id": 1, "title": "Soon", "due_date": in_3h_utc, "completed": False},
        {"id": 2, "title": "Late", "due_date": long_ago_utc, "completed": False},
    ]
    items = find_due(todos, real_now)
    assert [(i.title, i.overdue) for i in items] == [("Late", True), ("Soon", False)]
    assert all(i.due_date.tzinfo is None for i in items)  # returned in plain local time


def test_a_date_with_an_offset_is_compared_correctly():
    due = (datetime.now(timezone(timedelta(hours=5, minutes=30))) + timedelta(hours=2)).isoformat()
    items = find_due([{"id": 1, "title": "X", "due_date": due, "completed": False}], datetime.now())
    assert [i.overdue for i in items] == [False]


def test_an_unreadable_stored_date_is_skipped_not_fatal():
    todos = [{"id": 1, "title": "Bad", "due_date": "not-a-date", "completed": False}, todo(2, "Ok", hours(1))]
    assert [i.title for i in find_due(todos, NOW)] == ["Ok"]


# --- summary (task 1.3) ---------------------------------------------------------------

def test_summary_for_two_items_marks_overdue_clearly():
    items = find_due([todo(1, "Submit report", NOW - timedelta(days=1, hours=-3)), todo(2, "Call mom", hours(3))], NOW)
    text = build_summary(items, NOW)
    lines = text.splitlines()
    assert lines[0] == "2 todos need attention: 1 overdue, 1 due soon."
    assert lines[1].startswith("- Overdue: Submit report (was due yesterday")
    assert lines[2] == "- Due soon: Call mom (due today, 17:00)"


def test_summary_wording_for_one_item_and_for_tomorrow_and_dates():
    items = find_due([todo(1, "Tomorrow task", hours(15))], NOW)
    assert build_summary(items, NOW).splitlines()[0] == "1 todo needs attention: 0 overdue, 1 due soon."
    assert "due tomorrow, 05:00" in build_summary(items, NOW)
    old = find_due([todo(1, "Old", NOW - timedelta(days=5))], NOW)
    assert "was due 14 Oct, 14:00" in build_summary(old, NOW)


def test_summary_with_14_items_names_10_and_says_and_4_more_but_lists_all_14():
    todos = [todo(i, f"Task {i}", hours(i)) for i in range(1, 15)]
    items = find_due(todos, NOW)
    assert len(items) == 14
    lines = build_summary(items, NOW).splitlines()
    assert lines[0].startswith("14 todos need attention")
    assert len(lines) == 1 + 10 + 1
    assert lines[-1] == "- and 4 more"


def test_summary_when_nothing_is_due():
    assert build_summary([], NOW) == NOTHING_DUE
    assert "next 24 hours" in NOTHING_DUE


def test_summary_collapses_whitespace_in_titles():
    items = find_due([todo(1, "Line one\nline   two", hours(1))], NOW)
    assert "Line one line two" in build_summary(items, NOW)
