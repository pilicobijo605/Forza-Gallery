import asyncio

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, UploadFile, File, status

from src.core.dependencies import CurrentActiveUser, DbSession
from src.db.repositories.usuario_repository import UsuarioRepository
from src.schemas.usuario import PerfilOut, PerfilUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


@router.get("/{username}", response_model=PerfilOut)
async def get_perfil(username: str, db: DbSession):
    repo = UsuarioRepository(db)
    user = await repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if not user.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Este perfil es privado")
    return PerfilOut.model_validate(user)


@router.put("/me", response_model=PerfilOut)
async def update_perfil(data: PerfilUpdate, db: DbSession, current_user: CurrentActiveUser):
    repo = UsuarioRepository(db)
    user = await repo.update_profile(current_user, data.bio, data.is_public)
    return PerfilOut.model_validate(user)


@router.put("/me/avatar", response_model=PerfilOut)
async def update_avatar(
    db: DbSession,
    current_user: CurrentActiveUser,
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato no permitido")
    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Imagen demasiado grande (máx 5 MB)")

    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        content,
        folder="forzagallery/avatars",
        public_id=f"avatar_{current_user.username}",
        overwrite=True,
        resource_type="image",
        transformation=[{"width": 300, "height": 300, "crop": "fill", "gravity": "face"}],
    )
    repo = UsuarioRepository(db)
    user = await repo.update_profile(current_user, current_user.bio, current_user.is_public, avatar_url=result["secure_url"])
    return PerfilOut.model_validate(user)
