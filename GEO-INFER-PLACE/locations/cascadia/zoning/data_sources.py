"""
Cascadian Zoning Data Sources

This module is responsible for fetching and consolidating zoning data from
various state and local sources for the Cascadian bioregion.
"""
import logging
import os
import requests
import zipfile
from io import BytesIO
import geopandas as gpd
import pandas as pd
from shapely.geometry import box, Polygon
from typing import List, Tuple, Dict, Optional
import json
from datetime import datetime
import glob

logger = logging.getLogger(__name__)

class CascadianZoningDataSources:
    """
    Handles fetching and loading of real zoning data from multiple sources,
    including CA FMMP, Oregon's DLCD, and Washington county GIS services.
    """

    def __init__(self):
        self.fmmp_data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'fmmp')
        os.makedirs(self.fmmp_data_path, exist_ok=True)
        
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'data_urls.json')
        try:
            with open(config_path) as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse config file at {config_path}: {e}")
            self.config = {}

        self.target_ca_counties = [
            'Butte', 'Colusa', 'Del Norte', 'Glenn', 'Humboldt', 'Lake', 'Lassen', 
            'Mendocino', 'Modoc', 'Nevada', 'Plumas', 'Shasta', 'Sierra', 
            'Siskiyou', 'Tehama', 'Trinity'
        ]

        self.fmmp_base_url = self.config.get('zoning', {}).get('ca_fmmp', {}).get('base_url')
        self.or_zoning_service_url = self.config.get('zoning', {}).get('or_dlcd_service_url')
        self.wa_zoning_service_url = self.config.get('zoning', {}).get('wa_king_county_service_url')

    def _query_arcgis_service(self, url: str, bbox: Tuple[float, float, float, float], source_name: str) -> gpd.GeoDataFrame:
        """Generic function to query an ArcGIS Feature/MapServer for a given bounding box."""
        # Correctly format the bounding box as a comma-separated string: xmin,ymin,xmax,ymax
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
        logger.info(f"Querying {source_name} ArcGIS service at {url} with bbox: {bbox_str}")
        try:
            response = requests.get(url + "/query", params=params, timeout=180)
            response.raise_for_status()
            data = response.json()
            if data.get('features'):
                gdf = gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
                logger.info(f"Successfully fetched {len(gdf)} features from {source_name}.")
                gdf['source'] = source_name
                return gdf
            else:
                logger.info(f"No features found for the given extent in {source_name}.")
                return gpd.GeoDataFrame()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query {source_name} ArcGIS service: {e}", exc_info=True)
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse GeoJSON from {source_name}: {e}", exc_info=True)
        return gpd.GeoDataFrame()

    def fetch_ca_fmmp_data(self) -> gpd.GeoDataFrame:
        """
        Loads all available California FMMP county shapefiles from the local data directory
        and concatenates them. Assumes data has been manually downloaded as per README.
        """
        all_gdfs = []
        logger.info(f"Loading local CA FMMP shapefiles from {self.fmmp_data_path}...")

        # Search for shapefiles in subdirectories, e.g., .../data/fmmp/Butte/Butte.shp
        shapefiles = glob.glob(os.path.join(self.fmmp_data_path, '**', '*.shp'), recursive=True)

        if not shapefiles:
            logger.warning(f"No FMMP shapefiles found in {self.fmmp_data_path} or its subdirectories. Please ensure data is downloaded manually as per the README.")
            return gpd.GeoDataFrame()

        for shp_file in shapefiles:
            try:
                # Extract county name from the path, assuming path is like '.../fmmp/Butte/Butte.shp'
                county = os.path.basename(os.path.dirname(shp_file))
                
                gdf = gpd.read_file(shp_file)
                gdf['county'] = county
                gdf['source'] = 'CA_FMMP'
                all_gdfs.append(gdf)
                logger.info(f"Loaded {county} FMMP data from {shp_file}.")
            except Exception as e:
                logger.error(f"Failed to read shapefile {shp_file}: {e}")
        
        if not all_gdfs:
            logger.warning("No California FMMP data could be loaded successfully.")
            return gpd.GeoDataFrame()

        return pd.concat(all_gdfs, ignore_index=True)

    def fetch_all_zoning_data(self, target_hexagons: List[str]) -> gpd.GeoDataFrame:
        """
        Fetches all available real zoning data for the bioregion.
        """
        from utils_h3 import h3_to_geo_boundary

        if not target_hexagons:
            logger.error("Cannot fetch zoning data without target hexagons for bounding box.")
            return gpd.GeoDataFrame()

        hex_boundaries = [Polygon([(lon, lat) for lat, lon in h3_to_geo_boundary(h)]) for h in target_hexagons]
        min_lon = min(p.bounds[0] for p in hex_boundaries)
        min_lat = min(p.bounds[1] for p in hex_boundaries)
        max_lon = max(p.bounds[2] for p in hex_boundaries)
        max_lat = max(p.bounds[3] for p in hex_boundaries)
        bbox = (min_lon, min_lat, max_lon, max_lat)

        ca_gdf = self.fetch_ca_fmmp_data()
        or_gdf = self._query_arcgis_service(self.or_zoning_service_url, bbox, "OR_DLCD")
        wa_gdf = self._query_arcgis_service(self.wa_zoning_service_url, bbox, "WA_King_County")

        all_gdfs = []
        for gdf in [ca_gdf, or_gdf, wa_gdf]:
            if not gdf.empty:
                # Ensure CRS is consistent before adding
                all_gdfs.append(gdf.to_crs("EPSG:4326"))

        if not all_gdfs:
            logger.warning("No zoning data could be loaded for any jurisdiction.")
            return gpd.GeoDataFrame()
        
        # Clip the large California dataset to the bbox for performance
        final_gdfs = []
        for gdf in all_gdfs:
            if gdf['source'].iloc[0] == 'CA_FMMP':
                 # Use a small buffer to avoid clipping edges
                clipped_gdf = gpd.clip(gdf, box(bbox[0]-0.1, bbox[1]-0.1, bbox[2]+0.1, bbox[3]+0.1))
                if not clipped_gdf.empty:
                    final_gdfs.append(clipped_gdf)
            else:
                final_gdfs.append(gdf)

        if not final_gdfs:
            logger.warning("All zoning data was outside the target bounding box.")
            return gpd.GeoDataFrame()
            
        return pd.concat(final_gdfs, ignore_index=True) 