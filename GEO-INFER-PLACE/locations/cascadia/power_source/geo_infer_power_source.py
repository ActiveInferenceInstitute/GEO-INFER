"""GeoInferPowerSource: Power Source Analysis Module"""

import numpy as np
from typing import Dict, List, Any
import logging
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

logger = logging.getLogger(__name__)

class GeoInferPowerSource:
    """Agricultural power source and energy infrastructure analysis with H3 spatial indexing"""
    
    def __init__(self, resolution: int = 8):
        self.resolution = resolution
        self.h3_power_source_data = {}
        logger.info(f"GeoInferPowerSource initialized with H3 resolution {resolution}")
    
    def analyze_hexagons(self, hexagon_list: List[str]) -> Dict[str, Any]:
        """
        Analyze power sources for a list of H3 hexagons
        
        Args:
            hexagon_list: List of H3 hexagon identifiers
            
        Returns:
            Dictionary mapping hexagon IDs to power source analysis results
        """
        results = {}
        
        for hexagon in hexagon_list:
            try:
                # Get hexagon center coordinates
                lat, lng = h3_to_geo(hexagon)
                
                # Generate fallback power source data based on location
                result = self._generate_fallback_power_data(lat, lng, hexagon)
                results[hexagon] = result
                
            except Exception as e:
                logger.warning(f"Error analyzing hexagon {hexagon}: {e}")
                results[hexagon] = {
                    'status': 'error',
                    'error': str(e),
                    'estimated_energy_consumption': 0.0,
                    'grid_reliability_score': 0.0
                }
        
        return results
    
    def _generate_fallback_power_data(self, lat: float, lng: float, hex_id: str) -> Dict[str, Any]:
        """
        Generate fallback power source data based on geographic location
        
        Args:
            lat: Latitude
            lng: Longitude
            hex_id: H3 hexagon ID
            
        Returns:
            Power source analysis result
        """
        # Determine state and region
        state = 'CA' if lat < 42.0 else 'OR'
        
        # Geographic-based power patterns
        if state == 'CA':
            if lng < -122.0:  # Coastal California - PG&E, high renewable potential
                utility_provider = 'PG&E'
                consumption = np.random.uniform(30000, 80000)
                renewable_capacity = np.random.uniform(15000, 40000)
                reliability_score = np.random.uniform(0.7, 0.9)
                independence_potential = np.random.uniform(0.4, 0.7)
                infrastructure_adequacy = np.random.uniform(0.6, 0.8)
            elif lat < 40.5:  # Central Valley - mixed utilities, high consumption
                utility_provider = np.random.choice(['PG&E', 'Modesto Irrigation District', 'Turlock Irrigation District'])
                consumption = np.random.uniform(60000, 150000)
                renewable_capacity = np.random.uniform(20000, 60000)
                reliability_score = np.random.uniform(0.6, 0.8)
                independence_potential = np.random.uniform(0.3, 0.6)
                infrastructure_adequacy = np.random.uniform(0.5, 0.7)
            else:  # Northern California - rural utilities, moderate consumption
                utility_provider = np.random.choice(['PG&E', 'Plumas-Sierra REC', 'Surprise Valley Electrification'])
                consumption = np.random.uniform(25000, 70000)
                renewable_capacity = np.random.uniform(10000, 35000)
                reliability_score = np.random.uniform(0.5, 0.8)
                independence_potential = np.random.uniform(0.5, 0.8)
                infrastructure_adequacy = np.random.uniform(0.4, 0.7)
        else:  # Oregon
            if lng < -122.0:  # Coastal Oregon - cooperative utilities, hydroelectric
                utility_provider = np.random.choice(['Central Lincoln PUD', 'Tillamook PUD', 'Coos-Curry Electric'])
                consumption = np.random.uniform(40000, 90000)
                renewable_capacity = np.random.uniform(25000, 60000)
                reliability_score = np.random.uniform(0.7, 0.9)
                independence_potential = np.random.uniform(0.6, 0.9)
                infrastructure_adequacy = np.random.uniform(0.6, 0.8)
            elif lat > 44.0:  # Northern Oregon - mixed utilities, renewable focus
                utility_provider = np.random.choice(['Portland General Electric', 'Columbia River PUD', 'Northern Wasco PUD'])
                consumption = np.random.uniform(35000, 85000)
                renewable_capacity = np.random.uniform(20000, 50000)
                reliability_score = np.random.uniform(0.8, 0.9)
                independence_potential = np.random.uniform(0.5, 0.8)
                infrastructure_adequacy = np.random.uniform(0.7, 0.9)
            else:  # Southern Oregon - diverse utilities, solar potential
                utility_provider = np.random.choice(['Pacific Power', 'Ashland Electric', 'Medford Electric'])
                consumption = np.random.uniform(30000, 75000)
                renewable_capacity = np.random.uniform(15000, 45000)
                reliability_score = np.random.uniform(0.6, 0.8)
                independence_potential = np.random.uniform(0.4, 0.7)
                infrastructure_adequacy = np.random.uniform(0.5, 0.7)
        
        return {
            'status': 'success',
            'hex_id': hex_id,
            'latitude': lat,
            'longitude': lng,
            'state': state,
            'primary_utility_provider': utility_provider,
            'estimated_energy_consumption': consumption,
            'renewable_energy_capacity': renewable_capacity,
            'grid_reliability_score': reliability_score,
            'agricultural_rate_availability': np.random.choice([True, False], p=[0.7, 0.3]),
            'energy_independence_potential': independence_potential,
            'power_infrastructure_adequacy': infrastructure_adequacy,
            'data_source': 'fallback'
        }
    
    def analyze_power_sources_h3(self, resolution: int = None) -> Dict[str, Dict]:
        """Agricultural power source analysis at H3 level"""
        if resolution is None:
            resolution = self.resolution
            
        h3_power_sources = {}
        
        # Generate valid H3 hexagons for demonstration
        sample_coordinates = [
            (40.0, -122.0), (40.5, -121.5), (41.0, -123.0), (41.5, -122.5),
            (42.0, -121.0), (42.5, -120.5), (43.0, -123.5), (43.5, -122.0),
            (44.0, -121.5), (44.5, -123.0), (45.0, -122.5), (45.5, -121.0),
        ]
        
        for lat, lon in sample_coordinates:
            try:
                hex_id = geo_to_h3(lat, lon, resolution)
                h3_power_sources[hex_id] = {
                    'primary_utility_provider': 'PG&E',
                    'estimated_energy_consumption': 50000.0,
                    'renewable_energy_capacity': 20000.0,
                    'grid_reliability_score': 0.8,
                    'agricultural_rate_availability': True,
                    'energy_independence_potential': 0.4,
                    'power_infrastructure_adequacy': 0.7
                }
            except Exception as e:
                logger.warning(f"Could not generate H3 hexagon for {lat}, {lon}: {e}")
                continue
        
        self.h3_power_source_data = h3_power_sources
        return h3_power_sources
    
    def get_summary_statistics(self) -> Dict[str, any]:
        """Get summary statistics for power source analysis"""
        return {
            'module': 'GeoInferPowerSource',
            'h3_resolution': self.resolution,
            'total_hexagons': len(self.h3_power_source_data)
        } 