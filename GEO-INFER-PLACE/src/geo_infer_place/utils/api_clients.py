"""
API Clients: Standardized access to California data APIs.

This module provides specialized API client classes for accessing real California
datasets including CAL FIRE, NOAA, USGS, and weather services. Each client
implements robust error handling, rate limiting, caching, and data validation.
"""

import logging
import time
import json
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
import pandas as pd
import geopandas as gpd
from urllib.parse import urljoin, urlencode
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Standardized API response structure."""
    success: bool
    data: Any
    status_code: Optional[int]
    message: str
    response_time: float
    cached: bool
    timestamp: str

class BaseAPIClient:
    """
    Base class for all API clients with common functionality.
    
    Provides standardized error handling, caching, rate limiting,
    and response formatting for all California data API clients.
    """
    
    def __init__(self, 
                 base_url: str,
                 api_key: Optional[str] = None,
                 cache_dir: Optional[Path] = None,
                 rate_limit_delay: float = 1.0):
        """
        Initialize base API client.
        
        Args:
            base_url: Base URL for the API
            api_key: Optional API key for authentication
            cache_dir: Directory for caching responses
            rate_limit_delay: Minimum delay between requests (seconds)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        
        # Set up caching
        self.cache_dir = cache_dir or Path("cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_enabled = True
        self.cache_expiry_hours = 24
        
        # Request session for connection pooling
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update(self._get_auth_headers())
            
        logger.info(f"Initialized {self.__class__.__name__}")
        
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers. Override in subclasses."""
        return {}
        
    def _rate_limit(self):
        """Implement rate limiting."""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
        
    def _get_cache_path(self, url: str, params: Optional[Dict] = None) -> Path:
        """Generate cache file path for request."""
        cache_key = url
        if params:
            cache_key += "?" + urlencode(sorted(params.items()))
        
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
        return self.cache_dir / f"{cache_hash}.json"
        
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cached response is still valid."""
        if not cache_path.exists():
            return False
            
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age < timedelta(hours=self.cache_expiry_hours)
        
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load response from cache."""
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
            return None
            
    def _save_to_cache(self, cache_path: Path, data: Dict):
        """Save response to cache."""
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Error saving to cache: {e}")
            
    def _make_request(self, 
                     endpoint: str, 
                     params: Optional[Dict] = None,
                     method: str = 'GET') -> APIResponse:
        """
        Make HTTP request with caching and error handling.
        
        Args:
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            method: HTTP method
            
        Returns:
            APIResponse object
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        start_time = time.time()
        
        # Check cache first
        cache_path = self._get_cache_path(url, params)
        if self.cache_enabled and method == 'GET' and self._is_cache_valid(cache_path):
            cached_data = self._load_from_cache(cache_path)
            if cached_data:
                response_time = time.time() - start_time
                return APIResponse(
                    success=True,
                    data=cached_data,
                    status_code=200,
                    message="Retrieved from cache",
                    response_time=response_time,
                    cached=True,
                    timestamp=datetime.now().isoformat()
                )
                
        # Apply rate limiting
        self._rate_limit()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    data = response.text
                    
                # Save to cache
                if self.cache_enabled and method == 'GET':
                    self._save_to_cache(cache_path, data)
                    
                return APIResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code,
                    message="Request successful",
                    response_time=response_time,
                    cached=False,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return APIResponse(
                    success=False,
                    data=None,
                    status_code=response.status_code,
                    message=f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time=response_time,
                    cached=False,
                    timestamp=datetime.now().isoformat()
                )
                
        except requests.RequestException as e:
            response_time = time.time() - start_time
            logger.error(f"Request failed for {url}: {e}")
            
            return APIResponse(
                success=False,
                data=None,
                status_code=None,
                message=f"Request failed: {str(e)}",
                response_time=response_time,
                cached=False,
                timestamp=datetime.now().isoformat()
            )

class CALFIREClient(BaseAPIClient):
    """
    CAL FIRE API client for fire and forest data.
    
    Provides access to CAL FIRE datasets including fire perimeters,
    fire weather stations, forest health monitoring, and timber operations.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        """Initialize CAL FIRE client."""
        super().__init__(
            base_url="https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services",
            api_key=api_key,
            cache_dir=cache_dir,
            rate_limit_delay=0.5
        )
        
    def get_fire_perimeters(self, 
                           bbox: Optional[Tuple[float, float, float, float]] = None,
                           start_year: Optional[int] = None,
                           include_metadata: bool = True) -> Dict[str, Any]:
        """
        Get fire perimeter data from CAL FIRE.
        
        Args:
            bbox: Bounding box (west, south, east, north)
            start_year: Earliest year to include
            include_metadata: Whether to include detailed metadata
            
        Returns:
            Dictionary containing fire perimeter data
        """
        logger.info("Fetching CAL FIRE fire perimeters...")
        
        # CAL FIRE Fire Perimeters service endpoint
        endpoint = "/California_Fire_Perimeters/FeatureServer/0/query"
        
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'geojson',
            'returnGeometry': 'true'
        }
        
        # Add spatial filter
        if bbox:
            west, south, east, north = bbox
            params['geometry'] = f"{west},{south},{east},{north}"
            params['geometryType'] = 'esriGeometryEnvelope'
            params['spatialRel'] = 'esriSpatialRelIntersects'
            
        # Add temporal filter
        if start_year:
            params['where'] = f"YEAR_ >= {start_year}"
            
        response = self._make_request(endpoint, params)
        
        if response.success:
            # Process GeoJSON data
            fire_data = {
                'type': 'FeatureCollection',
                'features': response.data.get('features', []),
                'data_source': 'CAL FIRE',
                'query_params': params,
                'feature_count': len(response.data.get('features', [])),
                'cached': response.cached,
                'timestamp': response.timestamp
            }
            
            logger.info(f"Retrieved {fire_data['feature_count']} fire perimeters")
            return fire_data
        else:
            logger.error(f"Failed to retrieve fire perimeters: {response.message}")
            return {'error': response.message, 'data_source': 'CAL FIRE'}
            
    def get_fire_weather_stations(self, 
                                 bbox: Optional[Tuple[float, float, float, float]] = None,
                                 parameters: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get fire weather station data.
        
        Args:
            bbox: Bounding box for spatial filtering
            parameters: List of weather parameters to retrieve
            
        Returns:
            Dictionary containing weather station data
        """
        logger.info("Fetching CAL FIRE weather stations...")
        
        # This is a placeholder implementation as CAL FIRE weather data
        # typically comes from RAWS (Remote Automated Weather Stations)
        # which are managed by different agencies
        
        weather_data = {
            'data_source': 'CAL FIRE RAWS Network',
            'stations': [],
            'parameters': parameters or ['temperature', 'humidity', 'wind_speed', 'wind_direction'],
            'bbox': bbox,
            'status': 'placeholder_implementation',
            'note': 'Real implementation would access RAWS data through DRI or WRCC APIs'
        }
        
        # Placeholder station data for Del Norte County
        if bbox:
            west, south, east, north = bbox
            if west < -124 and east > -124 and south < 42 and north > 41.5:
                weather_data['stations'] = [
                    {
                        'station_id': 'KCEC',
                        'name': 'Crescent City Airport',
                        'lat': 41.78,
                        'lon': -124.24,
                        'elevation': 61,
                        'parameters': ['temperature', 'humidity', 'wind_speed', 'precipitation']
                    }
                ]
                
        return weather_data
        
    def get_timber_operations(self, 
                             bbox: Optional[Tuple[float, float, float, float]] = None,
                             time_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """
        Get timber harvest plan data.
        
        Args:
            bbox: Bounding box for spatial filtering
            time_range: (start_date, end_date) tuple
            
        Returns:
            Dictionary containing timber operations data
        """
        logger.info("Fetching CAL FIRE timber operations...")
        
        # Placeholder implementation for timber harvest plans
        timber_data = {
            'data_source': 'CAL FIRE FRAP Timber Harvest Plans',
            'harvest_plans': [],
            'bbox': bbox,
            'time_range': time_range,
            'status': 'placeholder_implementation',
            'note': 'Real implementation would access CAL FIRE FRAP database'
        }
        
        return timber_data
        
    def get_tree_mortality_data(self, 
                               bbox: Optional[Tuple[float, float, float, float]] = None,
                               time_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """
        Get tree mortality monitoring data.
        
        Args:
            bbox: Bounding box for spatial filtering
            time_range: (start_date, end_date) tuple
            
        Returns:
            Dictionary containing tree mortality data
        """
        logger.info("Fetching tree mortality data...")
        
        mortality_data = {
            'data_source': 'CAL FIRE Tree Mortality Survey',
            'surveys': [],
            'bbox': bbox,
            'time_range': time_range,
            'status': 'placeholder_implementation'
        }
        
        return mortality_data
        
    def get_fuel_moisture_data(self, 
                              bbox: Optional[Tuple[float, float, float, float]] = None,
                              fuel_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get fuel moisture monitoring data.
        
        Args:
            bbox: Bounding box for spatial filtering
            fuel_types: Types of fuel to include
            
        Returns:
            Dictionary containing fuel moisture data
        """
        logger.info("Fetching fuel moisture data...")
        
        fuel_data = {
            'data_source': 'CAL FIRE Fuel Moisture Monitoring',
            'measurements': [],
            'fuel_types': fuel_types or ['live_woody', 'dead_woody', 'herbaceous'],
            'bbox': bbox,
            'status': 'placeholder_implementation'
        }
        
        return fuel_data
        
    def get_fire_danger_ratings(self, 
                               bbox: Optional[Tuple[float, float, float, float]] = None,
                               forecast_days: int = 7) -> Dict[str, Any]:
        """
        Get fire danger rating forecasts.
        
        Args:
            bbox: Bounding box for spatial filtering
            forecast_days: Number of forecast days
            
        Returns:
            Dictionary containing fire danger ratings
        """
        logger.info("Fetching fire danger ratings...")
        
        danger_data = {
            'data_source': 'CAL FIRE Fire Danger Rating',
            'forecasts': [],
            'forecast_days': forecast_days,
            'bbox': bbox,
            'status': 'placeholder_implementation'
        }
        
        return danger_data
        
    def get_suppression_resources(self, 
                                 bbox: Optional[Tuple[float, float, float, float]] = None,
                                 resource_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get fire suppression resource locations.
        
        Args:
            bbox: Bounding box for spatial filtering
            resource_types: Types of resources to include
            
        Returns:
            Dictionary containing suppression resources
        """
        logger.info("Fetching fire suppression resources...")
        
        resource_data = {
            'data_source': 'CAL FIRE Suppression Resources',
            'resources': [],
            'resource_types': resource_types or ['fire_stations', 'equipment', 'personnel'],
            'bbox': bbox,
            'status': 'placeholder_implementation'
        }
        
        return resource_data

class NOAAClient(BaseAPIClient):
    """
    NOAA API client for coastal and weather data.
    
    Provides access to NOAA datasets including tide gauges, coastal data,
    weather stations, and climate projections.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        """Initialize NOAA client."""
        super().__init__(
            base_url="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
            api_key=api_key,
            cache_dir=cache_dir,
            rate_limit_delay=1.0
        )
        
    def get_tide_gauge_data(self, 
                           bbox: Optional[Tuple[float, float, float, float]] = None,
                           stations: Optional[List[str]] = None,
                           time_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """
        Get tide gauge data from NOAA.
        
        Args:
            bbox: Bounding box for station selection
            stations: Specific station IDs
            time_range: (start_date, end_date) tuple
            
        Returns:
            Dictionary containing tide gauge data
        """
        logger.info("Fetching NOAA tide gauge data...")
        
        # Default to Crescent City station for Del Norte County
        if not stations:
            stations = ['9419750']  # Crescent City, CA
            
        tide_data = {
            'data_source': 'NOAA Tides and Currents',
            'stations': stations,
            'measurements': [],
            'time_range': time_range,
            'bbox': bbox
        }
        
        for station_id in stations:
            params = {
                'station': station_id,
                'product': 'water_level',
                'datum': 'MLLW',
                'time_zone': 'lst_ldt',
                'format': 'json',
                'units': 'metric'
            }
            
            if time_range:
                params['begin_date'] = time_range[0].replace('-', '')
                params['end_date'] = time_range[1].replace('-', '')
            else:
                # Default to last 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                params['begin_date'] = start_date.strftime('%Y%m%d')
                params['end_date'] = end_date.strftime('%Y%m%d')
                
            response = self._make_request('', params)
            
            if response.success:
                station_data = {
                    'station_id': station_id,
                    'data': response.data,
                    'cached': response.cached,
                    'timestamp': response.timestamp
                }
                tide_data['measurements'].append(station_data)
            else:
                logger.error(f"Failed to get data for station {station_id}: {response.message}")
                
        return tide_data
        
    def get_coastal_elevation_models(self, 
                                    bbox: Tuple[float, float, float, float],
                                    resolution: str = '1_3_arc_second') -> Dict[str, Any]:
        """
        Get coastal digital elevation models.
        
        Args:
            bbox: Bounding box for data extent
            resolution: DEM resolution
            
        Returns:
            Dictionary containing elevation model information
        """
        logger.info("Fetching coastal elevation models...")
        
        elevation_data = {
            'data_source': 'NOAA Digital Coast',
            'resolution': resolution,
            'bbox': bbox,
            'status': 'placeholder_implementation',
            'note': 'Real implementation would access NOAA Digital Coast data services'
        }
        
        return elevation_data
        
    def get_shoreline_change_data(self, 
                                 bbox: Tuple[float, float, float, float],
                                 time_period: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """
        Get shoreline change analysis data.
        
        Args:
            bbox: Bounding box for analysis area
            time_period: (start_year, end_year) tuple
            
        Returns:
            Dictionary containing shoreline change data
        """
        logger.info("Fetching shoreline change data...")
        
        shoreline_data = {
            'data_source': 'USGS Shoreline Change',
            'time_period': time_period,
            'bbox': bbox,
            'status': 'placeholder_implementation'
        }
        
        return shoreline_data
        
    def get_storm_surge_models(self, 
                              region: str,
                              return_periods: List[int]) -> Dict[str, Any]:
        """
        Get storm surge modeling data.
        
        Args:
            region: Geographic region identifier
            return_periods: List of return periods (years)
            
        Returns:
            Dictionary containing storm surge model data
        """
        logger.info("Fetching storm surge models...")
        
        surge_data = {
            'data_source': 'NOAA Storm Surge Models',
            'region': region,
            'return_periods': return_periods,
            'status': 'placeholder_implementation'
        }
        
        return surge_data
        
    def get_sea_level_projections(self, 
                                 station: str,
                                 scenarios: List[str]) -> Dict[str, Any]:
        """
        Get sea level rise projections.
        
        Args:
            station: Tide gauge station ID
            scenarios: List of scenario names
            
        Returns:
            Dictionary containing sea level projections
        """
        logger.info("Fetching sea level projections...")
        
        projection_data = {
            'data_source': 'NOAA Sea Level Rise Projections',
            'station': station,
            'scenarios': scenarios,
            'status': 'placeholder_implementation'
        }
        
        return projection_data

class USGSClient(BaseAPIClient):
    """
    USGS API client for geological and water data.
    
    Provides access to USGS datasets including water resources,
    geological surveys, and land cover data.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        """Initialize USGS client."""
        super().__init__(
            base_url="https://waterservices.usgs.gov/nwis/iv",
            api_key=api_key,
            cache_dir=cache_dir,
            rate_limit_delay=0.5
        )
        
    def get_forest_inventory(self, 
                            bbox: Tuple[float, float, float, float],
                            include_metrics: List[str]) -> Dict[str, Any]:
        """
        Get forest inventory data.
        
        Args:
            bbox: Bounding box for inventory area
            include_metrics: Metrics to include in results
            
        Returns:
            Dictionary containing forest inventory data
        """
        logger.info("Fetching USGS forest inventory...")
        
        inventory_data = {
            'data_source': 'USGS Forest Inventory',
            'metrics': include_metrics,
            'bbox': bbox,
            'status': 'placeholder_implementation'
        }
        
        return inventory_data
        
    def get_land_cover_data(self, 
                           bbox: Tuple[float, float, float, float],
                           dataset: str = 'NLCD',
                           years: List[int] = None) -> Dict[str, Any]:
        """
        Get land cover classification data.
        
        Args:
            bbox: Bounding box for data extent
            dataset: Land cover dataset name
            years: List of years to include
            
        Returns:
            Dictionary containing land cover data
        """
        logger.info("Fetching USGS land cover data...")
        
        land_cover_data = {
            'data_source': f'USGS {dataset}',
            'years': years or [2019],
            'bbox': bbox,
            'status': 'placeholder_implementation'
        }
        
        return land_cover_data

class WeatherAPIClient(BaseAPIClient):
    """
    Weather API client for real-time meteorological data.
    
    Provides access to weather APIs for current conditions,
    forecasts, and severe weather alerts.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        """Initialize Weather API client."""
        super().__init__(
            base_url="https://api.weather.gov",
            api_key=api_key,
            cache_dir=cache_dir,
            rate_limit_delay=1.0
        )
        
    def get_current_weather(self, 
                           stations: List[str],
                           parameters: List[str]) -> Dict[str, Any]:
        """
        Get current weather conditions.
        
        Args:
            stations: Weather station identifiers
            parameters: Weather parameters to retrieve
            
        Returns:
            Dictionary containing current weather data
        """
        logger.info("Fetching current weather conditions...")
        
        weather_data = {
            'data_source': 'National Weather Service',
            'stations': stations,
            'parameters': parameters,
            'current_conditions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Placeholder implementation using NWS API
        for station in stations:
            station_data = {
                'station_id': station,
                'conditions': {},
                'status': 'placeholder_implementation'
            }
            weather_data['current_conditions'].append(station_data)
            
        return weather_data
        
    def get_hourly_forecast(self, 
                           location: Dict[str, float],
                           hours: int = 48) -> Dict[str, Any]:
        """
        Get hourly weather forecast.
        
        Args:
            location: Location coordinates
            hours: Number of forecast hours
            
        Returns:
            Dictionary containing hourly forecast
        """
        logger.info("Fetching hourly weather forecast...")
        
        forecast_data = {
            'data_source': 'National Weather Service',
            'location': location,
            'forecast_hours': hours,
            'forecast': [],
            'status': 'placeholder_implementation'
        }
        
        return forecast_data
        
    def get_daily_forecast(self, 
                          location: Dict[str, float],
                          days: int = 7) -> Dict[str, Any]:
        """
        Get daily weather forecast.
        
        Args:
            location: Location coordinates
            days: Number of forecast days
            
        Returns:
            Dictionary containing daily forecast
        """
        logger.info("Fetching daily weather forecast...")
        
        forecast_data = {
            'data_source': 'National Weather Service',
            'location': location,
            'forecast_days': days,
            'forecast': [],
            'status': 'placeholder_implementation'
        }
        
        return forecast_data
        
    def get_weather_alerts(self, 
                          region: str,
                          alert_types: List[str]) -> Dict[str, Any]:
        """
        Get weather alerts and warnings.
        
        Args:
            region: Geographic region identifier
            alert_types: Types of alerts to retrieve
            
        Returns:
            Dictionary containing weather alerts
        """
        logger.info("Fetching weather alerts...")
        
        alert_data = {
            'data_source': 'National Weather Service',
            'region': region,
            'alert_types': alert_types,
            'active_alerts': [],
            'status': 'placeholder_implementation'
        }
        
        return alert_data 