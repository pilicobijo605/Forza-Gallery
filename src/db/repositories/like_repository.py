from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.like import Like


class LikeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, usuario_id: int, imagen_id: int) -> Like | None:
        result = await self.db.execute(
            select(Like).where(Like.usuario_id == usuario_id, Like.imagen_id == imagen_id)
        )
        return result.scalar_one_or_none()

    async def toggle(self, usuario_id: int, imagen_id: int) -> bool:
        existing = await self.get(usuario_id, imagen_id)
        if existing:
            await self.db.delete(existing)
            await self.db.commit()
            return False
        self.db.add(Like(usuario_id=usuario_id, imagen_id=imagen_id))
        await self.db.commit()
        return True

    async def count(self, imagen_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Like).where(Like.imagen_id == imagen_id)
        )
        return result.scalar_one()

    async def usernames(self, imagen_id: int) -> list[str]:
        from src.models.usuario import Usuario
        result = await self.db.execute(
            select(Usuario.username)
            .join(Like, Like.usuario_id == Usuario.id)
            .where(Like.imagen_id == imagen_id)
            .order_by(Like.created_at.desc())
            .limit(50)
        )
        return list(result.scalars().all())
