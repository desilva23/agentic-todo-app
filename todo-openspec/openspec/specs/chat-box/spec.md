# chat-box Specification

## Purpose
Gives the user a chat box on the todo page for typing plain-English requests, reviewing what the agents understood, and confirming or cancelling before anything is saved.

## Requirements

### Requirement: Send a message and see the reply
The web page SHALL have a chat box where the user types a message and sends it, SHALL show a loading indicator while waiting, and SHALL then show the agent's reply. (FR-10, NFR-2)

#### Scenario: Send a message
- **WHEN** the user types "call mom tomorrow at 5pm" and sends it
- **THEN** a loading indicator is shown until the reply arrives
- **AND** the reply is then shown in the chat box

#### Scenario: Help reply
- **WHEN** the user sends "blah blah"
- **THEN** the chat box shows that the message was not understood, with example messages

### Requirement: Confirm or cancel a preview
When the reply contains a todo preview, the page SHALL show its title, due date and priority with a Confirm button and a Cancel button. Confirm SHALL save the todo and refresh the todo list. Cancel SHALL discard the preview and save nothing. (FR-12)

#### Scenario: Confirm
- **WHEN** a preview is shown and the user presses Confirm
- **THEN** the todo is saved and appears in the todo list without a page reload

#### Scenario: Cancel
- **WHEN** a preview is shown and the user presses Cancel
- **THEN** the preview disappears and no todo is saved

### Requirement: Readable errors that do not block the rest of the page
If the chat request fails, the chat box SHALL show a plain-language message that matches the cause (not configured, unavailable, answer not understood, message invalid), and the rest of the page SHALL keep working. (FR-17, NFR-6)

#### Scenario: AI unavailable
- **WHEN** the AI service is not configured or cannot be reached
- **THEN** the chat box shows a plain-language error
- **AND** the user can still add, edit, delete, complete and filter todos

#### Scenario: Empty message
- **WHEN** the user sends an empty message
- **THEN** the chat box shows that a message is required, and nothing is sent to the AI

#### Scenario: Small screen
- **WHEN** the page is viewed at a width of 375 pixels
- **THEN** the chat box and the preview buttons are usable and the page does not scroll sideways

### Requirement: Show a priority suggestion with Accept and Ignore
When the reply contains a priority suggestion, the chat box SHALL show the suggested priority and the reason. If the suggestion is linked to a saved todo, it SHALL also show that todo's title with an Accept button and an Ignore button. Accept SHALL change that todo's priority using the normal edit request and refresh the list. Ignore SHALL discard the suggestion. Nothing SHALL change before Accept is pressed. (FR-13)

#### Scenario: Accept
- **WHEN** a suggestion of high for a saved todo is shown and the user presses Accept
- **THEN** that todo's priority becomes high and the todo list shows it without a page reload

#### Scenario: Ignore
- **WHEN** a suggestion is shown and the user presses Ignore
- **THEN** the suggestion disappears and no todo is changed

#### Scenario: Suggestion with no saved todo
- **WHEN** the suggestion is not linked to a saved todo
- **THEN** the chat box shows the priority and reason as information only, with no Accept button

### Requirement: Show reminders with overdue items marked
When the reply contains a list of reminders, the chat box SHALL show each todo's title and due time, and SHALL mark overdue ones with a visible "Overdue" label that does not rely on color alone. (FR-14)

#### Scenario: Overdue and due soon
- **WHEN** the reply lists one overdue todo and one due in 3 hours
- **THEN** both are shown, and the overdue one carries the label "Overdue"

#### Scenario: Nothing due
- **WHEN** the reply has an empty list
- **THEN** the chat box shows the reply text saying nothing is overdue or due soon, and no list

#### Scenario: Small screen
- **WHEN** the reminder list or a suggestion is shown at a width of 375 pixels
- **THEN** it is fully readable, its buttons are reachable, and the page does not scroll sideways
