<!-- markdownlint-disable-file -->
# RPI Plan Critique: Bold UI theme (HVE build)

## Metadata

* Task ID: bold-ui-theme
* Critique date: 2026-10-20
* Plan: .copilot-tracking/plans/2026-10-20/bold-ui-theme-plan.md
* Critique execution: Complete
* Critique depth: standard
* Depth provenance: default
* Critique type: initial
* Earlier critique: not applicable

## Inputs and Criterion Boundary

* Task context and caller requirements: A presentation-only restyle of the HVE page to a "Bold" look (PD1 confirmed by the user), FR-001 to FR-003 and NFR-001 to NFR-005 in the plan, FR-8 and NFR-6 in docs/requirements.md.
* Research and evidence considered: .copilot-tracking/research/2026-10-20/bold-ui-theme-research.md; static/index.html and tests/test_page.py (read to verify claims); .github/instructions/todo-app/web-page.instructions.md.
* Decisions, dependencies, task Goals, and task Requirements considered: PD1; P01-T01 to P01-T05 Goals, Requirements, Details, References, Dependencies.
* Assessment boundary: the plan and the files above. The critique did not run the page or the browser scripts, and cannot judge whether the chosen colours will pass the contrast test.

## Lens Assessments

| Lens | Scope | Reasoning effort and source | Status | Candidates |
|------|-------|-----------------------------|--------|------------|
| Coverage | P01, FR-001 to FR-003, NFR-001 to NFR-005 | host default (assessed in this context) | direct | 1 adopted; 0 rejected |
| Evidence | claims about the page, tests and ids versus the files | host default | direct | 0 adopted; 1 rejected: the pinned id list was checked against the page and is correct |
| Executability | P01-T01 to P01-T05 order, shared names, tools | host default | direct | 2 adopted; 0 rejected |
| Risk | contrast, 375 px, plain-text rule, outside-project scripts | host default | direct | 0 adopted; 0 rejected |

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| FR-001, FR-003, NFR-001 to NFR-005 | Covered | Cited by P01-T01 to P01-T05; the pinned id list matches the page |
| FR-002 | Partial | The plan says reminder labels become chips, but P01-T03 only covers priority and status spans (PC-001) |
| P01 phase | Covered | Goals, dependencies, diagram present; order is T01 to T05 |
| PD1 | Covered | Reflected in P01-T02 |

## Verdict

* Verdict: Revise
* Rationale: No Critical or High finding. Two Medium findings would cause rework or a mismatch between tasks (reminder chips are in FR-002 but not in the task that builds them; the contrast test and the CSS have no agreed variable names), plus one Low gap about the browser script. All are direct planner corrections.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [Medium]: Reminder chips are in FR-002 and the T03 Goals but not in what T03 builds

* Related IDs: FR-002, P01-T03, P01-T04
* Evidence: plan FR-002 ("Priority, status and reminder labels are coloured chips"), P01-T03 Goals ("Priority, status and reminder labels carry classes") versus P01-T03 Requirements and Details (priority and status spans; preview, suggestion; no reminders). In static/index.html the reminders are list items whose text begins with the label (for example "Overdue: title") and the browser script checks that text.
* Concern: Making the reminder label a chip means wrapping the label in a span inside the list item, which changes markup the browser checks read. The plan neither commits to doing it nor to dropping it.
* Impact: The implementer must guess; either FR-002 is unmet or an existing browser check breaks.
* Smallest useful change: Decide in the plan: wrap the label in an inline `chip` span while keeping the list item's visible text identical ("Overdue: title ..."), and say so in P01-T03 Requirements, or remove reminders from FR-002 and the T03 Goals.
* Action owner: planning_parent
* Exact resolving evidence: FR-002, P01-T03 Goals and Requirements agree about reminders, and T04 names the text check that must still pass.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-002 -->
### PC-002 [Medium]: The contrast test and the CSS share no agreed variable names

* Related IDs: P01-T01, P01-T02, NFR-001
* Evidence: P01-T01 Requirements ("a contrast test reading the colour variables... each chip's text on its chip colour") and P01-T02 Requirements ("`--accent-a`, `--accent-b` ... and chip colours are declared"). The chip variable names, the names for text, muted text, background and card, and how the dark block is found are not stated. The current page has a single `:root` block with only `--gap`, `--line`, `--accent` and `--danger` (static/index.html).
* Concern: T01 is written first and must read names that T02 later invents.
* Impact: The tests written first cannot be run red then green without a rewrite, or T02 bends to whatever T01 guessed.
* Smallest useful change: State the variable contract in P01-T01 Requirements as a contract list (for example `--bg`, `--card`, `--text`, `--muted`, `--accent-a`, `--accent-b`, `--accent-text`, and `--chip-high-bg`, `--chip-high-text`, `--chip-medium-bg`, `--chip-medium-text`, `--chip-low-bg`, `--chip-low-text`), and that the dark values sit in a `prefers-color-scheme: dark` block, with T02 required to define exactly those.
* Action owner: planning_parent
* Exact resolving evidence: The names appear once as a contract in P01-T01 and P01-T02 refers to it.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-003 -->
### PC-003 [Low]: The dark-mode browser check needs a script change, which T04 says is unneeded

* Related IDs: P01-T04, NFR-002
* Evidence: P01-T04 Details ("Update the script only where a visible word changed (none should)") and Requirements ("the dark scheme at 375 px"). The existing stub-model script runs one colour scheme (per the research note C6).
* Concern: A dark run needs a browser context with a dark colour scheme, which the script does not do.
* Impact: The dark check could be skipped or claimed without evidence.
* Smallest useful change: Say in P01-T04 Details that the script is extended with a dark-scheme run (outside the project), and record it as not checked if it is not run.
* Action owner: planning_parent
* Exact resolving evidence: P01-T04 Details name the dark run.
* Decision route: direct planner correction

## Strengths and Residual Risk

* Strengths: one small phase; tests first; chip classes come from a fixed list; the contrast risk is handled by a test on both gradient ends; the plan avoids gradient-clipped text.
* Residual risk (accepted): final colours are not known until the contrast test runs; browser scripts live outside the project.

## Questions or Blocking Evidence Gaps

* None.

## Limitations

* The page and scripts were read, not run. The reminder markup was inferred from the page source and the research note.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning_parent
* Smallest next action: Direct revision of FR-002/P01-T03 (PC-001), the variable contract in P01-T01 (PC-002) and one sentence in P01-T04 (PC-003); then finalize.
* User response required: no
