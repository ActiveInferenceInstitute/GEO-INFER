"""
Utility functions for geospatial security operations.

This module provides helper functions for common security tasks.
"""

import os
import logging
import hashlib
import uuid
import json
import base64
import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import re
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon
import h3
from cryptography.fernet import Fernet
import numpy as np


logger = logging.getLogger(__name__)


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Length of the token in bytes
        
    Returns:
        Secure random token as a hex string
    """
    return os.urandom(length).hex()


def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, bytes]:
    """
    Hash a password securely.
    
    Args:
        password: Password to hash
        salt: Optional salt for the hash (if None, a new one will be generated)
        
    Returns:
        Tuple of (password_hash, salt)
    """
    if salt is None:
        salt = os.urandom(16)
        
    # Create hash with salt
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100000  # Number of iterations
    )
    
    # Convert to hex string
    password_hash = hash_obj.hex()
    
    return password_hash, salt


def verify_password(password: str, stored_hash: str, salt: bytes) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        password: Password to verify
        stored_hash: Previously stored password hash
        salt: Salt used for the hash
        
    Returns:
        True if the password is correct, False otherwise
    """
    # Hash the provided password with the same salt
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100000  # Same number of iterations
    )
    
    # Check if hashes match
    return hash_obj.hex() == stored_hash


def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        API key
    """
    # Generate a UUID and remove hyphens
    uid = str(uuid.uuid4()).replace('-', '')
    
    # Add a prefix for identification
    return f"geo-{uid}"


def sanitize_geospatial_input(input_str: str) -> str:
    """
    Sanitize user input for geospatial operations to prevent injection attacks.
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        Sanitized string
    """
    # Remove any SQL injection attempts
    sql_patterns = [
        r'--',
        r';.*',
        r'/\*.*\*/',
        r'UNION\s+ALL',
        r'SELECT\s+.*\s+FROM',
        r'INSERT\s+INTO',
        r'UPDATE\s+.*\s+SET',
        r'DELETE\s+FROM',
        r'DROP\s+TABLE',
        r'ALTER\s+TABLE',
        r'CREATE\s+TABLE',
        r'EXEC\s+',
        r'EXECUTE\s+'
    ]
    
    sanitized = input_str
    for pattern in sql_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Remove any potential script injection
    script_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'onload=',
        r'onerror=',
        r'onclick=',
        r'onmouseover='
    ]
    
    for pattern in script_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def validate_wgs84_coordinates(lat: float, lon: float) -> bool:
    """
    Validate that coordinates are within WGS84 bounds.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def secure_h3_index(lat: float, lon: float, resolution: int) -> str:
    """
    Generate H3 index with validation.
    
    Args:
        lat: Latitude
        lon: Longitude
        resolution: H3 resolution (0-15)
        
    Returns:
        H3 index
    """
    # Validate inputs
    if not validate_wgs84_coordinates(lat, lon):
        raise ValueError("Invalid coordinates")
        
    if not (0 <= resolution <= 15):
        raise ValueError("Invalid H3 resolution")
        
    # Generate H3 index
    h3_index = h3.geo_to_h3(lat, lon, resolution)
    
    return h3_index


def check_pii_columns(df: pd.DataFrame) -> List[str]:
    """
    Check for column names that may contain personally identifiable information.
    
    Args:
        df: DataFrame to check
        
    Returns:
        List of column names that may contain PII
    """
    pii_patterns = [
        r'name',
        r'address',
        r'email',
        r'phone',
        r'ssn',
        r'social.*security',
        r'birth.*date',
        r'dob',
        r'passport',
        r'license',
        r'id.*number',
        r'password',
        r'username',
        r'ip.*address'
    ]
    
    pii_columns = []
    
    for col in df.columns:
        col_lower = col.lower()
        for pattern in pii_patterns:
            if re.search(pattern, col_lower):
                pii_columns.append(col)
                break
                
    return pii_columns


def redact_text(text: str, patterns: Optional[List[str]] = None) -> str:
    """
    Redact sensitive information from text.
    
    Args:
        text: Text to redact
        patterns: Regular expression patterns to match (if None, default patterns will be used)
        
    Returns:
        Redacted text
    """
    if patterns is None:
        patterns = [
            # Email pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            # Phone number patterns (various formats)
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}\b',
            # Credit card pattern
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            # SSN pattern
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            # IP address pattern
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ]
    
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, '[REDACTED]', redacted)
        
    return redacted


def encrypt_sensitive_column(
    df: pd.DataFrame, 
    column: str, 
    key: Optional[bytes] = None
) -> Tuple[pd.DataFrame, bytes]:
    """
    Encrypt a sensitive column in a DataFrame.
    
    Args:
        df: DataFrame with column to encrypt
        column: Name of the column to encrypt
        key: Encryption key (if None, a new one will be generated)
        
    Returns:
        Tuple of (DataFrame with encrypted column, encryption key)
    """
    if column not in df.columns:
        raise ValueError(f"Column {column} not found in DataFrame")
        
    # Generate or use provided key
    if key is None:
        key = Fernet.generate_key()
        
    cipher = Fernet(key)
    
    # Create a copy of the DataFrame
    result = df.copy()
    
    # Encrypt the column
    result[column] = result[column].apply(
        lambda x: base64.urlsafe_b64encode(cipher.encrypt(str(x).encode())).decode() 
        if pd.notna(x) else None
    )
    
    # Add a suffix to indicate the column is encrypted
    result = result.rename(columns={column: f"{column}_encrypted"})
    
    return result, key


