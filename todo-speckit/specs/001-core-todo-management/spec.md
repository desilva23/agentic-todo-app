# Feature Specification: Core Todo Management

**Feature Branch**: `001-core-todo-management` (this project is not a git repository, so no branch is created)

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Core todo management for a single user: a web page where a person can create, view, edit, delete, complete and filter todos, and the todos are still there after the app is restarted." Source requirements: `docs/requirements.md` (FR-1 to FR-9, NFR-1, NFR-3, NFR-6, NFR-10, AC-1 to AC-7, AC-17).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add todos and see them in a list (Priority: P1)

A person opens the app and writes down things they need to do. Each todo has a title and, if they
wish, a description, a due date and time, and a priority (low, medium or high). They immediately
see their todos in a list showing each one's title, status, due date and priority. If they close
the app and open it again later, every todo is still there.

**Why this priority**: This is the whole point of a todo app. With only this story built, the user
already has a working list that keeps their data. Everything else refines it.

**Independent Test**: Add a todo titled "Buy milk" with nothing else, then add a second one with
every field filled in, then stop and restart the app. Both appear in the list with the values
entered, and "Buy milk" shows medium priority and active status.

**Acceptance Scenarios**:

1. **Given** the app is running, **When** the user adds a todo titled "Buy milk" and fills in nothing
   else, **Then** it appears in the list with medium priority and active status (AC-1; FR-1, FR-2).
2. **Given** the user fills in a title, description, due date and time, and high priority,
   **When** they add the todo, **Then** the list shows it with every value as entered (FR-1, FR-2).
3. **Given** the user submits an empty title, a title longer than 200 characters, an unknown
   priority or a due date that cannot be understood, **When** they save, **Then** the todo is
   rejected, a message names the field that is wrong, and nothing is saved (AC-2; FR-1).
4. **Given** several todos exist, **When** the app is stopped and started again, **Then** the same
   todos are shown with the same values (AC-7; FR-7).
5. **Given** the app is started for the first time with no data, **When** the user opens it,
   **Then** it works and shows an empty list without any setup step (NFR-10).

---

### User Story 2 - Keep todos up to date (Priority: P2)

As things change, the person marks todos as done, reopens one they marked done by mistake, fixes a
title or a due date, and removes todos they no longer need.

**Why this priority**: A list that cannot be updated quickly becomes useless, but it is only
valuable once there is a list to update.

**Independent Test**: With three todos present, complete one, reopen it, change another's due
date, and delete the third. The list reflects each action straight away and after a restart.

**Acceptance Scenarios**:

1. **Given** an active todo, **When** the user marks it complete, **Then** it shows as completed;
   **and when** they mark it again, **Then** it is active again (AC-5; FR-5).
2. **Given** an existing todo, **When** the user changes its due date, **Then** the list shows the
   new date (AC-3; FR-3).
3. **Given** an existing todo, **When** the user edits it to an empty title, **Then** the edit is
   rejected with a message naming the field and the todo keeps its old title (FR-3).
4. **Given** an existing todo, **When** the user deletes it, **Then** it no longer appears in the
   list, including after a restart (AC-4; FR-4, FR-7).
5. **Given** a todo that has been removed in the meantime, **When** the user tries to edit, complete
   or delete it, **Then** a clear "not found" message is shown and nothing else changes (FR-9).

---

### User Story 3 - Find what matters with filters (Priority: P3)

When the list grows, the person narrows it to active or completed todos, to one priority, or to
both at once.

**Why this priority**: Useful once there are many todos; not needed to capture or update them.

**Independent Test**: With a mix of active and completed todos of different priorities, choose
"completed", then "high priority", then both together, and check that only matching todos show.

**Acceptance Scenarios**:

1. **Given** active and completed todos, **When** the user filters by "completed", **Then** only
   completed todos are shown (AC-6; FR-6).
2. **Given** todos of several priorities, **When** the user filters by high priority, **Then** only
   high-priority todos are shown (FR-6).
3. **Given** a status filter and a priority filter are both chosen, **When** the list is shown,
   **Then** only todos matching both are listed (FR-6).
4. **Given** no filter is chosen, **When** the list is shown, **Then** all todos appear (FR-6).
5. **Given** a filter that matches nothing, **When** the list is shown, **Then** the page says there
   is nothing to show instead of looking broken.

---

### User Story 4 - Use it comfortably on any screen and get it running quickly (Priority: P3)

The person uses the app on a laptop or on a phone, and sees plain-language messages when
something goes wrong. A new person can get the app running by following a short set of written
steps.

**Why this priority**: It makes the first three stories pleasant and repeatable, but they deliver
value on their own first.

**Independent Test**: Open the page at a phone-sized width and perform every action; then follow the
written steps on a clean computer and time how long it takes.

**Acceptance Scenarios**:

1. **Given** a phone-sized screen (375 pixels wide), **When** the user performs any action,
   **Then** every control can be reached and the page never needs sideways scrolling (NFR-6).
2. **Given** an action fails, **When** the message is shown, **Then** it is in plain language, sits
   next to the action that failed, and shows no technical output (NFR-6).
