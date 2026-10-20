<!-- markdownlint-disable-file -->
# RPI Plan Critique: Todo App with AI Assistant (HVE build)

## Metadata

* Task ID: todo-app
* Critique date: 2026-10-20
* Plan: .copilot-tracking/plans/2026-10-20/todo-app-plan.md
* Critique execution: Complete
* Critique depth: standard
* Depth provenance: default
* Critique type: initial
* Earlier critique: not applicable

## Inputs and Criterion Boundary

* Task context and caller requirements: Fresh HVE build of the shared todo app (core phase P01, assistant phase P02) from docs/requirements.md.
* Research and evidence considered: .copilot-tracking/research/2026-10-20/todo-app-lessons-research.md; docs/requirements.md; .github/instructions/todo-app/project-rules.instructions.md; .github/instructions/todo-app/web-page.instructions.md; .github/instructions/coding-standards/python-tests.instructions.md
* Decisions, dependencies, task Goals, and task Requirements considered: D1 (fresh code), D2 (one plan, two phases), PD1 (20 s overall limit); all 19 tasks' Goals, Requirements, Details, References and Dependencies; FR-001 to FR-014 and NFR-001 to NFR-011.
* Assessment boundary: The plan and the supplied files only. The earlier builds' source was not re-read (the research artifact is the evidence for it). The critique cannot judge whether the pinned library versions install, or whether the Groq client accepts a per-call timeout.

## Lens Assessments

| Lens | Scope | Reasoning effort and source | Status | Candidates |
|------|-------|-----------------------------|--------|------------|
| Coverage | all phases and tasks, FR-001 to NFR-011, AC-1 to AC-17 | host default (no subagents, assessed in this context) | direct | 2 adopted; 0 rejected |
| Evidence | plan claims, Details, References versus research and instructions | host default | direct | 2 adopted; 0 rejected |
| Executability | P01-T01 to P02-T13 order, dependencies, tools, budgets | host default | direct | 2 adopted; 1 rejected: the claim that P02-T12 should depend on P02-T10 is cosmetic (README text does not need the page to exist) |
| Risk | secrets, third-party calls, shared ports and data, unaddressed concerns | host default | direct | 1 adopted; 1 rejected: browser runs should use a temporary database path (possible improvement, not a demonstrated error; kept as residual risk) |

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| FR-001 to FR-014 | Covered | Each is cited by at least one task's Requirements (checked FR by FR) |
| NFR-001, 003 to 011 | Covered | Cited by tasks; NFR-011 lessons each map to a task (huge id T03 in P01, data block/key leak/deadline P02-T03, calendar P02-T05, time zone P02-T04, retry-skip P02-T11) |
| NFR-002 | Partial | The 20 s rule is stated but does not bound the wait (PC-001) |
| NFR-010 / AC-17 | Partial | The 10-minute target is never timed (PC-003) |
| FR-012 | Covered with an unrecorded interpretation | Reminder as plain code differs from the glossary's "agent uses the LLM" (PC-002) |
| AC-1 to AC-16 | Covered | Mapped in P01-T04, P01-T06, P02-T09, P02-T11, P02-T13 |
| P01, P02 phases | Covered | Goals, Dependencies, diagrams present; task order is consistent |
| D1, D2, PD1 | Covered | Recorded as confirmed direction; PD1 only partly honoured by the task text (PC-001) |

## Verdict

* Verdict: Revise
* Rationale: No Critical or High finding. Three Medium findings change what the plan promises or records (the deadline does not deliver the bound the user chose, an interpretation of FR-14 is unrecorded, AC-17 is never measured), and three Low items are small demonstrated inconsistencies. All are direct planner corrections.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [Medium]: The 20 s limit does not bound the wait the user was promised

* Related IDs: PD1, NFR-002, P02-T03, P02-T07, P02-T08
* Evidence: plan P02-T03 Requirements ("no model call starts after 20 seconds have passed"); P02-T03 Details (per-call timeout left open); Risks row "Groq client may not accept a per-call timeout"; PD1 row ("earlier builds could wait up to about 45 s"). P02-T07 state list and P02-T08 route contain no start time or deadline.
* Concern: A call that starts at 19 s can still run for the full 15 s timeout, so the worst case is about 35 s, close to what PD1 was meant to prevent. Also, the limit is introduced in P02-T03 but the graph state (T07) and route (T08), which own "when the message arrived", do not carry it, so agents may have no way to see it.
* Impact: The user's decision may be implemented as a no-op for the slow case, and NFR-002 would be claimed without a real bound.
* Smallest useful change: In P02-T03 require each call's time to be capped to the time left in the budget (use the client's per-call or request timeout if it supports one; otherwise run the call so control returns when the budget ends), and state the true bound in the README either way. In P02-T07 add the start time/deadline to the trace or state, and in P02-T08 set it when the request arrives, with a route test using an injected clock that yields the fixed "unavailable" 503.
* Action owner: planning_parent
* Exact resolving evidence: P02-T03, P02-T07 and P02-T08 text name the cap and where the deadline lives; the Risks row for the per-call timeout is updated to the chosen mechanism or a stated fallback bound.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-002 -->
### PC-002 [Medium]: Reminder-as-code interpretation of the requirements is not recorded as a decision

