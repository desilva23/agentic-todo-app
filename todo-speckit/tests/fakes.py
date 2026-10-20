"""A fake language model for tests: no network, no key."""


class _Reply:
    def __init__(self, content):
        self.content = content


class ScriptedLLM:
    """Returns the scripted replies in order. A scripted Exception is raised instead.

    The last item repeats if the script runs out. `calls` records every message list sent.
    """

    def __init__(self, *script):
        self.script = list(script)
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        item = self.script[min(len(self.calls), len(self.script)) - 1]
        if isinstance(item, Exception):
            raise item
        return _Reply(item)
