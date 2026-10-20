# Research: AI Assistant

All choices were fixed by the constitution and the feature description, so there were no open "NEEDS
CLARIFICATION" items. Each decision below has its reasons. Some decisions reflect problems found while building the
same assistant earlier with a different method (the OpenSpec build); where so, it says so plainly.

## R-1. Agent framework: a LangGraph graph with a router

- **Decision**: One LangGraph `StateGraph`. An **orchestrator** node sets the intent; a conditional edge sends the
  message to `task_agent`, `priority_agent`, `reminder_agent`, or `unknown_reply`. State carries `message`, `now`,
  `intent`, `agent`, `reply`, `preview`, `suggestion`, `reminders`.
- **Rationale**: LangGraph is fixed by the constitution; the router shape makes a new agent one file plus one node
  and one edge.
- **Alternatives considered**: plain if/else (works, but is not the required agent framework); one big prompt that
  does everything (cannot be tested or limited per task).

## R-2. Model access: one function, any failure is "unavailable"

- **Decision**: Agents call the model only through `call_model(llm, messages)`, which returns the reply text and
  turns **any** exception (network, timeout, rejected key, rate limit) into `AIUnavailable`, logging only the
  exception's type name. Agents accept any object with `invoke(messages)`, so tests pass a fake. The Groq client
  is built with `max_retries=0`, a timeout from settings (default 15 s) and temperature 0.
- **Rationale**: One place decides what a failure means and one place guarantees no provider text or key leaks
  (constitution III). Disabling the client's own retries keeps the total wait inside the time budget; the only
  retry is our own JSON retry (R-3).
- **Alternatives considered**: letting each agent catch its own errors (leaks and drifts); the client's built-in
  retries (can multiply the wait).

## R-3. Model output: plain JSON, validated, one retry

- **Decision**: Every agent asks for one JSON object. The reply text is parsed (accepting a code fence or
  surrounding text) and validated with Pydantic. On invalid output it retries once, showing the model its own bad
  answer and asking for JSON only; a second failure raises `AIUnusableOutput`.
- **Rationale**: Groq's native "JSON schema" mode is supported only by some models and the list changes, so
  depending on it would tie the app to one model. Parse-and-validate works with any model and with the fake.
- **Alternatives considered**: `with_structured_output` or native JSON-schema mode (model-specific); unlimited
  retries (unbounded wait).

## R-4. Read-only by construction

- **Decision**: No module under `app/agents/` imports `app.storage`. `run_chat`/`build_graph` receive a
  `read_todos` function; the route passes `lambda: storage.list_todos(status="active")`. A preview or suggestion is
  only returned. **Confirm** posts to feature 001's create operation; **Accept** patches feature 001's edit
  operation. Two tests enforce this: one fails if any agent module or the chat route names a todo-changing function
  or opens the database directly; a stronger one fails if any module under `app/agents` imports `app.storage` at
  all. Each has self-tests that prove it catches violations.
- **Rationale**: A prompt rule like "never delete" can be bypassed by a crafted message; having no ability to
  write cannot. Even a fully hijacked model can then only propose something the user must confirm (constitution I).
- **Alternatives considered**: giving agents a create tool and trusting prompts (unsafe); importing `storage` and
  using only `list_todos` (one careless edit later could call a write function).

## R-5. The Reminder agent is plain code, not an AI call

- **Decision**: `due.py` selects and words the result. Selection: active todos with a due date; **overdue** if
  due before now; **due soon** if `now <= due <= now + 24 h`; overdue first (oldest first), then due soon (soonest
  first); completed and undated ignored. A due date with a time zone is parsed (a trailing `Z` is rewritten as
  `+00:00` so Python 3.10 can read it) and converted to local time before comparing. The reply is a count line then
  one line per todo (at most 10, then `- and N more`): `Overdue: Title (was due yesterday, 17:00)` or `Due soon:
  Title (due today, 17:00)`. With nothing to show it is exactly `Nothing is overdue or due in the next 24 hours.`
  The response also carries the full list with an `overdue` flag on each item.
- **Rationale**: The spec demands an exact list (nothing missed, nothing invented, overdue always marked). Code
  guarantees that, is instant, and removes a model call and a failure mode. It is still a graph node, so routing is
  the same as for the other agents.
- **Alternatives considered**: an AI-written summary with a code fallback (extra call and complexity for no gain in
  correctness; can be added later without changing the spec).

## R-6. Data blocks for untrusted text

- **Decision**: `data_block(tag, text)` removes every copy of the tag (case-insensitive, with optional spaces and
  slash) from the text, then wraps it: `<user_message>…</user_message>`, `<saved_todos>…</saved_todos>`. System
  prompts say block content is data and never instructions. Saved todos are given to the model as JSON with only
  `id`, `title` and `due_date`.
- **Rationale**: Without the tag removal, a message or a saved todo title containing a closing tag could end the
  block early and make the rest look like instructions. **The earlier OpenSpec build found this late, during
  verification; this plan includes it from the start.**
- **Alternatives considered**: relying on the prompt wording alone (bypassable); escaping with entities (harder to
  read for the model).

## R-7. Intent decision: unknown intents are safe

- **Decision**: `Intent` is `create_todo`, `suggest_priority`, `show_due` or `unknown`. If the model returns any
  other value (for example `delete_todo`), it is treated as `unknown`.
- **Rationale**: "delete all my todos" must get the friendly help reply (spec FR-010), not an error message.
- **Alternatives considered**: treating an unknown value as unusable output (the user would see an error instead of
  help).

## R-8. Priority agent

- **Decision**: Input is the message plus up to 50 active todos sorted soonest due first (undated last), as JSON in
  a data block. Output `{priority, reason, todo_id | null}` is validated. The reason is cut to 200 characters. A
  `todo_id` is accepted only if it was among the todos shown, and the linked **title always comes from our data**,
  never from the model.
