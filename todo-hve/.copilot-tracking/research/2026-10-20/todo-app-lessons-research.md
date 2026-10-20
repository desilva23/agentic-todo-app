<!-- markdownlint-disable-file -->
# Task Research: todo-app-lessons

| Field              | Value                       |
|--------------------|-----------------------------|
| Date               | 2026-10-20                  |
| Researcher / agent | rpi-research (Claude Code)  |
| Output mode        | convergence                 |

## Executive Summary

* Bottom line: The two earlier builds (OpenSpec, Spec Kit) already agree on almost every design choice, so the HVE build should reuse the *decisions* and write the *code* fresh. Five defects were found late in those builds. Four are already fixed in the Spec Kit build. One (weekday arithmetic by the model) is fixed only in the Spec Kit build and is still latent in the OpenSpec build. The HVE plan should make all five into tests written before the code.
* Why this matters: Starting from the lessons moves each of those defects from "found during verification" to "prevented in the plan", which is the point of HVE's Research then Plan then Implement order.
* Research status: Complete (one full three-wave cycle). Your two decisions are recorded: write fresh code, and use one plan with two phases.
* Confidence and uncertainty: High for what is written in the two projects (every claim cites a file). Medium for what the lessons imply for a third build, because it has not been built yet. Not tested in either build: simultaneous use, a long outage of the model service, and the real browser at other widths than 1000 px and 375 px.

## What You May Not Know

* The OpenSpec build's Task agent still has the weekday defect. Its prompt says only "Current local time: ... (Monday)" (C6), while the Spec Kit build fixed this with a printed 14-day calendar after the real model answered "Friday" as Thursday in 4 of 5 runs (C4, C5). Nobody went back to patch OpenSpec because that app was already finished and zipped.
* The two earlier apps are nearly the same code: about 1,390 lines each under `app/` and `static/`, and the Reminder logic differs only in comments and one variable (C11). The *method* differed (artifacts and process), not the *product*. For a three-way comparison the HVE build should therefore be fresh code, so the comparison is about process.
* The earlier test suites use plain `monkeypatch` and descriptive names. The HVE build's test standard (`python-tests.instructions.md`) asks for pytest-mock and `test_given_..._when_..._then_...` names with Arrange/Act/Assert (C13). Copying the old tests would break the HVE build's own rules.
* A single message can cost up to three model calls (orchestrator, task agent, one retry), each with a 15 s timeout. The OpenSpec design accepted this as a risk with no overall deadline (C9). It was never changed.

## Findings

### 1. Five defects were found late, and each has a known fix and test

Late means during verification or live testing, not at design time. The HVE plan can turn each into a test written first.

| # | Defect | Fix | Where it lives |
|---|--------|-----|----------------|
| 1 | A message or saved title containing a closing tag could end the data block and look like instructions | `data_block(tag, text)` removes the tag (case-insensitive, spaces, slash) | C1, C2 |
| 2 | A huge todo id (above 2**63-1) crashed SQLite with a 500 | ids outside `1..MAX_ID` are treated as "not found" | C3 |
| 3 | Real model gave the wrong date for weekdays | A 14-day calendar in the prompt (Spec Kit only) | C4, C5, C6 |
| 4 | The live test suite failed on Groq's free-tier rate limit | Retry a few times, then skip (not fail) | C7 |
| 5 | Risk that a model error text carrying the key reaches logs or responses | `call_model` logs only the exception type; a regression test uses a fake key in the error text | C8 |

