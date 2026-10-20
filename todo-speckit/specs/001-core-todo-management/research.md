# Research: Core Todo Management

All technical choices were fixed by the constitution and the feature description, so there were no
open "NEEDS CLARIFICATION" items. This file records each decision with its reasons.

## R-1. Web framework: FastAPI (with Uvicorn)

- **Decision**: FastAPI served by Uvicorn.
- **Rationale**: Fixed by the constitution. Its request models give field-level validation errors
  for free, and it generates interactive API docs, which helps new users try the operations.
- **Alternatives considered**: Flask (no built-in validation, more code); Django (far heavier than
  one page and five operations needs).

## R-2. Storage: standard-library `sqlite3`, parameterised queries only

- **Decision**: One SQLite file accessed through `sqlite3`, all access in `app/storage.py`; the
  table is created on start if it is missing. Column names in dynamic `UPDATE` statements come from a
  fixed allow-list; values always use `?` placeholders.
- **Rationale**: No dependency, one table, easy for a beginner to read. Creating storage on start
  satisfies "no setup step" (spec FR-007).
- **Alternatives considered**: SQLAlchemy or another ORM (heavy for one table, and the constitution
  says no ORM); a JSON file (no atomic updates, easy to corrupt on a crash).

## R-3. Validation: Pydantic models

- **Decision**: Pydantic models for create and for update. Title is trimmed and must be 1 to 200
  characters; priority is one of `low`, `medium`, `high`; the status filter is one of `all`,
  `active`, `completed`; the due date must be a readable date-time.
- **Rationale**: Gives a response that names the wrong field (spec FR-008) without hand-written
  checks, and runs before anything is saved.
- **Alternatives considered**: hand-written checks (repetitive, easy to forget a field).

## R-4. Due date: ISO 8601 local date-time text, time zone accepted

- **Decision**: Store the due date as ISO 8601 text. It must be able to hold a time of day, not only a
  date, because the later AI feature turns "tomorrow at 5pm" into a due time. A value carrying a time
  zone is accepted and stored as given; code that compares it with "now" converts it to local time.
- **Rationale**: Avoids a breaking change later; ISO text sorts correctly and is readable in the
  database. Accepting zone-aware input avoids rejecting valid dates from other programs.
- **Alternatives considered**: date only (cannot represent a time of day); integer timestamps
  (unreadable, and local-time semantics get lost).

## R-5. Status is derived from a `completed` flag

- **Decision**: Store `completed` as a boolean (0 or 1). The response also shows `status` as `active` or
  `completed`, computed from it. Completing and reopening are ordinary edits of `completed`.
- **Rationale**: One source of truth; no extra endpoints for complete and reopen (spec FR-005).
- **Alternatives considered**: a status text column (two fields could disagree); dedicated
  `/complete` and `/reopen` endpoints (more surface for no gain).

## R-6. Edit semantics: PATCH with only the fields that were sent

- **Decision**: `PATCH /todos/{id}` changes only the fields present in the request. `null` is allowed
  for `description` and `due_date` (it clears them) but not for `title`, `priority` or `completed`.
- **Rationale**: Lets the page send small edits and lets a client clear a due date, while still
  protecting required fields (spec FR-003, FR-008).
- **Alternatives considered**: `PUT` with the whole todo (forces clients to resend everything and
  risks overwriting concurrent changes).

## R-7. Identifiers: out-of-range ids mean "not found"

- **Decision**: Ids below 1 or above 2^63 - 1 are treated as "no such todo" (404) and never reach
  the database.
- **Rationale**: SQLite integers are 64-bit; passing a larger number raises an error that would
  surface as a server crash instead of the clear "not found" the spec requires (spec edge cases,
  FR-009). The earlier OpenSpec build found this bug late, so this build plans for it and adds a
  regression test up front (constitution IV).
- **Alternatives considered**: validating the id in the route (returns 422, not the specified
  "not found").

## R-8. Page: one static HTML file with inline CSS and JS, safe DOM methods

- **Decision**: `static/index.html` served at `/`. The script builds elements with `createElement`
  and sets `textContent`; it never writes user text with `innerHTML`. Server errors (which list the
  wrong fields) are turned into plain sentences shown next to the failed action.
- **Rationale**: No build step (constitution VI); text that looks like markup stays inert (spec
  FR-015); one file is easy to read and ship.
  The page also declares an empty inline icon (`<link rel="icon" href="data:,">`). No requirement asks
  for an icon; it exists only so browsers do not request `/favicon.ico`, which would log a failing
  request on every page load. It adds no feature and no file.
- **Alternatives considered**: React or another framework (adds tooling the app does not need);
  server-rendered templates (full page reloads, which the spec rules out).

## R-9. Preparing for the later AI feature without building it

- **Decision**: Keep every database operation in `app/storage.py` and call it only from `app/main.py`.
  Do not add any agent code now.
- **Rationale**: The later feature must give agents a read-only function and nothing that writes
  (constitution I). Having one storage module makes that boundary easy to draw and to test.
- **Alternatives considered**: building agent hooks now (speculative; constitution VI forbids it).

## R-10. Testing approach

- **Decision**: pytest with FastAPI's `TestClient`. Every test gets its own temporary database file
  through an environment variable, so tests never touch real data or each other. Performance is checked
  with a test that stores 1,000 todos and times the operations. The page is checked in a real browser at
  desktop and 375 px widths.
- **Rationale**: Fast, offline and deterministic (constitution IV).
- **Alternatives considered**: mocking the storage layer (would not catch real SQL mistakes).

## R-11. Settings

- **Decision**: One setting now, `TODO_DB_PATH` (default `todos.db`), read from the environment or
  `.env` at call time so tests can override it. `.env` is git-ignored and `.env.example` lists names only.
- **Rationale**: Sets the secrets pattern early (constitution III) with no secret needed yet.
- **Alternatives considered**: hard-coding the path (cannot give tests their own database).
