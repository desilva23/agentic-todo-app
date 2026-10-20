# Tasks: Core Todo Management

**Input**: Design documents from `/specs/001-core-todo-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http-api.md, quickstart.md
**Tests**: REQUIRED (constitution principle IV): tests are written before the code they cover and must fail first. Every test uses a temporary database, no network and no API key.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: which user story the task belongs to (US1 add and list, US2 update progress, US3 filters, US4 screens and run steps)

## Path Conventions

Single project at the repository root: `app/`, `static/`, `tests/`, plus `requirements.txt`, `.gitignore`, `.env.example`, `README.md`. Run all commands from the repository root with the virtual environment active.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: project skeleton and dependencies

- [X] T001 Create folders `app/`, `static/` and `tests/` with empty `app/__init__.py` and `tests/__init__.py`; verify `ls app tests` shows both `__init__.py` files
- [X] T002 [P] Create `requirements.txt` with exactly these pinned lines: `fastapi==0.146.0`, `uvicorn==0.54.0`, `pydantic==2.14.1`, `pytest==9.1.1`, `httpx==0.28.1`, `python-dotenv==1.2.4`
- [X] T003 [P] Create `.gitignore` containing `.env`, `.venv/`, `*.db`, `__pycache__/` and `.pytest_cache/`; verify with `grep -n '^\.env$' .gitignore`
- [X] T004 [P] Create `.env.example` with a comment line and `TODO_DB_PATH=todos.db` (names and defaults only, never a secret)
- [X] T005 Create `.venv`, run `pip install -r requirements.txt`, and verify `pip list` shows all six packages at the pinned versions and `python -c "import fastapi, pydantic, dotenv, httpx, pytest"` succeeds

**Checkpoint**: environment ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: settings, storage creation, shared types and the app skeleton that every story needs

**CRITICAL**: no user story work can begin until this phase is complete

- [X] T006 [P] Write `tests/test_config.py`: default path is `todos.db` when `TODO_DB_PATH` is unset; setting `TODO_DB_PATH` changes the result without reloading the module (it is read at call time); confirm the tests FAIL
- [X] T007 Implement `app/config.py` with `get_db_path()` that reads `TODO_DB_PATH` from the environment on every call (default `todos.db`) and calls `load_dotenv()` once at import; verify `tests/test_config.py` passes
- [X] T008 [P] Write `tests/test_storage.py` first tests: starting on a missing database file creates it and `list_todos()` returns `[]`; calling `init_db()` twice is safe and keeps existing rows; confirm they FAIL
- [X] T009 Implement `app/storage.py` with `get_db_path`-based `_connect()` (row factory), the `todos` table (columns `id` integer primary key autoincrement, `title` text not null, `description` text, `due_date` text, `priority` text not null default 'medium', `completed` integer not null default 0, `created_at` text not null) and `init_db()` that creates it if missing; verify the T008 tests pass
- [X] T010 Create `tests/conftest.py` with a `db_path` fixture that points `TODO_DB_PATH` at a fresh file under `tmp_path` (using `monkeypatch`) and calls `storage.init_db()`, so every test gets its own empty database; verify an existing test can use it
- [X] T011 [P] Write `tests/test_models.py` shared-type tests: `Priority` accepts only `low`, `medium`, `high`; `StatusFilter` accepts only `all`, `active`, `completed` and its error lists the allowed values; `Title` is "Whitespace trimmed; 1 to 200 characters after trimming" (200 accepted, 201 rejected, `"   "` rejected); confirm they FAIL
- [X] T012 Implement the shared types `Priority`, `StatusFilter` and `Title` in `app/models.py`; verify the T011 tests pass
- [X] T013 Create the FastAPI app skeleton in `app/main.py` (title, a lifespan that calls `storage.init_db()` on start); write a test in `tests/test_api.py` that sets `TODO_DB_PATH` (with `monkeypatch`) to a file under `tmp_path` that does NOT exist yet, does NOT use the `db_path` fixture (which would create the file itself), starts the app with `TestClient` as a context manager, and asserts the file now exists; verify it passes

**Checkpoint**: foundation ready; user stories can begin

---

## Phase 3: User Story 1 - Add todos and see them in a list (Priority: P1) MVP

**Goal**: add a todo (with validation) and see the list; todos survive a restart (spec FR-001, FR-002, FR-007, FR-008, FR-011; AC-1, AC-2, AC-7)

**Independent Test**: add "Buy milk" with nothing else, add a second todo with every field, restart the app: both are listed with the values entered, and "Buy milk" shows medium priority and active status.

### Tests for User Story 1 (write first, confirm they FAIL)

- [X] T014 [P] [US1] In `tests/test_models.py` add `TodoCreate` tests: `title` "Whitespace trimmed; 1 to 200 characters after trimming"; `description` optional text; `due_date` optional "ISO 8601 date-time" that must be readable (a value such as `"someday"` is rejected, a value ending in `Z` is accepted); `priority` "`low` | `medium` | `high`", default `medium`; the validation error names the wrong field
- [X] T015 [P] [US1] In `tests/test_storage.py` add tests for `create_todo`, `get_todo` and `list_todos` (no filters yet): defaults (priority `medium`, `completed` false, `description` and `due_date` null), all fields stored, `created_at` set by the system, creation order by `id`, a title such as `Robert'); DROP TABLE todos;--` is stored safely as plain text, and data written is still returned after `init_db()` is called again (simulated restart)
- [X] T016 [P] [US1] In `tests/test_api.py` add tests for `POST /todos` and `GET /todos` per `contracts/http-api.md`: title only gives 201 with priority `medium`, `status` `active`, `completed` false; all fields given; empty, blank (`"   "`) and 201-character titles give 422 naming `title` and save nothing; a 200-character title is accepted; unknown priority gives 422 naming `priority` and listing `low`, `medium`, `high`; unreadable `due_date` gives 422 naming `due_date`; a `due_date` ending in `Z` is accepted and returned unchanged; list returns `[]` when empty and todos in creation order; a rejected request leaves previously saved todos unchanged
- [X] T017 [P] [US1] Create `tests/test_page.py`: `GET /` returns 200 with content type `text/html`, contains `<title>Todo App</title>` and a `viewport` meta tag

