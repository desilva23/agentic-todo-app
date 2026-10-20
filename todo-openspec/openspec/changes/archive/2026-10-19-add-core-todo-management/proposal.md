# Proposal

## Why

The project has no code yet. Before any AI agent features can exist, users need a working todo app they can use without AI: create, view, edit, delete, complete and filter todos, with data that survives a restart. This is also the safe fallback required when the LLM is unavailable (FR-17, NFR-3), so it must come first.

## What Changes

- Add a FastAPI backend with a REST API to create, list, get, update and delete todos (FR-1 to FR-5, FR-9).
- Add filtering of the todo list by status and priority (FR-6).
- Add SQLite storage so todos persist across restarts (FR-7).
- Add input validation with clear error messages (FR-1, FR-9, NFR-5).
- Add a single plain HTML/JS page, served by FastAPI, for managing todos on desktop and phone-width screens (FR-8, NFR-6).
- Add automated tests for the API and storage (NFR-8).
- Add project setup: dependency list, `.env.example`, `.gitignore`, short README with run steps (NFR-4, NFR-10).

## Capabilities

### New Capabilities
- `todo-management`: creating, listing, viewing, editing, deleting and completing todos through the REST API, including validation and filtering by status and priority.
- `todo-persistence`: saving todos in SQLite so they remain after the app restarts.
- `todo-web-page`: a single web page for managing todos (add, edit, delete, complete, filter) that works on desktop and phone-width screens.

### Modified Capabilities
<!-- None. This is the first change; there are no existing specs. -->

## Out of Scope

- The chat box, the LangGraph agents and anything that calls Groq (FR-10 to FR-17). These come in a later change, `add-agent-chat`.
- User accounts, login, multiple users, deployment, notifications, languages other than English.
- A frontend framework or build step; the page is plain HTML/JS.

## Impact

- **New code:** `app/` (FastAPI app, models, storage), `static/` (the web page), `tests/`.
- **New files:** `requirements.txt`, `.env.example`, `.gitignore`, `README.md`.
- **Dependencies:** FastAPI, Uvicorn, pytest, httpx (for API tests). No LLM dependencies yet.
- **Requirements covered:** FR-1 to FR-9, NFR-1, NFR-3 (partly), NFR-6, NFR-7, NFR-8, NFR-10.
- **Acceptance criteria covered:** AC-1 to AC-7, AC-16, AC-17.
