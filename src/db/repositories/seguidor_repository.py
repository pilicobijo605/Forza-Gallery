from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.seguidor import Seguidor
from src.models.usuario import Usuario


class SeguidorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle(self, seguidor_id: int, seguido_id: int) -> bool:
        row = await self.db.get(Seguidor, (seguidor_id, seguido_id))
        if row:
            await self.db.delete(row)
            await self.db.commit()
            return False
        self.db.add(Seguidor(seguidor_id=seguidor_id, seguido_id=seguido_id))
        await self.db.commit()
        return True

    async def is_siguiendo(self, seguidor_id: int, seguido_id: int) -> bool:
        return bool(await self.db.get(Seguidor, (seguidor_id, seguido_id)))

    async def count_seguidores(self, usuario_id: int) -> int:
        r = await self.db.execute(select(func.count()).where(Seguidor.seguido_id == usuario_id))
        return r.scalar_one()

    async def count_siguiendo(self, usuario_id: int) -> int:
        r = await self.db.execute(select(func.count()).where(Seguidor.seguidor_id == usuario_id))
        return r.scalar_one()

    async def get_seguidores(self, usuario_id: int) -> list[Usuario]:
        r = await self.db.execute(
            select(Usuario)
            .join(Seguidor, Seguidor.seguidor_id == Usuario.id)
            .where(Seguidor.seguido_id == usuario_id)
            .order_by(Seguidor.created_at.desc())
        )
        return list(r.scalars().all())

    async def get_siguiendo(self, usuario_id: int) -> list[Usuario]:
        r = await self.db.execute(
            select(Usuario)
            .join(Seguidor, Seguidor.seguido_id == Usuario.id)
            .where(Seguidor.seguidor_id == usuario_id)
            .order_by(Seguidor.created_at.desc())
        )
        return list(r.scalars().all())
