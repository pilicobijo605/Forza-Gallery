from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.favorito_usuario import FavoritoUsuario
from src.models.usuario import Usuario


class FavoritoUsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle(self, usuario_id: int, favorito_id: int) -> bool:
        row = await self.db.get(FavoritoUsuario, (usuario_id, favorito_id))
        if row:
            await self.db.delete(row)
            await self.db.commit()
            return False
        self.db.add(FavoritoUsuario(usuario_id=usuario_id, favorito_id=favorito_id))
        await self.db.commit()
        return True

    async def is_favorito(self, usuario_id: int, favorito_id: int) -> bool:
        return bool(await self.db.get(FavoritoUsuario, (usuario_id, favorito_id)))

    async def get_favoritos(self, usuario_id: int) -> list[Usuario]:
        r = await self.db.execute(
            select(Usuario)
            .join(FavoritoUsuario, FavoritoUsuario.favorito_id == Usuario.id)
            .where(FavoritoUsuario.usuario_id == usuario_id)
            .order_by(FavoritoUsuario.created_at.desc())
        )
        return list(r.scalars().all())
