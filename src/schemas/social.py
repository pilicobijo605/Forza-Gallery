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
    reacciones: dict[str, int] = {}
    mi_reaccion: str | None = None


class ComentarioCreate(BaseModel):
    contenido: str


class ReporteCreate(BaseModel):
    motivo: str | None = None


class ReaccionCreate(BaseModel):
    emoji: str
