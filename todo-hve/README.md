# Todo App with an AI assistant

A small todo app. You can add, edit, complete, delete and filter todos on a web page, and you can also type plain English to an AI assistant ("call mom tomorrow at 5pm") that prepares a todo for you to confirm.

Stack: Python, FastAPI, SQLite, one HTML page, and a LangGraph agent graph that uses GroqCloud as the language model.

## Run it (about 5 minutes)

You need Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate            # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # on Windows: copy .env.example .env
uvicorn app.main:app --port 8001
```

Open <http://127.0.0.1:8001>. The todo list works right away, with no key and no internet.

Pick any free port. Port 8000 is often taken by another app; to check which app is answering on a port, open `/openapi.json` there: this app's title is `Todo App (HVE build)`.

The todos are saved in a file called `todos.db` in the project folder (change the place with `TODO_DB_PATH` in `.env`).

## Turn the assistant on

The assistant needs a free Groq API key.

1. Create a key at <https://console.groq.com/keys>.
2. Open your `.env` file and paste it after `GROQ_API_KEY=`.
3. Restart the app.

The key lives only in `.env`, which is git-ignored. Never put it in code, in `.env.example`, or in a chat message. The app never writes it to a log, a response or the page.

| Setting (in `.env`) | Meaning | Default |
|---|---|---|
| `GROQ_API_KEY` | Your Groq key. Blank means the assistant is off. | none |
| `GROQ_MODEL` | Which Groq model to use. | `openai/gpt-oss-20b` |
| `GROQ_TIMEOUT_SECONDS` | Longest wait for one model call. A bad value falls back to 15. | `15` |
| `TODO_DB_PATH` | Where the todos are saved. | `todos.db` |

Groq's free tier has a limit on requests per minute. If you hit it, the assistant says it is unavailable for a moment; try again shortly. Core todo features are not affected.

## What to type

| You type | The assistant |
|---|---|
| `call mom tomorrow at 5pm` or `urgent: fix the login bug today` | Shows a todo **preview**. Nothing is saved until you press **Confirm**; **Cancel** discards it. |
| `what priority should 'Submit tax return' be?` | Suggests low, medium or high with a short reason. **Accept** changes that todo's priority; **Ignore** does nothing. |
| `what is due soon?` or `anything overdue?` | Lists todos that are overdue or due in the next 24 hours (built by code, not guessed by the AI). |
| anything else | Says it did not understand and gives examples. |

Messages must be 1 to 500 characters.

### The assistant can only read

The assistant can never create, edit or delete a todo by itself. Its code is not given the storage module, only a function that reads your active todos, and tests fail if that ever changes. Only your **Confirm** and **Accept** presses change anything, and they use the normal todo operations. What you type and what your todos say is treated as data, never as instructions.

### If something goes wrong

| What you see | Why |
|---|---|
| The AI assistant is not configured. | No key in `.env`. |
| The AI assistant is unavailable right now. | Groq could not be reached, was too slow, rejected the key, or rate-limited you. |
| I could not understand the AI's answer. Please try again. | The model's answer was unusable twice in a row. |

In every case nothing is saved or changed and the rest of the app keeps working.

### How long it waits

Each message gets a 20 second budget. No model call starts after it is spent, each call is limited to the time left, and if the model has not answered when the budget ends the assistant stops waiting and says it is unavailable (the unanswered request is dropped in the background). So one message never waits much longer than 20 seconds. Normal replies take a second or two.

## API

| Method and path | What it does |
|---|---|
| `POST /todos` | Create. Body: `title` (1 to 200 characters), optional `description`, `due_date` (date and time, for example `2026-10-23T17:00`), `priority` (`low`, `medium`, `high`; default `medium`). |
| `GET /todos?status=&priority=` | List. `status` is `all`, `active` or `completed`. |
| `GET /todos/{id}` | One todo. |
| `PATCH /todos/{id}` | Change any fields, including `completed`. |
| `DELETE /todos/{id}` | Delete. |
| `POST /agent/message` | Body `{"message": "..."}`. Returns `intent`, `reply` and one of `preview`, `suggestion`, `reminders`. Never changes a todo. |

Bad input gives a 422 that names the field. An unknown id gives a 404 like `Todo 42 not found`.

## Tests

```bash
python -m pytest                                          # default: fake model, no network, no key needed
RUN_LIVE=1 python -m pytest tests/test_live_groq.py -v    # optional: the real Groq model
```

The default run uses a scripted fake model and a temporary database and removes any Groq settings from the environment. The live run reads the key from `.env`; if Groq rate-limits, a test waits and retries a few times and then skips (a skip means "not proven this run", not "passed").

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

## Project layout

```text
app/main.py            the web app and todo API
app/models.py          what a valid todo is
app/storage.py         all SQLite access
app/config.py          settings
app/chat.py            POST /agent/message
app/agents/            graph.py (LangGraph), orchestrator.py, task_agent.py, priority_agent.py,
                       due.py (reminders, plain code), llm.py, structured.py, schemas.py, errors.py
static/index.html      the single page (a "Bold" look: violet-to-pink gradient, rounded cards, coloured chips, dark mode)
tests/                 offline tests, and test_live_groq.py (opt-in)
```
