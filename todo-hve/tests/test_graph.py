from datetime import datetime, timedelta

import pytest

from app.agents.errors import AIUnavailable, AIUnusableOutput
from app.agents.graph import HELP_REPLY, build_graph, run_chat
from app.agents.llm import Budget
from app.agents.schemas import Intent
from tests.fakes import ScriptedLLM

NOW = datetime(2026, 10, 20, 12, 0, 0)
INTENT = '{{"intent": "{}"}}'
TASK = '{"title": "Call mom", "due_date": "2026-10-21T17:00:00", "priority": "medium"}'
PRIORITY = '{"priority": "high", "reason": "Due tomorrow.", "todo_id": 1}'


def saved(*rows):
    return lambda: [dict(r) for r in rows]


TODOS = (
    {"id": 1, "title": "Submit tax return", "due_date": (NOW + timedelta(hours=3)).isoformat(timespec="seconds"), "completed": False},
    {"id": 2, "title": "Old report", "due_date": (NOW - timedelta(days=1)).isoformat(timespec="seconds"), "completed": False},
)


def test_given_a_create_message_when_run_then_the_response_is_a_preview_and_nothing_else():
    # Arrange
    llm = ScriptedLLM(INTENT.format("create_todo"), TASK)

    # Act
    response = run_chat(llm, "call mom tomorrow at 5pm", saved(), NOW)

    # Assert
    assert response.intent is Intent.create_todo and response.preview.title == "Call mom"
    assert response.suggestion is None and response.reminders is None
    assert "Confirm" in response.reply and "Cancel" in response.reply


def test_given_a_priority_message_when_run_then_the_response_is_a_suggestion_linked_to_the_saved_todo():
    # Arrange
    llm = ScriptedLLM(INTENT.format("suggest_priority"), PRIORITY)

    # Act
    response = run_chat(llm, "priority for Submit tax return?", saved(*TODOS), NOW)

    # Assert
    assert response.intent is Intent.suggest_priority and response.suggestion.todo_title == "Submit tax return"
    assert response.reply == 'For "Submit tax return" I suggest high priority. Due tomorrow.'


def test_given_a_due_message_when_run_then_the_reminders_are_listed_and_the_model_is_not_called_after_routing():
    # Arrange
    llm = ScriptedLLM(INTENT.format("show_due"), RuntimeError("the model must not be called again"))

    # Act
    response = run_chat(llm, "what is due soon?", saved(*TODOS), NOW)

    # Assert
    assert [(r.title, r.overdue) for r in response.reminders] == [("Old report", True), ("Submit tax return", False)]
    assert len(llm.calls) == 1 and response.reply.startswith("2 todos need attention")


def test_given_a_due_message_with_nothing_due_when_run_then_the_nothing_due_sentence_is_the_reply():
    # Arrange
    llm = ScriptedLLM(INTENT.format("show_due"))

    # Act
    response = run_chat(llm, "anything overdue?", saved(), NOW)

    # Assert
    assert response.reply == "Nothing is overdue or due in the next 24 hours." and response.reminders == []


@pytest.mark.parametrize("message, reply", [
    ("blah blah", INTENT.format("unknown")),
    ("delete all my todos", INTENT.format("delete_todo")),
    ("mark buy milk as done", INTENT.format("complete_todo")),
])
def test_given_an_unknown_or_forbidden_request_when_run_then_the_help_reply_is_returned(message, reply):
    # Arrange
    llm = ScriptedLLM(reply)

    # Act
    response = run_chat(llm, message, saved(*TODOS), NOW)

    # Assert
    assert response.intent is Intent.unknown and response.reply == HELP_REPLY
    assert response.preview is None and response.suggestion is None and response.reminders is None


def test_given_the_help_reply_when_read_then_it_says_not_understood_gives_three_examples_and_no_edit_or_delete():
    # Arrange / Act
    lines = HELP_REPLY.splitlines()

    # Assert
    assert "did not understand" in lines[0].lower()
    assert len([line for line in lines if line.startswith("- ")]) == 3
    assert "can never edit or delete" in HELP_REPLY


def test_given_each_path_when_run_then_saved_todos_are_read_only_where_needed():
    # Arrange
    reads = {"create": 0, "priority": 0, "due": 0, "unknown": 0}
    cases = [("create", INTENT.format("create_todo"), TASK), ("priority", INTENT.format("suggest_priority"), PRIORITY),
             ("due", INTENT.format("show_due")), ("unknown", INTENT.format("unknown"))]

    # Act
    for name, *script in cases:
        def read(name=name):
            reads[name] += 1
            return []
        run_chat(ScriptedLLM(*script), "x", read, NOW)

    # Assert
    assert reads == {"create": 0, "priority": 1, "due": 1, "unknown": 0}


def test_given_the_trace_when_a_run_succeeds_then_it_records_the_intent_and_the_agent():
    # Arrange
    trace = {}
    llm = ScriptedLLM(INTENT.format("show_due"))

    # Act
    run_chat(llm, "x", saved(), NOW, trace=trace)

    # Assert
    assert (trace["intent"], trace["agent"]) == ("show_due", "reminder_agent")


def test_given_the_task_agent_fails_when_run_then_the_trace_still_names_the_agent_that_failed():
    # Arrange
    trace = {}
    llm = ScriptedLLM(INTENT.format("create_todo"), "nope", "nope")

    # Act / Assert
    with pytest.raises(AIUnusableOutput):
        run_chat(llm, "x", saved(), NOW, trace=trace)
    assert (trace["intent"], trace["agent"]) == ("create_todo", "task_agent")


def test_given_the_orchestrator_fails_when_run_then_the_trace_names_the_orchestrator():
    # Arrange
    trace = {}
    llm = ScriptedLLM(RuntimeError("down"))

    # Act / Assert
    with pytest.raises(AIUnavailable):
        run_chat(llm, "x", saved(), NOW, trace=trace)
    assert trace["agent"] == "orchestrator" and "intent" not in trace


def test_given_a_spent_budget_when_run_then_no_model_call_is_made_and_it_is_unavailable():
    # Arrange
    now = [0.0]
    budget = Budget(20, clock=lambda: now[0])
    now[0] = 21
    llm = ScriptedLLM(INTENT.format("unknown"))

    # Act / Assert
    with pytest.raises(AIUnavailable):
        run_chat(llm, "x", saved(), NOW, budget=budget)
    assert llm.calls == []


def test_given_the_clock_when_the_task_agent_runs_then_it_is_given_the_time_passed_to_run_chat():
    # Arrange
    llm = ScriptedLLM(INTENT.format("create_todo"), TASK)

    # Act
    run_chat(llm, "x", saved(), NOW)

    # Assert
    assert "2026-10-20T12:00:00" in llm.calls[1][0][1]


def test_given_the_graph_when_listed_then_it_has_the_orchestrator_and_the_four_destinations():
    # Arrange
    graph = build_graph(ScriptedLLM("x"), saved(), {})

    # Act
    nodes = set(graph.get_graph().nodes)

    # Assert
    assert {"orchestrator", "task_agent", "priority_agent", "reminder_agent", "unknown_reply"} <= nodes