### Implementation for User Story 1

- [X] T018 [US1] Add `TodoCreate` and `Todo` (response, with computed `status` = `completed` when `completed` is true, otherwise `active`; plus `id`, `created_at`) to `app/models.py`, applying the constraints quoted in T014; verify T014 passes
- [X] T019 [US1] Add `create_todo`, `get_todo` and `list_todos` to `app/storage.py` using parameterised SQL only (every value via `?` placeholders); verify T015 passes
- [X] T020 [US1] Add `POST /todos` (status 201) and `GET /todos` to `app/main.py` using `TodoCreate`/`Todo` and the storage functions; verify T016 passes
- [X] T021 [US1] Create `static/index.html` with a viewport meta tag, `<title>Todo App</title>`, an add form (title, description, due date-time, priority select defaulting to Medium) and a todo list that shows title, status, due date and priority, loading `GET /todos` and posting `POST /todos` with `fetch`; build elements with `createElement` and `textContent` only (no `innerHTML` with user text); a failed add shows a plain-language message next to the form (for example "Title is required and must be 1 to 200 characters."); a `due_date` value is shown in the user's local time
- [X] T022 [US1] Add the `GET /` route to `app/main.py` returning `static/index.html` as a file response; verify `tests/test_page.py` (T017) now passes
- [X] T023 [US1] Verify US1 in a real browser (scratch Playwright script outside the repo): add "Buy milk", see medium priority and active status, add a full todo, submit an empty title and see the message with nothing added, time how long add-to-visible takes (SC-001: under 5 seconds), stop and restart the server on the same database and see both todos again

