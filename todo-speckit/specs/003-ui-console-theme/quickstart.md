# Quickstart: seeing and checking the Console look

## Prerequisites

Set up the project as in the README (virtual environment, `pip install -r requirements.txt`).

## Run it (pick a FREE port; port 8000 may be another app)

```bash
uvicorn app.main:app --port 8002
```

Open the page and confirm which app answers: `/openapi.json` should show the title `Todo App (Spec Kit build)`.

## Scenarios

1. **Look**: the page is near-black with light monospace text, square panels, headings `> assistant`, `> new todo`, `> filter`, and green primary buttons.
2. **Always dark**: set the computer to light mode and reload: still dark.
3. **Chips**: add a high-priority todo: the row shows `[high]` and `[active]`.
4. **Reminders**: ask the assistant "what is due soon?" with an overdue todo saved: reminders read `[overdue]` / `[due soon]`.
5. **Behaviour unchanged**: add, edit, complete, delete and filter todos; use the assistant (preview Confirm/Cancel, suggestion Accept/Ignore, an error).
6. **Phone width**: make the window 375 px wide: nothing scrolls sideways and every button is on screen.
7. **Text safety**: a todo titled `<img src=x onerror=alert(1)>` shows as plain text.

## Automated checks

```bash
python -m pytest        # includes the page tests and the contrast test
```
