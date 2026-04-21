from datetime import datetime
from pydantic import BaseModel


class MensajeCreate(BaseModel):
    contenido: str


class MensajeOut(BaseModel):
    id: int
    conversacion_id: int
    autor_id: int
    autor_username: str
    contenido: str
    leido: bool
    created_at: datetime


class ConversacionOut(BaseModel):
    id: int
    otro_username: str
    otro_avatar: str | None
    ultimo_mensaje: str | None
    ultimo_at: datetime | None
    no_leidos: int
