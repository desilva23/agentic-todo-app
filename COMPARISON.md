# OpenSpec vs Spec Kit vs HVE: what we saw building the same app three times

Same requirements, same stack (FastAPI, SQLite, LangGraph, GroqCloud), same shared rules. Each app was built with one method,
and each later got a UI restyle through the same method. This table is what actually happened, not a generic description.

## 1. The methods side by side

| | **OpenSpec** | **Spec Kit** | **HVE (Hypervelocity Engineering)** |
|---|---|---|---|
| **Core idea** | Describe each change as a small **delta spec** (what is ADDED or MODIFIED), build it, then **archive** it so the main specs stay "how the app works now" | A **constitution** (project rules) governs every feature; each feature goes spec, plan, tasks, implement | **Research, Plan, Implement, Review**; every stage writes a file, and a separate **critique** and **review** check the work. "The AI carries the rules, humans keep the judgment" |
| **Main steps** | `propose` (proposal + delta spec + design + tasks), `apply`, `verify`, `archive` | `constitution`, `specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement` | `research`, `plan` (+ critique), `implement`, `review` (+ walkthrough) |
| **Where the paper trail lives** | `openspec/specs/` (living, 8 capabilities) and `openspec/changes/archive/` (history, 4 changes) | `.specify/` (constitution, templates) and `specs/00N-name/` (3 features) | `.copilot-tracking/` (dated research, plan, critique, changes, review) and `.github/instructions/` (rules) |
| **What a spec/plan looks like** | Short requirements with WHEN/THEN scenarios; design as numbered decisions | User stories with priorities, Given/When/Then, success criteria; plan with a Constitution Check; research, data model, contracts, quickstart | A plan of phases and tasks with Goals and Requirements, Before/After diagrams, evidence IDs (C1, W1), critique findings (PC-xxx), review findings (RV-xxx) |
| **Where the rules live** | `config.yaml` context and rules (a few lines) | `constitution.md` (6 principles, 114 lines), checked in every plan | Instruction files that apply by file pattern (Python rules, page rules, test style) |
| **Independent check built in** | `verify` compares code to the artifacts (after the work) | `analyze` checks spec, plan and tasks agree (before the work) | A separate **plan critique** before any code, and a **review** after |
| **Who decides** | You approve each artifact; the AI drafts | You approve the spec and answer clarifications | You answer decision questions at each stage, with a recommendation and evidence |
| **Weight for a small change (the UI restyle)** | 4 files + 12 tasks, one sitting | spec, plan, research, data-model, contract, quickstart, tasks (14 tasks); data-model and contracts said "nothing changes" | research, plan, critique, changes record, review (5 files, 5 tasks); the most ceremony |
| **Feel / learning curve** | Lightest, easiest to start | Medium: more templates, but very clear structure | Heaviest: many stages and terms, but it forces the most thinking before and after coding |
| **Where it helped most (observed)** | Archiving kept the main specs short and current; the delta idea is easy to explain | The constitution turned earlier lessons into standing rules; the Spec Kit plan included the fixes from day one | The critique caught real flaws before code (for example, the 20 s time limit would not really have bounded the wait); the review caught more (Delete never clicked in a browser, a loose id check) |
| **Where it hurt (observed)** | No independent critique or review stage (only `verify`): the weekday-date bug stayed hidden in this build until the other build found it | Heavy documents for tiny changes; many files to keep in step | Most overhead; its plan and summary lines went stale twice after the work finished; fresh code lost a lesson the older builds had (connections were not closed) until the coverage run exposed it |
| **Best when** | Small teams, fast changes, a long-lived app whose specs should stay current | Rules matter (compliance, safety, many features), and you want every feature specified the same way | The work is high-stakes or complex, you want independent checks and a decision trail, or several people share decisions |

## 2. Measured numbers

| | OpenSpec | Spec Kit | HVE |
|---|---|---|---|
| App code (lines in `app/`) | 882 | 895 | 1,016 |
| Test code (lines in `tests/`) | 1,872 | 1,852 | 3,013 |
| Offline tests that pass (live tests skipped) | 237 | 264 | 392 |
| Python line / branch coverage | 99.1% / 97.1% | 99.6% / 97.1% | 99.6% / 97.7% |
| Method paper trail (markdown files) | 31 | 24 (+ constitution) | 10 tracking files + 5 instruction files |
| Problems the method's own checks found before delivery | a prompt-escape bug found in verification | the fixes were planned in from the start | 9 plan findings (critique) + 7 review findings; 3 of the review findings were sent back to implementation |

## 3. Read this before trusting the table

- **Order matters.** OpenSpec came first, Spec Kit second, HVE third. The later builds started with lessons from the earlier ones, so HVE looks better partly because it came last.
- **One small app, one AI, one person.** This shows how each method *feels* on a small project. It does not prove how they scale to a team.
- **Test counts are not quality scores.** HVE has more tests partly because its instruction files ask for a particular test style (small, named, parametrised tests), not only because of the method.
- **Effort and time were not measured**, only the number of artifacts and lines.
- **Some method friction was tooling:** the Spec Kit and OpenSpec skills only load when you work inside their project folder, so some steps were followed by hand from the same instructions.

## 4. A simple way to choose

- Want **speed and simplicity**: OpenSpec.
- Want **strong, repeatable rules** across many features: Spec Kit.
- Want **independent checking and a record of decisions**: HVE.
- They are not exclusive: the common ground is "write down what you want before the AI builds it, and check it afterwards".
