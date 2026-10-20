<!-- markdownlint-disable-file -->
# Task Research: bold-ui-theme

| Field              | Value                      |
|--------------------|----------------------------|
| Date               | 2026-10-20                 |
| Researcher / agent | rpi-research (Claude Code) |
| Output mode        | convergence                |

## Executive Summary

* Bottom line: The "Bold" restyle is mostly a CSS job. The page's look comes from a handful of rules and one `:root` block; the script builds elements from a small set of stable class names. Only one thing needs a script change: priority and status are plain text spans today, so colourful priority chips need a class on those spans.
* Why this matters: A small, CSS-first change is low risk. The things that must not change (ids, labels, requests, the plain-text rule) are few and already pinned or easy to pin with tests.
* Research status: Complete (one three-wave cycle). No decision is open; no walkthrough needed.
* Confidence and uncertainty: High for what the page and tests show. Medium for contrast of the gradient accent, which is why the plan should test both gradient colours, not just one.

## What You May Not Know

* The HVE page has no per-priority classes today: the list shows plain text such as `Priority: Medium` in an unstyled span (C2). Colourful chips therefore need one small script edit (a class on that span), not just CSS.
* A gradient makes contrast depend on *two* colours. Text on a violet-to-pink button must pass 4.5 to 1 against both ends, and a gradient *heading text* (clipped to the letters) has no single background to test, so it is the riskiest part (C5).
* The other two builds already used the cheapest good guard: a test that reads the colour variables from the page and checks 4.5 to 1 (C5). That idea transfers directly; the code should be written fresh.

## Findings

### 1. The look lives in a few CSS rules and is mostly CSS-only

The `<style>` block defines one `:root` with `--gap`, `--line`, `--accent`, `--danger`, plus about 30 one-line rules for `.card`, `.row`, `.field`, `button`, `li.todo`, `.meta`, `.block`, `.reply`, `.status` and so on. The script builds elements from these class names (`todo`, `title`, `meta`, `desc`, `actions`, `error`, `primary`, `danger`, `block`, `reply`).

* Questions: Q2
* Evidence state: evidence-backed finding
* Evidence: C1, C2
* Confidence and limits: High. The only gap for the chosen look is priority and status styling (below).

### 2. Priority and status need a class from the script for coloured chips

`renderTodo` appends `el("span", "Priority: " + PRIORITY_TEXT[todo.priority])` and `el("span", "Status: ...")` with no class, so CSS cannot colour high, medium and low differently. Adding a class that carries the priority word (for example `chip high`) is a one-line change per place, and the visible words can stay exactly as they are (`Priority: High`), which keeps existing browser checks valid.

* Questions: Q2, Q4
* Evidence state: evidence-backed finding
* Evidence: C2, C6
* Confidence and limits: High. Reminder tags and the preview and suggestion blocks are built the same way in the script and can take the same class.

### 3. What must not change is short and mostly pinnable

Element ids used by the script (`add-title`, `add-desc`, `add-due`, `add-priority`, `add-error`, `add-form`, `filter-status`, `filter-priority`, `list-error`, `todo-list`, `chat-form`, `chat-input`, `chat-send`, `chat-status`, `chat-error`, `chat-reply`, `chat-result`), the visible labels (Mark done, Mark not done, Edit, Delete, Save, Cancel, Confirm, Accept, Ignore, Send, `Thinking...`, `Status:`, `Priority:`, `Due:`, `Overdue`, `Due soon`), the five requests, and the rule that user and AI text is inserted only with `createElement` and `textContent`. `tests/test_page.py` already scans for unsafe calls, checks the viewport tag, the assistant card's parts and its position; it does not yet pin the ids or measure contrast.

* Questions: Q1
* Evidence state: evidence-backed finding
* Evidence: C2, C3, C4
* Confidence and limits: High. The id list was read from the page and from the browser script that already drives it.

### 4. Colour and the 375 px grid are the two risks, and both have cheap checks

* Contrast: a test that reads colour variables and checks 4.5 to 1 for text, muted text, the text on the accent, **both ends of the gradient**, and the chip text on its chip colour, in light and dark. Avoid gradient-clipped heading text (no single background to test); use a solid heading with a gradient accent bar.
* Layout: a card grid must collapse to one column on a phone (`grid-template-columns` with a minimum width that cannot exceed the screen), checked in a real browser at 375 px.

* Questions: Q3
* Evidence state: evidence-backed finding (checks proven in the other two builds); the gradient specifics are a partially supported claim until tested
* Evidence: C5, C4
* Confidence and limits: Medium for the final colours, which the plan's test will settle.

### 5. Existing verification can be reused as an idea, not copied

