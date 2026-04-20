from fastapi import APIRouter, HTTPException, status

from src.core.dependencies import CurrentActiveUser, DbSession, OptionalUser
from src.core.moderation import contains_profanity
from src.db.repositories.comentario_repository import ComentarioRepository
from src.db.repositories.guardado_repository import GuardadoRepository
from src.db.repositories.imagen_repository import ImagenRepository
from src.db.repositories.like_repository import LikeRepository
from src.db.repositories.reaccion_repository import ReaccionRepository
from src.models.reaccion import ALLOWED_EMOJIS
from src.schemas.imagen import ImagenOut
from src.schemas.social import ComentarioCreate, ComentarioOut, LikeInfo, ReaccionCreate, ReporteCreate

router = APIRouter(prefix="/social", tags=["social"])


@router.post("/imagenes/{imagen_id}/like")
async def toggle_like(imagen_id: int, db: DbSession, user: CurrentActiveUser):
    if not await ImagenRepository(db).get_by_id(imagen_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Imagen no encontrada")
    repo = LikeRepository(db)
    liked = await repo.toggle(user.id, imagen_id)
    count = await repo.count(imagen_id)
    return {"liked": liked, "count": count}


@router.get("/imagenes/{imagen_id}/likes", response_model=LikeInfo)
async def get_likes(imagen_id: int, db: DbSession, user: OptionalUser):
    repo = LikeRepository(db)
    count = await repo.count(imagen_id)
    liked = bool(user and await repo.get(user.id, imagen_id))
    usernames = await repo.usernames(imagen_id)
    return LikeInfo(count=count, liked=liked, usernames=usernames)


@router.post("/imagenes/{imagen_id}/guardar")
async def toggle_guardado(imagen_id: int, db: DbSession, user: CurrentActiveUser):
    if not await ImagenRepository(db).get_by_id(imagen_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Imagen no encontrada")
    guardado = await GuardadoRepository(db).toggle(user.id, imagen_id)
    return {"guardado": guardado}


@router.get("/mis-guardados", response_model=list[ImagenOut])
async def mis_guardados(db: DbSession, user: CurrentActiveUser):
    imagenes = await GuardadoRepository(db).get_imagenes_guardadas(user.id)
    return [ImagenOut.model_validate(img) for img in imagenes]


@router.get("/imagenes/{imagen_id}/comentarios", response_model=list[ComentarioOut])
async def get_comentarios(imagen_id: int, db: DbSession, user: OptionalUser):
    comentarios = await ComentarioRepository(db).get_by_imagen(imagen_id)
    reaccion_repo = ReaccionRepository(db)
    result = []
    for c in comentarios:
        reacciones = await reaccion_repo.get_counts(c.id)
        mi_reaccion = await reaccion_repo.get_user_reaccion(c.id, user.id) if user else None
        result.append(ComentarioOut(
            id=c.id,
            imagen_id=c.imagen_id,
            usuario_id=c.usuario_id,
            username=c.usuario.username if c.usuario else "",
            contenido=c.contenido,
            created_at=c.created_at,
            reacciones=reacciones,
            mi_reaccion=mi_reaccion,
        ))
    return result


@router.post("/imagenes/{imagen_id}/comentarios", response_model=ComentarioOut, status_code=201)
async def add_comentario(imagen_id: int, body: ComentarioCreate, db: DbSession, user: CurrentActiveUser):
    contenido = body.contenido.strip()
    if not contenido:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El comentario no puede estar vacío")
    if contains_profanity(contenido):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El comentario contiene palabras no permitidas")
    if not await ImagenRepository(db).get_by_id(imagen_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Imagen no encontrada")
    c = await ComentarioRepository(db).create(imagen_id, user.id, contenido)
    return ComentarioOut(
        id=c.id,
        imagen_id=c.imagen_id,
        usuario_id=c.usuario_id,
        username=c.usuario.username if c.usuario else "",
        contenido=c.contenido,
        created_at=c.created_at,
    )


@router.delete("/comentarios/{comentario_id}", status_code=204)
async def delete_comentario(comentario_id: int, db: DbSession, user: CurrentActiveUser):
    repo = ComentarioRepository(db)
    c = await repo.get_by_id(comentario_id)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comentario no encontrado")
    if c.usuario_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No puedes eliminar este comentario")
    await repo.delete(c)


@router.post("/comentarios/{comentario_id}/reaccionar")
async def reaccionar(comentario_id: int, body: ReaccionCreate, db: DbSession, user: CurrentActiveUser):
    if body.emoji not in ALLOWED_EMOJIS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Emoji no permitido")
    if not await ComentarioRepository(db).get_by_id(comentario_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comentario no encontrado")
    repo = ReaccionRepository(db)
    mi_reaccion = await repo.toggle(comentario_id, user.id, body.emoji)
    reacciones = await repo.get_counts(comentario_id)
    return {"mi_reaccion": mi_reaccion, "reacciones": reacciones}


@router.post("/comentarios/{comentario_id}/reportar", status_code=204)
async def reportar_comentario(comentario_id: int, body: ReporteCreate, db: DbSession, user: CurrentActiveUser):
    repo = ComentarioRepository(db)
    c = await repo.get_by_id(comentario_id)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comentario no encontrado")
    if await repo.ya_reportado(comentario_id, user.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya has reportado este comentario")
    await repo.reportar(comentario_id, user.id, body.motivo)
