from typing import Annotated, Union
from fastapi import Depends, HTTPException, APIRouter
from fastapi import status
from pydantic import BaseModel
from .auth import get_password_hash

from database import db_dependency
from .auth import get_current_user
import models

router = APIRouter(prefix="/users", tags=["users"])
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserResponse(BaseModel):
    email: str
    first_name: str
    role: str
    last_name: str
    username: str
    phone_number: Union[str, None]


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_login_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(models.Users).first()


@router.put("/", status_code=status.HTTP_200_OK)
def update_password(user: user_dependency, db: db_dependency, new_password: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user = db.query(models.Users).first()
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)


@router.put(
    "/update_phone_number", status_code=status.HTTP_200_OK, response_model=UserResponse
)
def update_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user:
        user_db = db.query(models.Users).first()
        user_db.phone_number = phone_number
        db.commit()
        db.refresh(user_db)
        return user_db
    else:
        raise HTTPException(status_code=401, detail="Authentication Failed")
