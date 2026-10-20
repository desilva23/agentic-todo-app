# Research: Console Look

No unknowns remained ("NEEDS CLARIFICATION" count: 0). Each decision has its reasons.

## R-1. Always dark, one palette

- **Decision**: One dark palette defined as colour variables: near-black background, light text, a muted grey-green for secondary text, thin dim-green lines, one green accent for primary buttons, a soft red for danger and overdue.
- **Rationale**: The spec says always dark (FR-005); one palette means one set of contrast numbers to check. Colours are already variables in the page, so the change stays small.
- **Alternatives considered**: a light/dark pair (extra work, rejected by the spec); hard-coded colours per rule (hard to keep contrast right).

## R-2. System monospace font

- **Decision**: font stack `ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace`.
- **Rationale**: Instant, no download, no network, works offline (a constitution requirement for tests and the plain-page rule).
- **Alternatives considered**: a web font (needs a download; out of scope).

## R-3. Square panels with thin borders

- **Decision**: panels keep a 1 px border but lose rounded corners; headings are prompt lines (`> assistant`, `> new todo`, `> filter`) added as small headings.
- **Rationale**: It is the biggest visible difference from the other builds and costs nothing in behaviour.
- **Alternatives considered**: no borders at all (that is another build's "paper" look).

## R-4. Bracketed text chips

- **Decision**: priority, status and the reminder labels are written as text with brackets by the script (for example `[high]`), so the words, not the colour, carry the meaning.
- **Rationale**: Spec FR-004 and the project rule that status is never shown by colour alone.
- **Alternatives considered**: drawing brackets with CSS only (they would not be in the text a screen reader or a test reads).

## R-5. Contrast checked by a test

- **Decision**: a test reads the colour variables from the page and checks 4.5 to 1 for body text, muted text and button text.
- **Rationale**: A restyle is where contrast quietly regresses (SC-004); a test makes it permanent. A self-test of the helper proves it can tell good from bad colours.
- **Alternatives considered**: checking by eye (does not last).

## R-6. Proving behaviour is unchanged

- **Decision**: page tests pin every element id and label; a real-browser pass at 1000, 768 and 375 px runs every old behaviour check against a stub model on a free port after confirming the app title.
- **Rationale**: SC-002 and SC-003 need a real browser; the stub model keeps it offline.
- **Alternatives considered**: tests only (cannot see layout or clicks).
