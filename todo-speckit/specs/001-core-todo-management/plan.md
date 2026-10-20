# Implementation Plan: Core Todo Management

**Branch**: `001-core-todo-management` (no git repository; folder name only) | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-core-todo-management/spec.md`

## Summary

A single-user todo app: create, view, edit, delete, complete and filter todos, saved so they survive
a restart, with one web page for the user and a documented HTTP interface for other programs
(spec FR-001 to FR-016). The approach is deliberately small: a FastAPI service with Pydantic models for
validation, one storage module that is the only code touching SQLite (standard-library `sqlite3`,
parameterised SQL), and one plain HTML/JS page served by the same service. Everything works with no
AI, key or network. The design leaves room for the later AI feature by keeping todo storage behind
a few plain functions that only the route layer calls (see [research.md](research.md), R-9).

## Technical Context

**Language/Version**: Python 3.10 or newer (developed and tested on Python 3.14)

**Primary Dependencies**: FastAPI 0.146.0, Uvicorn 0.54.0, Pydantic 2.14.1, python-dotenv 1.2.4 (all pinned)

**Storage**: SQLite file through the standard-library `sqlite3` module; parameterised queries only; no ORM

**Testing**: pytest 9.1.1 with FastAPI `TestClient` (httpx 0.28.1); a fresh temporary database per test; a real browser check for the page

**Target Platform**: A user's own computer (macOS, Linux or Windows) running the service locally

**Project Type**: web-service with a single static page (backend plus one HTML/JS file, no build step)

**Performance Goals**: every operation under 500 ms with 1,000 stored todos (spec FR-014, SC-002)

**Constraints**: works with no network, no AI and no API key; page usable at 375 px width; no frontend framework; no raw technical errors shown to users

**Scale/Scope**: one user, up to about 1,000 todos, one page, five API operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Applies to this feature? | Check | Result |
|---|---|---|---|
| I. Agents Are Read-Only by Construction | Prepared for, not exercised here (no agents yet) | Storage lives in one module imported only by the route layer; no module outside the route layer may need to import it. The later feature must pass agents a read-only function | PASS |
| II. Core Works Without AI | Yes, central | Nothing in this feature calls an AI service, reads an API key, or needs the network (spec FR-013) | PASS |
| III. Secrets and Private Text Stay Out | Yes | No secret is used here. `.env` pattern and `.gitignore` are set up now; no todo text is logged; errors carry no internals | PASS |
| IV. Test-First and Offline by Default | Yes | Tests per task group, temporary database per test, no network; a regression test for every defect found later | PASS |
| V. Validate at Every Boundary | Yes | Pydantic validates all input; ids outside the storable range are "not found"; SQL is parameterised; user text is data, shown with safe DOM methods | PASS |
| VI. Simplicity and Plain Language | Yes | Standard-library storage, one page, no framework or build; plain-language messages next to the failed action; 375 px layout | PASS |

**Post-design re-check (after Phase 1)**: no change. The data model has one entity, the contract has
five operations, and nothing was added beyond the spec. No violations, so Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-core-todo-management/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output: decisions, rationale, alternatives
├── data-model.md        # Phase 1 output: the Todo entity and its rules
├── quickstart.md        # Phase 1 output: how to run and validate end to end
├── contracts/
│   └── http-api.md      # Phase 1 output: the HTTP interface
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── config.py        # settings from environment / .env (TODO_DB_PATH)
├── models.py        # request and response shapes; all input validation
├── storage.py       # the ONLY module that touches SQLite
└── main.py          # FastAPI app, the five operations, serves the page at /

static/
└── index.html       # the single page: HTML + inline CSS + inline JS

tests/
├── conftest.py      # temporary database fixture
├── test_config.py
├── test_models.py
├── test_storage.py
├── test_api.py
└── test_page.py

docs/requirements.md # shared requirements (source of FR/NFR/AC identifiers)
requirements.txt     # pinned dependencies
.env.example         # variable names only
.gitignore           # .env, .venv/, *.db, __pycache__/
README.md            # exact install and run steps
```

**Structure Decision**: A single project (not a separate frontend and backend), because the page is
one static file served by the same service. One module per job (settings, validation, storage,
routes) keeps each small and lets later features add files without rewriting these.

## Complexity Tracking

No constitution violations. Nothing to justify.
