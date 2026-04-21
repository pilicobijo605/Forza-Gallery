from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    tipo: Mapped[str] = mapped_column(String(50))
    from_username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    imagen_id: Mapped[int | None] = mapped_column(ForeignKey("imagenes.id", ondelete="SET NULL"), nullable=True)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
