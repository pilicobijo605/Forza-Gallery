from datetime import datetime
from pydantic import BaseModel


class LikeInfo(BaseModel):
    count: int
    liked: bool
    usernames: list[str]


class ComentarioOut(BaseModel):
    id: int
    imagen_id: int
    usuario_id: int
    username: str
    contenido: str
    created_at: datetime


class ComentarioCreate(BaseModel):
    contenido: str


class ReporteCreate(BaseModel):
    motivo: str | None = None
