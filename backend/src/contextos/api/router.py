from fastapi import APIRouter

from contextos.api.routes.admin import router as admin_router
from contextos.api.routes.documents import router as documents_router
from contextos.api.routes.me import router as me_router
from contextos.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(me_router)
api_router.include_router(documents_router)
api_router.include_router(admin_router)
