#!/usr/bin/env python3
"""
Specific API Clients for California Data Sources

This module implements specific API clients for California geospatial data sources,
extending the general BaseAPIManager from GEO-INFER-SPACE.
"""

import logging
from typing import Dict, Any, Optional
from geo_infer_space.core.api_clients import BaseAPIManager

logger = logging.getLogger(__name__)

class CALFIREClient(BaseAPIManager):
    """
    Client for CAL FIRE data access.
    """
    def __init__(self):
        super().__init__("https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/ArcGIS/rest/services/California_Fire_Perimeters/FeatureServer")
        self.incident_url = "https://www.fire.ca.gov/umbraco/api/IncidentApi/GetIncidents"

    def fetch_incidents(self) -> Any:
        """
        Fetch active fire incidents from CAL FIRE.
        
        Returns:
            JSON list of incidents
        """
        return self.fetch_data("", {}, base_url=self.incident_url)

    def fetch_perimeters(self, year: Optional[int] = None, county: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch fire perimeters data.
        
        Args:
            year: Optional year filter
            county: Optional county filter
            
        Returns:
            GeoJSON data
        """
        where = "1=1"
        if year:
            where += f" AND YEAR_ = {year}"
        if county:
            where += f" AND POOCounty = '{county}'"
            
        params = {
            "where": where,
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson"
        }
        return self.fetch_data("0/query", params)

class NOAAClient(BaseAPIManager):
    """
    Client for NOAA Tides and Currents data.
    """
    def __init__(self):
        super().__init__("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter")
        self.weather_url = "https://api.weather.gov/stations"

    def fetch_weather_observations(self, station_id: str) -> Dict[str, Any]:
        """
        Fetch latest weather observations for a station.
        
        Args:
            station_id: Weather station ID (e.g., KCEC)
            
        Returns:
            JSON data with weather properties
        """
        url = f"{self.weather_url}/{station_id}/observations/latest"
        return self.fetch_data("", {}, base_url=url)

    def fetch_tide_data(self, station: str, begin_date: str, end_date: str, product: str = "water_level") -> Dict[str, Any]:
        """
        Fetch tide gauge data.
        
        Args:
            station: Station ID
            begin_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            product: Data product (default: water_level)
            
        Returns:
            JSON data
        """
        params = {
            "station": station,
            "begin_date": begin_date,
            "end_date": end_date,
            "product": product,
            "datum": "MLLW",
            "time_zone": "lst",
            "units": "metric",
            "format": "json",
            "application": "GEO-INFER-PLACE"
        }
        return self.fetch_data("", params)

class USGSClient(BaseAPIManager):
    """
    Client for USGS water data.
    """
    def __init__(self):
        super().__init__("https://waterservices.usgs.gov/nwis/iv")

    def fetch_water_data(self, sites: str, start: str, end: str, parameter_cd: str = "00060,00065") -> Dict[str, Any]:
        """
        Fetch water data from USGS.
        
        Args:
            sites: Comma-separated site IDs
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            parameter_cd: Parameter codes (default: discharge and gage height)
            
        Returns:
            JSON data
        """
        params = {
            "format": "json",
            "sites": sites,
            "startDT": start,
            "endDT": end,
            "parameterCd": parameter_cd
        }
        return self.fetch_data("", params)

class USGSEarthquakeClient(BaseAPIManager):
    """
    Client for USGS Earthquake data.
    """
    def __init__(self):
        super().__init__("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary")
        
    def fetch_earthquakes(self, feed: str = "all_day.geojson") -> Dict[str, Any]:
        """
        Fetch earthquake data feed.
        
        Args:
            feed: Feed name (default: all_day.geojson)
            
        Returns:
            GeoJSON data
        """
        return self.fetch_data(f"/{feed}", {})

class CDECClient(BaseAPIManager):
    """
    Client for California Data Exchange Center.
    """
    def __init__(self):
        super().__init__("https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet")

    def fetch_sensor_data(self, stations: str, sensor_num: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch sensor data from CDEC.
        
        Args:
            stations: Comma-separated station IDs
            sensor_num: Sensor number
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            JSON data
        """
        params = {
            "Stations": stations,
            "SensorNums": sensor_num,
            "Start": start_date,
            "End": end_date
        }
        return self.fetch_data("", params)

class CaliforniaAPIManager:
    """
    Manager class that aggregates California-specific API clients.
    """
    def __init__(self):
        self.calfire = CALFIREClient()
        self.noaa = NOAAClient()
        self.usgs = USGSClient()
        self.usgs_eq = USGSEarthquakeClient()
        self.cdec = CDECClient()
        
        logger.info("California API Manager initialized with specific clients") 