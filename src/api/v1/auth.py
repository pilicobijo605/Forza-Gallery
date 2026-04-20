from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import CurrentActiveUser, DbSession
from src.db.session import get_session
from src.schemas.usuario import RegisterResponse, Token, UsuarioCreate, UsuarioOut
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(data: UsuarioCreate, db: DbSession):
    return await auth_service.register(data, db)


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_session)):
    await auth_service.verify_email(token, db)
    return RedirectResponse(url="/login.html?verified=1")


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    return await auth_service.login(form.username, form.password, db)


@router.get("/me", response_model=UsuarioOut)
async def me(user: CurrentActiveUser):
    return user
