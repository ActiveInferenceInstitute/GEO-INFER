"""
REST API module for OSC-GEO.

This module provides FastAPI routes for interacting with the OSC-GEO functionality.
"""

import logging
import os
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import shutil

from ..core.repos import clone_osc_repos, get_repo_path, OSC_REPOS
from ..core.h3grid import H3GridManager
from ..core.loader import H3DataLoader
from ..main import setup_osc_geo, get_repo_list

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/osc-geo",
    tags=["osc-geo"],
    responses={404: {"description": "Not found"}},
)

# State variables
_grid_manager = None
_data_loader = None

# Dependency functions
def get_grid_manager() -> H3GridManager:
    """Get or create an H3GridManager instance."""
    global _grid_manager
    if _grid_manager is None:
        try:
            _grid_manager = H3GridManager()
        except Exception as e:
            logger.error(f"Failed to create H3GridManager: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize H3 grid manager: {str(e)}"
            )
    return _grid_manager

def get_data_loader() -> H3DataLoader:
    """Get or create an H3DataLoader instance."""
    global _data_loader
    if _data_loader is None:
        try:
            _data_loader = H3DataLoader()
        except Exception as e:
            logger.error(f"Failed to create H3DataLoader: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize H3 data loader: {str(e)}"
            )
    return _data_loader

@router.get("/status")
def get_status() -> Dict[str, Any]:
    """Get the status of OSC-GEO components."""
    # Check repository availability
    repos_status = {}
    for key, info in OSC_REPOS.items():
        repo_path = get_repo_path(key)
        repos_status[key] = {
            "available": repo_path is not None,
            "path": repo_path
        }
    
    # Check if services are running
    grid_service_running = False
    try:
        grid_manager = get_grid_manager()
        grid_service_running = grid_manager.is_server_running()
    except Exception:
        pass
    
    # Compile status information
    return {
        "repositories": repos_status,
        "services": {
            "h3grid_service": {
                "running": grid_service_running
            }
        }
    }

@router.post("/setup")
def setup(
    output_dir: Optional[str] = None,
    github_token: Optional[str] = None
) -> Dict[str, Any]:
    """Set up OSC-GEO by cloning required repositories."""
    try:
        results = setup_osc_geo(output_dir, github_token)
        return {
            "success": all(results.values()),
            "repositories": results
        }
    except Exception as e:
        logger.error(f"Failed to set up OSC-GEO: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set up OSC-GEO: {str(e)}"
        )

@router.get("/repos")
def list_repositories() -> List[Dict[str, str]]:
    """List all OSC-GEO repositories."""
    return get_repo_list()

@router.post("/grid/start")
def start_grid_service(
    port: int = 8000,
    grid_manager: H3GridManager = Depends(get_grid_manager)
) -> Dict[str, Any]:
    """Start the H3 grid service."""
    try:
        success = grid_manager.start_server()
        if success:
            return {
                "success": True,
                "message": f"H3 grid service started on port {port}",
                "url": grid_manager.get_api_url()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to start H3 grid service"
            )
    except Exception as e:
        logger.error(f"Failed to start H3 grid service: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start H3 grid service: {str(e)}"
        )

@router.post("/grid/stop")
def stop_grid_service(
    grid_manager: H3GridManager = Depends(get_grid_manager)
) -> Dict[str, Any]:
    """Stop the H3 grid service."""
    try:
        success = grid_manager.stop_server()
        if success:
            return {
                "success": True,
                "message": "H3 grid service stopped"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to stop H3 grid service"
            )
    except Exception as e:
        logger.error(f"Failed to stop H3 grid service: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop H3 grid service: {str(e)}"
        )

@router.post("/load")
async def load_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    resolution: int = 8,
    format: str = "geojson",
    index_field: Optional[str] = None,
    lat_field: Optional[str] = None,
    lon_field: Optional[str] = None,
    wkt_field: Optional[str] = None,
    data_loader: H3DataLoader = Depends(get_data_loader)
) -> Dict[str, Any]:
    """
    Load geospatial data into an H3 grid system.
    
    This endpoint accepts a data file upload and processes it with the H3 loader,
    returning the processed data in the specified format.
    """
    # Create temporary directory for input/output files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save uploaded file
        input_path = os.path.join(temp_dir, file.filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Define output path
        output_filename = f"{os.path.splitext(file.filename)[0]}_h3_res{resolution}.{format}"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Process the data
        success = data_loader.load_data(
            input_file=input_path,
            output_file=output_path,
            resolution=resolution,
            format=format,
            index_field=index_field,
            lat_field=lat_field,
            lon_field=lon_field,
            wkt_field=wkt_field
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to process data"
            )
        
        # Check if output file was created
        if not os.path.exists(output_path):
            raise HTTPException(
                status_code=500,
                detail="Output file was not created"
            )
        
        # Schedule cleanup
        background_tasks.add_task(shutil.rmtree, temp_dir)
        
        # Return metadata about the processed file
        return {
            "success": True,
            "input_file": file.filename,
            "output_file": output_filename,
            "resolution": resolution,
            "format": format
        }
    except HTTPException:
        # Clean up on HTTP exceptions
        shutil.rmtree(temp_dir)
        raise
    except Exception as e:
        # Clean up on other exceptions
        shutil.rmtree(temp_dir)
        logger.error(f"Failed to process data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process data: {str(e)}"
        )

@router.post("/validate")
async def validate_data(
    file: UploadFile = File(...),
    strict: bool = False,
    data_loader: H3DataLoader = Depends(get_data_loader)
) -> Dict[str, Any]:
    """
    Validate geospatial data for use with the H3 loader.
    
    This endpoint accepts a data file upload and validates it for compatibility
    with H3 grid systems.
    """
    # Create temporary directory for input file
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save uploaded file
        input_path = os.path.join(temp_dir, file.filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Validate the data
        valid, issues = data_loader.validate_data(
            input_file=input_path,
            strict=strict
        )
        
        # Schedule cleanup
        background_tasks = BackgroundTasks()
        background_tasks.add_task(shutil.rmtree, temp_dir)
        
        # Return validation results
        return {
            "valid": valid,
            "issues": issues,
            "input_file": file.filename,
            "strict_validation": strict
        }
    except Exception as e:
        # Clean up on exceptions
        shutil.rmtree(temp_dir)
        logger.error(f"Failed to validate data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate data: {str(e)}"
        ) 