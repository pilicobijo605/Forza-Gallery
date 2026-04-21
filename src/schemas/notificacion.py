from datetime import datetime
from pydantic import BaseModel


class NotificacionOut(BaseModel):
    id: int
    tipo: str
    from_username: str | None
    imagen_id: int | None
    leida: bool
    created_at: datetime

    model_config = {"from_attributes": True}