**Checkpoint**: User Story 1 is fully functional and independently testable (the MVP)

---

## Phase 4: User Story 2 - Keep todos up to date (Priority: P2)

**Goal**: edit, complete and reopen, and delete todos; clear "not found" answers (spec FR-003, FR-004, FR-005, FR-009; AC-3, AC-4, AC-5)

**Independent Test**: with three todos, complete one, reopen it, change another's due date, delete the third; each change shows straight away and after a restart.

### Tests for User Story 2 (write first, confirm they FAIL)

- [X] T024 [P] [US2] In `tests/test_models.py` add `TodoUpdate` tests: every field optional and only fields sent are reported; `description` and `due_date` may be `null` (clears them); `title`, `priority` and `completed` "cannot be set to null"; empty or over-200 title rejected; a non-boolean `completed` rejected
- [X] T025 [P] [US2] In `tests/test_storage.py` add `update_todo` and `delete_todo` tests: partial update changes only the given columns, clearing `due_date` with `None`, completing and reopening, unknown id returns `None`/`False`, column names outside the allow-list (`title`, `description`, `due_date`, `priority`, `completed`) are ignored, and **regression tests for R-7**: ids `0`, `-5` and `99999999999999999999` (above 2**63 - 1) return `None` from `get_todo`/`update_todo` and `False` from `delete_todo` without raising
- [X] T026 [P] [US2] In `tests/test_api.py` add tests for `GET /todos/{id}`, `PATCH /todos/{id}` and `DELETE /todos/{id}` per the contract: view existing and unknown (404 with `detail` "Todo 9999 not found"); change a due date and see it in the list; clear it with `null`; an invalid edit (empty title, priority `urgent`) returns 422 and the old value stays; complete then reopen shows `status` `completed` then `active`; edit changes only the sent fields; an empty body changes nothing; delete gives 204 and the todo is gone, a second delete gives 404; **regression tests**: ids `0`, `-5` and `99999999999999999999` give 404 (not 500) for GET, PATCH and DELETE

### Implementation for User Story 2

- [X] T027 [US2] Add `TodoUpdate` to `app/models.py` with the constraints quoted in T024 (a validator rejecting `null` for `title`, `priority` and `completed`); verify T024 passes
- [X] T028 [US2] Add `update_todo` and `delete_todo` to `app/storage.py` using a fixed allow-list for column names and `?` placeholders for values, and an `_id_can_exist(id)` guard (`0 < id <= 2**63 - 1`) used by `get_todo`, `update_todo` and `delete_todo` so out-of-range ids behave as "not found"; verify T025 passes
- [X] T029 [US2] Add `GET /todos/{id}`, `PATCH /todos/{id}` (apply only fields that were sent, using `model_dump(exclude_unset=True)`) and `DELETE /todos/{id}` (204) to `app/main.py`, answering 404 with `{"detail": "Todo {id} not found"}`; verify T026 passes
- [X] T030 [US2] In `static/index.html` add, for each todo: a complete/reopen checkbox, an Edit button that swaps the item for an inline edit form (title, description, due, priority, Save, Cancel) and a Delete button; a failed action shows its plain-language message inside that item, and the list refreshes without a page reload
- [X] T031 [US2] Verify US2 in a real browser: complete and reopen, edit a due date, edit with an empty title (message shown, old title kept), delete, delete a todo behind the page's back (through the API) and then press Complete and Delete on it (a "not found" message appears inside that item and nothing else changes), and confirm the list updates with no reload (a marker set on `window` survives) and everything persists after a restart

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Find what matters with filters (Priority: P3)

**Goal**: filter by status and priority, alone or combined (spec FR-006; AC-6)

**Independent Test**: with active and completed todos of several priorities, choose "completed", then "high", then both: only matching todos show; a filter that matches nothing shows an empty message.

