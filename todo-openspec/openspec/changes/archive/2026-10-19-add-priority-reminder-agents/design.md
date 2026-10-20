# Design

## Context

The graph from `add-agent-chat` is in place: an orchestrator, a Task agent and an unknown reply, a chat route, and a fake-model test setup. This change adds two agents. The new element is that agents must now **read saved todos**, while the hard rule from the requirements stays: agents never create, edit or delete (FR-16). See `proposal.md` for motivation and the archived `add-agent-chat` design for the existing decisions (JSON-and-validate, data blocks, safe errors).

## Goals / Non-Goals

**Goals:**
- Give the agents read access to saved todos without giving them any write access.
- Make the Reminder results exact and reliable (AC-11 needs both todos listed and the overdue one marked).
- Keep adding agents a small change: one new file each, plus a node and an edge in the graph.

**Non-Goals:**
- New endpoints. Accepting a suggestion reuses `PATCH /todos/{id}`.
- Any LLM-written text for reminders (see decision 2).

## Decisions

### 1. Agents read todos through a function passed in, not through the storage module
`build_graph` and `run_chat` take a `read_todos` argument: a function that returns the saved active todos. The chat route supplies it (`storage.list_todos(status="active")`); tests supply a list. Modules under `app/agents/` never import `app.storage`.
**Why:** the rule "agents cannot write" is then easy to prove and to keep: the agents only ever hold a read-only function. The existing test that bans write names is extended to ban any `app.storage` import inside `app/agents/`.
**Alternative:** let agents import `storage` and use only `list_todos`. Rejected because one careless edit later could call a write function.

### 2. The Reminder agent is code, not an AI call
`due.py` selects the todos and builds the summary text from them. The AI is not used after the orchestrator has routed the message.
**Why:** AC-11 demands that both todos appear and the overdue one is clearly marked. Code guarantees that every time, is instant, and cannot invent a todo or drop one. An AI-written summary would add a second model call, a failure mode (and a fallback for it) and no new information. **Alternative:** an AI-written summary with a code fallback. Rejected as extra complexity for no gain in correctness; it can be added later without changing the specs if a friendlier tone is wanted.
The agent is still a LangGraph node, so the graph and the orchestrator's routing are the same as for the other agents.

### 3. Selection rules (in `due.py`)
Active todos with a due date; `overdue` if due before now; `due soon` if due from now up to and including 24 hours ahead; overdue first (oldest due first), then due soon (soonest first). A due date with a time zone is converted to local time before comparing, because the todo API accepts such dates and comparing them with a plain local time would raise an error. "Now" is passed in, so tests use a fixed clock.

### 4. Summary text
One line per todo, for example `Overdue: Submit report (was due 18 Oct, 17:00)` and `Due soon: Call mom (due today, 17:00)`, introduced by a count line. At most 10 lines, then `and N more`. The response also carries every selected todo as `{id, title, due_date, overdue}`, so the page can mark overdue items without parsing text.

### 5. Priority agent
Input: the user's message and up to 50 active todos (id, title, due date), soonest due first, serialised as JSON inside a data block. Output (validated with Pydantic, same retry rule as other agents): `{priority, reason, todo_id | null}`.
- The reason is cut to 200 characters.
- A `todo_id` that is not in the list given to the model is replaced with null. The linked todo's **title comes from our data**, never from the model.
- If the message names no saved todo, the model returns null and the reply says no saved todo matched.
**Why a cap of 50:** keeps the prompt small and the response fast; the soonest-due todos are the ones where priority advice matters most.

### 6. Orchestrator
The system prompt lists four intents with examples. The existing rule stays: an intent the model invents is treated as `unknown`, so requests such as "delete all my todos" still get the help reply. The `Intent` type gains `suggest_priority` and `show_due`; `KNOWN_INTENTS` is derived from it, so no second list needs updating.

### 7. Data blocks for saved todos
The helper from `add-agent-chat` generalises to `data_block(tag, text)`: it removes that tag from the text before wrapping, so neither a user message nor a saved todo title can close the block. `wrap_user_message` stays as a thin wrapper. Saved todo titles are a new route for injection (a todo titled "ignore your rules…"), but the worst outcome is still a wrong suggestion, because agents cannot write.

### 8. Response shape
`ChatResponse` keeps `intent`, `reply` and `preview`, and gains two optional fields: `suggestion` (`priority`, `reason`, `todo_id`, `todo_title`) and `reminders` (a list of `{id, title, due_date, overdue}`). Existing clients keep working because the new fields are optional.

### 9. Web page
The Assistant card renders a suggestion block (priority, reason, and for a linked todo: title, **Accept**, **Ignore**) and a reminders block (one row per todo with a text label "Overdue" or "Due soon", not only a color). Accept sends `PATCH /todos/{id}` with `{priority}`, then reloads the list. All text is inserted with safe DOM methods, as before.

### 10. Logging and errors
Unchanged rules: one log line per message with intent, agent and outcome, never the message text or the key. The new agents log as `priority_agent` and `reminder_agent`. The error mapping is the existing one (not configured, unavailable, unusable output).

### 11. Testing
Fake model and fixed clock throughout. Reminder tests cover the 24-hour boundary, overdue ordering, completed and undated todos, time-zone dates and the "and N more" rule, with no model at all. Priority tests cover a matched todo, no match, an invented id, the 50 cap, a long reason and an invalid answer. Route tests check that todos are unchanged after every new request, including a saved todo whose title is an instruction. Live tests for AC-10 and AC-11 join the optional real-model file.

## Risks / Trade-offs

- **The model may link the wrong saved todo** → the user sees the todo's title next to Accept and must press it; nothing changes otherwise.
- **Two todos with similar titles** → the model may pick either; acceptable because of the visible confirmation.
- **The 24 hour window is a fixed rule** → exactly as the requirements state; a different window would be a spec change.
- **The reminder summary is plain** → accepted in exchange for exactness (decision 2).
- **Changing the `Intent` type touches existing tests** that assumed two intents → they are updated in this change.
