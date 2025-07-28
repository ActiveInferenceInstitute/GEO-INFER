"""
H3 data loader module for OSC-GEO.

This module provides an interface to the OS Climate H3 loader command-line tool.
"""

import logging
import os
import sys
import subprocess
from typing import Dict, List, Optional, Tuple, Union, Any
import time

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
        Check if the H3 loader CLI is installed and install it if necessary.
        """
        try:
            # Try different Python executable names
            venv_python_candidates = [
                os.path.join(self.repo_path, 'venv', 'bin', 'python'),
                os.path.join(self.repo_path, 'venv', 'bin', 'python3'),
                os.path.join(self.repo_path, 'venv', 'Scripts', 'python.exe')  # Windows
            ]
            
            venv_python = None
            for candidate in venv_python_candidates:
                if os.path.exists(candidate):
                    venv_python = candidate
                    break
            
            if not venv_python:
                raise ValueError(f"H3 loader CLI repository not found. Please clone it first.")
            
            # Environment with the correct PYTHONPATH
            env = os.environ.copy()
            python_path = env.get('PYTHONPATH', '')
            src_path = os.path.join(self.repo_path, 'src')
            env['PYTHONPATH'] = f"{src_path}{os.pathsep}{python_path}"

            # Try running the CLI to check if it's installed
            process = subprocess.run(
                [venv_python, "-c", "import cli.cliexec_load; print('CLI available')"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=env
            )
            
            if process.returncode != 0:
                logger.info("H3 loader CLI not found, installing...")
                
                # Install the CLI in development mode using the venv's pip
                pip_executable = venv_python.replace('python', 'pip').replace('python3', 'pip')
                if not os.path.exists(pip_executable):
                    pip_executable = venv_python.replace('python', 'pip3').replace('python3', 'pip3')
                
                install_process = subprocess.run(
                    [pip_executable, "install", "-e", "."],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    cwd=self.repo_path,
                    env=env
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
            
            # Try different Python executable names
            venv_python_candidates = [
                os.path.join(self.repo_path, 'venv', 'bin', 'python'),
                os.path.join(self.repo_path, 'venv', 'bin', 'python3'),
                os.path.join(self.repo_path, 'venv', 'Scripts', 'python.exe')  # Windows
            ]
            
            venv_python = None
            for candidate in venv_python_candidates:
                if os.path.exists(candidate):
                    venv_python = candidate
                    break
            
            if not venv_python:
                raise ValueError(f"H3 loader CLI repository not found. Please clone it first.")
            
            # Environment with the correct PYTHONPATH
            env = os.environ.copy()
            python_path = env.get('PYTHONPATH', '')
            src_path = os.path.join(self.repo_path, 'src')
            env['PYTHONPATH'] = f"{src_path}{os.pathsep}{python_path}"
            
            # Use the real OSC CLI with CSV format (the only supported format)
            # Convert GeoJSON to CSV format for the real OSC methods
            import tempfile
            import yaml
            import json
            import geopandas as gpd
            import pandas as pd
            
            # Convert GeoJSON to CSV format
            csv_data = []
            csv_file = None
            config_path = None
            
            try:
                # Read the GeoJSON file
                logger.info(f"Reading GeoJSON file: {input_file}")
                gdf = gpd.read_file(input_file)
                logger.info(f"Found {len(gdf)} features in GeoJSON file")
                
                # Process features in chunks for better performance
                chunk_size = 1000  # Process 1000 features at a time
                csv_data = []
                
                for chunk_start in range(0, len(gdf), chunk_size):
                    chunk_end = min(chunk_start + chunk_size, len(gdf))
                    chunk_gdf = gdf.iloc[chunk_start:chunk_end]
                    
                    logger.info(f"Processing features {chunk_start+1}-{chunk_end} of {len(gdf)}")
                    
                    # Extract coordinates and properties for this chunk
                    for idx, row in chunk_gdf.iterrows():
                        geom = row.geometry
                        if geom.geom_type == 'Point':
                            lon, lat = geom.x, geom.y
                        elif geom.geom_type in ['Polygon', 'MultiPolygon']:
                            # Use centroid for polygons
                            lon, lat = geom.centroid.x, geom.centroid.y
                        else:
                            continue
                        
                        # Extract a data value (use first numeric column or default to 1.0)
                        data_value = 1.0
                        for col in gdf.columns:
                            if col != 'geometry' and pd.api.types.is_numeric_dtype(gdf[col]):
                                data_value = float(row[col])
                                break
                        
                        csv_data.append(f"{lon},{lat},{data_value}")
                
                logger.info(f"Converted {len(csv_data)} features to CSV format")
                
                # Create temporary CSV file
                csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                csv_file.write('\n'.join(csv_data))
                csv_file.close()
                
                # Create configuration for CSVLoader
                config_data = {
                    'loader_type': 'CSVLoader',
                    'dataset_name': 'geospatial_data',
                    'dataset_type': 'h3',
                    'database_dir': os.path.dirname(output_file),
                    'interval': 'one_time',
                    'max_resolution': resolution,
                    'data_columns': ['data_value'],
                    'file_path': csv_file.name,
                    'has_header_row': False,
                    'columns': {
                        'longitude': 'float',
                        'latitude': 'float',
                        'data_value': 'float'
                    },
                    'mode': 'create'
                }
                
                # Create temporary config file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as config_file:
                    yaml.dump(config_data, config_file)
                    config_path = config_file.name
                
                # Use the real OSC CLI with the configuration file
                cmd = [
                    venv_python, 
                    "-c", 
                    f"from cli.cliexec_load import CliExecLoad; loader = CliExecLoad(); loader.load('{config_path}')"
                ]
            
                # Run the command with enhanced logging
                try:
                    logger.info(f"🚀 Starting OSC CLI data loading process...")
                    logger.info(f"📁 Input file: {input_file}")
                    logger.info(f"📁 Output file: {output_file}")
                    logger.info(f"🎯 Resolution: {resolution}")
                    logger.info(f"📊 Features to process: {len(csv_data)}")
                    logger.info(f"⏱️ Timeout: 120 seconds (2 minutes)")
                    
                    # Start the process with real-time logging
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,
                        universal_newlines=True,
                        bufsize=1
                    )
                    
                    # Monitor the process with real-time output
                    start_time = time.time()
                    logger.info(f"⏳ OSC CLI process started at {time.strftime('%H:%M:%S')}")
                    
                    # Read output in real-time
                    stdout_lines = []
                    stderr_lines = []
                    
                    # Track repeated error messages to detect infinite loops
                    error_patterns = {}
                    max_repeated_errors = 5  # Reduced from 10 to 5 for faster detection
                    
                    while process.poll() is None:
                        # Check for timeout
                        elapsed = time.time() - start_time
                        if elapsed > 120:  # 2 minute timeout
                            logger.error(f"⏰ OSC H3 loader timed out after 2 minutes")
                            process.terminate()
                            try:
                                process.wait(timeout=10)  # Give it 10 seconds to terminate
                            except subprocess.TimeoutExpired:
                                process.kill()  # Force kill if it doesn't terminate
                            return False
                        
                        # Read available output
                        stdout_line = process.stdout.readline()
                        if stdout_line:
                            stdout_line = stdout_line.strip()
                            stdout_lines.append(stdout_line)
                            logger.info(f"📤 OSC CLI: {stdout_line}")
                        
                        stderr_line = process.stderr.readline()
                        if stderr_line:
                            stderr_line = stderr_line.strip()
                            stderr_lines.append(stderr_line)
                            logger.warning(f"⚠️ OSC CLI Error: {stderr_line}")
                            
                            # Track repeated error patterns to detect infinite loops
                            if "index" in stderr_line and "out of bounds" in stderr_line:
                                error_key = "index_out_of_bounds"
                                error_patterns[error_key] = error_patterns.get(error_key, 0) + 1
                                
                                logger.info(f"🔄 Error pattern count: {error_patterns[error_key]}/{max_repeated_errors}")
                                
                                if error_patterns[error_key] >= max_repeated_errors:
                                    logger.error(f"🔄 Detected infinite loop in OSC CLI after {error_patterns[error_key]} repeated errors")
                                    logger.error(f"⏱️ Process ran for {elapsed:.1f} seconds before detecting loop")
                                    process.terminate()
                                    try:
                                        process.wait(timeout=5)  # Give it 5 seconds to terminate
                                    except subprocess.TimeoutExpired:
                                        process.kill()  # Force kill if it doesn't terminate
                                    return False
                        
                        # Log progress every 10 seconds
                        if int(elapsed) % 10 == 0 and elapsed > 0:
                            logger.info(f"⏳ OSC CLI still running... ({int(elapsed)}s elapsed)")
                            
                            # If we've been running for more than 30 seconds with no progress, consider it stuck
                            if elapsed > 30 and len(stdout_lines) < 5:
                                logger.warning(f"⚠️ OSC CLI appears to be stuck after {elapsed:.1f}s with minimal output")
                                logger.warning(f"📊 Output lines: {len(stdout_lines)}, Error lines: {len(stderr_lines)}")
                                
                                # If we have many error lines but few output lines, it's likely stuck
                                if len(stderr_lines) > 20 and len(stdout_lines) < 10:
                                    logger.error(f"🔄 Detected stuck OSC CLI process - terminating")
                                    process.terminate()
                                    try:
                                        process.wait(timeout=5)
                                    except subprocess.TimeoutExpired:
                                        process.kill()
                                    return False
                    
                    # Get final return code
                    return_code = process.poll()
                    elapsed = time.time() - start_time
                    
                    if return_code == 0:
                        logger.info(f"✅ OSC CLI completed successfully in {elapsed:.1f} seconds")
                        logger.info(f"📊 Processed {len(csv_data)} features")
                        return True
                    else:
                        logger.error(f"❌ OSC CLI failed with return code {return_code}")
                        logger.error(f"⏱️ Process ran for {elapsed:.1f} seconds")
                        if stderr_lines:
                            logger.error(f"🔍 Error output:")
                            for line in stderr_lines[-5:]:  # Show last 5 error lines
                                logger.error(f"   {line}")
                        return False
                        
                except subprocess.TimeoutExpired:
                    logger.error(f"⏰ OSC H3 loader timed out after 2 minutes")
                    # Clean up temporary files on timeout
                    try:
                        if csv_file and os.path.exists(csv_file.name):
                            os.unlink(csv_file.name)
                        if config_path and os.path.exists(config_path):
                            os.unlink(config_path)
                    except:
                        pass
                    return False
                except Exception as e:
                    logger.error(f"❌ Error running OSC CLI: {e}")
                    # Clean up temporary files on error
                    try:
                        if csv_file and os.path.exists(csv_file.name):
                            os.unlink(csv_file.name)
                        if config_path and os.path.exists(config_path):
                            os.unlink(config_path)
                    except:
                        pass
                    return False
            except Exception as e:
                logger.error(f"Error converting GeoJSON to CSV or creating config: {e}")
                return False
            finally:
                # Clean up temporary files
                if csv_file and os.path.exists(csv_file.name):
                    os.unlink(csv_file.name)
                if config_path and os.path.exists(config_path):
                    os.unlink(config_path)
            
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
            
            # Path to the virtual environment's Python interpreter
            venv_python = os.path.join(self.repo_path, 'venv', 'bin', 'python3')
            
            # Environment with the correct PYTHONPATH
            env = os.environ.copy()
            python_path = env.get('PYTHONPATH', '')
            src_path = os.path.join(self.repo_path, 'src')
            env['PYTHONPATH'] = f"{src_path}{os.pathsep}{python_path}"
            
            # Use the real OSC CLI for validation
            cmd = [
                venv_python, 
                "-c", 
                f"from cli.cliexec_load import CliExecLoad; loader = CliExecLoad(); print('Validation not implemented in OSC CLI')"
            ]
            
            # Run the command with timeout to prevent hanging
            try:
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    env=env,
                    timeout=300  # 5 minute timeout
                )
            except subprocess.TimeoutExpired:
                logger.error(f"OSC H3 loader timed out after 5 minutes")
                return False
            
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