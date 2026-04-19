from sqlalchemy import Column, ForeignKey, Integer, String, Table

from src.db.session import Base

imagen_tags = Table(
    "imagen_tags",
    Base.metadata,
    Column("imagen_id", Integer, ForeignKey("imagenes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",    Integer, ForeignKey("tags.id",     ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id:   int = Column(Integer, primary_key=True)
    name: str = Column(String(100), unique=True, index=True)
