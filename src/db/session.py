from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with SessionLocal() as session:
        yield session


async def init_db():
    from src.models import usuario, imagen, tag  # noqa: F401
    from src.models import like, guardado, comentario, reaccion  # noqa: F401
    from src.models.usuario import Usuario
    from src.core.security import hash_password
    from sqlalchemy import select

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        result = await session.execute(select(Usuario).where(Usuario.username == settings.admin_username))
        if not result.scalar_one_or_none():
            admin = Usuario(
                username=settings.admin_username,
                email=settings.admin_email,
                password=hash_password(settings.admin_password),
                is_active=True,
                is_verified=True,
            )
            session.add(admin)
            await session.commit()