* Related IDs: FR-012, P02-T04, P02-T07
* Evidence: docs/requirements.md (Glossary: "Agent: A LangGraph node that uses the LLM to do one specific job"; FR-14 "The Reminder agent finds todos..."); plan P02-T04 Goals ("built by code and not by the AI"); research C10.
* Concern: The plan implements the Reminder agent without an LLM call, which departs from the glossary's wording. The earlier builds did the same and the user approved those designs, but this plan's Confirmed User Direction and Planning Decisions do not say so.
* Impact: A reader of the requirements could treat the HVE build as non-compliant; a later review could reopen the choice.
* Smallest useful change: Add a decision row (confirmed, owner user by prior approval of the OpenSpec design, evidence C10 and the requirements text AC-11) and one line in Confirmed User Direction; keep the Reminder node in the graph.
* Action owner: planning_parent
* Exact resolving evidence: Planning Decisions and Feedback has the row and P02-T04 cites it.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-003 -->
### PC-003 [Medium]: AC-17 (running in under 10 minutes) is never measured

* Related IDs: NFR-010, P02-T12, P02-T13
* Evidence: docs/requirements.md AC-17; plan P02-T13 Requirements ("A clean copy ... follows the README on a free port") and P02-T12.
* Concern: The clean-copy run proves the steps work but does not record how long they took, so the acceptance threshold has no evidence.
* Impact: AC-17 would be claimed as covered without a measurement.
* Smallest useful change: In P02-T13 require the clean-copy run to be timed from the first README command to a working page, and the time recorded in the changes record.
* Action owner: planning_parent
* Exact resolving evidence: P02-T13 Requirements include the timing and the 10-minute threshold.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-004 -->
### PC-004 [Low]: Test file names do not mirror modules, against the matched test instruction

* Related IDs: NFR-008, P02-T03, P02-T05 to P02-T08, Test ownership
* Evidence: .github/instructions/coding-standards/python-tests.instructions.md ("File naming mirrors module under test"); plan uses `tests/test_agent_foundation.py` for `llm.py` and `structured.py`, `tests/test_agents.py` for `orchestrator.py`, `task_agent.py` and `graph.py`, and `tests/test_chat_api.py` for `chat.py`.
* Concern: Several test files cover more than one module, and the Test ownership lock ("one test file per module") is inconsistent with that.
* Impact: A review against the test instruction would flag it; low rework.
* Smallest useful change: Either rename to mirrored files (`test_llm.py`, `test_structured.py`, `test_orchestrator.py`, `test_task_agent.py`, `test_graph.py`, `test_chat.py`) in the affected tasks, or record the grouping as a deliberate exception in Test ownership.
* Action owner: planning_parent
* Exact resolving evidence: Task Details and Test ownership name the same files.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-005 -->
### PC-005 [Low]: Exact library versions have no cited source

* Related IDs: P01-T01, P02-T01
* Evidence: plan P01-T01 and P02-T01 list exact pins; the research artifact does not contain them and Sources does not cite where they come from.
* Concern: The pins read as verified facts but come from the earlier builds' requirements files, which the plan does not cite.
* Impact: A wrong or unavailable version fails at install time; cheap to detect but unsupported as written.
* Smallest useful change: Cite the earlier builds' `requirements.txt` files in References as the origin, and say the implementer records the installed versions.
* Action owner: planning_parent
* Exact resolving evidence: References of P01-T01 and P02-T01 link or name the source.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-006 -->
### PC-006 [Low]: Two small internal contradictions in the plan text

* Related IDs: Executive Summary, P01-T01, Risks and Open Questions
* Evidence: Executive Summary ("A one-time pause point sits between phases") with no pause defined in P01-T06 or P02 Dependencies; Risks row ("do not open the earlier code while coding") versus P01-T01 Details and P02-T05 Details that point to the earlier builds' conftest and prompt.
* Concern: The pause point is described but not planned, and the fresh-code rule is stated more strictly than the task references allow.
* Impact: Minor confusion about whether a user checkpoint exists and whether the earlier code may be read.
* Smallest useful change: Reword the pause as "P01-T06 is a natural stopping point; P02 starts only after it passes", and reword the risk to "write from this plan and the research; the earlier code may be read as evidence, not copied".
* Action owner: planning_parent
* Exact resolving evidence: The two text locations are consistent with each other.
* Decision route: direct planner correction

## Strengths and Residual Risk

* Strengths: Every requirement is cited by a task; lessons from the research each map to a test written first; read-only agents have mutation-checked tests; browser checks name a free port and a title check.
* Residual risk (accepted unless the planner decides otherwise): live checks may skip on Groq's rate limit; Python 3.10 may not be available to run; browser runs against a default database path could leave test data in the project's `todos.db` (use `TODO_DB_PATH` pointing at a temporary file); the 500 ms timing test depends on the machine.

## Questions or Blocking Evidence Gaps

* None. Whether the Groq client accepts a per-call timeout is an implementation-time check already listed in Risks.

## Limitations

* The earlier builds' source files were not re-read; claims about them rest on the research artifact. Library version availability and Groq behaviour were not checked.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning_parent
* Smallest next action: Direct revision of P02-T03, P02-T07, P02-T08 (PC-001), a decision row (PC-002), a timing requirement in P02-T13 (PC-003), then the three Low text corrections; finalize.
* User response required: no
