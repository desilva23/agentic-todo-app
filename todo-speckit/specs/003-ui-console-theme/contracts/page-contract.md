# Page Contract: what the restyle must keep

The page is the only interface this feature touches. These must be exactly as before.

## Element ids the script relies on

`add-error` `add-form` `chat-error` `chat-form` `chat-input` `chat-loading` `chat-preview` `chat-reminders`
`chat-reply` `chat-send` `chat-suggestion` `filter-priority` `filter-status` `list-error` `new-description`
`new-due` `new-priority` `new-title` `todo-list`

## Requests the page makes (unchanged)

`GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `POST /agent/message`

## Visible text that must remain

Buttons and labels: Confirm, Cancel, Accept, Ignore, Edit, Delete, Save, Send, "Thinking...", the empty-list text,
and every plain-language error message. The reminder labels keep the words "overdue" and "due soon" (now in brackets).

## Rules

- Text from users and from the AI is inserted only as plain text (no markup-inserting calls).
- At 375 px width: no sideways scroll, every button fully on screen.
- Body, muted and button text: at least 4.5 to 1 contrast.
- Always dark; no light variant.
