# Data Model: Core Todo Management

One entity: **Todo**. Rules come from the spec (FR-001 to FR-009); decisions from [research.md](research.md).

## Todo

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | integer | assigned by the system | Starts at 1, increases, never reused for display purposes. Ids below 1 or above 2^63 - 1 cannot exist (R-7) |
| `title` | text | yes | Whitespace trimmed; 1 to 200 characters after trimming; cannot be set to null |
| `description` | text | no | Any text; may be cleared by setting it to null |
| `due_date` | ISO 8601 date-time text | no | Must be readable as a date-time; local time (zone-aware values accepted); may be cleared with null |
| `priority` | `low` \| `medium` \| `high` | no (default `medium`) | Any other value is rejected; cannot be set to null |
| `completed` | boolean | no (default false) | Cannot be set to null |
| `created_at` | ISO 8601 date-time text | assigned by the system | Local time when created; never edited |

**Derived field**: `status` = `completed` if `completed` is true, otherwise `active`. It is shown in
responses and is not stored.

## Storage table

A single table `todos` with columns matching the fields above (`completed` stored as 0 or 1). The
table is created on start if it does not exist. All access is through `app/storage.py`.

## State transitions

```text
        create                     complete
 (none) ------> active  ------------------------> completed
                  ^                                   |
                  |              reopen               |
                  +-----------------------------------+
 any state --delete--> (gone)
```

Completing and reopening are edits of the `completed` field (R-5). A todo can be edited or deleted in
either state.

## Filters (list operation)

| Filter | Allowed values | Default |
|---|---|---|
| `status` | `all`, `active`, `completed` | `all` |
| `priority` | `low`, `medium`, `high` | none (no priority filtering) |

Both may be combined. Results are returned in creation order (ascending `id`).

## Validation summary

| Input | Rejected when | Response |
|---|---|---|
| `title` | empty after trimming, or over 200 characters, or null on edit | 422 naming `title` |
| `priority` | not one of the three values, or null on edit | 422 naming `priority`, listing allowed values |
| `due_date` | not a readable date-time | 422 naming `due_date` |
| `completed` | not a boolean, or null on edit | 422 naming `completed` |
| `status` filter | not `all`, `active` or `completed` | 422 naming `status`, listing allowed values |
| `id` | does not exist, or is outside the storable range | 404 "not found" |

A rejected request changes nothing (spec FR-008).
