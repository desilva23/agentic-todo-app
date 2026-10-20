# Design

## Context

The page is one file with inline CSS and JavaScript. Colours already come from CSS variables, with a dark scheme under `prefers-color-scheme`, and the script finds its elements by id. Most of the look can therefore change in the `<style>` block alone. See `proposal.md` for the motivation.

## Goals / Non-Goals

**Goals:**
- A recognisably different look ("Paper") with no change in behaviour.
- Keep every element id, text label, request and safe-DOM rule the script relies on.
- Keep the dark scheme and the 375 px layout working.

**Non-Goals:**
- New features, new libraries, a CSS framework, downloaded fonts, or changes to the API or the other builds.

## Decisions

### 1. Change the CSS variables first, then the shapes
Replace the colour variables with a paper palette (off-white background `#faf6ee`, ink `#26231f`, muted ink `#5f5a52`, rule `#d9d1c0`, accent ink-blue `#1f3f7a`) and a matching dark set (near-black warm background, soft off-white ink, lighter blue accent). **Why:** one place to change; the dark scheme keeps working.
*Alternative:* hard-code colours per element. Rejected: harder to keep both schemes in step.

### 2. Serif headings from fonts already installed
Headings use `Georgia, "Times New Roman", serif`; body text keeps the system sans-serif. **Why:** no download, no network, instant. *Alternative:* a web font. Rejected: out of scope and needs the network.

### 3. Rules instead of boxes
Sections and todo rows lose their rounded borders and get a thin bottom rule and more spacing; the Assistant keeps a subtle left rule so it still reads as a distinct area. **Why:** this is the biggest visible difference from the other builds and is pure CSS.

### 4. Text tags for status and priority
Priority and status render as small-caps text tags (for example `HIGH`, `OVERDUE`) with a thin outline; colour is only an extra cue. **Why:** NFR-6 and the page rules say status must not rely on colour alone. The words are already in the page; only their styling changes.

### 5. A contrast test
A test reads the colour variables from the page source and checks the 4.5 to 1 ratio for text on background in both schemes. **Why:** a restyle is where contrast quietly regresses.

### 6. Pin what must not change
Page tests assert the ids the script uses, the labels `Overdue` and `Due soon`, no use of the unsafe DOM calls, and the viewport tag. A real-browser pass at 1000, 768 and 375 px checks behaviour on a free port after confirming the app title.

## Risks / Trade-offs

- **Serif font availability** → the stack falls back to the system serif; look differs slightly per computer. Accepted.
- **Contrast of the muted text on warm paper** → covered by the contrast test.
- **A restyle breaks a control on a small screen** → the real-browser pass at 375 px.
