# Data Model: AI Assistant

Nothing in this feature is stored. These are the shapes that move between the page and the service for one message.
Todos themselves are defined in feature 001 ([../001-core-todo-management/data-model.md](../001-core-todo-management/data-model.md)).
Rules come from [spec.md](spec.md) (FR-001 to FR-018); decisions from [research.md](research.md).

## ChatMessage (request)

| Field | Type | Rules |
|---|---|---|
| `message` | text | Whitespace trimmed; 1 to 500 characters after trimming. Empty, blank or longer is rejected (422, naming `message`) before any AI call |

## Intent

One of `create_todo`, `suggest_priority`, `show_due`, `unknown`. Any other value from the model is treated as `unknown` (R-7).

## AssistantReply (response)

| Field | Type | Rules |
|---|---|---|
| `intent` | Intent | What the assistant understood |
| `reply` | text | The words shown to the user |
| `preview` | TodoPreview or null | Present only for `create_todo` |
| `suggestion` | PrioritySuggestion or null | Present only for `suggest_priority` |
| `reminders` | list of DueItem or null | Present only for `show_due`; `[]` when nothing is due |

At most one of `preview`, `suggestion`, `reminders` is present.

## TodoPreview

A proposed todo that is **not saved**. It must satisfy the same rules as a hand-made todo so Confirm cannot fail.

| Field | Type | Rules |
|---|---|---|
| `title` | text | 1 to 200 characters (a longer model title is cut to 200) |
| `description` | text or null | Optional; blank becomes null |
| `due_date` | ISO 8601 date-time or null | Local time; a date with no time means 09:00 |
| `priority` | `low` \| `medium` \| `high` | Default `medium`; high for urgency words, low for unimportance words |

## PrioritySuggestion

| Field | Type | Rules |
|---|---|---|
| `priority` | `low` \| `medium` \| `high` | Required |
| `reason` | text | One sentence; at most 200 characters (longer is cut) |
| `todo_id` | integer or null | Set only if the id was among the (at most 50) active todos shown to the model |
| `todo_title` | text or null | Taken from the saved todo, never from the model; null when `todo_id` is null |

## DueItem

| Field | Type | Rules |
|---|---|---|
| `id` | integer | The saved todo's id |
| `title` | text | The saved todo's title |
| `due_date` | ISO 8601 date-time | Local time (a time-zone date is converted) |
| `overdue` | boolean | True when due before now; false when due from now to 24 hours ahead |

Selection and order: see R-5 (active only; overdue first, oldest first; then soonest due).

## Not-stored note

There is no chat history. Each message is handled on its own, and nothing about it is kept except the one log line
(intent, agent, outcome, duration; no text).
