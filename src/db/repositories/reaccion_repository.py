from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.reaccion import Reaccion


class ReaccionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_reaccion(self, comentario_id: int, usuario_id: int) -> str | None:
        result = await self.db.execute(
            select(Reaccion.emoji).where(
                Reaccion.comentario_id == comentario_id,
                Reaccion.usuario_id == usuario_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_counts(self, comentario_id: int) -> dict[str, int]:
        result = await self.db.execute(
            select(Reaccion.emoji, func.count())
            .where(Reaccion.comentario_id == comentario_id)
            .group_by(Reaccion.emoji)
        )
        return {row[0]: row[1] for row in result.all()}

    async def toggle(self, comentario_id: int, usuario_id: int, emoji: str) -> str | None:
        result = await self.db.execute(
            select(Reaccion).where(
                Reaccion.comentario_id == comentario_id,
                Reaccion.usuario_id == usuario_id,
            )
        )
        row = result.scalar_one_or_none()
        if row:
            if row.emoji == emoji:
                await self.db.delete(row)
                await self.db.commit()
                return None
            row.emoji = emoji
            await self.db.commit()
            return emoji
        self.db.add(Reaccion(comentario_id=comentario_id, usuario_id=usuario_id, emoji=emoji))
        await self.db.commit()
        return emoji
