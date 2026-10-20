from datetime import datetime, timedelta, timezone

from app.agents.due import NOTHING_DUE, build_summary, find_due

NOW = datetime(2026, 10, 19, 14, 0, 0)  # Monday 14:00


def todo(id, title, due=None, completed=False):
    return {"id": id, "title": title, "due_date": due.isoformat() if due else None, "completed": completed}


def hours(n):
    return NOW + timedelta(hours=n)


# --- selection (T026) --------------------------------------------------------------------------

def test_overdue_and_due_in_3_hours_are_both_listed_overdue_first():
    items = find_due([todo(1, "Soon", hours(3)), todo(2, "Late", hours(-5))], NOW)
    assert [i.title for i in items] == ["Late", "Soon"]
    assert [i.overdue for i in items] == [True, False]


def test_due_in_25_hours_is_excluded_and_exactly_24_hours_is_included():
    assert find_due([todo(1, "Far", hours(25))], NOW) == []
    assert [i.title for i in find_due([todo(1, "Edge", hours(24))], NOW)] == ["Edge"]


def test_due_exactly_now_is_due_soon_not_overdue():
    (item,) = find_due([todo(1, "Now", NOW)], NOW)
    assert item.overdue is False


def test_completed_and_undated_todos_are_ignored():
    assert find_due([todo(1, "Done late", hours(-5), completed=True), todo(2, "No date")], NOW) == []


def test_ordering_overdue_oldest_first_then_due_soon_soonest_first():
    todos = [todo(1, "soon-b", hours(10)), todo(2, "late-new", hours(-1)),
             todo(3, "soon-a", hours(2)), todo(4, "late-old", hours(-30))]
    assert [i.title for i in find_due(todos, NOW)] == ["late-old", "late-new", "soon-a", "soon-b"]


def test_a_date_ending_in_z_is_compared_correctly_and_returned_as_plain_local_time():
    real_now = datetime.now()
    soon = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat().replace("+00:00", "Z")
    late = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat().replace("+00:00", "Z")
    items = find_due([{"id": 1, "title": "Soon", "due_date": soon, "completed": False},
                      {"id": 2, "title": "Late", "due_date": late, "completed": False}], real_now)
    assert [(i.title, i.overdue) for i in items] == [("Late", True), ("Soon", False)]
    assert all(i.due_date.tzinfo is None for i in items)


def test_a_date_with_a_plus_0530_offset_is_compared_correctly():
    due = (datetime.now(timezone(timedelta(hours=5, minutes=30))) + timedelta(hours=2)).isoformat()
    items = find_due([{"id": 1, "title": "X", "due_date": due, "completed": False}], datetime.now())
    assert [i.overdue for i in items] == [False]


def test_an_unreadable_stored_date_is_skipped_not_fatal():
    todos = [{"id": 1, "title": "Bad", "due_date": "not-a-date", "completed": False}, todo(2, "Ok", hours(1))]
    assert [i.title for i in find_due(todos, NOW)] == ["Ok"]


# --- summary (T026) ----------------------------------------------------------------------------

def test_the_summary_has_a_count_line_and_marks_overdue_in_words():
    items = find_due([todo(1, "Submit report", NOW - timedelta(days=1, hours=-3)), todo(2, "Call mom", hours(3))], NOW)
    lines = build_summary(items, NOW).splitlines()
    assert lines[0] == "2 todos need attention: 1 overdue, 1 due soon."
    assert lines[1].startswith("- Overdue: Submit report (was due yesterday")
    assert lines[2] == "- Due soon: Call mom (due today, 17:00)"


def test_summary_wording_for_one_item_tomorrow_and_an_older_date():
    items = find_due([todo(1, "Tomorrow task", hours(15))], NOW)
    assert build_summary(items, NOW).splitlines()[0] == "1 todo needs attention: 0 overdue, 1 due soon."
    assert "due tomorrow, 05:00" in build_summary(items, NOW)
    old = find_due([todo(1, "Old", NOW - timedelta(days=5))], NOW)
    assert "was due 14 Oct, 14:00" in build_summary(old, NOW)


def test_with_14_items_the_summary_names_10_and_says_and_4_more_but_all_14_are_listed():
    items = find_due([todo(i, f"Task {i}", hours(i)) for i in range(1, 15)], NOW)
    assert len(items) == 14
    lines = build_summary(items, NOW).splitlines()
    assert lines[0].startswith("14 todos need attention")
    assert len(lines) == 1 + 10 + 1 and lines[-1] == "- and 4 more"


def test_the_nothing_due_text_is_exact():
    assert build_summary([], NOW) == NOTHING_DUE == "Nothing is overdue or due in the next 24 hours."


def test_titles_have_their_whitespace_collapsed_in_the_summary():
    items = find_due([todo(1, "Line one\nline   two", hours(1))], NOW)
    assert "Line one line two" in build_summary(items, NOW)
