# Agentic Todo App: built three ways

One todo app with an AI assistant, built **three times from the same requirements**, each with a different AI-assisted
development method, so the methods can be compared fairly.

| Folder | Method | UI look |
|---|---|---|
| [`todo-openspec/`](todo-openspec) | OpenSpec (delta specs, propose / apply / archive) | "Paper": calm, light, serif |
| [`todo-speckit/`](todo-speckit) | Spec Kit (constitution, specify / plan / tasks / implement) | "Console": dark, monospace |
| [`todo-hve/`](todo-hve) | HVE (research / plan / implement / review) | "Bold": gradient, rounded cards |

Every app has the same features: add, edit, complete, delete and filter todos, plus a chat box where plain English
("call mom tomorrow at 5pm") is routed by a LangGraph agent graph (Task, Priority and Reminder agents) using GroqCloud.
The assistant can **only read** todos; nothing is saved until you press Confirm or Accept.

Stack: Python, FastAPI, SQLite, LangGraph, GroqCloud, one plain HTML/JS page.

## Read these first

- [`COMPARISON.md`](COMPARISON.md): the three methods side by side, with measured numbers and honest caveats
- [`ARCHITECTURE.md`](ARCHITECTURE.md): the architecture diagram (shared by all three apps)
- [`requirements.md`](requirements.md): the shared requirements all three were built from

## Run an app

Each folder has its own `README.md` with the steps. In short:

```bash
cd todo-hve            # or todo-openspec / todo-speckit
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your own GROQ_API_KEY to turn the assistant on (optional)
python -m pytest       # offline tests, no key needed
uvicorn app.main:app --port 8001
```

## Secrets

The Groq key lives only in each app's `.env` file, which is git-ignored and **not** in this repository. Use
`.env.example` as the template and add your own key.
