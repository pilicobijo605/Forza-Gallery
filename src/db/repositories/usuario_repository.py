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

    async def create(self, username: str, email: str, hashed_password: str, verification_token: str | None = None, is_verified: bool = True) -> Usuario:
        user = Usuario(
            username=username,
            email=email,
            password=hashed_password,
            is_verified=is_verified,
            verification_token=verification_token,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def verify_user(self, user: Usuario) -> None:
        user.is_verified = True
        user.verification_token = None
        await self.db.commit()

    async def update_profile(self, user: Usuario, bio: str | None, is_public: bool, avatar_url: str | None = None) -> Usuario:
        user.bio = bio
        user.is_public = is_public
        if avatar_url is not None:
            user.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        return user
