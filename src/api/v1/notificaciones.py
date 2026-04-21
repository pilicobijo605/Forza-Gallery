from fastapi import APIRouter

from src.core.dependencies import CurrentActiveUser, DbSession
from src.db.repositories.notificacion_repository import NotificacionRepository
from src.schemas.notificacion import NotificacionOut

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.get("", response_model=list[NotificacionOut])
async def get_notificaciones(db: DbSession, user: CurrentActiveUser):
    return await NotificacionRepository(db).get_mis_notificaciones(user.id)


@router.get("/no-leidas")
async def count_no_leidas(db: DbSession, user: CurrentActiveUser):
    return {"count": await NotificacionRepository(db).count_no_leidas(user.id)}


@router.post("/leer-todas", status_code=204)
async def leer_todas(db: DbSession, user: CurrentActiveUser):
    await NotificacionRepository(db).marcar_todas_leidas(user.id)
