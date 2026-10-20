# Proposal

## Why

The assistant can only create todos so far (archived change `add-agent-chat`). The requirements also call for a **Priority agent** that helps a user decide how urgent a todo is (FR-13) and a **Reminder agent** that tells them what is overdue or due soon (FR-14). These complete the multi-agent design: an orchestrator with four intents and three specialist agents.

## What Changes

- Extend the orchestrator so it can recognise two more intents, "suggest a priority" and "show what is due", alongside "create a todo" and "unknown" (FR-11).
- Add a **Priority agent** that suggests low, medium or high with a one-sentence reason, and can link the suggestion to a saved todo (FR-13).
- Add a **Reminder agent** that finds overdue and due-within-24-hours todos and returns a short readable summary plus the list itself (FR-14).
- Let these two agents **read** saved active todos, still without any ability to change them (FR-16).
- Add chat-box behavior: a priority suggestion with **Accept** and **Ignore**, and a reminder list with overdue items clearly marked. Accept applies the priority through the existing edit request, so it is the user's click that changes a todo (FR-13).
- Extend the tests (fake model, plus live checks for AC-10 and AC-11).

## Capabilities

### New Capabilities
- `priority-agent`: suggesting a priority with a reason, and linking it to a saved todo when the message names one.
- `reminder-agent`: finding overdue and due-soon todos and summarising them.

### Modified Capabilities
- `agent-chat-api`: routing now has four intents (the existing "Route a message by intent" requirement changes), and agents may read saved todos but never change them (new requirement).
- `chat-box`: shows priority suggestions with Accept/Ignore and reminder lists (new requirements; existing ones are unchanged).

## Out of Scope

- Automatic priority suggestions when a todo is created (decided during requirements review: on request only).
- Agents that change todos. Accepting a suggestion is a user action through the existing edit request.
- Push or scheduled notifications, snooze, recurring reminders.
- Chat history or memory, streaming, other languages.

## Impact

- **New code:** `app/agents/priority_agent.py`, `app/agents/due.py` (the Reminder agent's selection and summary logic; the agent itself is a node in `graph.py`), new tests.
- **Changed files:** `app/agents/schemas.py`, `orchestrator.py`, `structured.py`, `graph.py`, `app/chat.py`, `static/index.html`, `README.md`, existing test files that assume only two intents.
- **No new dependencies and no new endpoints.** Saved todos are read through a function passed in by the chat route.
- **Requirements covered:** FR-11 (complete), FR-13, FR-14, FR-16, NFR-2, NFR-5, NFR-9.
- **Acceptance criteria covered:** AC-10, AC-11, plus AC-13, AC-15 and AC-16 re-checked. This completes all 17 functional requirements.