The HVE stub-model browser script (outside the project) checks every page state at 1000, 768 and 375 px and found 85/85 before; it depends on the visible words (for example `Priority: Medium`), so keeping those words keeps it valid. The "Paper" and "Console" looks of the other builds are different on purpose (serif and ruled; dark and monospace), so Bold should be light, rounded and gradient-led.

* Questions: Q4
* Evidence state: evidence-backed finding
* Evidence: C6, C7
* Confidence and limits: High.

## Recommendation and Alternatives

* Recommendation or decision state: Do the restyle in one phase, CSS-first, with a small script edit for chips; write tests first (ids and labels pinned, chip classes, contrast including both gradient colours in both schemes), then restyle, then run the stub-model browser check at three widths plus dark mode.
* Rationale: The page's structure is stable (C1, C2), the guards are cheap and proven (C5), and the existing browser evidence stays valid if the visible words stay the same (C6).
* What could change this result: A contrast test failing for the chosen violet-to-pink pair (then darken the colours, not the test).

| Option | Benefits | Costs and risks | Evidence | Disposition |
|--------|----------|-----------------|----------|-------------|
| CSS-first restyle plus chip class, tests first | Smallest change; keeps behaviour; testable | Needs one small script edit | C1, C2, C5 | selected |
| Gradient-clipped heading text | Striking look | No single background to test contrast; hard to guarantee 4.5 to 1 | C5 | rejected |
| Add a CSS framework | Fast styling | Out of scope (no new libraries); against the page rules | C4 | rejected |
| Several phases (CSS, then script, then tests) | Smaller steps | More paperwork for a small change | C1 | viable |

## Scope and Questions

* Goal: Decide how to restyle the page safely so it has its own "Bold" identity.
* Audience and use: the user and the later `/rpi-plan` step.
* In scope: `static/index.html`, `tests/test_page.py`, the project's page rules, the other builds' tests as ideas.
* Out of scope: behaviour or API changes, new libraries, copying the other builds' looks, editing them.
* Decision and evidence criteria: every claim cites a file; checks must be cheap and offline.
* Requested output: a recommendation for planning.

| ID | Question | Source | Status |
|----|----------|--------|--------|
| Q1 | What must stay unchanged (ids, labels, requests, plain-text rule)? | explicit | answered |
| Q2 | Which parts are CSS-only versus script-built? | explicit | answered |
| Q3 | What contrast and 375 px risks does the look bring, and the cheapest checks? | explicit | answered |
| Q4 | What verification evidence can be reused? | explicit | answered |

## Decisions and Feedback

| Group | Decision or feedback item | Status | Owner | Rationale or input needed | Evidence | Impact of answer |
|-------|---------------------------|--------|-------|---------------------------|----------|------------------|
| D1 | The "Bold" look (light base, rounded card grid, violet-to-pink gradient accent, colourful priority chips, large heading, dark variant) | confirmed | user | Chosen by the user before research | request | Fixes the look; no walkthrough needed |

No unresolved material decision remains, so no walkthrough is required.

## Risks and Open Questions

| Priority | Type | Risk, question, or research item | Impact | Smallest action or evidence needed | Owner |
|----------|------|----------------------------------|--------|------------------------------------|-------|
| M | risk | Violet-to-pink gradient may fail 4.5 to 1 with white text at one end | Unreadable button text | Contrast test on both ends in both schemes | downstream |
| M | risk | Card grid could overflow at 375 px | Sideways scroll | Grid with a screen-safe minimum width; browser check at 375 px | downstream |
| L | open question | Dark variant colours for chips | Chip text contrast in dark | Include chip colours in the contrast test | downstream |

## Planning Readiness and Next Step

| Field | Record |
|-------|--------|
| Research disposition | executed |
| Decision participation | user-owned; no open decisions, so no walkthrough |
| Planning Readiness | Ready (C1 to C7) |
| Research depth and helpers | one cycle, three waves; no helpers (subagents=none) |
| Blockers | none |
| Output mode and planning support | convergence; supports planning |
| Continuation owner | user |
| Required gates or confirmations | none pending |
| Next action | `/rpi-plan` |
| Primary evidence file | `.copilot-tracking/research/2026-10-20/bold-ui-theme-research.md` (date supplied by the caller) |

## Research Record

### Method and Boundaries

