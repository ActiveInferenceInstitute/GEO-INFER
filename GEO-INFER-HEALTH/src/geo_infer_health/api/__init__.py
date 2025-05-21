# API endpoints for GEO-INFER-HEALTH 

from fastapi import APIRouter

from . import api_disease_surveillance
from . import api_healthcare_accessibility
from . import api_environmental_health

router = APIRouter()

router.include_router(api_disease_surveillance.router)
router.include_router(api_healthcare_accessibility.router)
router.include_router(api_environmental_health.router)

__all__ = ["router"] 