3. **Given** the user adds, edits, completes or deletes a todo, **When** the action succeeds,
   **Then** the list updates without the whole page reloading (FR-8).
4. **Given** a person who has never seen the project, **When** they follow the written steps,
   **Then** they have the app running in under 10 minutes (AC-17; NFR-10).

---

### Edge Cases

- A title of exactly 200 characters is accepted; 201 characters is rejected. A title made only of
  spaces is treated as empty.
- Two todos may have the same title; they are separate todos.
- A due date in the past is allowed (the todo is simply overdue).
- A due date given together with a time zone is accepted and treated as the same moment in the
  user's local time.
- Asking for, changing or deleting a todo that does not exist (including an identifier too large to
  ever exist) gives a clear "not found" message, never a crash.
- A rejected request leaves every saved todo exactly as it was.
- Applying both filters to a list where nothing matches shows an empty state, not an error.
- An unknown status filter value is rejected with a message that lists the allowed values.
- Text typed into a title or description that looks like markup is shown exactly as typed and is
  never treated as instructions to the page.
- The app is stopped at any moment: todos already saved are intact on the next start.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to create a todo with a required title of 1 to 200 characters and
  optional description, due date and time, and priority (low, medium or high; default medium). A new
  todo MUST start as active. *(Source: FR-1)*
- **FR-002**: Users MUST be able to see a list of all todos, each showing title, status, due date and
  priority. *(Source: FR-2)*
- **FR-003**: Users MUST be able to change any field of an existing todo, and the same validation as
  when creating MUST apply. *(Source: FR-3)*
- **FR-004**: Users MUST be able to delete a todo. *(Source: FR-4)*
- **FR-005**: Users MUST be able to mark a todo as complete and mark a completed todo as active
  again. *(Source: FR-5)*
- **FR-006**: Users MUST be able to filter the list by status (all, active, completed) and by
  priority, and to combine both filters. With no filter, all todos MUST be shown. *(Source: FR-6)*
- **FR-007**: The system MUST keep todos across restarts and MUST create its own storage on first
  start with no setup step. *(Sources: FR-7, NFR-10)*
- **FR-008**: The system MUST reject invalid input (empty or over-long title, unknown priority,
  unreadable due date, unknown status filter) with a message that names the wrong field, and MUST
  save nothing. A failed request MUST leave all saved todos unchanged. *(Sources: FR-1, FR-9, NFR-3)*
- **FR-009**: The system MUST answer a request about a todo that does not exist with a clear
  "not found" message. *(Source: FR-9)*
- **FR-010**: The same operations (create, list, view one, change, delete, filter) MUST also be
  available to other programs through a documented interface, with the same validation and clear
  error messages as the page. *(Source: FR-9)*
- **FR-011**: The system MUST provide a web page that supports every operation above and updates the
  list without a full page reload. *(Source: FR-8)*
- **FR-012**: The page MUST be fully usable at a width of 375 pixels with no sideways scrolling, and
  MUST show errors in plain language next to the action that failed. *(Source: NFR-6)*
- **FR-013**: Every feature in this specification MUST work with no AI service, no API key and no
  network connection. *(Source: NFR-3)*
- **FR-014**: The system MUST respond to every operation in under half a second when up to 1,000
  todos are stored. *(Source: NFR-1)*
- **FR-015**: Text entered by users MUST be displayed exactly as typed and MUST NOT be interpreted as
  page content or instructions. *(Constitution V and VI)*
- **FR-016**: The project MUST include written steps to install and start the app, short enough that
  a new person succeeds in under 10 minutes. *(Sources: NFR-10, AC-17)*

### Key Entities

- **Todo**: One thing the user needs to do. Has an identifier assigned by the system, a title,
  an optional description, an optional due date and time (local time), a priority (low, medium,
  high), a status (active or completed), and the time it was created.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can add a todo and see it in the list in under 5 seconds, without reloading the
  page.
- **SC-002**: With 1,000 saved todos, every operation completes in under half a second (NFR-1).
- **SC-003**: 100% of saved todos are present, unchanged, after the app is stopped and started again
  (AC-7).
- **SC-004**: 100% of invalid submissions are rejected with a message that names the wrong field, and
  none of them changes saved data (AC-2).
- **SC-005**: Every action can be completed on a 375-pixel-wide screen with no sideways scrolling
  (NFR-6).
- **SC-006**: A person who has never seen the project has the app running in under 10 minutes by
  following the written steps (AC-17).
- **SC-007**: All of the acceptance scenarios for AC-1 to AC-7 pass with no AI service, no API key
  and no network connection.

## Assumptions

- One user on their own computer; there are no accounts, sign-in or sharing.
- Due dates and times are in the computer's local time zone.
- Todos are listed in the order they were created.
- Duplicate titles are allowed.
- The app is used in English only.
- The AI chat assistant, priority suggestions and reminders are a **separate, later feature** that
  builds on this one; nothing here depends on it.
- Deployment, notifications and multi-user use are out of scope.
- The shared requirements in `docs/requirements.md` are the source of the requirement identifiers
  cited here (FR-1…, NFR-…, AC-…), which are separate from the FR-001… numbers used in this spec.
