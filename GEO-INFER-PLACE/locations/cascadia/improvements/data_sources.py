"""
Cascadian Improvements Data Sources

This module is responsible for fetching and consolidating agricultural
improvements data, including building footprints and estimated values.
"""
import logging
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import requests
import zipfile
import io
from shapely.geometry import box

from geo_infer_space.utils.h3_utils import h3_to_geojson, geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill
from shapely.geometry import Polygon
import random

logger = logging.getLogger(__name__)

class CascadianImprovementsDataSources:
    """
    Manages acquisition and processing of building footprints and estimated property values.
    
    This class downloads building footprint data from the Microsoft USBuildingFootprints
    dataset and property value data from Zillow's ZHVI. It then estimates
    improvement and land values based on the combination of these sources.
    """
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'improvements')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.state_urls = {
            'CA': 'https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/California.geojson.zip',
            'OR': 'https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Oregon.geojson.zip'
        }
        self.zillow_zhvi_url = 'https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv'
        
        logger.info("Initialized CascadianImprovementsDataSources.")

    def _fetch_zillow_zhvi_data(self) -> gpd.GeoDataFrame:
        """Downloads Zillow Home Value Index data and pre-processes it."""
        zhvi_path = os.path.join(self.data_dir, 'Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')
        
        if not os.path.exists(zhvi_path):
            logger.info("Downloading Zillow ZHVI data...")
            try:
                response = requests.get(self.zillow_zhvi_url)
                response.raise_for_status()
                with open(zhvi_path, 'wb') as f:
                    f.write(response.content)
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download Zillow data: {e}")
                return gpd.GeoDataFrame()

        logger.info("Processing Zillow ZHVI data...")
        df = pd.read_csv(zhvi_path)
        # Get the most recent month's value
        latest_month = df.columns[-1]
        df = df[['RegionName', 'State', latest_month]].copy()
        df.rename(columns={'RegionName': 'zip_code', latest_month: 'median_home_value'}, inplace=True)
        df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)

        # To make this spatial, we need zip code boundaries.
        zip_boundaries_dir = os.path.join(self.data_dir, 'tl_2023_us_zcta520')
        zip_boundaries_shapefile = os.path.join(zip_boundaries_dir, 'tl_2023_us_zcta520.shp')
        
        if not os.path.exists(zip_boundaries_shapefile):
            logger.info("Downloading and unzipping US Zip Code boundaries...")
            url = 'https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/tl_2023_us_zcta520.zip'
            zip_path = os.path.join(self.data_dir, 'tl_2023_us_zcta520.zip')
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    os.makedirs(zip_boundaries_dir, exist_ok=True)
                    zip_ref.extractall(zip_boundaries_dir)
                os.remove(zip_path) # Clean up the zip file

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download zip code boundaries: {e}")
                return gpd.GeoDataFrame()
            except zipfile.BadZipFile:
                logger.error("Downloaded zip code boundaries file is not a valid zip.")
                return gpd.GeoDataFrame()

        logger.info(f"Reading zip code boundaries from {zip_boundaries_shapefile}")
        gdf_zips = gpd.read_file(zip_boundaries_shapefile)
        gdf_zips = gdf_zips[['ZCTA5CE20', 'geometry']].rename(columns={'ZCTA5CE20': 'zip_code'})
        gdf_zips['zip_code'] = gdf_zips['zip_code'].astype(str)
        
        # Merge Zillow data with zip boundaries
        zhvi_gdf = gdf_zips.merge(df, on='zip_code', how='inner')
        return zhvi_gdf

    def _download_and_unzip(self, state: str, url: str):
        zip_path = os.path.join(self.data_dir, f'{state}_buildings.zip')
        geojson_path = os.path.join(self.data_dir, f'{state}.geojson')

        if os.path.exists(geojson_path):
            logger.info(f"GeoJSON file already exists for {state}, skipping download.")
            return geojson_path

        if not os.path.exists(zip_path):
            logger.info(f"Downloading {state} building footprints from {url}...")
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"Download complete for {state}.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading file for {state}: {e}")
                return None
        
        logger.info(f"Unzipping {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            geojson_filename = [name for name in zip_ref.namelist() if name.endswith('.geojson')][0]
            zip_ref.extract(geojson_filename, path=self.data_dir)
            os.rename(os.path.join(self.data_dir, geojson_filename), geojson_path)
        logger.info(f"Unzipped and renamed to {geojson_path}.")
        return geojson_path

    def _estimate_improvement_values(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Estimates 'improvement_value' and 'land_value' based on geometry and Zillow data.
        Assumes 'median_home_value' is already joined to the GeoDataFrame.
        """
        if gdf.empty or 'median_home_value' not in gdf.columns:
            logger.warning("Cannot estimate values without median_home_value.")
            return gdf.assign(improvement_value=0, land_value=0)
        
        gdf['median_home_value'].fillna(gdf['median_home_value'].median(), inplace=True)
        
        gdf_proj = gdf.to_crs(epsg=3310)
        gdf['area_sqm'] = gdf_proj.geometry.area
        
        # Heuristic: Assume median home value is for a 150 sqm (1600 sqft) home.
        # This gives us a local $/sqm estimate.
        estimated_cost_per_sqm = gdf['median_home_value'] / 150
        
        # Improvement value is area * local $/sqm
        gdf['improvement_value'] = (gdf['area_sqm'] * estimated_cost_per_sqm).round(0)
        
        # Land value is a fraction of the improvement value.
        land_value_multiplier = np.random.normal(loc=0.5, scale=0.15, size=len(gdf))
        gdf['land_value'] = (gdf['improvement_value'] * land_value_multiplier).clip(lower=0).round(0)
        
        gdf['parcel_id'] = [f"est_parcel_{i}" for i in range(len(gdf))]
        
        return gdf.drop(columns=['area_sqm'])

    def fetch_all_improvements_data(self, target_hexagons: list) -> gpd.GeoDataFrame:
        """
        Fetches building footprints and Zillow data, merges them, and returns
        a consolidated GeoDataFrame with estimated financial data.
        """
        if not target_hexagons:
            logger.warning("Cannot fetch improvements data without target hexagons.")
            return gpd.GeoDataFrame()

        
        hex_boundaries = [Polygon(h3_to_geo_boundary(h)) for h in target_hexagons]
        minx = min(p.bounds[0] for p in hex_boundaries)
        miny = min(p.bounds[1] for p in hex_boundaries)
        maxx = max(p.bounds[2] for p in hex_boundaries)
        maxy = max(p.bounds[3] for p in hex_boundaries)
        bbox = (minx, miny, maxx, maxy)

        # Fetch Zillow data first
        zhvi_gdf = self._fetch_zillow_zhvi_data()
        if zhvi_gdf.empty:
            logger.error("Could not fetch Zillow data, cannot estimate real values.")
            return self._create_mock_improvements_data(target_hexagons)

        all_gdfs = []
        for state, url in self.state_urls.items():
            geojson_path = self._download_and_unzip(state, url)
            if geojson_path:
                try:
                    logger.info(f"Loading building footprints for {state} within bounding box: {bbox}...")
                    gdf = gpd.read_file(geojson_path, bbox=bbox)
                    
                    if not gdf.empty:
                        logger.info(f"Spatially joining {state} buildings with Zillow data...")
                        # Ensure CRS match for spatial join
                        gdf = gdf.to_crs(zhvi_gdf.crs)
                        # Spatial join to get median home value for each building
                        gdf_merged = gpd.sjoin(gdf, zhvi_gdf, how="left", op="within")
                        
                        logger.info("Estimating improvement and land values...")
                        gdf_valued = self._estimate_improvement_values(gdf_merged)
                        all_gdfs.append(gdf_valued)
                    else:
                        logger.info(f"No buildings found for {state} in the target area.")
                except Exception as e:
                    logger.error(f"Failed to load or process GeoJSON for {state}: {e}")
        
        if not all_gdfs:
            logger.warning("No improvements data was loaded from real sources. Falling back to mock data.")
            return self._create_mock_improvements_data(target_hexagons)
            
        logger.info(f"Successfully loaded and processed building data for {len(all_gdfs)} states.")
        return pd.concat(all_gdfs, ignore_index=True)

    def _create_mock_improvements_data(self, target_hexagons: list) -> gpd.GeoDataFrame:
        """Generates a fully mock GeoDataFrame as a last resort."""
        logger.warning("Generating fully mock improvements data as a fallback.")
        
        
        hex_boundaries = [Polygon(h3_to_geo_boundary(h)) for h in target_hexagons]
        minx = min(p.bounds[0] for p in hex_boundaries)
        miny = min(p.bounds[1] for p in hex_boundaries)
        maxx = max(p.bounds[2] for p in hex_boundaries)
        maxy = max(p.bounds[3] for p in hex_boundaries)
        bounds = [minx, miny, maxx, maxy]

        polygons = []
        for _ in range(500): 
            min_x, min_y, max_x, max_y = bounds
            x_start = random.uniform(min_x, max_x)
            y_start = random.uniform(min_y, max_y)
            x_end = x_start + random.uniform(0.0001, 0.0005)
            y_end = y_start + random.uniform(0.0001, 0.0005)
            polygons.append(box(x_start, y_start, x_end, y_end))

        gdf = gpd.GeoDataFrame({'geometry': polygons})
        gdf.crs = "EPSG:4326"

        gdf['improvement_value'] = np.random.randint(50000, 500000, size=len(gdf))
        gdf['land_value'] = np.random.randint(20000, 200000, size=len(gdf))
        gdf['parcel_id'] = [f"fully_mock_{i}" for i in range(len(gdf))]
        return gdf 