| Field | Record |
|-------|--------|
| Research posture and provenance | focused; caller |
| Helper lane effort | not applicable |
| Completion basis | All four questions answered from the page, its tests and the other builds' tests; contrarian wave found the chip-class gap and the gradient-heading risk |
| Explicit limits or deadline | none |
| Codebase and external scope | `static/index.html`, `tests/test_page.py`, `.github/instructions/todo-app/web-page.instructions.md`, `../todo-openspec/tests/test_page.py`, `../todo-speckit/tests/test_page.py`; no external scope |
| Initial candidate areas | page CSS, script-built classes, page tests, other builds' guards |
| Evidence root | `.copilot-tracking/`, default |
| Constraints and excluded sources | `.env` not read; other projects not edited |
| Prior knowledge | The earlier lessons research (todo-app-lessons) was reused only as background |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped contract | Selected or skipped reason |
|------|-----------|--------------------------------|----------------------------|
| instruction | `todo-app/web-page.instructions.md` | matches `static/**` | selected (page rules as criteria) |
| instruction | `hve-core/copilot-tracking.instructions.md` | matches the evidence path | selected |
| skill | other research-time skills | none listed | skipped |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|----------------------|-----------------------------------|---------------------------------|--------------------------------|
| intake | topic, posture, the Bold look | supplied by the request; the user already chose the look | no question needed |
| convergence | any open decision? | none | no walkthrough |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: focused; read-only; no `.env`.

##### Wave 1: Wider

* Focus and questions: Q1 to Q4 across the page, tests and the other builds' guards.
* Evidence: Q2 to C1, C2; Q1 to C3, C4; Q3 to C5; Q4 to C6.
* Reflection: The CSS is small; the open question is how priority is rendered.

##### Wave 2: Deeper

* Focus and questions: read `renderTodo` and the `<style>` block exactly.
* Evidence: C2 (priority and status are unclassed spans); C1 (`:root` has only four variables).
* Reflection: Chips need a class from the script; everything else is CSS.

##### Wave 3: Contrarian

* Focus and questions: could a gradient or a card grid break the guards?
* Evidence: C5 (contrast depends on both gradient ends; gradient-clipped text has no testable background); C7 (the other builds' looks must not be copied).
* Reflection: Changed the recommendation to a solid heading with a gradient bar and a two-ended contrast test.

##### Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|-------------------|----------|-------------|-----------|--------------------|
| Restyle is mostly CSS | C1, C2 | accepted | few rules, stable classes | Finding 1 |
| Chips need a class | C2 | accepted | spans have none | Finding 2 |
| Gradient-clipped heading | C5 | rejected | cannot test contrast | Alternatives |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: scope covered; sources redundant
* Readiness or revalidation effect: none

### Evidence Log

* Helpers: none

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|----|------------------|--------------------|----------------------|------|------------|-------|
| C1 | The `<style>` block defines `:root` (`--gap`, `--line`, `--accent`, `--danger`) and about 30 one-line rules | `static/index.html`, `<style>` block | not applicable | read | high | |
| C2 | `renderTodo` builds priority and status as unclassed spans (`"Priority: " + PRIORITY_TEXT[...]`); other blocks use stable classes (`todo`, `title`, `meta`, `desc`, `actions`, `error`, `primary`, `danger`, `block`, `reply`) | `static/index.html`, `renderTodo`, `button`, `el` | not applicable | read | high | |
| C3 | Page tests scan for unsafe calls, viewport tag, assistant card parts and order; they do not pin ids or contrast | `tests/test_page.py` | not applicable | read | high | |
| C4 | Page rules: only `createElement`/`textContent`; status as text; 375 px; no new libraries or features | `.github/instructions/todo-app/web-page.instructions.md` | not applicable | read | high | |
| C5 | The other builds guard looks with a test that reads colour variables and checks 4.5 to 1 and pins ids | `../todo-openspec/tests/test_page.py`, `parse_colour_blocks` and `contrast`; `../todo-speckit/tests/test_page.py`, `colour_variables` | not applicable | read | high | Idea only; write fresh |
| C6 | The stub-model browser script (outside the project) checks every page state at three widths and relies on the visible words | session scratchpad `hve_ui_browser.py` (not in the repository) | not applicable | read | medium | Outside the workspace; recorded for provenance |
| C7 | The other builds use a light serif "Paper" look and a dark monospace "Console" look | `../todo-openspec/static/index.html`, `../todo-speckit/static/index.html`, `<style>` blocks | not applicable | read | high | To avoid copying |

#### Contradictions and Conflicts

* none

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness and next action without the Research Record.
* [x] Every question is answered and every material result has one evidence state.
* [x] Findings keep explanation, evidence, confidence and counter-evidence together.
* [x] Every codebase finding has a `C#` ID with path and symbol; no external findings.
* [x] The cycle records Wider, Deeper and Contrarian waves in order with a re-entry decision.
* [x] Method, extensions, participation and prior knowledge are recorded.
* [x] Convergence selects one recommendation with rejected alternatives.
* [x] D1 recorded as confirmed; no walkthrough needed.
* [x] Disposition, readiness, blockers, owner, gates and next action are complete.
* [x] No secrets recorded; the write boundary held.
* Checked sections: all
* Missing or limited sections: C6 is outside the workspace (scratchpad)
