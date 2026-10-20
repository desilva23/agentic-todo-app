"""Access to the language model. Agents only use `call_model`, so tests can pass in any object with an
`invoke(messages)` method instead of the real Groq model."""

import logging

from langchain_groq import ChatGroq

from app import config
from app.agents.errors import AgentError, AINotConfigured, AIUnavailable

logger = logging.getLogger("agent")


def get_llm() -> ChatGroq:
    """Build the Groq chat model, or raise AINotConfigured if there is no key."""
    key = config.get_groq_api_key()
    if key is None:
        raise AINotConfigured()
    return ChatGroq(
        model=config.get_groq_model(),
        api_key=key,
        temperature=0,
        timeout=config.get_groq_timeout(),
        max_retries=0,  # the only retry is our own JSON retry, so the wait stays inside the time budget
    )


def _text_of(response) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):  # some models return a list of content parts
        return "".join(part if isinstance(part, str) else part.get("text", "") for part in content)
    return str(content)


def call_model(llm, messages: list) -> str:
    """Send messages to the model and return its reply text.

    Any failure (network, timeout, rejected key, rate limit) becomes AIUnavailable. Only the exception
    TYPE is logged: the error text could contain the key or private text.
    """
    try:
        return _text_of(llm.invoke(messages))
    except AgentError:
        raise
    except Exception as exc:
        logger.warning("model call failed: %s", type(exc).__name__)
        raise AIUnavailable() from None
