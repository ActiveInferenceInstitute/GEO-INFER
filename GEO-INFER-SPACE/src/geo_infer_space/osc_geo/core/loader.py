"""
H3 data loader module for OSC-GEO.

This module provides an interface to the OS Climate H3 loader command-line tool.
"""

import logging
import os
import sys
import subprocess
from typing import Dict, List, Optional, Tuple, Union, Any

from ..core.repos import get_repo_path

logger = logging.getLogger(__name__)

class H3DataLoader:
    """
    Manager for interacting with OS Climate H3 loader CLI.
    
    This class provides an interface to the H3 loader command-line tool for
    loading data into H3 grid systems.
    """
    
    def __init__(
        self,
        repo_base_dir: Optional[str] = None,
    ):
        """
        Initialize the H3 data loader.
        
        Args:
            repo_base_dir: Base directory for cloned repositories. If None,
                uses the default from GEO-INFER-GIT.
        """
        self.repo_path = get_repo_path("h3loader-cli", repo_base_dir)
        if not self.repo_path:
            raise ValueError("H3 loader CLI repository not found. Please clone it first.")
        
        # Ensure the loader CLI is installed
        self._check_loader_installation()
    
    def _check_loader_installation(self) -> None:
        """
        Check if the H3 loader CLI is installed, and install it if not.
        """
        try:
            # Change to the repository directory
            os.chdir(self.repo_path)
            
            # Try running the CLI to check if it's installed
            process = subprocess.run(
                ["osc-geo-h3loader", "--help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if process.returncode != 0:
                logger.info("H3 loader CLI not found, installing...")
                
                # Install the CLI in development mode
                install_process = subprocess.run(
                    ["pip", "install", "-e", "."],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False
                )
                
                if install_process.returncode != 0:
                    stderr = install_process.stderr.decode()
                    logger.error(f"Failed to install H3 loader CLI: {stderr}")
                    raise RuntimeError(f"Failed to install H3 loader CLI: {stderr}")
                
                logger.info("H3 loader CLI installed successfully")
        except Exception as e:
            logger.error(f"Error checking/installing H3 loader CLI: {e}")
            raise
    
    def load_data(
        self,
        input_file: str,
        output_file: str,
        resolution: int = 8,
        format: str = "geojson",
        index_field: Optional[str] = None,
        lat_field: Optional[str] = None,
        lon_field: Optional[str] = None,
        wkt_field: Optional[str] = None,
        driver: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Load geospatial data into an H3 grid system.
        
        Args:
            input_file: Path to input file.
            output_file: Path to output file.
            resolution: H3 resolution (0-15).
            format: Output format (geojson, shapefile, etc.).
            index_field: Name of index field in input data.
            lat_field: Name of latitude field in input data.
            lon_field: Name of longitude field in input data.
            wkt_field: Name of WKT field in input data.
            driver: GDAL driver to use.
            **kwargs: Additional arguments to pass to the loader CLI.
            
        Returns:
            True if the data was loaded successfully, False otherwise.
        """
        try:
            logger.info(f"Loading data from {input_file} to {output_file} at H3 resolution {resolution}")
            
            # Build command
            cmd = ["osc-geo-h3loader"]
            
            # Add common arguments
            cmd.extend(["--input", input_file])
            cmd.extend(["--output", output_file])
            cmd.extend(["--resolution", str(resolution)])
            cmd.extend(["--format", format])
            
            # Add optional arguments
            if index_field:
                cmd.extend(["--index-field", index_field])
            
            if lat_field:
                cmd.extend(["--lat-field", lat_field])
            
            if lon_field:
                cmd.extend(["--lon-field", lon_field])
                
            if wkt_field:
                cmd.extend(["--wkt-field", wkt_field])
                
            if driver:
                cmd.extend(["--driver", driver])
            
            # Add any additional arguments
            for key, value in kwargs.items():
                key = key.replace("_", "-")
                if isinstance(value, bool):
                    if value:
                        cmd.append(f"--{key}")
                else:
                    cmd.extend([f"--{key}", str(value)])
            
            # Run the command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if process.returncode != 0:
                stderr = process.stderr.decode()
                logger.error(f"Failed to load data: {stderr}")
                return False
            
            logger.info(f"Successfully loaded data to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def validate_data(
        self,
        input_file: str,
        strict: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate geospatial data for use with the H3 loader.
        
        Args:
            input_file: Path to input file.
            strict: Whether to perform strict validation.
            
        Returns:
            Tuple of (validation_passed, list_of_issues).
        """
        try:
            logger.info(f"Validating data file: {input_file}")
            
            # Build command
            cmd = ["osc-geo-h3loader", "--validate", "--input", input_file]
            
            if strict:
                cmd.append("--strict")
            
            # Run the command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            # Parse output
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()
            
            # Check validation result
            if process.returncode == 0:
                logger.info(f"Validation passed for {input_file}")
                return True, []
            else:
                # Extract issues from output
                issues = []
                for line in stderr.split("\n"):
                    if line.strip() and "ERROR" in line:
                        issues.append(line.strip())
                
                logger.warning(f"Validation failed for {input_file} with {len(issues)} issues")
                return False, issues
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return False, [str(e)] 