"""
Cascadian Current Use Data Sources

Multi-source agricultural land use classification integrating NASS CDL,
Land IQ crop mapping, and Oregon EFU reporting systems.
"""

import requests
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import logging
from datetime import datetime
from urllib.parse import urljoin
import json
import os
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

logger = logging.getLogger(__name__)

@dataclass
class CropClassification:
    """Crop classification data structure"""
    crop_code: int
    crop_name: str
    crop_category: str
    water_requirements: str
    economic_value: float
    seasonal_pattern: str

class CascadianCurrentUseDataSources:
    """Multi-source agricultural land use classification for Cascadian bioregion"""
    
    def __init__(self):
        self.data_sources = self._init_data_sources()
        self.crop_classifications = self._init_crop_classifications()
        self.target_ca_counties = [
            'Butte', 'Colusa', 'Del Norte', 'Glenn', 'Humboldt', 
            'Lake', 'Lassen', 'Mendocino', 'Modoc', 'Nevada', 
            'Plumas', 'Shasta', 'Sierra', 'Siskiyou', 'Tehama', 'Trinity'
        ]
        
    def _init_data_sources(self) -> Dict[str, Dict]:
        """Initialize data sources configuration"""
        return {
            'nass_cdl': {
                'url': 'https://www.nass.usda.gov/Research_and_Science/Cropland/',
                'api_endpoint': 'https://nassgeodata.gmu.edu/CropScapeService/rest/services/CropScapeService/CDL/MapServer',
                'spatial_resolution': '30 meters',
                'temporal_coverage': '2008-present',
                'classification_categories': '50+ crop-specific categories',
                'api_access': 'USDA APIs with rate limiting',
                'format': 'GeoTIFF raster'
            },
            'land_iq': {
                'partnership': 'California Department of Water Resources',
                'spatial_resolution': '0.5-2.0 acre minimum mapping units',
                'coverage': '15.4 million acres',
                'accuracy': '98%+',
                'update_frequency': 'Annual (water year basis)',
                'api_endpoint': 'https://www.landiq.com/api/v1/',
                'format': 'Vector polygons'
            },
            'oregon_farm_reports': {
                'source': 'Oregon Department of Land Conservation and Development',
                'coverage': 'EFU and forest zone land use decisions',
                'frequency': 'Biennial',
                'data_elements': 'Agricultural land conversion tracking',
                'api_endpoint': 'https://www.oregon.gov/lcd/api/',
                'format': 'Tabular and spatial data'
            },
            'usda_nass_stats': {
                'api_endpoint': 'https://quickstats.nass.usda.gov/api',
                'coverage': 'County-level agricultural statistics',
                'update_frequency': 'Annual',
                'data_elements': 'Crop acreage, production, value',
                'format': 'JSON API'
            }
        }
    
    def _init_crop_classifications(self) -> Dict[int, CropClassification]:
        """Initialize standardized crop classification system"""
        return {
            1: CropClassification(1, 'Corn', 'Field Crops', 'High', 800.0, 'Annual'),
            2: CropClassification(2, 'Cotton', 'Field Crops', 'High', 1200.0, 'Annual'),
            3: CropClassification(3, 'Rice', 'Field Crops', 'Very High', 1500.0, 'Annual'),
            4: CropClassification(4, 'Sorghum', 'Field Crops', 'Medium', 400.0, 'Annual'),
            5: CropClassification(5, 'Soybeans', 'Field Crops', 'Medium', 600.0, 'Annual'),
            6: CropClassification(6, 'Sunflower', 'Field Crops', 'Low', 500.0, 'Annual'),
            10: CropClassification(10, 'Peanuts', 'Field Crops', 'Medium', 1000.0, 'Annual'),
            11: CropClassification(11, 'Tobacco', 'Field Crops', 'High', 2000.0, 'Annual'),
            12: CropClassification(12, 'Sweet Corn', 'Vegetables', 'High', 1200.0, 'Annual'),
            13: CropClassification(13, 'Pop Corn', 'Field Crops', 'Medium', 700.0, 'Annual'),
            14: CropClassification(14, 'Mint', 'Herbs', 'High', 1500.0, 'Perennial'),
            21: CropClassification(21, 'Barley', 'Field Crops', 'Low', 300.0, 'Annual'),
            22: CropClassification(22, 'Durum Wheat', 'Field Crops', 'Low', 400.0, 'Annual'),
            23: CropClassification(23, 'Spring Wheat', 'Field Crops', 'Low', 400.0, 'Annual'),
            24: CropClassification(24, 'Winter Wheat', 'Field Crops', 'Low', 400.0, 'Annual'),
            25: CropClassification(25, 'Other Small Grains', 'Field Crops', 'Low', 350.0, 'Annual'),
            26: CropClassification(26, 'Dbl Crop WinWht/Corn', 'Field Crops', 'Medium', 600.0, 'Annual'),
            27: CropClassification(27, 'Rye', 'Field Crops', 'Low', 300.0, 'Annual'),
            28: CropClassification(28, 'Oats', 'Field Crops', 'Low', 300.0, 'Annual'),
            29: CropClassification(29, 'Millet', 'Field Crops', 'Low', 250.0, 'Annual'),
            30: CropClassification(30, 'Speltz', 'Field Crops', 'Low', 300.0, 'Annual'),
            31: CropClassification(31, 'Canola', 'Field Crops', 'Medium', 500.0, 'Annual'),
            32: CropClassification(32, 'Flaxseed', 'Field Crops', 'Low', 400.0, 'Annual'),
            33: CropClassification(33, 'Safflower', 'Field Crops', 'Low', 400.0, 'Annual'),
            34: CropClassification(34, 'Rape Seed', 'Field Crops', 'Medium', 500.0, 'Annual'),
            35: CropClassification(35, 'Mustard', 'Field Crops', 'Low', 300.0, 'Annual'),
            36: CropClassification(36, 'Alfalfa', 'Forage', 'High', 600.0, 'Perennial'),
            37: CropClassification(37, 'Other Hay/Non Alfalfa', 'Forage', 'Medium', 400.0, 'Perennial'),
            38: CropClassification(38, 'Camelina', 'Field Crops', 'Low', 300.0, 'Annual'),
            39: CropClassification(39, 'Buckwheat', 'Field Crops', 'Low', 200.0, 'Annual'),
            41: CropClassification(41, 'Sugarbeets', 'Field Crops', 'High', 1000.0, 'Annual'),
            42: CropClassification(42, 'Dry Beans', 'Field Crops', 'Medium', 800.0, 'Annual'),
            43: CropClassification(43, 'Potatoes', 'Vegetables', 'High', 1500.0, 'Annual'),
            44: CropClassification(44, 'Other Crops', 'Mixed', 'Medium', 500.0, 'Variable'),
            45: CropClassification(45, 'Sugarcane', 'Field Crops', 'Very High', 2000.0, 'Perennial'),
            46: CropClassification(46, 'Sweet Potatoes', 'Vegetables', 'High', 1200.0, 'Annual'),
            47: CropClassification(47, 'Misc Vegs & Fruits', 'Vegetables', 'High', 1500.0, 'Variable'),
            48: CropClassification(48, 'Watermelons', 'Vegetables', 'High', 1000.0, 'Annual'),
            49: CropClassification(49, 'Onions', 'Vegetables', 'High', 1200.0, 'Annual'),
            50: CropClassification(50, 'Cucumbers', 'Vegetables', 'High', 1000.0, 'Annual'),
            51: CropClassification(51, 'Chick Peas', 'Field Crops', 'Low', 600.0, 'Annual'),
            52: CropClassification(52, 'Lentils', 'Field Crops', 'Low', 500.0, 'Annual'),
            53: CropClassification(53, 'Peas', 'Field Crops', 'Medium', 400.0, 'Annual'),
            54: CropClassification(54, 'Tomatoes', 'Vegetables', 'High', 1800.0, 'Annual'),
            55: CropClassification(55, 'Caneberries', 'Fruits', 'High', 1500.0, 'Perennial'),
            56: CropClassification(56, 'Hops', 'Specialty', 'High', 2000.0, 'Perennial'),
            57: CropClassification(57, 'Herbs', 'Specialty', 'Medium', 1200.0, 'Variable'),
            58: CropClassification(58, 'Clover/Wildflowers', 'Forage', 'Low', 300.0, 'Annual'),
            59: CropClassification(59, 'Sod/Grass Seed', 'Forage', 'High', 800.0, 'Perennial'),
            60: CropClassification(60, 'Switchgrass', 'Forage', 'Low', 200.0, 'Perennial'),
            61: CropClassification(61, 'Fallow/Idle Cropland', 'Fallow', 'None', 0.0, 'Seasonal'),
            63: CropClassification(63, 'Forest', 'Forest', 'Low', 100.0, 'Perennial'),
            64: CropClassification(64, 'Shrubland', 'Natural', 'None', 0.0, 'Perennial'),
            65: CropClassification(65, 'Barren', 'Natural', 'None', 0.0, 'Permanent'),
            66: CropClassification(66, 'Cherries', 'Tree Fruits', 'High', 3000.0, 'Perennial'),
            67: CropClassification(67, 'Peaches', 'Tree Fruits', 'High', 2500.0, 'Perennial'),
            68: CropClassification(68, 'Apples', 'Tree Fruits', 'High', 2800.0, 'Perennial'),
            69: CropClassification(69, 'Grapes', 'Tree Fruits', 'High', 4000.0, 'Perennial'),
            70: CropClassification(70, 'Christmas Trees', 'Specialty', 'Medium', 1000.0, 'Perennial'),
            71: CropClassification(71, 'Other Tree Crops', 'Tree Fruits', 'High', 2000.0, 'Perennial'),
            72: CropClassification(72, 'Citrus', 'Tree Fruits', 'High', 3500.0, 'Perennial'),
            74: CropClassification(74, 'Pecans', 'Tree Fruits', 'Medium', 1500.0, 'Perennial'),
            75: CropClassification(75, 'Almonds', 'Tree Fruits', 'High', 4000.0, 'Perennial'),
            76: CropClassification(76, 'Walnuts', 'Tree Fruits', 'High', 3500.0, 'Perennial'),
            77: CropClassification(77, 'Pears', 'Tree Fruits', 'High', 2500.0, 'Perennial'),
            81: CropClassification(81, 'Clouds/No Data', 'No Data', 'None', 0.0, 'No Data'),
            82: CropClassification(82, 'Developed', 'Developed', 'None', 0.0, 'Permanent'),
            83: CropClassification(83, 'Water', 'Water', 'None', 0.0, 'Permanent'),
            87: CropClassification(87, 'Wetlands', 'Natural', 'None', 0.0, 'Permanent'),
            88: CropClassification(88, 'Nonag/Undefined', 'Natural', 'None', 0.0, 'Permanent'),
            92: CropClassification(92, 'Aquaculture', 'Aquaculture', 'Very High', 5000.0, 'Continuous'),
            111: CropClassification(111, 'Open Water', 'Water', 'None', 0.0, 'Permanent'),
            112: CropClassification(112, 'Perennial Ice/Snow', 'Natural', 'None', 0.0, 'Permanent'),
            121: CropClassification(121, 'Developed/Open Space', 'Developed', 'None', 0.0, 'Permanent'),
            122: CropClassification(122, 'Developed/Low Intensity', 'Developed', 'None', 0.0, 'Permanent'),
            123: CropClassification(123, 'Developed/Med Intensity', 'Developed', 'None', 0.0, 'Permanent'),
            124: CropClassification(124, 'Developed/High Intensity', 'Developed', 'None', 0.0, 'Permanent'),
            131: CropClassification(131, 'Barren Land', 'Natural', 'None', 0.0, 'Permanent'),
            141: CropClassification(141, 'Deciduous Forest', 'Forest', 'Low', 100.0, 'Perennial'),
            142: CropClassification(142, 'Evergreen Forest', 'Forest', 'Low', 100.0, 'Perennial'),
            143: CropClassification(143, 'Mixed Forest', 'Forest', 'Low', 100.0, 'Perennial'),
            152: CropClassification(152, 'Shrubland', 'Natural', 'None', 0.0, 'Perennial'),
            176: CropClassification(176, 'Grassland/Pasture', 'Grassland', 'Low', 200.0, 'Perennial'),
            190: CropClassification(190, 'Woody Wetlands', 'Wetlands', 'None', 0.0, 'Permanent'),
            195: CropClassification(195, 'Herbaceous Wetlands', 'Wetlands', 'None', 0.0, 'Permanent')
        }
    
    def fetch_nass_cdl_data(self, year: int, county: str = None, state: str = 'CA') -> Optional[np.ndarray]:
        """
        Fetch NASS CDL (Cropland Data Layer) raster data from local file
        
        Args:
            year: Year of data to fetch
            county: County name (optional)
            state: State abbreviation
            
        Returns:
            Numpy array with crop classification data or None if fetch fails
        """
        try:
            import rasterio
            
            local_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cdl', f'{year}_{state}.tif')
            if not os.path.exists(local_path):
                logger.error(f'Local CDL file missing: {local_path}')
                logger.info('Please download the CDL GeoTIFF for {state} {year} from:')
                logger.info('https://www.nass.usda.gov/Research_and_Science/Cropland/Release/index.php')
                logger.info('And place it in data/cdl/ as {year}_{state}.tif')
                return None
            
            with rasterio.open(local_path) as src:
                data = src.read(1)  # Read band 1
                # TODO: If county specified, clip to county bounds
                return data
            
        except Exception as e:
            logger.error(f"Error fetching NASS CDL data: {str(e)}")
            return None
    
    def fetch_land_iq_data(self, county: str) -> gpd.GeoDataFrame:
        local_path = self.data_sources['land_iq'].get('local_path', None) # Assuming 'local_path' is a key in data_sources
        if local_path and os.path.exists(local_path):
            logging.info(f"Loading local Land IQ data for {county}")
            return gpd.read_file(local_path)
        
        logging.warning(f"Local Land IQ data not found for {county}. Attempting to fetch from DWR API.")
        
        base_url = "https://gis.water.ca.gov/arcgis/rest/services/Planning/i15_Crop_Mapping_2018/FeatureServer/0/query"
        params = {
            'where': f"COUNTY = '{county.upper()}'",
            'outFields': '*',
            'returnGeometry': True,
            'f': 'geojson',
            'outSR': 4326  # WGS84
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if 'features' in data:
                gdf = gpd.GeoDataFrame.from_features(data['features'])
                logging.info(f"Successfully fetched Land IQ data for {county} from API.")
                return gdf
            else:
                logging.error(f"No features returned from Land IQ API for {county}.")
                return self.generate_fallback_current_use_data(county)
        except Exception as e:
            logging.error(f"Error fetching Land IQ data from API for {county}: {str(e)}")
            return self.generate_fallback_current_use_data(county)
    
    def fetch_oregon_efu_reports(self, year: int = None) -> pd.DataFrame:
        """
        Fetch Oregon EFU land use reports from local file
        
        Args:
            year: Year of data to fetch (optional)
            
        Returns:
            DataFrame with Oregon agricultural land use data or empty if fails
        """
        try:
            year = year or datetime.now().year
            local_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'oregon_efu', f'efu_report_{year}.csv')
            if not os.path.exists(local_path):
                logger.error(f'Local Oregon EFU file missing: {local_path}')
                logger.info('Please download the EFU report from:')
                logger.info('https://www.oregon.gov/lcd/FF/Pages/Farm-Forest-Reports.aspx')
                logger.info('Convert to CSV if needed and place in data/oregon_efu/')
                return pd.DataFrame()
            
            return pd.read_csv(local_path)
            
        except Exception as e:
            logger.error(f"Error fetching Oregon EFU reports: {str(e)}")
            return pd.DataFrame()
    
    def fetch_usda_nass_stats(self, year: int, commodity: str = None, 
                             county: str = None, state: str = 'CA') -> pd.DataFrame:
        """
        Fetch USDA NASS QuickStats data
        
        Args:
            year: Year of data
            commodity: Commodity name (optional)
            county: County name (optional)
            state: State abbreviation
            
        Returns:
            DataFrame with agricultural statistics
        """
        try:
            nass_config = self.data_sources['usda_nass_stats']
            
            # Construct NASS API query
            base_url = nass_config['api_endpoint']
            
            params = {
                'key': 'API_KEY_PLACEHOLDER',  # Would need actual API key
                'source_desc': 'CENSUS',
                'year': year,
                'state_alpha': state,
                'format': 'JSON'
            }
            
            if commodity:
                params['commodity_desc'] = commodity
            if county:
                params['county_name'] = county
            
            logger.info(f"Fetching NASS stats for {year}, {commodity or 'all commodities'}, {county or 'all counties'}, {state}")
            
            # Placeholder for actual NASS API call
            # In production, this would make actual API request
            
            # Return empty DataFrame for now
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching NASS stats: {str(e)}")
            raise
    
    def get_crop_classification(self, crop_code: int) -> Optional[CropClassification]:
        """
        Get crop classification information
        
        Args:
            crop_code: CDL crop code
            
        Returns:
            CropClassification object or None if not found
        """
        return self.crop_classifications.get(crop_code)
    
    def classify_crop_category(self, crop_code: int) -> str:
        """
        Classify crop into broad category
        
        Args:
            crop_code: CDL crop code
            
        Returns:
            Crop category string
        """
        classification = self.get_crop_classification(crop_code)
        return classification.crop_category if classification else 'Unknown'
    
    def estimate_water_requirements(self, crop_code: int) -> str:
        """
        Estimate water requirements for crop
        
        Args:
            crop_code: CDL crop code
            
        Returns:
            Water requirement level
        """
        classification = self.get_crop_classification(crop_code)
        return classification.water_requirements if classification else 'Unknown'
    
    def estimate_economic_value(self, crop_code: int) -> float:
        """
        Estimate economic value per acre for crop
        
        Args:
            crop_code: CDL crop code
            
        Returns:
            Economic value per acre (USD)
        """
        classification = self.get_crop_classification(crop_code)
        return classification.economic_value if classification else 0.0
    
    def get_seasonal_pattern(self, crop_code: int) -> str:
        """
        Get seasonal pattern for crop
        
        Args:
            crop_code: CDL crop code
            
        Returns:
            Seasonal pattern string
        """
        classification = self.get_crop_classification(crop_code)
        return classification.seasonal_pattern if classification else 'Unknown'
    
    def validate_data_availability(self, year: int, source: str = 'nass_cdl') -> bool:
        """
        Validate data availability for given year and source
        
        Args:
            year: Year to validate
            source: Data source name
            
        Returns:
            True if data is available
        """
        try:
            current_year = datetime.now().year
            
            if source == 'nass_cdl':
                return 2008 <= year <= current_year - 1  # CDL has 1-year delay
            elif source == 'land_iq':
                return 2014 <= year <= current_year - 1  # Land IQ started 2014
            elif source == 'oregon_farm_reports':
                return 2018 <= year <= current_year  # Recent Oregon reporting
            elif source == 'usda_nass_stats':
                return 2012 <= year <= current_year - 1  # NASS stats availability
            else:
                return False
                
        except Exception as e:
            logger.warning(f"Could not validate data availability: {str(e)}")
            return False
    
    def get_available_years(self, source: str = 'nass_cdl') -> List[int]:
        """
        Get list of available years for data source
        
        Args:
            source: Data source name
            
        Returns:
            List of available years
        """
        current_year = datetime.now().year
        
        if source == 'nass_cdl':
            return list(range(2008, current_year))
        elif source == 'land_iq':
            return list(range(2014, current_year))
        elif source == 'oregon_farm_reports':
            return list(range(2018, current_year + 1))
        elif source == 'usda_nass_stats':
            return list(range(2012, current_year))
        else:
            return []
    
    def get_target_counties(self, state: str = 'CA') -> List[str]:
        """
        Get list of target counties
        
        Args:
            state: State abbreviation
            
        Returns:
            List of county names
        """
        if state == 'CA':
            return self.target_ca_counties
        elif state == 'OR':
            return [f"Oregon County {i}" for i in range(1, 37)]  # Placeholder
        else:
            return [] 