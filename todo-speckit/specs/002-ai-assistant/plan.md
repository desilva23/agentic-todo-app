# Implementation Plan: AI Assistant

**Branch**: `002-ai-assistant` (no git repository; folder name only) | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-ai-assistant/spec.md`

## Summary

A chat box on the existing todo page. A message goes to one HTTP operation, `POST /agent/message`, where an
**orchestrator** (a LangGraph graph node that asks the language model) decides the kind of message and hands it
to one of three specialists: a **Task agent** (message to todo preview), a **Priority agent** (priority
suggestion), or a **Reminder agent** (what is overdue or due soon). Anything else gets a fixed help reply. The
model is Groq through `langchain-groq`; every model answer is plain JSON validated with Pydantic. The Reminder
agent is plain code, not an AI call, so its list and wording are exact. The agents can **only read** todos
(through one function passed in) and never write: confirming a preview or accepting a suggestion is the user's
click, which uses feature 001's normal todo operations. Failures become fixed, plain messages and never touch
the todos. See [research.md](research.md) for each decision and its alternatives.

## Technical Context

**Language/Version**: Python 3.10 or newer (developed and tested on Python 3.14; feature 001 was also run on 3.10 and 3.12)

**Primary Dependencies**: LangGraph 1.2.16, langchain-core 1.6.12, langchain-groq 1.1.3 (new, pinned); FastAPI, Pydantic, python-dotenv as in feature 001

**Storage**: none new. Reads active todos through feature 001's storage via a function the route passes in. Nothing from this feature is persisted

**Testing**: pytest with FastAPI `TestClient`; a fake model (`tests/fakes.py`), a fixed clock and a temporary database for every default test; opt-in live tests (`RUN_LIVE=1`) against the real Groq

**Target Platform**: a user's own computer, calling the Groq online service when the assistant is used

**Project Type**: web-service with one static page (same project as feature 001)

**Performance Goals**: a reply within 10 seconds under normal conditions (spec FR-016); measured replies in earlier trials took about 1 to 2 seconds; the reminder path makes no model call after routing

**Constraints**: agents have no write access to todos; core features work with no AI, key or network; the key and message text never appear in responses or logs; default tests run with no network and no key

**Scale/Scope**: one user, one message at a time, at most 50 todos sent to the model for a priority question

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Agents Are Read-Only by Construction | No agent module imports `app.storage`; agents receive only a `read_todos` function; Confirm and Accept use feature 001's operations. Two tests enforce it (no write names anywhere in agents or the route; no storage import at all under `app/agents`), each with self-tests that prove the check catches violations | PASS |
| II. Core Works Without AI | The assistant is additive: feature 001 code paths are not changed; the route fails with a fixed message when the AI is unusable; a test with no key shows chat returns 503 while every core operation still works | PASS |
| III. Secrets and Private Text Stay Out | Key read only from `.env`/environment; error text is fixed and never contains provider text; one log line per message with intent, agent, outcome, duration only; tests prove the key, message text and todo titles are absent from responses and logs | PASS |
| IV. Test-First and Offline by Default | Tests per task group written first; fake model, fixed clock, temporary database; feature 001's autouse fixture already strips `GROQ_*`; live tests are opt-in, retry then skip on a rate limit | PASS |
| V. Validate at Every Boundary | Message validated first (1 to 500 characters); model output parsed as JSON and validated with Pydantic, one retry; a model-named todo id is accepted only if it was supplied; `data_block` removes the block's own tag from message and todo text | PASS |
| VI. Simplicity and Plain Language | One new package, one route, one card on the page; no streaming, memory or extra features; fixed plain-language messages; safe DOM methods only; 375 px layout | PASS |

**Post-design re-check (after Phase 1)**: no change. The reminder agent being plain code removes a model call and a
failure mode. The design adds no entity that is stored, no new endpoint besides `POST /agent/message`, and no
dependency beyond the three pinned. No violations, so Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-assistant/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output: decisions, rationale, alternatives
├── data-model.md        # Phase 1 output: message, reply, preview, suggestion, due item
├── quickstart.md        # Phase 1 output: key setup, run and validation scenarios
├── contracts/
│   └── http-api.md      # Phase 1 output: POST /agent/message
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
app/
├── config.py            # + Groq settings (key, model, timeout), read at call time
├── main.py              # + include the chat router
├── chat.py              # NEW: POST /agent/message, error mapping, the decision log line
└── agents/              # NEW package; none of these files may import app.storage
    ├── __init__.py
    ├── errors.py        # AINotConfigured, AIUnavailable, AIUnusableOutput (fixed messages)
    ├── schemas.py       # ChatRequest, TodoPreview, PrioritySuggestion, ReminderItem, ChatResponse, Intent
    ├── llm.py           # get_llm() builds the Groq model; call_model() turns any failure into AIUnavailable
    ├── structured.py    # ask-for-JSON-and-validate helper (one retry); data_block()
    ├── orchestrator.py  # decides the intent
    ├── task_agent.py    # message -> todo preview
    ├── priority_agent.py# message + todos -> priority suggestion
    ├── due.py           # Reminder agent: find_due() and build_summary() (plain code)
    └── graph.py         # the LangGraph wiring and run_chat()

static/index.html        # + the Assistant card (message box, loading, preview, suggestion, reminders)

tests/
├── fakes.py             # ScriptedLLM: scripted replies or exceptions, records calls
├── test_agent_foundation.py
├── test_due.py
├── test_priority_agent.py
├── test_agents.py
├── test_chat_api.py
├── test_agent_isolation.py   # AST checks that agents cannot write or import storage
└── test_live_groq.py         # opt-in, real Groq

requirements.txt         # + langgraph, langchain-core, langchain-groq (pinned)
.env.example             # + GROQ_API_KEY (empty), GROQ_MODEL, GROQ_TIMEOUT_SECONDS
README.md                # + how to turn the assistant on
```

**Structure Decision**: Same single project as feature 001. One file per agent so a later agent is one new
file plus a node and an edge. The route lives in `app/chat.py` (outside the agents package) because it is the
only place allowed to hand agents the read-only function.

## Complexity Tracking

No constitution violations. Nothing to justify.
