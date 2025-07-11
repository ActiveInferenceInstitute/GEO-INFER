"""
Cascadian Power Source Data Sources

This module is responsible for fetching and loading power infrastructure
data (e.g., transmission lines) from the HIFLD open data portal.
"""
import logging
import os
import geopandas as gpd
import requests
import zipfile
import io
import json
from typing import List, Tuple
from shapely.geometry import Polygon

from utils_h3 import h3_to_geo_boundary


logger = logging.getLogger(__name__)

class CascadianPowerSourceDataSources:
    """Handles fetching and loading of power infrastructure data."""
    
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'data_urls.json')
        try:
            with open(config_path) as f:
                self.config = json.load(f).get('power_source', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse power_source config: {e}")
            self.config = {}

        self.hifld_transmission_url = self.config.get('hifld_transmission_url')
        self.hifld_power_plants_url = self.config.get('hifld_power_plants_url')

    def _calculate_bbox_from_hexagons(self, hexagons: List[str]) -> Tuple[float, float, float, float]:
        """Calculates a bounding box from a list of H3 hexagons."""
        boundaries = [Polygon(h3_to_geo_boundary(h)) for h in hexagons]
        min_lon = min(b.bounds[0] for b in boundaries)
        min_lat = min(b.bounds[1] for b in boundaries)
        max_lon = max(b.bounds[2] for b in boundaries)
        max_lat = max(b.bounds[3] for b in boundaries)
        return (min_lon, min_lat, max_lon, max_lat)

    def _query_hifld_service(self, service_url: str, layer_name: str, hexagons: List[str]) -> gpd.GeoDataFrame:
        """Generic function to query a HIFLD service layer for a given list of hexagons."""
        if not service_url:
            logger.error(f"HIFLD service URL for '{layer_name}' not configured.")
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

        if not hexagons:
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

        bbox = self._calculate_bbox_from_hexagons(hexagons)
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        
        params = {
            'where': '1=1',
            'outFields': '*',
            'geometry': bbox_str,
            'geometryType': 'esriGeometryEnvelope',
            'inSR': '4326',
            'outSR': '4326',
            'f': 'geojson'
        }
        
        logger.info(f"Querying HIFLD {layer_name} service with bbox: {bbox_str}")
        try:
            # The query endpoint is typically at '/query' relative to the layer URL
            query_url = f"{service_url}/query"
            response = requests.get(query_url, params=params, timeout=180)
            response.raise_for_status()
            
            # Check for empty response
            if not response.text or not response.text.strip():
                logger.info(f"Empty response from HIFLD {layer_name} service.")
                return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

            gdf = gpd.read_file(io.StringIO(response.text))
            logger.info(f"Successfully loaded {len(gdf)} {layer_name} records.")
            return gdf
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {layer_name} data from HIFLD service: {e}")
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")
        except Exception as e:
            logger.error(f"Failed to read GeoJSON response from HIFLD {layer_name} service: {e}")
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

    def fetch_power_infrastructure_features(self, hexagons: List[str]) -> dict:
        """
        Fetches all power infrastructure (transmission lines, power plants)
        for the area covered by the given hexagons.
        """
        logger.info("Fetching all power infrastructure features from HIFLD...")
        
        transmission_lines = self._query_hifld_service(
            self.hifld_transmission_url, 
            "transmission lines", 
            hexagons
        )
        
        power_plants = self._query_hifld_service(
            self.hifld_power_plants_url,
            "power plants",
            hexagons
        )

        return {
            'transmission_lines': transmission_lines,
            'power_plants': power_plants
        } 