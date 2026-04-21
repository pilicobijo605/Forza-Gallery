from datetime import datetime, timedelta, timezone
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.imagen import Imagen
from src.models.tag import Tag, imagen_tags


class ImagenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        juego: str | None = None,
        tag: str | None = None,
        fecha: str | None = None,
        usuario: str | None = None,
        q: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Imagen]:
        query = select(Imagen).order_by(Imagen.created_at.desc()).offset(skip).limit(limit)
        if juego:
            query = query.where(Imagen.juego == juego)
        if usuario:
            from src.models.usuario import Usuario as UsuarioModel
            query = query.join(UsuarioModel).where(UsuarioModel.username == usuario)
        if tag:
            query = query.where(
                Imagen.id.in_(
                    select(imagen_tags.c.imagen_id).join(Tag).where(Tag.name == tag.lower())
                )
            )
        if fecha:
            from datetime import date as date_type
            d = date_type.fromisoformat(fecha)
            start = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)
            end   = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
            query = query.where(Imagen.created_at.between(start, end))
        if q:
            query = query.where(
                or_(Imagen.titulo.ilike(f"%{q}%"), Imagen.descripcion.ilike(f"%{q}%"))
            )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_trending(self, limit: int = 10) -> list[Imagen]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        query = (
            select(Imagen)
            .where(Imagen.created_at >= cutoff)
            .order_by(Imagen.visitas.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, imagen_id: int) -> Imagen | None:
        result = await self.db.execute(select(Imagen).where(Imagen.id == imagen_id))
        return result.scalar_one_or_none()

    async def increment_visitas(self, imagen: Imagen) -> None:
        imagen.visitas += 1
        await self.db.commit()

    async def count_by_juego(self) -> dict[str, int]:
        result = await self.db.execute(select(Imagen.juego, Imagen.id))
        rows = result.all()
        counts: dict[str, int] = {}
        for juego, _ in rows:
            counts[juego] = counts.get(juego, 0) + 1
        return counts

    async def create(
        self,
        titulo: str,
        juego: str,
        descripcion: str | None,
        filename: str,
        usuario_id: int,
        tags: list = [],
        map_x: float | None = None,
        map_y: float | None = None,
    ) -> Imagen:
        img = Imagen(
            titulo=titulo,
            juego=juego,
            descripcion=descripcion,
            filename=filename,
            usuario_id=usuario_id,
            tags=tags,
            map_x=map_x,
            map_y=map_y,
        )
        self.db.add(img)
        await self.db.commit()
        await self.db.refresh(img)
        return img

    async def update(
        self,
        imagen: Imagen,
        titulo: str,
        juego: str,
        descripcion: str | None,
        tags: list,
    ) -> Imagen:
        imagen.titulo = titulo
        imagen.juego = juego
        imagen.descripcion = descripcion or None
        imagen.tags = tags
        await self.db.commit()
        await self.db.refresh(imagen)
        return imagen

    async def delete(self, imagen: Imagen) -> None:
        await self.db.delete(imagen)
        await self.db.commit()
