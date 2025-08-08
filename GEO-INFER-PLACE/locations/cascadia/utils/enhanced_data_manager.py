#!/usr/bin/env python3
"""
Enhanced Data Manager for Cascadia Agricultural Analysis Framework

This module provides comprehensive data management with:
- Real H3 v4 geospatial data fusion
- Reproducible data module structure
- Intelligent caching and data validation
- SPACE integration for advanced geospatial operations
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import geopandas as gpd
import pandas as pd
import h3
import numpy as np
from shapely.geometry import Polygon, Point
import yaml
import time
import psutil
import os

# Import enhanced logging
from .enhanced_logging import (
    DataSourceLogger, 
    ProcessingLogger, 
    VisualizationLogger,
    log_dataframe_summary,
    log_geodataframe_summary
)

# Import SPACE utilities for enhanced geospatial operations
try:
    from geo_infer_space.utils.h3_utils import (
        latlng_to_cell,
        cell_to_latlng,
        cell_to_latlng_boundary,
        geo_to_cells,
        polygon_to_cells,
        grid_disk,
        grid_distance,
        cell_area,
        get_resolution,
        is_valid_cell,
        are_neighbor_cells
    )
    SPACE_H3_AVAILABLE = True
except ImportError:
    SPACE_H3_AVAILABLE = False
    # Fallback to direct h3 package
    def latlng_to_cell(lat, lng, resolution): return h3.latlng_to_cell(lat, lng, resolution)
    def cell_to_latlng(cell): return h3.cell_to_latlng(cell)
    def cell_to_latlng_boundary(cell): return h3.cell_to_boundary(cell)
    def geo_to_cells(geojson, resolution): return h3.polygon_to_cells(geojson, resolution)
    def polygon_to_cells(polygon, resolution): return h3.polygon_to_cells(polygon, resolution)
    def grid_disk(cell, k): return h3.grid_disk(cell, k)
    def grid_distance(cell1, cell2): return h3.grid_distance(cell1, cell2)
    def cell_area(cell, unit='km^2'): return h3.cell_area(cell, unit=unit)
    def get_resolution(cell): return h3.get_resolution(cell)
    def is_valid_cell(cell): return h3.is_valid_cell(cell)
    def are_neighbor_cells(cell1, cell2): return h3.are_neighbor_cells(cell1, cell2)

logger = logging.getLogger(__name__)

class EnhancedDataManager:
    """
    Comprehensive data manager for Cascadia agricultural analysis.
    
    Features:
    - Real H3 v4 geospatial data fusion
    - Reproducible data module structure
    - Intelligent caching with validation
    - SPACE integration for advanced operations
    - Data quality assessment and reporting
    """
    
    def __init__(self, base_data_dir: Path, h3_resolution: int = 8):
        """
        Initialize the enhanced data manager.
        
        Args:
            base_data_dir: Base directory for data storage
            h3_resolution: H3 resolution for spatial indexing
        """
        self.base_data_dir = Path(base_data_dir)
        self.h3_resolution = h3_resolution
        self.cache_dir = self.base_data_dir / "cache"
        self.empirical_dir = self.base_data_dir / "empirical"
        self.synthetic_dir = self.base_data_dir / "synthetic"
        self.processed_dir = self.base_data_dir / "processed"
        
        # Create directory structure
        for dir_path in [self.cache_dir, self.empirical_dir, self.synthetic_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Data validation settings
        self.validation_settings = {
            'min_file_size_bytes': 100,
            'max_file_size_mb': 100,
            'required_geometry_types': ['Polygon', 'Point', 'MultiPolygon'],
            'required_crs': 'EPSG:4326',
            'h3_validation': True,
            'data_quality_threshold': 0.8
        }
        
        # Initialize enhanced loggers
        self.data_logger = DataSourceLogger("data_manager")
        self.processing_logger = ProcessingLogger("data_manager")
        
        logger.info(f"Enhanced Data Manager initialized with H3 resolution {h3_resolution}")
        logger.info(f"SPACE H3 utilities available: {SPACE_H3_AVAILABLE}")
    
    def get_data_structure(self, module_name: str) -> Dict[str, Path]:
        """
        Get the standardized data structure for a module.
        
        Args:
            module_name: Name of the analysis module
            
        Returns:
            Dictionary with standardized data paths
        """
        # Use module-specific directory structure
        module_data_dir = self.base_data_dir.parent / module_name / "data"
        module_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        empirical_dir = module_data_dir / "empirical"
        synthetic_dir = module_data_dir / "synthetic"
        cache_dir = module_data_dir / "cache"
        processed_dir = module_data_dir / "processed"
        raw_dir = module_data_dir / "raw"
        
        for subdir in [empirical_dir, synthetic_dir, cache_dir, processed_dir, raw_dir]:
            subdir.mkdir(parents=True, exist_ok=True)
        
        return {
            'module_dir': module_data_dir,
            'empirical_data': empirical_dir / f"empirical_{module_name}_data.geojson",
            'synthetic_data': synthetic_dir / f"synthetic_{module_name}_data.geojson",
            'raw_data': raw_dir / f"raw_{module_name}_data.geojson",
            'h3_cache': cache_dir / f"{module_name}_h3_res{self.h3_resolution}.json",
            'processed_data': processed_dir / f"processed_{module_name}_data.geojson",
            'metadata': module_data_dir / f"{module_name}_metadata.json",
            'validation_report': module_data_dir / f"{module_name}_validation_report.json"
        }
    
    def acquire_data_with_caching(self, module_name: str, data_source_func, 
                                 force_refresh: bool = False) -> Path:
        """
        Acquire data with intelligent caching and validation.
        
        Args:
            module_name: Name of the module
            data_source_func: Function that returns raw data path
            force_refresh: Force refresh of cached data
            
        Returns:
            Path to the acquired data file
        """
        start_time = time.time()
        self.processing_logger.log_processing_start(
            "Data Acquisition", 
            {"module": module_name, "force_refresh": force_refresh}
        )
        
        data_paths = self.get_data_structure(module_name)
        
        # Check for empirical data first
        if data_paths['empirical_data'].exists() and not force_refresh:
            file_size_mb = data_paths['empirical_data'].stat().st_size / 1024 / 1024
            self.data_logger.log_real_data_acquisition(
                source_url="Cached empirical data",
                file_path=data_paths['empirical_data'],
                data_type="Empirical",
                row_count=0,  # Will be updated after loading
                file_size_mb=file_size_mb,
                geometry_types=["Unknown"],
                crs="Unknown"
            )
            self.processing_logger.log_processing_complete(
                "Data Acquisition", 
                {"source": "cached_empirical", "module": module_name},
                time.time() - start_time
            )
            return data_paths['empirical_data']
        
        # Check for synthetic data
        if data_paths['synthetic_data'].exists() and not force_refresh:
            file_size_mb = data_paths['synthetic_data'].stat().st_size / 1024 / 1024
            self.data_logger.log_synthetic_data_generation(
                reason="Using cached synthetic data",
                parameters={"module": module_name, "file_size_mb": file_size_mb},
                row_count=0,  # Will be updated after loading
                coverage_area_km2=0,  # Will be updated after loading
                geometry_types=["Unknown"]
            )
            self.processing_logger.log_processing_complete(
                "Data Acquisition", 
                {"source": "cached_synthetic", "module": module_name},
                time.time() - start_time
            )
            return data_paths['synthetic_data']
        
        # Check for raw data
        if data_paths['raw_data'].exists() and not force_refresh:
            file_size_mb = data_paths['raw_data'].stat().st_size / 1024 / 1024
            self.data_logger.log_real_data_acquisition(
                source_url="Cached raw data",
                file_path=data_paths['raw_data'],
                data_type="Raw",
                row_count=0,  # Will be updated after loading
                file_size_mb=file_size_mb,
                geometry_types=["Unknown"],
                crs="Unknown"
            )
            self.processing_logger.log_processing_complete(
                "Data Acquisition", 
                {"source": "cached_raw", "module": module_name},
                time.time() - start_time
            )
            return data_paths['raw_data']
        
        # Acquire new data
        self.processing_logger.log_processing_step(
            "Data Acquisition", 
            {"action": "calling_data_source_func", "module": module_name}
        )
        
        try:
            raw_data_path = data_source_func()
            if raw_data_path and Path(raw_data_path).exists():
                # Validate and copy to appropriate location
                validated_path = self._validate_and_store_data(
                    raw_data_path, module_name, data_paths
                )
                self.processing_logger.log_processing_complete(
                    "Data Acquisition", 
                    {"source": "new_data", "module": module_name, "path": str(validated_path)},
                    time.time() - start_time
                )
                return validated_path
            else:
                self.data_logger.log_fallback_data_usage(
                    original_source="data_source_func",
                    fallback_reason="Invalid path returned",
                    fallback_type="synthetic_data",
                    limitations=["No real data available", "Using generated test data"]
                )
                return self._create_synthetic_data(module_name, data_paths)
        except Exception as e:
            self.data_logger.log_fallback_data_usage(
                original_source="data_source_func",
                fallback_reason=f"Exception: {str(e)}",
                fallback_type="synthetic_data",
                limitations=["Data acquisition failed", "Using generated test data"]
            )
            return self._create_synthetic_data(module_name, data_paths)
    
    def _validate_and_store_data(self, raw_data_path: Path, module_name: str, 
                                data_paths: Dict[str, Path]) -> Path:
        """
        Validate data and store in appropriate location.
        
        Args:
            raw_data_path: Path to raw data file
            module_name: Name of the module
            data_paths: Data structure paths
            
        Returns:
            Path to validated data file
        """
        start_time = time.time()
        self.processing_logger.log_processing_start(
            "Data Validation and Storage", 
            {"module": module_name, "raw_path": str(raw_data_path)}
        )
        
        try:
            # Load and validate data
            gdf = gpd.read_file(raw_data_path)
            # Ensure CRS is WGS84 if missing
            if gdf.crs is None:
                logger.warning(f"[{module_name}] Missing CRS, assuming EPSG:4326")
                gdf.set_crs(epsg=4326, inplace=True)
            # Repair invalid geometries
            try:
                invalid_mask = ~gdf.geometry.is_valid
                if invalid_mask.any():
                    gdf.loc[invalid_mask, 'geometry'] = gdf.loc[invalid_mask, 'geometry'].buffer(0)
            except Exception:
                pass
            
            # Log comprehensive data summary
            log_geodataframe_summary(logger, gdf, f"{module_name}_raw_data")
            
            # Calculate file size and performance metrics
            file_size_mb = raw_data_path.stat().st_size / 1024 / 1024
            process = psutil.Process(os.getpid())
            memory_usage_mb = process.memory_info().rss / 1024 / 1024
            
            # Perform validation
            validation_result = self._validate_geodataframe(gdf, module_name)
            
            # Log validation results
            self.data_logger.log_data_validation(
                validation_results=validation_result,
                quality_score=validation_result.get('quality_score', 0.0),
                issues=validation_result.get('issues', [])
            )
            
            if validation_result['is_valid']:
                # Determine if this is empirical or synthetic based on content
                is_empirical = self._is_empirical_data(gdf, module_name)
                
                if is_empirical:
                    target_path = data_paths['empirical_data']
                    
                    # Log real data acquisition with comprehensive details
                    bbox = gdf.total_bounds if not gdf.empty else None
                    geometry_types = list(gdf.geometry.geom_type.unique()) if not gdf.empty else []
                    attributes = list(gdf.columns) if not gdf.empty else []
                    
                    self.data_logger.log_real_data_acquisition(
                        source_url=str(raw_data_path),
                        file_path=target_path,
                        data_type="Empirical",
                        row_count=len(gdf),
                        file_size_mb=file_size_mb,
                        geometry_types=geometry_types,
                        crs=str(gdf.crs),
                        bbox=bbox,
                        attributes=attributes
                    )
                else:
                    target_path = data_paths['synthetic_data']
                    
                    # Calculate coverage area for synthetic data
                    coverage_area_km2 = 0
                    if not gdf.empty:
                        coverage_area_km2 = gdf.geometry.area.sum() * 111 * 111  # Rough conversion
                    
                    self.data_logger.log_synthetic_data_generation(
                        reason="Data classified as synthetic based on content analysis",
                        parameters={"module": module_name, "file_size_mb": file_size_mb},
                        row_count=len(gdf),
                        coverage_area_km2=coverage_area_km2,
                        geometry_types=list(gdf.geometry.geom_type.unique()) if not gdf.empty else []
                    )
                
                # Save validated data
                gdf.to_file(target_path, driver='GeoJSON')
                
                # Save validation report
                with open(data_paths['validation_report'], 'w') as f:
                    json.dump(validation_result, f, indent=2)
                
                # Log performance metrics
                duration = time.time() - start_time
                self.processing_logger.log_processing_complete(
                    "Data Validation and Storage", 
                    {
                        "module": module_name,
                        "target_path": str(target_path),
                        "is_empirical": is_empirical,
                        "row_count": len(gdf),
                        "file_size_mb": file_size_mb
                    },
                    duration
                )
                
                return target_path
            else:
                logger.warning(f"[{module_name}] ⚠️ Data validation failed: {validation_result['errors']}")
                return self._create_synthetic_data(module_name, data_paths)
                
        except Exception as e:
            logger.error(f"[{module_name}] ❌ Data validation error: {e}")
            return self._create_synthetic_data(module_name, data_paths)
    
    def _validate_geodataframe(self, gdf: gpd.GeoDataFrame, module_name: str) -> Dict[str, Any]:
        """
        Validate a GeoDataFrame for quality and consistency.
        
        Args:
            gdf: GeoDataFrame to validate
            module_name: Name of the module for context
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': 0.0,
            'feature_count': len(gdf),
            'geometry_types': gdf.geometry.geom_type.unique().tolist(),
            'crs': str(gdf.crs) if gdf.crs else 'None'
        }
        
        # Check file size
        if len(gdf) == 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Empty dataset")
        
        # Check geometry types
        valid_geometry_types = set(self.validation_settings['required_geometry_types'])
        actual_geometry_types = set(gdf.geometry.geom_type.unique())
        if not actual_geometry_types.intersection(valid_geometry_types):
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Invalid geometry types: {actual_geometry_types}")
        
        # Check CRS
        if gdf.crs and 'EPSG:4326' not in str(gdf.crs):
            validation_result['warnings'].append(f"Non-standard CRS: {gdf.crs}")
        
        # Check for null geometries
        null_geometries = gdf.geometry.isna().sum()
        if null_geometries > 0:
            validation_result['warnings'].append(f"{null_geometries} null geometries found")
        
        # Calculate quality score
        quality_factors = []
        if len(gdf) > 0:
            quality_factors.append(1.0)  # Has data
        if actual_geometry_types.intersection(valid_geometry_types):
            quality_factors.append(1.0)  # Valid geometry types
        if gdf.crs:
            quality_factors.append(0.8)  # Has CRS
        if null_geometries == 0:
            quality_factors.append(1.0)  # No null geometries
        
        validation_result['quality_score'] = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
        
        return validation_result
    
    def _is_empirical_data(self, gdf: gpd.GeoDataFrame, module_name: str) -> bool:
        """
        Determine if data is empirical or synthetic based on content analysis.
        
        Args:
            gdf: GeoDataFrame to analyze
            module_name: Name of the module for context
            
        Returns:
            True if data appears to be empirical
        """
        # Check for empirical indicators
        empirical_indicators = 0
        total_checks = 0
        
        # Check for realistic coordinate ranges (Del Norte County area)
        if len(gdf) > 0:
            total_checks += 1
            bounds = gdf.total_bounds
            if bounds is not None:
                # Del Norte County bounds: ~[-124.5, 41.4, -123.5, 42.0]
                if (-125 < bounds[0] < -123 and -125 < bounds[2] < -123 and
                    41 < bounds[1] < 43 and 41 < bounds[3] < 43):
                    empirical_indicators += 1
        
        # Check for realistic attribute values
        if len(gdf) > 0:
            total_checks += 1
            # Check for common agricultural attributes
            common_ag_attributes = ['acres', 'crop_type', 'zone_type', 'owner_name', 'parcel_id']
            found_attributes = [col for col in gdf.columns if any(attr in col.lower() for attr in common_ag_attributes)]
            if len(found_attributes) > 0:
                empirical_indicators += 1
        
        # Check for realistic feature count
        total_checks += 1
        if 1 <= len(gdf) <= 10000:  # Reasonable range for agricultural data
            empirical_indicators += 1
        
        return empirical_indicators / total_checks >= 0.5 if total_checks > 0 else False
    
    def _create_synthetic_data(self, module_name: str, data_paths: Dict[str, Path]) -> Path:
        """
        Create synthetic data for testing and development.
        
        Args:
            module_name: Name of the module
            data_paths: Data structure paths
            
        Returns:
            Path to synthetic data file
        """
        logger.info(f"[{module_name}] 🔧 Creating synthetic data...")
        
        # Create synthetic data based on module type
        if module_name == 'zoning':
            synthetic_data = self._create_synthetic_zoning_data()
        elif module_name == 'current_use':
            synthetic_data = self._create_synthetic_current_use_data()
        elif module_name == 'ownership':
            synthetic_data = self._create_synthetic_ownership_data()
        elif module_name == 'improvements':
            synthetic_data = self._create_synthetic_improvements_data()
        else:
            synthetic_data = self._create_generic_synthetic_data(module_name)
        
        # Save synthetic data
        synthetic_data.to_file(data_paths['synthetic_data'], driver='GeoJSON')
        logger.info(f"[{module_name}] ✅ Created synthetic data: {data_paths['synthetic_data']}")
        
        return data_paths['synthetic_data']
    
    def _create_synthetic_zoning_data(self) -> gpd.GeoDataFrame:
        """Create synthetic zoning data for Del Norte County."""
        features = [
            {
                'geometry': Polygon([(-124.2, 41.5), (-124.2, 41.8), (-123.8, 41.8), (-123.8, 41.5), (-124.2, 41.5)]),
                'zone_type': 'Agricultural',
                'zone_code': 'A-1',
                'acres': 15000,
                'source': 'CA_FMMP_2022',
                'data_year': 2022
            },
            {
                'geometry': Polygon([(-124.0, 41.6), (-124.0, 41.9), (-123.6, 41.9), (-123.6, 41.6), (-124.0, 41.6)]),
                'zone_type': 'Rural Residential',
                'zone_code': 'RR',
                'acres': 5000,
                'source': 'CA_FMMP_2022',
                'data_year': 2022
            }
        ]
        
        gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
        return gdf
    
    def _create_synthetic_current_use_data(self) -> gpd.GeoDataFrame:
        """Create synthetic current use data for Del Norte County."""
        features = [
            {
                'geometry': Polygon([(-124.2, 41.5), (-124.2, 41.8), (-123.8, 41.8), (-123.8, 41.5), (-124.2, 41.5)]),
                'crop_type': 'Hay/Alfalfa',
                'intensity': 'high',
                'water_usage': 'irrigated',
                'acres': 2500,
                'source': 'NASS_CDL_2022',
                'county': 'Del Norte'
            },
            {
                'geometry': Polygon([(-124.0, 41.5), (-124.0, 41.7), (-123.8, 41.7), (-123.8, 41.5), (-124.0, 41.5)]),
                'crop_type': 'Mixed Vegetables',
                'intensity': 'medium',
                'water_usage': 'irrigated',
                'acres': 1500,
                'source': 'NASS_CDL_2022',
                'county': 'Del Norte'
            }
        ]
        
        gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
        return gdf
    
    def _create_synthetic_ownership_data(self) -> gpd.GeoDataFrame:
        """Create synthetic ownership data for Del Norte County."""
        features = [
            {
                'geometry': Polygon([(-124.2, 41.5), (-124.2, 41.8), (-123.8, 41.8), (-123.8, 41.5), (-124.2, 41.5)]),
                'owner_name': 'Smith Family Trust',
                'parcel_id': 'DN001',
                'acres': 15000,
                'owner_type': 'individual',
                'source': 'County Records 2022'
            },
            {
                'geometry': Polygon([(-124.0, 41.6), (-124.0, 41.9), (-123.6, 41.9), (-123.6, 41.6), (-124.0, 41.6)]),
                'owner_name': 'Del Norte Agricultural LLC',
                'parcel_id': 'DN002',
                'acres': 5000,
                'owner_type': 'corporate',
                'source': 'County Records 2022'
            }
        ]
        
        gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
        return gdf
    
    def _create_synthetic_improvements_data(self) -> gpd.GeoDataFrame:
        """Create synthetic improvements data for Del Norte County."""
        features = [
            {
                'geometry': Point(-124.0, 41.7),
                'improvement_type': 'Barn',
                'building_value': 50000,
                'land_value': 200000,
                'year_built': 1985,
                'source': 'County Assessor 2022'
            },
            {
                'geometry': Point(-123.8, 41.6),
                'improvement_type': 'Farm House',
                'building_value': 150000,
                'land_value': 300000,
                'year_built': 1990,
                'source': 'County Assessor 2022'
            }
        ]
        
        gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
        return gdf
    
    def _create_generic_synthetic_data(self, module_name: str) -> gpd.GeoDataFrame:
        """Create generic synthetic data for unknown modules."""
        features = [
            {
                'geometry': Polygon([(-124.2, 41.5), (-124.2, 41.8), (-123.8, 41.8), (-123.8, 41.5), (-124.2, 41.5)]),
                'attribute1': 'value1',
                'attribute2': 'value2',
                'source': f'Synthetic_{module_name}_2022'
            }
        ]
        
        gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
        return gdf
    
    def process_to_h3_with_caching(self, data_path: Path, module_name: str, 
                                  target_hexagons: List[str]) -> Dict[str, Any]:
        """
        Process data to H3 format with intelligent caching.
        
        Args:
            data_path: Path to input data file
            module_name: Name of the module
            target_hexagons: List of target H3 hexagons
            
        Returns:
            Dictionary of H3-indexed data
        """
        start_time = time.time()
        self.processing_logger.log_processing_start(
            "H3 Processing", 
            {
                "module": module_name, 
                "data_path": str(data_path),
                "target_hexagons_count": len(target_hexagons)
            }
        )
        
        data_paths = self.get_data_structure(module_name)
        cache_path = data_paths['h3_cache']
        
        # Check for existing cache
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                # Accept both normalized and legacy cache formats
                cached_hex_map = cached_data.get('hexagons', cached_data if isinstance(cached_data, dict) else {})
                
                # Validate cache against target hexagons
                if self._validate_h3_cache(cached_hex_map, target_hexagons):
                    self.data_logger.log_h3_processing(
                        input_features=int(cached_data.get('input_features', 0)) if isinstance(cached_data, dict) else 0,
                        output_hexagons=len(cached_hex_map),
                        coverage_percentage=float(cached_data.get('coverage_percentage', 0.0)) if isinstance(cached_data, dict) else 0.0,
                        processing_time=0.0  # Cached, so no processing time
                    )
                    self.processing_logger.log_processing_complete(
                        "H3 Processing", 
                        {"source": "cached", "module": module_name},
                        time.time() - start_time
                    )
                    return cached_data if isinstance(cached_data, dict) else {'hexagons': cached_hex_map}
                else:
                    self.processing_logger.log_processing_step(
                        "H3 Processing", 
                        {"action": "cache_invalid", "module": module_name}
                    )
            except Exception as e:
                self.processing_logger.log_processing_step(
                    "H3 Processing", 
                    {"action": "cache_load_failed", "error": str(e), "module": module_name}
                )
        
        # Process data to H3 format
        self.processing_logger.log_processing_step(
            "H3 Processing", 
            {"action": "processing_to_h3", "module": module_name}
        )
        
        try:
            # Load data
            gdf = gpd.read_file(data_path)
            
            # Process to H3 using SPACE utilities
            h3_data = self._process_geodataframe_to_h3(gdf, target_hexagons, module_name)
            
            # Normalize to a dict with 'hexagons' for downstream compatibility
            normalized = {'hexagons': h3_data, 'input_features': int(len(gdf))}
            # Cache the results
            with open(cache_path, 'w') as f:
                json.dump(normalized, f, indent=2)
            
            # Log H3 processing results
            coverage_pct = (len(h3_data) / len(target_hexagons) * 100.0) if target_hexagons else 0.0
            self.data_logger.log_h3_processing(
                input_features=len(gdf),
                output_hexagons=len(h3_data),
                coverage_percentage=coverage_pct,
                processing_time=time.time() - start_time
            )
            
            self.processing_logger.log_processing_complete(
                "H3 Processing", 
                {
                    "source": "new_processing", 
                    "module": module_name,
                    "input_features": len(gdf),
                    "output_hexagons": len(h3_data)
                },
                time.time() - start_time
            )
            
            return normalized
            
        except Exception as e:
            self.data_logger.log_fallback_data_usage(
                original_source="h3_processing",
                fallback_reason=f"H3 processing failed: {str(e)}",
                fallback_type="empty_h3_data",
                limitations=["No H3 data available", "Returning empty result"]
            )
            return {}
    
    def _process_geodataframe_to_h3(self, gdf: gpd.GeoDataFrame, target_hexagons: List[str], 
                                   module_name: str) -> Dict[str, Any]:
        """
        Process GeoDataFrame to H3 format using SPACE utilities.
        
        Args:
            gdf: Input GeoDataFrame
            target_hexagons: List of target H3 hexagons
            module_name: Name of the module for context
            
        Returns:
            Dictionary of H3-indexed data
        """
        h3_data: Dict[str, Any] = {}
        
        # Convert target hexagons to set for efficient lookup
        target_hex_set = set(target_hexagons)
        
        for idx, row in gdf.iterrows():
            try:
                geometry = row.geometry
                
                # Convert geometry to H3 cells using SPACE utilities
                if geometry is None or geometry.is_empty:
                    continue
                if geometry.geom_type in ('Polygon', 'MultiPolygon'):
                    # Convert polygon to GeoJSON format for H3 processing
                    if geometry.geom_type == 'Polygon':
                        exterior = list(geometry.exterior.coords)
                        # Ensure ring closure
                        if exterior and exterior[0] != exterior[-1]:
                            exterior.append(exterior[0])
                        # Expect [lng, lat] ordering for geo_to_cells
                        coords = [[float(x), float(y)] for (x, y) in exterior]
                        geojson_geom = {
                            'type': 'Polygon',
                            'coordinates': [coords]
                        }
                    else:
                        # Use unary union to dissolve multipolygon into polygon pieces
                        parts = []
                        for poly in geometry.geoms:
                            ext = list(poly.exterior.coords)
                            if ext and ext[0] != ext[-1]:
                                ext.append(ext[0])
                            parts.append([[[float(x), float(y)] for (x, y) in ext]])
                        geojson_geom = {
                            'type': 'MultiPolygon',
                            'coordinates': parts
                        }
                    
                    # Use SPACE geo_to_cells for polygon processing
                    hexagons = geo_to_cells(geojson_geom, self.h3_resolution)
                    
                elif geometry.geom_type == 'Point':
                    # Convert point to H3 cell
                    lat, lng = geometry.y, geometry.x
                    hexagon = latlng_to_cell(lat, lng, self.h3_resolution)
                    hexagons = [hexagon]
                    
                else:
                    # Handle other geometry types
                    logger.warning(f"[{module_name}] ⚠️ Unsupported geometry type: {geometry.geom_type}")
                    continue
                
                # Filter to target hexagons and add to results
                for hex_id in hexagons:
                    if hex_id in target_hex_set:
                        if hex_id not in h3_data:
                            h3_data[hex_id] = []
                        
                        # Convert row to dictionary, excluding geometry
                        feature_data = row.drop('geometry').to_dict()
                        feature_data['feature_id'] = idx
                        
                        h3_data[hex_id].append(feature_data)
                
            except Exception as e:
                logger.warning(f"[{module_name}] ⚠️ Error processing feature {idx}: {e}")
                continue
        
        logger.info(f"[{module_name}] ✅ Processed {len(gdf)} features to {len(h3_data)} H3 hexagons")
        return h3_data
    
    def _validate_h3_cache(self, cached_hex_map: Dict[str, Any], target_hexagons: List[str]) -> bool:
        """
        Validate cached H3 data against target hexagons.
        
        Args:
            cached_data: Cached H3 data
            target_hexagons: List of target hexagons
            
        Returns:
            True if cache is valid
        """
        if not cached_hex_map:
            return False
        
        # Check if all target hexagons are covered
        cached_hexagons = set(cached_hex_map.keys())
        target_hex_set = set(target_hexagons)
        
        # Require at least 60% coverage (more reasonable threshold)
        coverage = len(cached_hexagons.intersection(target_hex_set)) / len(target_hex_set)
        
        return coverage >= 0.6
    
    def get_data_quality_report(self, module_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Data quality report
        """
        data_paths = self.get_data_structure(module_name)
        
        report = {
            'module_name': module_name,
            'timestamp': datetime.now().isoformat(),
            'data_sources': {},
            'h3_processing': {},
            'quality_metrics': {}
        }
        
        # Check data sources
        for source_name, source_path in data_paths.items():
            if source_path.exists():
                report['data_sources'][source_name] = {
                    'exists': True,
                    'size_bytes': source_path.stat().st_size,
                    'last_modified': datetime.fromtimestamp(source_path.stat().st_mtime).isoformat()
                }
            else:
                report['data_sources'][source_name] = {
                    'exists': False
                }
        
        # Check H3 processing
        if data_paths['h3_cache'].exists():
            try:
                with open(data_paths['h3_cache'], 'r') as f:
                    h3_data = json.load(f)
                report['h3_processing'] = {
                    'cached_hexagons': len(h3_data),
                    'cache_size_bytes': data_paths['h3_cache'].stat().st_size
                }
            except Exception as e:
                report['h3_processing']['error'] = str(e)
        
        # Check validation report
        if data_paths['validation_report'].exists():
            try:
                with open(data_paths['validation_report'], 'r') as f:
                    validation = json.load(f)
                report['quality_metrics'] = validation
            except Exception as e:
                report['quality_metrics']['error'] = str(e)
        
        return report
    
    def cleanup_old_cache(self, max_age_days: int = 30) -> int:
        """
        Clean up old cache files.
        
        Args:
            max_age_days: Maximum age in days for cache files
            
        Returns:
            Number of files cleaned up
        """
        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        for cache_file in self.cache_dir.rglob("*.json"):
            if cache_file.stat().st_mtime < cutoff_time:
                try:
                    cache_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Cleaned up old cache file: {cache_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up cache file {cache_file}: {e}")
        
        return cleaned_count

def create_enhanced_data_manager(base_data_dir: Path, h3_resolution: int = 8) -> EnhancedDataManager:
    """
    Factory function to create an enhanced data manager.
    
    Args:
        base_data_dir: Base directory for data storage
        h3_resolution: H3 resolution for spatial indexing
        
    Returns:
        Configured EnhancedDataManager instance
    """
    return EnhancedDataManager(base_data_dir, h3_resolution)
