<!-- markdownlint-disable-file -->
# Review: Todo App with AI Assistant (HVE build)

## Executive Summary

* Assessment (proposal): The app meets nearly every requirement and the evidence for it is strong. Three gaps are worth fixing or recording before calling it fully done: the 20 s per-message limit is weaker than it is described, the Delete button was never exercised in a real browser although the plan requires it, and the README claims Python 3.10 support that was not tested. Two smaller issues are noted.
* Why this matters: The 20 s limit was a decision you made (PD1), and the README tells users it holds; the Delete gap leaves one acceptance criterion (AC-4) proven only through the API, not through the page.
* Review execution: Complete
* Assessed outcome (proposal): Defects found (no Critical or High; 2 Medium, 3 Low)
* Validation coverage: Offline suite re-run during review: 318 passed, 28 skipped. Everything else (live x2, browsers, secrets scan, clean copy, Python 3.12) is taken from the changes record, whose claims I cross-checked against the code and tests but did not re-run.
* Confidence and limitations: High for what the source and tests show. Not assessed: live model behaviour (not re-run), browser behaviour (not re-run), Python 3.10.

The assessment above is the reviewer's proposal. Parent Decision Record contains the final decisions, or states that decisions are pending.

## What You May Not Know

* The Groq client applies a single number as the limit for each phase of a request (connect, send, wait for reply, pool) separately. So capping a call to "the time left" does not guarantee that one call ends within it on a bad network. Normal conditions are unaffected (replies took about 1 to 2 seconds in the live runs).
* The strongest evidence in the record is that the safety and regression tests were each shown to fail when the code was deliberately broken (12 mutation checks recorded). I re-ran the suite and found no mutation left behind in the source.
* The core app now imports the AI libraries when it starts (the chat route is part of the app), so if `langgraph` were missing the whole app, not just the assistant, would fail to start. A normal install from `requirements.txt` has them.

## Findings and Proposed Routes

<!-- rpi:review id=RV-001 -->
### RV-001 [Medium]: The 20 s per-message limit does not bound a single slow call as the README and plan describe

Each model call is given `timeout = min(15, time left)`. The HTTP library treats a single number as a separate limit for connecting, sending, waiting and pool access, so one call on a bad network can take up to about four times that number. The README says each call is "limited to the time left", and PD1 was chosen to keep worst-case waits bounded.

* Related scope: P02-T03, P02-T08, NFR-002, PD1, critique PC-001
* Expected behavior: "the wait for one message is bounded by about 20 seconds" (plan P02-T03 Requirements and Details; PD1 in User Decisions).
* Observed behavior and evidence: `app/agents/llm.py`, `call_model` passes `timeout=min(get_groq_timeout(), left)`. `tests/test_llm.py` (real-client test) proves the value reaches the client's `create` call, not the elapsed time. In the installed `httpx`, `Timeout(4.0)` gives connect, read, write and pool all 4.0 (checked in the project environment). No test or live run measured a slow or hung call.
* Impact: In a degraded network a message could wait well over 20 s while the page shows "Thinking...", which is what PD1 was meant to prevent. Normal use is unaffected.
* Resolution condition: Either the total time for one message is enforced (for example by returning control when the budget ends, or by giving the client a timeout whose connect, write and pool parts are short and whose total is what is left) with a test using a call that hangs, or the README, plan and changes record state the real bound in plain words.
* Proposed destination: rpi-implement
* Smallest useful next action: Decide the bound to promise, then make the code or the wording match and add a test with a deliberately slow fake.

<!-- rpi:review id=RV-002 -->
### RV-002 [Medium]: The page's Delete button was never exercised in a real browser, although P01-T06 requires it

The core gate required, in a real browser, "add, edit, complete and reopen, delete, filter, and a stop-and-restart". The browser runs clicked every other control but removed todos through the API. The changes record is honest about this (Validation Record row "Delete button clicked in a real browser: Skipped"), yet the task is checked complete.

* Related scope: P01-T06, FR-004, AC-4
* Expected behavior: Plan P01-T06 Requirements list delete among the browser checks; AC-4: after deleting, the todo no longer appears in the list.
* Observed behavior and evidence: `static/index.html` has the Delete handler (`act(error, () => call("DELETE", ...))`); `tests/test_api.py` proves `DELETE /todos/{id}` returns 204 and removes the todo; the changes record's P01-T06 entry and Validation Record say the button itself was not clicked in a browser.
* Impact: The one control that removes data has no end-to-end evidence through the page (for example, handling of the empty 204 response). A defect there would be invisible to every test.
* Resolution condition: A real-browser check that clicking Delete on a todo removes it from the list and from `GET /todos`, recorded in the changes record.
* Proposed destination: rpi-implement
* Smallest useful next action: Add the Delete click to the browser script, run it on a free port and record the result.

