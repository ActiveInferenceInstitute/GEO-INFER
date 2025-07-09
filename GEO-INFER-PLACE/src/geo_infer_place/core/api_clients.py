"""
CaliforniaAPIClients: Real data integration with California and federal APIs.

This module provides standardized API clients for fetching real data from
California-specific and federal data sources including CAL FIRE, NOAA, USGS,
CDEC, and other government APIs. It implements authentication, rate limiting,
error handling, and data standardization.
"""

import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from urllib.parse import urljoin, urlencode
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import geopandas as gpd

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Standardized API response object."""
    success: bool
    data: Any
    error: Optional[str] = None
    response_time_ms: Optional[int] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAPIClient:
    """Base class for all API clients with common functionality."""
    
    def __init__(self, 
                 base_url: str, 
                 api_key: Optional[str] = None,
                 rate_limit_calls: int = 100,
                 rate_limit_period: int = 3600,
                 timeout: int = 30):
        """
        Initialize base API client.
        
        Args:
            base_url: Base URL for the API
            api_key: Optional API key for authentication
            rate_limit_calls: Maximum calls per period
            rate_limit_period: Rate limit period in seconds
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.rate_limit_calls = rate_limit_calls
        self.rate_limit_period = rate_limit_period
        self.timeout = timeout
        
        # Request session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rate limiting
        self.request_history = []
        
        logger.info(f"Initialized {self.__class__.__name__} with base URL: {base_url}")
        
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = time.time()
        # Remove old requests
        cutoff = now - self.rate_limit_period
        self.request_history = [req_time for req_time in self.request_history if req_time > cutoff]
        
        if len(self.request_history) >= self.rate_limit_calls:
            sleep_time = self.rate_limit_period - (now - self.request_history[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                return False
        return True
        
    def _make_request(self, 
                     endpoint: str, 
                     params: Optional[Dict] = None,
                     method: str = 'GET',
                     headers: Optional[Dict] = None) -> APIResponse:
        """Make a standardized API request."""
        
        # Rate limiting
        self._check_rate_limit()
        self.request_history.append(time.time())
        
        # Prepare request
        url = urljoin(self.base_url + '/', endpoint)
        
        if headers is None:
            headers = {}
            
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = response.text
                    
                return APIResponse(
                    success=True,
                    data=data,
                    response_time_ms=response_time_ms,
                    source=self.__class__.__name__,
                    timestamp=datetime.now(),
                    metadata={'status_code': response.status_code, 'url': url}
                )
            else:
                return APIResponse(
                    success=False,
                    data=None,
                    error=f"HTTP {response.status_code}: {response.reason}",
                    response_time_ms=response_time_ms,
                    source=self.__class__.__name__,
                    timestamp=datetime.now(),
                    metadata={'status_code': response.status_code, 'url': url}
                )
                
        except requests.exceptions.Timeout:
            return APIResponse(
                success=False,
                data=None,
                error="Request timeout",
                source=self.__class__.__name__,
                timestamp=datetime.now()
            )
        except requests.exceptions.ConnectionError:
            return APIResponse(
                success=False,
                data=None,
                error="Connection error",
                source=self.__class__.__name__,
                timestamp=datetime.now()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                error=f"Request error: {str(e)}",
                source=self.__class__.__name__,
                timestamp=datetime.now()
            )

class CALFIREClient(BaseAPIClient):
    """API client for CAL FIRE data services."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            base_url="https://calfire-forestry.maps.arcgis.com/sharing/rest/services",
            api_key=api_key,
            rate_limit_calls=50,
            rate_limit_period=60
        )
        
    def get_fire_perimeters(self, 
                           bbox: Optional[Tuple[float, float, float, float]] = None,
                           year: Optional[int] = None,
                           active_only: bool = False) -> APIResponse:
        """
        Get fire perimeter data from CAL FIRE.
        
        Args:
            bbox: Bounding box as (west, south, east, north)
            year: Filter by fire year
            active_only: Only return active fires
            
        Returns:
            APIResponse with fire perimeter data
        """
        endpoint = "CALFIRE_Fire_Perimeters/MapServer/0/query"
        
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
            
        # Add year filter
        if year:
            params['where'] += f" AND FIRE_YEAR = {year}"
            
        # Add active filter
        if active_only:
            params['where'] += " AND ACTIVE = 'Y'"
            
        response = self._make_request(endpoint, params)
        
        if response.success and response.data:
            # Convert to standardized format
            response.data = self._standardize_fire_data(response.data)
            
        return response
        
    def get_fire_weather_stations(self, 
                                 station_ids: Optional[List[str]] = None,
                                 bbox: Optional[Tuple[float, float, float, float]] = None) -> APIResponse:
        """
        Get fire weather station data.
        
        Args:
            station_ids: Specific station IDs to retrieve
            bbox: Bounding box filter
            
        Returns:
            APIResponse with weather station data
        """
        endpoint = "CALFIRE_Weather_Stations/MapServer/0/query"
        
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'geojson',
            'returnGeometry': 'true'
        }
        
        if station_ids:
            station_list = "','".join(station_ids)
            params['where'] += f" AND STATION_ID IN ('{station_list}')"
            
        if bbox:
            west, south, east, north = bbox
            params['geometry'] = f"{west},{south},{east},{north}"
            params['geometryType'] = 'esriGeometryEnvelope'
            params['spatialRel'] = 'esriSpatialRelIntersects'
            
        return self._make_request(endpoint, params)
        
    def _standardize_fire_data(self, raw_data: Dict) -> Dict:
        """Standardize CAL FIRE data format."""
        standardized = {
            'type': 'fire_perimeters',
            'source': 'CAL_FIRE',
            'features': [],
            'metadata': {
                'total_features': len(raw_data.get('features', [])),
                'processed_at': datetime.now().isoformat()
            }
        }
        
        for feature in raw_data.get('features', []):
            properties = feature.get('properties', {})
            
            standardized_feature = {
                'type': 'Feature',
                'geometry': feature.get('geometry'),
                'properties': {
                    'fire_name': properties.get('FIRE_NAME'),
                    'fire_year': properties.get('FIRE_YEAR'),
                    'acres_burned': properties.get('ACRES'),
                    'start_date': properties.get('ALARM_DATE'),
                    'containment_date': properties.get('CONT_DATE'),
                    'active': properties.get('ACTIVE') == 'Y',
                    'cause': properties.get('CAUSE'),
                    'unit': properties.get('UNIT_ID')
                }
            }
            
            standardized['features'].append(standardized_feature)
            
        return standardized

class NOAAClient(BaseAPIClient):
    """API client for NOAA data services."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            base_url="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
            api_key=api_key,
            rate_limit_calls=1000,
            rate_limit_period=60
        )
        
    def get_tide_data(self, 
                     station_id: str,
                     start_date: datetime,
                     end_date: datetime,
                     product: str = 'water_level',
                     datum: str = 'MLLW',
                     units: str = 'metric') -> APIResponse:
        """
        Get tide gauge data from NOAA.
        
        Args:
            station_id: NOAA station ID
            start_date: Start date for data
            end_date: End date for data
            product: Data product type
            datum: Vertical datum
            units: Unit system
            
        Returns:
            APIResponse with tide data
        """
        params = {
            'product': product,
            'application': 'GEO-INFER',
            'begin_date': start_date.strftime('%Y%m%d %H:%M'),
            'end_date': end_date.strftime('%Y%m%d %H:%M'),
            'station': station_id,
            'time_zone': 'gmt',
            'units': units,
            'datum': datum,
            'format': 'json'
        }
        
        response = self._make_request('', params)
        
        if response.success and response.data:
            response.data = self._standardize_tide_data(response.data, station_id)
            
        return response
        
    def get_stations_metadata(self, 
                            bbox: Optional[Tuple[float, float, float, float]] = None) -> APIResponse:
        """
        Get metadata for tide gauge stations.
        
        Args:
            bbox: Bounding box filter
            
        Returns:
            APIResponse with station metadata
        """
        # NOAA stations API endpoint
        base_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
        
        params = {}
        if bbox:
            west, south, east, north = bbox
            params['bbox'] = f"{west},{south},{east},{north}"
            
        # Override base URL for this specific request
        original_base_url = self.base_url
        self.base_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi"
        
        response = self._make_request('stations.json', params)
        
        # Restore original base URL
        self.base_url = original_base_url
        
        return response
        
    def _standardize_tide_data(self, raw_data: Dict, station_id: str) -> Dict:
        """Standardize NOAA tide data format."""
        standardized = {
            'type': 'tide_data',
            'source': 'NOAA',
            'station_id': station_id,
            'data': [],
            'metadata': {
                'total_records': len(raw_data.get('data', [])),
                'processed_at': datetime.now().isoformat()
            }
        }
        
        for record in raw_data.get('data', []):
            standardized_record = {
                'timestamp': record.get('t'),
                'water_level': float(record.get('v', 0)) if record.get('v') else None,
                'quality': record.get('q', 'unknown')
            }
            standardized['data'].append(standardized_record)
            
        return standardized

class USGSClient(BaseAPIClient):
    """API client for USGS water data services."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            base_url="https://waterservices.usgs.gov/nwis/iv",
            api_key=api_key,
            rate_limit_calls=1000,
            rate_limit_period=60
        )
        
    def get_streamflow_data(self, 
                          site_codes: List[str],
                          start_date: datetime,
                          end_date: datetime,
                          parameter_codes: List[str] = None) -> APIResponse:
        """
        Get streamflow data from USGS.
        
        Args:
            site_codes: USGS site codes
            start_date: Start date
            end_date: End date
            parameter_codes: Parameter codes (default: streamflow)
            
        Returns:
            APIResponse with streamflow data
        """
        if parameter_codes is None:
            parameter_codes = ['00060']  # Discharge (streamflow)
            
        params = {
            'format': 'json',
            'sites': ','.join(site_codes),
            'startDT': start_date.strftime('%Y-%m-%d'),
            'endDT': end_date.strftime('%Y-%m-%d'),
            'parameterCd': ','.join(parameter_codes),
            'siteStatus': 'all'
        }
        
        response = self._make_request('', params)
        
        if response.success and response.data:
            response.data = self._standardize_usgs_data(response.data)
            
        return response
        
    def get_site_info(self, 
                     bbox: Optional[Tuple[float, float, float, float]] = None,
                     state_code: str = 'CA') -> APIResponse:
        """
        Get USGS site information.
        
        Args:
            bbox: Bounding box filter
            state_code: State code filter
            
        Returns:
            APIResponse with site information
        """
        # Use site web service
        base_url = "https://waterservices.usgs.gov/nwis/site"
        
        params = {
            'format': 'json',
            'stateCd': state_code,
            'siteType': 'ST',  # Stream sites
            'hasDataTypeCd': 'dv'  # Has daily values
        }
        
        if bbox:
            west, south, east, north = bbox
            params['bBox'] = f"{west},{south},{east},{north}"
            
        # Override base URL for this request
        original_base_url = self.base_url
        self.base_url = "https://waterservices.usgs.gov/nwis"
        
        response = self._make_request('site', params)
        
        # Restore original base URL
        self.base_url = original_base_url
        
        return response
        
    def _standardize_usgs_data(self, raw_data: Dict) -> Dict:
        """Standardize USGS data format."""
        standardized = {
            'type': 'streamflow_data',
            'source': 'USGS',
            'sites': [],
            'metadata': {
                'processed_at': datetime.now().isoformat()
            }
        }
        
        time_series = raw_data.get('value', {}).get('timeSeries', [])
        
        for series in time_series:
            site_info = series.get('sourceInfo', {})
            variable_info = series.get('variable', {})
            values = series.get('values', [{}])[0].get('value', [])
            
            site_data = {
                'site_code': site_info.get('siteCode', [{}])[0].get('value'),
                'site_name': site_info.get('siteName'),
                'latitude': float(site_info.get('geoLocation', {}).get('geogLocation', {}).get('latitude', 0)),
                'longitude': float(site_info.get('geoLocation', {}).get('geogLocation', {}).get('longitude', 0)),
                'parameter': variable_info.get('variableName'),
                'unit': variable_info.get('unit', {}).get('unitCode'),
                'data': []
            }
            
            for value in values:
                data_point = {
                    'timestamp': value.get('dateTime'),
                    'value': float(value.get('value', 0)) if value.get('value') else None,
                    'qualifiers': value.get('qualifiers', [])
                }
                site_data['data'].append(data_point)
                
            standardized['sites'].append(site_data)
            
        return standardized

class CDECClient(BaseAPIClient):
    """API client for California Data Exchange Center."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            base_url="https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet",
            api_key=api_key,
            rate_limit_calls=100,
            rate_limit_period=60
        )
        
    def get_station_data(self, 
                        station_id: str,
                        sensor_num: int,
                        duration_code: str = 'H',
                        start_date: datetime = None,
                        end_date: datetime = None) -> APIResponse:
        """
        Get data from CDEC station.
        
        Args:
            station_id: CDEC station ID
            sensor_num: Sensor number
            duration_code: Duration code (H=hourly, D=daily)
            start_date: Start date
            end_date: End date
            
        Returns:
            APIResponse with station data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
            
        params = {
            'Stations': station_id,
            'SensorNums': sensor_num,
            'dur_code': duration_code,
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        }
        
        response = self._make_request('', params)
        
        if response.success and response.data:
            response.data = self._standardize_cdec_data(response.data, station_id)
            
        return response
        
    def get_station_list(self, bbox: Optional[Tuple[float, float, float, float]] = None) -> APIResponse:
        """
        Get list of CDEC stations.
        
        Args:
            bbox: Bounding box filter
            
        Returns:
            APIResponse with station list
        """
        # This would require a different endpoint or manual filtering
        # For now, return a basic structure
        params = {}
        
        # CDEC doesn't have a direct stations API, so we'll need to
        # implement station discovery differently
        return APIResponse(
            success=True,
            data={'message': 'Station list endpoint not directly available'},
            source=self.__class__.__name__,
            timestamp=datetime.now()
        )
        
    def _standardize_cdec_data(self, raw_data: Dict, station_id: str) -> Dict:
        """Standardize CDEC data format."""
        return {
            'type': 'cdec_data',
            'source': 'CDEC',
            'station_id': station_id,
            'data': raw_data,
            'metadata': {
                'processed_at': datetime.now().isoformat()
            }
        }

class CaliforniaAPIManager:
    """Manager class for all California API clients."""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize API manager with optional API keys.
        
        Args:
            api_keys: Dictionary mapping service names to API keys
        """
        if api_keys is None:
            api_keys = {}
            
        self.api_keys = api_keys
        
        # Initialize clients
        self.calfire = CALFIREClient(api_keys.get('calfire'))
        self.noaa = NOAAClient(api_keys.get('noaa'))
        self.usgs = USGSClient(api_keys.get('usgs'))
        self.cdec = CDECClient(api_keys.get('cdec'))
        
        self.clients = {
            'calfire': self.calfire,
            'noaa': self.noaa,
            'usgs': self.usgs,
            'cdec': self.cdec
        }
        
        logger.info("CaliforniaAPIManager initialized with clients: " + 
                   ", ".join(self.clients.keys()))
        
    def get_comprehensive_data_for_location(self, 
                                          location_bounds: Tuple[float, float, float, float],
                                          location_name: str,
                                          start_date: datetime = None,
                                          end_date: datetime = None) -> Dict[str, APIResponse]:
        """
        Get comprehensive data for a location from all available sources.
        
        Args:
            location_bounds: Bounding box as (west, south, east, north)
            location_name: Name of the location
            start_date: Start date for time series data
            end_date: End date for time series data
            
        Returns:
            Dictionary of API responses by data type
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
            
        logger.info(f"Fetching comprehensive data for {location_name}")
        
        results = {}
        
        # Fire data from CAL FIRE
        try:
            results['fire_perimeters'] = self.calfire.get_fire_perimeters(
                bbox=location_bounds,
                year=datetime.now().year
            )
        except Exception as e:
            logger.error(f"Error fetching fire data: {e}")
            results['fire_perimeters'] = APIResponse(
                success=False, data=None, error=str(e), source='CALFIREClient'
            )
            
        # Tide data from NOAA (if coastal)
        west, south, east, north = location_bounds
        if west < -120:  # Rough coastal check
            try:
                # Get station metadata first
                stations_response = self.noaa.get_stations_metadata(bbox=location_bounds)
                results['tide_stations'] = stations_response
                
                # Get tide data for first station if available
                if stations_response.success and stations_response.data:
                    stations = stations_response.data.get('stations', [])
                    if stations:
                        station_id = stations[0].get('id')
                        results['tide_data'] = self.noaa.get_tide_data(
                            station_id=station_id,
                            start_date=start_date,
                            end_date=end_date
                        )
            except Exception as e:
                logger.error(f"Error fetching tide data: {e}")
                results['tide_data'] = APIResponse(
                    success=False, data=None, error=str(e), source='NOAAClient'
                )
                
        # Stream data from USGS
        try:
            sites_response = self.usgs.get_site_info(bbox=location_bounds)
            results['usgs_sites'] = sites_response
            
            # Get streamflow data for available sites
            if sites_response.success and sites_response.data:
                site_data = sites_response.data.get('value', {}).get('timeSeries', [])
                if site_data:
                    site_codes = [site.get('sourceInfo', {}).get('siteCode', [{}])[0].get('value') 
                                 for site in site_data[:5]]  # Limit to 5 sites
                    site_codes = [code for code in site_codes if code]
                    
                    if site_codes:
                        results['streamflow_data'] = self.usgs.get_streamflow_data(
                            site_codes=site_codes,
                            start_date=start_date,
                            end_date=end_date
                        )
        except Exception as e:
            logger.error(f"Error fetching USGS data: {e}")
            results['streamflow_data'] = APIResponse(
                success=False, data=None, error=str(e), source='USGSClient'
            )
            
        # Weather station data from CAL FIRE
        try:
            results['weather_stations'] = self.calfire.get_fire_weather_stations(
                bbox=location_bounds
            )
        except Exception as e:
            logger.error(f"Error fetching weather station data: {e}")
            results['weather_stations'] = APIResponse(
                success=False, data=None, error=str(e), source='CALFIREClient'
            )
            
        successful_requests = sum(1 for result in results.values() if result.success)
        total_requests = len(results)
        
        logger.info(f"Completed data fetch for {location_name}: "
                   f"{successful_requests}/{total_requests} successful")
        
        return results
        
    def validate_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate connections to all API services.
        
        Returns:
            Dictionary with validation results for each service
        """
        validation_results = {}
        
        for service_name, client in self.clients.items():
            try:
                # Simple connectivity test
                start_time = time.time()
                response = requests.head(client.base_url, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                validation_results[service_name] = {
                    'accessible': response.status_code < 400,
                    'response_time_ms': int(response_time),
                    'status_code': response.status_code,
                    'api_key_configured': client.api_key is not None,
                    'base_url': client.base_url,
                    'last_checked': datetime.now().isoformat()
                }
                
            except Exception as e:
                validation_results[service_name] = {
                    'accessible': False,
                    'error': str(e),
                    'api_key_configured': client.api_key is not None,
                    'base_url': client.base_url,
                    'last_checked': datetime.now().isoformat()
                }
                
        return validation_results 