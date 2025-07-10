#!/usr/bin/env python3
"""
Data Sources for Agricultural Zoning Analysis

This module provides data access functions for various agricultural zoning
data sources including California FMMP and Oregon EFU data.
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
import geopandas as gpd
import os
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

logger = logging.getLogger(__name__)


class CascadianZoningDataSources:
    """
    Unified data sources for Cascadian agricultural zoning analysis
    """
    
    def __init__(self):
        """Initialize the zoning data sources"""
        self.california_counties = [
            'Butte', 'Colusa', 'Del Norte', 'Glenn', 'Humboldt', 
            'Lake', 'Lassen', 'Mendocino', 'Modoc', 'Nevada', 
            'Plumas', 'Shasta', 'Sierra', 'Siskiyou', 'Tehama', 'Trinity'
        ]
        self.oregon_counties = [
            'Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 
            'Crook', 'Curry', 'Deschutes', 'Douglas', 'Gilliam', 'Grant', 
            'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josephine', 
            'Klamath', 'Lake', 'Lane', 'Lincoln', 'Linn', 'Malheur', 
            'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 
            'Umatilla', 'Union', 'Wallowa', 'Wasco', 'Washington', 'Wheeler', 'Yamhill'
        ]
        logger.info("CascadianZoningDataSources initialized")
    
    def fetch_all_zoning_data(self) -> Dict[str, Any]:
        """
        Fetch all zoning data for the Cascadian bioregion
        
        Returns:
            Comprehensive zoning data dictionary
        """
        return fetch_comprehensive_zoning_data(
            self.california_counties, 
            ['CA', 'OR']
        )


def fetch_fmmp_data(county: str, retry_count: int = 3) -> Optional[Dict[str, Any]]:
    shapefile_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fmmp', f"{county.lower()}_fmmp.shp")
    shapefile_path = os.path.abspath(shapefile_path)
    
    if os.path.exists(shapefile_path):
        try:
            gdf = gpd.read_file(shapefile_path)
            if 'COUNTY' in gdf.columns:
                gdf = gdf[gdf['COUNTY'].str.lower() == county.lower()]
            geojson = json.loads(gdf.to_json())
            logger.info(f"Loaded {len(geojson.get('features', []))} FMMP features for {county} from local shapefile.")
            return geojson
        except Exception as e:
            logger.error(f"Error loading local FMMP shapefile for {county}: {e}")
    
    # Fetch from API if local file missing or failed
    logger.info(f"Local shapefile not found or failed. Fetching FMMP data for {county} from API.")
    url = "https://gis.conservation.ca.gov/server/rest/services/DLRP/CaliforniaImportantFarmland_mostrecent/FeatureServer/0/query"
    params = {
        'where': f"COUNTY = '{county.upper()}'",
        'outFields': '*',
        'f': 'geojson',
        'returnGeometry': 'true'
    }
    for attempt in range(retry_count):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, params=params, timeout=30, headers=headers)
            response.raise_for_status()
            geojson = response.json()
            if 'features' in geojson:
                logger.info(f"Fetched {len(geojson['features'])} FMMP features for {county} from API.")
                return geojson
            else:
                logger.warning(f"No features returned for {county}")
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed to fetch FMMP data for {county}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    logger.error(f"Failed to fetch FMMP data for {county} after {retry_count} attempts.")
    return None


def fetch_oregon_efu_data(county: str, retry_count: int = 3) -> Optional[Dict[str, Any]]:
    """
    Fetch Oregon zoning data for the specified county
    
    Args:
        county: County name
        retry_count: Number of retry attempts
        
    Returns:
        Oregon zoning data or None if fetch fails
    """
    logger.info(f"Fetching Oregon zoning data for {county}")
    
    shapefile_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'oregon_zoning', f"{county.lower()}_zoning.shp")
    shapefile_path = os.path.abspath(shapefile_path)
    
    if os.path.exists(shapefile_path):
        try:
            gdf = gpd.read_file(shapefile_path)
            geojson = json.loads(gdf.to_json())
            logger.info(f"Loaded {len(geojson.get('features', []))} zoning features for {county} from local shapefile.")
            return geojson
        except Exception as e:
            logger.error(f"Error loading local zoning shapefile for {county}: {e}")
    
    # Fetch from API if local file missing or failed
    logger.info(f"Local shapefile not found or failed. Fetching zoning data for {county} from DLCD API.")
    url = "https://services.arcgis.com/uUvJ8eSSKhJ30d6A/arcgis/rest/services/Statewide_Zoning_2023/FeatureServer/0/query"
    params = {
        'where': f"COUNTY = '{county.upper()}'",
        'outFields': '*',
        'f': 'geojson',
        'returnGeometry': 'true'
    }
    for attempt in range(retry_count):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, params=params, timeout=30, headers=headers)
            response.raise_for_status()
            geojson = response.json()
            if 'features' in geojson:
                # Optionally filter for EFU or agricultural zones
                features = [f for f in geojson['features'] if f['properties'].get('Zoning_Code') in ['EFU', 'AF-20', 'other_ag_codes']]  # Adjust based on actual codes
                geojson['features'] = features
                logger.info(f"Fetched {len(features)} zoning features for {county} from API.")
                return geojson
            else:
                logger.warning(f"No features returned for {county}")
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed to fetch zoning data for {county}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    logger.error(f"Failed to fetch zoning data for {county} after {retry_count} attempts.")
    return None


def fetch_alternative_zoning_data(county: str, state: str) -> Optional[Dict[str, Any]]:
    """
    Fetch alternative zoning data sources when primary sources fail
    
    Args:
        county: County name
        state: State abbreviation (CA or OR)
        
    Returns:
        Alternative zoning data or None
    """
    logger.info(f"Fetching alternative zoning data for {county}, {state}")
    
    # This would implement fallback data sources such as:
    # - USDA NASS data
    # - Commercial parcel data
    # - County GIS services
    # - Open data portals
    
    try:
        # Placeholder for alternative data sources
        alternative_data = {
            'type': 'FeatureCollection',
            'features': [],
            'metadata': {
                'source': 'Alternative data sources',
                'description': f'Alternative zoning data for {county}, {state}',
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.6
            }
        }
        
        return alternative_data
        
    except Exception as e:
        logger.error(f"Error fetching alternative zoning data: {e}")
        return None


def validate_zoning_data(data: Dict[str, Any]) -> bool:
    """
    Validate zoning data structure and content
    
    Args:
        data: Zoning data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    try:
        # Check basic structure
        if not isinstance(data, dict):
            return False
        
        # Check for required fields
        required_fields = ['type']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check if it's a valid GeoJSON-like structure
        if data.get('type') == 'FeatureCollection':
            if 'features' not in data:
                logger.warning("FeatureCollection missing 'features' field")
                return False
            
            if not isinstance(data['features'], list):
                logger.warning("'features' field is not a list")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating zoning data: {e}")
        return False


