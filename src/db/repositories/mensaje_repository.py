from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.mensaje import Mensaje


class MensajeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_mensajes(self, conversacion_id: int, limit: int = 100) -> list[Mensaje]:
        r = await self.db.execute(
            select(Mensaje)
            .where(Mensaje.conversacion_id == conversacion_id)
            .order_by(Mensaje.created_at.asc())
            .limit(limit)
        )
        return list(r.scalars().all())

    async def crear(self, conversacion_id: int, autor_id: int, contenido: str) -> Mensaje:
        m = Mensaje(conversacion_id=conversacion_id, autor_id=autor_id, contenido=contenido)
        self.db.add(m)
        await self.db.commit()
        await self.db.refresh(m)
        return m

    async def marcar_leidos(self, conversacion_id: int, receptor_id: int) -> None:
        await self.db.execute(
            update(Mensaje)
            .where(
                Mensaje.conversacion_id == conversacion_id,
                Mensaje.autor_id != receptor_id,
                Mensaje.leido == False,  # noqa: E712
            )
            .values(leido=True)
        )
        await self.db.commit()

    async def count_no_leidos(self, conversacion_id: int, receptor_id: int) -> int:
        r = await self.db.execute(
            select(func.count(Mensaje.id)).where(
                Mensaje.conversacion_id == conversacion_id,
                Mensaje.autor_id != receptor_id,
                Mensaje.leido == False,  # noqa: E712
            )
        )
        return r.scalar_one()

    async def ultimo_mensaje(self, conversacion_id: int) -> Mensaje | None:
        r = await self.db.execute(
            select(Mensaje)
            .where(Mensaje.conversacion_id == conversacion_id)
            .order_by(Mensaje.created_at.desc())
            .limit(1)
        )
        return r.scalar_one_or_none()
