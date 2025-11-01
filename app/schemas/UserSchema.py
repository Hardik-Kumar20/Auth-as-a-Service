from pydantic import BaseModel, Emailstr

class UserCreate(BaseModel):
    email: Emailstr
    password: str


class UserLogin(BaseModel):
    password: str
    email: Emailstr


class UserOut(BaseModel):
    id: int
    email: str
    role: str
