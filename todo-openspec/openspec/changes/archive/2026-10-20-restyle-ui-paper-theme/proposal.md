# Proposal

## Why

The three builds of this todo app (OpenSpec, Spec Kit, HVE) currently share the same look, so a reader comparing them cannot tell them apart on screen. Giving each build its own visual identity makes the comparison easier to see and costs nothing in behaviour, because the page is already driven by CSS variables and a small set of stable element ids.

## What Changes

- Restyle the single page (`static/index.html`) in a calm light **"Paper"** look: warm off-white background, serif (Georgia) headings, thin horizontal rules instead of boxed cards, generous spacing, one ink-blue accent, and small-caps text tags for status and priority.
- Keep a matching night variant for people whose system prefers dark mode, as the page already does.
- Add a small automated check that the text and the accent keep enough contrast in both colour schemes.
- Add page tests that pin the things that must not change: the element ids the script uses, the text labels, and the safe way of inserting text.
- Nothing about behaviour, the API, the data or the agents changes.

**Out of scope:** any behaviour or API change, any new feature, a CSS framework or other library, downloading fonts (the serif comes from fonts already on the computer), and changing the other two builds.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `todo-web-page`: gains requirements about the page's visual identity, text-based status labels and readable contrast; existing behaviour requirements are untouched.

## Impact

- `static/index.html` (CSS and a small amount of markup), `tests/test_page.py`.
- Source requirements: FR-8 (a web page that supports the todo features) and NFR-6 (usable on desktop and phone width, plain-language errors) in `docs/requirements.md`.
