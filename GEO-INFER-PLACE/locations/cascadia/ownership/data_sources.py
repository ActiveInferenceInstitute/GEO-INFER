"""
Cascadian Ownership Data Sources

This module is responsible for fetching parcel-level ownership data by
querying public ArcGIS REST services.
"""
import logging
import os
import requests
import geopandas as gpd
from shapely.geometry import box, Polygon
from typing import List, Dict
import json

from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary, polygon_to_cells

logger = logging.getLogger(__name__)

class CascadianOwnershipDataSources:
    """
    Handles fetching of ownership parcel data from public ArcGIS services.
    """
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'parcels')
        os.makedirs(self.data_dir, exist_ok=True)
        
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'data_urls.json')
        try:
            with open(config_path) as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse config file at {config_path}: {e}")
            self.config = {}

        self.arcgis_service_urls = {
            'CA': self.config.get('ownership', {}).get('ca_parcels_service_url')
        }
        self.arcgis_service_urls = {k: v for k, v in self.arcgis_service_urls.items() if v}

    def _fetch_arcgis_parcels(self, service_url: str, bbox: tuple) -> gpd.GeoDataFrame:
        """
        Fetches parcel data from an ArcGIS Feature/MapServer for a given bounding box.
        """
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        params = {
            'geometry': bbox_str,
            'geometryType': 'esriGeometryEnvelope',
            'inSR': '4326',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*',  # Get all available fields
            'outSR': '4326',
            'f': 'geojson'
        }
        
        query_url = f"{service_url}/query"
        logger.info(f"Querying ArcGIS service: {query_url} with bbox: {bbox_str}")

        try:
            response = requests.get(query_url, params=params, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('features'):
                logger.info("No features returned from the ArcGIS service for the given extent.")
                return gpd.GeoDataFrame()

            # The geojson response from ArcGIS is directly readable by GeoPandas
            gdf = gpd.GeoDataFrame.from_features(data['features'])
            gdf.set_crs("EPSG:4326", inplace=True)
            
            logger.info(f"Successfully fetched {len(gdf)} parcels from {service_url}")
            return gdf
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying ArcGIS service at {service_url}: {e}")
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing GeoJSON response from {service_url}: {e}")
        
        return gpd.GeoDataFrame()

    def fetch_all_parcel_data(self, target_hexagons: List[str]) -> gpd.GeoDataFrame:
        """
        Fetches all available parcel data from configured ArcGIS services
        that intersect with the target hexagons.
        """
        if not target_hexagons:
            logger.warning("Cannot fetch parcel data without target hexagons.")
            return gpd.GeoDataFrame()

        # 1. Calculate the total bounding box for the H3 hexagons
        hex_polygons = [Polygon(cell_to_latlng_boundary(h)) for h in target_hexagons]
        min_lon = min(p.bounds[0] for p in hex_polygons)
        min_lat = min(p.bounds[1] for p in hex_polygons)
        max_lon = max(p.bounds[2] for p in hex_polygons)
        max_lat = max(p.bounds[3] for p in hex_polygons)
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        all_gdfs = []
        
        # 2. Query each configured ArcGIS service
        for state, url in self.arcgis_service_urls.items():
            logger.info(f"Fetching parcel data for {state}...")
            state_gdf = self._fetch_arcgis_parcels(url, bbox)
            if not state_gdf.empty:
                state_gdf['source_state'] = state
                all_gdfs.append(state_gdf)

        if not all_gdfs:
            logger.warning("No parcel data was loaded from any ArcGIS service.")
            return gpd.GeoDataFrame()
            
        logger.info(f"Successfully loaded data from {len(all_gdfs)} sources.")
        
        # 3. Combine and standardize the data
        combined_gdf = gpd.pd.concat(all_gdfs, ignore_index=True)
        
        # Basic standardization - column names can vary wildly between sources
        # A more robust solution would have a mapping for each source.
        # For now, we look for common parcel ID columns.
        id_cols = ['PARNO', 'APN', 'parcel_id', 'OBJECTID']
        parcel_id_col = next((col for col in id_cols if col in combined_gdf.columns), 'generated_id')
        
        if parcel_id_col == 'generated_id':
            combined_gdf['parcel_id'] = [f'gen_{i}' for i in range(len(combined_gdf))]
        else:
            combined_gdf.rename(columns={parcel_id_col: 'parcel_id'}, inplace=True)
            
        return combined_gdf 