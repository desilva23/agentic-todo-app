"""Access to the language model. Agents only use `call_model`, so tests can pass in any object with an
`invoke(messages, **kwargs)` method instead of the real Groq model."""

import logging
import threading
import time
from typing import Callable, Optional

from app.agents.errors import AgentError, AINotConfigured, AIUnavailable
from app.config import get_groq_api_key, get_groq_model, get_groq_timeout

logger = logging.getLogger("agent")

DEFAULT_BUDGET_SECONDS = 20


class Budget:
    """The time one message may use. No model call starts after it is spent, and each call is limited
    to the time left."""

    def __init__(self, seconds: float = DEFAULT_BUDGET_SECONDS, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._deadline = clock() + seconds

    def remaining(self) -> float:
        return self._deadline - self._clock()


def get_llm():
    """Build the Groq chat model from settings. No network call is made here."""
    key = get_groq_api_key()
    if not key:
        raise AINotConfigured()
    from langchain_groq import ChatGroq  # imported here so the core app never needs it

    return ChatGroq(
        model=get_groq_model(),
        api_key=key,
        temperature=0,
        max_retries=0,  # the only retry is our own JSON retry, so the wait stays inside the time budget
        timeout=get_groq_timeout(),
    )


def _text_of(reply) -> str:
    content = getattr(reply, "content", reply)
    if isinstance(content, list):
        return "".join(part if isinstance(part, str) else part.get("text", "") for part in content)
    return str(content)


def _invoke_within(llm, messages: list, kwargs: dict, seconds: float):
    """Run one model call, but give control back when `seconds` have passed, even if the call has not
    answered. The HTTP client limits each phase of a request separately, so its own timeout alone cannot
    promise a total. A call that is given up on is abandoned: it ends by itself at the client's timeout."""
    outcome: dict = {}

    def work() -> None:
        try:
            outcome["reply"] = llm.invoke(messages, **kwargs)
        except BaseException as exc:  # handed back to the caller below
            outcome["error"] = exc

    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    thread.join(seconds)
    if thread.is_alive():
        raise TimeoutError("the time budget for this message ended")
    if "error" in outcome:
        raise outcome["error"]
    return outcome["reply"]


def call_model(llm, messages: list, budget: Optional[Budget] = None) -> str:
    """Send messages to the model and return its reply text.

    Any failure (network, timeout, rejected key, rate limit) becomes AIUnavailable. Only the exception
    TYPE is logged: the error text could contain the key or private text. With a budget, no call is
    made once it is spent, each call is limited to the time left, and control returns when the budget
    ends even if the model has not answered.
    """
    kwargs = {}
    if budget is not None:
        left = budget.remaining()
        if left <= 0:
            logger.warning("model call skipped: the time budget for this message is spent")
            raise AIUnavailable()
        kwargs["timeout"] = min(get_groq_timeout(), left)
    try:
        if budget is None:
            reply = llm.invoke(messages, **kwargs)
        else:
            reply = _invoke_within(llm, messages, kwargs, left)
        return _text_of(reply)
    except AgentError:
        raise
    except Exception as exc:
        logger.warning("model call failed: %s", type(exc).__name__)
        raise AIUnavailable() from None
