<!--
SYNC IMPACT REPORT (temporary review note; remove before committing)
Version change: (template, unversioned) -> 1.0.0
Modified principles: none (initial ratification)
Added principles: I. Agents Are Read-Only by Construction; II. Core Works Without AI;
  III. Secrets and Private Text Stay Out; IV. Test-First and Offline by Default;
  V. Validate at Every Boundary; VI. Simplicity and Plain Language
Added sections: Technology and Safety Constraints; Development Workflow and Quality Gates
Removed sections: none (template had 5 principle slots; 6 were requested, so one slot was added)
Follow-up TODOs: none. [GUIDANCE_FILE] resolved to README.md, which the first feature must create.
-->

# Agentic Todo App Constitution

## Core Principles

### I. Agents Are Read-Only by Construction

Agent code MUST NOT import, call or hold any ability to create, edit or delete saved todos. An
agent MAY only receive a read-only function that returns the todos it needs. Anything an agent
proposes (a todo preview, a priority suggestion) MUST be saved or applied only when the user
presses Confirm or Accept, and that action MUST use the normal todo requests. A test MUST fail
if any agent module imports storage code.

Rationale: a prompt rule such as "never delete" can be bypassed by a crafted message; the lack of
any write ability cannot be. Even a fully manipulated model can then only produce a proposal.

### II. Core Works Without AI

Creating, listing, editing, completing, deleting and filtering todos MUST work with no AI
service, no API key and no network. A failure of the AI service (missing key, rejected key,
rate limit, timeout, unusable output) MUST NOT break the app or lose or change any todo, and
MUST show a clear plain-language error.

Rationale: the todo list is the product; the assistant is a convenience on top of it.

### III. Secrets and Private Text Stay Out

The Groq API key MUST live only in `.env`, which MUST be git-ignored, and MUST NOT appear in
code, logs, responses, error messages, tests or the repository. Logs MUST record only the
decision (intent, agent used, outcome, duration) and MUST NOT contain user message text, todo
titles or descriptions, or the key. Raw error text from the AI provider MUST NOT be passed on to
users or logs.

Rationale: provider errors and prompts can echo secrets and personal data.

### IV. Test-First and Offline by Default

Tests MUST be written with or before the code they cover. The default test run MUST pass with no
network and no API key, using a fake model and a temporary database for every test, and MUST
strip any real key from the environment so a test cannot reach the real provider by accident.
Tests that call the real Groq MUST be opt-in (`RUN_LIVE=1`), MUST skip rather than fail when the
provider rate-limits, and MUST NOT be part of the default run. Every bug found after a feature
is built MUST get a regression test.

Rationale: fast, deterministic, free tests that anyone can run; real-model checks stay available
without making the suite flaky.

### V. Validate at Every Boundary

All input MUST be validated on the server. Model output MUST be requested as plain JSON and
validated with Pydantic, with at most one retry, and the app MUST NOT depend on any
model-specific structured-output feature. User text and saved todo text MUST be placed inside
clearly marked data blocks in prompts, with any copy of the block's own tag removed first, and
MUST NOT be treated as instructions. An identifier returned by a model MUST be accepted only if
it was among the values supplied to it.

Rationale: models are unreliable and attackable; validation is what keeps their mistakes small.

### VI. Simplicity and Plain Language

Build the smallest thing that satisfies the spec; speculative features MUST NOT be added. Errors
and interface text MUST be in plain language and MUST NOT show raw technical output. The page
MUST work at a width of 375 px without horizontal scrolling, and MUST insert user and AI text
with safe DOM methods (no `innerHTML` with such text).

Rationale: a small, readable app is easier to verify, and plain wording is what users can act on.

## Technology and Safety Constraints

- Backend: Python with FastAPI. Storage: SQLite through the standard library `sqlite3` with
  parameterised queries only (no ORM, no string-built SQL).
- Frontend: one plain HTML/JS page served by FastAPI. No frontend framework and no build step.
- Agents: LangGraph. LLM: GroqCloud, with the model name and timeout set in configuration, never
  hard-coded in logic.
- Shared requirements: `docs/requirements.md` is the source of requirement IDs (FR, NFR, AC).
  Specs and tasks MUST cite those IDs instead of inventing new ones.
- A todo's due date is a local date-time. Dates carrying a time zone MUST be converted to local
  time before being compared with the current time.

## Development Workflow and Quality Gates

- Work proceeds through the Spec Kit pipeline per feature: specify, clarify (when needed), plan,
  tasks, analyze, implement, converge. The user reviews the result of each step before the next.
- A feature is done only when the default test suite passes offline, the page has been checked
  in a real browser (including 375 px width), and any live-model acceptance checks have been run
  at least once or are explicitly reported as not run.
- Task lists MUST land each group's tests and documentation with that group, not at the end.
- A secrets scan (the real key appears in no file other than `.env`) MUST be run before a
  feature is called done.

## Governance

This constitution supersedes other practices for this project. Every implementation plan MUST
include a Constitution Check against the principles above, and any violation MUST be justified in
the plan's Complexity Tracking section or the plan MUST be changed.

Amendments MUST be recorded in this file with an updated version and date. Versioning follows
semantic rules: MAJOR for removing or redefining a principle in a backward-incompatible way,
MINOR for adding a principle or section or materially expanding guidance, PATCH for wording
clarifications. Compliance is reviewed at the end of each feature during analysis and
verification. Runtime guidance for running the app lives in `README.md`.

**Version**: 1.0.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19
