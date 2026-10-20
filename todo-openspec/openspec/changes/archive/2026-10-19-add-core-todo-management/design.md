# Design

## Context

This is a new project with no code. The stack is fixed by the project context: Python, FastAPI, SQLite and one plain HTML/JS page. See `proposal.md` for the reason this change comes first. The later `add-agent-chat` change will add agents that read and propose todos, so the todo code must be usable from Python code and not only through HTTP.

## Goals / Non-Goals

**Goals:**
- A small, clear code layout with separate API, storage and (later) agent parts (NFR-7).
- Todo logic that can be called from the API now and from agents later, without going through HTTP.
- Tests that run quickly, with no network and no API key (NFR-8).

**Non-Goals:**
- Any LLM or LangGraph code (next change).
- A database migration system or an ORM.
- Authentication, pagination, or sorting options beyond what the specs require.

## Decisions

### 1. Project layout
```
app/
  main.py        FastAPI app, routes, serves the web page
  models.py      request/response shapes and validation
  storage.py     all SQLite access
  config.py      settings read from environment / .env
static/
  index.html     the single page (HTML + inline JS/CSS)
tests/
```
**Why:** one file per job keeps it easy to read. The agents later get their own `app/agents/` folder. *Alternative:* everything in one `main.py`. Rejected because it mixes concerns and makes later agent code harder to add cleanly.

### 2. Storage with Python's built-in `sqlite3`
Storage is one small module with plain SQL, one `todos` table, and the database file path read from configuration (default `todos.db`). The table is created on startup if missing.
**Why:** no extra dependency, and the data model is a single table. *Alternative:* SQLAlchemy. Rejected as too heavy for one table, and harder for a beginner to follow.

### 3. Validation with Pydantic models
Title length, the priority list (low, medium, high), and the date format are enforced by Pydantic models used by FastAPI. FastAPI then returns a clear 422 error that names the bad field.
**Why:** it is built into FastAPI and matches the "clear error naming the field" scenarios. *Alternative:* hand-written checks. Rejected as repetitive and easy to get wrong.

### 4. Data shape
| Field | Type | Notes |
|---|---|---|
| `id` | integer | assigned by the database |
| `title` | text | required, 1–200 characters |
| `description` | text or null | optional |
| `due_date` | ISO 8601 date-time text or null | local time, no time zone (see assumption 6 in requirements) |
| `priority` | text | `low`, `medium` or `high`; default `medium` |
| `completed` | boolean | default false; the API also shows this as status `active` or `completed` |
| `created_at` | ISO 8601 date-time text | set by the server |

**Why a date-time and not only a date:** the agent feature must turn "tomorrow at 5pm" into a due time, so the field must hold a time from the start. Changing it later would be a breaking change.

### 5. API shape
| Method and path | Purpose |
|---|---|
| `POST /todos` | create |
| `GET /todos?status=&priority=` | list, with optional filters |
| `GET /todos/{id}` | view one |
| `PATCH /todos/{id}` | change any subset of fields, including `completed` |
| `DELETE /todos/{id}` | delete |

Status filter values: `all`, `active`, `completed`. Unknown ids return 404.
**Why PATCH for completion:** completing and reopening are just changes to the `completed` field, so no extra endpoints are needed.

### 6. Web page
One `static/index.html` with inline CSS and JavaScript, using the browser's `fetch` to call the API. FastAPI serves it at `/`. The layout is a single column with flexible widths so it fits a 375 px screen.
**Why:** no build step and no framework, as the project context requires. *Alternative:* React. Rejected because it adds tooling that this app does not need.

### 7. Settings and secrets
`config.py` reads settings from environment variables, loaded from `.env` when present. `.env` is in `.gitignore`, and `.env.example` documents the variable names without values. No Groq key is needed in this change, but the pattern is set now.

### 8. Testing
`pytest` with FastAPI's `TestClient`. Each test uses a fresh temporary database file, so tests never touch real data and do not depend on each other. Tests are written to match the spec scenarios one to one where practical.

## Risks / Trade-offs

- **Raw SQL is easy to get wrong** → use parameterised queries only, never string-built SQL; cover every storage function with a test.
- **Naive local date-times can be ambiguous across time zones** → accepted for a single-user local app (requirements assumption 1 and 6).
- **Inline JS in one HTML file can get long** → acceptable for this size; revisit only if the page grows well beyond the specs.
- **SQLite allows limited concurrent writes** → acceptable for a single user.
