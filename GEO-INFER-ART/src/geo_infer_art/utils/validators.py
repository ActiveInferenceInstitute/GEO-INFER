"""
Validation functions for file paths, geospatial data, and other inputs.
"""

import os
from typing import List, Union, Tuple

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


def validate_style_name(style_name: str, valid_styles: List[str]) -> None:
    """
    Validate a style name against a list of valid styles.

    Args:
        style_name: Style name to validate
        valid_styles: List of valid style names

    Raises:
        ValueError: If style name is not in the valid list
    """
    if style_name not in valid_styles:
        raise ValueError(
            f"Invalid style name: {style_name}. Valid styles: {', '.join(valid_styles)}"
        )


def validate_numeric_range(value: float, min_val: float, max_val: float, name: str = "value") -> None:
    """
    Validate that a numeric value is within a specified range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Name of the value for error messages

    Raises:
        ValueError: If value is outside the valid range
        TypeError: If value is not numeric
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value)}")

    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}, got {value}")


def validate_image_array(image_array: np.ndarray) -> None:
    """
    Validate a numpy array representing an image.

    Args:
        image_array: Image array to validate

    Raises:
        ValueError: If array is not a valid image format
    """
    if not isinstance(image_array, np.ndarray):
        raise ValueError(f"Image must be a numpy array, got {type(image_array)}")

    if image_array.ndim not in [2, 3]:
        raise ValueError(f"Image must be 2D or 3D array, got {image_array.ndim}D")

    if image_array.ndim == 3 and image_array.shape[2] not in [1, 3, 4]:
        raise ValueError(
            f"3D image must have 1, 3, or 4 channels, got {image_array.shape[2]}"
        )

    # Check for reasonable size limits
    total_pixels = image_array.size
    if total_pixels > 100_000_000:  # 100 megapixels
        raise ValueError(f"Image too large: {total_pixels} pixels (max 100M)")


def validate_resolution(resolution: Tuple[int, int]) -> None:
    """
    Validate image resolution.

    Args:
        resolution: Resolution as (width, height)

    Raises:
        ValueError: If resolution is invalid
    """
    if not isinstance(resolution, (tuple, list)) or len(resolution) != 2:
        raise ValueError("Resolution must be a tuple or list of (width, height)")

    width, height = resolution

    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("Resolution width and height must be integers")

    if width <= 0 or height <= 0:
        raise ValueError("Resolution width and height must be positive")

    if width > 10000 or height > 10000:
        raise ValueError("Resolution too high (max 10000x10000)")


def validate_file_format(file_path: str, valid_formats: List[str]) -> None:
    """
    Validate file format against a list of valid formats.

    Args:
        file_path: Path to the file
        valid_formats: List of valid file extensions (e.g., ['.png', '.jpg'])

    Raises:
        ValueError: If file format is not supported
    """
    _, ext = os.path.splitext(file_path)

    if ext.lower() not in valid_formats:
        raise ValueError(
            f"Unsupported file format: {ext}. Valid formats: {', '.join(valid_formats)}"
        ) 