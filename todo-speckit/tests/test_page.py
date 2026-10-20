from fastapi.testclient import TestClient

from app.main import app


def test_root_serves_the_todo_page(db_path):
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>Todo App</title>" in response.text
    assert 'name="viewport"' in response.text  # needed for phone-width screens


# ---- feature 003 (console look): what must not change, and contrast ----
import re
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parent.parent / "static" / "index.html"

# Every id the page's script relies on (specs/003-ui-console-theme/contracts/page-contract.md).
REQUIRED_IDS = [
    "add-error", "add-form", "chat-error", "chat-form", "chat-input", "chat-loading", "chat-preview",
    "chat-reminders", "chat-reply", "chat-send", "chat-suggestion", "filter-priority", "filter-status",
    "list-error", "new-description", "new-due", "new-priority", "new-title", "todo-list",
]
UNSAFE_CALLS = ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(")


def page_source() -> str:
    return PAGE.read_text()


@pytest.mark.parametrize("element_id", REQUIRED_IDS)
def test_given_the_page_when_read_then_each_required_element_id_is_there(element_id):
    assert f'id="{element_id}"' in page_source()


@pytest.mark.parametrize("label", ["Confirm", "Cancel", "Accept", "Ignore", "Edit", "Delete", "Save", "Send", "Thinking"])
def test_given_the_page_when_read_then_the_visible_labels_are_still_there(label):
    assert label in page_source()


@pytest.mark.parametrize("call", UNSAFE_CALLS)
def test_given_the_page_when_read_then_it_uses_no_markup_inserting_call(call):
    assert call not in page_source()


# contrast: text must stay readable (at least 4.5 to 1)

def colour_variables(source: str) -> dict:
    block = re.search(r":root\s*\{([^}]*)\}", source).group(1)
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block))


def luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


@pytest.mark.parametrize("foreground, background", [
    ("text", "bg"), ("muted", "bg"), ("text", "card"), ("muted", "card"), ("accent-text", "accent"),
])
def test_given_the_page_colours_when_text_is_compared_with_its_background_then_the_contrast_is_at_least_4_5_to_1(foreground, background):
    colours = colour_variables(page_source())
    ratio = contrast(colours[foreground], colours[background])
    assert ratio >= 4.5, f"{foreground} on {background} is only {ratio:.2f} to 1"


@pytest.mark.parametrize("a, b, ok", [("#000000", "#ffffff", True), ("#777777", "#ffffff", False), ("#3a4a3a", "#0b0e0b", False)])
def test_given_the_contrast_helper_when_given_known_colours_then_it_tells_good_from_bad(a, b, ok):
    assert (contrast(a, b) >= 4.5) is ok


# ---- user story 1: the console look ----

def css_block(source: str, selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", source)
    assert match, f"no rule for {selector}"
    return match.group(1)


def test_given_the_console_look_when_the_page_is_read_then_it_uses_a_monospace_font_stack():
    assert re.search(r"font-family:\s*ui-monospace[^;]*monospace", page_source())


def test_given_the_console_look_when_the_page_is_read_then_it_declares_a_dark_colour_scheme():
    assert "color-scheme: dark" in page_source()


def test_given_the_console_look_when_the_page_is_read_then_there_is_no_light_variant():
    source = page_source()
    assert "prefers-color-scheme" not in source


@pytest.mark.parametrize("selector", [".card", "li.todo"])
def test_given_the_console_look_when_panels_are_read_then_they_have_square_corners(selector):
    assert "border-radius: 0" in css_block(page_source(), selector)


@pytest.mark.parametrize("heading", ["&gt; assistant", "&gt; new todo", "&gt; filter"])
def test_given_the_console_look_when_the_page_is_read_then_the_sections_have_prompt_headings(heading):
    assert heading in page_source()


# ---- user story 2: status and priority are bracketed words ----

def test_given_the_console_look_when_the_script_is_read_then_a_chip_helper_wraps_words_in_brackets():
    assert re.search(r'function chip\(word\)\s*\{\s*return "\[" \+ word \+ "\]";', page_source())


@pytest.mark.parametrize("use", [
    "chip(todo.priority)", "chip(todo.status)", "chip(suggestion.priority)", "chip(preview.priority)",
    'chip(item.overdue ? "overdue" : "due soon")',
])
def test_given_the_console_look_when_the_script_is_read_then_each_label_is_built_as_a_bracketed_word(use):
    assert use in page_source()


def test_given_the_console_look_when_the_script_is_read_then_the_status_has_its_own_chip_class():
    assert 'className: "status"' in page_source()
