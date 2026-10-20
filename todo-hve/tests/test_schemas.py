import pytest
from pydantic import ValidationError

from app.agents.schemas import ChatRequest, ChatResponse, Intent, PrioritySuggestion, ReminderItem, TodoPreview


@pytest.mark.parametrize("message", ["a", "a" * 500])
def test_given_a_message_of_1_or_500_characters_when_validating_then_it_is_accepted(message):
    # Arrange / Act
    request = ChatRequest(message=message)

    # Assert
    assert request.message == message


@pytest.mark.parametrize("message", ["", "   ", "\n\t ", "a" * 501])
def test_given_an_empty_blank_or_501_character_message_when_validating_then_it_is_rejected_naming_the_field(message):
    # Arrange / Act / Assert
    with pytest.raises(ValidationError) as error:
        ChatRequest(message=message)
    assert "message" in str(error.value)


def test_given_a_padded_message_when_validating_then_it_is_trimmed_before_counting():
    # Arrange / Act
    request = ChatRequest(message="  " + "a" * 500 + "  ")

    # Assert
    assert request.message == "a" * 500


def test_given_the_intent_type_when_listed_then_it_has_exactly_the_four_values():
    # Arrange / Act
    values = {intent.value for intent in Intent}

    # Assert
    assert values == {"create_todo", "suggest_priority", "show_due", "unknown"}


def test_given_a_preview_with_a_201_character_title_when_validating_then_it_is_rejected():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        TodoPreview(title="a" * 201)


def test_given_a_preview_when_validating_then_it_follows_the_same_rules_as_a_new_todo():
    # Arrange / Act
    preview = TodoPreview(title="  Call mom ", due_date="2026-10-23T17:00:00", priority="high")

    # Assert
    assert (preview.title, preview.due_date, preview.priority.value, preview.description) == (
        "Call mom", "2026-10-23T17:00:00", "high", None)


def test_given_a_suggestion_with_a_reason_of_200_characters_when_validating_then_it_is_accepted():
    # Arrange / Act
    suggestion = PrioritySuggestion(priority="low", reason="r" * 200)

    # Assert
    assert len(suggestion.reason) == 200 and suggestion.todo_id is None and suggestion.todo_title is None


def test_given_a_suggestion_with_a_reason_of_201_characters_when_validating_then_it_is_rejected():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        PrioritySuggestion(priority="low", reason="r" * 201)


def test_given_a_response_with_only_intent_and_reply_when_dumped_without_empty_fields_then_only_those_remain():
    # Arrange
    response = ChatResponse(intent="unknown", reply="hello")

    # Act
    body = response.model_dump(mode="json", exclude_none=True)

    # Assert
    assert body == {"intent": "unknown", "reply": "hello"}


def test_given_a_response_with_reminders_when_dumped_then_each_item_has_id_title_due_date_and_overdue():
    # Arrange
    item = ReminderItem(id=1, title="Pay rent", due_date="2026-10-19T10:00:00", overdue=True)
    response = ChatResponse(intent="show_due", reply="1 todo needs attention", reminders=[item])

    # Act
    body = response.model_dump(mode="json", exclude_none=True)

    # Assert
    assert body["reminders"] == [{"id": 1, "title": "Pay rent", "due_date": "2026-10-19T10:00:00", "overdue": True}]
