"""POST /agent/message: send a plain-English message to the assistant.

This route never writes to the database. A Task-agent result is only a preview; the user saves it by
pressing Confirm, which calls the normal POST /todos.
"""

import logging
import time
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, status

from app import storage
from app.agents.errors import AgentError, AIUnusableOutput
from app.agents.graph import run_chat
from app.agents.llm import get_llm
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

    It is a function (not the model itself) so a missing key is noticed only after the message has
    been validated: an empty message gets a 422, not a 503.
    """
    return get_llm


def _http_status(error: AgentError) -> int:
    # An answer we could not use is a bad answer from upstream (502); not configured or unreachable
    # means the assistant is unavailable (503).
    if isinstance(error, AIUnusableOutput):
        return status.HTTP_502_BAD_GATEWAY
    return status.HTTP_503_SERVICE_UNAVAILABLE


def _log(trace: dict, outcome: str, started: float) -> None:
    # Only the decision is recorded: never the message text, todo titles or the key.
    logger.info(
        "intent=%s agent=%s outcome=%s duration_ms=%d",
        trace.get("intent", "-"), trace.get("agent", "-"), outcome, (time.perf_counter() - started) * 1000,
    )


@router.post("/agent/message", response_model=ChatResponse)
def send_message(payload: ChatRequest, provider: Callable = Depends(get_llm_provider)):
    trace: dict = {}
    started = time.perf_counter()
    try:
        llm = provider()
        # The agents get a read-only view of the active todos and nothing that can write.
        response = run_chat(
            llm, payload.message, datetime.now(), trace,
            read_todos=lambda: storage.list_todos(status="active"),
        )
    except AgentError as error:
        _log(trace, type(error).__name__, started)
        raise HTTPException(status_code=_http_status(error), detail=error.user_message) from None
    _log(trace, "ok", started)
    return response
