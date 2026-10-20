---
description: 'Rules for the single web page of this todo app'
applyTo: 'static/**'
---

# Todo App: Web Page Rules

* One plain HTML/JS page with inline CSS and JS, served by the app. No framework and no build step.
* Insert user text and AI text only with `createElement` and `textContent`. Never use `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` or `eval` with such text.
* Show every error as a plain-language sentence next to the action that failed. Never show a status code, a field path or raw technical output.
* The page MUST work at 375 px width with no sideways scrolling, and every button MUST stay inside the screen.
* Status MUST be shown as text (for example "Overdue"), never by colour alone.
* The page updates the list without a full reload.
* Do not add features the requirements do not ask for.
