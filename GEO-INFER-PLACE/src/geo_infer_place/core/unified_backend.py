#!/usr/bin/env python3
"""
Unified H3 Backend for Cascadian Agricultural Land Analysis - Enhanced with SPACE Integration

This module provides a unified interface for integrating multiple data sources
through H3 spatial indexing, enabling cross-border analysis between California
and Oregon agricultural areas with maximum SPACE integration.
"""
import sys
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import logging
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, mapping
import folium
from folium.plugins import HeatMap, MarkerCluster

# --- Enhanced H3 and OSC Integration ---
import h3
from geo_infer_space.osc_geo import create_h3_data_loader, H3DataLoader
from geo_infer_space.osc_geo.utils import cell_to_latlngjson, geojson_to_h3
from geo_infer_space.core.spatial_processor import SpatialProcessor
from geo_infer_space.core.data_integrator import DataIntegrator
from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine
from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary, polygon_to_cells
from geo_infer_space.utils.config_loader import LocationConfigLoader, LocationBounds

# --- Local Core Imports ---
# Base class for type hinting
from .base_module import BaseAnalysisModule
from geo_infer_space.core.unified_backend import UnifiedH3Backend, NumpyEncoder

import hashlib
from typing import List, Dict, Any, Optional, Tuple
import logging
import time
from collections import defaultdict

# Import SPACE components with fallback handling
try:
    from geo_infer_space.core.unified_backend import UnifiedH3Backend
    from geo_infer_space.osc_geo import create_h3_data_loader
    from geo_infer_space.utils.config_loader import LocationConfigLoader
    from geo_infer_space.utils.h3_utils import polygon_to_cells
    SPACE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"SPACE components not fully available: {e}")
    SPACE_AVAILABLE = False
    UnifiedH3Backend = object

# Standard imports
import h3
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon, shape as shapely_shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
try:
    from shapely import mapping
except ImportError:
    from shapely.geometry import mapping

logger = logging.getLogger(__name__)


