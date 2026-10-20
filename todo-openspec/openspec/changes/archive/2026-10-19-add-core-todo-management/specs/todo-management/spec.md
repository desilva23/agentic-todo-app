# Spec Delta

## Purpose

Lets a user create, view, edit, delete, complete and filter todos through a REST API, with clear validation errors, so the todo app is fully usable without any AI feature.

## ADDED Requirements

### Requirement: Create a todo
The system SHALL create a todo from a title (required, 1 to 200 characters) and optional description, due date and priority. Priority SHALL be one of low, medium or high and SHALL default to medium. A new todo SHALL start as not completed. (FR-1)

#### Scenario: Create with only a title
- **WHEN** a client creates a todo with the title "Buy milk" and no other fields
- **THEN** the system returns the created todo with a unique id, priority medium and status active

#### Scenario: Create with all fields
- **WHEN** a client creates a todo with a title, description, due date and priority high
- **THEN** the system returns the created todo containing every supplied value

### Requirement: Reject invalid todo input
The system SHALL reject a todo that has an empty title, a title longer than 200 characters, an unknown priority or an unreadable due date. The response SHALL explain which field is wrong, and nothing SHALL be saved. (FR-1, FR-9, NFR-5)

#### Scenario: Empty title
- **WHEN** a client creates a todo with an empty title
- **THEN** the system rejects the request with an error naming the title field
- **AND** no todo is saved

#### Scenario: Title too long
- **WHEN** a client creates a todo with a title of 201 characters
- **THEN** the system rejects the request with an error naming the title field

#### Scenario: Unknown priority
- **WHEN** a client creates a todo with priority "urgent"
- **THEN** the system rejects the request and lists the allowed priorities

### Requirement: List todos
The system SHALL return all saved todos, each showing title, status, due date and priority. (FR-2)

#### Scenario: List with todos present
- **WHEN** a client requests the todo list and three todos exist
- **THEN** the system returns all three todos

#### Scenario: List when empty
- **WHEN** a client requests the todo list and no todos exist
- **THEN** the system returns an empty list and no error

### Requirement: View one todo
The system SHALL return a single todo by its id, and SHALL return a clear not-found error for an id that does not exist. (FR-9)

#### Scenario: Existing id
- **WHEN** a client requests a todo by an id that exists
- **THEN** the system returns that todo

#### Scenario: Unknown id
- **WHEN** a client requests a todo by an id that does not exist
- **THEN** the system returns a not-found error

### Requirement: Edit a todo
The system SHALL let a client change any field of an existing todo, and SHALL apply the same validation rules as when creating. (FR-3)

#### Scenario: Change the due date
- **WHEN** a client updates the due date of an existing todo
- **THEN** the system returns the todo with the new due date
- **AND** later list requests show the new due date

#### Scenario: Edit with invalid value
- **WHEN** a client updates an existing todo with an empty title
- **THEN** the system rejects the update and the todo keeps its old title

#### Scenario: Edit a todo that does not exist
- **WHEN** a client updates an id that does not exist
- **THEN** the system returns a not-found error

### Requirement: Delete a todo
The system SHALL delete a todo by its id. (FR-4)

#### Scenario: Delete existing todo
- **WHEN** a client deletes an existing todo
- **THEN** the todo no longer appears in the list

#### Scenario: Delete unknown id
- **WHEN** a client deletes an id that does not exist
- **THEN** the system returns a not-found error

### Requirement: Complete and reopen a todo
The system SHALL let a client mark a todo as completed and mark a completed todo as active again. (FR-5)

#### Scenario: Mark complete
- **WHEN** a client marks an active todo as completed
- **THEN** the todo is returned with status completed

#### Scenario: Reopen
- **WHEN** a client marks a completed todo as active
- **THEN** the todo is returned with status active

### Requirement: Filter the list
The system SHALL filter the todo list by status (all, active, completed) and by priority, and SHALL allow both filters at once. When no filter is given, all todos SHALL be returned. (FR-6)

#### Scenario: Filter by completed
- **WHEN** a client lists todos filtered by status completed, and both active and completed todos exist
- **THEN** only completed todos are returned

#### Scenario: Filter by priority
- **WHEN** a client lists todos filtered by priority high
- **THEN** only high-priority todos are returned

#### Scenario: Combined filters
- **WHEN** a client lists todos with status active and priority high
- **THEN** only todos that are both active and high priority are returned

#### Scenario: Invalid filter value
- **WHEN** a client lists todos with a status value that is not all, active or completed
- **THEN** the system rejects the request with an error listing the allowed values

### Requirement: Core features work without AI
The system SHALL provide every todo-management behavior above without requiring an AI service, an API key or network access. (FR-17, NFR-3)

#### Scenario: No API key configured
- **WHEN** the app runs with no Groq API key set
- **THEN** creating, listing, editing, deleting, completing and filtering todos all work normally
