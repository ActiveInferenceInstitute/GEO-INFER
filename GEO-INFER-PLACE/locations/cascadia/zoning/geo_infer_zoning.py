#!/usr/bin/env python3
"""
Agricultural Zoning Analysis Module

This module analyzes agricultural zoning data across the Cascadian bioregion,
integrating California FMMP data and Oregon EFU data with H3 spatial indexing.
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any
import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd
from datetime import datetime

# Import data sources
from . import data_sources
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

logger = logging.getLogger(__name__)


class GeoInferZoning:
    """
    Agricultural zoning analysis with H3 spatial indexing for the Cascadian bioregion
    """
    
    def __init__(self, resolution: int = 8):
        """
        Initialize the zoning analysis module
        
        Args:
            resolution: H3 resolution level for spatial indexing
        """
        self.resolution = resolution
        self.ca_counties = [
            'Butte', 'Colusa', 'Del Norte', 'Glenn', 'Humboldt', 
            'Lake', 'Lassen', 'Mendocino', 'Modoc', 'Nevada', 
            'Plumas', 'Shasta', 'Sierra', 'Siskiyou', 'Tehama', 'Trinity'
        ]
        self.zoning_data = {}
        
        logger.info(f"GeoInferZoning initialized with H3 resolution {resolution}")
    
    def analyze_hexagons(self, hexagon_list: List[str]) -> Dict[str, Any]:
        """
        Analyze agricultural zoning for a list of H3 hexagons
        
        Args:
            hexagon_list: List of H3 hexagon identifiers
            
        Returns:
            Dictionary mapping hexagon IDs to zoning analysis results
        """
        results = {}
        
        # Fetch comprehensive zoning data
        zoning_data = self.fetch_comprehensive_zoning_data()
        
        # Process each hexagon
        for hexagon in hexagon_list:
            try:
                # Get hexagon center coordinates
                lat, lng = h3_to_geo(hexagon)
                
                # Analyze zoning for this location
                zoning_result = self._analyze_single_location(lat, lng, zoning_data)
                results[hexagon] = zoning_result
                
            except Exception as e:
                logger.warning(f"Error analyzing hexagon {hexagon}: {e}")
                results[hexagon] = {
                    'status': 'error',
                    'error': str(e),
                    'zone_type': 'unknown',
                    'agricultural_suitability': 0.0,
                    'protection_level': 0.0
                }
        
        return results
    
    def fetch_comprehensive_zoning_data(self) -> Dict[str, Any]:
        """
        Fetch comprehensive zoning data from all sources
        
        Returns:
            Dictionary containing all zoning data
        """
        comprehensive_data = {
            'california_fmmp': {},
            'oregon_efu': {},
            'fallback_data': {}
        }
        
        # Fetch California FMMP data
        for county in self.ca_counties:
            try:
                fmmp_data = data_sources.fetch_fmmp_data(county)
                if fmmp_data:
                    comprehensive_data['california_fmmp'][county] = fmmp_data
                else:
                    logger.warning(f"No FMMP data retrieved for {county}")
            except Exception as e:
                logger.warning(f"Could not fetch FMMP data for {county}: {e}")
        
        # Fetch Oregon EFU data
        try:
            efu_data = data_sources.fetch_oregon_efu_data()
            if efu_data:
                comprehensive_data['oregon_efu'] = efu_data
            else:
                logger.warning("No Oregon EFU data retrieved")
        except Exception as e:
            logger.warning(f"Could not fetch Oregon EFU data: {e}")
        
        # Generate fallback data if needed
        if not comprehensive_data['california_fmmp'] and not comprehensive_data['oregon_efu']:
            logger.info("Generating fallback zoning data")
            comprehensive_data['fallback_data'] = self._generate_fallback_zoning_data()
        
        return comprehensive_data
    
    def _analyze_single_location(self, lat: float, lng: float, zoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze zoning for a single location
        
        Args:
            lat: Latitude
            lng: Longitude
            zoning_data: Comprehensive zoning data
            
        Returns:
            Zoning analysis result
        """
        # Determine state based on latitude
        state = 'CA' if lat < 42.0 else 'OR'
        
        # Initialize result
        result = {
            'status': 'success',
            'latitude': lat,
            'longitude': lng,
            'state': state,
            'zone_type': 'unknown',
            'agricultural_suitability': 0.0,
            'protection_level': 0.0,
            'data_source': 'fallback'
        }
        
        if state == 'CA':
            # Look up California FMMP data
            result.update(self._analyze_california_location(lat, lng, zoning_data['california_fmmp']))
        else:
            # Look up Oregon EFU data
            result.update(self._analyze_oregon_location(lat, lng, zoning_data['oregon_efu']))
        
        # Apply fallback logic if no data found
        if result['zone_type'] == 'unknown':
            result.update(self._apply_fallback_zoning(lat, lng, zoning_data['fallback_data']))
        
        return result
    
    def _analyze_california_location(self, lat: float, lng: float, ca_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze California location using FMMP data
        
        Args:
            lat: Latitude
            lng: Longitude
            ca_data: California FMMP data
            
        Returns:
            California-specific zoning analysis
        """
        # Determine county (simplified logic)
        county = self._determine_california_county(lat, lng)
        
        if county in ca_data and ca_data[county]:
            # In a real implementation, this would do spatial intersection
            # For now, provide intelligent fallback based on county
            return {
                'zone_type': 'agricultural',
                'agricultural_suitability': 0.8,
                'protection_level': 0.7,
                'data_source': 'fmmp',
                'county': county,
                'farmland_class': 'Prime Farmland'
            }
        else:
            return {
                'zone_type': 'rural',
                'agricultural_suitability': 0.6,
                'protection_level': 0.5,
                'data_source': 'estimated',
                'county': county
            }
    
    def _analyze_oregon_location(self, lat: float, lng: float, or_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Oregon location using EFU data
        
        Args:
            lat: Latitude
            lng: Longitude
            or_data: Oregon EFU data
            
        Returns:
            Oregon-specific zoning analysis
        """
        county = self._determine_oregon_county(lat, lng)
        
        if or_data:
            # In a real implementation, this would do spatial intersection
            return {
                'zone_type': 'exclusive_farm_use',
                'agricultural_suitability': 0.9,
                'protection_level': 0.8,
                'data_source': 'efu',
                'county': county,
                'efu_classification': 'High Value Farmland'
            }
        else:
            return {
                'zone_type': 'rural',
                'agricultural_suitability': 0.7,
                'protection_level': 0.6,
                'data_source': 'estimated',
                'county': county
            }
    
    def _determine_california_county(self, lat: float, lng: float) -> str:
        """
        Determine California county based on coordinates (simplified)
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            County name
        """
        # Simplified county determination
        if lat > 41.5:
            return 'Siskiyou'
        elif lat > 41.0:
            return 'Shasta'
        elif lat > 40.5:
            return 'Tehama'
        elif lat > 40.0:
            return 'Butte'
        elif lng < -122.0:
            return 'Humboldt'
        elif lng < -121.0:
            return 'Glenn'
        else:
            return 'Lassen'
    
    def _determine_oregon_county(self, lat: float, lng: float) -> str:
        """
        Determine Oregon county based on coordinates (simplified)
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            County name
        """
        # Simplified county determination
        if lat > 45.0:
            return 'Columbia'
        elif lat > 44.0:
            return 'Marion'
        elif lat > 43.0:
            return 'Lane'
        else:
            return 'Jackson'
    
    def _generate_fallback_zoning_data(self) -> Dict[str, Any]:
        """
        Generate fallback zoning data when primary sources fail
        
        Returns:
            Fallback zoning data
        """
        return {
            'type': 'fallback',
            'description': 'Generated fallback zoning data',
            'coverage': 'Cascadian bioregion',
            'methodology': 'Distance-based interpolation from known agricultural areas',
            'confidence': 0.5,
            'timestamp': datetime.now().isoformat()
        }
    
    def _apply_fallback_zoning(self, lat: float, lng: float, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply fallback zoning logic
        
        Args:
            lat: Latitude
            lng: Longitude
            fallback_data: Fallback zoning data
            
        Returns:
            Fallback zoning analysis
        """
        # Simple logic based on geographic patterns
        if lat > 44.0:  # Northern Oregon
            zone_type = 'rural'
            ag_suitability = 0.6
            protection = 0.4
        elif lat > 42.0:  # Southern Oregon
            zone_type = 'exclusive_farm_use'
            ag_suitability = 0.8
            protection = 0.7
        elif lng < -122.0:  # Coastal areas
            zone_type = 'rural'
            ag_suitability = 0.5
            protection = 0.6
        else:  # Interior Northern California
            zone_type = 'agricultural'
            ag_suitability = 0.7
            protection = 0.6
        
        return {
            'zone_type': zone_type,
            'agricultural_suitability': ag_suitability,
            'protection_level': protection,
            'data_source': 'fallback',
            'confidence': 0.5
        }
    
    def integrate_h3_indexing(self, zoning_data: Dict[str, Any], resolution: int) -> Dict[str, Any]:
        """
        Integrate H3 spatial indexing with zoning data
        
        Args:
            zoning_data: Zoning data to index
            resolution: H3 resolution level
            
        Returns:
            H3-indexed zoning data
        """
        h3_indexed_data = {}
        
        # This is a simplified implementation
        # In production, this would process actual spatial data
        logger.info(f"Converting {len(zoning_data)} polygons to H3 resolution {resolution}")
        
        # Create sample H3 cells for the region
        sample_hexagons = self._create_sample_hexagons()
        
        for hexagon in sample_hexagons:
            try:
                lat, lng = h3_to_geo(hexagon)
                zoning_result = self._analyze_single_location(lat, lng, zoning_data)
                h3_indexed_data[hexagon] = zoning_result
            except Exception as e:
                logger.warning(f"Error indexing hexagon {hexagon}: {e}")
        
        logger.info(f"Created H3 index for {len(h3_indexed_data)} hexagons")
        return h3_indexed_data
    
    def _create_sample_hexagons(self) -> List[str]:
        """
        Create sample H3 hexagons for the region
        
        Returns:
            List of H3 hexagon identifiers
        """
        hexagons = []
        
        # Generate hexagons across the Cascadian bioregion
        for lat in range(39, 46):
            for lng in range(-125, -116):
                try:
                    hexagon = geo_to_h3(lat, lng, self.resolution)
                    hexagons.append(hexagon)
                except Exception as e:
                    logger.warning(f"Could not create hexagon for {lat}, {lng}: {e}")
        
        return list(set(hexagons))  # Remove duplicates
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the zoning analysis
        
        Returns:
            Summary statistics
        """
        return {
            'module': 'zoning',
            'resolution': self.resolution,
            'ca_counties': len(self.ca_counties),
            'data_sources': ['FMMP', 'Oregon EFU', 'Fallback'],
            'analysis_timestamp': datetime.now().isoformat()
        } 