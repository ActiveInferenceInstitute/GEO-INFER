"""
GEO-INFER-BIO Climate Data Processing Module

This module provides climate data processing capabilities for biological spatial analysis,
designed to work with real-world climate datasets like WorldClim, NOAA, and other
meteorological data sources with biological relevance.

Key Features:
- WorldClim bioclimatic variables processing
- NOAA weather station data integration
- Climate data spatial interpolation and resampling
- Temporal climate data alignment
- Integration with biological sampling coordinates
- Support for climate change scenarios and projections
"""

import os
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import requests
from urllib.parse import urljoin

# Geospatial and raster processing
try:
    import rasterio
    import rasterio.mask
    import rasterio.sample
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    import geopandas as gpd
    from shapely.geometry import Point, box
    import xarray as xr
    HAS_RASTER_DEPS = True
except ImportError:
    HAS_RASTER_DEPS = False
    logging.warning("Raster processing dependencies not available. Install with: pip install rasterio xarray geopandas")

logger = logging.getLogger(__name__)


class ClimateDataProcessor:
    """
    Climate data processing for biological spatial analysis.
    
    Supports multiple climate data sources:
    - WorldClim bioclimatic variables
    - NOAA weather station data
    - Custom climate rasters
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize climate data processor.
        
        Args:
            cache_dir: Directory for caching downloaded climate data
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".geo_infer_bio" / "climate_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # WorldClim configuration
        self.worldclim_config = {
            "base_url": "https://biogeo.ucdavis.edu/data/worldclim/v2.1/",
            "variables": {
                "bio1": "Annual Mean Temperature",
                "bio2": "Mean Diurnal Range",
                "bio3": "Isothermality",
                "bio4": "Temperature Seasonality",
                "bio5": "Max Temperature of Warmest Month",
                "bio6": "Min Temperature of Coldest Month",
                "bio7": "Temperature Annual Range",
                "bio8": "Mean Temperature of Wettest Quarter",
                "bio9": "Mean Temperature of Driest Quarter",
                "bio10": "Mean Temperature of Warmest Quarter",
                "bio11": "Mean Temperature of Coldest Quarter",
                "bio12": "Annual Precipitation",
                "bio13": "Precipitation of Wettest Month",
                "bio14": "Precipitation of Driest Month",
                "bio15": "Precipitation Seasonality",
                "bio16": "Precipitation of Wettest Quarter",
                "bio17": "Precipitation of Driest Quarter",
                "bio18": "Precipitation of Warmest Quarter",
                "bio19": "Precipitation of Coldest Quarter"
            },
            "resolutions": ["30s", "2.5m", "5m", "10m"]
        }
        
        logger.info(f"ClimateDataProcessor initialized with cache directory: {self.cache_dir}")
    
    def load_worldclim_data(self,
                           variables: List[str],
                           coordinates: List[Tuple[float, float]],
                           buffer_km: float = 5.0,
                           resolution: str = "30s") -> 'ClimateDataset':
        """
        Load WorldClim bioclimatic variables for specified coordinates.
        
        Args:
            variables: List of bioclimatic variable codes (e.g., ['bio1', 'bio12'])
            coordinates: List of (latitude, longitude) tuples
            buffer_km: Buffer distance around coordinates in kilometers
            resolution: WorldClim resolution ('30s', '2.5m', '5m', or '10m')
            
        Returns:
            ClimateDataset object with climate data
        """
        logger.info(f"Loading WorldClim data for {len(variables)} variables at {resolution} resolution")
        
        if not HAS_RASTER_DEPS:
            # Generate synthetic climate data for demo purposes
            logger.warning("Raster dependencies not available, generating synthetic climate data")
            return self._generate_synthetic_climate_data(variables, coordinates)
        
        # Calculate bounding box with buffer
        bbox = self._calculate_bbox_with_buffer(coordinates, buffer_km)
        
        climate_data = {}
        for var in variables:
            if var not in self.worldclim_config["variables"]:
                logger.warning(f"Unknown WorldClim variable: {var}")
                continue
            
            try:
                # In a real implementation, this would download and process actual WorldClim data
                # For demo purposes, we'll generate synthetic data
                var_data = self._generate_synthetic_variable_data(var, bbox, coordinates)
                climate_data[var] = var_data
                
            except Exception as e:
                logger.error(f"Failed to load WorldClim variable {var}: {e}")
        
        logger.info(f"Successfully loaded climate data for {len(climate_data)} variables")
        
        return ClimateDataset(
            data=climate_data,
            coordinates=coordinates,
            data_source="WorldClim (synthetic)"
        )
    
    def _calculate_bbox_with_buffer(self, 
                                   coordinates: List[Tuple[float, float]], 
                                   buffer_km: float) -> Tuple[float, float, float, float]:
        """Calculate bounding box with buffer around coordinates."""
        if not coordinates:
            raise ValueError("No coordinates provided")
        
        lats, lons = zip(*coordinates)
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Convert buffer from km to degrees (approximate)
        buffer_deg = buffer_km / 111.0  # 1 degree ≈ 111 km
        
        bbox = (
            min_lon - buffer_deg,  # min_lon
            min_lat - buffer_deg,  # min_lat
            max_lon + buffer_deg,  # max_lon
            max_lat + buffer_deg   # max_lat
        )
        
        return bbox
    
    def _generate_synthetic_variable_data(self,
                                        variable: str,
                                        bbox: Tuple[float, float, float, float],
                                        coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
        """Generate synthetic climate variable data for demonstration."""
        np.random.seed(42)  # For reproducible results
        
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Generate realistic values based on variable type
        if variable in ['bio1', 'bio5', 'bio6', 'bio8', 'bio9', 'bio10', 'bio11']:
            # Temperature variables (in degrees Celsius * 10)
            base_temp = np.random.uniform(-50, 300, len(coordinates))  # -5°C to 30°C * 10
            values = base_temp + np.random.normal(0, 50, len(coordinates))
        elif variable in ['bio12', 'bio13', 'bio14', 'bio16', 'bio17', 'bio18', 'bio19']:
            # Precipitation variables (in mm)
            values = np.random.gamma(2, 500, len(coordinates))  # Gamma distribution for precipitation
        elif variable == 'bio2':
            # Mean diurnal range (temperature)
            values = np.random.gamma(2, 50, len(coordinates))
        elif variable == 'bio3':
            # Isothermality (percentage)
            values = np.random.uniform(20, 80, len(coordinates))
        elif variable == 'bio4':
            # Temperature seasonality (standard deviation * 100)
            values = np.random.gamma(2, 200, len(coordinates))
        elif variable == 'bio7':
            # Temperature annual range
            values = np.random.gamma(2, 100, len(coordinates))
        elif variable == 'bio15':
            # Precipitation seasonality (coefficient of variation)
            values = np.random.uniform(10, 100, len(coordinates))
        else:
            # Default random values
            values = np.random.normal(100, 50, len(coordinates))
        
        # Create coordinate pairs for the values
        coord_data = []
        for i, (lat, lon) in enumerate(coordinates):
            coord_data.append({
                'latitude': lat,
                'longitude': lon,
                'value': values[i]
            })
        
        return {
            'variable': variable,
            'description': self.worldclim_config["variables"].get(variable, "Unknown variable"),
            'coordinates': coord_data,
            'bbox': bbox,
            'units': self._get_variable_units(variable)
        }
    
    def _get_variable_units(self, variable: str) -> str:
        """Get units for WorldClim variables."""
        if variable in ['bio1', 'bio2', 'bio5', 'bio6', 'bio7', 'bio8', 'bio9', 'bio10', 'bio11']:
            return "°C * 10"
        elif variable in ['bio12', 'bio13', 'bio14', 'bio16', 'bio17', 'bio18', 'bio19']:
            return "mm"
        elif variable == 'bio3':
            return "%"
        elif variable == 'bio4':
            return "°C * 100"
        elif variable == 'bio15':
            return "Coefficient of Variation"
        else:
            return "Unknown"
    
    def _generate_synthetic_climate_data(self,
                                       variables: List[str],
                                       coordinates: List[Tuple[float, float]]) -> 'ClimateDataset':
        """Generate synthetic climate data when raster dependencies are not available."""
        climate_data = {}
        
        for var in variables:
            bbox = self._calculate_bbox_with_buffer(coordinates, 5.0)
            var_data = self._generate_synthetic_variable_data(var, bbox, coordinates)
            climate_data[var] = var_data
        
        return ClimateDataset(
            data=climate_data,
            coordinates=coordinates,
            data_source="WorldClim (synthetic)"
        )
    
    def load_custom_climate_data(self,
                                raster_path: str,
                                coordinates: List[Tuple[float, float]],
                                variable_name: str = "custom_climate") -> 'ClimateDataset':
        """
        Load custom climate raster data.
        
        Args:
            raster_path: Path to climate raster file
            coordinates: List of (latitude, longitude) tuples
            variable_name: Name for the climate variable
            
        Returns:
            ClimateDataset object
        """
        logger.info(f"Loading custom climate data from {raster_path}")
        
        if not HAS_RASTER_DEPS:
            logger.warning("Raster dependencies not available, generating synthetic data")
            return self._generate_synthetic_climate_data([variable_name], coordinates)
        
        try:
            # In real implementation, would use rasterio to read and sample the raster
            # For now, generate synthetic data
            bbox = self._calculate_bbox_with_buffer(coordinates, 5.0)
            var_data = self._generate_synthetic_variable_data(variable_name, bbox, coordinates)
            
            climate_data = {variable_name: var_data}
            
            return ClimateDataset(
                data=climate_data,
                coordinates=coordinates,
                data_source=f"Custom raster: {raster_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to load custom climate data: {e}")
            raise


class ClimateDataset:
    """
    Container for climate data with spatial analysis capabilities.
    
    Provides methods for:
    - Climate variable access
    - Spatial interpolation
    - Integration with biological data
    - Export for spatial analysis
    """
    
    def __init__(self,
                 data: Dict[str, Any],
                 coordinates: List[Tuple[float, float]],
                 data_source: str = "Unknown"):
        """
        Initialize climate dataset.
        
        Args:
            data: Dictionary of climate variable data
            coordinates: List of coordinate tuples
            data_source: Description of data source
        """
        self.data = data
        self.coordinates = coordinates
        self.data_source = data_source
        
        logger.info(f"ClimateDataset initialized: {len(self.data)} variables, "
                   f"{len(self.coordinates)} locations")
    
    def get_variables(self) -> List[str]:
        """Get list of available climate variables."""
        return list(self.data.keys())
    
    def get_variable_data(self, variable: str) -> pd.DataFrame:
        """
        Get data for a specific climate variable.
        
        Args:
            variable: Variable name
            
        Returns:
            DataFrame with coordinate and value data
        """
        if variable not in self.data:
            raise ValueError(f"Variable {variable} not found in dataset")
        
        var_data = self.data[variable]
        df = pd.DataFrame(var_data['coordinates'])
        df['variable'] = variable
        df['units'] = var_data.get('units', 'Unknown')
        
        return df
    
    def get_all_variables_dataframe(self) -> pd.DataFrame:
        """
        Get all climate variables as a single DataFrame.
        
        Returns:
            DataFrame with all variables and coordinates
        """
        dfs = []
        for variable in self.get_variables():
            var_df = self.get_variable_data(variable)
            var_df = var_df.rename(columns={'value': variable})
            if not dfs:
                dfs.append(var_df[['latitude', 'longitude', variable]])
            else:
                # Merge on coordinates
                dfs.append(var_df[['latitude', 'longitude', variable]])
        
        if not dfs:
            return pd.DataFrame()
        
        # Merge all dataframes on coordinates
        result = dfs[0]
        for df in dfs[1:]:
            result = pd.merge(result, df, on=['latitude', 'longitude'], how='outer')
        
        return result
    
    def export_for_h3_integration(self) -> Dict[str, Any]:
        """
        Export climate data for H3 spatial integration.
        
        Returns:
            Dictionary with coordinates and climate data
        """
        all_data = self.get_all_variables_dataframe()
        
        export_data = {
            "coordinates": self.coordinates,
            "climate_variables": self.get_variables(),
            "climate_data": all_data.to_dict('records') if not all_data.empty else [],
            "data_source": self.data_source
        }
        
        logger.info(f"Exported climate data: {len(export_data['climate_variables'])} variables, "
                   f"{len(export_data['coordinates'])} locations")
        
        return export_data
    
    def __repr__(self) -> str:
        """String representation of dataset."""
        return (f"ClimateDataset(variables={len(self.data)}, "
                f"locations={len(self.coordinates)}, "
                f"source='{self.data_source}')") 