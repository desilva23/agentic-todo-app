# Todo App (OpenSpec build)

A todo app built with the **OpenSpec** spec-driven workflow.

- **Core todos:** create, view, edit, delete, complete and filter, saved in SQLite, with a single web page.
- **Assistant (AI agents, built with LangGraph):** type a plain-English message in the chat box. An orchestrator routes it to one of three agents:
  - **Task agent:** "call mom tomorrow at 5pm" becomes a todo **preview**. Nothing is saved until you press **Confirm**.
  - **Priority agent:** "what priority should 'Submit tax return' be?" gives low, medium or high with a reason. Press **Accept** to apply it to that todo, or **Ignore**.
  - **Reminder agent:** "what is due soon?" lists active todos that are overdue or due in the next 24 hours, with overdue ones labelled.

Requirements: [docs/requirements.md](docs/requirements.md). Specs of what the app does today: [openspec/specs/](openspec/specs/). Plans and history of each change: [openspec/changes/](openspec/changes/).

## Run it

Needs Python 3.10 or newer (built and tested on Python 3.14).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in a browser. API docs are at http://127.0.0.1:8000/docs.

If a package does not install on your Python version, create the environment with Python 3.12 instead (for example `uv venv --python 3.12`).

## Turn on the Assistant

The todo features work without any setup. The Assistant needs a free GroqCloud key:

1. Create a key at https://console.groq.com.
2. Open `.env` and put it after `GROQ_API_KEY=` (no quotes). Save the file.
3. Restart the app.

Never put the key anywhere except `.env` (it is git-ignored). Without a key, the chat box shows "The AI assistant is not configured." and everything else keeps working.

Try these messages:

| Message | What happens |
|---|---|
| `call mom tomorrow at 5pm` | Task agent shows a preview with a due date; **Confirm** saves it |
| `urgent: fix the login bug today` | Preview with high priority |
| `what priority should 'Submit tax return' be?` | Priority agent suggests a priority with a reason; **Accept** applies it to the saved todo named in your message, **Ignore** discards it |
| `what is due soon?` / `anything overdue?` | Reminder agent lists overdue todos and todos due within 24 hours (completed and undated todos are skipped) |
| `delete all my todos` | Not done: the Assistant explains that it cannot edit or delete |

**The Assistant never changes your todos by itself.** It can only read active todos and make suggestions. Anything that is saved or changed happens when *you* press Confirm or Accept, which use the normal todo requests.

The reminder list is built by the app itself (not by the AI), so it is exact: nothing missed, nothing invented.

Groq's free tier has rate limits. If you send many messages quickly you may see "The AI assistant is unavailable right now"; wait a moment and try again.

## Settings

Set in `.env` (copy from `.env.example`; `.env` is git-ignored):

| Variable | Meaning | Default |
|---|---|---|
| `TODO_DB_PATH` | SQLite file location | `todos.db` |
| `GROQ_API_KEY` | Groq key for the Assistant | empty |
| `GROQ_MODEL` | Which Groq model to use | `openai/gpt-oss-20b` |
| `GROQ_TIMEOUT_SECONDS` | How long to wait for Groq | `15` |

## Run the tests

```bash
python -m pytest
```

The default run uses a temporary database and a **fake AI model** for every test. It needs no network and no API key, and it removes any key from the environment so a test can never call Groq by accident.

To also check the real Groq model (needs the key in `.env`; makes a few real API calls):

```bash
RUN_LIVE=1 python -m pytest tests/test_live_groq.py -v
```

## API

| Method and path | Purpose |
|---|---|
| `POST /todos` | create a todo (`title` required, 1–200 characters) |
| `GET /todos?status=&priority=` | list; `status` is `all`, `active` or `completed`; `priority` is `low`, `medium` or `high` |
| `GET /todos/{id}` | view one |
| `PATCH /todos/{id}` | change any fields, including `completed` |
| `DELETE /todos/{id}` | delete |
| `POST /agent/message` | send `{"message": "..."}` to the agents; returns `intent` (`create_todo`, `suggest_priority`, `show_due` or `unknown`), `reply`, and one of the optional `preview`, `suggestion` or `reminders`. Never changes anything. Errors: 422 bad message, 503 AI not configured or unavailable, 502 unusable AI answer |

## How the agents work

```
message -> Orchestrator -+-> create_todo      -> Task agent     -> preview    -> (you press Confirm) -> POST /todos
                         +-> suggest_priority -> Priority agent -> suggestion -> (you press Accept)  -> PATCH /todos/{id}
                         +-> show_due         -> Reminder agent -> list + summary (plain code, no AI call)
                         +-> unknown          -> help reply
```

The agents never import the database code (a test enforces this). They are handed one read-only function that returns the active todos, so even a tricked model can only propose something for you to confirm.

## Code coverage and SonarQube

Measure how much of the Python code the tests run (lines and branches):

```bash
python -m pytest --cov --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=test-results.xml
```

This prints a table, writes a browsable report to `htmlcov/index.html`, and writes `coverage.xml` and `test-results.xml`
for SonarQube. Settings live in `.coveragerc`. The reports are git-ignored.

To send the results to SonarQube or SonarCloud, install `sonar-scanner`, then run it from the project folder:

```bash
sonar-scanner -Dsonar.host.url=<your SonarQube address> -Dsonar.token=<your token>
```

`sonar-project.properties` already points at `app` and `static` (sources), `tests`, `coverage.xml` and `test-results.xml`.
Coverage covers the Python code only; the JavaScript inside `static/index.html` is analysed by Sonar but has no coverage number.
Keep the token out of the repository (pass it on the command line or as the `SONAR_TOKEN` environment variable).

## Layout

```
app/          FastAPI app (main.py), validation (models.py), SQLite (storage.py), settings (config.py), chat route (chat.py)
app/agents/   LangGraph graph, orchestrator, Task agent, model access, schemas
static/       the web page (index.html), styled as a calm light "Paper" look with a matching dark mode
tests/        pytest tests (fake model); test_live_groq.py is the optional real-model check
openspec/     specs and changes managed by OpenSpec
docs/         shared requirements
```