<!-- rpi:review id=RV-003 -->
### RV-003 [Low]: The README promises Python 3.10 or newer, but nothing was run on 3.10

The requirements assume Python 3.10 or newer and the README says so. 3.10 is not installed here; the suite was run on 3.14.7 and 3.12.13. The code was written to avoid newer syntax and rewrites a trailing `Z` for 3.10, but that is untested.

* Related scope: P01-T01, NFR-010, requirements assumption 2
* Expected behavior: The documented minimum Python version works.
* Observed behavior and evidence: `README.md` "You need Python 3.10 or newer"; changes record Validation Record row "Default suite on Python 3.10: Unavailable"; plan Risks row accepts it as residual risk.
* Impact: A 3.10 user could hit a failure the evidence cannot rule out. It was an accepted, disclosed risk, so this is a documentation-versus-evidence gap, not a surprise.
* Resolution condition: Run the default suite on 3.10 and record it, or change the README to state the versions actually verified (3.12 and 3.14).
* Proposed destination: follow-up
* Smallest useful next action: Pick the cheaper of the two (reword the README, or run on 3.10 where it is available).

<!-- rpi:review id=RV-004 -->
### RV-004 [Low]: A model answer of `true` can link the suggestion to todo number 1

The Priority agent accepts a todo id only if it was among the todos shown, and always takes the title from our data. The id is read as an integer, and the validator accepts the JSON value `true` as 1 (and `"2"` as 2). If todo 1 was shown, a malformed `true` would link the suggestion to it.

* Related scope: P02-T06, FR-011, NFR-005, project rule "a model-supplied identifier is accepted only if it was among the values supplied"
* Expected behavior: A model-supplied identifier is used only if it is a genuine id from the supplied list.
* Observed behavior and evidence: `app/agents/priority_agent.py`, `_Answer.todo_id: Optional[int]`; checked in the project environment: `todo_id=True` gives 1 and `"2"` gives 2. `tests/test_priority_agent.py` covers an invented id (99) but not a boolean or text id.
* Impact: Very small. The user still sees the real title next to Accept and must press it; nothing changes without that. It is a gap against the strictness of the project rule rather than a harmful path.
* Resolution condition: A strict integer rule for `todo_id` (a boolean or text is rejected or treated as no link), with a test.
* Proposed destination: rpi-implement
* Smallest useful next action: Make the field strict and add a parametrized test for `true` and `"1"`.

<!-- rpi:review id=RV-005 -->
### RV-005 [Low]: The plan's Executive Summary still says "ready for implementation"

After implementation the plan's summary line "Planning result: Complete and ready for implementation" is stale. Its readiness table was updated ("implemented"), but the summary was not.

* Related scope: plan Executive Summary, Planning Readiness and Next Step
* Expected behavior: Implementation-time updates reconcile the executive summary with current state (references/implementation.md, plan updates).
* Observed behavior and evidence: `.copilot-tracking/plans/2026-10-20/todo-app-plan.md` Executive Summary "Planning result" bullet versus the Planning Readiness row "Complete; implemented".
* Impact: A cosmetic inconsistency a reader may notice; no effect on the code.
* Resolution condition: The summary states the current status.
* Proposed destination: follow-up
* Smallest useful next action: Reword the one bullet at the next plan touch.

## Parent Decision Record

<!-- Decisions live here. Append events; never rewrite the evidence body above to fit a decision. -->

### Current Disposition

* Based on events: RD-002 to RD-009
* Review execution: Complete
* Final outcome: Defects found (two Medium and three Low findings, all accepted; no Critical or High)
* Finding decisions and next actions: RV-001 accepted, rpi-implement (user); RV-002 accepted, rpi-implement (user); RV-003 accepted, follow-up (user); RV-004 accepted, rpi-implement (user); RV-005 accepted, follow-up (user)
* Decisions still needed: none

This summary is derived from Decision History, not a second decision record. The latest event for each subject governs; refresh this summary after appending decisions and on recovery.

### Decision History

