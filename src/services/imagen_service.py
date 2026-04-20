import asyncio

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.repositories.imagen_repository import ImagenRepository
from src.db.repositories.tag_repository import TagRepository, parse_tags
from src.schemas.imagen import ImagenOut

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 10 * 1024 * 1024


def _extract_public_id(url: str) -> str:
    part = url.split("/upload/")[-1]
    segments = part.split("/")
    if segments[0].startswith("v") and segments[0][1:].isdigit():
        part = "/".join(segments[1:])
    return part.rsplit(".", 1)[0]


async def list_imagenes(
    db: AsyncSession,
    juego: str | None,
    tag: str | None,
    fecha: str | None,
    usuario: str | None,
    skip: int,
    limit: int,
) -> list[ImagenOut]:
    repo = ImagenRepository(db)
    tag_norm = tag.lower() if tag else None
    return [ImagenOut.model_validate(i) for i in await repo.get_all(juego, tag_norm, fecha, usuario, skip, limit)]


async def get_imagen(db: AsyncSession, imagen_id: int) -> ImagenOut:
    repo = ImagenRepository(db)
    img = await repo.get_by_id(imagen_id)
    if not img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    await repo.increment_visitas(img)
    return ImagenOut.model_validate(img)


async def upload_imagen(
    db: AsyncSession,
    file: UploadFile,
    titulo: str,
    juego: str,
    descripcion: str | None,
    tags_raw: str | None,
    usuario_id: int,
) -> ImagenOut:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato no permitido")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Imagen demasiado grande (máx 10 MB)")

    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        content,
        folder="forzagram",
        resource_type="image",
    )
    image_url = result["secure_url"]

    tag_names = parse_tags(tags_raw) if tags_raw else []
    tag_repo = TagRepository(db)
    tags = await tag_repo.get_or_create_many(tag_names)

    repo = ImagenRepository(db)
    img = await repo.create(titulo, juego, descripcion, image_url, usuario_id, tags)
    return ImagenOut.model_validate(img)


async def update_imagen(
    db: AsyncSession,
    imagen_id: int,
    usuario_id: int,
    titulo: str,
    juego: str,
    descripcion: str | None,
    tags_raw: str,
) -> ImagenOut:
    repo = ImagenRepository(db)
    img = await repo.get_by_id(imagen_id)
    if not img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    if img.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso")

    tag_names = parse_tags(tags_raw) if tags_raw else []
    tags = await TagRepository(db).get_or_create_many(tag_names)

    img = await repo.update(img, titulo, juego, descripcion, tags)
    return ImagenOut.model_validate(img)


async def delete_imagen(db: AsyncSession, imagen_id: int, usuario_id: int) -> None:
    repo = ImagenRepository(db)
    img = await repo.get_by_id(imagen_id)
    if not img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    if img.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso")

    public_id = _extract_public_id(img.filename)
    await asyncio.to_thread(cloudinary.uploader.destroy, public_id)

    await repo.delete(img)


async def get_stats(db: AsyncSession) -> dict:
    repo = ImagenRepository(db)
    by_game = await repo.count_by_juego()
    total = sum(by_game.values())
    return {"total": total, "por_juego": by_game}
