# Contract: `POST /agent/message`

The only new operation in this feature. Feature 001's operations ([../../001-core-todo-management/contracts/http-api.md](../../001-core-todo-management/contracts/http-api.md))
are unchanged and are what the page calls for Confirm (`POST /todos`) and Accept (`PATCH /todos/{id}`).
Shapes are defined in [../data-model.md](../data-model.md).

## Request

```json
{ "message": "call mom tomorrow at 5pm" }
```

`message`: required, trimmed, 1 to 500 characters.

## Responses

### 200: create

```json
{
  "intent": "create_todo",
  "reply": "Here is the todo I understood. Press Confirm to save it, or Cancel to discard it.",
  "preview": { "title": "Call mom", "description": null, "due_date": "2026-10-20T17:00:00", "priority": "medium" },
  "suggestion": null,
  "reminders": null
}
```

### 200: priority

```json
{
  "intent": "suggest_priority",
  "reply": "For \"Submit tax return\" I suggest high priority. Due tomorrow.",
  "preview": null,
  "suggestion": { "priority": "high", "reason": "Due tomorrow.", "todo_id": 7, "todo_title": "Submit tax return" },
  "reminders": null
}
```

With no matching saved todo: `todo_id` and `todo_title` are `null`, and the reply ends with "(No saved todo matched, so
this is based on your description.)".

### 200: due

```json
{
  "intent": "show_due",
  "reply": "2 todos need attention: 1 overdue, 1 due soon.\n- Overdue: Submit report (was due yesterday, 17:00)\n- Due soon: Call mom (due today, 17:00)",
  "preview": null,
  "suggestion": null,
  "reminders": [
    { "id": 2, "title": "Submit report", "due_date": "2026-10-18T17:00:00", "overdue": true },
    { "id": 1, "title": "Call mom", "due_date": "2026-10-19T17:00:00", "overdue": false }
  ]
}
```

With nothing due: `reply` is `Nothing is overdue or due in the next 24 hours.` and `reminders` is `[]`.

### 200: anything else

`intent` is `unknown`; `reply` says it did not understand, gives example messages, and says the assistant can create todos,
suggest priorities and show what is due but cannot edit or delete todos. `preview`, `suggestion` and `reminders` are `null`.

## Errors

| Status | When | `detail` |
|---|---|---|
| 422 | `message` missing, blank, or over 500 characters | A list naming the field `message` (no AI call is made) |
| 503 | No key is configured | `The AI assistant is not configured.` |
| 503 | The AI cannot be reached, is too slow, rate-limits, or rejects the key | `The AI assistant is unavailable right now.` |
| 502 | The AI's answer cannot be understood, even after one retry | `I could not understand the AI's answer. Please try again.` |

Error text is fixed. It never contains the key or any text from the AI provider.

## Guarantees

- The operation **never creates, changes or deletes a todo**. A preview or suggestion is only a proposal.
- Validation of `message` happens before the key is checked: an empty message is a 422 even with no key.
- A failure leaves every saved todo exactly as it was, and feature 001's operations keep working.
- The key, the message text and todo titles never appear in a response (other than a todo title the user already
  has, shown in a suggestion or a due list) or in any log. One log line per message records only intent, agent, outcome
  and duration.
- The due list is built by the system, not by the AI, and contains every overdue or due-within-24-hours active todo.
