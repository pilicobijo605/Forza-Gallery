from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversacion import Conversacion


class ConversacionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, user_a: int, user_b: int) -> Conversacion:
        u1, u2 = min(user_a, user_b), max(user_a, user_b)
        r = await self.db.execute(
            select(Conversacion).where(Conversacion.user1_id == u1, Conversacion.user2_id == u2)
        )
        conv = r.scalar_one_or_none()
        if not conv:
            conv = Conversacion(user1_id=u1, user2_id=u2)
            self.db.add(conv)
            await self.db.commit()
            await self.db.refresh(conv)
        return conv

    async def get_mis_conversaciones(self, usuario_id: int) -> list[Conversacion]:
        r = await self.db.execute(
            select(Conversacion).where(
                or_(Conversacion.user1_id == usuario_id, Conversacion.user2_id == usuario_id)
            )
        )
        return list(r.scalars().all())