- **Rationale**: A model can name a todo that does not exist or invent a title; accepting only supplied ids keeps
  the link honest (constitution V). The cap of 50 keeps the prompt small and the answer fast.
- **Alternatives considered**: matching titles in code (misses paraphrases); letting the model return the title
  (could invent one).

## R-9. Task agent and dates

- **Decision**: The current local date, time and weekday go into the prompt; the model returns `title`,
  `description`, `due_date` (`YYYY-MM-DDTHH:MM:SS` or null) and `priority`. The prompt tells it that a date with no
  time means 09:00, urgency words mean high, unimportance words low, otherwise medium. A title over 200 characters is
  cut to 200.
- **Rationale**: The model is good at language but must be given "now" to resolve "tomorrow". The result is
  validated like a hand-made todo so Confirm cannot fail on a preview.
- **Added during implementation (a defect found with the real model)**: the prompt also carries a printed calendar
  of the next 14 days, built in code from `now` (`calendar_for`), one line per day such as `Friday 2026-10-23`,
  with `(today)` and `(tomorrow)` marked, and a rule that a weekday name means the date the calendar lists for it.
  **Why**: with only "today is Monday" in the prompt, the real model answered "dentist on Friday" with Thursday in 4
  of 5 runs (while Wednesday and "next Thursday" were right 5 of 5), so it cannot be trusted to do weekday arithmetic.
  With the calendar, "Friday" was right 5 of 5 and 30 of 30 answers across six weekday phrases were right.
  A regression test (the prompt contains the exact calendar) and an opt-in live test cover it.
  **Alternative considered**: a date-parsing library after the model (misses wording the model handles).
- **Alternatives considered**: a date-parsing library (misses wording the model handles); trusting the model's
  own idea of today (wrong).

## R-10. The HTTP operation and the model provider

- **Decision**: `POST /agent/message` takes `{message}` (1 to 500 characters, trimmed). Responses use `{intent,
  reply, preview?, suggestion?, reminders?}`. Errors: 422 for a bad message; 503 "The AI assistant is not
  configured."; 503 "The AI assistant is unavailable right now."; 502 "I could not understand the AI's answer.
  Please try again." The route receives the model through a **provider function** (`get_llm_provider`, a FastAPI
  dependency) rather than the model itself.
- **Rationale**: With a provider function, the message is validated before the key is checked, so an empty message
  gets 422 even with no key configured; tests replace the provider with the fake. 503 means "assistant not
  available"; 502 means "the upstream answer was unusable".
- **Alternatives considered**: building the model in the dependency (a missing key would hide a validation error).

## R-11. Logging

- **Decision**: Logger `agent` writes one line per message: `intent=… agent=… outcome=… duration_ms=…`. A small
  `trace` dictionary filled by the graph nodes lets a failure still log which agent was running. The line never
  contains the message, todo titles or descriptions, or the key; the exception type is logged for model failures,
  never its text.
- **Rationale**: Constitution III. Provider errors and prompts can echo secrets and private text.
- **Alternatives considered**: logging requests for debugging (leaks private text).

## R-12. The page

- **Decision**: An Assistant card above the add form. Elements are built with `createElement`/`textContent`. While
  waiting: a loading line and a disabled Send button. A preview shows Confirm and Cancel; a suggestion shows Accept
  and Ignore only when it is linked to a saved todo; reminders are a list with a text label (Overdue or Due soon)
  and, when the list is not empty, only the first line of the summary above it. Errors appear in the card only, the
  typed message stays after an error, and an empty message shows "Please type a message first." without a request.
- **Rationale**: Reuses the page's safe patterns; the label is text so it does not rely on colour alone.
- **Alternatives considered**: a floating chat window (more layout and no extra value); showing the full summary and
  the list (duplicated information).

## R-13. Testing

- **Decision**: Default tests use `ScriptedLLM` (scripted replies or exceptions; records calls), a fixed clock and a
  temporary database, with no network. Feature 001's autouse fixture already removes `GROQ_*` from the environment.
  `tests/test_live_groq.py` is opt-in (`RUN_LIVE=1`; the key is read from `.env`): its `chat()` helper, on a 503,
  waits and retries a few times, then **skips** (a free-tier rate limit says nothing about our code); only the
  invalid-key test expects a 503 and does not use it.
- **Rationale**: Constitution IV. **In the earlier build the live suite failed on Groq's free-tier rate limit; this
  plan includes retry-then-skip from the start.**
- **Alternatives considered**: mocking the HTTP layer (does not test our parsing); no live tests (real-model
  behaviour such as routing and date resolution would go unchecked).

## R-14. Model choice

- **Decision**: Default `openai/gpt-oss-20b`, set by `GROQ_MODEL`.
- **Rationale**: Earlier, the models available to the project's key were listed and three chat models
  (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`) were tried on the extraction prompts; all three
  answered correctly. `gpt-oss-20b` was chosen for speed and likely lighter rate limits. It is a setting, not code.
- **Alternatives considered**: the larger `gpt-oss-120b` (slower for no observed gain); `qwen/qwen3.8-27b` (fastest,
  but less established).

## R-15. Settings

- **Decision**: `GROQ_API_KEY` (no default; blank counts as missing), `GROQ_MODEL` (default `openai/gpt-oss-20b`),
  `GROQ_TIMEOUT_SECONDS` (default 15; a non-number or a value of zero or below falls back to 15). All read at call
  time from the environment or `.env`.
- **Rationale**: Tests can override settings without reloading modules; a bad timeout never breaks the app.
- **Alternatives considered**: reading once at start (harder to test).
