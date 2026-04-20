from fastapi import APIRouter, Form, UploadFile

from src.core.dependencies import CurrentActiveUser, DbSession
from src.schemas.imagen import ImagenOut
from src.services import imagen_service

router = APIRouter(prefix="/imagenes", tags=["imagenes"])


@router.get("", response_model=list[ImagenOut])
async def list_imagenes(
    db: DbSession,
    juego: str | None = None,
    tag: str | None = None,
    fecha: str | None = None,
    skip: int = 0,
    limit: int = 20,
):
    return await imagen_service.list_imagenes(db, juego, tag, fecha, skip, limit)


@router.get("/stats")
async def stats(db: DbSession):
    return await imagen_service.get_stats(db)


@router.get("/{imagen_id}", response_model=ImagenOut)
async def get_imagen(imagen_id: int, db: DbSession):
    return await imagen_service.get_imagen(db, imagen_id)


@router.post("", response_model=ImagenOut, status_code=201)
async def upload_imagen(
    db: DbSession,
    user: CurrentActiveUser,
    file: UploadFile,
    titulo: str = Form(...),
    juego: str = Form(...),
    descripcion: str | None = Form(None),
    tags: str | None = Form(None),
):
    return await imagen_service.upload_imagen(db, file, titulo, juego, descripcion, tags, user.id)


@router.delete("/{imagen_id}", status_code=204)
async def delete_imagen(imagen_id: int, db: DbSession, user: CurrentActiveUser):
    await imagen_service.delete_imagen(db, imagen_id, user.id)
