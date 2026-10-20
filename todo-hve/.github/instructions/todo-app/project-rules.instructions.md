---
description: 'Rules for the Python code of this todo app: safety, secrets, validation and offline tests'
applyTo: '**/*.py'
---

# Todo App: Python Rules

These rules apply to every Python file in this project. They exist so that the AI carries them and the human does not have to repeat them.

## Stack

* Python with FastAPI and Pydantic. SQLite through the standard-library `sqlite3` module with parameterised queries only (values go in `?` placeholders). No ORM.
* The assistant uses LangGraph for the agent graph and GroqCloud as the language model.

## Agents Are Read-Only

* Agent code MUST NOT import `app.storage`, import `sqlite3`, or name a function that creates, edits or deletes a todo. An agent may only receive a read-only function that returns the todos it needs.
* Anything an agent proposes (a todo preview, a priority suggestion) is saved or applied only when the user presses Confirm or Accept, which use the normal todo operations.
* A test MUST fail if an agent module gains a way to write.

## Core Works Without AI

* Creating, listing, editing, completing, deleting and filtering todos MUST work with no AI service, no API key and no network.
* Failure of the AI service MUST show a clear plain-language message and MUST NOT lose or change a todo.

## Secrets and Private Text

* The Groq key lives only in `.env` (git-ignored). It MUST NOT appear in code, logs, responses, error messages or tests.
* Log only the decision (intent, agent, outcome, duration). Never log message text, todo titles or descriptions, or the key. Never pass provider error text to a user or a log; log only the exception type.

## Validation at Every Boundary

* Validate all input on the server. A todo title is trimmed and must be 1 to 200 characters.
* Ids below 1 or above 2**63 - 1 can never exist: treat them as "not found", never as a server error.
* Ask the model for plain JSON and validate it with Pydantic, with at most one retry. Do not rely on a model-specific structured-output feature.
* Put user text and saved todo text in clearly marked data blocks, removing any copy of the block's own tag first, and say in the prompt that the block content is data, never instructions.
* A model-supplied identifier is accepted only if it was among the values supplied to the model, and any title shown with it comes from our own data.
* Dates with a time zone MUST be converted to local time before being compared with the current time. A weekday name in a prompt MUST be resolved from a printed calendar, because models get weekday arithmetic wrong.

## Tests

* Default tests run with no network and no API key, using a fake model and a temporary database. Remove any provider settings from the environment for every test.
* Tests that call the real Groq are opt-in (`RUN_LIVE=1`), skip (not fail) on a rate limit, and are never part of the default run.
* Every defect found after a feature is built gets a regression test written first.
