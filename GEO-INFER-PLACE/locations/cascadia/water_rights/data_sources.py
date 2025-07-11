"""
Cascadian Water Rights Data Sources

This module is responsible for fetching water rights data from the official
state data portals for California, Oregon, and Washington.
"""
import os
import logging
import pandas as pd
import geopandas as gpd
import numpy as np
import requests
from shapely.geometry import Point, box
from typing import Dict, Tuple
import json
from datetime import datetime

from geo_infer_space.utils.h3_utils import h3_to_geo_boundary
from shapely.geometry import Polygon

logger = logging.getLogger(__name__)

class CascadianWaterRightsDataSources:
    """
    Manages the acquisition of water rights data for the Cascadia region.
    
    This class handles downloading real data from state-level ArcGIS REST
    services and public data portals.
    """
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'water_rights')
        os.makedirs(self.data_dir, exist_ok=True)
        
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'data_urls.json')
        try:
            with open(config_path) as f:
                self.config = json.load(f).get('water_rights', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse water_rights config: {e}")
            self.config = {}

        self.ca_url = self.config.get('ca_ewrims_csv_url')
        self.or_url = self.config.get('or_wr_service_url') # This may be None
        self.or_url_comment = self.config.get('or_wr_service_url_comment')

        self.ca_csv_path = os.path.join(self.data_dir, 'ca_water_rights_summary.csv')
        logger.info("Initialized CascadianWaterRightsDataSources.")

    def _download_ca_file(self) -> None:
        """Downloads the CA eWRIMS data file if it's not already cached."""
        if os.path.exists(self.ca_csv_path):
            logger.info(f"Using cached CA water rights file: {self.ca_csv_path}")
            return

        if not self.ca_url:
            logger.error("California water rights URL not configured.")
            return

        logger.info(f"Attempting to download CA water rights file from {self.ca_url}...")
        try:
            response = requests.get(self.ca_url, timeout=300) # Increased timeout for large file
            response.raise_for_status()

            with open(self.ca_csv_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded CA water rights file to {self.ca_csv_path}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download CA water rights from primary URL: {e}")

    def _fetch_ca_data(self) -> gpd.GeoDataFrame:
        """ Fetches and processes California water rights data. """
        try:
            self._download_ca_file()
            if not os.path.exists(self.ca_csv_path):
                logger.error("CA water rights CSV not found after download attempt.")
                return gpd.GeoDataFrame()

            df = pd.read_csv(self.ca_csv_path, low_memory=False)
            df = df.rename(columns=lambda x: x.strip().lower().replace(' ', '_'))
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df = df.dropna(subset=['latitude', 'longitude'])
            
            geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
            gdf['state'] = 'CA'
            logger.info(f"Successfully loaded and processed {len(gdf)} water rights records for CA.")
            return gdf
        except Exception as e:
            logger.error(f"Failed to process CA water rights data: {e}", exc_info=True)
            return gpd.GeoDataFrame()
    
    def _fetch_or_data(self, bbox: Tuple[float, float, float, float]) -> gpd.GeoDataFrame:
        """ Fetches Oregon water rights data (Points of Diversion) from the OWRD ArcGIS service. """
        if not self.or_url:
            log_message = "Oregon water rights URL not configured, skipping fetch."
            if self.or_url_comment:
                log_message += f" Reason: {self.or_url_comment}"
            logger.warning(log_message)
            return gpd.GeoDataFrame()

        # Layer IDs for Points of Diversion (can be found by inspecting the service)
        # 0: PODs Surface Water, 1: PODs Groundwater
        gdfs = []
        for layer_id in [0, 1]:
            query_url = f"{self.or_url}/{layer_id}/query"
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
            logger.info(f"Querying OR Water Rights Layer ID {layer_id} with bbox: {bbox_str}")
            try:
                response = requests.get(query_url, params=params, timeout=60)
                response.raise_for_status()
                data = response.json()
                if data.get('features'):
                    gdf = gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
                    gdfs.append(gdf)
                    logger.info(f"Successfully fetched {len(gdf)} features from OR Layer ID {layer_id}.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to query OR Layer ID {layer_id}: {e}", exc_info=True)
            except (KeyError, ValueError) as e:
                logger.error(f"Failed to parse GeoJSON from OR Layer ID {layer_id}: {e}", exc_info=True)
        
        if not gdfs:
            logger.warning("No water rights data found for Oregon.")
            return gpd.GeoDataFrame()
        
        or_gdf = pd.concat(gdfs, ignore_index=True)
        or_gdf['state'] = 'OR'
        logger.info(f"Successfully loaded {len(or_gdf)} total water rights records for OR.")
        return or_gdf

    def _fetch_wa_data(self, bbox: Tuple[float, float, float, float]) -> gpd.GeoDataFrame:
        """ Placeholder for fetching Washington water rights data. """
        logger.warning(
            "Washington water rights data source has not been implemented. "
            "A public-facing ArcGIS REST service needs to be identified. "
            "Skipping WA data."
        )
        return gpd.GeoDataFrame()

    def fetch_all_water_rights_data(self, target_hexagons: list) -> gpd.GeoDataFrame:
        """
        Fetches water rights data for all three states (CA, OR, WA).
        """
        
        if not target_hexagons:
            logger.error("Cannot fetch water rights without target hexagons for bounding box.")
            return gpd.GeoDataFrame()

        # Correct the bounding box creation for the polygon clipping
        hex_boundaries = [Polygon([(lon, lat) for lat, lon in h3_to_geo_boundary(h)]) for h in target_hexagons]
        min_lon = min(p.bounds[0] for p in hex_boundaries)
        min_lat = min(p.bounds[1] for p in hex_boundaries)
        max_lon = max(p.bounds[2] for p in hex_boundaries)
        max_lat = max(p.bounds[3] for p in hex_boundaries)
        bbox = (min_lon, min_lat, max_lon, max_lat)

        ca_gdf = self._fetch_ca_data()
        or_gdf = self._fetch_or_data(bbox)
        wa_gdf = self._fetch_wa_data(bbox)

        # Filter CA data to the bounding box of the analysis
        if not ca_gdf.empty:
            ca_gdf = ca_gdf.cx[bbox[0]:bbox[2], bbox[1]:bbox[3]]

        all_gdfs = [gdf for gdf in [ca_gdf, or_gdf, wa_gdf] if not gdf.empty]

        if not all_gdfs:
            logger.warning("No water rights data could be loaded for any state in the target area.")
            return gpd.GeoDataFrame()

        return pd.concat(all_gdfs, ignore_index=True) 