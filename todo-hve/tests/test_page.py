from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

PAGE = Path(__file__).resolve().parent.parent / "static" / "index.html"

# Calls that would put text into the page as markup.
UNSAFE = ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(")


def unsafe_calls_in(source: str) -> list[str]:
    return [call for call in UNSAFE if call in source]


def test_given_the_running_app_when_opening_the_root_then_the_page_is_served(db_path):
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200 and "<title>Todo App (HVE build)</title>" in response.text


def test_given_the_page_source_when_scanned_then_it_uses_no_call_that_inserts_markup():
    # Arrange
    source = PAGE.read_text()

    # Act
    found = unsafe_calls_in(source)

    # Assert
    assert found == [], f"user or AI text must only be inserted with textContent: {found}"


@pytest.mark.parametrize("snippet", [
    "el.innerHTML = text",
    "el.outerHTML = text",
    "el.insertAdjacentHTML('beforeend', text)",
    "document.write(text)",
    "eval(text)",
])
def test_given_a_snippet_with_an_unsafe_call_when_scanned_then_the_check_flags_it(snippet):
    # Arrange / Act / Assert
    assert unsafe_calls_in(snippet)


def test_given_the_page_source_when_scanned_then_it_has_a_viewport_tag_for_phones():
    # Arrange / Act
    source = PAGE.read_text()

    # Assert
    assert 'name="viewport"' in source


@pytest.mark.parametrize("needle", [
    'id="chat-form"',
    "Please type a message first.",
    '"/agent/message"',
    "Confirm",
    "Cancel",
    "Accept",
    "Ignore",
    "Overdue",
    "Due soon",
    "Thinking",
])
def test_given_the_page_source_when_read_then_the_assistant_card_has_its_parts(needle):
    # Arrange / Act
    source = PAGE.read_text()

    # Assert
    assert needle in source


def test_given_the_page_source_when_read_then_the_assistant_card_comes_before_the_add_form():
    # Arrange / Act
    source = PAGE.read_text()

    # Assert
    assert source.index('id="chat-form"') < source.index('id="add-form"')


# ---- Bold look: pinned ids and labels, chip classes, colour contrast (plan: bold-ui-theme) ----
import re as _re

PINNED_IDS = [
    "add-title", "add-desc", "add-due", "add-priority", "add-error", "add-form", "filter-status", "filter-priority",
    "list-error", "todo-list", "chat-form", "chat-input", "chat-send", "chat-status", "chat-error", "chat-reply",
    "chat-result",
]
PINNED_LABELS = ["Mark done", "Mark not done", "Edit", "Delete", "Save", "Cancel", "Confirm", "Accept", "Ignore",
                 "Send", "Thinking", "Status: ", "Priority: ", "Due: ", "Overdue", "Due soon"]


def _source() -> str:
    return (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text()


@pytest.mark.parametrize("element_id", PINNED_IDS)
def test_given_the_restyled_page_when_read_then_each_pinned_element_id_is_still_there(element_id):
    # Arrange / Act / Assert
    assert f'id="{element_id}"' in _source()


@pytest.mark.parametrize("label", PINNED_LABELS)
def test_given_the_restyled_page_when_read_then_each_pinned_visible_label_is_still_there(label):
    # Arrange / Act / Assert
    assert label in _source()


def test_given_the_bold_look_when_the_script_is_read_then_chip_classes_come_from_a_fixed_list():
    # Arrange
    source = _source()

    # Act
    uses = source.count("chipClass(")

    # Assert: one definition plus list priority, list status, preview priority, suggestion priority, reminder label
    assert "function chipClass(" in source and uses >= 6


def test_given_the_bold_look_when_the_page_is_read_then_cards_are_large_and_rounded_and_buttons_use_the_gradient():
    # Arrange
    source = _source()

    # Act
    card = _re.search(r"\.card\s*\{([^}]*)\}", source).group(1)

    # Assert
    assert _re.search(r"border-radius:\s*(1[4-9]|2\d)px", card)
    assert "linear-gradient(" in source and "var(--accent-a)" in source and "var(--accent-b)" in source


def test_given_the_bold_look_when_the_page_is_read_then_the_card_grid_cannot_exceed_a_phone_screen():
    # Arrange / Act / Assert
    assert "minmax(min(100%" in _source()


def test_given_the_bold_look_when_the_page_is_read_then_it_has_a_dark_variant():
    # Arrange / Act / Assert
    assert "prefers-color-scheme: dark" in _source()


def _bold_colours(source: str) -> dict:
    light = _re.search(r":root\s*\{([^}]*)\}", source).group(1)
    dark = _re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}", source).group(1)

    def variables(block):
        return dict(_re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block))

    return {"light": variables(light), "dark": {**variables(light), **variables(dark)}}


def _lum(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast(a: str, b: str) -> float:
    high, low = sorted((_lum(a), _lum(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


PAIRS = [
    ("text", "bg"), ("text", "card"), ("muted", "bg"), ("muted", "card"),
    ("accent-text", "accent-a"), ("accent-text", "accent-b"),
    ("chip-high-text", "chip-high-bg"), ("chip-medium-text", "chip-medium-bg"), ("chip-low-text", "chip-low-bg"),
]


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("foreground, background", PAIRS)
def test_given_a_colour_scheme_when_text_meets_its_background_then_the_contrast_is_at_least_4_5_to_1(scheme, foreground, background):
    # Arrange
    colours = _bold_colours(_source())[scheme]

    # Act
    ratio = _contrast(colours[foreground], colours[background])

    # Assert
    assert ratio >= 4.5, f"{scheme}: {foreground} on {background} is only {ratio:.2f} to 1"


@pytest.mark.parametrize("a, b, ok", [("#000000", "#ffffff", True), ("#777777", "#ffffff", False), ("#ffffff", "#f7f5ff", False)])
def test_given_the_contrast_helper_when_given_known_colours_then_it_tells_good_from_bad(a, b, ok):
    # Arrange / Act / Assert
    assert (_contrast(a, b) >= 4.5) is ok
