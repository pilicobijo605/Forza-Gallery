from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import credentials_error, inactive_user
from src.core.security import decode_token
from src.db.session import get_session
from src.db.repositories.usuario_repository import UsuarioRepository
from src.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> Usuario:
    try:
        username = decode_token(token)
    except JWTError:
        raise credentials_error
    repo = UsuarioRepository(db)
    user = await repo.get_by_username(username)
    if not user:
        raise credentials_error
    return user


async def get_current_active_user(
    user: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    if not user.is_active:
        raise inactive_user
    return user


async def get_optional_user(
    token: Annotated[str | None, Depends(oauth2_optional)],
    db: DbSession,
) -> Usuario | None:
    if not token:
        return None
    try:
        username = decode_token(token)
    except JWTError:
        return None
    return await UsuarioRepository(db).get_by_username(username)


CurrentUser = Annotated[Usuario, Depends(get_current_user)]
CurrentActiveUser = Annotated[Usuario, Depends(get_current_active_user)]
OptionalUser = Annotated[Usuario | None, Depends(get_optional_user)]
