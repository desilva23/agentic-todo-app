# task-agent Specification

## Purpose
Turns a plain-English sentence into a structured todo preview (title, due date, priority) that the user can check before anything is saved.

## Requirements

### Requirement: Turn a message into a todo preview
The Task agent SHALL produce a preview containing a short title, an optional description, an optional due date and a priority from a create-intent message. The preview SHALL meet the same rules as a todo created by hand (title 1 to 200 characters, priority low, medium or high). It SHALL be returned for the user to confirm and SHALL NOT be saved. (FR-12)

#### Scenario: Message with a time
- **WHEN** the user sends "call mom tomorrow at 5pm"
- **THEN** the preview has the title "Call mom" and a due date of tomorrow at 17:00
- **AND** the preview has a priority
- **AND** nothing is saved

#### Scenario: Message with no date
- **WHEN** the user sends "buy milk"
- **THEN** the preview has the title "Buy milk" and no due date

#### Scenario: Title too long to use as is
- **WHEN** the message describes a task in more than 200 characters
- **THEN** the preview title is shortened to 200 characters or fewer

### Requirement: Resolve dates and priority from the wording
The Task agent SHALL resolve relative dates such as "tomorrow", "next Monday" or "in 2 hours" against the current local date and time, and SHALL choose a priority from urgency words in the message, defaulting to medium when there are none. (FR-12; requirements assumption 6)

#### Scenario: Relative date
- **WHEN** the current local time is Monday 09:00 and the user sends "submit report tomorrow at 3pm"
- **THEN** the preview due date is Tuesday 15:00 of the same week

#### Scenario: Urgent wording
- **WHEN** the user sends "urgent: fix the login bug today"
- **THEN** the preview priority is high

#### Scenario: No urgency words
- **WHEN** the user sends "water the plants"
- **THEN** the preview priority is medium
