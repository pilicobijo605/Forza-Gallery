from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from src.core.dependencies import CurrentActiveUser, DbSession
from src.db.repositories.conversacion_repository import ConversacionRepository
from src.db.repositories.mensaje_repository import MensajeRepository
from src.db.repositories.usuario_repository import UsuarioRepository
from src.schemas.mensaje import ConversacionOut, MensajeCreate, MensajeOut

router = APIRouter(prefix="/mensajes", tags=["mensajes"])


@router.get("/no-leidos")
async def total_no_leidos(db: DbSession, user: CurrentActiveUser):
    conv_repo = ConversacionRepository(db)
    msg_repo = MensajeRepository(db)
    convs = await conv_repo.get_mis_conversaciones(user.id)
    total = sum([await msg_repo.count_no_leidos(c.id, user.id) for c in convs])
    return {"count": total}


@router.get("/conversaciones", response_model=list[ConversacionOut])
async def get_conversaciones(db: DbSession, user: CurrentActiveUser):
    conv_repo = ConversacionRepository(db)
    msg_repo = MensajeRepository(db)
    user_repo = UsuarioRepository(db)
    convs = await conv_repo.get_mis_conversaciones(user.id)
    result = []
    for c in convs:
        otro_id = c.user2_id if c.user1_id == user.id else c.user1_id
        otro = await user_repo.get_by_id(otro_id)
        ultimo = await msg_repo.ultimo_mensaje(c.id)
        no_leidos = await msg_repo.count_no_leidos(c.id, user.id)
        result.append(ConversacionOut(
            id=c.id,
            otro_username=otro.username if otro else "?",
            otro_avatar=otro.avatar_url if otro else None,
            ultimo_mensaje=ultimo.contenido[:60] if ultimo else None,
            ultimo_at=ultimo.created_at if ultimo else None,
            no_leidos=no_leidos,
        ))
    result.sort(key=lambda x: x.ultimo_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return result


@router.get("/{username}", response_model=list[MensajeOut])
async def get_mensajes(username: str, db: DbSession, user: CurrentActiveUser):
    user_repo = UsuarioRepository(db)
    otro = await user_repo.get_by_username(username)
    if not otro:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    conv = await ConversacionRepository(db).get_or_create(user.id, otro.id)
    msg_repo = MensajeRepository(db)
    await msg_repo.marcar_leidos(conv.id, user.id)
    mensajes = await msg_repo.get_mensajes(conv.id)
    return [
        MensajeOut(
            id=m.id,
            conversacion_id=m.conversacion_id,
            autor_id=m.autor_id,
            autor_username=user.username if m.autor_id == user.id else otro.username,
            contenido=m.contenido,
            leido=m.leido,
            created_at=m.created_at,
        )
        for m in mensajes
    ]


@router.post("/{username}", response_model=MensajeOut, status_code=201)
async def enviar_mensaje(username: str, body: MensajeCreate, db: DbSession, user: CurrentActiveUser):
    contenido = body.contenido.strip()
    if not contenido:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El mensaje no puede estar vacío")
    user_repo = UsuarioRepository(db)
    otro = await user_repo.get_by_username(username)
    if not otro:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if otro.id == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No puedes enviarte mensajes a ti mismo")
    conv = await ConversacionRepository(db).get_or_create(user.id, otro.id)
    m = await MensajeRepository(db).crear(conv.id, user.id, contenido)
    return MensajeOut(
        id=m.id,
        conversacion_id=m.conversacion_id,
        autor_id=m.autor_id,
        autor_username=user.username,
        contenido=m.contenido,
        leido=m.leido,
        created_at=m.created_at,
    )
