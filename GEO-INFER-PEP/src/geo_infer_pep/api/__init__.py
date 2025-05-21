# API endpoints for GEO-INFER-PEP
from fastapi import APIRouter

from .crm_endpoints import router as crm_router
from .hr_endpoints import router as hr_router
from .talent_endpoints import router as talent_router

# You can create a main API router here that includes all module-specific routers
api_router = APIRouter(prefix="/pep")

api_router.include_router(crm_router)
api_router.include_router(hr_router)
api_router.include_router(talent_router)

__all__ = ["api_router"]

