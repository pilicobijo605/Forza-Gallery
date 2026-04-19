from datetime import datetime

from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
