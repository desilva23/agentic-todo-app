"""The three errors the assistant may show. Each has a fixed message and accepts no arguments, so
provider text (which could hold a key or private text) cannot be passed in by accident."""


class AgentError(Exception):
    message = "The AI assistant had a problem."

    def __init__(self) -> None:
        super().__init__(self.message)


class AINotConfigured(AgentError):
    message = "The AI assistant is not configured."


class AIUnavailable(AgentError):
    message = "The AI assistant is unavailable right now."


class AIUnusableOutput(AgentError):
    message = "I could not understand the AI's answer. Please try again."
