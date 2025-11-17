from pydantic import BaseModel, Emailstr

class UserCreate(BaseModel):
    email: Emailstr
    password: str


class UserLogin(BaseModel):
    password: str
    email: Emailstr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"



class RefreshTokenSchema(BaseModel):
    refresh_token: str



class UserOut(BaseModel):
    id: int
    email: str
    role: str