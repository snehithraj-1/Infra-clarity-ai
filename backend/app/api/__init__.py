from fastapi import APIRouter
from app.api.routes_enhance import router as enhance_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_meta import router as meta_router
from app.api.routes_assistant import router as assistant_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(meta_router)
api_v1_router.include_router(enhance_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(assistant_router)

__all__ = ["api_v1_router"]
