"""The assistant must never be able to change a todo. These checks read the source code of the agent
modules and the chat route, so they fail the moment someone gives the assistant a way to write."""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parent.parent / "app"
AGENT_FILES = sorted((APP / "agents").glob("*.py"))
ROUTE_FILE = APP / "chat.py"

# Names that change a todo or open the database directly.
FORBIDDEN_NAMES = {"create_todo", "update_todo", "delete_todo", "init_db", "sqlite3"}
# The only storage function the chat route may use.
ALLOWED_STORAGE_USE = {"list_todos"}


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
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES and not _is_intent_value(node):
            found.add(node.attr)
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES and isinstance(node.ctx, ast.Load):
            found.add(node.id)
    return found


def _is_intent_value(node: ast.Attribute) -> bool:
    """`Intent.create_todo` is the name of an intent (an enum value), not a call that creates a todo."""
    return isinstance(node.value, ast.Name) and node.value.id == "Intent"


def storage_imports_in(source: str) -> list:
    """Imports of the storage module (agents may only ever receive a read-only function)."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "app.storage" or module.startswith("app.storage."):
                found.append(module)
            if module == "app" and any(alias.name == "storage" for alias in node.names):
                found.append("app.storage")
        elif isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name == "app.storage" or a.name.startswith("app.storage.")]
    return found


def storage_aliases_in(source: str) -> list:
    """Imports that rename the storage module, which would hide what the route calls on it."""
    return [
        alias.asname for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ImportFrom) and node.module == "app"
        for alias in node.names if alias.name == "storage" and alias.asname
    ]


def storage_functions_used_in(source: str) -> set:
    """Every `storage.<name>` the source uses."""
    return {
        node.attr for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "storage"
    }


def test_given_the_assistant_folder_when_listed_then_there_are_modules_to_check():
    # Arrange / Act
    names = {f.name for f in AGENT_FILES}

    # Assert (a guard against checking an empty folder)
    assert {"graph.py", "llm.py", "structured.py", "orchestrator.py", "task_agent.py", "priority_agent.py", "due.py"} <= names
    assert ROUTE_FILE.exists()


def test_given_the_agent_modules_and_chat_route_when_scanned_then_none_can_change_todos_or_open_the_database():
    # Arrange / Act
    offenders = {f.name: forbidden_names_in(f.read_text()) for f in AGENT_FILES + [ROUTE_FILE]}
    offenders = {name: found for name, found in offenders.items() if found}

    # Assert
    assert offenders == {}, f"the assistant must not be able to write: {offenders}"


def test_given_the_agent_modules_when_scanned_then_none_imports_the_storage_module_at_all():
    # Arrange / Act
    offenders = {f.name: storage_imports_in(f.read_text()) for f in AGENT_FILES}
    offenders = {name: found for name, found in offenders.items() if found}

    # Assert
    assert offenders == {}, f"agents may only read todos through the function they are given: {offenders}"


def test_given_the_chat_route_when_scanned_then_the_only_storage_function_it_uses_is_the_read_one():
    # Arrange / Act
    used = storage_functions_used_in(ROUTE_FILE.read_text())

    # Assert
    assert used == ALLOWED_STORAGE_USE


@pytest.mark.parametrize("snippet", [
    "from app.storage import create_todo",
    "from app import storage\nstorage.delete_todo(1)",
    "import sqlite3",
    "from app.storage import update_todo as u",
    "storage.init_db()",
    "import sqlite3 as db",
    "from sqlite3 import connect",
])
def test_given_a_snippet_that_can_write_when_scanned_then_the_write_check_flags_it(snippet):
    # Arrange / Act / Assert
    assert forbidden_names_in(snippet)


@pytest.mark.parametrize("snippet", [
    "from app.storage import list_todos",
    "from app import storage",
    "import app.storage",
    "from app.storage import list_todos as read",
    "import app.storage.helpers",
])
def test_given_a_snippet_that_imports_storage_when_scanned_then_the_import_check_flags_it(snippet):
    # Arrange / Act / Assert
    assert storage_imports_in(snippet)


def test_given_the_chat_route_when_scanned_then_it_does_not_rename_the_storage_module():
    # Arrange / Act / Assert
    assert storage_aliases_in(ROUTE_FILE.read_text()) == []


def test_given_an_import_that_renames_storage_when_scanned_then_the_alias_check_flags_it():
    # Arrange / Act / Assert
    assert storage_aliases_in("from app import storage as s") == ["s"]


@pytest.mark.parametrize("snippet", [
    "services.create_todo({})",
    "read_todos.delete_todo(1)",
    "create_todo({})",
])
def test_given_a_call_to_a_writer_through_any_object_when_scanned_then_the_write_check_flags_it(snippet):
    # Arrange / Act / Assert
    assert forbidden_names_in(snippet)


@pytest.mark.parametrize("snippet", [
    "x = Intent.create_todo",
    "class Intent:\n    create_todo = 'create_todo'",
    "ROUTES = {Intent.create_todo: 'task_agent'}",
])
def test_given_the_create_todo_intent_name_when_scanned_then_it_is_not_mistaken_for_a_write(snippet):
    # Arrange / Act / Assert
    assert not forbidden_names_in(snippet)


@pytest.mark.parametrize("snippet", [
    "import json\nfrom app.models import Priority\nx = [t for t in read_todos()]",
    "from app.agents.due import find_due",
])
def test_given_innocent_code_when_scanned_then_neither_check_flags_it(snippet):
    # Arrange / Act / Assert
    assert not forbidden_names_in(snippet) and not storage_imports_in(snippet)


@pytest.mark.parametrize("snippet, expected", [
    ("storage.list_todos()", {"list_todos"}),
    ("storage.list_todos()\nstorage.create_todo({})", {"list_todos", "create_todo"}),
    ("other.create_todo()", set()),
])
def test_given_code_using_storage_when_scanned_then_the_use_check_reports_exactly_the_functions_used(snippet, expected):
    # Arrange / Act / Assert
    assert storage_functions_used_in(snippet) == expected
