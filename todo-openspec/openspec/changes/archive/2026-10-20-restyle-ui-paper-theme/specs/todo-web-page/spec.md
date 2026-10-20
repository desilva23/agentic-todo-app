# Spec Delta

## ADDED Requirements

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
