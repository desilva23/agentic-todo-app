import logging
import socket
import time

import pytest
from groq.resources.chat.completions import Completions

from app.agents import llm as llm_module
from app.agents.errors import AINotConfigured, AIUnavailable
from app.agents.llm import Budget, call_model, get_llm
from pydantic import BaseModel

from tests.fakes import ScriptedLLM

FAKE_KEY = "gsk_fake_key_for_tests_only"


class _Word(BaseModel):
    word: str


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_given_no_key_when_building_the_model_then_it_is_not_configured_and_no_network_is_touched(mocker):
    # Arrange
    connect = mocker.patch.object(socket.socket, "connect", side_effect=AssertionError("network used"))

    # Act / Assert
    with pytest.raises(AINotConfigured):
        get_llm()
    connect.assert_not_called()


def test_given_a_key_when_building_the_model_then_name_timeout_retries_and_temperature_come_from_settings(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", FAKE_KEY)
    monkeypatch.setenv("GROQ_MODEL", "some-model")
    monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", "9")

    # Act
    model = get_llm()

    # Assert
    assert (model.model_name, model.request_timeout, model.max_retries) == ("some-model", 9, 0)
    assert model.temperature < 0.001  # the client turns 0 into a tiny value, which Groq accepts


def test_given_a_reply_when_calling_the_model_then_its_text_is_returned():
    # Arrange
    llm = ScriptedLLM("hello")

    # Act / Assert
    assert call_model(llm, [("human", "hi")]) == "hello"


def test_given_list_style_content_when_calling_the_model_then_the_text_parts_are_joined():
    # Arrange
    llm = ScriptedLLM([{"type": "text", "text": "he"}, "llo"])

    # Act / Assert
    assert call_model(llm, [("human", "hi")]) == "hello"


@pytest.mark.parametrize("failure", [ConnectionError("down"), TimeoutError("slow"), RuntimeError("401 rejected"), ValueError("odd")])
def test_given_any_model_failure_when_calling_the_model_then_it_becomes_the_fixed_unavailable_error(failure):
    # Arrange
    llm = ScriptedLLM(failure)

    # Act / Assert
    with pytest.raises(AIUnavailable):
        call_model(llm, [("human", "hi")])


def test_given_an_error_text_carrying_the_key_when_calling_the_model_then_it_never_reaches_the_error_or_the_logs(caplog):
    # Arrange
    llm = ScriptedLLM(RuntimeError(f"401 invalid api key {FAKE_KEY}"))

    # Act
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(AIUnavailable) as error:
            call_model(llm, [("human", "hi")])

    # Assert
    assert FAKE_KEY not in str(error.value) and FAKE_KEY not in caplog.text
    assert error.value.__cause__ is None and error.value.__suppress_context__
    assert "RuntimeError" in caplog.text


def test_given_a_budget_with_time_left_when_calling_the_model_then_the_call_time_is_capped_to_the_time_left(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", "15")
    clock = FakeClock()
    budget = Budget(20, clock=clock)
    clock.now += 17  # 3 seconds are left
    llm = ScriptedLLM("ok")

    # Act
    call_model(llm, [("human", "hi")], budget)

    # Assert
    assert llm.kwargs == [{"timeout": pytest.approx(3.0)}]


def test_given_plenty_of_budget_when_calling_the_model_then_the_configured_timeout_is_used(monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", "15")
    llm = ScriptedLLM("ok")

    # Act
    call_model(llm, [("human", "hi")], Budget(20, clock=FakeClock()))

    # Assert
    assert llm.kwargs == [{"timeout": 15}]


def test_given_a_spent_budget_when_calling_the_model_then_no_call_is_made_and_it_is_unavailable():
    # Arrange
    clock = FakeClock()
    budget = Budget(20, clock=clock)
    clock.now += 20
    llm = ScriptedLLM("never used")

    # Act / Assert
    with pytest.raises(AIUnavailable):
        call_model(llm, [("human", "hi")], budget)
    assert llm.calls == []


def test_given_no_budget_when_calling_the_model_then_no_timeout_is_passed():
    # Arrange
    llm = ScriptedLLM("ok")

    # Act
    call_model(llm, [("human", "hi")])

    # Assert
    assert llm.kwargs == [{}]


def test_given_the_real_groq_client_when_calling_with_a_budget_then_the_capped_timeout_reaches_the_http_call(mocker, monkeypatch):
    # Arrange
    monkeypatch.setenv("GROQ_API_KEY", FAKE_KEY)
    clock = FakeClock()
    budget = Budget(20, clock=clock)
    clock.now += 16  # 4 seconds are left
    create = mocker.patch.object(Completions, "create", side_effect=RuntimeError("stop before any network"))
    model = get_llm()

    # Act
    with pytest.raises(AIUnavailable):
        call_model(model, [("human", "hi")], budget)

    # Assert
    assert create.call_args.kwargs["timeout"] == pytest.approx(4.0)


def test_given_the_default_budget_when_created_then_it_is_20_seconds():
    # Arrange / Act
    budget = Budget(clock=FakeClock())

    # Assert
    assert budget.remaining() == 20 and llm_module.DEFAULT_BUDGET_SECONDS == 20


class HangingLLM:
    """A model call that does not answer until released (it gives up by itself after 5 seconds)."""

    def __init__(self, delay_before_hanging=0.0):
        import threading
        self.release = threading.Event()
        self.calls = 0

    def invoke(self, messages, **kwargs):
        self.calls += 1
        self.release.wait(5)
        raise RuntimeError("late")


def test_given_a_call_that_never_answers_when_calling_with_a_budget_then_control_returns_when_the_budget_ends():
    # Arrange
    llm = HangingLLM()
    budget = Budget(0.3)
    started = time.monotonic()

    # Act
    with pytest.raises(AIUnavailable):
        call_model(llm, [("human", "hi")], budget)
    elapsed = time.monotonic() - started
    llm.release.set()

    # Assert
    assert elapsed < 1.0


def test_given_a_slow_first_call_and_a_hanging_second_when_asking_with_a_budget_then_the_total_wait_stays_in_the_budget():
    # Arrange
    from app.agents.structured import ask

    class SlowThenHang(HangingLLM):
        def invoke(self, messages, **kwargs):
            self.calls += 1
            if self.calls == 1:
                time.sleep(0.2)
                return type("R", (), {"content": "not json"})()
            self.release.wait(5)
            raise RuntimeError("late")

    llm = SlowThenHang()
    started = time.monotonic()

    # Act
    with pytest.raises(AIUnavailable):
        ask(llm, "system", "user", _Word, budget=Budget(0.5))
    elapsed = time.monotonic() - started
    llm.release.set()

    # Assert
    assert llm.calls == 2 and elapsed < 1.2


def test_given_a_quick_call_when_calling_with_a_budget_then_the_reply_is_returned_and_errors_still_become_unavailable():
    # Arrange
    ok = ScriptedLLM("fine")
    bad = ScriptedLLM(ConnectionError("down"))

    # Act / Assert
    assert call_model(ok, [("human", "hi")], Budget(5)) == "fine"
    with pytest.raises(AIUnavailable):
        call_model(bad, [("human", "hi")], Budget(5))
