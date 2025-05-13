"""
Main application entry point for GEO-INFER-OPS.

This module initializes the FastAPI application, sets up logging,
and configures all routes and middleware.
"""

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from geo_infer_ops.utils import load_config, configure_logging, get_logger

# Initialize logger
logger = get_logger("geo_infer_ops.app")

def create_app():
    """Create and configure the FastAPI application."""
    # Load configuration
    try:
        config = load_config()
        # Configure logging based on config
        configure_logging(
            log_level=config["logging"]["level"],
            json_format=config["logging"]["format"] == "json",
            log_file=config["logging"]["file"]
        )
    except Exception as e:
        # Fall back to default logging if config fails
        configure_logging()
        logger.error("Failed to load configuration", error=str(e))
        config = {
            "service": {"host": "0.0.0.0", "port": 8000},
            "security": {"cors_origins": []},
            "monitoring": {"enabled": True, "metrics_path": "/metrics"}
        }

    # Create FastAPI app
    app = FastAPI(
        title="GEO-INFER-OPS",
        description="Operational kernel for system orchestration, logging, testing, and architecture",
        version="0.1.0"
    )

    # Configure CORS
    origins = config["security"].get("cors_origins", [])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add Prometheus metrics endpoint
    if config["monitoring"].get("enabled", False):
        metrics_app = make_asgi_app()
        app.mount(config["monitoring"]["metrics_path"], metrics_app)

    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    # Version endpoint
    @app.get("/version")
    def version():
        from geo_infer_ops import __version__
        return {"version": __version__}

    return app, config

app, config = create_app()

if __name__ == "__main__":
    """Run the application when executed as a script."""
    logger.info(
        "Starting GEO-INFER-OPS",
        host=config["service"]["host"],
        port=config["service"]["port"]
    )
    
    uvicorn.run(
        "geo_infer_ops.app:app",
        host=config["service"]["host"],
        port=config["service"]["port"],
        reload=config["development"].get("hot_reload", False),
    ) 