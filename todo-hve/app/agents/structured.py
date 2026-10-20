"""Ask the model for plain JSON, check it, and wrap untrusted text so it cannot pose as instructions."""

import json
import re
from typing import Optional, TypeVar

from pydantic import BaseModel

from app.agents.errors import AIUnusableOutput
from app.agents.llm import Budget, call_model

T = TypeVar("T", bound=BaseModel)

_FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL | re.IGNORECASE)


def extract_json(text: str):
    """Find the JSON object in a model reply: bare, in a code fence, or inside other words."""
    text = text.strip()
    fenced = _FENCE.match(text)
    if fenced:
        text = fenced.group(1)
    try:
        return json.loads(text)
    except ValueError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object found")
    return json.loads(text[start:end + 1])


def data_block(tag: str, text: str) -> str:
    """Wrap untrusted text in <tag>...</tag>, after removing every copy of the tag from the text (any case,
    with spaces, a slash or attributes), repeating until none is left, so the text cannot close the block
    early or assemble a tag from pieces."""
    pattern = re.compile(rf"<\s*/?\s*{re.escape(tag)}\b[^>]*>", re.IGNORECASE)
    previous = None
    while previous != text:
        previous, text = text, pattern.sub("", text)
    return f"<{tag}>\n{text}\n</{tag}>"


RETRY_NOTE = "That was not valid. Reply again with ONE JSON object only, matching the requested fields, and nothing else."


def ask(llm, system: str, user: str, schema: type[T], budget: Optional[Budget] = None) -> T:
    """Ask for a JSON answer and validate it. If it is not usable, retry ONCE, showing the model its own
    bad answer; a second failure raises AIUnusableOutput."""
    messages = [("system", system), ("human", user)]
    text = call_model(llm, messages, budget)
    try:
        return schema.model_validate(extract_json(text))
    except ValueError:
        pass
    retry = [*messages, ("ai", text), ("human", RETRY_NOTE)]
    text = call_model(llm, retry, budget)
    try:
        return schema.model_validate(extract_json(text))
    except ValueError:
        raise AIUnusableOutput() from None