* Questions: Q1
* Evidence state: evidence-backed finding
* Evidence: C1 to C8
* Confidence and limits: High. The incident of two apps answering on one port (my own test hit the user's OpenSpec app on port 8000) is from this session's history, not from a repository file, so it is recorded here as a process lesson without a C# ID and is already reflected in `CLAUDE.md` (C14).

### 2. Eight design decisions held up in both builds and should be adopted unchanged

Both builds use: a LangGraph router (orchestrator node, then a conditional edge to one agent); plain JSON validated by Pydantic with exactly one retry; agents with no storage import and a `read_todos` function passed in; the Reminder agent as plain code, not AI; unknown intents becoming `unknown`; the title of a linked todo always coming from our data; one log line per message with the decision only; a provider *function* for the route so validation happens before the key check.

* Questions: Q2
* Evidence state: evidence-backed finding
* Evidence: C1, C9, C10, C11, C12
* Confidence and limits: High that they work (191 and 208 offline tests passed, live checks passed). They were not stress-tested for concurrent users, which is outside the requirements.

### 3. The builds differ in process and test layout, not in behaviour

* OpenSpec built the product in three changes (core, agent chat, priority and reminder agents). The chat change had only two intents and was later extended, which meant re-touching tests (C9, C10).
* Spec Kit built it in two features (core, assistant) with the whole assistant planned at once, so the data-block fix, retry-then-skip and the stronger "no `app.storage` import" test were in the plan from day one (C1, C12).
* Questions: Q3
* Evidence state: evidence-backed finding
* Evidence: C9, C10, C12, C15
* Confidence and limits: High. The effect on speed or quality was not measured (and you said a comparison report is not needed).

### 4. Four kinds of verification evidence are cheap to reuse as *ideas*

1. Offline suite with a scripted fake model (`ScriptedLLM`), fixed clock, temporary database, and an autouse fixture that removes `GROQ_*` settings (C13).
2. AST tests that read the source and fail if an agent can write or imports storage, each with negative self-tests that prove the test catches a violation (C12).
3. Opt-in live tests (`RUN_LIVE=1`) with retry-then-skip (C7).
4. Real-browser checks against a stub model at 1000 px and 375 px, a secrets scan, and a clean-copy run on a free port (from the Spec Kit tasks, C16).

* Questions: Q4
* Evidence state: evidence-backed finding
* Evidence: C7, C12, C13, C16
* Confidence and limits: High. The browser scripts live outside the repositories (session scratchpad), so they must be rewritten for the HVE page title.

### 5. Open unknowns are few and small

No overall deadline per message (C9); the live tests depend on a rate-limited free tier, so a skip means "not proven this run"; page checks only cover two widths; no test of two browser tabs changing the same todo.

* Questions: Q5
* Evidence state: partially supported claim (these are known gaps, not tested outcomes)
* Evidence: C9, C7
* Confidence and limits: Medium. These were not probed further because the requirements do not demand them (Assumptions say single user).

## Recommendation and Alternatives

* Recommendation or decision state: Build the HVE app as fresh code, reusing the decisions in Finding 2 and the five defect tests in Finding 1 as planned work, with tests written to the HVE standard (BDD names, pytest-mock). Plan it as one plan with two phases (core todos, then the assistant), because the two earlier builds proved the split has no product effect.
* Rationale: Fresh code keeps the three builds comparable (C11), keeps the HVE test standard intact (C13), and costs little because the design is already settled (C9, C10, C12). One plan with two phases keeps one critique and one change log while still giving a safe stopping point after the core.
* What could change this result: You wanting the quickest possible result (copy the code), or wanting two separate RPI runs to mirror the OpenSpec three-change shape.

| Option | Benefits | Costs and risks | Evidence | Disposition |
|--------|----------|-----------------|----------|-------------|
| Fresh code, lessons as tests (one plan, two phases) | Comparable process; fits HVE test rules; lessons become checks | More typing than copying | C11, C13 | selected |
| Copy the Spec Kit code, then review | Fastest; known to pass | Not a fair HVE build; tests break HVE standard; hides defects the plan should catch | C11, C13 | rejected |
| Fresh code, two separate RPI runs (core, then assistant) | Mirrors earlier shapes | Two critiques and two logs for little gain | C9, C12 | viable |
| Fresh code, assistant first | None for this app | Assistant needs the core todo operations | C9 | rejected |

## Scope and Questions

* Goal: Decide what the HVE build should carry over from the two earlier builds, so the Plan can be written with no repeated mistakes.
* Audience and use: You (a beginner learning HVE) and the later `/rpi-plan` step.
* In scope: `../todo-openspec` and `../todo-speckit` (read-only), this project's HVE instruction files.
* Out of scope: Editing the earlier projects; reading any `.env`; external web research; a comparison report.
* Decision and evidence criteria: Every claim traces to a file path with a heading or symbol; a lesson counts only if it was a real defect, a design choice that survived verification, or a gap that was recorded.
* Requested output: A recommendation for planning.

| ID | Question | Source | Status |
|----|----------|--------|--------|
| Q1 | Which defects were found late, with fix and regression test? | inferred from your request | answered |
| Q2 | Which design decisions held up in both builds? | inferred | answered |
| Q3 | Which differences between the builds matter for a third build? | inferred | answered |
| Q4 | Which verification evidence is cheap to reuse? | inferred | answered |
| Q5 | What is still unknown or untested? | inferred | answered |

## Decisions and Feedback

| Group | Decision or feedback item | Status | Owner | Rationale or input needed | Evidence | Impact of answer |
|-------|---------------------------|--------|-------|---------------------------|----------|------------------|
| D1 | Write the HVE code fresh, or reuse the earlier code | confirmed: write fresh | user | Fresh keeps the comparison fair and follows HVE test rules; reuse is faster | C11, C13 | The Plan contains build tasks for every module |
| D2 | One plan with two phases, or two separate plans | confirmed: one plan, two phases (core, then assistant) | user | One plan is simpler; two plans mirror the earlier builds | C9, C12 | One plan file and one critique |

## Risks and Open Questions

| Priority | Type | Risk, question, or research item | Impact | Smallest action or evidence needed | Owner |
|----------|------|----------------------------------|--------|------------------------------------|-------|
| M | risk | Live tests may skip because of Groq's rate limit, so the real model is not proven in a given run | Real-model behaviour (routing, dates) unproven that run | Run the live suite more than once and record skips honestly | downstream |
| M | risk | Up to three model calls at 15 s each could exceed the 10 s reply budget in a bad network | NFR-2 can be missed in poor conditions | Decide in Plan whether to add an overall deadline | user |
| L | open question | The OpenSpec build still has the weekday defect | Only matters if the user keeps using that app | Optional follow-up outside this task | user |
| L | further research | Page behaviour at widths between 375 px and 1000 px | Layout bugs in the middle | Add a 768 px check in the Plan | downstream |

## Planning Readiness and Next Step

| Field | Record |
|-------|--------|
| Research disposition | executed |
| Decision participation | user-owned (standalone default), set in `CLAUDE.md` |
| Planning Readiness | Ready; D1 and D2 are answered, evidence C1 to C16 |
| Research depth and helpers | one cycle, three waves; no helpers (subagents=none) |
| Blockers | none |
| Output mode and planning support | convergence; supports planning |
| Continuation owner | user (manual) |
| Required gates or confirmations | passed (D1 and D2 answered 2026-10-20) |
| Next action | `/rpi-plan` |
| Primary evidence file | `.copilot-tracking/research/2026-10-20/todo-app-lessons-research.md` (date supplied by the caller) |

## Research Record

### Method and Boundaries

| Field | Record |
|-------|--------|
| Research posture and provenance | focused; caller |
| Helper lane effort | not applicable (no helpers) |
| Completion basis | All five questions answered from primary files; contrarian wave found one extra latent defect (C6) and no evidence that overturns the recommendation |
| Explicit limits or deadline | none |
| Codebase and external scope | `../todo-openspec`, `../todo-speckit`, this project's `.github/instructions`; no external scope |
| Initial candidate areas | design and research notes, agent modules, tests |
| Evidence root | `.copilot-tracking/` in this project, default |
| Constraints and excluded sources | `.env` files not read; the Groq key never recorded; earlier projects not edited |
| Prior knowledge | The session history (earlier builds) was used only as pointers to files, then re-verified in the files |

### Extensions and Participation

#### Extension Registry

| Kind | Candidate | Provenance and scoped contract | Selected or skipped reason |
|------|-----------|--------------------------------|----------------------------|
| instruction | `hve-core/copilot-tracking.instructions.md` | Matches the evidence path | selected |
| instruction | `coding-standards/python-tests.instructions.md` | Matches test files, only for planning input | selected (as evidence C13) |
| instruction | `todo-app/project-rules.instructions.md` | Matches Python; read-only research | skipped (no code is edited) |
| skill | other research-time skills | none listed | skipped |

#### Direction and Participation Log

| Checkpoint or change | Question, direction, or rationale | Answer or no-interaction reason | Result and revalidation effect |
|----------------------|-----------------------------------|---------------------------------|--------------------------------|
| intake | Topic and posture | Supplied by the invoking request (focused, convergence, subagents=none) | No question needed |
| convergence | D1: fresh code or reuse; D2: one plan or two | D1 write fresh; D2 one plan, two phases (both the recommended option) | Recommendation confirmed; no revalidation needed |

### Research Cycle Log

#### Cycle 1

* Active posture, controls, and limits: focused; read-only; no `.env`; no limits.

##### Wave 1: Wider

* Focus and questions: Q1 to Q5 across both projects' designs, tasks, research notes, code layout and tests.
* Evidence: Q1 to C1, C2, C3, C7, C8; Q2 to C9, C10, C12; Q3 to C15; Q4 to C12, C13; Q5 to C9.
* Reflection: The Spec Kit research note names the OpenSpec lessons directly, which makes it the best single source. Weekday arithmetic is the one defect without an OpenSpec counterpart, so check it in Wave 2.

##### Wave 2: Deeper

* Focus and questions: Read the exact code for each defect fix and the tests that guard it; compare `llm.py` and `due.py` line by line.
* Evidence: C3 (storage guard and huge-id test), C4 and C5 (calendar_for), C8 (call_model and leak test), C11 (diff shows the modules are nearly identical).
* Reflection: Behaviour is identical across the builds; the defects are a matter of when they were found.

##### Wave 3: Contrarian

* Focus and questions: Is there evidence that the OpenSpec build lacks a fix the Spec Kit build has? Is there evidence that copying the code is better? Do the earlier tests already meet the HVE test standard?
* Evidence: C6 (OpenSpec task agent prompt has no calendar: weakens "all five fixed in both"); C13 (earlier tests have 0 uses of `mocker` and no BDD names: weakens "reuse tests"); C11 (identical code: supports "copy is faster" but not "copy is a fair comparison").
* Reflection: The contrarian evidence changed Finding 1 (one defect is open in OpenSpec) and added the test-standard reason against reuse.

##### Synthesis and Re-entry

| Material or claim | Evidence | Disposition | Rationale | User-facing effect |
|-------------------|----------|-------------|-----------|--------------------|
| Five late defects, fixes known | C1 to C8 | accepted | Each cited in a file | Finding 1 |
| Eight design decisions held | C1, C9 to C12 | accepted | Same in both builds | Finding 2 |
| Copy the code | C11, C13 | rejected | Unfair comparison; breaks test standard | Recommendation |
| Fix OpenSpec's weekday defect now | C6 | deferred | Outside this task; user's call | Risks table |

* Another complete three-wave cycle needed: no
* Trigger or stop basis: scope covered; sources redundant (the same decisions repeat across designs and research notes); contrarian wave changed no recommendation
* Readiness or revalidation effect: none

### Evidence Log

* Helpers: none

| ID | Claim or finding | Source or location | Retrieved and version | Tool | Confidence | Notes |
|----|------------------|--------------------|----------------------------|------|------------|-------|
| C1 | Data-block tag stripping was added in the Spec Kit plan because the OpenSpec build found the escape late | `../todo-speckit/specs/002-ai-assistant/research.md`, "R-6. Data blocks for untrusted text" | not applicable | read | high | Also `../todo-speckit/app/agents/structured.py`, `data_block` |
| C2 | OpenSpec design records the same fix ("found during verification, now covered by tests") | `../todo-openspec/openspec/changes/archive/2026-10-19-add-agent-chat/design.md`, "6. Prompt-injection posture" | not applicable | read | high | |
| C3 | Ids outside 1..2**63-1 are "not found"; a test uses a 20-digit id | `../todo-speckit/app/storage.py`, `MAX_ID`, `_id_can_exist`; `../todo-speckit/tests/test_storage.py`, `HUGE_ID`; same in `../todo-openspec/app/storage.py` | not applicable | grep, read | high | |
| C4 | Real model got "Friday" wrong in 4 of 5 runs; calendar fixed it (5 of 5, 30 of 30) | `../todo-speckit/specs/002-ai-assistant/research.md`, "R-9. Task agent and dates" | not applicable | read | high | The counts are the build's own recorded measurements |
| C5 | Fix is `calendar_for(now)` over 14 days | `../todo-speckit/app/agents/task_agent.py`, `calendar_for` | not applicable | read | high | A test checks the prompt holds the exact calendar |
| C6 | OpenSpec prompt gives only "now" and the weekday name; no calendar | `../todo-openspec/app/agents/task_agent.py`, `SYSTEM_PROMPT` and `system = SYSTEM_PROMPT.format(...)`; grep for "calendar" finds none | not applicable | grep, read | high | Latent defect in the finished OpenSpec app |
| C7 | Both live suites retry then skip on rate limit | `../todo-speckit/tests/test_live_groq.py`, `chat(client, message, tries=4, wait=20)`; `../todo-openspec/tests/test_live_groq.py`, same pattern with `pytest.skip` | not applicable | read | high | OpenSpec gained it after the failure; Spec Kit had it from the plan |
| C8 | `call_model` logs only the exception type; both builds have a test with a fake key in the error text | `../todo-speckit/app/agents/llm.py`, `call_model`; `../todo-speckit/tests/test_agent_foundation.py`, `test_regression_error_text_carrying_a_key_never_reaches_logs_or_the_raised_error`; `../todo-openspec/tests/test_agent_foundation.py`, `test_model_errors_do_not_leak_the_key_into_logs_or_messages` | not applicable | read, diff | high | |
| C9 | OpenSpec design: LangGraph router, JSON and one retry, no write access, data blocks, 502/503 table, one log line; Risk "No overall deadline per message" up to three calls | `../todo-openspec/openspec/changes/archive/2026-10-19-add-agent-chat/design.md`, Decisions 2 to 9 and "Risks / Trade-offs" | not applicable | read | high | |
| C10 | `read_todos` function injected; Reminder agent as code; `Intent` extended | `../todo-openspec/openspec/changes/archive/2026-10-19-add-priority-reminder-agents/design.md`, Decisions 1, 2, 6 | not applicable | read | high | |
| C11 | The two builds' `app/` modules are near-identical (diff of `llm.py` and `due.py` shows only comment and variable differences); about 1,390 lines each | `../todo-openspec/app/agents/llm.py` vs `../todo-speckit/app/agents/llm.py`; `due.py` same | not applicable | diff, wc | high | |
| C12 | Spec Kit isolation test: forbidden-names check plus stricter "no `app.storage` import", each with negative self-tests; OpenSpec has the same checks in two files | `../todo-speckit/tests/test_agent_isolation.py`; `../todo-openspec/tests/test_agents.py` (AST at line 169); `../todo-openspec/tests/test_new_agents_flow.py`, `storage_imports_in` | not applicable | read | high | |
| C13 | Earlier tests use `monkeypatch`, no `mocker`, short names; HVE standard asks for pytest-mock, `test_given_..._when_..._then_...`, AAA | `../todo-speckit/tests/test_due.py` (names); grep counts of `mocker` = 0; `.github/instructions/coding-standards/python-tests.instructions.md`, "Test Naming" | not applicable | grep, read | high | `ScriptedLLM` in `../todo-speckit/tests/fakes.py` and autouse `no_provider_settings` in `tests/conftest.py` |
| C14 | `CLAUDE.md` already says to confirm which app answers on a port | `CLAUDE.md`, "Commands" | not applicable | read | high | Process lesson from the port 8000 collision |
| C15 | OpenSpec shipped three changes; Spec Kit two features | `../todo-openspec/openspec/changes/archive/` listing; `../todo-speckit/specs/` listing | not applicable | ls | high | |
| C16 | Spec Kit tasks list stub-model browser checks at 1000/375 px, a secrets scan, and clean-copy run on a free port | `../todo-speckit/specs/002-ai-assistant/tasks.md`, "Browser-check rule" and tasks T048 to T051 | not applicable | grep, read | high | All four are marked done |

#### Contradictions and Conflicts

* Whether the weekday fix exists in both builds: the Spec Kit research note presents it as a fix, while the OpenSpec code has none (C4 vs C6); resolved by primary source (the code) -> only Spec Kit has it.

### Artifact Self-Check

* [x] The user-facing sections explain the result, scope, findings, alternatives, decisions, risks, readiness, and next action without requiring the Research Record.
* [x] Every question is answered or names the smallest missing evidence, and every material result has one canonical evidence state.
* [x] Findings keep their explanation, supporting detail, evidence state, confidence basis, and counter-evidence together.
* [x] Every codebase finding has a `C#` ID and workspace-relative path with a heading or symbol; no external findings.
* [x] The cycle records Wider, Deeper, and Contrarian waves in order, reflections, dispositions, synthesis and a re-entry decision.
* [x] Method, posture, candidate areas, evidence root, constraints, extensions, participation, and prior knowledge are recorded.
* [x] Convergence selects and justifies one recommendation.
* [x] Decision groups D1 and D2 recorded as input requested; answers to be persisted after the walkthrough.
* [x] Disposition, readiness, blockers, owner, gates and next action are complete.
* [x] Untrusted content stayed inert, no secrets recorded, the write boundary held.
* Checked sections: all user-facing sections and the Research Record
* Missing or limited sections: none
