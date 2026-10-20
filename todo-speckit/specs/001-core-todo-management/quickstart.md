# Quickstart: validate Core Todo Management end to end

A run-and-check guide for this feature. Details of shapes are in [data-model.md](data-model.md) and
[contracts/http-api.md](contracts/http-api.md).

## Prerequisites

- Python 3.10 or newer
- A terminal in the project folder

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Interactive API docs are at http://127.0.0.1:8000/docs.

## Automated checks

```bash
python -m pytest
```

Expected: all tests pass with no network access.

## Manual validation scenarios

| # | Do this | Expected | Spec reference |
|---|---|---|---|
| 1 | Add a todo titled "Buy milk" and nothing else | It appears with medium priority and active status | AC-1, FR-001, FR-002 |
| 2 | Submit an empty title; then a 201-character title | A message names the title field; nothing is added | AC-2, FR-008 |
| 3 | Edit a todo's due date | The list shows the new date | AC-3, FR-003 |
| 4 | Delete a todo | It disappears | AC-4, FR-004 |
| 5 | Mark a todo complete, then mark it again | It shows completed, then active | AC-5, FR-005 |
| 6 | Filter by "completed", then by high priority, then both | Only matching todos show; a filter with no matches shows an empty message | AC-6, FR-006 |
| 7 | Stop the app (Ctrl+C) and start it again | All todos are still there | AC-7, FR-007 |
| 8 | Open the page at 375 px width and do every action above | No sideways scrolling; everything reachable | NFR-6, FR-012 |
| 9 | Request a todo that does not exist, including `/todos/99999999999999999999` | A clear "not found" response, not a crash | FR-009 |
| 10 | Add a todo titled `<img src=x onerror=alert(1)>` | The text is shown as typed; nothing runs | FR-015 |
| 11 | Start with no network and no `.env` values | Everything above still works | FR-013 |
| 12 | Time a fresh setup following only this guide | Running in under 10 minutes | AC-17, SC-006 |

## Performance check

Store 1,000 todos (the test suite does this), then list, filter and fetch one: each completes in
under 500 ms (spec FR-014, SC-002).
