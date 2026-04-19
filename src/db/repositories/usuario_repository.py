from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Usuario | None:
        result = await self.db.execute(select(Usuario).where(Usuario.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Usuario | None:
        result = await self.db.execute(select(Usuario).where(Usuario.email == email))
        return result.scalar_one_or_none()

    async def create(self, username: str, email: str, hashed_password: str) -> Usuario:
        user = Usuario(username=username, email=email, password=hashed_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