def decrypt_sensitive_column(
    df: pd.DataFrame, 
    column: str, 
    key: bytes
) -> pd.DataFrame:
    """
    Decrypt an encrypted column in a DataFrame.
    
    Args:
        df: DataFrame with encrypted column
        column: Name of the encrypted column
        key: Encryption key
        
    Returns:
        DataFrame with decrypted column
    """
    if column not in df.columns:
        raise ValueError(f"Column {column} not found in DataFrame")
        
    cipher = Fernet(key)
    
    # Create a copy of the DataFrame
    result = df.copy()
    
    # Decrypt the column
    result[column] = result[column].apply(
        lambda x: cipher.decrypt(base64.urlsafe_b64decode(x)).decode() 
        if pd.notna(x) else None
    )
    
    # Remove the _encrypted suffix if present
    if column.endswith('_encrypted'):
        original_name = column[:-10]
        result = result.rename(columns={column: original_name})
    
    return result


def audit_log(
    action: str,
    user_id: str,
    resource: str,
    status: str,
    details: Optional[str] = None,
    log_file: Optional[str] = None
) -> Dict:
    """
    Create a security audit log entry.
    
    Args:
        action: Action performed
        user_id: User ID
        resource: Resource affected
        status: Status of the action
        details: Additional details
        log_file: Optional path to log file
        
    Returns:
        Log entry as a dictionary
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "status": status,
        "details": details,
        "client_ip": "N/A"  # In a real application, get from request
    }
    
    # Log the entry
    logger.info(f"Security: {action} on {resource} by {user_id}: {status}")
    
    # Write to log file if specified
    if log_file:
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to audit log file: {str(e)}")
    
    return log_entry


def validate_spatial_bounds(
    gdf: gpd.GeoDataFrame, 
    bounds: Optional[Dict[str, float]] = None,
    geometry_col: str = "geometry"
) -> bool:
    """
    Validate that geometries are within specified bounds.
    
    Args:
        gdf: GeoDataFrame to validate
        bounds: Dictionary with min_lat, max_lat, min_lon, max_lon (if None, WGS84 bounds are used)
        geometry_col: Name of the geometry column
        
    Returns:
        True if all geometries are within bounds, False otherwise
    """
    if bounds is None:
        bounds = {
            "min_lat": -90.0,
            "max_lat": 90.0,
            "min_lon": -180.0,
            "max_lon": 180.0
        }
    
    # Extract bounds
    min_lat = bounds["min_lat"]
    max_lat = bounds["max_lat"]
    min_lon = bounds["min_lon"]
    max_lon = bounds["max_lon"]
    
    # Create a bounding box
    from shapely.geometry import box
    bbox = box(min_lon, min_lat, max_lon, max_lat)
    
    # Check if all geometries are within the box
    return all(geom.within(bbox) for geom in gdf[geometry_col])


def detect_outliers(
    gdf: gpd.GeoDataFrame, 
    method: str = "iqr",
    z_threshold: float = 3.0,
    iqr_factor: float = 1.5,
    geometry_col: str = "geometry"
) -> gpd.GeoDataFrame:
    """
    Detect outliers in geospatial data.
    
    Args:
        gdf: GeoDataFrame to analyze
        method: Detection method ('iqr' or 'zscore')
        z_threshold: Z-score threshold (only used if method is 'zscore')
        iqr_factor: IQR factor (only used if method is 'iqr')
        geometry_col: Name of the geometry column
        
    Returns:
        GeoDataFrame with outlier flag
    """
    # Extract points
    points = []
    
    for geom in gdf[geometry_col]:
        if isinstance(geom, Point):
            points.append((geom.x, geom.y))
        else:
            # For non-point geometries, use centroid
            centroid = geom.centroid
            points.append((centroid.x, centroid.y))
    
    # Convert to DataFrame for analysis
    coords_df = pd.DataFrame(points, columns=['lon', 'lat'])
    
    # Add outlier flag
    result = gdf.copy()
    result['is_outlier'] = False
    
    if method == 'zscore':
        # Z-score method
        from scipy import stats
        z_scores = stats.zscore(coords_df)
        abs_z_scores = np.abs(z_scores)
        outliers = (abs_z_scores > z_threshold).any(axis=1)
        result['is_outlier'] = outliers
        
    elif method == 'iqr':
        # IQR method
        for col in ['lat', 'lon']:
            q1 = coords_df[col].quantile(0.25)
            q3 = coords_df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - iqr_factor * iqr
            upper_bound = q3 + iqr_factor * iqr
            outlier_mask = (coords_df[col] < lower_bound) | (coords_df[col] > upper_bound)
            result.loc[outlier_mask, 'is_outlier'] = True
    
    return result 