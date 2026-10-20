# Architecture: Agentic Todo App

The same architecture is used by all three builds (OpenSpec, Spec Kit, HVE). Only the paper trail and the look of the page differ.

![Architecture diagram](architecture.png)

(The diagram source is `architecture.mmd`; `architecture.svg` is the same picture as a scalable file. GitHub and VS Code
also draw the Mermaid below directly.)

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "Arial, Helvetica, sans-serif", "fontSize": "15px", "primaryColor": "#eef2ff", "primaryBorderColor": "#4f46e5", "lineColor": "#475569"}}}%%
flowchart TB
    user(["User in a browser"])

    subgraph UI["Web page: static/index.html"]
        todoUI["Todo list UI<br/>add / edit / complete / delete / filter"]
        chatUI["Assistant card<br/>message, preview Confirm/Cancel,<br/>suggestion Accept/Ignore, reminders"]
    end

    subgraph API["FastAPI: main.py, chat.py"]
        todoAPI["Todo API<br/>POST/GET/PATCH/DELETE /todos"]
        chatAPI["POST /agent/message<br/>validate, run graph, map errors,<br/>log decision line"]
    end

    subgraph CORE["Core: works with no AI"]
        models["models.py<br/>validation"]
        storage["storage.py<br/>SQLite, parameterised SQL"]
        db[("todos.db")]
        models --> storage --> db
    end

    subgraph AGENTS["Assistant: app/agents (read-only)"]
        lg{{"graph.py<br/>LangGraph router"}}
        orch["orchestrator.py<br/>decides the intent"]
        task["task_agent.py<br/>sentence to todo PREVIEW"]
        prio["priority_agent.py<br/>low / medium / high + reason"]
        due["due.py<br/>overdue / due soon<br/>(plain code, no AI)"]
        helpmsg["help reply<br/>(unknown intent)"]
        struct["structured.py<br/>JSON + 1 retry + data blocks"]
        llm["llm.py<br/>call_model, 20 s budget,<br/>safe errors"]
        lg -->|1 decide intent| orch
        orch -->|create_todo| task
        orch -->|suggest_priority| prio
        orch -->|show_due| due
        orch -->|unknown| helpmsg
        orch --> struct
        task --> struct
        prio --> struct
        struct --> llm
    end

    groq[["GroqCloud LLM<br/>(via langchain-groq)"]]
    env[/".env<br/>GROQ_API_KEY (never in code or logs)"/]

    user --> UI
    todoUI -->|fetch| todoAPI
    chatUI -->|fetch| chatAPI
    todoAPI --> models
    chatAPI --> lg
    chatAPI -. "read_todos() function only" .-> storage
    chatUI -->|"Confirm: POST /todos<br/>Accept: PATCH /todos/id"| todoAPI
    llm -->|HTTPS| groq
    env -.-> llm

    classDef safe fill:#ecfdf5,stroke:#059669,color:#064e3b
    classDef ai fill:#fef3c7,stroke:#d97706,color:#78350f
    class due,helpmsg,models,storage,db safe
    class orch,task,prio,struct,llm,groq ai
```

## How to read it

- **Blue** boxes are the app's plumbing (page, routes, router). **Amber** boxes use the AI model. **Green** boxes are plain
  code and data with no AI.
- **Core (right)** is a normal todo app: the page calls the Todo API, `models.py` validates, `storage.py` talks to SQLite.
  It works with no key and no internet.
- **Assistant (left)** is added on top. A message goes to `POST /agent/message`, then a LangGraph router asks the
  orchestrator for the intent, then exactly one of four things runs:
  `task_agent` (sentence to a todo *preview*), `priority_agent` (suggestion), `due.py` (exact reminder list, plain code) or a help reply.
- **Every AI call** goes through `structured.py` (ask for JSON, check it, retry once, wrap user text as data) and `llm.py`
  (one door to Groq with a 20 second budget and safe errors). The key lives only in `.env`.

## The one rule the diagram shows

The assistant is **read-only**. The dotted line from the chat route to `storage.py` carries only a `read_todos()` function;
the agents never import the storage module. Anything the assistant proposes becomes a real change only when you press
**Confirm** or **Accept** on the page, which sends a normal `POST /todos` or `PATCH /todos/{id}` (the line from the
Assistant card to the Todo API). Tests fail if an agent ever gains a way to write.

## Walk-through: "call mom tomorrow at 5pm"

1. The Assistant card sends the text to `POST /agent/message`.
2. The route validates it (1 to 500 characters) and starts the 20 second budget.
3. The graph asks the orchestrator, which answers `create_todo`.
4. `task_agent` asks the model for JSON (title, due date, priority), checked against a printed calendar for weekday dates.
5. The page shows a **preview**. Nothing is saved yet.
6. You press **Confirm**: the page calls `POST /todos`, and only then is the todo stored in `todos.db`.
