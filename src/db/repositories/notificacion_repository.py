from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notificacion import Notificacion


class NotificacionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear(self, usuario_id: int, tipo: str, from_username: str, imagen_id: int | None = None) -> None:
        self.db.add(Notificacion(
            usuario_id=usuario_id, tipo=tipo,
            from_username=from_username, imagen_id=imagen_id,
        ))
        await self.db.commit()

    async def get_mis_notificaciones(self, usuario_id: int, limit: int = 30) -> list[Notificacion]:
        r = await self.db.execute(
            select(Notificacion)
            .where(Notificacion.usuario_id == usuario_id)
            .order_by(Notificacion.created_at.desc())
            .limit(limit)
        )
        return list(r.scalars().all())

    async def count_no_leidas(self, usuario_id: int) -> int:
        r = await self.db.execute(
            select(func.count(Notificacion.id))
            .where(Notificacion.usuario_id == usuario_id, Notificacion.leida == False)  # noqa: E712
        )
        return r.scalar_one()

    async def marcar_todas_leidas(self, usuario_id: int) -> None:
        await self.db.execute(
            update(Notificacion)
            .where(Notificacion.usuario_id == usuario_id, Notificacion.leida == False)  # noqa: E712
            .values(leida=True)
        )
        await self.db.commit()
