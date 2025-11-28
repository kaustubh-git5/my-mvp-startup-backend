# backend/app/schemas.py
from pydantic import BaseModel, EmailStr

class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
