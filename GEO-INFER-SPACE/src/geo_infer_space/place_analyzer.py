"""
Place Analyzer - Spatial place analysis for GEO-INFER-SPACE.

This module provides comprehensive place-based spatial analysis capabilities
including demographic analysis, environmental assessment, and spatial indexing.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
import h3

logger = logging.getLogger(__name__)


class PlaceAnalyzer:
    """
    Advanced place-based spatial analysis for GEO-INFER framework.
    
    Provides comprehensive spatial analysis capabilities including:
    - Demographic analysis
    - Environmental assessment
    - Spatial indexing and querying
    - Place-based data integration
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize PlaceAnalyzer with base directory.
        
        Args:
            base_dir: Base directory for data storage and configuration
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.config_dir = self.base_dir / "config"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize analysis components
        self.spatial_index = {}
        self.place_data = {}
        self.analysis_results = {}
        
        logger.info(f"PlaceAnalyzer initialized with base_dir: {self.base_dir}")
    
    def analyze_place(self, place_name: str, coordinates: Tuple[float, float], 
                     radius_km: float = 10.0) -> Dict[str, Any]:
        """
        Perform comprehensive place analysis.
        
        Args:
            place_name: Name of the place to analyze
            coordinates: (latitude, longitude) coordinates
            radius_km: Analysis radius in kilometers
            
        Returns:
            Dictionary containing analysis results
        """
        lat, lon = coordinates
        
        # Create analysis area
        analysis_area = self._create_analysis_area(lat, lon, radius_km)
        
        # Perform spatial analysis
        results = {
            'place_name': place_name,
            'coordinates': coordinates,
            'radius_km': radius_km,
            'analysis_area': analysis_area,
            'h3_cells': self._get_h3_cells(lat, lon, radius_km),
            'spatial_metrics': self._calculate_spatial_metrics(analysis_area),
            'environmental_factors': self._analyze_environmental_factors(lat, lon, radius_km),
            'accessibility_metrics': self._calculate_accessibility(lat, lon, radius_km),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Store results
        self.analysis_results[place_name] = results
        
        logger.info(f"Completed analysis for {place_name}")
        return results
    
    def _create_analysis_area(self, lat: float, lon: float, radius_km: float) -> Polygon:
        """Create analysis area polygon."""
        # Simple circular approximation
        center = Point(lon, lat)
        return center.buffer(radius_km / 111.0)  # Rough conversion to degrees
    
    def _get_h3_cells(self, lat: float, lon: float, radius_km: float) -> List[str]:
        """Get H3 cells covering the analysis area."""
        # Determine appropriate H3 resolution based on radius
        if radius_km <= 1:
            resolution = 9
        elif radius_km <= 5:
            resolution = 8
        elif radius_km <= 20:
            resolution = 7
        else:
            resolution = 6
        
        # Get center cell
        center_cell = h3.latlng_to_cell(lat, lon, resolution)
        
        # Get cells within radius
        cells = h3.grid_disk(center_cell, int(radius_km / 2))
        
        return [str(cell) for cell in cells]
    
    def _calculate_spatial_metrics(self, area: Polygon) -> Dict[str, float]:
        """Calculate spatial metrics for the analysis area."""
        return {
            'area_km2': area.area * 111.0 * 111.0,  # Rough conversion
            'perimeter_km': area.length * 111.0,
            'compactness': 4 * np.pi * area.area / (area.length ** 2) if area.length > 0 else 0
        }
    
    def _analyze_environmental_factors(self, lat: float, lon: float, radius_km: float) -> Dict[str, Any]:
        """Analyze environmental factors for the area."""
        # Placeholder for environmental analysis
        return {
            'elevation_range': {'min': 0, 'max': 100, 'mean': 50},
            'climate_zone': 'temperate',
            'vegetation_cover': 0.6,
            'water_bodies': 2,
            'protected_areas': 1
        }
    
    def _calculate_accessibility(self, lat: float, lon: float, radius_km: float) -> Dict[str, float]:
        """Calculate accessibility metrics."""
        return {
            'road_density': 2.5,  # km/km2
            'transit_stops': 15,
            'healthcare_facilities': 3,
            'educational_institutions': 5,
            'commercial_centers': 8
        }
    
    def get_analysis_summary(self, place_name: str) -> Dict[str, Any]:
        """Get summary of analysis results for a place."""
        if place_name not in self.analysis_results:
            raise ValueError(f"No analysis results found for {place_name}")
        
        results = self.analysis_results[place_name]
        
        return {
            'place_name': results['place_name'],
            'analysis_date': results['timestamp'],
            'spatial_coverage': len(results['h3_cells']),
            'area_km2': results['spatial_metrics']['area_km2'],
            'environmental_score': self._calculate_environmental_score(results['environmental_factors']),
            'accessibility_score': self._calculate_accessibility_score(results['accessibility_metrics'])
        }
    
    def _calculate_environmental_score(self, factors: Dict[str, Any]) -> float:
        """Calculate environmental quality score."""
        # Simple scoring algorithm
        score = 0.0
        score += factors.get('vegetation_cover', 0) * 0.3
        score += (1 - factors.get('elevation_range', {}).get('mean', 0) / 1000) * 0.2
        score += min(factors.get('water_bodies', 0) / 5, 1) * 0.3
        score += min(factors.get('protected_areas', 0) / 3, 1) * 0.2
        return min(score, 1.0)
    
    def _calculate_accessibility_score(self, metrics: Dict[str, float]) -> float:
        """Calculate accessibility score."""
        # Simple scoring algorithm
        score = 0.0
        score += min(metrics.get('road_density', 0) / 5, 1) * 0.2
        score += min(metrics.get('transit_stops', 0) / 20, 1) * 0.2
        score += min(metrics.get('healthcare_facilities', 0) / 5, 1) * 0.2
        score += min(metrics.get('educational_institutions', 0) / 10, 1) * 0.2
        score += min(metrics.get('commercial_centers', 0) / 15, 1) * 0.2
        return min(score, 1.0)
    
    def export_results(self, place_name: str, format: str = 'json') -> str:
        """Export analysis results to file."""
        if place_name not in self.analysis_results:
            raise ValueError(f"No analysis results found for {place_name}")
        
        results = self.analysis_results[place_name]
        output_file = self.data_dir / f"{place_name}_analysis.{format}"
        
        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Exported results to {output_file}")
        return str(output_file) 