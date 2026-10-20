<!-- markdownlint-disable-file -->
# Review: Bold UI theme (HVE build)

## Executive Summary

* Assessment (proposal): The Bold restyle meets every requirement in the plan. The colour-variable contract is met in both colour schemes, the chips come only from a fixed list, text is still inserted as plain text, the card grids cannot exceed a phone screen, and no library or font was added. Two small Low findings remain, neither affecting behaviour.
* Why this matters: The page now looks different from the other two builds with no behaviour change, and the tests guard the look, so a later edit cannot quietly break contrast or an id.
* Review execution: Complete
* Assessed outcome (proposal): Residual work (no defects; 2 Low items, both small and non-blocking)
* Validation coverage: Offline suite re-run during review: 386 passed, 28 skipped. Checked in the files: every CSS variable used is defined in both schemes, no external reference, six chip-class uses. The browser run (129/129), red-first test run and secrets scan are taken from the changes record and were not re-run.
* Confidence and limitations: High for source-level claims. Not assessed: the browser behaviour (not re-run), the dark scheme at widths other than 375 px (the plan required only 375 px), Python 3.10.

The assessment above is the reviewer's proposal. Parent Decision Record contains the final decisions, or states that decisions are pending.

## What You May Not Know

* The dark scheme was browser-checked only at 375 px, as the plan specified; light was checked at 1000, 768 and 375 px.
* The top-of-page cards stretch to equal height, so a short card can show empty space under its content (visible in the screenshots). It is cosmetic and was not raised as a finding.

## Findings and Proposed Routes

<!-- rpi:review id=RV-001 -->
### RV-001 [Low]: Red error and Delete text is not covered by the contrast test

The plan's variable contract lists text, muted text, the text on both gradient colours and the three chip pairs. Error messages and the Delete button use the `--danger` colour on the card or page background, and that pair is not in the contract, so a later colour edit could drop it below 4.5 to 1 without a test failing. Today it passes: about 6.0 to 6.6 in light and 8.5 to 9.2 in dark (computed by the reviewer).

* Related scope: P01-T01, NFR-001
* Expected behavior: Text colours used on the page keep at least 4.5 to 1 (NFR-001).
* Observed behavior and evidence: `tests/test_page.py` (the pair list `PAIRS`) has no `danger` entry; `static/index.html` uses `var(--danger)` for `.error` and `button.danger`.
* Impact: A regression guard is missing for one text colour; no current defect.
* Resolution condition: `danger` on `card` and `bg` is added to the contrast pairs and passes in both schemes.
* Proposed destination: follow-up
* Smallest useful next action: Add two pairs to `PAIRS` in `tests/test_page.py` and run them.

<!-- rpi:review id=RV-002 -->
### RV-002 [Low]: The plan's status lines still say "ready for implementation"

After implementation the plan's Executive Summary ("Complete and ready for implementation") and its readiness table ("Ready for implementation"; next action `/rpi-implement`) were not updated, the same kind of stale line the earlier review found in the main plan.

* Related scope: plan Executive Summary and Planning Readiness and Next Step
* Expected behavior: Implementation-time updates keep the executive summary current with the plan's state.
* Observed behavior and evidence: `.copilot-tracking/plans/2026-10-20/bold-ui-theme-plan.md`, Executive Summary "Planning result" and the Planning Readiness rows "Planning execution and readiness" and "Next action", compared with the changes record's status Complete.
* Impact: A reader of the plan alone would think the work is not yet built. No code effect.
* Resolution condition: Those lines state that implementation is complete and name `/rpi-review` or nothing as the next action.
* Proposed destination: follow-up
* Smallest useful next action: Reword the three lines.

## Parent Decision Record

<!-- Decisions live here. Append events; never rewrite the evidence body above to fit a decision. -->

### Current Disposition

* Based on events: RD-002 to RD-006
* Review execution: Complete
* Final outcome: Residual work (no defects; two Low follow-ups accepted)
* Finding decisions and next actions: RV-001 accepted, follow-up (user); RV-002 accepted, follow-up (user)
* Decisions still needed: none

This summary is derived from Decision History, not a second decision record. The latest event for each subject governs; refresh this summary after appending decisions and on recovery.

### Decision History

| Event | Subject | Decision source | Status or value | Proposed destination | Final destination | Owner | More information needed | Smallest next action | Rationale |
|-------|---------|-----------------|-----------------|----------------------|-------------------|-------|--------------------------|----------------------|-----------|
| RD-001 | participation | system | user-owned (standalone default), subagents none | none | none | user | none | walk through each actionable finding | Invoked standalone with participation mode user-owned |
| RD-002 | RV-001 | user | accepted | follow-up | follow-up | user | none | add danger-on-card and danger-on-background pairs to the contrast test | Low: passes today (6.0 to 9.2), guard missing |
| RD-003 | RV-002 | user | accepted | follow-up | follow-up | user | none | reword the plan Executive Summary line and two readiness rows | Low: stale status wording |
| RD-004 | walkthrough | system | completed (RV-001 and RV-002 decided, none remaining) | none | none | user | none | none | each actionable finding walked through one at a time |
| RD-005 | execution | system | Complete | none | none | user | none | none | evidence body complete within the boundary |
| RD-006 | outcome | system | Residual work | none | none | user | none | keep the two follow-ups | no defects; two distinct non-blocking follow-ups accepted |

## Validation Evidence

