"""The web app: the REST API for todos and the single page."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse

from app import storage
from app.chat import router as chat_router
from app.models import Priority, StatusFilter, TodoCreate, TodoUpdate

PAGE = Path(__file__).resolve().parent.parent / "static" / "index.html"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    storage.init_db()
    yield


app = FastAPI(title="Todo App (HVE build)", lifespan=lifespan)
app.include_router(chat_router)


def _with_status(todo: dict) -> dict:
    return {**todo, "status": "completed" if todo["completed"] else "active"}


def _not_found(todo_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Todo {todo_id} not found")


@app.get("/", include_in_schema=False)
def page():
    return FileResponse(PAGE, media_type="text/html")


@app.post("/todos", status_code=201)
def create_todo(payload: TodoCreate):
    data = payload.model_dump(mode="json")
    return _with_status(storage.create_todo(data))


@app.get("/todos")
def list_todos(status: StatusFilter = StatusFilter.all, priority: Optional[Priority] = Query(default=None)):
    todos = storage.list_todos(status=status.value, priority=priority.value if priority else None)
    return [_with_status(t) for t in todos]


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    todo = storage.get_todo(todo_id)
    if todo is None:
        raise _not_found(todo_id)
    return _with_status(todo)


@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, payload: TodoUpdate):
    sent = payload.model_dump(mode="json", include=payload.model_fields_set)
    todo = storage.update_todo(todo_id, sent)
    if todo is None:
        raise _not_found(todo_id)
    return _with_status(todo)


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    if not storage.delete_todo(todo_id):
        raise _not_found(todo_id)
    return Response(status_code=204)
