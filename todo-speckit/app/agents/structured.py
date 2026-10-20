"""Ask the model for JSON and validate it with Pydantic.

We do not rely on any model-specific "structured output" feature: the model replies with plain text,
we parse it, and we check it against a Pydantic model. Exactly one retry is allowed.
"""

import json
import re
from typing import TypeVar

from pydantic import BaseModel

from app.agents.errors import AIUnusableOutput
from app.agents.llm import call_model

T = TypeVar("T", bound=BaseModel)

CORRECTION = (
    "That was not valid. Reply again with ONLY one JSON object that matches the format, "
    "with no other text."
)
_FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL | re.IGNORECASE)


def extract_json(text: str):
    """Parse the first JSON object in the text, accepting a ```json code fence around it."""
    text = text.strip()
    fenced = _FENCE.match(text)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("no JSON object found")
    return json.loads(text[start : end + 1])


def data_block(tag: str, text: str) -> str:
    """Wrap text in <tag>...</tag> so a prompt can say "this is data, not instructions".

    Any copy of that tag inside the text is removed first (any case, optional spaces and slash), so
    neither a user message nor a saved todo title can close the block early and make the rest look
    like instructions.
    """
    pattern = re.compile(rf"<\s*/?\s*{re.escape(tag)}\s*>", re.IGNORECASE)
    return f"<{tag}>{pattern.sub('', text)}</{tag}>"


def ask(llm, system: str, user: str, schema: type[T]) -> T:
    """Return the model's answer as a validated `schema` object, or raise AIUnusableOutput."""
    messages = [("system", system), ("human", user)]
    for attempt in range(2):
        reply = call_model(llm, messages)
        try:
            return schema.model_validate(extract_json(reply))
        except ValueError:  # JSON errors and Pydantic validation errors are both ValueErrors
            if attempt == 1:
                raise AIUnusableOutput() from None
            messages = messages + [("ai", reply), ("human", CORRECTION)]
    raise AIUnusableOutput()  # pragma: no cover (the loop always returns or raises)