| Command | Scope | Status | Summary |
|---------|-------|--------|---------|
| `python -m pytest -q` (re-run by the reviewer, offline only) | project | Passed | 386 passed, 28 skipped |
| Variable and reference check (read-only script) | static/index.html | Passed | every `var(--x)` used is defined; every light variable is redefined in the dark block; no external URL, font-face or import; six `chipClass(` uses; grid minimums are `minmax(min(100%, ...))` |
| Red-first test run | P01-T01 | Passed (recorded) | 22 failed before the restyle, per the changes record |
| Real-browser run, light 1000/768/375 and dark 375 | page | Passed (recorded, not re-run) | 129/129 per the changes record |
| Secrets scan | project | Passed (recorded, not re-run) | key in no file other than `.env` |
| Python 3.10 run | project | Unavailable | not installed |
| Dual-theme rendering of plan diagrams | plan | Unavailable | no preview available |

## Risks, Blockers, and Residual Work

* Blockers: none
* Remaining active work: none (all markers checked)
* Residual work: RV-001 and RV-002 (follow-ups); equal-height card whitespace (cosmetic, no action proposed)

## Review Record

### Scope and Evidence

* Task ID: bold-ui-theme
* Review date: 2026-10-20
* Review scope: full task (P01)
* Assessed boundary: plan FR-001 to FR-003, NFR-001 to NFR-005, tasks P01-T01 to P01-T05, critique dispositions PC-001 to PC-003, the changes record's claims
* Review depth and provenance: standard; default
* Candidate identity: bold-ui-theme, full task, current working tree after implementation
* Review execution: Complete
* Helper use: none (subagents=none)
* Plan: .copilot-tracking/plans/2026-10-20/bold-ui-theme-plan.md
* Plan critique: .copilot-tracking/reviews/plans/2026-10-20/bold-ui-theme-plan-critique.md
* Changes: .copilot-tracking/changes/2026-10-20/bold-ui-theme-changes.md
* Other evidence considered: .copilot-tracking/research/2026-10-20/bold-ui-theme-research.md, static/index.html, tests/test_page.py, README.md

### Opening Review State

* Interpreted review goal: check that the Bold restyle meets the plan's Requirements and that the changes record's claims are true
* Review scope: full task
* Evidence readiness: plan (all markers checked), critique (Revise, all resolved), changes record (Complete, review-ready), source and tests
* Acceptance basis: plan FR and NFR, task Requirements, the binding colour-variable contract
* First comparison boundary: source and tests against task Requirements; recorded validation compared to claims
* Active read-only boundaries: this record only
* Authority: the review parent compares evidence and writes findings; final outcome, route dispositions, and continuation are recorded in Parent Decision Record
* Initial blockers: none

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|----------------------|----------------------------------------|------------|----------------------|
| FR-001 (Bold look, grid, gradient, dark variant) | static/index.html `<style>`: 18 px cards, grid with capped minimums, gradient on `button.primary` and the heading bar, `prefers-color-scheme: dark` block; tests for radius, gradient, grid, dark block | Met | none |
| FR-002 (chips keep the words, incl. reminders) | `chipClass` and six uses (list priority and status, preview, suggestion, reminder label span plus text node); visible text unchanged; browser reminder checks (recorded) | Met | none |
| FR-003 (behaviour unchanged, plain text) | 17 ids and 16 labels pinned; no `innerHTML` and friends; browser run 129/129 (recorded) | Met | none |
| NFR-001 (contrast 4.5 to 1) | contrast test over the contract pairs in both schemes | Met with a coverage gap | RV-001 |
| NFR-002 (375 px) | `minmax(min(100%, ...))` grids; browser check at 375 px (recorded) | Met | none |
| NFR-003 (offline tests, free port, title confirmed) | suite re-run offline; browser run on a free port with the title check (recorded) | Met | none |
| NFR-004 (textContent only) | scan test; `document.createTextNode` for the reminder text | Met | none |
| NFR-005 (no library, font, framework) | reviewer check: no external URL, font-face or import | Met | none |
| P01-T01 contract (variable names, dark only in the media block) | every contract name defined in `:root` and redefined in the dark block; no undefined variable | Met | none |
| P01-T04 dark check | dark run at 375 px recorded | Met (as scoped) | limit noted above |
| P01-T05 (README, secrets scan) | README line present; scan recorded | Met | none |
| Plan status reconciliation | plan Executive Summary and readiness table | Gap | RV-002 |

### Critique and Follow-Up Assessment

* Latest critique dispositions: PC-001 (reminder chips, resolved in P01-T03), PC-002 (variable contract, resolved in P01-T01 and P01-T02), PC-003 (dark browser run, resolved in P01-T04); each resolution is visible in the code and the changes record.
* Material revisions: none after the critique.
* Dependent-work pause assessment: no early resumption; no decision was needed during implementation.
* Justification assessment: supported.

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|----------------|-----------------------------|----------------------|----------------------|
| none in the plan | not applicable | not applicable | RV-001 and RV-002 are new distinct follow-ups, owner user |

### Reviewer Self-Check

* [x] Every requirement, marker, critique disposition, validation result and plan follow-up has an assessment or explicit gap.
* [x] Findings are evidence-grounded, severity-graded, with expected and observed behavior, a resolution condition and one route each.
* [x] Execution, outcome, validation coverage, limitations and routes are consistent.
* [x] The summary is scoped and advisory.
* [x] Standard depth assessed the material boundary without cosmetics.
* [ ] The review did not mutate source, plan, critique, research or changes and wrote only this record (met), and did not execute validation: not fully met, because the user allowed the offline suite and I also ran read-only one-off scripts (variable check, contrast arithmetic); no file other than this record changed.
* Checked boundary: FR-001 to FR-003, NFR-001 to NFR-005, tasks T01 to T05, critique dispositions, validation rows
* Missing or limited evidence: browser behaviour not re-run; dark scheme only at 375 px; Python 3.10 unavailable
