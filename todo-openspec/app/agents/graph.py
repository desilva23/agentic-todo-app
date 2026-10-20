"""The LangGraph wiring:

    orchestrator -> task_agent      (create a todo preview)
                 -> priority_agent  (suggest a priority)
                 -> reminder_agent  (what is overdue or due soon)
                 -> unknown_reply   (help)
"""

from datetime import datetime
from typing import Callable, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.due import build_summary, find_due
from app.agents.orchestrator import decide_intent
from app.agents.priority_agent import suggest_priority
from app.agents.schemas import (
    ChatResponse,
    Intent,
    PrioritySuggestion,
    ReminderItem,
    TodoPreview,
)
from app.agents.task_agent import create_preview

UNKNOWN_REPLY = (
    "Sorry, I didn't understand that request. I can create a todo from a sentence, suggest a "
    "priority, or tell you what is due, but I can't edit or delete todos, so use the list for "
    "that. Try something like: \"Call mom tomorrow at 5pm\", \"What is due soon?\" or "
    "\"What priority should 'Submit tax return' be?\"."
)
PREVIEW_REPLY = "Here is the todo I understood. Press Confirm to save it, or Cancel to discard it."
NO_MATCH_NOTE = "No saved todo matched, so this is based on your description."

# intent -> the node that handles it; any other intent goes to the unknown reply
AGENT_FOR_INTENT = {
    "create_todo": "task_agent",
    "suggest_priority": "priority_agent",
    "show_due": "reminder_agent",
}


class ChatState(TypedDict, total=False):
    message: str
    now: datetime
    intent: Intent
    agent: str
    reply: str
    preview: Optional[TodoPreview]
    suggestion: Optional[PrioritySuggestion]
    reminders: Optional[list[ReminderItem]]


def suggestion_reply(suggestion: PrioritySuggestion) -> str:
    if suggestion.todo_id is not None:
        return f"For \"{suggestion.todo_title}\" I suggest {suggestion.priority} priority. {suggestion.reason}"
    return f"I suggest {suggestion.priority} priority. {suggestion.reason} ({NO_MATCH_NOTE})"


def build_graph(llm, trace: Optional[dict] = None, read_todos: Optional[Callable[[], list]] = None):
    """Build the graph around a model. Tests pass a fake model; the app passes Groq.

    `read_todos` returns the saved active todos. It is the ONLY access to saved todos the
    agents get, and it is read-only; nothing in the agents can create, edit or delete.

    `trace` is filled in as the graph runs (intent, agent) so the caller can log what
    happened even when a node fails part-way.
    """
    trace = trace if trace is not None else {}
    read_todos = read_todos if read_todos is not None else (lambda: [])

    def orchestrator(state: ChatState) -> dict:
        trace["agent"] = "orchestrator"
        intent = decide_intent(llm, state["message"])
        trace["intent"] = intent
        return {"intent": intent}

    def task_agent(state: ChatState) -> dict:
        trace["agent"] = "task_agent"
        preview = create_preview(llm, state["message"], state["now"])
        return {"agent": "task_agent", "preview": preview, "reply": PREVIEW_REPLY}

    def priority_agent(state: ChatState) -> dict:
        trace["agent"] = "priority_agent"
        suggestion = suggest_priority(llm, state["message"], read_todos(), state["now"])
        return {"agent": "priority_agent", "suggestion": suggestion, "reply": suggestion_reply(suggestion)}

    def reminder_agent(state: ChatState) -> dict:
        trace["agent"] = "reminder_agent"
        items = find_due(read_todos(), state["now"])  # plain code: no model call here
        return {"agent": "reminder_agent", "reminders": items, "reply": build_summary(items, state["now"])}

    def unknown_reply(state: ChatState) -> dict:
        trace["agent"] = "unknown_reply"
        return {"agent": "unknown_reply", "reply": UNKNOWN_REPLY}

    def route(state: ChatState) -> str:
        return AGENT_FOR_INTENT.get(state["intent"], "unknown_reply")

    graph = StateGraph(ChatState)
    graph.add_node("orchestrator", orchestrator)
    graph.add_node("task_agent", task_agent)
    graph.add_node("priority_agent", priority_agent)
    graph.add_node("reminder_agent", reminder_agent)
    graph.add_node("unknown_reply", unknown_reply)
    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator", route, ["task_agent", "priority_agent", "reminder_agent", "unknown_reply"]
    )
    for node in ("task_agent", "priority_agent", "reminder_agent", "unknown_reply"):
        graph.add_edge(node, END)
    return graph.compile()


def run_chat(
    llm,
    message: str,
    now: datetime,
    trace: Optional[dict] = None,
    read_todos: Optional[Callable[[], list]] = None,
) -> ChatResponse:
    state = build_graph(llm, trace, read_todos).invoke({"message": message, "now": now})
    return ChatResponse(
        intent=state["intent"],
        reply=state["reply"],
        preview=state.get("preview"),
        suggestion=state.get("suggestion"),
        reminders=state.get("reminders"),
    )
