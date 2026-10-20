# Tasks

## 1. Tests first

- [x] 1.1 Add page tests in `tests/test_page.py` that pin the existing element ids the script uses, the `Overdue` and `Due soon` labels, the viewport tag and the absence of unsafe DOM calls, and a test that the page declares a serif heading stack; run them and confirm the serif test fails before the restyle
- [x] 1.2 Add a contrast test that reads the colour variables from `static/index.html` and checks body text, muted text and primary-button text against their backgrounds are at least 4.5 to 1 in both the light and dark schemes; confirm it runs (and fails if a colour is made too light)

## 2. Restyle the page

- [x] 2.1 Replace the colour variables with the paper palette and a matching dark set, and make the page background warm off-white
- [x] 2.2 Set serif headings (`Georgia, "Times New Roman", serif`), more generous spacing and a single ink-blue accent for primary buttons
- [x] 2.3 Replace boxed cards and todo rows with thin rules; keep a subtle left rule on the Assistant area and the preview and suggestion blocks
- [x] 2.4 Style status and priority as small-caps text tags (words stay in the page; colour is only an extra cue) and keep the `Overdue` and `Due soon` labels as text
- [x] 2.5 Keep every element id, message and request unchanged; add only a short tagline under the title if it helps the look

## 3. Verify

- [x] 3.1 Run the full default test suite and confirm everything passes with no network and no key
- [x] 3.2 In a real browser, on a free port (never 8000 or 8001) after confirming `/openapi.json` shows this app's title, check add, edit, complete, delete, filter and the assistant card at 1000, 768 and 375 px, with no sideways scroll, and take screenshots
- [x] 3.3 Check the dark scheme in the browser (light and dark) and confirm text is readable

## 4. Wrap up

- [x] 4.1 Mention the new look in `README.md` in one line
- [x] 4.2 Run `/opsx:verify restyle-ui-paper-theme`, fix any critical finding, then archive with `/opsx:archive`
