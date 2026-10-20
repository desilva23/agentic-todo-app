# Design

## Context

The core app is done: FastAPI, SQLite, `app/storage.py`, `app/models.py` and a single HTML page (see the archived change). This change adds the first AI agents. The stack is fixed: LangGraph for agents and GroqCloud as the LLM. See `proposal.md` for motivation. The requirements impose three hard rules that shape this design: agents never change saved todos (FR-16), core features must work without the AI (FR-17), and tests must run with no network or key (NFR-8).

## Goals / Non-Goals

**Goals:**
- A LangGraph graph with an orchestrator and a Task agent that is easy to extend with more agents in the next change.
- Safety by construction: the agent code cannot write to the database.
- A model that can be swapped (real Groq or a fake in tests) without changing agent code.

**Non-Goals:**
- Priority and Reminder agents, conversation memory, streaming, tool-calling loops.
- Relying on a model-specific "structured output" feature.

## Decisions

### 1. Layout
```
app/agents/
  schemas.py       Pydantic shapes: ChatRequest, ChatResponse, TodoPreview, Intent
  errors.py        the three safe-to-show errors (not configured, unavailable, unusable output)
  llm.py           builds the Groq chat model; turns every model failure into a safe error
  structured.py    ask-for-JSON-and-validate helper with one retry; wraps user text in a data block
  orchestrator.py  intent decision
  task_agent.py    message -> TodoPreview
  graph.py         the LangGraph wiring
app/chat.py        the FastAPI route POST /agent/message (takes the model through a provider function)
```
**Why:** one file per job; the next change adds `priority_agent.py` and `reminder_agent.py` and edits only `orchestrator.py` and `graph.py`.

### 2. LangGraph graph shape
A `StateGraph` with state `{message, now, intent, agent, reply, preview}`:
```
START -> orchestrator --(intent)--> task_agent -> END
                      \-- unknown --> unknown_reply -> END
```
The orchestrator node sets `intent`; a conditional edge routes on it. Adding an intent later means adding a node and one edge.
**Alternative:** a plain if/else without LangGraph. Rejected because LangGraph is a project requirement, and the graph form is what makes adding agents a small change.

### 3. The agents have no write access (FR-16 by construction)
Agent modules do not import `app.storage` write functions, and the graph has no database tool. The response carries a `preview` only. **Confirm** in the page calls the existing `POST /todos`. A test asserts that the saved todos are identical before and after a chat call.
**Why:** a prompt rule such as "never delete" can be bypassed by a malicious message; having no ability to write cannot be. **Alternative:** give agents a create tool and rely on prompts. Rejected as unsafe and contrary to the confirmation requirement.

### 4. Model output is plain JSON validated by Pydantic
Each agent asks for a single JSON object, parses the reply text, and validates it with a Pydantic model. On invalid output it retries once with a short correction message; a second failure raises an "unusable output" error. Temperature is 0.
**Why:** Groq's native JSON-schema mode is supported only on some models and the list changes, so relying on it would tie the app to one model. Parse-and-validate works with any model and with a fake model in tests. **Alternative:** `with_structured_output`. Rejected for the reason above.

### 5. Dates come from code, not from the model's guess
The route passes the current local date, time and weekday into the Task agent prompt. The model returns an ISO date-time (`YYYY-MM-DDTHH:MM:SS`) or null, which Pydantic validates. Tests pass a fixed "now" so "tomorrow at 3pm" is checked exactly.

### 6. Prompt-injection posture
User text goes into the prompt inside a clearly marked data block, and the system prompt says to treat it as data. Any block tags the user types are stripped first, so a message cannot close the block early (found during verification, now covered by tests). Because of decision 3, even a fully hijacked model can only produce a preview, which the user still has to confirm. Output is validated against the schema before use.

### 7. Settings (`app/config.py`)
`GROQ_API_KEY`, `GROQ_MODEL` and `GROQ_TIMEOUT_SECONDS` (default 15) read from the environment and `.env`. The default model is chosen during implementation by listing the models the key can use, and is then written to `.env.example`. The key is never logged or returned.

### 8. Error mapping
| Situation | HTTP status | Message to the user |
|---|---|---|
| Message empty or over 500 characters | 422 | names the `message` field |
| No key configured | 503 | "The AI assistant is not configured." |
| Groq unreachable, timed out or rejects the key | 503 | "The AI assistant is unavailable right now." |
| Output still invalid after one retry | 502 | "I could not understand the AI's answer. Please try again." |

Error text never contains the key or the raw Groq error body.

### 9. Logging
A logger `agent` writes one line per message: intent, agent used, outcome and duration. It does not write the message text or the key.

### 10. Web page
A new "Assistant" card in `static/index.html` with a text field, a send button, a loading indicator, a reply area, and a preview block with Confirm and Cancel. It uses the same safe DOM building as the rest of the page (no `innerHTML` with user or AI text). Confirm calls `POST /todos`, then reloads the list. Chat errors appear inside the Assistant card only.

### 11. Testing
- Agent tests use a fake chat model that returns canned JSON; the route gets the model through a FastAPI dependency that tests override.
- Tests cover: preview, relative dates with a fixed clock, priority wording, unknown and "delete all", invalid JSON then retry, two failures, missing key, no writes, no key in responses or logs.
- A separate **live smoke test** calls the real Groq model; it is skipped unless a key is present and `RUN_LIVE=1` is set, and it is not part of the default test run.
- The page is verified in a real browser against a stub model, then by hand against the real model.

## Risks / Trade-offs

- **The model may misread a message** → the user confirms every preview; the retry and validation catch malformed output.
- **Groq's free tier may rate-limit** → surfaces as the "unavailable" error; core features are unaffected. Documented in the README.
- **Model names change over time** → the model is a setting, not a constant.
- **No overall deadline per message** → each model call is limited to the timeout setting (15 s), but a bad network could stack up to three calls (orchestrator plus a retried Task agent). Normal replies take about 1 to 2 seconds. Accepted for now; an overall deadline could be added later.
- **Date errors near midnight or in other time zones** → single local time zone assumed (requirements assumption 6); fixed-clock tests cover the common cases.
- **Parse-and-validate costs an occasional extra call** → at most one retry, so worst case is two model calls per message, within the 10 second budget (NFR-2) in normal conditions.

## Open Questions

- Which exact Groq model is the best default? Decided at implementation by listing the models available to the key; it does not affect the specs.
