"""
Health check endpoints for the GEO-INFER-API.
"""
from fastapi import APIRouter, Depends

from geo_infer_api.core.config import get_settings, Settings

# Create router
router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Simple health check endpoint.
    
    Returns:
        dict: Status information about the API
    """
    return {
        "status": "ok",
        "version": settings.app_version,
        "name": settings.app_name
    }


@router.get("/health/detailed", summary="Detailed health check")
async def detailed_health_check(settings: Settings = Depends(get_settings)):
    """
    Detailed health check with component status information.
    
    Returns:
        dict: Detailed status information about the API and its components
    """
    # In a real application, this would check database connections,
    # external service availability, etc.
    
    return {
        "status": "ok",
        "version": settings.app_version,
        "components": {
            "database": {"status": "ok"},
            "geojson_service": {"status": "ok"},
            "memory_usage": {"status": "ok", "value": "50MB"},
            "uptime": {"status": "ok", "value": "12h 30m"}
        },
        "environment": "development"
    } 