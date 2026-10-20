# Todo App (Spec Kit build)

A single-user todo app built with the **Spec Kit** spec-driven workflow.

- **Core todos** (feature 001): create, view, edit, delete, complete and filter. Saved in SQLite, so they are still
  there after a restart. Works with no AI service, no API key and no network.
- **Assistant** (feature 002, built with LangGraph and GroqCloud): type a plain-English message in the chat box.
  It can turn a sentence into a todo **preview**, suggest a **priority**, or list what is **overdue or due soon**.

- Specs, plans and tasks: [specs/001-core-todo-management/](specs/001-core-todo-management/) and [specs/002-ai-assistant/](specs/002-ai-assistant/)
- Project rules: [.specify/memory/constitution.md](.specify/memory/constitution.md)
- Shared requirements: [docs/requirements.md](docs/requirements.md)

## Run it

Needs Python 3.10 or newer (built and tested on Python 3.14).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in a browser. Interactive API docs are at http://127.0.0.1:8000/docs.
Stop the app with `Ctrl + C`; your todos stay in `todos.db`.

If a package does not install on your Python version, create the environment with Python 3.12 instead
(for example `uv venv --python 3.12`).

## Turn on the Assistant

The todo features work without any setup. The Assistant needs a free GroqCloud key:

1. Create a key at https://console.groq.com.
2. Open `.env` and put it after `GROQ_API_KEY=` (no quotes). Save the file.
3. Restart the app.

Keep the key **only** in `.env`, which is git-ignored. Without a key the chat box says "The AI assistant is not
configured." and everything else keeps working. Groq's free plan limits how many messages you can send per minute;
if you send many quickly you may see "The AI assistant is unavailable right now". Wait a moment and try again.

Try these messages:

| Message | What happens |
|---|---|
| `call mom tomorrow at 5pm` | A **preview** with a due date; **Confirm** saves it, **Cancel** discards it |
| `urgent: fix the login bug today` | A preview with high priority |
| `what priority should 'Submit tax return' be?` | A priority and a reason; if it names a saved todo, **Accept** sets that priority and **Ignore** discards it |
| `what is due soon?` / `anything overdue?` | The active todos that are overdue or due within 24 hours, overdue ones labelled "Overdue" |
| `delete all my todos` | Not done: the Assistant explains that it can never edit or delete |

**The Assistant never changes your todos by itself.** It can only read your active todos and make proposals. A todo
is saved or changed only when *you* press Confirm or Accept, which use the normal todo operations. The due list is built
by the app itself, not guessed by the AI, so it is exact. The model and timeout can be set with `GROQ_MODEL` and
`GROQ_TIMEOUT_SECONDS` in `.env`.

## Run the tests

```bash
python -m pytest
```

Every test uses its own temporary database and a **fake AI model**, and needs no network and no API key. Any key in
your environment is removed for the tests, so a test cannot call Groq by accident.

To also check the real Groq model (needs the key in `.env`; makes real calls):

```bash
RUN_LIVE=1 python -m pytest tests/test_live_groq.py -v
```

If Groq's free-plan limit is reached, those tests pause and retry, and are skipped (not failed) if it persists.
Run them occasionally, not repeatedly. To run part of the file: add `-k "ac10 or ac11"`.

## Settings

Set in `.env` (copy from `.env.example`; `.env` is git-ignored):

| Variable | Meaning | Default |
|---|---|---|
| `TODO_DB_PATH` | Where the SQLite file is stored | `todos.db` |
| `GROQ_API_KEY` | Groq key for the Assistant | empty |
| `GROQ_MODEL` | Which Groq model to use | `openai/gpt-oss-20b` |
| `GROQ_TIMEOUT_SECONDS` | How long to wait for Groq | `15` |

## API

| Method and path | Purpose |
|---|---|
| `GET /` | the web page |
| `POST /todos` | create a todo (`title` required, 1 to 200 characters; optional `description`, `due_date`, `priority`) |
| `GET /todos?status=&priority=` | list; `status` is `all`, `active` or `completed`; `priority` is `low`, `medium` or `high` |
| `GET /todos/{id}` | view one |
| `PATCH /todos/{id}` | change any fields, including `completed`; only the fields you send change |
| `DELETE /todos/{id}` | delete (204) |
| `POST /agent/message` | send `{"message": "..."}` (1 to 500 characters); returns `intent`, `reply`, and one of `preview`, `suggestion` or `reminders`. Never changes any todo. Errors: 422 bad message, 503 AI not configured or unavailable, 502 unusable AI answer |

Details of the Assistant operation: [contracts/http-api.md](specs/002-ai-assistant/contracts/http-api.md).

Unknown ids give a 404 `{"detail": "Todo 42 not found"}`. Invalid input gives a 422 that names the wrong
field. Details: [contracts/http-api.md](specs/001-core-todo-management/contracts/http-api.md).

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
app/agents/   the Assistant: LangGraph graph, orchestrator, Task agent, Priority agent, reminder logic, model access
static/       the web page (index.html), a dark "Console" look (monospace, green accent)
tests/        pytest tests (fake model); test_live_groq.py is the optional real-model check
specs/        Spec Kit feature folders: spec, plan, research, data model, contracts, tasks
.specify/     Spec Kit's toolbox: constitution, templates, scripts
docs/         shared requirements
```

## About the browser checks

The page was checked in a real browser (desktop and 375 px width) with a throwaway script kept outside this
repository, so the repository holds the automated tests (`python -m pytest`) but not the browser script.
