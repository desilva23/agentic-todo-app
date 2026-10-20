# Tasks

## 1. Project setup

- [x] 1.1 Create the folders `app/`, `static/`, `tests/` and verify `app/__init__.py` and `tests/__init__.py` exist
- [x] 1.2 Create `requirements.txt` (fastapi, uvicorn, pytest, httpx, python-dotenv), create a `.venv`, install, and verify `pip list` shows each package. If a package fails on the installed Python version, use a Python 3.12 environment instead and note it in the README
- [x] 1.3 Create `.gitignore` (must include `.env`, `.venv/`, `*.db`, `__pycache__/`) and `.env.example` (variable names only, no values), and verify `.env` is listed in `.gitignore`
- [x] 1.4 Implement `app/config.py` that reads the database path from an environment variable (default `todos.db`) and verify with a small test that overriding the variable changes the path

## 2. Storage (todo-persistence)

- [x] 2.1 Implement `app/storage.py` with table creation on startup, using parameterised SQL only, and verify a test that starts on a missing database file returns an empty list
- [x] 2.2 Implement create, get, list, update and delete functions in `app/storage.py` and verify unit tests for each pass against a temporary database
- [x] 2.3 Add a test that data written, then read through a fresh connection (simulating a restart), is unchanged, and a test that a deleted todo stays deleted

## 3. Models and validation (todo-management)

- [x] 3.1 Implement `app/models.py` with create, update (all fields optional) and response models: title 1–200 characters, priority limited to low/medium/high with default medium, optional ISO date-time due date; verify unit tests for the empty title, 201-character title and "urgent" priority cases are rejected
- [x] 3.2 Add the status filter type (`all`, `active`, `completed`) and verify an unknown value is rejected with the allowed values listed

## 4. REST API (todo-management)

- [x] 4.1 Implement `POST /todos` and verify tests for the "title only" and "all fields" scenarios pass
- [x] 4.2 Implement `GET /todos` (with optional `status` and `priority` filters) and `GET /todos/{id}`, and verify tests for list with items, empty list, each filter, combined filters, invalid filter and unknown id pass
- [x] 4.3 Implement `PATCH /todos/{id}` (including `completed`) and verify tests for changing the due date, invalid edit leaves the old value, complete, reopen, and unknown id pass
- [x] 4.4 Implement `DELETE /todos/{id}` and verify tests for deleting an existing todo and an unknown id pass
- [x] 4.5 Add a test that starts the app with no Groq key set and exercises create, list, edit, complete, filter and delete, verifying it all succeeds
- [x] 4.6 Add a test that a rejected request leaves previously saved todos unchanged

## 5. Web page (todo-web-page)

- [x] 5.1 Serve `static/index.html` at `/` from `app/main.py` and verify a test that `GET /` returns the page with status 200
- [x] 5.2 Build the page: list view showing title, status, due date and priority, and verify in a browser that existing todos are displayed
- [x] 5.3 Add the add-todo form, edit, delete and complete controls that update the list without a page reload, and verify each action in a browser against the page scenarios
- [x] 5.4 Add status and priority filters and verify in a browser that selecting "active" shows only active todos
- [x] 5.5 Show readable error messages beside the failed action (for example "Title is required") and verify an empty title shows the message and adds nothing
- [x] 5.6 Make the layout work at 375 px width with no horizontal scroll and verify using the browser's device toolbar

## 6. Documentation and final checks

- [x] 6.1 Write `README.md` with the exact setup and run commands (create venv, install, copy `.env.example` to `.env`, run `uvicorn`) and verify the commands work as written from a clean checkout
- [x] 6.2 Run the full test suite with no network access and no API key and verify all tests pass (AC-16)
- [x] 6.3 Search the repository for secrets and verify no API key appears in any committed file (AC-15)
- [x] 6.4 Walk through AC-1 to AC-7 by hand in the browser and verify each passes

## Workflow follow-up

- Review the implementation against the specs, then archive the change with `/opsx:archive`.
- Start the next change, `add-agent-chat`, for FR-10 to FR-17.
