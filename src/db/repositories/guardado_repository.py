from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.guardado import Guardado
from src.models.imagen import Imagen


class GuardadoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, usuario_id: int, imagen_id: int) -> Guardado | None:
        result = await self.db.execute(
            select(Guardado).where(Guardado.usuario_id == usuario_id, Guardado.imagen_id == imagen_id)
        )
        return result.scalar_one_or_none()

    async def toggle(self, usuario_id: int, imagen_id: int) -> bool:
        existing = await self.get(usuario_id, imagen_id)
        if existing:
            await self.db.delete(existing)
            await self.db.commit()
            return False
        self.db.add(Guardado(usuario_id=usuario_id, imagen_id=imagen_id))
        await self.db.commit()
        return True

    async def get_imagenes_guardadas(self, usuario_id: int) -> list[Imagen]:
        result = await self.db.execute(
            select(Imagen)
            .join(Guardado, Guardado.imagen_id == Imagen.id)
            .where(Guardado.usuario_id == usuario_id)
            .order_by(Guardado.created_at.desc())
        )
        return list(result.scalars().all())
