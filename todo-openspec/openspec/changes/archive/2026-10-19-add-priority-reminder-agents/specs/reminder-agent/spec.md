# Spec Delta

## Purpose

Tells a user which todos are overdue or due soon, with an exact list chosen by the system and a short readable summary, so nothing urgent is missed.

## ADDED Requirements

### Requirement: Find overdue and due-soon todos
The Reminder agent SHALL select active todos whose due date is before the current local time (overdue) or within the next 24 hours (due soon), ordered with overdue first and then soonest due first. Completed todos and todos without a due date SHALL be ignored. The system, not the AI, SHALL make this selection. (FR-14)

#### Scenario: Overdue and due soon together
- **WHEN** one todo is overdue and another is due in 3 hours
- **THEN** both are selected, with the overdue one first

#### Scenario: Outside the window
- **WHEN** a todo is due in 25 hours
- **THEN** it is not selected

#### Scenario: Completed or undated todos
- **WHEN** an overdue todo is completed, and another todo has no due date
- **THEN** neither is selected

#### Scenario: Due date with an explicit time zone
- **WHEN** a todo's due date carries a time zone, such as a trailing Z
- **THEN** it is compared with the current time correctly and does not cause an error

### Requirement: Short readable summary with overdue clearly marked
The reply SHALL be a short readable summary that names each selected todo (up to 10, then "and N more"), states for each whether it is overdue or due soon, and gives its due time. The response SHALL also carry the full list of selected todos with an overdue flag on each, so the marking never depends on wording. The summary SHALL be built by the system. (FR-14)

#### Scenario: Overdue item is clearly marked
- **WHEN** one todo is overdue and another is due in 3 hours
- **THEN** the reply mentions both and clearly marks the first as overdue
- **AND** the list in the response has an overdue flag of true for the first and false for the second

#### Scenario: More than 10 selected
- **WHEN** 14 todos are selected
- **THEN** the reply names 10 and says "and 4 more", and the list in the response contains all 14

#### Scenario: Nothing is due
- **WHEN** no todo is overdue or due within 24 hours
- **THEN** the reply says that nothing is overdue or due in the next 24 hours, and the list is empty
