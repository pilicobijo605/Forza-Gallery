from datetime import datetime

from pydantic import BaseModel, field_validator


class ImagenOut(BaseModel):
    id: int
    titulo: str
    juego: str
    descripcion: str | None
    filename: str
    usuario_id: int
    created_at: datetime
    tags: list[str] = []

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tag_names(cls, v):
        if isinstance(v, list) and v and hasattr(v[0], "name"):
            return [tag.name for tag in v]
        return v
