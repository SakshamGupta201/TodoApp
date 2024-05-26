from fastapi import FastAPI

from .database import engine
from .routers import auth, todos, admin, users
from . import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# health check
@app.get("/health")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(todos.router)
app.include_router(users.router)
