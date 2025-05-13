"""
Validation functions for file paths, geospatial data, and other inputs.
"""

import os
from typing import List, Union

import geopandas as gpd
import numpy as np


def validate_file_path(
    file_path: str, 
    extensions: List[str] = None
) -> None:
    """
    Validate that a file path exists and has the correct extension.
    
    Args:
        file_path: Path to the file to validate
        extensions: List of valid file extensions (e.g., ['.geojson', '.json'])
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file has an invalid extension
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    if extensions:
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in extensions:
            raise ValueError(
                f"Invalid file extension: {ext}. Expected one of: {extensions}"
            )


def validate_geospatial_data(data: Union[gpd.GeoDataFrame, np.ndarray]) -> None:
    """
    Validate that the data is a valid GeoDataFrame or numpy array.
    
    Args:
        data: Data to validate
        
    Raises:
        ValueError: If the data is not a valid GeoDataFrame or numpy array
    """
    if isinstance(data, gpd.GeoDataFrame):
        # Check if GeoDataFrame has a geometry column
        if not data.geometry.any():
            raise ValueError("GeoDataFrame has no valid geometries")
            
        # Check if GeoDataFrame has a CRS
        if data.crs is None:
            raise ValueError("GeoDataFrame has no CRS (Coordinate Reference System)")
            
    elif isinstance(data, np.ndarray):
        # Check if numpy array has valid dimensions
        if data.ndim not in [2, 3]:
            raise ValueError(
                f"Invalid array dimensions: {data.ndim}. Expected 2D or 3D array."
            )
            
        # For 3D arrays, check if it has valid number of channels
        if data.ndim == 3 and data.shape[2] not in [1, 3, 4]:
            raise ValueError(
                f"Invalid number of channels: {data.shape[2]}. Expected 1, 3, or 4."
            )
            
    else:
        raise ValueError(
            f"Invalid data type: {type(data)}. Expected GeoDataFrame or numpy array."
        )


def validate_coordinates(lat: float, lon: float) -> None:
    """
    Validate geographic coordinates.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        
    Raises:
        ValueError: If coordinates are outside valid ranges
    """
    if not isinstance(lat, (int, float)):
        raise ValueError(f"Latitude must be a number, got {type(lat)}")
        
    if not isinstance(lon, (int, float)):
        raise ValueError(f"Longitude must be a number, got {type(lon)}")
        
    if not -90 <= lat <= 90:
        raise ValueError(f"Latitude {lat} is outside valid range -90 to 90 degrees")
        
    if not -180 <= lon <= 180:
        raise ValueError(f"Longitude {lon} is outside valid range -180 to 180 degrees")


def validate_bbox(bbox: tuple) -> None:
    """
    Validate a bounding box.
    
    Args:
        bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
        
    Raises:
        ValueError: If bbox is invalid
    """
    if not isinstance(bbox, tuple):
        raise ValueError(f"Bounding box must be a tuple, got {type(bbox)}")
        
    if len(bbox) != 4:
        raise ValueError(f"Bounding box must have 4 elements, got {len(bbox)}")
        
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Validate individual coordinates
    validate_coordinates(min_lat, min_lon)
    validate_coordinates(max_lat, max_lon)
    
    # Check that min is less than max
    if min_lon >= max_lon:
        raise ValueError(f"min_lon ({min_lon}) must be less than max_lon ({max_lon})")
        
    if min_lat >= max_lat:
        raise ValueError(f"min_lat ({min_lat}) must be less than max_lat ({max_lat})")


def validate_color(color: str) -> None:
    """
    Validate a color string.
    
    Args:
        color: Color string (hex, RGB, or named color)
        
    Raises:
        ValueError: If color is invalid
    """
    import re
    from matplotlib.colors import is_color_like
    
    if not isinstance(color, str):
        raise ValueError(f"Color must be a string, got {type(color)}")
        
    # Check if it's a valid hex color
    hex_pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    is_hex = bool(re.match(hex_pattern, color))
    
    # Check if it's a valid color using matplotlib
    is_valid = is_color_like(color)
    
    if not (is_hex or is_valid):
        raise ValueError(f"Invalid color: {color}") 