"""Errors the agent feature can raise. Messages are fixed, safe to show to users,
and never contain the API key or raw error text from Groq."""


class AgentError(Exception):
    user_message = "Something went wrong with the AI assistant."


class AINotConfigured(AgentError):
    user_message = "The AI assistant is not configured."


class AIUnavailable(AgentError):
    user_message = "The AI assistant is unavailable right now."


class AIUnusableOutput(AgentError):
    user_message = "I could not understand the AI's answer. Please try again."
