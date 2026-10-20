"""The agent graph (LangGraph). The orchestrator decides the intent, then one of these runs:

    task_agent      turn a sentence into a todo preview
    priority_agent  suggest low, medium or high
    reminder_agent  what is overdue or due soon (plain code, no model call)
    unknown_reply   a friendly help message

Agents only ever receive `read_todos`, a function that returns the saved active todos. They have no way to
create, change or delete one, so even a hijacked model can only produce a preview or a suggestion that the
user must confirm.
"""

from datetime import datetime
from typing import Any, Callable, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.due import build_summary, find_due
from app.agents.llm import Budget
from app.agents.orchestrator import classify
from app.agents.priority_agent import describe, suggest
from app.agents.schemas import ChatResponse, Intent
from app.agents.task_agent import make_preview

HELP_REPLY = """Sorry, I did not understand that. Here are some things you can try:
- call mom tomorrow at 5pm
- what priority should 'Submit tax return' be?
- what is due soon?
I can create todos, suggest priorities and show what is due, but I can never edit or delete your todos."""

PREVIEW_REPLY = "Here is the todo I understood. Press Confirm to save it, or Cancel to discard it."

ROUTES = {
    Intent.create_todo: "task_agent",
    Intent.suggest_priority: "priority_agent",
    Intent.show_due: "reminder_agent",
    Intent.unknown: "unknown_reply",
}


class ChatState(TypedDict, total=False):
    message: str
    now: datetime
    budget: Optional[Budget]
    intent: Intent
    agent: str
    reply: str
    preview: Any
    suggestion: Any
    reminders: Any


def build_graph(llm, read_todos: Callable[[], list], trace: dict):
    """Wire the graph. `trace` is filled as the nodes run, so a failure still shows which agent was running."""

    def orchestrator(state: ChatState) -> dict:
        trace["agent"] = "orchestrator"
        intent = classify(llm, state["message"], state.get("budget"))
        trace["intent"] = intent.value
        return {"intent": intent}

    def route(state: ChatState) -> str:
        return ROUTES[state["intent"]]

    def task_agent(state: ChatState) -> dict:
        trace["agent"] = "task_agent"
        preview = make_preview(llm, state["message"], state["now"], state.get("budget"))
        return {"agent": "task_agent", "preview": preview, "reply": PREVIEW_REPLY}

    def priority_agent(state: ChatState) -> dict:
        trace["agent"] = "priority_agent"
        suggestion = suggest(llm, state["message"], read_todos(), state["now"], state.get("budget"))
        return {"agent": "priority_agent", "suggestion": suggestion, "reply": describe(suggestion)}

    def reminder_agent(state: ChatState) -> dict:
        trace["agent"] = "reminder_agent"
        items = find_due(read_todos(), state["now"])
        return {"agent": "reminder_agent", "reminders": items, "reply": build_summary(items, state["now"])}

    def unknown_reply(state: ChatState) -> dict:
        trace["agent"] = "unknown_reply"
        return {"agent": "unknown_reply", "reply": HELP_REPLY}

    graph = StateGraph(ChatState)
    graph.add_node("orchestrator", orchestrator)
    graph.add_node("task_agent", task_agent)
    graph.add_node("priority_agent", priority_agent)
    graph.add_node("reminder_agent", reminder_agent)
    graph.add_node("unknown_reply", unknown_reply)
    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges("orchestrator", route, list(ROUTES.values()))
    for node in ROUTES.values():
        graph.add_edge(node, END)
    return graph.compile()


def run_chat(
    llm,
    message: str,
    read_todos: Callable[[], list],
    now: datetime,
    trace: Optional[dict] = None,
    budget: Optional[Budget] = None,
) -> ChatResponse:
    """Run one message through the graph and return the response."""
    trace = trace if trace is not None else {}
    graph = build_graph(llm, read_todos, trace)
    state = graph.invoke({"message": message, "now": now, "budget": budget})
    # Only the parts that apply are set, so the HTTP response leaves the others out.
    parts = {key: state[key] for key in ("preview", "suggestion", "reminders") if state.get(key) is not None}
    return ChatResponse(intent=state["intent"], reply=state["reply"], **parts)
