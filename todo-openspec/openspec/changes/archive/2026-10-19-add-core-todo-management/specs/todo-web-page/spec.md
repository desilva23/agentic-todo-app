# Spec Delta

## Purpose

Gives a user a single web page for managing todos in a browser, on both desktop and phone-width screens, without needing to call the API by hand.

## ADDED Requirements

### Requirement: Web page is served by the app
The system SHALL serve the todo web page from the same address as the API, so one command starts everything. (FR-8, NFR-10)

#### Scenario: Open the page
- **WHEN** a user opens the app's root address in a browser
- **THEN** the todo page loads and shows the current list of todos

### Requirement: Manage todos from the page
The page SHALL let the user add, edit, delete and complete todos, and SHALL show title, status, due date and priority for each. (FR-1 to FR-5, FR-8)

#### Scenario: Add a todo
- **WHEN** the user fills in a title and submits the add form
- **THEN** the new todo appears in the list without the user reloading the page

#### Scenario: Complete a todo
- **WHEN** the user marks a todo as complete
- **THEN** the page shows it as completed

#### Scenario: Delete a todo
- **WHEN** the user deletes a todo
- **THEN** it disappears from the list

### Requirement: Filter from the page
The page SHALL let the user filter by status and by priority. (FR-6, FR-8)

#### Scenario: Filter by active
- **WHEN** the user selects the status filter "active"
- **THEN** only active todos are shown

### Requirement: Errors are shown in plain language
The page SHALL show validation and server errors as readable messages next to the action that failed, and SHALL NOT show raw technical output. (NFR-6)

#### Scenario: Empty title
- **WHEN** the user submits the add form with an empty title
- **THEN** the page shows a message saying the title is required
- **AND** no todo is added

### Requirement: Usable on small screens
The page SHALL remain fully usable at a phone-width screen, with no horizontal scrolling. (NFR-6)

#### Scenario: Narrow screen
- **WHEN** the page is viewed at a width of 375 pixels
- **THEN** all controls are reachable and the page does not scroll sideways