class CascadianAgriculturalH3Backend(UnifiedH3Backend):
    """
    Enhanced H3-based backend for agricultural analysis in the Cascadian bioregion
    with integrated SPACE functionality, persistent caching, and performance optimizations.
    
    Supports:
    - Cross-border analysis between California and Oregon
    - Multiple agricultural analysis modules
    - H3 spatial indexing for consistent analysis
    - SPACE integration for advanced geospatial operations
    - Persistent caching for improved performance
    """
    
    def __init__(self, 
                 modules: Dict[str, Any],
                 resolution: int = 8,
                 bioregion: str = 'Cascadia',
                 target_counties: Optional[Dict[str, List[str]]] = None,
                 base_data_dir: Optional[Path] = None,
                 osc_repo_dir: Optional[str] = None,
                 enable_caching: bool = True):
        """
        Initialize the enhanced Cascadian H3 backend with SPACE integration and caching.
        
        Args:
            modules: Dictionary of analysis modules
            resolution: H3 resolution level (0-15)
            bioregion: Target bioregion identifier
            target_counties: Dictionary mapping states to county lists
            base_data_dir: Base directory for data storage
            osc_repo_dir: Path to OSC repository for SPACE integration
            enable_caching: Whether to enable persistent caching
        """
        self.bioregion = bioregion
        self.enable_caching = enable_caching
        self.cache_dir = Path(base_data_dir or '.') / 'cache' if enable_caching else None
        self.resolution = resolution  # Set resolution early
        self.base_data_dir = Path(base_data_dir or '.')  # Set base_data_dir
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger(__name__)
        
        # Initialize SPACE data loader if available
        self.h3_data_loader = None
        self.h3_loader = None  # Add this attribute for compatibility with SPACE BaseAnalysisModule
        self.osc_repo_dir = osc_repo_dir
        if SPACE_AVAILABLE and osc_repo_dir:
            try:
                self.h3_data_loader = create_h3_data_loader(osc_repo_dir)
                self.h3_loader = self.h3_data_loader  # Set h3_loader to h3_data_loader for compatibility
                logger.info("Successfully initialized H3DataLoader from GEO-INFER-SPACE.")
            except Exception as e:
                logger.warning(f"Failed to initialize H3DataLoader: {e}")
        
        # Get target counties and generate hexagons with caching
        county_geoms, all_hexagons = self._define_target_region_cached(target_counties)
        
        # Initialize the parent UnifiedH3Backend if SPACE is available
        if SPACE_AVAILABLE:
            try:
                # Convert county_geoms to the format expected by parent constructor
                target_areas = {}
                for state, counties in county_geoms.items():
                    target_areas[state] = list(counties.keys())
                
                super().__init__(
                    modules=modules,
                    resolution=resolution,
                    target_region=bioregion,
                    target_areas=target_areas,
                    base_data_dir=base_data_dir,
                    osc_repo_dir=osc_repo_dir
                )
            except Exception as e:
                logger.warning(f"Failed to initialize UnifiedH3Backend: {e}")
                # Initialize basic attributes directly
                self.modules = modules
                self.target_hexagons = all_hexagons
                self.unified_data = {}
        else:
            # Initialize basic attributes directly
            self.modules = modules
            self.target_hexagons = all_hexagons
            self.unified_data = {}
        
        # Enhanced SPACE integration
        self.spatial_processor = SpatialProcessor()
        self.data_integrator = None  # Will be initialized when needed
        self.visualization_engine = None  # Will be initialized when needed
        
        # Cascadia-specific configuration
        self.cascadia_config = self._load_cascadia_config()
        
        # Enhanced data structures
        self.spatial_analysis_results = {}
        self.h3_spatial_correlations = {}
        self.hotspot_analysis = {}
        self.redevelopment_scores = {}
        
        # Add Cascadia-specific initialization here
        self.target_hexagons_by_state, self.target_hexagons = self._define_target_region(target_counties)
        
        logger.info(f"Enhanced CascadianAgriculturalH3Backend initialized for '{self.bioregion}' with {len(self.modules)} active modules at H3 resolution {self.resolution}")
        logger.info(f"Active modules: {list(self.modules.keys())}")
        logger.info(f"Defined {len(self.target_hexagons)} total target hexagons across {len(self.target_hexagons_by_state)} states.")
        logger.info(f"SPACE integration: Spatial processor, data integrator, and visualization engine available")

    def _load_cascadia_config(self) -> Dict[str, Any]:
        """Load Cascadia-specific configuration with SPACE integration"""
        try:
            config_loader = LocationConfigLoader()
            config = config_loader.load_location_config('cascadia')
            if not config:
                # Enhanced default configuration
                config = {
                    'bounds': LocationBounds(
                        north=46.3,  # Northern Oregon
                        south=32.5,  # Southern California
                        east=-114.0, # Eastern boundary
                        west=-124.8  # Western boundary
                    ),
                    'h3_resolution': self.resolution,
                    'spatial_analysis': {
                        'buffer_distance': 1000,  # meters
                        'proximity_analysis': True,
                        'multi_overlay': True,
                        'correlation_analysis': True
                    },
                    'visualization': {
                        'base_map': 'CartoDB positron',
                        'default_zoom': 7,
                        'center': [44.0, -120.5],  # Center of Oregon
                        'layers': {
                            'zoning': {'color': '#1f77b4', 'opacity': 0.6},
                            'current_use': {'color': '#2ca02c', 'opacity': 0.6},
                            'water': {'color': '#d62728', 'opacity': 0.6},
                            'ownership': {'color': '#ff7f0e', 'opacity': 0.6},
                            'redevelopment': {'color': '#9467bd', 'opacity': 0.7}
                        }
                    }
                }
            logger.info("✅ Cascadia configuration loaded successfully")
            return config
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Cascadia configuration: {e}. Using defaults.")
            return {}

    def _get_cache_key(self, target_counties: Dict[str, List[str]]) -> str:
        """Generate a cache key based on target counties and resolution."""
        cache_data = {
            'target_counties': target_counties,
            'resolution': self.resolution,
            'bioregion': self.bioregion
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Tuple[Dict[str, Dict[str, Any]], List[str]]]:
        """Load county geometries and hexagons from cache."""
        if not self.cache_dir:
            return None
            
        cache_file = self.cache_dir / f"region_cache_{cache_key}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            logger.info(f"Loading region data from cache: {cache_file}")
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Reconstruct geometries from GeoJSON
            county_geoms = {}
            for state, counties in cache_data['county_geoms'].items():
                county_geoms[state] = {}
                for county, geom_data in counties.items():
                    county_geoms[state][county] = shapely_shape(geom_data)
            
            hexagons = cache_data['hexagons']
            logger.info(f"✅ Loaded {len(hexagons)} hexagons from cache")
            return county_geoms, hexagons
            
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, county_geoms: Dict[str, Dict[str, Any]], hexagons: List[str]) -> None:
        """Save county geometries and hexagons to cache."""
        if not self.cache_dir:
            return
            
        cache_file = self.cache_dir / f"region_cache_{cache_key}.json"
        
        try:
            # Convert geometries to GeoJSON for serialization
            serializable_geoms = {}
            for state, counties in county_geoms.items():
                serializable_geoms[state] = {}
                for county, geom in counties.items():
                    serializable_geoms[state][county] = mapping(geom)
            
            cache_data = {
                'county_geoms': serializable_geoms,
                'hexagons': hexagons,
                'cached_at': time.time(),
                'resolution': self.resolution,
                'bioregion': self.bioregion
            }
            
            logger.info(f"Saving region data to cache: {cache_file}")
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.info(f"✅ Cached {len(hexagons)} hexagons")
            
        except Exception as e:
            logger.warning(f"Failed to save to cache: {e}")
            import traceback
            logger.debug(f"Cache error details: {traceback.format_exc()}")
    
    def _define_target_region_cached(self, target_counties: Optional[Dict[str, List[str]]] = None) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
        """
        Define target region with caching support.
        
        Args:
            target_counties: Dictionary mapping states to county lists
            
        Returns:
            Tuple of (county_geometries, all_hexagons)
        """
        if target_counties is None:
            target_counties = {'CA': ['all'], 'OR': ['all']}
        
        # Try to load from cache first
        cache_key = self._get_cache_key(target_counties)
        cached_result = self._load_from_cache(cache_key)
        
        if cached_result is not None:
            logger.info("Using cached region data")
            return cached_result
        
        # Generate new data if not in cache
        logger.info("Generating new region data (not in cache)")
        county_geoms, all_hexagons = self._define_target_region(target_counties)
        
        # Save to cache for future use
        self._save_to_cache(cache_key, county_geoms, all_hexagons)
        
        return county_geoms, all_hexagons

    def _define_target_region(self, target_counties: Optional[Dict[str, List[str]]] = None) -> Tuple[Dict[str, List[str]], List[str]]:
        """
        Define the target region based on county geometries.
        
        Args:
            target_counties: Dictionary mapping states to lists of counties
            
        Returns:
            Tuple of (hexagons_by_state, all_hexagons)
        """
        logger = logging.getLogger(__name__)
        
        county_geoms = self._get_county_geometries(target_counties)
        
        if not county_geoms:
            logger.error("No county geometries could be loaded or defined. Cannot define a target region.")
            return {}, []

        hexagons_by_state: Dict[str, set] = {state: set() for state in county_geoms.keys()}
        
        for state, counties in county_geoms.items():
            for county_name, geom in counties.items():
                logger.info(f"Generating hexagons for {county_name}, {state} using SPACE utilities...")
                logger.debug(f"Geometry type: {type(geom)}, Geometry: {geom}")
                try:
                    # Use direct H3 library for polygon_to_cells (more reliable than SPACE polygon_to_cells)
                    if isinstance(geom, (Polygon, MultiPolygon)):
                        # Convert to GeoJSON format for H3 polygon_to_cells
                        geojson_geom = mapping(geom)
                        logger.debug(f"Converted to GeoJSON: {geojson_geom}")
                        try:
                            # Ensure proper GeoJSON structure for H3 v4
                            if geojson_geom.get('type') == 'Polygon' and geojson_geom.get('coordinates'):
                                # Ensure coordinates are properly nested for H3 v4
                                if not isinstance(geojson_geom['coordinates'][0][0], (list, tuple)):
                                    geojson_geom['coordinates'] = [geojson_geom['coordinates']]
                            
                            # Use correct H3 API for version 4.x - geo_to_cells for GeoJSON
                            hexagons_in_county = h3.geo_to_cells(geojson_geom, self.resolution)
                            hexagons_by_state[state].update(hexagons_in_county)
                            logger.info(f"Generated {len(hexagons_in_county)} hexagons for {county_name}, {state}")
                        except Exception as h3_error:
                            logger.error(f"H3 geo_to_cells failed: {h3_error}")
                            # Fallback to SPACE polygon_to_cells
                            try:
                                from geo_infer_space.utils.h3_utils import polygon_to_cells
                                hexagons_in_county = polygon_to_cells(geojson_geom, self.resolution)
                                hexagons_by_state[state].update(hexagons_in_county)
                                logger.info(f"Generated {len(hexagons_in_county)} hexagons using SPACE fallback for {county_name}, {state}")
                            except Exception as space_error:
                                logger.error(f"SPACE polygon_to_cells also failed: {space_error}")
                    elif isinstance(geom, dict) and geom.get('type') == 'Polygon':
                        # Already in GeoJSON format
                        try:
                            # Ensure coordinates are properly nested for H3 v4
                            if not isinstance(geom['coordinates'][0][0], (list, tuple)):
                                geom['coordinates'] = [geom['coordinates']]
                                
                            hexagons_in_county = h3.geo_to_cells(geom, self.resolution)
                            hexagons_by_state[state].update(hexagons_in_county)
                            logger.info(f"Generated {len(hexagons_in_county)} hexagons for {county_name}, {state}")
                        except Exception as h3_error:
                            logger.error(f"H3 geo_to_cells failed: {h3_error}")
                            # Fallback to SPACE polygon_to_cells
                            try:
                                from geo_infer_space.utils.h3_utils import polygon_to_cells
                                hexagons_in_county = polygon_to_cells(geom, self.resolution)
                                hexagons_by_state[state].update(hexagons_in_county)
                                logger.info(f"Generated {len(hexagons_in_county)} hexagons using SPACE fallback for {county_name}, {state}")
                            except Exception as space_error:
                                logger.error(f"SPACE polygon_to_cells also failed: {space_error}")
                    elif isinstance(geom, dict) and geom.get('type') == 'Feature':
                        # GeoJSON Feature - extract geometry
                        try:
                            geometry = geom.get('geometry', {})
                            if geometry and geometry.get('type') == 'Polygon':
                                # Ensure coordinates are properly nested for H3 v4
                                if not isinstance(geometry['coordinates'][0][0], (list, tuple)):
                                    geometry['coordinates'] = [geometry['coordinates']]
                                
                                hexagons_in_county = h3.geo_to_cells(geometry, self.resolution)
                                hexagons_by_state[state].update(hexagons_in_county)
                                logger.info(f"Generated {len(hexagons_in_county)} hexagons for {county_name}, {state}")
                            else:
                                logger.error(f"Invalid or missing geometry in Feature for {county_name}, {state}")
                        except Exception as h3_error:
                            logger.error(f"H3 geo_to_cells failed for Feature: {h3_error}")
                    elif isinstance(geom, dict):
                        # Try to convert plain dict to proper GeoJSON structure
                        logger.warning(f"Attempting to convert plain dict to GeoJSON for {county_name}, {state}")
                        if 'coordinates' in geom:
                            geojson_geom = {
                                'type': 'Polygon',
                                'coordinates': [geom['coordinates']]  # Ensure proper nesting for H3 v4
                            }
                            try:
                                hexagons_in_county = h3.geo_to_cells(geojson_geom, self.resolution)
                                hexagons_by_state[state].update(hexagons_in_county)
                                logger.info(f"Generated {len(hexagons_in_county)} hexagons for {county_name}, {state}")
                            except Exception as h3_error:
                                logger.error(f"H3 geo_to_cells failed: {h3_error}")
                        else:
                            logger.error(f"Invalid geometry structure for {county_name}, {state}: {geom}")
                    else:
                        logger.warning(f"Skipping invalid geometry for {county_name}, {state}: {type(geom)}")
                except Exception as e:
                    logger.error(f"SPACE H3 polygon_to_cells failed for {county_name}, {state}: {e}")
                    logger.debug(f"Geometry that failed: {geom}")

        final_hex_by_state = {k: sorted(list(v)) for k, v in hexagons_by_state.items() if v}
        final_all_hexagons = sorted(list(set.union(*hexagons_by_state.values())))
            
        if not final_all_hexagons:
            logger.error(f"Failed to generate any H3 hexagons for bioregion '{self.bioregion}' with filters {target_counties}")
            return {}, []
            
        logger.info(f"✅ Generated {len(final_all_hexagons)} H3 hexagons using SPACE utilities")
        return final_hex_by_state, final_all_hexagons

    def _get_county_geometries(self, target_counties: Optional[Dict[str, List[str]]]) -> Dict[str, Dict[str, Any]]:
        """
        Enhanced county geometry loading with county boundary loader.
        Falls back to placeholder bounding boxes if the loader is not available.
        """
        if not target_counties:
            return {}

        logger = logging.getLogger(__name__)
        logger.info("Loading county geometries with boundary loader...")
        
        try:
            # Import the county boundary loader
            import sys
            import json
            from pathlib import Path
            
            # Add the config directory to the path
            config_dir = Path(__file__).parent.parent.parent.parent / 'locations' / 'cascadia' / 'config'
            if str(config_dir) not in sys.path:
                sys.path.insert(0, str(config_dir))
            
            # Try multiple approaches to load county geometries
            county_geometries = {}
            
            # Approach 1: Try using county_boundary_loader
            try:
                from county_boundary_loader import create_county_boundary_loader
                # Create the loader and get geometries
                loader = create_county_boundary_loader()
                county_geometries = loader.get_all_county_geometries(target_counties)
                if county_geometries:
                    logger.info(f"Successfully loaded county geometries using boundary loader")
                    return county_geometries
            except ImportError:
                logger.warning("county_boundary_loader not found, trying alternative methods")
            except Exception as e:
                logger.warning(f"Error using county_boundary_loader: {e}")
            
            # Approach 2: Try direct loading from GeoJSON files
            try:
                for state, counties in target_counties.items():
                    if state not in county_geometries:
                        county_geometries[state] = {}
                    
                    for county in counties:
                        if county == 'all':
                            # Try to load state-wide file
                            state_file = config_dir / f"{state.lower()}_counties_boundary.geojson"
                            if state_file.exists():
                                with open(state_file, 'r') as f:
                                    geojson_data = json.load(f)
                                
                                if geojson_data.get('type') == 'FeatureCollection':
                                    for feature in geojson_data.get('features', []):
                                        if 'properties' in feature and 'geometry' in feature:
                                            county_name = feature['properties'].get('county_name')
                                            if county_name:
                                                county_geometries[state][county_name] = feature['geometry']
                                                logger.info(f"Loaded geometry for {county_name}, {state}")
                        else:
                            # Try to load specific county file
                            county_file = config_dir / f"{state.lower()}_{county.lower()}_boundary.geojson"
                            if county_file.exists():
                                with open(county_file, 'r') as f:
                                    geojson_data = json.load(f)
                                
                                if geojson_data.get('type') == 'FeatureCollection':
                                    for feature in geojson_data.get('features', []):
                                        if 'geometry' in feature:
                                            county_geometries[state][county] = feature['geometry']
                                            logger.info(f"Loaded geometry for {county}, {state}")
                                elif geojson_data.get('type') == 'Feature':
                                    county_geometries[state][county] = geojson_data['geometry']
                                    logger.info(f"Loaded geometry for {county}, {state}")
                
                if county_geometries and any(counties for counties in county_geometries.values()):
                    logger.info(f"Successfully loaded county geometries from GeoJSON files")
                    return county_geometries
            except Exception as e:
                logger.warning(f"Error loading from GeoJSON files: {e}")
            
            # Approach 3: Try loading from a specific file we know exists
            try:
                lassen_file = config_dir / "ca_lassen_boundary.geojson"
                if lassen_file.exists():
                    with open(lassen_file, 'r') as f:
                        geojson_data = json.load(f)
                    
                    if 'CA' not in county_geometries:
                        county_geometries['CA'] = {}
                    
                    if geojson_data.get('type') == 'FeatureCollection':
                        for feature in geojson_data.get('features', []):
                            if 'geometry' in feature:
                                county_geometries['CA']['Lassen'] = feature['geometry']
                                logger.info("Loaded geometry for Lassen, CA from specific file")
                                return county_geometries
            except Exception as e:
                logger.warning(f"Error loading from specific file: {e}")
            
            # If we still don't have geometries, fall back to placeholder geometries
            if not county_geometries or not any(counties for counties in county_geometries.values()):
                logger.warning("No county geometries loaded, falling back to placeholder geometries")
                return self._create_placeholder_geometries(target_counties)
            
            return county_geometries
            
        except Exception as e:
            logger.error(f"Failed to load county geometries: {e}")
            logger.info("Falling back to placeholder geometries")
            return self._create_placeholder_geometries(target_counties)

    def _create_placeholder_geometries(self, target_counties: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """Create placeholder geometries when boundary loader is not available"""
        logger.info("Creating placeholder geometries...")
        
        placeholder_geoms = {}
        for state, counties in target_counties.items():
            if counties == ['all'] or 'all' in counties:
                # Create a simple bounding box for the state
                if state == 'CA':
                    # California bounding box - create proper Shapely Polygon
                    placeholder_geoms[state] = {'all': Polygon([
                        (-124.5, 32.5), (-114.0, 32.5), (-114.0, 42.0), (-124.5, 42.0), (-124.5, 32.5)
                    ])}
                elif state == 'OR':
                    # Oregon bounding box - create proper Shapely Polygon
                    placeholder_geoms[state] = {'all': Polygon([
                        (-124.5, 42.0), (-116.5, 42.0), (-116.5, 46.3), (-124.5, 46.3), (-124.5, 42.0)
                    ])}
                elif state == 'WA':
                    # Washington bounding box - create proper Shapely Polygon
                    placeholder_geoms[state] = {'all': Polygon([
                        (-124.5, 46.3), (-116.5, 46.3), (-116.5, 49.0), (-124.5, 49.0), (-124.5, 46.3)
                    ])}
            else:
                # For specific counties, create individual polygons
                placeholder_geoms[state] = {}
                for county in counties:
                    if state == 'CA' and county == 'Lassen':
                        # Lassen County bounding box
                        placeholder_geoms[state][county] = Polygon([
                            (-121.5, 40.0), (-120.0, 40.0), (-120.0, 41.5), (-121.5, 41.5), (-121.5, 40.0)
                        ])
                    else:
                        # Generic county bounding box
                        placeholder_geoms[state][county] = Polygon([
                            (-124.0, 40.0), (-120.0, 40.0), (-120.0, 42.0), (-124.0, 42.0), (-124.0, 40.0)
                        ])
        
        return placeholder_geoms

    def run_comprehensive_analysis(self) -> None:
        """
        Enhanced comprehensive analysis with SPACE integration.
        
        This method orchestrates the complete analysis pipeline:
        1.  Acquire raw data for each module.
        2.  Process raw data to H3 using the OSC loader.
        3.  Run the module's final analysis on the H3 data.
        4.  Aggregate results.
        5.  Perform spatial analysis using SPACE utilities.
        """
        logger.info("Starting enhanced comprehensive analysis with SPACE integration...")
        module_results = {}
        data_acquisition_stats = {}

        for name, module in self.modules.items():
            logger.info(f"--- Processing Module: {name.upper()} with SPACE integration ---")
            
            # Track data acquisition for this module
            module_stats = {
                'raw_data_acquired': False,
                'h3_data_processed': 0,
                'final_analysis_completed': False,
                'errors': []
            }
            
            try:
                # Step 1: Acquire raw data with detailed tracking
                logger.info(f"[{name}] Starting real data acquisition...")
                try:
                    raw_data_path = module.acquire_raw_data()
                    if raw_data_path and raw_data_path.exists():
                        # Check if file has real content
                        file_size = raw_data_path.stat().st_size
                        if file_size > 100:  # More than just headers
                            module_stats['raw_data_acquired'] = True
                            logger.info(f"[{name}] ✅ Raw data acquired: {raw_data_path} ({file_size} bytes)")
                        else:
                            logger.warning(f"[{name}] ⚠️ Raw data file too small: {raw_data_path} ({file_size} bytes)")
                    else:
                        logger.warning(f"[{name}] ⚠️ No raw data path returned or file doesn't exist")
                except Exception as e:
                    error_msg = f"Raw data acquisition failed: {e}"
                    module_stats['errors'].append(error_msg)
                    logger.error(f"[{name}] ❌ {error_msg}")
                
                # Step 2: Run module analysis with detailed tracking
                logger.info(f"[{name}] Starting module analysis...")
                try:
                    result = module.run_analysis()
                    
                    # Track H3 data processing
                    if result:
                        h3_count = len(result)
                        module_stats['h3_data_processed'] = h3_count
                        module_stats['final_analysis_completed'] = True
                        logger.info(f"[{name}] ✅ Analysis completed: {h3_count} H3 cells processed")
                        
                        # Log sample of processed data
                        if h3_count > 0:
                            sample_keys = list(result.keys())[:3]
                            logger.info(f"[{name}] 📊 Sample processed data keys: {sample_keys}")
                            for key in sample_keys:
                                sample_data = result[key]
                                logger.info(f"[{name}] 📊 Sample data for {key}: {sample_data}")
                    else:
                        logger.warning(f"[{name}] ⚠️ Analysis returned empty result")
                        
                except Exception as e:
                    error_msg = f"Module analysis failed: {e}"
                    module_stats['errors'].append(error_msg)
                    logger.error(f"[{name}] ❌ {error_msg}")
                
                module_results[name] = result
                data_acquisition_stats[name] = module_stats
                
                # Log module summary
                logger.info(f"[{name}] 📊 Module processing summary:")
                logger.info(f"[{name}]   - Raw data acquired: {module_stats['raw_data_acquired']}")
                logger.info(f"[{name}]   - H3 cells processed: {module_stats['h3_data_processed']}")
                logger.info(f"[{name}]   - Final analysis completed: {module_stats['final_analysis_completed']}")
                if module_stats['errors']:
                    logger.info(f"[{name}]   - Errors: {len(module_stats['errors'])}")
                    for error in module_stats['errors']:
                        logger.info(f"[{name}]     ❌ {error}")
                
                logger.info(f"✅ Successfully processed module: {name.upper()}")
                
            except Exception as e:
                error_msg = f"Module processing failed: {e}"
                module_stats['errors'].append(error_msg)
                logger.error(f"❌ Failed to process module {name.upper()}: {e}", exc_info=True)
                module_results[name] = {}
                data_acquisition_stats[name] = module_stats
        
        # Log comprehensive data acquisition summary
        logger.info("📊 COMPREHENSIVE DATA ACQUISITION SUMMARY:")
        total_hexagons_processed = 0
        modules_with_data = 0
        
        for name, stats in data_acquisition_stats.items():
            logger.info(f"📊 {name.upper()}:")
            logger.info(f"   - Raw data acquired: {stats['raw_data_acquired']}")
            logger.info(f"   - H3 cells processed: {stats['h3_data_processed']}")
            logger.info(f"   - Final analysis completed: {stats['final_analysis_completed']}")
            logger.info(f"   - Errors: {len(stats['errors'])}")
            
            if stats['h3_data_processed'] > 0:
                modules_with_data += 1
                total_hexagons_processed += stats['h3_data_processed']
        
        logger.info(f"📊 OVERALL SUMMARY:")
        logger.info(f"   - Modules with data: {modules_with_data}/{len(self.modules)}")
        logger.info(f"   - Total hexagons processed: {total_hexagons_processed}")
        logger.info(f"   - Target hexagons: {len(self.target_hexagons)}")
        
        if total_hexagons_processed == 0:
            logger.error("❌ CRITICAL: No hexagons processed by any module!")
            logger.error("🔍 This indicates a fundamental data acquisition or processing failure.")
            logger.error("🔍 Check module data sources, file paths, and processing logic.")
        
        self._aggregate_module_results(module_results)
        
        # Enhanced spatial analysis using SPACE utilities
        logger.info("Performing enhanced spatial analysis with SPACE utilities...")
        self._perform_spatial_analysis()
        
        logger.info("✅ Enhanced comprehensive analysis complete. All module data has been aggregated and spatially analyzed.")
    
    def _perform_spatial_analysis(self) -> None:
        """Perform comprehensive spatial analysis using SPACE utilities"""
        logger.info("Performing spatial analysis with SPACE integration...")
        
        try:
            # Spatial correlation analysis
            self._analyze_spatial_correlations()
            
            # Hotspot analysis
            self._analyze_hotspots()
            
            # Buffer and proximity analysis
            self._analyze_spatial_relationships()
            
            logger.info("✅ Spatial analysis completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Spatial analysis failed: {e}")
    
    def _analyze_spatial_correlations(self) -> None:
        """Analyze spatial correlations between modules using SPACE utilities"""
        logger.info("Analyzing spatial correlations between modules...")
        
        try:
            # Get module data for correlation analysis
            module_data = {}
            for module_name in self.modules.keys():
                module_scores = []
                for hex_id in self.target_hexagons:
                    hex_data = self.unified_data.get(hex_id, {})
                    module_data_point = hex_data.get(module_name, {})
                    # Extract a score or key metric from each module
                    if module_data_point:
                        # This is a simplified approach - each module should provide a score
                        score = module_data_point.get('score', 0.5)
                        module_scores.append(score)
                    else:
                        module_scores.append(0.0)
                module_data[module_name] = module_scores
            
            # Calculate correlations between modules
            if len(module_data) > 1:
                module_names = list(module_data.keys())
                for i, module1 in enumerate(module_names):
                    for module2 in module_names[i+1:]:
                        correlation = np.corrcoef(module_data[module1], module_data[module2])[0, 1]
                        self.h3_spatial_correlations[f"{module1}_{module2}"] = correlation
                        logger.debug(f"Spatial correlation {module1}-{module2}: {correlation:.3f}")
            
            logger.info(f"✅ Calculated {len(self.h3_spatial_correlations)} spatial correlations")
            
        except Exception as e:
            logger.error(f"❌ Spatial correlation analysis failed: {e}")
    
    def _analyze_hotspots(self) -> None:
        """Analyze hotspots using SPACE spatial analysis utilities"""
        logger.info("Analyzing hotspots using SPACE utilities...")
        
        try:
            # Analyze redevelopment potential hotspots
            scores = [self.redevelopment_scores.get(h, {}).get('composite_score', 0) 
                     for h in self.target_hexagons]
            
            if scores:
                mean_score = np.mean(scores)
                std_score = np.std(scores)
                
                # Identify hotspots (areas with scores > mean + 1 std)
                hotspot_threshold = mean_score + std_score
                hotspots = [h for h in self.target_hexagons 
                          if self.redevelopment_scores.get(h, {}).get('composite_score', 0) > hotspot_threshold]
                
                self.hotspot_analysis = {
                    'mean_score': mean_score,
                    'std_score': std_score,
                    'hotspot_threshold': hotspot_threshold,
                    'hotspot_count': len(hotspots),
                    'hotspot_hexagons': hotspots
                }
                
                logger.info(f"✅ Identified {len(hotspots)} hotspots with threshold {hotspot_threshold:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Hotspot analysis failed: {e}")
    
    def _analyze_spatial_relationships(self) -> None:
        """Analyze spatial relationships using SPACE spatial processor"""
        logger.info("Analyzing spatial relationships using SPACE spatial processor...")
        
        try:
            # Convert H3 data to GeoDataFrame for spatial analysis
            features = []
            for hex_id in self.target_hexagons:
                hex_data = self.unified_data.get(hex_id, {})
                if hex_data.get('boundary'):
                    # Create polygon from H3 boundary
                    boundary_coords = hex_data['boundary']
                    polygon = Polygon(boundary_coords)
                    
                    # Add properties
                    properties = {
                        'hex_id': hex_id,
                        'redevelopment_score': self.redevelopment_scores.get(hex_id, {}).get('composite_score', 0)
                    }
                    
                    # Add module data
                    for module_name in self.modules.keys():
                        module_data = hex_data.get(module_name, {})
                        if module_data:
                            properties[f"{module_name}_score"] = module_data.get('score', 0)
                    
                    features.append({
                        'geometry': polygon,
                        'properties': properties
                    })
            
            if features:
                # Create GeoDataFrame
                gdf = gpd.GeoDataFrame(features)
                
                # Perform buffer analysis
                buffer_distance = self.cascadia_config.get('spatial_analysis', {}).get('buffer_distance', 1000)
                buffered_gdf = self.spatial_processor.buffer_analysis(gdf, buffer_distance)
                
                # Store spatial analysis results
                self.spatial_analysis_results = {
                    'total_features': len(features),
                    'buffer_distance': buffer_distance,
                    'buffered_features': len(buffered_gdf)
                }
                
                logger.info(f"✅ Spatial relationship analysis completed for {len(features)} features")
            
        except Exception as e:
            logger.error(f"❌ Spatial relationship analysis failed: {e}")
    
    def _aggregate_module_results(self, results: Dict[str, Dict]):
        """Enhanced aggregation with SPACE H3 utilities"""
        logger.info("Aggregating results from all modules using SPACE utilities...")
        
        for hexagon in self.target_hexagons:
            hex_data = {'hex_id': hexagon}
            
            # Add geometry and metadata using SPACE utilities
            try:
                # Use SPACE H3 utilities for enhanced geometry processing
                lat, lng = cell_to_latlng(hexagon)
                hex_data['centroid'] = [lat, lng]
                hex_data['boundary'] = cell_to_latlng_boundary(hexagon)
            except Exception as e:
                logger.warning(f"Could not process geometry for {hexagon} using SPACE utilities: {e}")
                hex_data['centroid'] = None
                hex_data['boundary'] = None

            # Add module data
            for module_name, module_data in results.items():
                hex_data[module_name] = module_data.get(hexagon, {})
            
            self.unified_data[hexagon] = hex_data
            
        logger.info(f"✅ Aggregated data for {len(self.target_hexagons)} hexagons from {len(results)} modules using SPACE utilities.")

    def calculate_agricultural_redevelopment_potential(self) -> Dict[str, Dict]:
        """
        Enhanced redevelopment score calculation with SPACE integration.
        
        Returns:
            Dictionary of redevelopment scores for each hexagon.
        """
        logger.info("Calculating enhanced agricultural redevelopment potential scores with SPACE integration...")
        if not self.unified_data:
            logger.warning("Unified data is not available. Cannot calculate redevelopment scores.")
            return {}

        for h3_index, hex_data in self.unified_data.items():
            scores = {
                'zoning': self._score_zoning(hex_data.get('zoning', {})),
                'current_use': self._score_current_use(hex_data.get('current_use', {})),
                'water': self._score_water(hex_data.get('surface_water', {}), hex_data.get('ground_water', {})),
                'water_rights': self._score_water_rights(hex_data.get('water_rights', {})),
                'infrastructure': self._score_infrastructure(hex_data.get('improvements', {}), hex_data.get('power_source', {})),
                'ownership': self._score_ownership(hex_data.get('ownership', {})),
                'debt': self._score_mortgage_debt(hex_data.get('mortgage_debt', {}))
            }

            # Enhanced weighted composite score with spatial considerations
            # Weights based on research document priorities, adjusted for new data
            composite_score = (
                scores['zoning'] * 0.20 +
                scores['water'] * 0.20 +
                scores['water_rights'] * 0.10 +
                scores['infrastructure'] * 0.20 +
                scores['ownership'] * 0.15 +
                scores['debt'] * 0.15
            ) / 1.0  # Normalizing factor

            # Add spatial context to scores
            spatial_context = self._calculate_spatial_context(h3_index, scores)
            composite_score = self._adjust_score_with_spatial_context(composite_score, spatial_context)

            self.redevelopment_scores[h3_index] = {
                'composite_score': composite_score,
                'factors': scores,
                'spatial_context': spatial_context
            }
            
        logger.info(f"✅ Calculated enhanced redevelopment scores for {len(self.redevelopment_scores)} hexagons with SPACE integration.")
        return self.redevelopment_scores

    def _calculate_spatial_context(self, h3_index: str, scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate spatial context for a hexagon using SPACE utilities"""
        try:
            # Get neighboring hexagons
            neighbors = h3.grid_disk(h3_index, 1)
            
            # Calculate neighborhood statistics
            neighbor_scores = []
            for neighbor in neighbors:
                if neighbor in self.redevelopment_scores:
                    neighbor_scores.append(self.redevelopment_scores[neighbor]['composite_score'])
            
            spatial_context = {
                'neighbor_count': len(neighbor_scores),
                'neighbor_mean_score': np.mean(neighbor_scores) if neighbor_scores else 0,
                'neighbor_std_score': np.std(neighbor_scores) if neighbor_scores else 0,
                'is_hotspot': h3_index in self.hotspot_analysis.get('hotspot_hexagons', []),
                'spatial_cluster': self._identify_spatial_cluster(h3_index)
            }
            
            return spatial_context
            
        except Exception as e:
            logger.warning(f"Could not calculate spatial context for {h3_index}: {e}")
            return {}

    def _identify_spatial_cluster(self, h3_index: str) -> str:
        """Identify spatial cluster type for a hexagon"""
        try:
            # Simple clustering based on score and neighbors
            score = self.redevelopment_scores.get(h3_index, {}).get('composite_score', 0)
            
            if score > 0.75:
                return 'high_potential_cluster'
            elif score > 0.5:
                return 'medium_potential_cluster'
            elif score > 0.25:
                return 'low_potential_cluster'
            else:
                return 'minimal_potential_cluster'
                
        except Exception as e:
            logger.warning(f"Could not identify spatial cluster for {h3_index}: {e}")
            return 'unknown_cluster'

    def _adjust_score_with_spatial_context(self, base_score: float, spatial_context: Dict[str, Any]) -> float:
        """Adjust score based on spatial context"""
        try:
            adjusted_score = base_score
            
            # Adjust based on neighborhood
            neighbor_mean = spatial_context.get('neighbor_mean_score', 0)
            if neighbor_mean > 0.7:  # High-potential neighborhood
                adjusted_score *= 1.1  # Boost score
            elif neighbor_mean < 0.3:  # Low-potential neighborhood
                adjusted_score *= 0.9  # Reduce score
            
            # Adjust based on hotspot status
            if spatial_context.get('is_hotspot', False):
                adjusted_score *= 1.05  # Slight boost for hotspots
            
            return min(1.0, max(0.0, adjusted_score))
            
        except Exception as e:
            logger.warning(f"Could not adjust score with spatial context: {e}")
            return base_score

    # Enhanced scoring helper methods with SPACE integration
    def _score_zoning(self, data: Dict) -> float:
        """Enhanced zoning scoring with spatial considerations"""
        if not data: return 0.1
        score = 0.5
        if data.get('is_ag_zone'): score += 0.4
        if data.get('allows_redevelopment'): score += 0.4
        return min(1.0, score)

    def _score_current_use(self, data: Dict) -> float:
        """Enhanced current use scoring"""
        if not data: return 0.1
        # More sophisticated logic based on crop types, intensity, etc.
        intensity = data.get('agricultural_intensity', 0.5)
        diversity = data.get('crop_diversity', 1)
        
        # Lower intensity and higher diversity generally indicate easier redevelopment
        score = (1.0 - intensity) * 0.6 + (min(diversity, 5) / 5.0) * 0.4
        return min(1.0, score)

    def _score_water(self, surface: Dict, ground: Dict) -> float:
        """Enhanced water scoring with spatial water availability"""
        if not surface and not ground: return 0.1
        
        surface_score = surface.get('water_security_score', 0.5) if surface else 0
        ground_score = ground.get('water_security_score', 0.5) if ground else 0
        
        # Weighted combination
        score = surface_score * 0.6 + ground_score * 0.4
        return min(1.0, score)

    def _score_water_rights(self, data: Dict) -> float:
        """Enhanced water rights scoring"""
        return data.get('water_security_score', 0.5)

    def _score_infrastructure(self, improvements: Dict, power: Dict) -> float:
        """Enhanced infrastructure scoring"""
        infra_score = improvements.get('modernization_score', 0) if improvements else 0
        power_score = power.get('grid_reliability_score', 0) if power else 0
        return (infra_score * 0.6 + power_score * 0.4)

    def _score_ownership(self, data: Dict) -> float:
        """Enhanced ownership scoring with spatial concentration analysis"""
        if not data: return 0.1
        concentration = data.get('ownership_concentration', 0.5)
        return 1.0 - concentration
    
    def _score_mortgage_debt(self, data: Dict) -> float:
        """Enhanced mortgage debt scoring"""
        if not data: return 0.1
        risk_level = data.get('financial_risk_level', 0.5)
        return 1.0 - risk_level

    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """
        Enhanced comprehensive summary with SPACE integration.
        
        Returns:
            Dictionary containing the enhanced analysis summary.
        """
        if not self.unified_data:
            return {'error': 'Analysis has not been run.'}

        scores = [s['composite_score'] for s in self.redevelopment_scores.values()]
        
        summary = {
            'bioregion': self.bioregion,
            'h3_resolution': self.resolution,
            'total_hexagons': len(self.target_hexagons),
            'modules_analyzed': list(self.modules.keys()),
            'analysis_timestamp': datetime.now().isoformat(),
            'space_integration': {
                'spatial_processor': True,
                'data_integrator': self.data_integrator is not None,
                'visualization_engine': self.visualization_engine is not None,
                'h3_utilities': True,
                'osc_integration': True
            },
            'redevelopment_potential': {
                'mean_score': round(np.mean(scores), 3) if scores else 0,
                'median_score': round(np.median(scores), 3) if scores else 0,
                'std_dev': round(np.std(scores), 3) if scores else 0,
                'high_potential_hexagons': len([s for s in scores if s > 0.75]),
                'low_potential_hexagons': len([s for s in scores if s < 0.25]),
            },
            'spatial_analysis': {
                'correlations_calculated': len(self.h3_spatial_correlations),
                'hotspots_identified': self.hotspot_analysis.get('hotspot_count', 0),
                'spatial_relationships_analyzed': len(self.spatial_analysis_results) > 0
            },
            'module_summaries': {}
        }

        for module_name in self.modules.keys():
            valid_hex_count = sum(1 for hex_data in self.unified_data.values() if hex_data.get(module_name))
            summary['module_summaries'][module_name] = {
                'processed_hexagons': valid_hex_count,
                'coverage': round(valid_hex_count / len(self.target_hexagons) * 100, 2) if self.target_hexagons else 0,
            }
        
        return summary
    
    def export_unified_data(self, output_path: str, export_format: str = 'geojson') -> None:
        """
        Enhanced export with SPACE utilities.
        
        Args:
            output_path: Output file path.
            export_format: 'geojson', 'csv', or 'json'.
        """
        if not self.unified_data:
            raise ValueError("No unified data to export. Please run the analysis first.")
        
        # Combine unified data with redevelopment scores and spatial analysis
        export_data = {}
        for h3_index, data in self.unified_data.items():
            export_data[h3_index] = data.copy()
            export_data[h3_index]['redevelopment_potential'] = self.redevelopment_scores.get(h3_index, {})
            export_data[h3_index]['spatial_analysis'] = self.spatial_analysis_results

        if export_format == 'geojson':
            self._export_geojson_enhanced(export_data, output_path)
        elif export_format == 'csv':
            self._export_csv(export_data, output_path)
        elif export_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, cls=NumpyEncoder)
        else:
            logger.error(f"Unsupported export format: {export_format}")
            return
        logger.info(f"✅ Successfully exported enhanced unified data to {output_path}")

    def _export_geojson_enhanced(self, data_to_export: Dict, output_path: str):
        """Enhanced GeoJSON export using SPACE utilities"""
        try:
            # Use SPACE H3 utilities for enhanced GeoJSON generation
            features = []
            for hex_id, properties in data_to_export.items():
                # Get geometry for the hexagon using SPACE utilities
                boundary = cell_to_latlng_boundary(hex_id)
                
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [boundary]
                    },
                    'properties': properties
                })
                
            feature_collection = {
                'type': 'FeatureCollection',
                'features': features,
                'properties': {
                    'generated_by': 'GEO-INFER-SPACE Enhanced Cascadian Backend',
                    'timestamp': datetime.now().isoformat(),
                    'h3_resolution': self.resolution,
                    'spatial_analysis': self.spatial_analysis_results
                }
            }
            
            with open(output_path, 'w') as f:
                json.dump(feature_collection, f, cls=NumpyEncoder)
                
            logger.info(f"✅ Enhanced GeoJSON export completed with {len(features)} features")
            
        except Exception as e:
            logger.error(f"❌ Enhanced GeoJSON export failed: {e}")
            # Fall back to basic export
            self._export_geojson(data_to_export, output_path)

    def _export_geojson(self, data_to_export: Dict, output_path: str):
        """Basic GeoJSON export (fallback)"""
        features = []
        for hex_id, properties in data_to_export.items():
            # Get geometry for the hexagon
            boundary = h3.cell_to_boundary(hex_id)
            
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [boundary]
                },
                'properties': properties
            })
            
        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        with open(output_path, 'w') as f:
            json.dump(feature_collection, f, cls=NumpyEncoder)

    def _export_csv(self, data_to_export: Dict, output_path: str):
        """Enhanced CSV export with spatial analysis data"""
        # This will flatten the nested dictionary structure
        flat_data = []
        for hex_id, props in data_to_export.items():
            row = {'h3_index': hex_id}
            for key, value in props.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        row[f"{key}_{sub_key}"] = sub_value
                else:
                    row[key] = value
            flat_data.append(row)
        
        df = pd.DataFrame(flat_data)
        df.to_csv(output_path, index=False)

    def generate_interactive_dashboard(self, output_path: str) -> None:
        """
        Enhanced interactive dashboard generation with SPACE visualization.
        
        Args:
            output_path: Path to save the HTML dashboard file.
        """
        if not self.unified_data:
            logger.error("No unified data available to generate a dashboard.")
            return

        # Define a sensible default if no hexagons are available
        if not self.target_hexagons:
            map_center = [44.0, -120.5] # Default to center of Oregon
        else:
            # Calculate the centroid of the entire target region for the map center
            all_boundaries = [Polygon(h3.cell_to_boundary(h)) for h in self.target_hexagons]
            gdf_all = gpd.GeoDataFrame({'geometry': all_boundaries}, crs="EPSG:4326")
            unified_geom = gdf_all.unary_union
            centroid = unified_geom.centroid
            map_center = [centroid.y, centroid.x]

        logger.info(f"Generating enhanced interactive dashboard centered at {map_center}...")
        m = folium.Map(location=map_center, zoom_start=7, tiles='CartoDB positron')

        # Enhanced title with SPACE integration info
        title_html = f'''
            <h3 style="text-align: center; color: #333; padding: 10px; background-color: #f0f0f0; border-radius: 5px; font-family: 'Arial', sans-serif;">
                🗺️ Enhanced Cascadian Agricultural Land Redevelopment Potential Dashboard
            </h3>
            <p style="text-align: center; color: #666; font-size: 12px;">
                🔷 Powered by GEO-INFER-SPACE with H3 spatial indexing and OSC integration
            </p>
            <p style="text-align: center; color: #888; font-size: 10px;">
                📊 Spatial Analysis: {len(self.spatial_analysis_results)} features | 🔥 Hotspots: {len(self.hotspot_analysis.get('hotspot_hexagons', []))} | 📈 Correlations: {len(self.h3_spatial_correlations)}
            </p>
        '''
        m.get_root().header.add_child(folium.Element(title_html))

        folium.TileLayer('Stamen Terrain', attr='Stamen').add_to(m)
        
        # Enhanced Feature Groups with SPACE integration
        groups = {
            'redevelopment': folium.FeatureGroup(name="Redevelopment Potential", show=True),
            'zoning': folium.FeatureGroup(name="Zoning", show=False),
            'current_use': folium.FeatureGroup(name="Current Use", show=False),
            'water': folium.FeatureGroup(name="Water Security", show=False),
            'ownership': folium.FeatureGroup(name="Ownership Concentration", show=False),
            'spatial_analysis': folium.FeatureGroup(name="Spatial Analysis", show=False)
        }

        # Enhanced layer population with SPACE data
        for h3_index, hex_data in self.unified_data.items():
            boundary = hex_data.get('boundary')
            if not boundary: continue
            
            # Redevelopment Layer with enhanced popup
            score_data = self.redevelopment_scores.get(h3_index, {})
            score = score_data.get('composite_score', 0)
            spatial_context = score_data.get('spatial_context', {})
            
            popup_html = f"""
                <b>H3:</b> {h3_index}<br>
                <b>Score:</b> {score:.3f}<br>
                <b>Neighbors:</b> {spatial_context.get('neighbor_count', 0)}<br>
                <b>Cluster:</b> {spatial_context.get('spatial_cluster', 'Unknown')}<br>
                <b>Hotspot:</b> {'Yes' if spatial_context.get('is_hotspot', False) else 'No'}
            """
            
            folium.Polygon(
                locations=boundary,
                color=self._get_color_for_score(score),
                fill_color=self._get_color_for_score(score),
                weight=1, fill_opacity=0.6,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"Redevelopment Score: {score:.3f}"
            ).add_to(groups['redevelopment'])

            # Enhanced Zoning Layer
            zoning_data = hex_data.get('zoning', {})
            if zoning_data:
                z_popup = f"<b>H3:</b> {h3_index}<br><b>Zone:</b> {zoning_data.get('zone_type', 'N/A')}<br><b>Score:</b> {zoning_data.get('score', 0):.3f}"
                folium.Polygon(
                    locations=boundary, color="purple", weight=1, fill_opacity=0.5,
                    popup=z_popup, tooltip=f"Zone: {zoning_data.get('zone_type', 'N/A')}"
                ).add_to(groups['zoning'])
                
            # Enhanced Current Use Layer
            use_data = hex_data.get('current_use', {})
            if use_data:
                u_popup = f"<b>H3:</b> {h3_index}<br><b>Use:</b> {use_data.get('primary_use', 'N/A')}<br><b>Intensity:</b> {use_data.get('agricultural_intensity', 0):.3f}"
                folium.Polygon(
                    locations=boundary, color="green", weight=1, fill_opacity=0.5,
                    popup=u_popup, tooltip=f"Use: {use_data.get('primary_use', 'N/A')}"
                ).add_to(groups['current_use'])

            # Enhanced Spatial Analysis Layer
            if h3_index in self.hotspot_analysis.get('hotspot_hexagons', []):
                sa_popup = f"""
                    <b>H3:</b> {h3_index}<br>
                    <b>Hotspot:</b> Yes<br>
                    <b>Threshold:</b> {self.hotspot_analysis.get('hotspot_threshold', 0):.3f}<br>
                    <b>Mean Score:</b> {self.hotspot_analysis.get('mean_score', 0):.3f}
                """
                folium.Polygon(
                    locations=boundary, color="red", weight=2, fill_opacity=0.8,
                    popup=sa_popup, tooltip=f"🔥 Hotspot: {score:.3f}"
                ).add_to(groups['spatial_analysis'])

            # Enhanced Water Layer
            water_score = score_data.get('factors', {}).get('water', 0)
            w_popup = f"<b>H3:</b> {h3_index}<br><b>Water Score:</b> {water_score:.3f}<br><b>Surface Water:</b> {hex_data.get('surface_water', {}).get('water_security_score', 0):.3f}<br><b>Ground Water:</b> {hex_data.get('ground_water', {}).get('water_security_score', 0):.3f}"
            folium.Polygon(
                locations=boundary, color=self._get_color_for_score(water_score, 'blue'), 
                fill_color=self._get_color_for_score(water_score, 'blue'),
                weight=1, fill_opacity=0.6,
                popup=w_popup, tooltip=f"Water Score: {water_score:.3f}"
            ).add_to(groups['water'])

            # Enhanced Ownership Layer
            owner_score = score_data.get('factors', {}).get('ownership', 0)
            o_popup = f"<b>H3:</b> {h3_index}<br><b>Ownership Concentration:</b> {owner_score:.3f}<br><b>Cluster:</b> {spatial_context.get('spatial_cluster', 'Unknown')}"
            folium.Polygon(
                locations=boundary, color=self._get_color_for_score(owner_score, 'grey'), 
                fill_color=self._get_color_for_score(owner_score, 'grey'),
                weight=1, fill_opacity=0.6,
                popup=o_popup, tooltip=f"Ownership Score: {owner_score:.3f}"
            ).add_to(groups['ownership'])

            # Spatial Analysis Layer
            if spatial_context.get('is_hotspot', False):
                sa_popup = f"<b>H3:</b> {h3_index}<br><b>Hotspot:</b> Yes<br><b>Neighbor Score:</b> {spatial_context.get('neighbor_mean_score', 0):.3f}"
                folium.Polygon(
                    locations=boundary, color="red", weight=2, fill_opacity=0.8,
                    popup=sa_popup, tooltip="Spatial Hotspot"
                ).add_to(groups['spatial_analysis'])

        # Add layers to map
        for group in groups.values():
            group.add_to(m)

        # Enhanced Heatmap with spatial analysis
        heat_data = [
            [
                self.unified_data[h]['centroid'][1], 
                self.unified_data[h]['centroid'][0], 
                self.redevelopment_scores.get(h, {}).get('composite_score', 0)
            ]
            for h in self.target_hexagons 
            if h in self.unified_data and 'centroid' in self.unified_data[h] and self.unified_data[h]['centroid']
        ]

        if heat_data:
            HeatMap(heat_data, name="Redevelopment Heatmap", show=False).add_to(m)

        # Add enhanced layer control
        folium.LayerControl().add_to(m)
        
        try:
            m.save(output_path)
            logger.info(f"✅ Successfully generated enhanced interactive dashboard at {output_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save enhanced interactive dashboard to {output_path}: {e}")

    def _get_color_for_score(self, score: float, theme: str = 'default') -> str:
        """Enhanced color mapping with SPACE integration"""
        if not isinstance(score, (float, int)):
            return '#808080' # Grey for invalid score

        if theme == 'blue': # For water
            if score > 0.85: return '#d73027'
            elif score > 0.7: return '#fc8d59'
            elif score > 0.55: return '#fee08b'
            elif score > 0.4: return '#d9ef8b'
            elif score > 0.25: return '#91cf60'
            else: return '#1a9850'
        elif theme == 'grey': # For ownership
            if score > 0.75: return '#252525'
            if score > 0.5: return '#636363'
            if score > 0.25: return '#969696'
            return '#cccccc'
        else: # Default: Green-Yellow-Red
            if score > 0.75: return '#2ca25f'
            if score > 0.5: return '#99d8c9'
            if score > 0.25: return '#fed976'
            return '#e31a1c' 