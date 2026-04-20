from fastapi import APIRouter

from src.api.v1 import auth, health, imagenes, usuarios

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(auth.router)
router.include_router(imagenes.router)
router.include_router(usuarios.router)
