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
    from src.models import seguidor, favorito_usuario  # noqa: F401
    from src.models import notificacion, conversacion, mensaje  # noqa: F401
    from src.models.usuario import Usuario
    from src.core.security import hash_password
    from sqlalchemy import select

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import text
        try:
            await conn.execute(text("ALTER TABLE imagenes ADD COLUMN visitas INTEGER NOT NULL DEFAULT 0"))
        except Exception:
            pass
        try:
            await conn.execute(text("UPDATE usuarios SET is_public = TRUE WHERE is_public IS NULL"))
        except Exception:
            pass
        try:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS seguidores (
                    seguidor_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    seguido_id  INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (seguidor_id, seguido_id)
                )
            """))
        except Exception:
            pass
        try:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    tipo VARCHAR(50) NOT NULL,
                    from_username VARCHAR(50),
                    imagen_id INTEGER REFERENCES imagenes(id) ON DELETE SET NULL,
                    leida BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """))
        except Exception:
            pass
        try:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS conversaciones (
                    id SERIAL PRIMARY KEY,
                    user1_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    user2_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """))
        except Exception:
            pass
        try:
            await conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS conv_unique
                ON conversaciones (LEAST(user1_id, user2_id), GREATEST(user1_id, user2_id))
            """))
        except Exception:
            pass
        try:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY,
                    conversacion_id INTEGER NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
                    autor_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    contenido TEXT NOT NULL,
                    leido BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """))
        except Exception:
            pass
        try:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usuarios_favoritos (
                    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    favorito_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (usuario_id, favorito_id)
                )
            """))
        except Exception:
            pass

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
