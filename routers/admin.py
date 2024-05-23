from typing import Annotated
from fastapi import Depends, Path, HTTPException, APIRouter
from fastapi import status
from pydantic import BaseModel, Field


from database import db_dependency
from .auth import get_current_user
import models

router = APIRouter(prefix="/admin/todo", tags=["admin"])
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(models.Todos).all()
