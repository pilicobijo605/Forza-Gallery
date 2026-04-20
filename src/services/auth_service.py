import asyncio
import secrets

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.email import send_verification_email
from src.core.security import create_access_token, hash_password, verify_password
from src.db.repositories.usuario_repository import UsuarioRepository
from src.models.usuario import Usuario
from src.schemas.usuario import RegisterResponse, Token, UsuarioCreate


async def register(data: UsuarioCreate, db: AsyncSession) -> Token:
    repo = UsuarioRepository(db)
    if await repo.get_by_username(data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username ya en uso")
    if await repo.get_by_email(data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya en uso")

    user = await repo.create(data.username, data.email, hash_password(data.password), verification_token=None, is_verified=True)
    return Token(access_token=create_access_token(user.username))


async def verify_email(token: str, db: AsyncSession) -> None:
    repo = UsuarioRepository(db)
    user = await repo.get_by_verification_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o expirado")
    await repo.verify_user(user)


async def cambiar_password(user: Usuario, password_actual: str, nueva_password: str, db: AsyncSession) -> None:
    if not verify_password(password_actual, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual incorrecta")
    user.password = hash_password(nueva_password)
    await db.commit()


async def eliminar_cuenta(user: Usuario, password: str, db: AsyncSession) -> None:
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña incorrecta")

    from src.db.repositories.imagen_repository import ImagenRepository
    from src.services.imagen_service import _extract_public_id
    import cloudinary.uploader

    imagenes = await ImagenRepository(db).get_all(usuario=user.username, limit=500)
    for img in imagenes:
        try:
            public_id = _extract_public_id(img.filename)
            await asyncio.to_thread(cloudinary.uploader.destroy, public_id)
        except Exception:
            pass

    uid = user.id
    for stmt in [
        "DELETE FROM reacciones WHERE usuario_id = :uid",
        "DELETE FROM reportes WHERE usuario_id = :uid",
        "DELETE FROM comentarios WHERE usuario_id = :uid",
        "DELETE FROM likes WHERE usuario_id = :uid",
        "DELETE FROM guardados WHERE usuario_id = :uid",
        "DELETE FROM seguidores WHERE seguidor_id = :uid OR seguido_id = :uid",
        "DELETE FROM usuarios_favoritos WHERE usuario_id = :uid OR favorito_id = :uid",
        "DELETE FROM imagen_tags WHERE imagen_id IN (SELECT id FROM imagenes WHERE usuario_id = :uid)",
        "DELETE FROM imagenes WHERE usuario_id = :uid",
        "DELETE FROM usuarios WHERE id = :uid",
    ]:
        await db.execute(text(stmt), {"uid": uid})
    await db.commit()


async def login(username: str, password: str, db: AsyncSession) -> Token:
    repo = UsuarioRepository(db)
    user = await repo.get_by_username(username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta no verificada. Revisa tu email.",
        )
    return Token(access_token=create_access_token(user.username))