### Tests for User Story 3 (write first, confirm they FAIL)

- [X] T032 [P] [US3] In `tests/test_storage.py` add `list_todos(status, priority)` tests: `all`, `active`, `completed`, each priority, both combined, no match returns `[]`, results stay in creation order
- [X] T033 [P] [US3] In `tests/test_api.py` add filter tests for `GET /todos?status=&priority=`: each status value, each priority value, both combined, no filter returns everything, a filter with no matches returns `[]` with 200, and `status=done` gives 422 naming `status` and listing `all`, `active`, `completed`

### Implementation for User Story 3

- [X] T034 [US3] Extend `list_todos` in `app/storage.py` to accept `status` and `priority`, adding `WHERE` conditions with `?` placeholders only; verify T032 passes
- [X] T035 [US3] Add the `status` (type `StatusFilter`, default `all`) and `priority` (optional `Priority`) query parameters to `GET /todos` in `app/main.py`; verify T033 passes
- [X] T036 [US3] In `static/index.html` add a Show select (All, Active, Completed) and a Priority select (Any, Low, Medium, High) that reload the list, and an empty state "No todos to show." when nothing matches
- [X] T037 [US3] Verify US3 in a real browser: filter active, completed, a priority, both together, and an empty result

**Checkpoint**: all three functional stories work

---

## Phase 6: User Story 4 - Use it on any screen and get it running quickly (Priority: P3)

**Goal**: phone-width layout, plain-language errors everywhere, no full reloads, and written run steps (spec FR-011, FR-012, FR-015, FR-016; NFR-6; AC-17)

**Independent Test**: use every action at 375 px width with no sideways scrolling; follow the README on a clean copy and have the app running quickly.

