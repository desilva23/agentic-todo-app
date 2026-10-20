# Spec Delta

## Purpose

Gives the user a chat box on the todo page for typing plain-English requests, reviewing what the agents understood, and confirming or cancelling before anything is saved.

## ADDED Requirements

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
