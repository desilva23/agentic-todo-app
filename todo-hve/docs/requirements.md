# Agentic Todo App: Requirements Document

**Version:** 1.0 (draft for review)
**Used for:** three builds of the same app, one each with OpenSpec, Spec Kit and Hyper-Velocity Engineering (HVE)
**Stack:** FastAPI (Python), LangGraph, GroqCloud (LLM), SQLite

---

## 1. Purpose and Scope

### 1.1 Purpose
Build a simple todo app where a user can manage tasks normally (add, edit, delete, complete) **and** by typing plain English to AI agents (for example, "remind me to call mom tomorrow at 5pm").

The same requirements are used to build the app three times, each with a different method, so the methods can be compared fairly.

### 1.2 In scope
- A todo web page and a REST API.
- Saved data (todos survive a restart).
- A small multi-agent feature built with LangGraph that uses Groq as the LLM.

### 1.3 Out of scope
User accounts and login, multiple users, native mobile apps, cloud deployment, notifications by email or SMS, languages other than English, and a written comparison report of the three build methods.

### 1.4 Glossary
| Term | Meaning |
|---|---|
| Todo | One task with a title, status, due date and priority |
| Agent | A LangGraph node that uses the LLM to do one specific job |
| Orchestrator | The agent that reads the user's message and decides which agent handles it |

---

## 2. Functional Requirements

### 2.1 Core todo features
| ID | Requirement |
|---|---|
| FR-1 | The user can **create** a todo with a title (required, 1–200 characters), an optional description, an optional due date and a priority (low, medium or high; default medium). |
| FR-2 | The user can **view a list** of all todos, showing title, status, due date and priority. |
| FR-3 | The user can **edit** any field of an existing todo. |
| FR-4 | The user can **delete** a todo. |
| FR-5 | The user can **mark** a todo as complete, and mark it as not complete again. |
| FR-6 | The user can **filter** the list by status (all, active, completed) and by priority. |
| FR-7 | Todos are **saved** in SQLite and are still there after the app restarts. |
| FR-8 | The app has a **web page** that supports FR-1 to FR-6 and the agent chat box (FR-10). |
| FR-9 | The app has a **REST API** for FR-1 to FR-6 (create, list, get, update, delete, with filters on list). The API validates input and returns clear error messages. |

### 2.2 Agentic features
| ID | Requirement |
|---|---|
| FR-10 | The web page has a **chat box** where the user types a message in plain English. The message is sent to an agent endpoint (`POST /agent/message`). |
| FR-11 | The **Orchestrator agent** reads the message and decides its intent: *create a todo*, *suggest a priority*, *show what is due or overdue*, or *unknown*. It routes the message to the matching agent. |
| FR-12 | The **Task agent** turns a message like "call mom tomorrow at 5pm" into a structured todo (title, due date, priority). It returns this as a **preview**. The todo is saved only after the user confirms. |
| FR-13 | The **Priority agent** suggests low, medium or high for a todo, with a one-sentence reason. The user can accept or ignore it. |
| FR-14 | The **Reminder agent** finds todos that are overdue or due within the next 24 hours and returns a short, readable summary. |
| FR-15 | If the intent is *unknown*, the agent replies that it did not understand and gives two or three example messages. |
| FR-16 | Agents may only **create previews, suggest, and read** todos. Agents must **never delete or edit** a todo on their own. |
| FR-17 | **Fallback:** if Groq is unreachable, the API key is missing or the LLM returns unusable output, the agent endpoint returns a clear error message. All core features (FR-1 to FR-9) keep working. |

### 2.3 Agent flow (overview)
```
User message → Orchestrator ─┬→ Task agent      → todo preview → user confirms → saved
                             ├→ Priority agent  → suggested priority
                             ├→ Reminder agent  → overdue / due-soon summary
                             └→ Unknown         → help message
```

---

## 3. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | Core API calls (FR-1 to FR-6) respond in under **500 ms** for up to 1,000 todos when run locally. |
| NFR-2 | Performance | Agent responses arrive in under **10 seconds** in normal conditions. The page shows a loading indicator while waiting. |
| NFR-3 | Reliability | A failure in the agent feature never crashes the app or loses saved todos (see FR-17). |
| NFR-4 | Security | The Groq API key is kept in a `.env` file, which is listed in `.gitignore`. The key is never written in code, logs or the web page. |
| NFR-5 | Security | All user input is validated on the server. Agent output is checked against a fixed schema before use. The app treats user text as data, not as instructions to the app. |
| NFR-6 | Usability | The page is usable on both a desktop and a phone-width screen. Errors are shown in plain language. |
| NFR-7 | Maintainability | Code is split into clear parts: API, storage, and one module per agent. Each agent is a separate LangGraph node. |
| NFR-8 | Testability | Core features have automated tests. Agent tests use a **mocked LLM**, so they run without a key or network access. |
| NFR-9 | Observability | The app logs each agent decision (intent chosen, agent used, success or failure) without logging secrets. |
| NFR-10 | Portability | The app installs and starts with a short, documented set of commands (create a virtual environment, install requirements, copy `.env.example`, run `uvicorn`). |
| NFR-11 | Consistency | All three builds meet the **same** requirements and acceptance criteria, so the methods can be compared fairly. |

