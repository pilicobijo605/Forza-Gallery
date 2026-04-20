from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base

ALLOWED_EMOJIS = {"❤️", "😂", "😮", "👍", "🔥"}


class Reaccion(Base):
    __tablename__ = "reacciones"
    comentario_id: Mapped[int] = mapped_column(ForeignKey("comentarios.id", ondelete="CASCADE"), primary_key=True)
    usuario_id:    Mapped[int] = mapped_column(ForeignKey("usuarios.id",    ondelete="CASCADE"), primary_key=True)
    emoji:         Mapped[str] = mapped_column(String(10))
    created_at:    Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
