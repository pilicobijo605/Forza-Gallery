from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Mínimo 12 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Debe contener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Debe contener al menos un número")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Debe contener al menos un carácter especial")
        return v


class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PerfilOut(BaseModel):
    username: str
    bio: str | None
    avatar_url: str | None
    is_public: bool
    created_at: datetime
    seguidores: int = 0
    siguiendo: int = 0
    yo_sigo: bool = False
    es_favorito: bool = False

    model_config = {"from_attributes": True}


class UsuarioMinimoOut(BaseModel):
    username: str
    avatar_url: str | None = None
    bio: str | None = None
    yo_sigo: bool = False

    model_config = {"from_attributes": True}


class PerfilUpdate(BaseModel):
    bio: str | None = None
    is_public: bool = True


class CambiarPassword(BaseModel):
    password_actual: str
    nueva_password: str

    @field_validator("nueva_password")
    @classmethod
    def validate_nueva(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Mínimo 12 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Debe contener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Debe contener al menos un número")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Debe contener al menos un carácter especial")
        return v


class EliminarCuenta(BaseModel):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    message: str
    email: str
