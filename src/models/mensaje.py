from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.session import Base


class Mensaje(Base):
    __tablename__ = "mensajes"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversacion_id: Mapped[int] = mapped_column(ForeignKey("conversaciones.id", ondelete="CASCADE"))
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    contenido: Mapped[str] = mapped_column(Text)
    leido: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    conversacion: Mapped["Conversacion"] = relationship(back_populates="mensajes")
