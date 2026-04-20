from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator


class ImagenOut(BaseModel):
    id: int
    titulo: str
    juego: str
    descripcion: str | None
    filename: str
    usuario_id: int
    username: str = ""
    created_at: datetime
    tags: list[str] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def from_orm_object(cls, data):
        if hasattr(data, "__tablename__"):
            usuario = getattr(data, "usuario", None)
            return {
                "id": data.id,
                "titulo": data.titulo,
                "juego": data.juego,
                "descripcion": data.descripcion,
                "filename": data.filename,
                "usuario_id": data.usuario_id,
                "username": usuario.username if usuario else "",
                "created_at": data.created_at,
                "tags": data.tags,
            }
        return data

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tag_names(cls, v):
        if isinstance(v, list) and v and hasattr(v[0], "name"):
            return [tag.name for tag in v]
        return v
