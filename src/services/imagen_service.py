import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.imagen_repository import ImagenRepository
from src.db.repositories.tag_repository import TagRepository, parse_tags
from src.schemas.imagen import ImagenOut

UPLOADS_DIR = Path("static/uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


async def list_imagenes(
    db: AsyncSession,
    juego: str | None,
    tag: str | None,
    skip: int,
    limit: int,
) -> list[ImagenOut]:
    repo = ImagenRepository(db)
    tag_norm = tag.lower() if tag else None
    return [ImagenOut.model_validate(i) for i in await repo.get_all(juego, tag_norm, skip, limit)]


async def get_imagen(db: AsyncSession, imagen_id: int) -> ImagenOut:
    repo = ImagenRepository(db)
    img = await repo.get_by_id(imagen_id)
    if not img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
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

    ext = Path(file.filename or "imagen.jpg").suffix.lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOADS_DIR / filename).write_bytes(content)

    tag_names = parse_tags(tags_raw) if tags_raw else []
    tag_repo = TagRepository(db)
    tags = await tag_repo.get_or_create_many(tag_names)

    repo = ImagenRepository(db)
    img = await repo.create(titulo, juego, descripcion, filename, usuario_id, tags)
    return ImagenOut.model_validate(img)


async def delete_imagen(db: AsyncSession, imagen_id: int, usuario_id: int) -> None:
    repo = ImagenRepository(db)
    img = await repo.get_by_id(imagen_id)
    if not img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    if img.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso")

    filepath = UPLOADS_DIR / img.filename
    if filepath.exists():
        filepath.unlink()

    await repo.delete(img)


async def get_stats(db: AsyncSession) -> dict:
    repo = ImagenRepository(db)
    by_game = await repo.count_by_juego()
    total = sum(by_game.values())
    return {"total": total, "por_juego": by_game}
