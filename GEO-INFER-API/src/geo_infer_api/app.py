"""
Main application entry point for GEO-INFER-API.
"""
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles

from geo_infer_api.core.config import get_settings
from geo_infer_api.endpoints import geojson_router, health_router

# Create FastAPI app
settings = get_settings()
main_app = FastAPI(
    title=settings.app_name,
    description="GEO-INFER API - Standardized Interfaces for Geospatial Interoperability",
    version=settings.app_version,
    docs_url=None,
    redoc_url=None,
)

# Configure CORS
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
main_app.include_router(health_router.router, tags=["Health"])
main_app.include_router(geojson_router.router, prefix="/api/v1", tags=["GeoJSON"])

# Custom documentation endpoints
@main_app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=main_app.openapi_url,
        title=f"{main_app.title} - Swagger UI",
        oauth2_redirect_url=main_app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@main_app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=main_app.openapi_url,
        title=f"{main_app.title} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

# For serving static files (docs, etc.)
if os.path.exists("static"):
    main_app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("geo_infer_api.app:main_app", host="0.0.0.0", port=8000, reload=True) 