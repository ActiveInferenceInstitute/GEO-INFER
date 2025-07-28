#!/usr/bin/env python3
"""
Base Analysis Module for GEO-INFER-SPACE

This module provides the foundational class for all analysis modules
in the GEO-INFER-SPACE framework, implementing standardized workflows
for data acquisition, processing, and analysis with H3 spatial indexing.
"""

import logging
import json
import numpy as np
import h3
import time
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import geopandas as gpd
from shapely.geometry import shape
import os

# A forward declaration for type hinting the backend without circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geo_infer_space.core.unified_backend import UnifiedH3Backend

logger = logging.getLogger(__name__)

class BaseAnalysisModule(ABC):
    """
    Abstract Base Class for a GEO-INFER analysis module.
    
    Each subclass is responsible for a specific data domain (e.g., Zoning, Water Rights).
    The base class provides a standardized workflow:
    1.  Check for cached H3-processed data.
    2.  If not found, acquire raw data from source.
    3.  Process raw data into H3 using the backend's OSC H3 loader.
    4.  Cache the H3 data.
    5.  Load and perform final analysis on the H3 data.
    """
    def __init__(self, backend: 'UnifiedH3Backend', module_name: str):
        """
        Initialize the module.
        
        Args:
            backend: A reference to the main UnifiedH3Backend instance.
            module_name: The name of the module (e.g., 'zoning').
        """
        self.backend = backend
        self.module_name = module_name
        self.resolution = backend.resolution
        self.target_hexagons = backend.target_hexagons
        
        # Define standardized data paths
        self.data_dir = Path(self.backend.base_data_dir) / self.module_name
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.h3_cache_path = self.data_dir / f'{self.module_name}_h3_res{self.resolution}.json'

    @abstractmethod
    def acquire_raw_data(self) -> Path:
        """
        Acquires raw data from its source (API, file download, etc.).
        
        This method must implement caching for the raw data file itself, i.e.,
        it should check if the raw file exists before re-downloading it.
        
        Returns:
            The file path to the acquired raw data.
        """
        pass

    def process_to_h3(self, raw_data_path: Path) -> dict:
        """
        Processes a raw data file (e.g., GeoJSON, Shapefile) into an H3-indexed dictionary.
        
        This method uses direct H3 processing instead of the buggy OSC CLI.
        
        Args:
            raw_data_path: Path to the raw geospatial data file.
            
        Returns:
            A dictionary of H3-indexed data.
        """
        try:
            logger.info(f"[{self.module_name}] 🔄 Using direct H3 processing for {raw_data_path}")
            
            # Skip the buggy OSC CLI entirely and use direct H3 processing
            start_time = time.time()
            h3_data = self._direct_h3_processing(raw_data_path)
            processing_time = time.time() - start_time
            
            if h3_data:
                logger.info(f"[{self.module_name}] ✅ Direct H3 processing completed successfully in {processing_time:.1f}s")
                logger.info(f"[{self.module_name}] 🎯 Generated {len(h3_data)} H3 cells")
            else:
                logger.error(f"[{self.module_name}] ❌ Direct H3 processing failed")
            
            return h3_data
            
        except Exception as e:
            logger.error(f"[{self.module_name}] ❌ H3 processing failed: {e}")
            return {}

    def _clear_osc_database_files(self):
        """Clear OSC database files to prevent conflicts."""
        try:
            # Remove any existing DuckDB files that might cause conflicts
            for db_file in self.data_dir.glob("*.duckdb"):
                logger.info(f"[{self.module_name}] Removing existing OSC database file: {db_file}")
                db_file.unlink()
            
            # Also remove any geospatial_data files
            for data_file in self.data_dir.glob("geospatial_data*"):
                logger.info(f"[{self.module_name}] Removing existing data file: {data_file}")
                data_file.unlink()
                
        except Exception as e:
            logger.warning(f"[{self.module_name}] Warning: Could not clear OSC database files: {e}")

    def _direct_h3_processing(self, raw_data_path: Path) -> dict:
        """
        Process raw data directly to H3 format using H3 v4 API.
        
        Args:
            raw_data_path: Path to the raw data file (GeoJSON)
            
        Returns:
            Dictionary with H3-indexed data
        """
        try:
            logger.info(f"[{self.module_name}] 🔄 Using direct H3 processing for {raw_data_path}")
            logger.info(f"[{self.module_name}] 🔄 Starting direct H3 processing for {raw_data_path}")
            
            # Load GeoJSON data
            logger.info(f"[{self.module_name}] 📁 Loading GeoJSON data...")
            gdf = gpd.read_file(raw_data_path)
            logger.info(f"[{self.module_name}] 📊 Loaded {len(gdf)} features for direct processing")
            
            # Initialize H3 data storage
            h3_data = {}
            processed_features = 0
            failed_features = 0
            
            logger.info(f"[{self.module_name}] 🔄 Processing features...")
            
            for idx, row in gdf.iterrows():
                try:
                    # Get the geometry - this should already be a shapely geometry from geopandas
                    geom = row.geometry
                    
                    # Ensure we have a shapely geometry
                    if hasattr(geom, 'geom_type'):
                        # It's already a shapely geometry
                        shapely_geom = geom
                    elif isinstance(geom, dict):
                        # Convert from GeoJSON dict to shapely
                        shapely_geom = shape(geom)
                    else:
                        logger.warning(f"[{self.module_name}] ⚠️ Unrecognized geometry type: {type(geom)} for feature {idx}")
                        failed_features += 1
                        continue
                    
                    # Handle different geometry types
                    if shapely_geom.geom_type == 'Point':
                        # Buffer points to create small polygons
                        shapely_geom = shapely_geom.buffer(0.001)
                        logger.info(f"[{self.module_name}] 🔄 Buffered Point to Polygon for feature {idx}")
                    
                    if shapely_geom.geom_type == 'Polygon':
                        # Convert polygon to H3 cells using H3 v4 API
                        # Extract coordinates from shapely polygon
                        coords = list(shapely_geom.exterior.coords)
                        # Remove the last coordinate if it's the same as the first (closing point)
                        if coords[0] == coords[-1]:
                            coords = coords[:-1]
                        
                        # Validate coordinates
                        if len(coords) < 3:
                            logger.warning(f"[{self.module_name}] ⚠️ Invalid polygon (less than 3 points) for feature {idx}")
                            failed_features += 1
                            continue
                        
                        # Convert to the format expected by H3 v4 polygon_to_cells
                        # H3 v4 expects a list of [lat, lng] pairs
                        # Shapely stores as [lng, lat], so we need to swap
                        h3_coords = [[lat, lng] for lng, lat in coords]
                        
                        # Validate coordinate ranges
                        valid_coords = True
                        for lat, lng in h3_coords:
                            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                                logger.warning(f"[{self.module_name}] ⚠️ Invalid coordinates [{lat}, {lng}] for feature {idx}")
                                valid_coords = False
                                break
                        
                        if not valid_coords:
                            failed_features += 1
                            continue
                        
                        try:
                            h3_cells = h3.polygon_to_cells(h3_coords, self.resolution)
                            
                            # Add properties to each H3 cell
                            properties = {}
                            for col in row.index:
                                if col != 'geometry':
                                    value = row[col]
                                    # Convert to serializable types
                                    if isinstance(value, (np.integer, np.floating)):
                                        properties[col] = int(value) if isinstance(value, np.integer) else float(value)
                                    elif isinstance(value, (int, float, str, bool)):
                                        properties[col] = value
                                    else:
                                        properties[col] = str(value)
                            
                            # Add to H3 data
                            for h3_cell in h3_cells:
                                if h3_cell not in h3_data:
                                    h3_data[h3_cell] = {}
                                h3_data[h3_cell].update(properties)
                            
                            processed_features += 1
                            
                        except Exception as h3_error:
                            logger.warning(f"[{self.module_name}] ⚠️ H3 conversion failed for feature {idx}: {h3_error}")
                            failed_features += 1
                        
                    else:
                        logger.warning(f"[{self.module_name}] ⚠️ Unsupported geometry type: {shapely_geom.geom_type} for feature {idx}")
                        failed_features += 1
                        
                except Exception as e:
                    logger.warning(f"[{self.module_name}] ⚠️ Failed to process feature {idx}: {e}")
                    failed_features += 1
            
            logger.info(f"[{self.module_name}] ✅ Direct processing completed:")
            logger.info(f"[{self.module_name}]   📊 Processed features: {processed_features}")
            logger.info(f"[{self.module_name}]   ❌ Failed features: {failed_features}")
            logger.info(f"[{self.module_name}]   🎯 H3 cells generated: {len(h3_data)}")
            
            if not h3_data:
                logger.error(f"[{self.module_name}] ❌ Direct H3 processing failed")
                return {}
            
            return {'h3_data': h3_data}
            
        except Exception as e:
            logger.error(f"[{self.module_name}] ❌ Error in direct H3 processing: {e}")
            return {}

    @abstractmethod
    def run_final_analysis(self, h3_data: dict) -> dict:
        """
        Performs the final, module-specific analysis on H3-indexed data.
        
        Args:
            h3_data: The H3-indexed data, loaded from cache or freshly processed.
            
        Returns:
            A dictionary of H3 hexagons with the final analysis results.
        """
        pass

    def run_analysis(self) -> dict:
        """
        Executes the full, standardized workflow for the module with real data tracking.
        
        This method orchestrates the caching, acquisition, and processing steps with detailed logging.
        
        Returns:
            The final H3-indexed analysis results for this module.
        """
        logger.info(f"[{self.module_name}] 🚀 Starting real data analysis workflow...")
        
        # Track data processing statistics
        analysis_stats = {
            'cached_data_used': False,
            'raw_data_acquired': False,
            'h3_data_processed': 0,
            'final_analysis_completed': False,
            'errors': []
        }
        
        try:
            # 1. Check for cached H3 data
            if self.h3_cache_path.exists():
                logger.info(f"[{self.module_name}] 📁 Found cached H3 data. Loading from {self.h3_cache_path}")
                try:
                    with open(self.h3_cache_path, 'r') as f:
                        h3_data = json.load(f)
                    
                    if h3_data and len(h3_data) > 0:
                        analysis_stats['cached_data_used'] = True
                        analysis_stats['h3_data_processed'] = len(h3_data)
                        logger.info(f"[{self.module_name}] ✅ Loaded {len(h3_data)} hexagons from cache")
                    else:
                        logger.warning(f"[{self.module_name}] ⚠️ Cached data is empty")
                        h3_data = {}
                        
                except Exception as e:
                    error_msg = f"Failed to load cached data: {e}"
                    analysis_stats['errors'].append(error_msg)
                    logger.error(f"[{self.module_name}] ❌ {error_msg}")
                    h3_data = {}
            else:
                logger.info(f"[{self.module_name}] 📁 No cached H3 data found. Starting real data acquisition...")
                h3_data = {}
                
                # 2. Acquire raw data with detailed tracking
                try:
                    logger.info(f"[{self.module_name}] 🔍 Acquiring raw data...")
                    raw_data_path = self.acquire_raw_data()
                    
                    if raw_data_path and raw_data_path.exists():
                        # Check if file has real content
                        file_size = raw_data_path.stat().st_size
                        if file_size > 100:  # More than just headers
                            analysis_stats['raw_data_acquired'] = True
                            logger.info(f"[{self.module_name}] ✅ Raw data acquired: {raw_data_path} ({file_size} bytes)")
                        else:
                            logger.warning(f"[{self.module_name}] ⚠️ Raw data file too small: {raw_data_path} ({file_size} bytes)")
                    else:
                        logger.warning(f"[{self.module_name}] ⚠️ No raw data path returned or file doesn't exist")
                        
                except Exception as e:
                    error_msg = f"Raw data acquisition failed: {e}"
                    analysis_stats['errors'].append(error_msg)
                    logger.error(f"[{self.module_name}] ❌ {error_msg}")
                    raw_data_path = None
                
                # 3. Process raw data to H3 if acquisition was successful
                if raw_data_path and raw_data_path.exists():
                    try:
                        logger.info(f"[{self.module_name}] 🔄 Processing raw data to H3...")
                        h3_data = self.process_to_h3(raw_data_path)
                        
                        if h3_data and len(h3_data) > 0:
                            analysis_stats['h3_data_processed'] = len(h3_data)
                            logger.info(f"[{self.module_name}] ✅ Processed {len(h3_data)} hexagons to H3")
                        else:
                            logger.warning(f"[{self.module_name}] ⚠️ H3 processing returned empty data")
                            
                    except Exception as e:
                        error_msg = f"H3 processing failed: {e}"
                        analysis_stats['errors'].append(error_msg)
                        logger.error(f"[{self.module_name}] ❌ {error_msg}")
                        h3_data = {}
                
                # 4. Cache the H3 data if processing was successful
                if h3_data and len(h3_data) > 0:
                    try:
                        logger.info(f"[{self.module_name}] 💾 Caching new H3 data to {self.h3_cache_path}")
                        with open(self.h3_cache_path, 'w') as f:
                            json.dump(h3_data, f)
                        logger.info(f"[{self.module_name}] ✅ H3 data cached successfully")
                    except Exception as e:
                        error_msg = f"Failed to cache H3 data: {e}"
                        analysis_stats['errors'].append(error_msg)
                        logger.error(f"[{self.module_name}] ❌ {error_msg}")

            # 5. Run the final analysis on the (now available) H3 data
            if h3_data and len(h3_data) > 0:
                try:
                    logger.info(f"[{self.module_name}] 🔬 Running final analysis on {len(h3_data)} hexagons...")
                    final_results = self.run_final_analysis(h3_data)
                    
                    if final_results and len(final_results) > 0:
                        analysis_stats['final_analysis_completed'] = True
                        logger.info(f"[{self.module_name}] ✅ Final analysis completed: {len(final_results)} results")
                        
                        # Log sample of final results
                        sample_keys = list(final_results.keys())[:3]
                        logger.info(f"[{self.module_name}] 📊 Sample final results keys: {sample_keys}")
                        for key in sample_keys:
                            sample_data = final_results[key]
                            logger.info(f"[{self.module_name}] 📊 Sample result for {key}: {sample_data}")
                    else:
                        logger.warning(f"[{self.module_name}] ⚠️ Final analysis returned empty results")
                        final_results = {}
                        
                except Exception as e:
                    error_msg = f"Final analysis failed: {e}"
                    analysis_stats['errors'].append(error_msg)
                    logger.error(f"[{self.module_name}] ❌ {error_msg}")
                    final_results = {}
            else:
                logger.warning(f"[{self.module_name}] ⚠️ No H3 data available for final analysis")
                final_results = {}
            
            # Log comprehensive analysis summary
            logger.info(f"[{self.module_name}] 📊 ANALYSIS SUMMARY:")
            logger.info(f"[{self.module_name}]   - Cached data used: {analysis_stats['cached_data_used']}")
            logger.info(f"[{self.module_name}]   - Raw data acquired: {analysis_stats['raw_data_acquired']}")
            logger.info(f"[{self.module_name}]   - H3 cells processed: {analysis_stats['h3_data_processed']}")
            logger.info(f"[{self.module_name}]   - Final analysis completed: {analysis_stats['final_analysis_completed']}")
            logger.info(f"[{self.module_name}]   - Final results: {len(final_results)} hexagons")
            if analysis_stats['errors']:
                logger.info(f"[{self.module_name}]   - Errors: {len(analysis_stats['errors'])}")
                for error in analysis_stats['errors']:
                    logger.info(f"[{self.module_name}]     ❌ {error}")
            
            if len(final_results) == 0:
                logger.error(f"[{self.module_name}] ❌ CRITICAL: No final results generated!")
                logger.error(f"[{self.module_name}] 🔍 This indicates a fundamental processing failure.")
                logger.error(f"[{self.module_name}] 🔍 Check data sources, file paths, and analysis logic.")
            
            return final_results
            
        except Exception as e:
            error_msg = f"Module analysis workflow failed: {e}"
            analysis_stats['errors'].append(error_msg)
            logger.error(f"[{self.module_name}] ❌ {error_msg}")
            return {} 