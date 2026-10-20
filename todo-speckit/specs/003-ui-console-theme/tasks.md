# Tasks: Console Look

**Input**: Design documents from `/specs/003-ui-console-theme/` (plan.md, spec.md, research.md, data-model.md, contracts/page-contract.md, quickstart.md)

**Tests**: Required (constitution IV): write each group's tests first and see them fail; every default test is offline.

**Format**: `[ID] [P?] [Story] Description`. [P] means it touches a different file and can run in parallel.

**Browser-check rule (applies to every browser task)**: start the app on a free port you choose (for example 8780 upward, never 8000 or 8001), and before testing confirm which app answers (`/openapi.json` title must be `Todo App (Spec Kit build)`).

## Phase 1: Foundational (blocks all stories)

- [X] T001 Extend `tests/test_page.py` with tests that pin every element id and visible label in `specs/003-ui-console-theme/contracts/page-contract.md`, the absence of markup-inserting calls (`innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`), and the viewport tag; run them (they pass on the current page)
- [X] T002 [P] Add a contrast test to `tests/test_page.py` that reads the colour variables from `static/index.html` and checks body text, muted text and button text against their backgrounds are at least 4.5 to 1, with a self-test of the contrast helper (known good and bad colours); run it

## Phase 2: User Story 1 - The page looks like a developer console (Priority: P1) 🎯 MVP

**Goal**: dark near-black page, light monospace text, square panels with thin borders, prompt-style headings, one green accent.

**Independent Test**: open the page: dark, monospace, square, `>` headings, green primary buttons.

### Tests for User Story 1 ⚠️ write first, confirm they fail

- [X] T003 [US1] In `tests/test_page.py` add tests: the page declares a monospace font stack, declares `color-scheme: dark` and no light-scheme override, has no rounded corners on panels (`border-radius` of panels is 0), and has headings `> assistant`, `> new todo`, `> filter`; run and confirm they fail

### Implementation for User Story 1

- [X] T004 [US1] In `static/index.html` replace the colour variables with the dark console palette (near-black background, light text, muted grey-green, thin dim-green lines, one green accent, soft red for danger) and add `color-scheme: dark`
- [X] T005 [US1] In `static/index.html` set the monospace font stack and make panels and todo rows square with thin borders
- [X] T006 [US1] In `static/index.html` add the three prompt-style headings (`> assistant`, `> new todo`, `> filter`) above their panels and use the green accent only for primary buttons; run the T003 tests until they pass

**Checkpoint**: User Story 1 is visible and testable on its own.

## Phase 3: User Story 2 - Status and priority are readable words (Priority: P2)

**Goal**: priority, status, overdue and due soon are bracketed words.

**Independent Test**: a high-priority overdue todo shows `[high]` `[active]`; the reminder shows `[overdue]`.

### Tests for User Story 2 ⚠️ write first, confirm they fail

- [X] T007 [US2] In `tests/test_page.py` add tests that the script builds bracketed labels for priority, status and the reminder tags (`"["` joined with the word and `"]"`), and that no label is colour-only; run and confirm they fail

### Implementation for User Story 2

- [X] T008 [US2] In `static/index.html` change the script so priority, status and the reminder tags are written as bracketed words with `textContent` (same words as before), and style them as square chips; run the T007 tests until they pass

## Phase 4: User Story 3 - Everything still works, and is readable on a phone (Priority: P1)

**Goal**: all previous behaviour, at 1000, 768 and 375 px, no sideways scroll, 4.5 to 1 contrast.

**Independent Test**: run the real-browser behaviour checks at the three widths.

- [X] T009 [US3] Run the full default test suite (`python -m pytest`) with no network and no key; everything passes
- [X] T010 [US3] Browser-check rule applies: against a stub model at 1000, 768 and 375 px check add, edit, complete, delete, filter, assistant preview Confirm and Cancel, suggestion Accept and Ignore, reminders, an error, and markup-looking text shown as plain text; confirm no sideways scroll and every button on screen; take screenshots
- [X] T011 [US3] Check that a computer set to a light colour scheme still shows the dark page (FR-005) in the browser

## Phase 5: Polish & Cross-Cutting

- [X] T012 [P] Mention the look in one line in `README.md`
- [X] T013 Secrets scan: the real key from `.env` appears in no other file of the project (print only file names); `.env` stays git-ignored
- [X] T014 Run the `quickstart.md` scenarios 1 to 7 and note the results

## Dependencies & Execution Order

- Phase 1 (T001, T002) first. Phase 2 (US1) and Phase 3 (US2) both edit `static/index.html`, so do them one after the other (US1 first). Phase 4 (US3) verifies the result, so it comes after both. Phase 5 last.
- Within a story: tests first, then the page change.

## Implementation Strategy

- **MVP first**: finish Phase 1 and User Story 1, look at the page, then add the chips (US2), then prove nothing broke (US3).
- Mark each task `[X]` as it is finished.
