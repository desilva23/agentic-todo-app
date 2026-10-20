# todo-web-page Specification

## Purpose
Gives a user a single web page for managing todos in a browser, on both desktop and phone-width screens, without needing to call the API by hand.

## Requirements

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

### Requirement: The page has its own "Paper" visual identity
The page SHALL present a calm light "Paper" look: a warm off-white page background, serif headings, thin horizontal rules (not boxed cards) between sections, and a single ink-blue accent colour used for primary actions. (FR-8, NFR-6)

#### Scenario: Open the page in a light colour scheme
- **WHEN** a user opens the page on a computer that prefers a light colour scheme
- **THEN** the page background is a warm off-white and the headings use a serif typeface
- **AND** sections are separated by thin rules rather than bordered boxes
- **AND** primary buttons use one accent colour

#### Scenario: Open the page in a dark colour scheme
- **WHEN** a user opens the page on a computer that prefers a dark colour scheme
- **THEN** the page uses a dark paper-and-ink variant of the same look and stays readable

### Requirement: Status and priority are shown as words
The page SHALL show each todo's status and priority, and the Overdue and Due soon labels of the assistant, as text (styled as small tags), never by colour alone. (NFR-6)

#### Scenario: A todo is listed
- **WHEN** the list shows a todo
- **THEN** its priority is written as a word (Low, Medium or High) and its status is written as a word
- **AND** an overdue todo or reminder carries the word "Overdue"

### Requirement: Text stays readable against the background
The page's body text, muted text and primary-button text SHALL have a contrast ratio of at least 4.5 to 1 against their backgrounds in both colour schemes. (NFR-6)

#### Scenario: Check contrast
- **WHEN** the colours defined for the light and dark schemes are compared
- **THEN** body text, muted text and button text each meet a 4.5 to 1 contrast ratio against their background

### Requirement: A visual change does not change behaviour
Restyling the page SHALL NOT change what the page does: every control, element identifier, message and request that existed before the restyle SHALL still work as before, and the page SHALL still work at 375 pixels width with no sideways scrolling. (FR-8, NFR-6)

#### Scenario: Use the page after the restyle
- **WHEN** a user adds, completes, deletes and filters todos and sends a message to the assistant
- **THEN** each action works exactly as it did before the restyle

#### Scenario: Narrow screen after the restyle
- **WHEN** the page is viewed at a width of 375 pixels
- **THEN** every control is on screen and the page does not scroll sideways
