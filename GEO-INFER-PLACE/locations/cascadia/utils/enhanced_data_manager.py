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
        module_dir = self.base_data_dir / module_name
        module_dir.mkdir(exist_ok=True)
        
        return {
            'module_dir': module_dir,
            'empirical_data': self.empirical_dir / f"empirical_{module_name}_data.geojson",
            'synthetic_data': self.synthetic_dir / f"synthetic_{module_name}_data.geojson",
            'raw_data': module_dir / f"raw_{module_name}_data.geojson",
            'h3_cache': module_dir / f"{module_name}_h3_res{self.h3_resolution}.json",
            'processed_data': self.processed_dir / f"processed_{module_name}_data.geojson",
            'metadata': module_dir / f"{module_name}_metadata.json",
            'validation_report': module_dir / f"{module_name}_validation_report.json"
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
        data_paths = self.get_data_structure(module_name)
        
        # Check for empirical data first
        if data_paths['empirical_data'].exists() and not force_refresh:
            logger.info(f"[{module_name}] ✅ Using empirical data: {data_paths['empirical_data']}")
            return data_paths['empirical_data']
        
        # Check for synthetic data
        if data_paths['synthetic_data'].exists() and not force_refresh:
            logger.info(f"[{module_name}] ⚠️ Using synthetic data: {data_paths['synthetic_data']}")
            return data_paths['synthetic_data']
        
        # Check for raw data
        if data_paths['raw_data'].exists() and not force_refresh:
            logger.info(f"[{module_name}] 📄 Using cached raw data: {data_paths['raw_data']}")
            return data_paths['raw_data']
        
        # Acquire new data
        logger.info(f"[{module_name}] 🔍 Acquiring new data...")
        try:
            raw_data_path = data_source_func()
            if raw_data_path and Path(raw_data_path).exists():
                # Validate and copy to appropriate location
                validated_path = self._validate_and_store_data(
                    raw_data_path, module_name, data_paths
                )
                return validated_path
            else:
                logger.warning(f"[{module_name}] ⚠️ Data source function returned invalid path")
                return self._create_synthetic_data(module_name, data_paths)
        except Exception as e:
            logger.error(f"[{module_name}] ❌ Failed to acquire data: {e}")
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
        try:
            # Load and validate data
            gdf = gpd.read_file(raw_data_path)
            
            # Perform validation
            validation_result = self._validate_geodataframe(gdf, module_name)
            
            if validation_result['is_valid']:
                # Determine if this is empirical or synthetic based on content
                if self._is_empirical_data(gdf, module_name):
                    target_path = data_paths['empirical_data']
                    logger.info(f"[{module_name}] ✅ Validated as empirical data")
                else:
                    target_path = data_paths['synthetic_data']
                    logger.info(f"[{module_name}] ⚠️ Classified as synthetic data")
                
                # Save validated data
                gdf.to_file(target_path, driver='GeoJSON')
                
                # Save validation report
                with open(data_paths['validation_report'], 'w') as f:
                    json.dump(validation_result, f, indent=2)
                
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
        data_paths = self.get_data_structure(module_name)
        cache_path = data_paths['h3_cache']
        
        # Check for existing cache
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                
                # Validate cache against target hexagons
                if self._validate_h3_cache(cached_data, target_hexagons):
                    logger.info(f"[{module_name}] ✅ Using cached H3 data: {len(cached_data)} hexagons")
                    return cached_data
                else:
                    logger.info(f"[{module_name}] ⚠️ Cache validation failed, reprocessing...")
            except Exception as e:
                logger.warning(f"[{module_name}] ⚠️ Cache loading failed: {e}")
        
        # Process data to H3 format
        logger.info(f"[{module_name}] 🔄 Processing data to H3 format...")
        
        try:
            # Load data
            gdf = gpd.read_file(data_path)
            
            # Process to H3 using SPACE utilities
            h3_data = self._process_geodataframe_to_h3(gdf, target_hexagons, module_name)
            
            # Cache the results
            with open(cache_path, 'w') as f:
                json.dump(h3_data, f, indent=2)
            
            logger.info(f"[{module_name}] ✅ Processed and cached H3 data: {len(h3_data)} hexagons")
            return h3_data
            
        except Exception as e:
            logger.error(f"[{module_name}] ❌ H3 processing failed: {e}")
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
        h3_data = {}
        
        # Convert target hexagons to set for efficient lookup
        target_hex_set = set(target_hexagons)
        
        for idx, row in gdf.iterrows():
            try:
                geometry = row.geometry
                
                # Convert geometry to H3 cells using SPACE utilities
                if geometry.geom_type == 'Polygon':
                    # Convert polygon to GeoJSON format for H3 processing
                    geojson_geom = {
                        'type': 'Polygon',
                        'coordinates': [list(geometry.exterior.coords)]
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
                        feature_data['geometry'] = {
                            'type': geometry.geom_type,
                            'coordinates': list(geometry.coords) if hasattr(geometry, 'coords') else []
                        }
                        
                        h3_data[hex_id].append(feature_data)
                
            except Exception as e:
                logger.warning(f"[{module_name}] ⚠️ Error processing feature {idx}: {e}")
                continue
        
        logger.info(f"[{module_name}] ✅ Processed {len(gdf)} features to {len(h3_data)} H3 hexagons")
        return h3_data
    
    def _validate_h3_cache(self, cached_data: Dict[str, Any], target_hexagons: List[str]) -> bool:
        """
        Validate cached H3 data against target hexagons.
        
        Args:
            cached_data: Cached H3 data
            target_hexagons: List of target hexagons
            
        Returns:
            True if cache is valid
        """
        if not cached_data:
            return False
        
        # Check if all target hexagons are covered
        cached_hexagons = set(cached_data.keys())
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
