# Feature Specification: Console Look

**Feature Branch**: `003-ui-console-theme` (this project is not a git repository, so no branch is created)

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "Visual identity for the page: a dark developer-console look. The page gets its own look so the three builds of this app can be told apart on screen: near-black background, light monospace text, one green accent for primary actions, square-edged panels with thin borders, prompt-style section headings such as '> assistant', and status, priority, Overdue and Due soon shown as bracketed text chips such as [high] [active] [overdue]. Always dark. Nothing about behaviour changes."

**Source**: docs/requirements.md FR-8 (a web page that supports the todo features), NFR-6 (usable on desktop and phone width, plain-language errors); acceptance criteria AC-1 to AC-14 re-checked for unchanged behaviour.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The page looks like a developer console (Priority: P1)

A person opens the todo page and sees a dark, terminal-style screen: a near-black background, light
monospace text, square-edged panels with thin borders, headings written like prompts (for example
"> assistant", "> new todo", "> filter"), and one green accent used for the main buttons.

**Why this priority**: This is the whole point of the feature. It is what lets someone looking at the three
builds tell this one apart at a glance.

**Independent Test**: Open the page in a browser. It is dark, text is monospace, panels have square corners and
thin borders, section headings start with ">", and primary buttons are green. Compare with the page before this
feature: it is clearly different.

**Acceptance Scenarios**:

1. **Given** the page is open on any computer, **When** a person looks at it, **Then** the background is
   near-black, the text is light and monospace, and panels have square corners and thin borders.
2. **Given** the page is open, **When** a person reads the section headings, **Then** each begins with a
   prompt marker such as "> assistant", "> new todo" and "> filter".
3. **Given** the page is open on a computer set to a light colour scheme, **When** it loads, **Then** it is still
   the dark console look (there is no light variant).

---

### User Story 2 - Status and priority are readable words (Priority: P2)

A person scanning the list sees each todo's priority and status as short bracketed words, for example
`[high]` and `[active]`, and the assistant's reminders as `[overdue]` or `[due soon]`. The meaning never depends
on colour alone.

**Why this priority**: Status must stay understandable for everyone (a project rule), and the bracketed words are
also the console look's signature.

**Independent Test**: With a high-priority overdue todo in the list, the row reads `[high]` `[active]` and the
reminder reads `[overdue]`, in text. Turning the colours off (or printing in black and white) loses no meaning.

**Acceptance Scenarios**:

1. **Given** a todo with priority high, **When** it appears in the list, **Then** its priority is written as the
   word "high" inside brackets, and its status as the word "active" or "completed" inside brackets.
2. **Given** an overdue todo and one due soon, **When** the assistant lists them, **Then** each is marked with the
   words "overdue" or "due soon" inside brackets.

---

### User Story 3 - Everything still works, and is readable on a phone (Priority: P1)

A person uses the page exactly as before: adds, edits, completes, deletes and filters todos, and talks to the
assistant (preview with Confirm and Cancel, priority suggestion with Accept and Ignore, reminders, error messages).
On a phone-width screen nothing scrolls sideways and every button stays on screen. Text stays easy to read.

**Why this priority**: A restyle must never break the app. This is the safety net for the whole feature.

**Independent Test**: Run every behaviour check that existed before (AC-1 to AC-14 through the page) in a real
browser at 1000, 768 and 375 px wide. All pass, nothing scrolls sideways, and body text, muted text and button
text each have at least 4.5 to 1 contrast against their background.

**Acceptance Scenarios**:

1. **Given** the restyled page, **When** a person adds, completes, edits, deletes and filters todos, **Then**
   each action works as before.
2. **Given** the restyled page, **When** a person sends messages to the assistant, **Then** previews, suggestions,
   reminders and errors appear and work as before, and anything typed or returned by the AI is shown as plain text.
3. **Given** a screen 375 px wide, **When** the page is used, **Then** it does not scroll sideways and every button is
   fully on screen.

---

### Edge Cases

- A very long todo title or description wraps and never pushes a button off screen.
- Text that looks like markup (for example `<img src=x onerror=alert(1)>`) is shown as plain text, as before.
- The computer has no preferred monospace font: a common system monospace font is used instead and the layout
  still fits.
- A person with their computer set to light mode still sees the dark console page.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The page MUST present a dark "console" look: near-black background, light monospace text, and
  square-edged panels with thin borders instead of rounded cards. (Source: FR-8, NFR-6)
- **FR-002**: Primary actions MUST use one green accent colour, and no other accent colour MUST be used for actions.
- **FR-003**: Section headings MUST be written as prompts beginning with ">" (for example "> assistant",
  "> new todo", "> filter").
- **FR-004**: A todo's priority and status, and the assistant's Overdue and Due soon labels, MUST be shown as
  bracketed words (for example `[high]`, `[active]`, `[overdue]`, `[due soon]`) and MUST NOT rely on colour alone.
  (Source: NFR-6)
- **FR-005**: The page MUST stay dark whatever colour scheme the person's computer prefers.
- **FR-006**: Every control, message and request that existed before this feature MUST keep working exactly as before
  (Source: AC-1 to AC-14), and text typed by the user or returned by the AI MUST still be shown as plain text.
- **FR-007**: The page MUST work at 375 px width with no sideways scrolling, and every button MUST stay fully on
  screen. (Source: NFR-6)
- **FR-008**: Body text, muted text and button text MUST each have a contrast ratio of at least 4.5 to 1 against
  their background.
- **FR-009**: This feature MUST NOT change any behaviour, data, request or message, add any feature, or require a new
  library or downloaded font.

### Key Entities

None. This feature changes only how existing information is shown.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Someone shown screenshots of the three builds can pick out this one as the dark console look without
  being told.
- **SC-002**: 100% of the behaviour checks that passed before this feature (add, edit, complete, delete, filter,
  preview, confirm, cancel, suggestion, accept, ignore, reminders, each error) still pass in a real browser at
  1000, 768 and 375 px.
- **SC-003**: At 375 px width, no page ever scrolls sideways in any of those checks.
- **SC-004**: Body text, muted text and button text are all at least 4.5 to 1 against their background.

## Assumptions

- The look is always dark; a light variant is out of scope.
- "Monospace" means a monospace font already on the person's computer; no font is downloaded.
- The green accent is a single colour chosen to reach 4.5 to 1 contrast with the dark background and with the
  text on the buttons.
- The page already exists with all its behaviour (features 001 and 002); this feature only changes appearance and a
  few visible headings and labels.
- Out of scope: any behaviour or API change, a light variant, changes to the other two builds.
