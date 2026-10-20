import logging
import socket

import pytest
from pydantic import BaseModel, ValidationError

from app.agents.errors import AINotConfigured, AIUnavailable, AIUnusableOutput
from app.agents.llm import call_model, get_llm
from app.agents.schemas import ChatRequest, ChatResponse, TodoPreview
from app.agents.structured import ask, extract_json
from tests.fakes import ScriptedLLM


# --- schemas (task 2.1) -------------------------------------------------------

@pytest.mark.parametrize("bad", ["", "   ", "x" * 501])
def test_chat_request_rejects_empty_blank_and_too_long(bad):
    with pytest.raises(ValidationError) as err:
        ChatRequest(message=bad)
    assert "message" in str(err.value)


def test_chat_request_accepts_1_and_500_characters_and_trims():
    assert ChatRequest(message="x").message == "x"
    assert len(ChatRequest(message="x" * 500).message) == 500
    assert ChatRequest(message="  hi  ").message == "hi"


def test_preview_follows_the_same_rules_as_a_hand_made_todo():
    assert TodoPreview(title="Call mom").priority == "medium"
    with pytest.raises(ValidationError):
        TodoPreview(title="x" * 201)
    with pytest.raises(ValidationError):
        TodoPreview(title="A", priority="urgent")


def test_chat_response_intents():
    assert ChatResponse(intent="unknown", reply="hi").preview is None
    with pytest.raises(ValidationError):
        ChatResponse(intent="delete_everything", reply="x")


# --- model access (task 2.2) --------------------------------------------------

def test_missing_key_raises_not_configured_without_any_network_call(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("network used")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(AINotConfigured):
        get_llm()


def test_with_a_key_the_model_is_built_from_settings(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    monkeypatch.setenv("GROQ_MODEL", "some-model")
    monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", "9")
    model = get_llm()
    assert model.model_name == "some-model"
    assert model.request_timeout == 9


def test_any_model_failure_becomes_unavailable():
    with pytest.raises(AIUnavailable):
        call_model(ScriptedLLM(ConnectionError("boom")), [("human", "hi")])


def test_model_errors_do_not_leak_the_key_into_logs_or_messages(caplog):
    secret = "gsk_THIS_MUST_NEVER_APPEAR"
    failing = ScriptedLLM(RuntimeError(f"401 invalid api key {secret}"))
    with caplog.at_level(logging.DEBUG, logger="agent"):
        with pytest.raises(AIUnavailable) as err:
            call_model(failing, [("human", "hi")])
    assert secret not in caplog.text
    assert secret not in str(err.value) and secret not in err.value.user_message
    assert err.value.__cause__ is None  # the original error text is not carried along


def test_list_style_model_content_is_joined():
    llm = ScriptedLLM([{"type": "text", "text": "ab"}, "cd"])
    assert call_model(llm, []) == "abcd"


# --- JSON helper (task 2.3) ---------------------------------------------------

class Thing(BaseModel):
    name: str
    count: int


def test_extract_json_plain_fenced_and_surrounded():
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Sure! Here it is: {"a": 1} Hope that helps') == {"a": 1}


def test_extract_json_rejects_text_without_json():
    with pytest.raises(ValueError):
        extract_json("no json here")


def test_ask_returns_validated_object():
    llm = ScriptedLLM('{"name": "x", "count": 2}')
    assert ask(llm, "sys", "usr", Thing) == Thing(name="x", count=2)
    assert len(llm.calls) == 1


def test_ask_accepts_fenced_json():
    llm = ScriptedLLM('```json\n{"name": "x", "count": 2}\n```')
    assert ask(llm, "s", "u", Thing).count == 2


def test_ask_retries_once_then_succeeds():
    llm = ScriptedLLM("not json at all", '{"name": "x", "count": 3}')
    result = ask(llm, "s", "u", Thing)
    assert result.count == 3
    assert len(llm.calls) == 2
    # the retry shows the model its bad answer and asks for JSON only
    assert llm.calls[1][-1][0] == "human" and "ONLY one JSON" in llm.calls[1][-1][1]


def test_ask_retries_when_json_is_valid_but_wrong_shape():
    llm = ScriptedLLM('{"name": "x"}', '{"name": "x", "count": 1}')
    assert ask(llm, "s", "u", Thing).count == 1


def test_ask_fails_after_two_bad_answers():
    llm = ScriptedLLM("nope", "still nope")
    with pytest.raises(AIUnusableOutput):
        ask(llm, "s", "u", Thing)
    assert len(llm.calls) == 2  # exactly one retry, never more


def test_ask_does_not_retry_when_the_model_is_unavailable():
    llm = ScriptedLLM(ConnectionError("down"))
    with pytest.raises(AIUnavailable):
        ask(llm, "s", "u", Thing)
    assert len(llm.calls) == 1
