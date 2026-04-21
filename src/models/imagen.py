from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.tag import Tag, imagen_tags

from src.db.session import Base


class Imagen(Base):
    __tablename__ = "imagenes"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    juego: Mapped[str] = mapped_column(String(10))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    filename: Mapped[str] = mapped_column(String(255))
    visitas: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    map_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="imagenes", lazy="selectin")  # noqa: F821
    tags: Mapped[list[Tag]] = relationship(secondary=imagen_tags, lazy="selectin")
