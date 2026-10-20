# Proposal

## Why

The core todo app works (see the archived change `add-core-todo-management`), but users can only manage todos by filling in forms. The project's goal is an agentic todo app: a user should be able to type "call mom tomorrow at 5pm" and have an AI agent turn it into a todo. This change adds the first working agent slice end to end: chat box, orchestrator, Task agent, and safe failure handling. The priority and reminder agents follow in a separate change so each change stays small enough to review.

## What Changes

- Add a chat endpoint that accepts a plain-English message and returns a reply (FR-10).
- Add an **Orchestrator agent** that decides what the user wants and routes the message. In this change it recognises "create a todo" and "unknown" (FR-11, FR-15).
- Add a **Task agent** that turns a message into a todo **preview** with title, due date and priority. Nothing is saved by the agent (FR-12, FR-16).
- Add a chat box to the web page that shows the reply, and shows a preview with **Confirm** and **Cancel** buttons. Confirm saves through the existing todo creation API (FR-12, AC-9).
- Add safe failure handling: if Groq is unreachable, the key is missing or invalid, or the model returns unusable output, the user gets a clear message and every core todo feature keeps working (FR-17, NFR-3).
- Add settings for the Groq key and model, kept in `.env` (NFR-4), and logging of agent decisions without secrets or message text (NFR-9).
- Add automated tests that use a fake model, so they need no network and no API key (NFR-8).

## Capabilities

### New Capabilities
- `agent-chat-api`: the chat endpoint, routing of messages by intent, the reply for messages the agents cannot handle, the rule that agents never change saved todos, failure handling, and secret-safe logging.
- `task-agent`: turning a plain-English message into a todo preview, including relative dates such as "tomorrow at 5pm" and priority words.
- `chat-box`: the chat box on the web page, including the preview with Confirm and Cancel, a loading indicator, and readable errors.

### Modified Capabilities
<!-- None. Existing todo specs are unchanged: saving a confirmed preview reuses the existing "Create a todo" behavior. -->

## Out of Scope

- The **Priority agent** (FR-13) and the **Reminder agent** (FR-14). They come in a later change, which will extend the orchestrator's routing.
- Chat history, conversation memory, streaming replies and multi-turn dialogue. Each message is handled on its own.
- Agents that edit or delete todos (forbidden by FR-16).
- Languages other than English, user accounts, deployment.

## Impact

- **New code:** `app/agents/` (LLM access, orchestrator, task agent, graph, schemas), a chat route, an updated `static/index.html`, new tests.
- **Changed files:** `app/main.py` (register the chat route), `app/config.py` (Groq settings), `requirements.txt`, `.env.example`, `README.md`.
- **New dependencies:** LangGraph, LangChain core, LangChain Groq (pinned versions).
- **Requirements covered:** FR-10, FR-11 (create and unknown only), FR-12, FR-15, FR-16, FR-17, NFR-2, NFR-3, NFR-4, NFR-5, NFR-9.
- **Acceptance criteria covered:** AC-8, AC-9, AC-12, AC-13, AC-14, plus AC-15 and AC-16 re-checked.
- **External service:** GroqCloud, used only by the agent feature.
