"""
H3 grid management module for OSC-GEO.

This module provides an interface to the OS Climate H3 grid service.
"""

import logging
import os
import sys
import subprocess
from typing import Dict, List, Optional, Tuple, Union, Any

from ..core.repos import get_repo_path

logger = logging.getLogger(__name__)

class H3GridManager:
    """
    Manager for interacting with OS Climate H3 grid service.
    
    This class provides an interface to the H3 grid service, including
    grid generation, visualization, and analysis capabilities.
    """
    
    def __init__(
        self,
        repo_base_dir: Optional[str] = None,
        server_port: int = 8000,
        auto_start: bool = False
    ):
        """
        Initialize the H3 grid manager.
        
        Args:
            repo_base_dir: Base directory for cloned repositories. If None,
                uses the default from GEO-INFER-GIT.
            server_port: Port for the H3 grid service.
            auto_start: Whether to automatically start the service.
        """
        self.repo_path = get_repo_path("h3grid-srv", repo_base_dir)
        if not self.repo_path:
            raise ValueError("H3 grid service repository not found. Please clone it first.")
        
        self.server_port = server_port
        self.server_process = None
        
        if auto_start:
            self.start_server()
    
    def start_server(self) -> bool:
        """
        Start the H3 grid service.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        if self.server_process and self.server_process.poll() is None:
            logger.warning("H3 grid service is already running")
            return True
        
        try:
            logger.info(f"Starting H3 grid service on port {self.server_port}")
            
            # Change to the repository directory
            os.chdir(self.repo_path)
            
            # Start the server as a subprocess
            self.server_process = subprocess.Popen(
                [
                    "python", "-m", "uvicorn", 
                    "osc_geo_h3grid_srv.main:app", 
                    "--host", "0.0.0.0", 
                    "--port", str(self.server_port)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check if the server started successfully
            # Wait a bit for the server to start
            import time
            time.sleep(1)
            
            if self.server_process.poll() is None:
                logger.info("H3 grid service started successfully")
                return True
            else:
                stderr = self.server_process.stderr.read().decode()
                logger.error(f"Failed to start H3 grid service: {stderr}")
                return False
        except Exception as e:
            logger.error(f"Error starting H3 grid service: {e}")
            return False
    
    def stop_server(self) -> bool:
        """
        Stop the H3 grid service.
        
        Returns:
            True if the server was stopped successfully, False otherwise.
        """
        if not self.server_process:
            logger.warning("H3 grid service is not running")
            return True
        
        try:
            logger.info("Stopping H3 grid service")
            self.server_process.terminate()
            
            # Wait for the process to terminate
            self.server_process.wait(timeout=5)
            
            if self.server_process.poll() is None:
                # Force kill if it didn't terminate
                logger.warning("H3 grid service did not terminate gracefully, forcing kill")
                self.server_process.kill()
                self.server_process.wait(timeout=5)
            
            self.server_process = None
            logger.info("H3 grid service stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Error stopping H3 grid service: {e}")
            return False
    
    def is_server_running(self) -> bool:
        """
        Check if the H3 grid service is running.
        
        Returns:
            True if the server is running, False otherwise.
        """
        return self.server_process is not None and self.server_process.poll() is None
    
    def get_api_url(self) -> str:
        """
        Get the base URL for the H3 grid service API.
        
        Returns:
            URL string for the H3 grid service API.
        """
        return f"http://localhost:{self.server_port}"
    
    def __del__(self):
        """Cleanup method to ensure server is stopped when object is destroyed."""
        self.stop_server()
    
    def __enter__(self):
        """Context manager entry point."""
        if not self.is_server_running():
            self.start_server()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.stop_server() 