---

## 4. Acceptance Criteria

Each criterion is written as Given / When / Then so it can be tested directly.

### 4.1 Core features
| ID | Covers | Criterion |
|---|---|---|
| AC-1 | FR-1 | **Given** the app is running, **when** I create a todo titled "Buy milk" with no other fields, **then** it appears in the list with priority medium and status active. |
| AC-2 | FR-1, FR-9 | **Given** I submit an empty title or a title over 200 characters, **when** I save, **then** the todo is rejected with a clear error and nothing is saved. |
| AC-3 | FR-3 | **Given** an existing todo, **when** I change its due date, **then** the list shows the new date. |
| AC-4 | FR-4 | **Given** an existing todo, **when** I delete it, **then** it no longer appears in the list. |
| AC-5 | FR-5 | **Given** an active todo, **when** I mark it complete, **then** it shows as completed, and marking it again returns it to active. |
| AC-6 | FR-6 | **Given** a mix of active and completed todos, **when** I filter by "completed", **then** only completed todos are shown. |
| AC-7 | FR-7 | **Given** saved todos, **when** I stop and restart the app, **then** all todos are still present. |

### 4.2 Agentic features
| ID | Covers | Criterion |
|---|---|---|
| AC-8 | FR-11, FR-12 | **Given** I type "call mom tomorrow at 5pm", **when** the agent responds, **then** I see a preview with title "Call mom", tomorrow's date at 17:00 and a priority, and **no todo is saved yet**. |
| AC-9 | FR-12 | **Given** a preview is shown, **when** I confirm, **then** the todo is saved and appears in the list. **When** I cancel instead, **then** nothing is saved. |
| AC-10 | FR-13 | **Given** a todo "Submit tax return, due tomorrow", **when** I ask for a priority suggestion, **then** I get low, medium or high with a one-sentence reason. |
| AC-11 | FR-14 | **Given** one overdue todo and one due in 3 hours, **when** I ask "what is due soon?", **then** the reply mentions both and clearly marks the overdue one. |
| AC-12 | FR-15 | **Given** I type "blah blah", **when** the agent responds, **then** it says it did not understand and shows example messages. |
| AC-13 | FR-16 | **Given** I type "delete all my todos", **when** the agent responds, **then** no todo is deleted or changed, and the reply explains that agents cannot delete. |
| AC-14 | FR-17, NFR-3 | **Given** the Groq key is missing or invalid, **when** I use the chat box, **then** I see a clear error, and I can still create, edit, delete and filter todos normally. |

### 4.3 Non-functional checks
| ID | Covers | Criterion |
|---|---|---|
| AC-15 | NFR-4 | A search of the repository finds no API key in any committed file, and `.env` is in `.gitignore`. |
| AC-16 | NFR-8 | The automated test suite runs and passes with no network access and no API key. |
| AC-17 | NFR-10 | A new person can follow the README and have the app running in under 10 minutes. |

---

## 5. Assumptions

1. **Single user, no login.** The app runs on the user's own computer.
2. **Python 3.10 or newer** is installed.
3. **A free Groq API key** is available and supplied by the user through `.env`.
4. **Groq free-tier limits** (requests per minute) are enough for normal testing. Heavy use may be rate limited.
5. **English only.** The agents are not required to understand other languages.
6. **Time zone:** words like "tomorrow" use the computer's local time zone.
7. **LLM output is imperfect.** The agents may sometimes misread a message, which is why the user confirms before a todo is saved (FR-12).
8. **Simple UI.** One HTML/JS page served by FastAPI is enough; no frontend framework is required.
9. **SQLite** is sufficient for storage. No separate database server is needed.
10. **Same requirements for all three builds.** OpenSpec, Spec Kit and HVE each receive this document as input. Each method produces its own specs, plans and tasks from it, in its own format.
11. **No deployment.** Running locally is enough.
12. **Specific Groq model:** the choice of model is made during the build. It should be set in configuration, not hard-coded.

---

## 6. Decisions Made in Review
| Question | Decision |
|---|---|
| Should the priority agent run automatically when a todo is created? | **No.** It runs only on request (FR-13). |
| Is a confirmation step wanted before saving agent-created todos? | **Yes.** The user must confirm the preview before anything is saved (FR-12, AC-9). |
| Is a comparison report of the three methods required? | **No.** It is out of scope. |
