from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str  = "bearer"

class TokenData(BaseModel):
    user_id: Optional[UUID] = None

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserRead(BaseModel):
    user_id: UUID
    email: EmailStr
    name: str

    class Config:
        orm_mode = True
