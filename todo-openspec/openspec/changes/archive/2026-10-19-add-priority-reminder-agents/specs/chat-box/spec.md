# Spec Delta

## ADDED Requirements

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
