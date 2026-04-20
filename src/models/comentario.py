from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.session import Base


class Comentario(Base):
    __tablename__ = "comentarios"
    id:         Mapped[int] = mapped_column(primary_key=True)
    imagen_id:  Mapped[int] = mapped_column(ForeignKey("imagenes.id", ondelete="CASCADE"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    contenido:  Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    usuario:    Mapped["Usuario"] = relationship(lazy="selectin")  # noqa: F821


class Reporte(Base):
    __tablename__ = "reportes"
    id:            Mapped[int]      = mapped_column(primary_key=True)
    comentario_id: Mapped[int]      = mapped_column(ForeignKey("comentarios.id", ondelete="CASCADE"))
    usuario_id:    Mapped[int]      = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    motivo:        Mapped[str|None] = mapped_column(String(200), nullable=True)
    created_at:    Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