def generate_fallback_zoning_data(lat: float, lng: float) -> Dict[str, Any]:
    """
    Generate fallback zoning data based on geographic location
    
    Args:
        lat: Latitude
        lng: Longitude
        
    Returns:
        Fallback zoning data
    """
    # Determine probable zoning based on geographic patterns
    if lat < 42.0:  # California
        if lng < -122.0:  # Coastal
            zone_type = 'rural'
            farmland_class = 'Grazing Land'
            protection_level = 0.4
        else:  # Interior
            zone_type = 'agricultural'
            farmland_class = 'Prime Farmland'
            protection_level = 0.8
    else:  # Oregon
        if lng < -120.0:  # Western Oregon
            zone_type = 'exclusive_farm_use'
            farmland_class = 'High Value Farmland'
            protection_level = 0.7
        else:  # Eastern Oregon
            zone_type = 'rural'
            farmland_class = 'Grazing Land'
            protection_level = 0.5
    
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [lng, lat]
        },
        'properties': {
            'zone_type': zone_type,
            'farmland_class': farmland_class,
            'protection_level': protection_level,
            'data_source': 'fallback',
            'confidence': 0.5,
            'timestamp': datetime.now().isoformat()
        }
    }


def fetch_comprehensive_zoning_data(counties: List[str], states: List[str]) -> Dict[str, Any]:
    """
    Fetch comprehensive zoning data from multiple sources
    
    Args:
        counties: List of counties to fetch data for
        states: List of states to fetch data for
        
    Returns:
        Comprehensive zoning data
    """
    comprehensive_data = {
        'california_data': {},
        'oregon_data': {},
        'alternative_data': {},
        'metadata': {
            'fetch_timestamp': datetime.now().isoformat(),
            'sources_attempted': [],
            'sources_successful': [],
            'data_quality_score': 0.0
        }
    }
    
    # Define county lists
    california_counties = [
        'Butte', 'Colusa', 'Del Norte', 'Glenn', 'Humboldt', 
        'Lake', 'Lassen', 'Mendocino', 'Modoc', 'Nevada', 
        'Plumas', 'Shasta', 'Sierra', 'Siskiyou', 'Tehama', 'Trinity'
    ]
    oregon_counties = [
        'Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 
        'Crook', 'Curry', 'Deschutes', 'Douglas', 'Gilliam', 'Grant', 
        'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josephine', 
        'Klamath', 'Lake', 'Lane', 'Lincoln', 'Linn', 'Malheur', 
        'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 
        'Umatilla', 'Union', 'Wallowa', 'Wasco', 'Washington', 'Wheeler', 'Yamhill'
    ]
    
    # Fetch California data
    ca_counties = [c for c in counties if c in california_counties and 'CA' in states]
    successful_ca_fetches = 0
    for county in ca_counties:
        comprehensive_data['metadata']['sources_attempted'].append(f"FMMP_{county}")
        
        fmmp_data = fetch_fmmp_data(county)
        if fmmp_data:
            comprehensive_data['california_data'][county] = fmmp_data
            comprehensive_data['metadata']['sources_successful'].append(f"FMMP_{county}")
            successful_ca_fetches += 1
        else:
            # Try alternative sources
            alt_data = fetch_alternative_zoning_data(county, 'CA')
            if alt_data:
                comprehensive_data['alternative_data'][f"{county}_CA"] = alt_data
                comprehensive_data['metadata']['sources_successful'].append(f"Alternative_{county}_CA")
    
    # Fetch Oregon data
    or_counties = [c for c in counties if c in oregon_counties and 'OR' in states]
    for county in or_counties:
        comprehensive_data['metadata']['sources_attempted'].append(f"Oregon_Zoning_{county}")
        
        oregon_data = fetch_oregon_efu_data(county)
        if oregon_data:
            comprehensive_data['oregon_data'][county] = oregon_data
            comprehensive_data['metadata']['sources_successful'].append(f"Oregon_Zoning_{county}")
        else:
            # Try alternative sources
            alt_data = fetch_alternative_zoning_data(county, 'OR')
            if alt_data:
                comprehensive_data['alternative_data'][f"{county}_OR"] = alt_data
                comprehensive_data['metadata']['sources_successful'].append(f"Alternative_{county}_OR")
    
    # Calculate data quality score
    attempted_sources = len(comprehensive_data['metadata']['sources_attempted'])
    successful_sources = len(comprehensive_data['metadata']['sources_successful'])
    
    if attempted_sources > 0:
        comprehensive_data['metadata']['data_quality_score'] = successful_sources / attempted_sources
    
    logger.info(f"Comprehensive zoning data fetch completed: {successful_sources}/{attempted_sources} sources successful")
    
    return comprehensive_data 