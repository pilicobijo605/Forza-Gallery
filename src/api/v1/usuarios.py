import asyncio

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, UploadFile, File, status

from src.core.dependencies import CurrentActiveUser, DbSession, OptionalUser
from src.db.repositories.usuario_repository import UsuarioRepository
from src.db.repositories.seguidor_repository import SeguidorRepository
from src.db.repositories.favorito_usuario_repository import FavoritoUsuarioRepository
from src.schemas.usuario import PerfilOut, PerfilUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


@router.get("/{username}", response_model=PerfilOut)
async def get_perfil(username: str, db: DbSession, viewer: OptionalUser):
    repo = UsuarioRepository(db)
    user = await repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if user.is_public is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Este perfil es privado")
    seg_repo = SeguidorRepository(db)
    fav_repo = FavoritoUsuarioRepository(db)
    try:
        seguidores  = await seg_repo.count_seguidores(user.id)
        siguiendo   = await seg_repo.count_siguiendo(user.id)
        yo_sigo     = await seg_repo.is_siguiendo(viewer.id, user.id) if viewer else False
        es_favorito = await fav_repo.is_favorito(viewer.id, user.id) if viewer else False
    except Exception:
        seguidores = siguiendo = 0
        yo_sigo = es_favorito = False
    return PerfilOut(
        username=user.username,
        bio=user.bio,
        avatar_url=user.avatar_url,
        is_public=user.is_public if user.is_public is not None else True,
        created_at=user.created_at,
        seguidores=seguidores,
        siguiendo=siguiendo,
        yo_sigo=yo_sigo,
        es_favorito=es_favorito,
    )


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
