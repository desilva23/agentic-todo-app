from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse

from app import chat, storage
from app.models import Priority, StatusFilter, Todo, TodoCreate, TodoUpdate

INDEX_PAGE = Path(__file__).resolve().parent.parent / "static" / "index.html"


@asynccontextmanager
async def lifespan(_: FastAPI):
    storage.init_db()  # create the table on start, so there is no setup step
    yield


app = FastAPI(title="Todo App (Spec Kit build)", lifespan=lifespan)
app.include_router(chat.router)


def _not_found(todo_id: int) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo {todo_id} not found")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(INDEX_PAGE)


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    return storage.create_todo(**payload.model_dump(mode="json"))


@app.get("/todos", response_model=list[Todo])
def list_todos(status: StatusFilter = "all", priority: Optional[Priority] = None):
    return storage.list_todos(status=status, priority=priority)


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    todo = storage.get_todo(todo_id)
    if todo is None:
        raise _not_found(todo_id)
    return todo


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoUpdate):
    changes = payload.model_dump(mode="json", exclude_unset=True)  # only the fields that were sent
    todo = storage.update_todo(todo_id, changes)
    if todo is None:
        raise _not_found(todo_id)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    if not storage.delete_todo(todo_id):
        raise _not_found(todo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
