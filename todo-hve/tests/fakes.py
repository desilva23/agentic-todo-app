"""A scripted stand-in for the language model, so default tests need no key and no network."""


class _Reply:
    def __init__(self, content):
        self.content = content


class ScriptedLLM:
    """Returns the scripted replies in order. A scripted Exception is raised instead.

    The last item repeats if the script runs out. `calls` records every message list sent and `kwargs`
    the keyword arguments (such as `timeout`) of each call.
    """

    def __init__(self, *script):
        self.script = list(script)
        self.calls = []
        self.kwargs = []

    def invoke(self, messages, **kwargs):
        self.calls.append(messages)
        self.kwargs.append(kwargs)
        item = self.script[min(len(self.calls), len(self.script)) - 1]
        if isinstance(item, Exception):
            raise item
        return _Reply(item)
