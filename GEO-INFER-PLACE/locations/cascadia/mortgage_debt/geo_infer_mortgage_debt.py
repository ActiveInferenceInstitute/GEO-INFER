"""
GeoInfer Mortgage & Debt Module

This module analyzes agricultural mortgage and debt data within an H3 grid by
leveraging public Home Mortgage Disclosure Act (HMDA) data.
"""
import logging
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import requests
import zipfile
import io
import os

from .data_sources import CascadianMortgageDataSources
from geo_infer_space.utils.h3_utils import h3_to_geojson, geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

logger = logging.getLogger(__name__)

class GeoInferMortgageDebt:
    """Processes and analyzes mortgage data aggregated at the census tract level."""

    def __init__(self, resolution: int):
        self.resolution = resolution
        self.mortgage_data_source = CascadianMortgageDataSources()
        self.census_data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'census')
        os.makedirs(self.census_data_dir, exist_ok=True)
        logger.info(f"Initialized GeoInferMortgageDebt with resolution {resolution}")

    def _fetch_census_tract_geometries(self, year: int, state_fips: str) -> gpd.GeoDataFrame:
        """
        Downloads and caches US Census TIGER/Line shapefiles for a given state.
        """
        zip_path = os.path.join(self.census_data_dir, f'tl_{year}_{state_fips}_tract.zip')
        shapefile_dir = os.path.join(self.census_data_dir, f'tl_{year}_{state_fips}_tract')
        
        if not os.path.exists(shapefile_dir):
            if not os.path.exists(zip_path):
                url = f'https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_fips}_tract.zip'
                logger.info(f"Downloading census tract geometries for state FIPS {state_fips} from {url}")
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to download census tract data for FIPS {state_fips}: {e}")
                    return gpd.GeoDataFrame()
            
            logger.info(f"Unzipping {zip_path}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(shapefile_dir)
        
        try:
            gdf = gpd.read_file(shapefile_dir)
            # GEOID is the full census tract FIPS code
            gdf.rename(columns={'GEOID': 'census_tract'}, inplace=True)
            return gdf[['census_tract', 'geometry']]
        except Exception as e:
            logger.error(f"Failed to read shapefile from {shapefile_dir}: {e}")
            return gpd.GeoDataFrame()

    def run_analysis(self, target_hexagons: List[str], year: int = 2022) -> Dict[str, Dict[str, Any]]:
        """
        Spatially joins HMDA mortgage data with H3 hexagons and calculates debt metrics.
        """
        logger.info(f"Starting mortgage & debt analysis for {len(target_hexagons)} hexagons.")
        
        # 1. Fetch aggregated mortgage data from HMDA source
        mortgage_df = self.mortgage_data_source.fetch_all_mortgage_data(year)
        if mortgage_df.empty:
            logger.warning("No mortgage data found. Aborting analysis.")
            return {}

        # 2. Fetch census tract geometries for CA (06) and OR (41)
        ca_tracts = self._fetch_census_tract_geometries(year, '06')
        or_tracts = self._fetch_census_tract_geometries(year, '41')
        census_tract_gdf = pd.concat([ca_tracts, or_tracts], ignore_index=True)
        if census_tract_gdf.empty:
            logger.error("Could not load any census tract geometries. Aborting.")
            return {}

        # 3. Merge tabular and spatial data to create a mortgage GeoDataFrame
        mortgage_gdf = census_tract_gdf.merge(mortgage_df, on='census_tract', how='inner')
        if mortgage_gdf.empty:
            logger.warning("No matching census tracts found for the loaded mortgage data.")
            return {}
            
        # 4. Create a GeoDataFrame for the target hexagons
        hex_geometries = [Polygon(h3_to_geo_boundary(h)) for h in target_hexagons]
        hex_gdf = gpd.GeoDataFrame(
            {'hex_id': target_hexagons}, 
            geometry=hex_geometries, 
            crs=census_tract_gdf.crs # Use the same CRS as census data
        )
        
        # 5. Ensure CRS alignment before join
        mortgage_gdf = mortgage_gdf.to_crs(hex_gdf.crs)

        # 6. Perform the spatial join
        logger.info("Performing spatial join between hexagons and mortgage census tracts...")
        # Use 'intersects' as a hexagon can overlap with multiple tracts
        joined_gdf = gpd.sjoin(hex_gdf, mortgage_gdf, how="inner", predicate="intersects")
        
        if joined_gdf.empty:
            logger.warning("Spatial join resulted in no matches between hexagons and mortgage data.")
            return {}

        # 7. Aggregate results and calculate metrics per hexagon
        logger.info("Aggregating mortgage results per hexagon...")
        h3_mortgage = {}
        for hex_id, group in joined_gdf.groupby('hex_id'):
            # Weighted average of metrics based on intersection area is too complex here.
            # We will do a simpler aggregation: average of the tract values.
            h3_mortgage[hex_id] = {
                'total_loan_volume': group['total_loan_volume'].sum(),
                'avg_loan_to_value_ratio': group['loan_to_value_ratio'].mean(),
                'avg_income': group['average_income'].mean(),
                'number_of_loans': group['number_of_loans'].sum(),
                'number_of_source_tracts': group['census_tract'].nunique()
            }

        logger.info(f"Completed mortgage analysis. Processed {len(h3_mortgage)} hexagons.")
        return h3_mortgage 