"""The assistant must never be able to change a todo (constitution I). These checks read the source code
of the agent modules and the chat route, so they fail the moment someone gives the assistant a way to write."""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent / "app"
AGENT_FILES = sorted((ROOT / "agents").glob("*.py"))
ROUTE_FILE = ROOT / "chat.py"

# Anything that names a todo-changing function or opens the database directly.
FORBIDDEN_NAMES = {"create_todo", "update_todo", "delete_todo", "init_db", "sqlite3"}


def forbidden_names_in(source: str) -> set:
    """Names in the source that would give the assistant the power to change or directly open todos."""
    found = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom):
            found |= {alias.name for alias in node.names} & FORBIDDEN_NAMES
            if node.module and node.module.split(".")[0] in FORBIDDEN_NAMES:
                found.add(node.module)
        elif isinstance(node, ast.Import):
            found |= {a.name for a in node.names if a.name.split(".")[0] in FORBIDDEN_NAMES}
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
            found.add(node.attr)
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            found.add(node.id)
    return found


def storage_imports_in(source: str) -> list:
    """Imports of the storage module (agents must only ever receive a read-only function)."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "app.storage" or module.startswith("app.storage."):
                found.append(module)
            if module == "app" and any(alias.name == "storage" for alias in node.names):
                found.append("app.storage")
        elif isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name == "app.storage"]
    return found


def test_there_are_agent_modules_to_check():
    assert len(AGENT_FILES) >= 9 and ROUTE_FILE.exists()  # a guard against checking an empty folder


def test_no_agent_module_and_not_the_chat_route_can_change_todos_or_open_the_database():
    offenders = {f.name: forbidden_names_in(f.read_text()) for f in AGENT_FILES + [ROUTE_FILE]}
    offenders = {name: found for name, found in offenders.items() if found}
    assert offenders == {}, f"the assistant must not be able to write: {offenders}"


def test_no_module_under_app_agents_imports_the_storage_module_at_all():
    offenders = {f.name: storage_imports_in(f.read_text()) for f in AGENT_FILES}
    offenders = {name: found for name, found in offenders.items() if found}
    assert offenders == {}, f"agents may only read todos through the function they are given: {offenders}"


@pytest.mark.parametrize("snippet", [
    "from app.storage import create_todo",
    "from app import storage\nstorage.delete_todo(1)",
    "import sqlite3",
    "from app.storage import update_todo as u",
    "storage.init_db()",
])
def test_the_write_check_really_catches_violations(snippet):
    assert forbidden_names_in(snippet)


@pytest.mark.parametrize("snippet", [
    "from app.storage import list_todos",
    "from app import storage",
    "import app.storage",
    "from app.storage import list_todos as read",
])
def test_the_storage_import_check_really_catches_violations(snippet):
    assert storage_imports_in(snippet)


@pytest.mark.parametrize("snippet", [
    "x = {'create_todo': 'task_agent'}",   # an intent name in a string is fine
    "from app.models import Priority",
])
def test_the_checks_do_not_flag_harmless_code(snippet):
    assert not forbidden_names_in(snippet) and not storage_imports_in(snippet)
