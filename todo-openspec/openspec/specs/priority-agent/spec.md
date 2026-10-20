# priority-agent Specification

## Purpose
Helps a user decide how urgent a todo is by suggesting a priority with a short reason, for a todo they describe or one that is already saved, without changing anything.

## Requirements

### Requirement: Suggest a priority with a reason
The Priority agent SHALL answer a request for a priority suggestion with one of low, medium or high and a one-sentence reason of at most 200 characters, taking the todo's wording and due date into account. It SHALL only return the suggestion and SHALL NOT change any todo. (FR-13)

#### Scenario: Saved todo that is due soon
- **WHEN** a todo "Submit tax return" is saved with a due date of tomorrow, and the user asks "what priority should 'Submit tax return' be?"
- **THEN** the reply contains a priority of low, medium or high and a one-sentence reason
- **AND** the saved todo is unchanged

#### Scenario: Todo that is only described
- **WHEN** the user asks "how important is 'organise my bookshelf'?" and no saved todo matches
- **THEN** the reply still contains a priority and a reason
- **AND** the reply says that no saved todo matched

#### Scenario: Long reason
- **WHEN** the AI gives a reason longer than 200 characters
- **THEN** the reason in the reply is shortened to 200 characters or fewer

### Requirement: Link the suggestion to a saved todo
When the message names a saved todo that is not completed, the suggestion SHALL identify that todo by its id and title, and the agent SHALL use its due date as context. The agent SHALL consider at most 50 such todos, soonest due first, and SHALL ignore any todo id that is not among them. (FR-13)

#### Scenario: Message names a saved todo
- **WHEN** the user asks about a saved todo by name
- **THEN** the suggestion carries that todo's id and title

#### Scenario: The AI names a todo that does not exist
- **WHEN** the AI answers with a todo id that is not among the todos it was given
- **THEN** the suggestion is returned without a linked todo

#### Scenario: More than 50 active todos
- **WHEN** 120 active todos are saved
- **THEN** at most 50 of them, the soonest due first, are given to the AI as context
