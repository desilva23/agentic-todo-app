from fastapi.testclient import TestClient

from app.main import app


def test_root_serves_the_todo_page(db_path):
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>Todo App</title>" in response.text
    assert 'name="viewport"' in response.text  # needed for phone-width screens


# ---- the page's look and what must not change when it is restyled (change: restyle-ui-paper-theme) ----
import re
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parent.parent / "static" / "index.html"

# Every id the page's script (and a person using the page) relies on.
REQUIRED_IDS = [
    "add-error", "add-form", "chat-error", "chat-form", "chat-input", "chat-loading", "chat-preview",
    "chat-reminders", "chat-reply", "chat-send", "chat-suggestion", "filter-priority", "filter-status",
    "list-error", "new-description", "new-due", "new-priority", "new-title", "todo-list",
]
UNSAFE_CALLS = ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(")


def page_source() -> str:
    return PAGE.read_text()


@pytest.mark.parametrize("element_id", REQUIRED_IDS)
def test_given_the_restyled_page_when_read_then_each_required_element_id_is_still_there(element_id):
    assert f'id="{element_id}"' in page_source()


@pytest.mark.parametrize("label", ["Overdue", "Due soon", "Confirm", "Cancel", "Accept", "Ignore", "Thinking"])
def test_given_the_restyled_page_when_read_then_the_text_labels_are_still_there(label):
    assert label in page_source()


@pytest.mark.parametrize("call", UNSAFE_CALLS)
def test_given_the_restyled_page_when_read_then_it_uses_no_markup_inserting_call(call):
    assert call not in page_source()


def test_given_the_paper_look_when_the_page_is_read_then_headings_use_a_serif_stack():
    assert re.search(r"font-family:\s*Georgia", page_source())


def test_given_the_paper_look_when_the_page_is_read_then_status_is_styled_as_a_text_tag():
    source = page_source()
    assert re.search(r"\.status\s*\{", source) and 'className: "status"' in source


# ---- contrast: text must stay readable in both colour schemes ----

def parse_colour_blocks(source: str) -> dict:
    """The colour variables of the light scheme and of the dark scheme."""
    light = re.search(r":root\s*\{([^}]*)\}", source).group(1)
    dark = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}", source).group(1)

    def variables(block):
        return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block))

    return {"light": variables(light), "dark": {**variables(light), **variables(dark)}}


def luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("foreground, background", [
    ("text", "bg"), ("muted", "bg"), ("text", "card"), ("muted", "card"), ("accent-text", "accent"),
])
def test_given_a_colour_scheme_when_text_is_compared_with_its_background_then_the_contrast_is_at_least_4_5_to_1(scheme, foreground, background):
    colours = parse_colour_blocks(page_source())[scheme]
    ratio = contrast(colours[foreground], colours[background])
    assert ratio >= 4.5, f"{scheme}: {foreground} on {background} is only {ratio:.2f} to 1"


@pytest.mark.parametrize("a, b, ok", [("#000000", "#ffffff", True), ("#777777", "#ffffff", False), ("#cccccc", "#ffffff", False)])
def test_given_the_contrast_helper_when_given_known_colours_then_it_tells_good_from_bad(a, b, ok):
    assert (contrast(a, b) >= 4.5) is ok
