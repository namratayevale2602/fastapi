from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class UserCreate(BaseModel):
    username: str
    password: str