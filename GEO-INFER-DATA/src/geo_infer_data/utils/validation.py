"""
Data validation utilities for GEO-INFER-DATA.

This module provides comprehensive validation utilities for geospatial data
including format validation, schema validation, and data integrity checks.
"""

import logging
from typing import Dict, Union, Any

import geopandas as gpd
import pandas as pd
from shapely.validation import explain_validity

from ..models.schemas import QualityCheck, QualityStatus


logger = logging.getLogger(__name__)


def _now_for_series(series: pd.Series) -> pd.Timestamp:
    """Return a comparison timestamp matching a datetime series timezone."""
    if isinstance(series.dtype, pd.DatetimeTZDtype):
        return pd.Timestamp.now(tz=series.dt.tz)
    return pd.Timestamp.now()


class GeospatialValidator:
    """
    Comprehensive geospatial data validation.

    This class provides validation utilities for geospatial data including
    format validation, schema validation, geometric validation, and
    data integrity checks.

    Examples:
        >>> validator = GeospatialValidator()
        >>>
        >>> # Validate geospatial data
        >>> result = await validator.validate_data(geodataframe)
        >>> print(f"Validation score: {result.score:.2f}")
        >>>
        >>> # Validate specific aspect
        >>> geometry_check = validator.validate_geometries(geodataframe)
        >>> print(f"Geometry validation: {geometry_check.status}")
    """

    def __init__(self):
        self.validation_rules = {
            "geometry": self._validate_geometry,
            "coordinates": self._validate_coordinates,
            "attributes": self._validate_attributes,
            "metadata": self._validate_metadata,
            "temporal": self._validate_temporal,
            "spatial_reference": self._validate_spatial_reference,
        }

        logger.info("Initialized GeospatialValidator")

    async def validate_data(self, data: Any) -> QualityCheck:
        """
        Validate geospatial data comprehensively.

        Args:
            data: Data to validate

        Returns:
            Quality check result
        """
        logger.debug("Starting comprehensive data validation")

        issues = []
        score = 1.0

        # Run all validation checks
        for validation_name, validation_func in self.validation_rules.items():
            try:
                check_result = await validation_func(data)
                if not check_result["valid"]:
                    issues.extend(check_result["issues"])
                    score -= check_result["penalty"]
            except Exception as e:
                logger.error(f"Validation {validation_name} failed: {e}")
                issues.append(
                    {
                        "type": "validation_error",
                        "message": f"{validation_name} validation failed: {e}",
                        "severity": "high",
                    }
                )
                score -= 0.2

        # Determine status
        if score >= 0.8:
            status = QualityStatus.PASS
        elif score >= 0.5:
            status = QualityStatus.WARNING
        else:
            status = QualityStatus.FAIL

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def _validate_geometry(self, data: Any) -> Dict[str, Any]:
        """Validate geometry data."""
        issues = []
        penalty = 0.0

        if isinstance(data, gpd.GeoDataFrame) and "geometry" in data.columns:
            invalid_count = 0
            total_count = len(data)

            for idx, geom in data.geometry.items():
                if geom is None:
                    invalid_count += 1
                    issues.append(
                        {
                            "type": "null_geometry",
                            "message": f"Null geometry at index {idx}",
                            "severity": "high",
                        }
                    )
                elif not geom.is_valid:
                    invalid_count += 1
                    issues.append(
                        {
                            "type": "invalid_geometry",
                            "message": f"Invalid geometry at index {idx}: {explain_validity(geom)}",
                            "severity": "high",
                        }
                    )

            if invalid_count > 0:
                invalid_percent = invalid_count / total_count
                penalty = min(0.5, invalid_percent * 2)  # Up to 50% penalty

        return {"valid": penalty < 0.1, "issues": issues, "penalty": penalty}

    async def _validate_coordinates(self, data: Any) -> Dict[str, Any]:
        """Validate coordinate data."""
        issues = []
        penalty = 0.0

        if isinstance(data, pd.DataFrame):
            # Check for latitude/longitude columns
            lat_cols = [col for col in data.columns if "lat" in col.lower()]
            lon_cols = [col for col in data.columns if "lon" in col.lower()]

            for lat_col in lat_cols:
                invalid_coords = 0
                for value in data[lat_col].dropna():
                    if not (-90 <= value <= 90):
                        invalid_coords += 1

                if invalid_coords > 0:
                    issues.append(
                        {
                            "type": "invalid_latitude",
                            "message": f"Invalid latitude values in {lat_col}",
                            "severity": "high",
                        }
                    )
                    penalty += 0.2

            for lon_col in lon_cols:
                invalid_coords = 0
                for value in data[lon_col].dropna():
                    if not (-180 <= value <= 180):
                        invalid_coords += 1

                if invalid_coords > 0:
                    issues.append(
                        {
                            "type": "invalid_longitude",
                            "message": f"Invalid longitude values in {lon_col}",
                            "severity": "high",
                        }
                    )
                    penalty += 0.2

        elif isinstance(data, gpd.GeoDataFrame):
            # Check geometry bounds
            if not data.empty:
                bounds = data.total_bounds
                if len(bounds) == 4:
                    min_lon, min_lat, max_lon, max_lat = bounds

                    if not (-180 <= min_lon <= 180) or not (-180 <= max_lon <= 180):
                        issues.append(
                            {
                                "type": "invalid_longitude_bounds",
                                "message": "Invalid longitude bounds in geometry",
                                "severity": "high",
                            }
                        )
                        penalty += 0.2

                    if not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
                        issues.append(
                            {
                                "type": "invalid_latitude_bounds",
                                "message": "Invalid latitude bounds in geometry",
                                "severity": "high",
                            }
                        )
                        penalty += 0.2

        return {"valid": penalty < 0.1, "issues": issues, "penalty": penalty}

    async def _validate_attributes(self, data: Any) -> Dict[str, Any]:
        """Validate data attributes."""
        issues = []
        penalty = 0.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check for required columns
            if len(data.columns) == 0:
                issues.append(
                    {
                        "type": "no_columns",
                        "message": "Dataset has no columns",
                        "severity": "critical",
                    }
                )
                penalty += 0.5

            # Check for data types
            for col in data.columns:
                if data[col].dtype == "object":
                    # Check for mixed types
                    unique_types = data[col].dropna().apply(type).unique()
                    if len(unique_types) > 1:
                        issues.append(
                            {
                                "type": "mixed_types",
                                "message": f"Mixed data types in column {col}",
                                "severity": "low",
                            }
                        )
                        penalty += 0.1

        return {"valid": penalty < 0.1, "issues": issues, "penalty": penalty}

    async def _validate_metadata(self, data: Any) -> Dict[str, Any]:
        """Validate metadata consistency."""
        # Metadata validation logic
        return {"valid": True, "issues": [], "penalty": 0.0}

    async def _validate_temporal(self, data: Any) -> Dict[str, Any]:
        """Validate temporal data."""
        issues = []
        penalty = 0.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Find datetime columns
            datetime_cols = data.select_dtypes(
                include=["datetime", "datetimetz"]
            ).columns

            for col in datetime_cols:
                # Check for future dates
                future_dates = data[col] > _now_for_series(data[col])
                if future_dates.any():
                    future_count = future_dates.sum()
                    issues.append(
                        {
                            "type": "future_dates",
                            "message": f"Future dates detected in {col}: {future_count} records",
                            "severity": "medium",
                        }
                    )
                    penalty += 0.1

                # Check for unreasonable date ranges
                if not data[col].empty:
                    date_range = data[col].max() - data[col].min()
                    if date_range.days > 365 * 50:  # More than 50 years
                        issues.append(
                            {
                                "type": "unreasonable_date_range",
                                "message": f"Unreasonable date range in {col}: {date_range.days} days",
                                "severity": "low",
                            }
                        )
                        penalty += 0.1

        return {"valid": penalty < 0.1, "issues": issues, "penalty": penalty}

    async def _validate_spatial_reference(self, data: Any) -> Dict[str, Any]:
        """Validate spatial reference system."""
        issues = []
        penalty = 0.0

        if isinstance(data, gpd.GeoDataFrame):
            if data.crs is None:
                issues.append(
                    {
                        "type": "missing_crs",
                        "message": "Missing coordinate reference system",
                        "severity": "medium",
                    }
                )
                penalty += 0.2
            else:
                # Check CRS validity
                try:
                    crs_code = data.crs.to_epsg()
                    if crs_code is None:
                        issues.append(
                            {
                                "type": "invalid_crs",
                                "message": "Invalid coordinate reference system",
                                "severity": "medium",
                            }
                        )
                        penalty += 0.2
                except Exception as e:
                    issues.append(
                        {
                            "type": "crs_error",
                            "message": f"CRS validation error: {e}",
                            "severity": "medium",
                        }
                    )
                    penalty += 0.2

        return {"valid": penalty < 0.1, "issues": issues, "penalty": penalty}

    def validate_geometries(self, geodataframe: gpd.GeoDataFrame) -> QualityCheck:
        """
        Validate geometries in a GeoDataFrame.

        Args:
            geodataframe: GeoDataFrame to validate

        Returns:
            Geometry validation result
        """
        issues = []
        score = 1.0

        if "geometry" not in geodataframe.columns:
            return QualityCheck(
                score=0.0,
                status=QualityStatus.FAIL,
                issues=[
                    {"type": "missing_geometry", "message": "No geometry column found"}
                ],
            )

        # Check geometry validity
        invalid_count = 0
        for idx, geom in geodataframe.geometry.items():
            if geom is None:
                invalid_count += 1
                issues.append(
                    {
                        "type": "null_geometry",
                        "message": f"Null geometry at index {idx}",
                        "severity": "high",
                    }
                )
            elif not geom.is_valid:
                invalid_count += 1
                issues.append(
                    {
                        "type": "invalid_geometry",
                        "message": f"Invalid geometry at index {idx}",
                        "severity": "high",
                    }
                )

        if invalid_count > 0:
            invalid_percent = invalid_count / len(geodataframe)
            score -= min(0.8, invalid_percent * 2)

        # Check geometry types
        geom_types = geodataframe.geometry.type.unique()
        if len(geom_types) > 5:  # Too many geometry types
            issues.append(
                {
                    "type": "mixed_geometry_types",
                    "message": f"Too many geometry types: {list(geom_types)}",
                    "severity": "low",
                }
            )
            score -= 0.1

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    def validate_coordinates(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame]
    ) -> QualityCheck:
        """
        Validate coordinate data.

        Args:
            data: DataFrame or GeoDataFrame with coordinate data

        Returns:
            Coordinate validation result
        """
        issues = []
        score = 1.0

        if isinstance(data, gpd.GeoDataFrame):
            # Validate geometry bounds
            try:
                bounds = data.total_bounds
                if len(bounds) == 4:
                    min_lon, min_lat, max_lon, max_lat = bounds

                    if not (-180 <= min_lon <= 180) or not (-180 <= max_lon <= 180):
                        issues.append(
                            {
                                "type": "invalid_longitude_bounds",
                                "message": "Invalid longitude bounds",
                                "severity": "high",
                            }
                        )
                        score -= 0.3

                    if not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
                        issues.append(
                            {
                                "type": "invalid_latitude_bounds",
                                "message": "Invalid latitude bounds",
                                "severity": "high",
                            }
                        )
                        score -= 0.3

            except Exception as e:
                issues.append(
                    {
                        "type": "bounds_calculation_error",
                        "message": f"Error calculating bounds: {e}",
                        "severity": "high",
                    }
                )
                score -= 0.2

        elif isinstance(data, pd.DataFrame):
            # Check for lat/lon columns
            lat_cols = [col for col in data.columns if "lat" in col.lower()]
            lon_cols = [col for col in data.columns if "lon" in col.lower()]

            for lat_col in lat_cols:
                invalid_count = 0
                for value in data[lat_col].dropna():
                    if not (-90 <= value <= 90):
                        invalid_count += 1

                if invalid_count > 0:
                    invalid_percent = invalid_count / len(data)
                    issues.append(
                        {
                            "type": "invalid_latitude",
                            "message": f"Invalid latitude values in {lat_col}: {invalid_percent:.2%}",
                            "severity": "high",
                        }
                    )
                    score -= 0.3

            for lon_col in lon_cols:
                invalid_count = 0
                for value in data[lon_col].dropna():
                    if not (-180 <= value <= 180):
                        invalid_count += 1

                if invalid_count > 0:
                    invalid_percent = invalid_count / len(data)
                    issues.append(
                        {
                            "type": "invalid_longitude",
                            "message": f"Invalid longitude values in {lon_col}: {invalid_percent:.2%}",
                            "severity": "high",
                        }
                    )
                    score -= 0.3

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    def validate_temporal_data(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame]
    ) -> QualityCheck:
        """
        Validate temporal data.

        Args:
            data: DataFrame or GeoDataFrame with temporal data

        Returns:
            Temporal validation result
        """
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Find datetime columns
            datetime_cols = data.select_dtypes(
                include=["datetime", "datetimetz"]
            ).columns

            for col in datetime_cols:
                # Check for future dates
                future_dates = data[col] > _now_for_series(data[col])
                if future_dates.any():
                    future_count = future_dates.sum()
                    future_percent = future_count / len(data)

                    issues.append(
                        {
                            "type": "future_dates",
                            "message": f"Future dates in {col}: {future_percent:.2%}",
                            "severity": "medium",
                        }
                    )
                    score -= 0.2

                # Check for chronological order
                if not data[col].is_monotonic_increasing:
                    issues.append(
                        {
                            "type": "non_chronological",
                            "message": f"Non-chronological order in {col}",
                            "severity": "low",
                        }
                    )
                    score -= 0.1

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)
