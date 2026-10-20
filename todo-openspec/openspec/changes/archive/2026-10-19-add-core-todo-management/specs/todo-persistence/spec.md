# Spec Delta

## Purpose

Keeps a user's todos saved on disk so that they are still present after the app is stopped and started again, and so one failed request never loses saved data.

## ADDED Requirements

### Requirement: Todos survive a restart
The system SHALL save every create, edit, complete and delete so the data is still correct after the app is stopped and started again. (FR-7)

#### Scenario: Restart keeps data
- **WHEN** three todos exist and the app is stopped and started again
- **THEN** the same three todos are returned, with the same field values

#### Scenario: Deleted stays deleted
- **WHEN** a todo is deleted and the app is restarted
- **THEN** the deleted todo is not returned

### Requirement: Storage is created automatically
The system SHALL create its storage on first start, with no manual setup step. (NFR-10)

#### Scenario: First start
- **WHEN** the app starts for the first time with no existing data
- **THEN** it starts successfully and returns an empty todo list

### Requirement: A failed request does not damage saved data
The system SHALL leave saved todos unchanged when a request fails validation or an unexpected error occurs while handling it. (NFR-3)

#### Scenario: Rejected request
- **WHEN** a request is rejected for invalid input
- **THEN** all previously saved todos are unchanged
