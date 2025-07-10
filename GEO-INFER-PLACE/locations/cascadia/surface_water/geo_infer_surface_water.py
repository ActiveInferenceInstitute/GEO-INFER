"""GeoInferSurfaceWater: Surface Water Rights Analysis Module"""

import numpy as np
from typing import Dict, List, Any
import logging
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

logger = logging.getLogger(__name__)

class GeoInferSurfaceWater:
    """Surface water rights analysis with H3 spatial indexing"""
    
    def __init__(self, resolution: int = 8):
        self.resolution = resolution
        self.h3_water_rights_data = {}
        logger.info(f"GeoInferSurfaceWater initialized with H3 resolution {resolution}")
    
    def analyze_hexagons(self, hexagon_list: List[str]) -> Dict[str, Any]:
        """
        Analyze surface water rights for a list of H3 hexagons
        
        Args:
            hexagon_list: List of H3 hexagon identifiers
            
        Returns:
            Dictionary mapping hexagon IDs to surface water analysis results
        """
        results = {}
        
        for hexagon in hexagon_list:
            try:
                # Get hexagon center coordinates
                lat, lng = h3_to_geo(hexagon)
                
                # Generate fallback surface water data based on location
                result = self._generate_fallback_surface_water_data(lat, lng, hexagon)
                results[hexagon] = result
                
            except Exception as e:
                logger.warning(f"Error analyzing hexagon {hexagon}: {e}")
                results[hexagon] = {
                    'status': 'error',
                    'error': str(e),
                    'total_water_allocation': 0.0,
                    'water_security_score': 0.0
                }
        
        return results
    
    def _generate_fallback_surface_water_data(self, lat: float, lng: float, hex_id: str) -> Dict[str, Any]:
        """
        Generate fallback surface water data based on geographic location
        
        Args:
            lat: Latitude
            lng: Longitude
            hex_id: H3 hexagon ID
            
        Returns:
            Surface water analysis result
        """
        # Determine state and region
        state = 'CA' if lat < 42.0 else 'OR'
        
        # Geographic-based water patterns
        if state == 'CA':
            if lng < -122.0:  # Coastal California - reliable water but limited rights
                water_allocation = np.random.uniform(50, 150)
                rights_count = np.random.randint(3, 8)
                senior_rights_ratio = np.random.uniform(0.4, 0.7)
                security_score = np.random.uniform(0.6, 0.8)
                seasonal_availability = np.random.choice(['High', 'Medium'], p=[0.7, 0.3])
            elif lat < 40.5:  # Central Valley - intensive irrigation, complex rights
                water_allocation = np.random.uniform(100, 300)
                rights_count = np.random.randint(5, 15)
                senior_rights_ratio = np.random.uniform(0.5, 0.8)
                security_score = np.random.uniform(0.5, 0.7)
                seasonal_availability = np.random.choice(['Medium', 'Low'], p=[0.6, 0.4])
            else:  # Northern California - moderate water availability
                water_allocation = np.random.uniform(80, 200)
                rights_count = np.random.randint(4, 10)
                senior_rights_ratio = np.random.uniform(0.6, 0.8)
                security_score = np.random.uniform(0.7, 0.9)
                seasonal_availability = np.random.choice(['High', 'Medium'], p=[0.8, 0.2])
        else:  # Oregon
            if lng < -122.0:  # Coastal Oregon - abundant water
                water_allocation = np.random.uniform(80, 180)
                rights_count = np.random.randint(2, 6)
                senior_rights_ratio = np.random.uniform(0.7, 0.9)
                security_score = np.random.uniform(0.8, 1.0)
                seasonal_availability = 'High'
            elif lat > 44.0:  # Northern Oregon - good water access
                water_allocation = np.random.uniform(60, 140)
                rights_count = np.random.randint(3, 8)
                senior_rights_ratio = np.random.uniform(0.6, 0.8)
                security_score = np.random.uniform(0.7, 0.9)
                seasonal_availability = np.random.choice(['High', 'Medium'], p=[0.8, 0.2])
            else:  # Southern Oregon - moderate water access
                water_allocation = np.random.uniform(70, 160)
                rights_count = np.random.randint(4, 9)
                senior_rights_ratio = np.random.uniform(0.5, 0.7)
                security_score = np.random.uniform(0.6, 0.8)
                seasonal_availability = np.random.choice(['Medium', 'High'], p=[0.6, 0.4])
        
        return {
            'status': 'success',
            'hex_id': hex_id,
            'latitude': lat,
            'longitude': lng,
            'state': state,
            'total_water_allocation': water_allocation,
            'number_of_rights': rights_count,
            'senior_rights_ratio': senior_rights_ratio,
            'irrigation_allocation_share': np.random.uniform(0.6, 0.9),
            'priority_date_range': f"{np.random.randint(1900, 1980)}-{np.random.randint(1990, 2020)}",
            'seasonal_availability': seasonal_availability,
            'water_security_score': security_score,
            'data_source': 'fallback'
        }
    
    def analyze_surface_water_rights_h3(self, resolution: int = None) -> Dict[str, Dict]:
        """Cross-border surface water rights analysis at H3 level"""
        if resolution is None:
            resolution = self.resolution
            
        h3_water_rights = {}
        
        # Generate valid H3 hexagons for demonstration
        sample_coordinates = [
            (40.0, -122.0), (40.5, -121.5), (41.0, -123.0), (41.5, -122.5),
            (42.0, -121.0), (42.5, -120.5), (43.0, -123.5), (43.5, -122.0),
            (44.0, -121.5), (44.5, -123.0), (45.0, -122.5), (45.5, -121.0),
        ]
        
        for lat, lon in sample_coordinates:
            try:
                hex_id = geo_to_h3(lat, lon, resolution)
                h3_water_rights[hex_id] = {
                    'total_water_allocation': 100.0,
                    'number_of_rights': 5,
                    'senior_rights_ratio': 0.6,
                    'irrigation_allocation_share': 0.8,
                    'priority_date_range': '1900-2020',
                    'seasonal_availability': 'High',
                    'water_security_score': 0.7
                }
            except Exception as e:
                logger.warning(f"Could not generate H3 hexagon for {lat}, {lon}: {e}")
                continue
        
        self.h3_water_rights_data = h3_water_rights
        return h3_water_rights
    
    def get_summary_statistics(self) -> Dict[str, any]:
        """Get summary statistics for surface water analysis"""
        return {
            'module': 'GeoInferSurfaceWater',
            'h3_resolution': self.resolution,
            'total_hexagons': len(self.h3_water_rights_data)
        } 