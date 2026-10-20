"""POST /agent/message: send a plain-English message to the assistant.

This route never changes a todo. A Task-agent result is only a preview; the user saves it by pressing
Confirm, which calls the normal POST /todos. A priority suggestion is applied only by Accept, which
calls the normal PATCH /todos/{id}.
"""

import logging
import time
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, status

from app import storage
from app.agents.errors import AgentError, AINotConfigured, AIUnavailable, AIUnusableOutput
from app.agents.graph import run_chat
from app.agents.llm import Budget, get_llm
from app.agents.schemas import ChatRequest, ChatResponse

logger = logging.getLogger("agent")
if not logger.handlers:  # make the decision log visible when running under uvicorn
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s agent: %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

router = APIRouter()


def get_llm_provider() -> Callable[[], object]:
    """Returns a function that builds the model. Tests replace this with a fake.

    It is a function (not the model itself) so a missing key is noticed only after the message has been
    validated: an empty message gets a 422, not a 503.
    """
    return get_llm


def get_now() -> datetime:
    """The current local date and time. Tests replace this with a fixed clock."""
    return datetime.now()


def get_budget() -> Budget:
    """The time this message may use (20 seconds), starting when the request arrives."""
    return Budget()


_OUTCOMES = {AINotConfigured: "not_configured", AIUnavailable: "unavailable", AIUnusableOutput: "unusable_output"}


def _http_status(error: AgentError) -> int:
    # An answer we could not use is a bad answer from upstream (502); not configured or unreachable
    # means the assistant is unavailable (503).
    return status.HTTP_502_BAD_GATEWAY if isinstance(error, AIUnusableOutput) else status.HTTP_503_SERVICE_UNAVAILABLE


def _log(trace: dict, outcome: str, started: float) -> None:
    # Only the decision is recorded: never the message text, todo titles or the key.
    logger.info(
        "intent=%s agent=%s outcome=%s duration_ms=%d",
        trace.get("intent", "-"), trace.get("agent", "-"), outcome, (time.perf_counter() - started) * 1000,
    )


@router.post("/agent/message", response_model=ChatResponse, response_model_exclude_unset=True)
def send_message(
    payload: ChatRequest,
    provider: Callable = Depends(get_llm_provider),
    now: datetime = Depends(get_now),
    budget: Budget = Depends(get_budget),
):
    trace: dict = {}
    started = time.perf_counter()
    try:
        llm = provider()
        response = run_chat(
            llm, payload.message, lambda: storage.list_todos(status="active"), now, trace=trace, budget=budget,
        )
    except AgentError as error:
        _log(trace, _OUTCOMES.get(type(error), "failure"), started)
        raise HTTPException(status_code=_http_status(error), detail=error.message) from None
    except Exception as exc:  # a bug or a storage problem inside the assistant must not crash the app
        logger.warning("assistant failed: %s", type(exc).__name__)
        _log(trace, "unavailable", started)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=AIUnavailable.message) from None
    _log(trace, "success", started)
    return response
