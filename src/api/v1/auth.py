from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import CurrentActiveUser, DbSession
from src.db.session import get_session
from src.schemas.usuario import Token, UsuarioCreate, UsuarioOut
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
async def register(data: UsuarioCreate, db: DbSession):
    return await auth_service.register(data, db)


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    return await auth_service.login(form.username, form.password, db)


@router.get("/me", response_model=UsuarioOut)
async def me(user: CurrentActiveUser):
    return user
