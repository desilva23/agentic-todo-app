# Implementation Plan: Console Look

**Branch**: `003-ui-console-theme` (no git repository; folder name only) | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-ui-console-theme/spec.md`

## Summary

Give the single todo page a dark developer-console look without changing what it does. Almost all of it is the page's
style block: new colour variables (always dark), a system monospace font stack, square panels with thin borders, a
green accent for main buttons. A little markup changes: three prompt-style headings, and the priority, status and
reminder labels become bracketed words (`[high]`, `[active]`, `[overdue]`) written as text. Tests come first: page
tests pin every element id and label the script relies on, and a contrast test checks 4.5 to 1. A real-browser pass
at three widths proves behaviour is unchanged. See [research.md](research.md) for each decision.

## Technical Context

**Language/Version**: Python 3.10 or newer (unchanged); the changed file is HTML with inline CSS and JavaScript

**Primary Dependencies**: none new (no library, no CSS framework, no downloaded font)

**Storage**: none. No data or schema change

**Testing**: pytest (page source tests and a contrast test, no network); a real-browser pass with Playwright run from outside the project

**Target Platform**: a user's own computer, any modern browser, desktop and phone width

**Project Type**: web-service with one static page (same project as features 001 and 002)

**Performance Goals**: none new; the page must not get slower to open (no new files or fonts)

**Constraints**: every element id, message and request stays; text from users and the AI stays plain text; 375 px with no sideways scroll; 4.5 to 1 contrast; always dark

**Scale/Scope**: one file (`static/index.html`) and one test file (`tests/test_page.py`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Agents Are Read-Only by Construction | No agent, route or storage code is touched | Pass |
| II. Core Works Without AI | Core controls keep working; the restyle adds no dependency on the assistant | Pass |
| III. Secrets and Private Text Stay Out | No logging, key or message handling changes | Pass |
| IV. Test-First and Offline by Default | Page and contrast tests are written first and run offline; browser pass uses a stub model | Pass |
| V. Validate at Every Boundary | No input or model-output handling changes | Pass |
| VI. Simplicity and Plain Language | Smallest change (style block plus a few labels); text still inserted with `textContent`; 375 px kept; status stays as words | Pass |

No violations, so Complexity Tracking stays empty. Re-checked after design: still pass.

## Project Structure

### Documentation (this feature)

```text
specs/003-ui-console-theme/
├── plan.md              # this file
├── research.md          # decisions with reasons and alternatives
├── data-model.md        # states that no data changes
├── quickstart.md        # how to see and check the look
├── contracts/
│   └── page-contract.md # the ids, labels and rules the restyle must keep
├── checklists/
│   └── requirements.md
└── tasks.md             # created by the tasks step
```

### Source Code (repository root)

```text
static/index.html        # restyled (style block, 3 headings, bracketed labels)
tests/test_page.py       # extended: ids, labels, look, contrast
README.md                # one line about the look
```

**Structure Decision**: single project as before. No new files in `app/`.

## Complexity Tracking

None.