- [X] T038 [US4] In `static/index.html` make a single function turn server errors into plain sentences (a 422 list becomes "Title is required and must be 1 to 200 characters." / "Priority must be low, medium or high." / "The due date is not a valid date and time." / "Status must be all, active or completed."; a 404 shows its detail; a network failure shows "Could not reach the server. Please try again."), so no raw field paths or status codes are ever shown
- [X] T039 [US4] In `static/index.html` make the layout flexible for 375 px (single column, wrapping rows, controls at least 40 px tall, long words wrapping); add nothing the spec does not ask for (constitution VI: no dark mode or other extras); and verify with the browser that `scrollWidth <= clientWidth` at width 375
- [X] T040 [P] [US4] Write `README.md`: what the app is, exact run steps (create `.venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`, `cp .env.example .env`, `uvicorn app.main:app --reload`, open http://127.0.0.1:8000), the Python 3.12 fallback note, how to run `python -m pytest`, the `TODO_DB_PATH` setting, an API table matching `contracts/http-api.md`, and the project layout
- [X] T041 [US4] Verify US4 in a real browser at 1000 px and 375 px: every control reachable, no sideways scroll, each error kind shows its plain sentence next to the failed action, adds/edits/deletes never reload the page, and a todo created through the API with a `Z` due date is displayed in the correct local time

**Checkpoint**: all user stories complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: checks that span all stories (spec SC-002, SC-003, SC-006, SC-007; constitution gates)

- [X] T042 [P] Add a performance test to `tests/test_api.py`: store 1,000 todos directly, then `GET /todos`, a filtered list and `GET /todos/500` each respond in under 500 ms
- [X] T043 [P] Add an XSS regression check to the browser verification: a todo titled `<img src=x onerror="window.__xss=1">` is displayed as text and `window.__xss` stays undefined
- [X] T044 Run the whole default suite with every network connection blocked (patch `socket.socket.connect` and `socket.create_connection`) and no `GROQ_API_KEY`; verify all tests pass (constitution IV, spec SC-007)
- [X] T045 Secrets scan: search the repository (excluding `.venv`) for `gsk_` and for any key-like string, and verify `.env` is listed in `.gitignore` and no key appears in any file (constitution III)
- [X] T046 Run the README steps on a clean copy of the project (no `.venv`, no `.env`, no `.db`): install, copy `.env.example`, run the tests, start the server, and confirm `/`, `/docs` and a `POST /todos` work (spec SC-006, AC-17)
- [X] T047 Walk through `quickstart.md` scenarios 1 to 12 and acceptance criteria AC-1 to AC-7 in a real browser, including a real server restart for AC-7 and the huge-id "not found" check, and note any item not verified

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; start immediately
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories
- **User Stories (Phases 3 to 6)**: all depend on Foundational
  - US1 (P1) first: it is the MVP and creates the pieces US2 and US3 extend
  - US2 (P2) extends the files US1 created (`models.py`, `storage.py`, `main.py`, `index.html`)
  - US3 (P3) extends `list_todos`, `GET /todos` and the page
  - US4 (P3) refines the page and adds the README; it can start once the page has US1 to US3 content
- **Polish (Phase 7)**: depends on all stories being complete

### Within Each User Story

- Tests are written first and must FAIL before the implementation task that makes them pass
- Types and models before storage, storage before routes, routes before the page, the page before the browser check
- A story is complete (its browser check passes) before the next priority starts

### Parallel Opportunities

- Setup: T002, T003, T004 (different files)
- Foundational: T006, T008 and T011 can be written together (different test files or independent sections)
- Within a story: the test tasks marked [P] touch different test files or sections and can be written together
- T040 (README) can be written alongside T038 and T039
- T042 and T043 are independent of each other

---

## Parallel Example: User Story 1

```bash
# Write all four US1 test groups together (they must fail first):
Task: "Add TodoCreate tests in tests/test_models.py"           # T014
Task: "Add create/get/list tests in tests/test_storage.py"      # T015
Task: "Add POST/GET /todos tests in tests/test_api.py"          # T016
Task: "Create tests/test_page.py"                               # T017
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1)
3. **STOP and VALIDATE**: run T023; the user can already keep a list that survives restarts

### Incremental Delivery

1. Setup + Foundational, then US1 (MVP), validate
2. Add US2 (update progress), validate
3. Add US3 (filters), validate
4. Add US4 (screens and run steps), validate
5. Polish, then run `/speckit-analyze` before implementing and `/speckit-converge` after

---

## Notes

- [P] tasks = different files, no dependencies on unfinished tasks
- [Story] labels trace each task to a user story in `spec.md`
- The later AI feature is a separate feature (`002-...`); nothing here adds agent code
- Every defect found later gets a regression test (constitution IV); T025 and T026 already include the large-id cases found in the earlier OpenSpec build
- Avoid: vague tasks, two tasks editing the same file at once, tests written after the code

---

## Phase 8: Convergence

**Purpose**: remaining work found by `/speckit-converge` after implementation (code assessed against spec, plan, tasks and constitution)

- [X] T048 CRITICAL: Add an autouse fixture to `tests/conftest.py` that removes `GROQ_API_KEY`, `GROQ_MODEL` and `GROQ_TIMEOUT_SECONDS` from the environment for every test, plus a test in `tests/test_config.py` asserting none of them is visible to a test, and verify the suite still passes when run with `GROQ_API_KEY=fake` set in the outer shell per Constitution IV (partial)
- [X] T049 Add a contract test in `tests/test_api.py` that `POST /todos` ignores unknown extra fields (for example `id`, `completed`, `status`, `created_at` and a made-up field): the todo is created as active with a system-assigned id, per contracts/http-api.md POST /todos (partial)
- [X] T050 Review the inline empty icon `<link rel="icon" href="data:,">` in `static/index.html`, which no requirement asks for: justify it in `specs/001-core-todo-management/research.md` R-8 (it stops the browser requesting `/favicon.ico`, which would log a failing request) or remove it, per spec scope (unrequested)
