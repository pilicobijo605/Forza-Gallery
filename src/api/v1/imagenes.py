from fastapi import APIRouter, Form, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.dependencies import CurrentActiveUser, DbSession
from src.schemas.imagen import ImagenOut, ImagenUpdate
from src.services import imagen_service

router = APIRouter(prefix="/imagenes", tags=["imagenes"])
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=list[ImagenOut])
async def list_imagenes(
    db: DbSession,
    juego: str | None = None,
    tag: str | None = None,
    fecha: str | None = None,
    usuario: str | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 20,
):
    return await imagen_service.list_imagenes(db, juego, tag, fecha, usuario, q, skip, limit)


@router.get("/stats")
async def stats(db: DbSession):
    return await imagen_service.get_stats(db)


@router.get("/trending", response_model=list[ImagenOut])
async def get_trending(db: DbSession, limit: int = 10):
    return await imagen_service.get_trending(db, limit)


@router.get("/{imagen_id}", response_model=ImagenOut)
async def get_imagen(imagen_id: int, db: DbSession):
    return await imagen_service.get_imagen(db, imagen_id)


@router.post("", response_model=ImagenOut, status_code=201)
@limiter.limit("10/minute")
async def upload_imagen(
    request: Request,
    db: DbSession,
    user: CurrentActiveUser,
    file: UploadFile,
    titulo: str = Form(...),
    juego: str = Form(...),
    descripcion: str | None = Form(None),
    tags: str | None = Form(None),
):
    return await imagen_service.upload_imagen(db, file, titulo, juego, descripcion, tags, user.id)


@router.put("/{imagen_id}", response_model=ImagenOut)
async def update_imagen(imagen_id: int, body: ImagenUpdate, db: DbSession, user: CurrentActiveUser):
    return await imagen_service.update_imagen(
        db, imagen_id, user.id, body.titulo, body.juego, body.descripcion, body.tags
    )


@router.delete("/{imagen_id}", status_code=204)
async def delete_imagen(imagen_id: int, db: DbSession, user: CurrentActiveUser):
    await imagen_service.delete_imagen(db, imagen_id, user.id)
