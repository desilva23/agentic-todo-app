import pytest

from app.agents.errors import AgentError, AINotConfigured, AIUnavailable, AIUnusableOutput


@pytest.mark.parametrize("error_type, text", [
    (AINotConfigured, "The AI assistant is not configured."),
    (AIUnavailable, "The AI assistant is unavailable right now."),
    (AIUnusableOutput, "I could not understand the AI's answer. Please try again."),
])
def test_given_each_error_when_converted_to_text_then_the_fixed_message_is_shown(error_type, text):
    # Arrange / Act
    error = error_type()

    # Assert
    assert str(error) == text and error.message == text


@pytest.mark.parametrize("error_type", [AINotConfigured, AIUnavailable, AIUnusableOutput])
def test_given_each_error_when_checked_then_it_is_an_agent_error(error_type):
    # Arrange / Act / Assert
    assert isinstance(error_type(), AgentError)


@pytest.mark.parametrize("error_type", [AINotConfigured, AIUnavailable, AIUnusableOutput])
def test_given_provider_text_when_building_an_error_then_it_is_refused(error_type):
    # Arrange / Act / Assert
    with pytest.raises(TypeError):
        error_type("401 invalid api key gsk_secret")
