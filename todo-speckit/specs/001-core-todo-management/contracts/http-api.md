# Contract: HTTP interface for todos

Serves the web page and the same operations to other programs (spec FR-010, FR-011). Data shapes are
defined in [../data-model.md](../data-model.md). All request and response bodies are JSON.

## Todo (response shape)

```json
{
  "id": 1,
  "title": "Buy milk",
  "description": null,
  "due_date": "2026-10-20T17:00:00",
  "priority": "medium",
  "completed": false,
  "created_at": "2026-10-19T09:00:00",
  "status": "active"
}
```

## Operations

| Method and path | Purpose | Success | Errors |
|---|---|---|---|
| `GET /` | The web page | 200, HTML | - |
| `POST /todos` | Create a todo | 201, the todo | 422 invalid field |
| `GET /todos` | List todos | 200, a list of todos (empty list when none) | 422 invalid filter value |
| `GET /todos/{id}` | View one todo | 200, the todo | 404 not found |
| `PATCH /todos/{id}` | Change fields, including `completed` | 200, the updated todo | 404 not found; 422 invalid field |
| `DELETE /todos/{id}` | Delete a todo | 204, no body | 404 not found |

### `POST /todos`

Request body: `title` (required); `description`, `due_date`, `priority` (optional).

- Priority defaults to `medium`; the new todo is active.
- Unknown extra fields are ignored.

### `GET /todos`

Query parameters (both optional):

- `status`: `all` (default), `active` or `completed`
- `priority`: `low`, `medium` or `high`

Returns todos in creation order. A filter that matches nothing returns `[]`, not an error.

### `PATCH /todos/{id}`

Request body: any subset of `title`, `description`, `due_date`, `priority`, `completed`.

- Only the fields sent are changed.
- `description` and `due_date` may be `null` to clear them; `title`, `priority` and `completed` may not.
- An empty body changes nothing and returns the todo as it is.

## Error shapes

- **404**: `{"detail": "Todo 42 not found"}`. Also returned for ids that can never exist (below 1 or above 2^63 - 1).
- **422**: `{"detail": [{"loc": ["body", "title"], "msg": "...", "type": "..."}]}`. The last item of `loc` is the name of the wrong field. The page turns this into a plain sentence; other programs may read it directly.

## Guarantees

- A rejected request (422 or 404) leaves all saved todos unchanged.
- Every operation responds in under 500 ms with up to 1,000 stored todos.
- Nothing in this interface needs an AI service, an API key or the network.
