"""
Cascadian Surface Water Data Sources

This module is responsible for fetching surface water data (flowlines and
water bodies) from the USGS National Hydrography Dataset (NHD).
"""
import logging
import os
import geopandas as gpd
import requests
from shapely.geometry import box
from typing import Tuple
import json

logger = logging.getLogger(__name__)

class CascadianSurfaceWaterDataSources:
    """
    Handles fetching of surface water data from the USGS NHD ArcGIS service.
    """
    
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'data_urls.json')
        try:
            with open(config_path) as f:
                self.config = json.load(f).get('surface_water', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse surface_water config: {e}")
            self.config = {}

        self.flowlines_url = self.config.get('nhd_flowlines_url')
        self.waterbodies_url = self.config.get('nhd_waterbodies_url')

    def _query_nhd_layer(self, service_url: str, layer_name: str, bbox: Tuple[float, float, float, float]) -> gpd.GeoDataFrame:
        """
        Queries a specific layer from the NHD ArcGIS REST service for a given bounding box.

        Args:
            service_url: The full URL to the map service layer.
            layer_name: A descriptive name for logging (e.g., "flowlines").
            bbox: A tuple representing the bounding box (xmin, ymin, xmax, ymax)
                  in WGS84 (EPSG:4326).

        Returns:
            A GeoDataFrame containing the queried features, or an empty one on failure.
        """
        if not service_url:
            logger.error(f"No URL configured for NHD layer '{layer_name}'.")
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

        query_url = f"{service_url}/query"
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        
        params = {
            'where': '1=1',
            'geometry': bbox_str,
            'geometryType': 'esriGeometryEnvelope',
            'inSR': '4326',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*',
            'returnGeometry': 'true',
            'outSR': '4326',
            'f': 'geojson'
        }
        
        logger.info(f"Querying NHD {layer_name} with bbox: {bbox_str}")
        
        try:
            response = requests.get(query_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('features'):
                logger.info(f"No features found in {layer_name} for the given bounding box.")
                return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")
                
            gdf = gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
            logger.info(f"Successfully fetched {len(gdf)} features from {layer_name}.")
            return gdf

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query NHD layer {layer_name}: {e}", exc_info=True)
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse GeoJSON response from NHD {layer_name}: {e}", exc_info=True)
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

    def fetch_surface_water_features(self, bbox: Tuple[float, float, float, float]) -> dict:
        """
        Fetches all relevant surface water features (flowlines and waterbodies)
        from the NHD for a given bounding box.

        Args:
            bbox: The bounding box for the query.

        Returns:
            A dictionary containing two GeoDataFrames: 'flowlines' and 'waterbodies'.
        """
        logger.info("Fetching all surface water features from NHD...")
        flowlines_gdf = self._query_nhd_layer(self.flowlines_url, "flowlines", bbox)
        waterbodies_gdf = self._query_nhd_layer(self.waterbodies_url, "waterbodies", bbox)

        return {
            'flowlines': flowlines_gdf,
            'waterbodies': waterbodies_gdf
        } 