from typing import Annotated
from fastapi import Depends, Path, HTTPException, APIRouter
from fastapi import status
from pydantic import BaseModel, Field


from database import db_dependency
from .auth import get_current_user
import models

router = APIRouter(prefix="/todo", tags=["todo"])
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/")
def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return (
        db.query(models.Todos)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .all()
    )


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
def read_todos_by_id(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(title="The ID of the item to get", gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo_model is not None:
        return todo_model

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo Not Found"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_todo(user: user_dependency, db: db_dependency, todo: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = models.Todos(**todo.model_dump(), owner_id=user.get("user_id"))

    db.add(todo_model)
    db.commit()


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not Found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not Found")

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()