| Event | Subject | Decision source | Status or value | Proposed destination | Final destination | Owner | More information needed | Smallest next action | Rationale |
|-------|---------|-----------------|-----------------|----------------------|-------------------|-------|--------------------------|----------------------|-----------|
| RD-001 | participation | system | user-owned (standalone default), subagents none | none | none | user | none | walk through each actionable finding | Invoked standalone with participation mode user-owned |
| RD-002 | RV-001 | user | accepted | rpi-implement | rpi-implement | user | none | decide the bound to promise; enforce a real total wait or reword the README; add a slow-call test | Medium: PD1 promise not fully delivered on a bad network |
| RD-003 | RV-002 | user | accepted | rpi-implement | rpi-implement | user | none | click Delete in a real browser on a free port and record the result | Medium: plan P01-T06 required it; only API evidence exists |
| RD-004 | RV-003 | user | accepted | follow-up | follow-up | user | none | reword README to tested versions or run on Python 3.10 | Low: disclosed, accepted risk |
| RD-005 | RV-004 | user | accepted | rpi-implement | rpi-implement | user | none | make todo_id strict; add parametrized test | Low: stricter than the project rule requires |
| RD-006 | RV-005 | user | accepted | follow-up | follow-up | user | none | reword the plan Executive Summary bullet at the next plan touch | Low: cosmetic |
| RD-007 | walkthrough | system | completed (RV-001 to RV-005 decided, none remaining) | none | none | user | none | none | all actionable findings walked through one at a time |
| RD-008 | execution | system | Complete | none | none | user | none | none | evidence body complete within the boundary |
| RD-009 | outcome | system | Defects found | none | none | user | none | route accepted findings | two Medium and three Low findings accepted; none Critical or High |

## Validation Evidence

| Command | Scope | Status | Summary |
|---------|-------|--------|---------|
| `python -m pytest -q` (re-run by the reviewer, offline only) | project | Passed | 318 passed, 28 skipped (live tests skip by default) |
| Live Groq suite, twice | tests/test_live_groq.py | Passed (recorded, not re-run) | 28 passed twice, no skips, per the changes record |
| Real-browser checks (core 20/20, stub model 85/85, real Groq 14/14) | page and assistant | Passed (recorded, not re-run) | per the changes record; Delete button not clicked (RV-002) |
| Secrets scan, clean copy, network-blocked, fake-key and Python 3.12 runs | project | Passed (recorded, not re-run) | per the changes record; clean copy timed with a warm pip cache |
| Python 3.10 run | project | Unavailable | 3.10 not installed (RV-003) |
| Diagram rendering in light and dark themes | plan | Unavailable | no preview available |

## Risks, Blockers, and Residual Work

* Blockers: none
* Remaining active work: none (all plan markers checked)
* Residual work: the OpenSpec build's weekday-date defect (research C6) is outside this task; app imports AI libraries at start-up (see What You May Not Know), an accepted design carried over from the earlier builds, no action proposed; browser checks only covered three widths.

## Review Record

### Scope and Evidence

* Task ID: todo-app
* Review date: 2026-10-20
* Review scope: full task (P01 and P02)
* Assessed boundary: plan FR-001 to FR-014, NFR-001 to NFR-011, every task's Requirements, requirements AC-1 to AC-17, implementation-time updates, critique dispositions and follow-ups
* Review depth and provenance: standard; default
* Candidate identity: todo-app, full task, current working tree after implementation
* Review execution: Complete
* Helper use: none (subagents=none)
* Plan: .copilot-tracking/plans/2026-10-20/todo-app-plan.md
* Plan critique: .copilot-tracking/reviews/plans/2026-10-20/todo-app-plan-critique.md
* Changes: .copilot-tracking/changes/2026-10-20/todo-app-changes.md
* Other evidence considered: .copilot-tracking/research/2026-10-20/todo-app-lessons-research.md, docs/requirements.md, project instruction files, source under app/, static/, tests/

### Opening Review State

* Interpreted review goal: check that what was built meets the plan's task Requirements and docs/requirements.md, and that the changes record's claims are supported
* Review scope: full task
* Evidence readiness: plan (all markers checked), critique (Revise, all six findings disposed), changes record (Complete, review-ready), research, source and tests
* Acceptance basis: plan FR-001 to FR-014 and NFR-001 to NFR-011, task Requirements, docs/requirements.md AC-1 to AC-17
* First comparison boundary: source under app/, static/, tests/ against task Requirements; recorded validation compared to claims
* Active read-only boundaries: this record only; no fixes
* Authority: the review parent compares evidence and writes findings; final outcome, route dispositions, and continuation are recorded in Parent Decision Record
* Initial blockers: none

### Acceptance and Change Coverage

