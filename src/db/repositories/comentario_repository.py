from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comentario import Comentario, Reporte


class ComentarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_imagen(self, imagen_id: int) -> list[Comentario]:
        result = await self.db.execute(
            select(Comentario)
            .where(Comentario.imagen_id == imagen_id)
            .order_by(Comentario.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, comentario_id: int) -> Comentario | None:
        result = await self.db.execute(
            select(Comentario).where(Comentario.id == comentario_id)
        )
        return result.scalar_one_or_none()

    async def create(self, imagen_id: int, usuario_id: int, contenido: str) -> Comentario:
        c = Comentario(imagen_id=imagen_id, usuario_id=usuario_id, contenido=contenido)
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def delete(self, comentario: Comentario) -> None:
        await self.db.delete(comentario)
        await self.db.commit()

    async def reportar(self, comentario_id: int, usuario_id: int, motivo: str | None) -> None:
        self.db.add(Reporte(comentario_id=comentario_id, usuario_id=usuario_id, motivo=motivo))
        await self.db.commit()

    async def ya_reportado(self, comentario_id: int, usuario_id: int) -> bool:
        result = await self.db.execute(
            select(Reporte).where(
                Reporte.comentario_id == comentario_id,
                Reporte.usuario_id == usuario_id,
            )
        )
        return result.scalar_one_or_none() is not None
