import secrets

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.email import send_verification_email
from src.core.security import create_access_token, hash_password, verify_password
from src.db.repositories.usuario_repository import UsuarioRepository
from src.schemas.usuario import RegisterResponse, Token, UsuarioCreate


async def register(data: UsuarioCreate, db: AsyncSession) -> RegisterResponse:
    repo = UsuarioRepository(db)
    if await repo.get_by_username(data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username ya en uso")
    if await repo.get_by_email(data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya en uso")

    token = secrets.token_urlsafe(32)
    user = await repo.create(data.username, data.email, hash_password(data.password), token)

    try:
        await send_verification_email(user.email, user.username, token)
    except Exception:
        await db.delete(user)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo enviar el email de verificación. Inténtalo de nuevo.",
        )

    return RegisterResponse(
        message="Te hemos enviado un email de verificación.",
        email=user.email,
    )


async def verify_email(token: str, db: AsyncSession) -> None:
    repo = UsuarioRepository(db)
    user = await repo.get_by_verification_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o expirado")
    await repo.verify_user(user)


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