| Requirement or scope | Implementation and validation evidence | Assessment | Finding or rationale |
|----------------------|----------------------------------------|------------|----------------------|
| FR-001 to FR-003, FR-005, FR-006, AC-1 to AC-3, AC-5 to AC-7 | app/models.py, app/storage.py, app/main.py; tests/test_models.py, test_storage.py, test_api.py; browser 20/20 (recorded) | Met | Boundary, restart, huge id, 1,000-todo timing all tested |
| FR-004, AC-4 | DELETE route and storage tested; page Delete handler in static/index.html | Gap (browser evidence) | RV-002 |
| FR-007, NFR-006 | static/index.html; tests/test_page.py; browser at 1000/768/375 px (recorded) | Met | none |
| FR-008, FR-009, AC-12 | app/chat.py, app/agents/schemas.py, orchestrator.py, graph.py; tests/test_chat.py, test_orchestrator.py, test_graph.py | Met | invented intents become unknown; validation before key check tested |
| FR-010, AC-8, AC-9 | task_agent.py (calendar, 09:00 rule); tests/test_task_agent.py; live and browser runs (recorded) | Met | weekday regression test mutation-checked |
| FR-011, AC-10 | priority_agent.py; tests/test_priority_agent.py | Met with a Low gap | RV-004 |
| FR-012, AC-11 | due.py; tests/test_due.py (24 h edge, zone, ordering); PD2 recorded | Met | none |
| FR-013, AC-13 | tests/test_agent_isolation.py (AST, negative self-tests); tests/test_chat.py unchanged-todos cases | Met | mutation-checked on real files |
| FR-014, NFR-003, AC-14 | error mapping in chat.py; tests/test_chat.py; second-server browser check (recorded) | Met | none |
| NFR-001 | tests/test_api.py 1,000-todo list under 500 ms | Met | none |
| NFR-002, PD1 | Budget and call_model in llm.py; tests/test_llm.py | Gap (bound) | RV-001 |
| NFR-004, AC-15 | .gitignore, scan results (recorded), tests with fake keys | Met | none |
| NFR-005, NFR-009 | data_block, Pydantic validation, decision log line; tests | Met | none |
| NFR-007, NFR-008, AC-16 | one module per agent; offline suite re-run: 318 passed | Met | none |
| NFR-010, AC-17 | README; clean copy 13 s warm cache (recorded) | Met with a documentation gap | RV-003 |
| NFR-011 lessons | data-block, huge-id, key-leak, weekday, time-zone, retry-skip tests each present | Met | none |
| Plan updates (Guidance blocks, per-call timeout risk row) | changes record "Implementation-Time Plan Updates" | Met | the resolved risk row is the root of RV-001's claim |
| Plan Executive Summary reconciliation | plan Executive Summary | Gap | RV-005 |

### Critique and Follow-Up Assessment

* Latest critique dispositions: PC-001 to PC-006 all resolved; PC-001's route test and per-call cap exist in tests/test_chat.py and tests/test_llm.py, but see RV-001 about the strength of the bound.
* Material revisions: Guidance blocks and a resolved risk row only; no requirement or design changed.
* Dependent-work pause assessment: no early resumption; no decision was needed during implementation.
* Justification assessment: supported; the entry correcting an inaccurate claim shows the record was checked against output.

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|----------------|-----------------------------|----------------------|----------------------|
| none in the plan | not applicable | not applicable | The OpenSpec weekday defect is recorded in the research only; distinct follow-up, owner user |

### Reviewer Self-Check

* [x] Every supplied requirement, in-scope marker, material update, critique disposition, validation result, blocker, remaining item, and plan follow-up has an assessment or explicit gap.
* [x] Findings are substantive, evidence-grounded, severity-graded, and use stable `RV-xxx` IDs with expected and observed behavior, a resolution condition, and one proposed route each.
* [x] Execution status, assessed outcome, validation coverage, limitations, and proposed routes are consistent.
* [x] The summary is scoped and advisory; coverage distinguishes demonstrated gaps from unassessed behavior.
* [x] Standard depth assessed the material boundary without restatement or cosmetics.
* [ ] The review did not mutate source, plan, critique, research or changes and wrote only this record (met), and did not execute validation: not fully met, because the user allowed one offline test run and I also ran read-only one-off Python checks in the project environment (id coercion, timeout semantics); neither changed any file.
* Checked boundary: all FR, NFR and AC listed above, all 19 task markers, implementation-time updates, critique dispositions, follow-ups, validation rows
* Missing or limited evidence: live model and browser results were not re-run; Python 3.10 unavailable
