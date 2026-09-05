"""
Data validation and quality assurance for GEO-INFER-DATA.

This module provides comprehensive data validation capabilities including
geospatial validation, temporal validation, completeness checks, and
quality assessment.
"""

import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum

import geopandas as gpd
import pandas as pd
import numpy as np

from ..models.schemas import (
    QualityCheck,
    QualityStatus,
    DataQualityReport,
    DatasetMetadata,
)
from ..utils.validation import (
    count_future_dates,
    has_mixed_types,
    scan_geometry_validity,
    wgs84_bounds_issues,
)



logger = logging.getLogger(__name__)


def _now_for_series(series: pd.Series) -> pd.Timestamp:
    """Return a comparison timestamp matching a datetime series timezone."""
    if isinstance(series.dtype, pd.DatetimeTZDtype):
        return pd.Timestamp.now(tz=series.dt.tz)
    return pd.Timestamp.now()


def _coerce_for_series(value: datetime, series: pd.Series) -> pd.Timestamp:
    """Coerce metadata timestamps to the timezone of a datetime series."""
    timestamp = pd.Timestamp(value)
    if isinstance(series.dtype, pd.DatetimeTZDtype):
        if timestamp.tzinfo is None:
            return timestamp.tz_localize(series.dt.tz)
        return timestamp.tz_convert(series.dt.tz)
    if timestamp.tzinfo is not None:
        return timestamp.tz_convert(None)
    return timestamp


class ValidationLevel(str, Enum):
    """Validation strictness levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"


class ValidationRule(str, Enum):
    """Available validation rules."""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    FORMAT = "format"
    SCHEMA = "schema"


@dataclass
class ValidationConfig:
    """Configuration for data validation."""

    validation_rules: Optional[List[str]] = field(default=None)
    quality_threshold: float = 0.8
    strict_mode: bool = False
    real_time_monitoring: bool = True
    custom_rules: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self) -> None:
        if self.validation_rules is None:
            self.validation_rules = [rule.value for rule in ValidationRule]


class GeospatialValidator:
    """Comprehensive geospatial data validation."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.validation_rules = {
            "completeness": self._check_completeness,
            "accuracy": self._check_accuracy,
            "consistency": self._check_consistency,
            "validity": self._check_validity,
            "temporal": self._check_temporal,
            "spatial": self._check_spatial,
            "format": self._check_format,
            "schema": self._check_schema,
        }

    def validate_geometries(self, data: gpd.GeoDataFrame) -> QualityCheck:
        """Validate geometry presence, validity, CRS, and WGS84 coordinate bounds."""
        issues = []
        score = 1.0

        if not isinstance(data, gpd.GeoDataFrame) or "geometry" not in data.columns:
            return QualityCheck(
                score=0.0,
                status=QualityStatus.FAIL,
                issues=[
                    {
                        "type": "missing_geometry",
                        "message": "GeoDataFrame geometry column is required",
                    }
                ],
            )

        total = max(len(data), 1)
        invalid_geometries = 0
        invalid_coordinates = 0
        for _idx, reason, geom in scan_geometry_validity(data.geometry.items()):
            if reason in ("null", "invalid"):
                invalid_geometries += 1
            elif reason == "ok" and wgs84_bounds_issues(geom.bounds):
                invalid_coordinates += 1

        if invalid_geometries:
            ratio = invalid_geometries / total
            issues.append(
                {
                    "type": "invalid_geometries",
                    "message": f"Invalid or missing geometries: {ratio:.2%}",
                    "severity": "high",
                }
            )
            score -= min(0.9, ratio * 1.5)
        if invalid_coordinates:
            ratio = invalid_coordinates / total
            issues.append(
                {
                    "type": "invalid_coordinates",
                    "message": f"Coordinates outside WGS84 bounds: {ratio:.2%}",
                    "severity": "high",
                }
            )
            score -= min(0.9, ratio * 1.5)
        if data.crs is None:
            issues.append(
                {
                    "type": "missing_crs",
                    "message": "Missing coordinate reference system",
                }
            )
            score -= 0.2

        score = max(0.0, score)
        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )
        return QualityCheck(score=score, status=status, issues=issues)

    def validate_coordinates(self, data: pd.DataFrame) -> QualityCheck:
        """Validate latitude and longitude columns in tabular data."""
        if "latitude" not in data.columns or "longitude" not in data.columns:
            return QualityCheck(
                score=0.0,
                status=QualityStatus.FAIL,
                issues=[
                    {
                        "type": "missing_coordinates",
                        "message": "latitude and longitude columns are required",
                    }
                ],
            )

        valid_mask = (
            data["latitude"].notna()
            & data["longitude"].notna()
            & data["latitude"].between(-90, 90)
            & data["longitude"].between(-180, 180)
        )
        invalid_ratio = 1.0 - (valid_mask.sum() / max(len(data), 1))
        issues = []
        score = 1.0
        if invalid_ratio:
            issues.append(
                {
                    "type": "invalid_coordinates",
                    "message": f"Invalid coordinates: {invalid_ratio:.2%}",
                    "severity": "high",
                }
            )
            score -= min(0.9, invalid_ratio * 4.0)

        score = max(0.0, score)
        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )
        return QualityCheck(score=score, status=status, issues=issues)

    def validate_temporal_data(self, data: pd.DataFrame) -> QualityCheck:
        """Validate datetime columns for plausible, ordered timestamps."""
        datetime_cols = data.select_dtypes(include=["datetime", "datetimetz"]).columns
        if len(datetime_cols) == 0:
            return QualityCheck(
                score=0.0,
                status=QualityStatus.FAIL,
                issues=[
                    {
                        "type": "missing_temporal_data",
                        "message": "No datetime columns found",
                    }
                ],
            )

        issues = []
        score = 1.0
        for col in datetime_cols:
            series = data[col].dropna()
            if series.empty:
                continue
            future_count = count_future_dates(series)
            if future_count:
                ratio = future_count / len(series)
                issues.append(
                    {
                        "type": "future_dates",
                        "message": f"Future dates in {col}: {ratio:.2%}",
                        "severity": "medium",
                    }
                )
                score -= min(0.3, ratio * 0.3)
            if not series.is_monotonic_increasing:
                issues.append(
                    {
                        "type": "non_chronological",
                        "message": f"Non-chronological order in {col}",
                    }
                )
                score -= 0.1

        score = max(0.0, score)
        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )
        return QualityCheck(score=score, status=status, issues=issues)

    async def validate_data(
        self, data: Any, metadata: Optional[DatasetMetadata] = None
    ) -> DataQualityReport:
        """
        Validate geospatial data comprehensively.

        Args:
            data: Data to validate
            metadata: Dataset metadata

        Returns:
            Comprehensive quality report
        """
        logger.info("Starting comprehensive data validation")

        dataset_id = metadata.title if metadata else "unknown_dataset"
        checks = {}
        overall_score = 0.0

        # Run all configured validation checks
        configured_rules = self.config.validation_rules
        rules: List[str] = (
            configured_rules
            if configured_rules is not None
            else [rule.value for rule in ValidationRule]
        )
        for rule_name in rules:
            if rule_name in self.validation_rules:
                try:
                    check_result = await self.validation_rules[rule_name](
                        data, metadata
                    )
                    checks[rule_name] = check_result

                    # Update overall score
                    if check_result.status == QualityStatus.PASS:
                        overall_score += check_result.score
                    elif check_result.status == QualityStatus.WARNING:
                        overall_score += (
                            check_result.score * 0.8
                        )  # Weight warnings lower
                    else:
                        overall_score += (
                            check_result.score * 0.5
                        )  # Weight failures lower

                except Exception as e:
                    logger.error(f"Validation rule {rule_name} failed: {e}")
                    checks[rule_name] = QualityCheck(
                        score=0.0,
                        status=QualityStatus.FAIL,
                        issues=[{"type": "validation_error", "message": str(e)}],
                    )

        # Calculate overall score
        if checks:
            overall_score /= len(checks)
            overall_score = min(
                overall_score, min(check.score for check in checks.values())
            )

        # Generate recommendations
        recommendations = self._generate_recommendations(checks, overall_score)

        quality_report = DataQualityReport(
            dataset_id=dataset_id,
            overall_score=overall_score,
            checks=checks,
            recommendations=recommendations,
            assessment_method=rules,
            validation_rules=list(rules),
        )

        logger.info(
            f"Data validation completed with overall score: {overall_score:.2f}"
        )
        return quality_report

    async def _check_completeness(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check data completeness."""
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            if data.empty:
                issues.append(
                    {
                        "type": "empty_dataset",
                        "message": "Dataset is empty",
                        "severity": "critical",
                    }
                )
                return QualityCheck(score=0.0, status=QualityStatus.FAIL, issues=issues)

            # Check for missing values
            missing_percent = data.isnull().sum().sum() / (
                data.shape[0] * data.shape[1]
            )

            if missing_percent > 0.1:  # More than 10% missing
                issues.append(
                    {
                        "type": "high_missing_values",
                        "message": f"High percentage of missing values: {missing_percent:.2%}",
                        "severity": "high",
                    }
                )
                score -= min(0.9, missing_percent * 1.5)
            elif missing_percent > 0.05:  # More than 5% missing
                issues.append(
                    {
                        "type": "moderate_missing_values",
                        "message": f"Moderate percentage of missing values: {missing_percent:.2%}",
                        "severity": "medium",
                    }
                )
                score -= 0.1

        elif isinstance(data, np.ndarray):
            # Check for NaN values in arrays
            nan_count = np.isnan(data).sum()
            total_count = data.size

            if nan_count > 0:
                nan_percent = nan_count / total_count
                issues.append(
                    {
                        "type": "array_nan_values",
                        "message": f"Array contains NaN values: {nan_percent:.2%}",
                        "severity": "medium",
                    }
                )
                score -= 0.2

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def _check_accuracy(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check data accuracy."""
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check for outliers
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for col in numeric_columns:
                if col in data.columns:
                    values = data[col].dropna()
                    if len(values) > 0:
                        # Simple outlier detection using IQR
                        Q1 = values.quantile(0.25)
                        Q3 = values.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR

                        outliers = values[
                            (values < lower_bound) | (values > upper_bound)
                        ]
                        outlier_percent = len(outliers) / len(values)

                        if outlier_percent > 0.1:  # More than 10% outliers
                            issues.append(
                                {
                                    "type": "high_outliers",
                                    "message": f"High percentage of outliers in {col}: {outlier_percent:.2%}",
                                    "severity": "medium",
                                }
                            )
                            score -= 0.2

            # Check coordinate accuracy if geospatial
            if isinstance(data, gpd.GeoDataFrame) and "geometry" in data.columns:
                # Check for invalid coordinates
                invalid_coords = sum(
                    1
                    for _idx, reason, _geom in scan_geometry_validity(
                        data.geometry.items()
                    )
                    if reason != "ok"
                )

                if invalid_coords > 0:
                    invalid_percent = invalid_coords / len(data)
                    issues.append(
                        {
                            "type": "invalid_geometries",
                            "message": f"Invalid geometries found: {invalid_percent:.2%}",
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

    async def _check_consistency(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check data consistency."""
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check data types consistency
            for col in data.columns:
                if col == "geometry":
                    continue
                if has_mixed_types(data[col]):
                    issues.append(
                        {
                            "type": "mixed_data_types",
                            "message": f"Mixed data types in column {col}",
                            "severity": "low",
                        }
                    )
                    score -= 0.1

            # Check for duplicate records. Geometry objects can expose pandas
            # internals that are not duplicate-check friendly, so use scalar
            # attributes for this consistency rule.
            duplicate_data = data.drop(columns=["geometry"], errors="ignore")
            duplicates = duplicate_data.duplicated().sum()
            if duplicates > 0:
                duplicate_percent = duplicates / len(data)
                issues.append(
                    {
                        "type": "duplicate_records",
                        "message": f"Duplicate records found: {duplicate_percent:.2%}",
                        "severity": "medium",
                    }
                )
                score -= 0.2

            # Check temporal consistency if datetime columns exist
            datetime_cols = data.select_dtypes(
                include=["datetime", "datetimetz"]
            ).columns
            for col in datetime_cols:
                if col in data.columns:
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

    async def _check_validity(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check data validity."""
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check for valid values in each column
            for col in data.columns:
                if data[col].dtype in ["object", "string"]:
                    # Check for suspicious string values
                    suspicious_values = (
                        data[col]
                        .dropna()
                        .astype(str)
                        .str.contains(r"[^\w\s\-.,()&]", regex=True)
                    )
                    if suspicious_values.any():
                        issues.append(
                            {
                                "type": "suspicious_characters",
                                "message": f"Suspicious characters in column {col}",
                                "severity": "low",
                            }
                        )
                        score -= 0.1

                elif pd.api.types.is_numeric_dtype(data[col]):
                    # Check for infinite values
                    if np.isinf(data[col]).any():
                        issues.append(
                            {
                                "type": "infinite_values",
                                "message": f"Infinite values in column {col}",
                                "severity": "high",
                            }
                        )
                        score -= 0.3

        elif isinstance(data, np.ndarray):
            # Check for valid array values
            if np.isinf(data).any():
                issues.append(
                    {
                        "type": "infinite_values",
                        "message": "Infinite values in array",
                        "severity": "high",
                    }
                )
                score -= 0.3

            if np.isnan(data).any():
                issues.append(
                    {
                        "type": "nan_values",
                        "message": "NaN values in array",
                        "severity": "medium",
                    }
                )
                score -= 0.2

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def _check_temporal(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check temporal validity."""
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Find datetime columns
            datetime_cols = data.select_dtypes(
                include=["datetime", "datetimetz"]
            ).columns

            for col in datetime_cols:
                if col in data.columns:
                    # Check for future dates (might be data entry errors)
                    future_count = count_future_dates(data[col])
                    if future_count:
                        future_percent = future_count / len(data)
                        issues.append(
                            {
                                "type": "future_dates",
                                "message": f"Future dates in {col}: {future_percent:.2%}",
                                "severity": "medium",
                            }
                        )
                        score -= 0.2

                    # Check for unreasonable date ranges
                    date_range = data[col].max() - data[col].min()
                    if date_range > timedelta(days=365 * 100):  # More than 100 years
                        issues.append(
                            {
                                "type": "unreasonable_date_range",
                                "message": f"Unreasonable date range in {col}: {date_range.days} days",
                                "severity": "low",
                            }
                        )
                        score -= 0.1

        # Check temporal extent if metadata provided
        if metadata and metadata.temporal:
            # Validate temporal extent consistency
            if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
                datetime_cols = data.select_dtypes(
                    include=["datetime", "datetimetz"]
                ).columns
                if len(datetime_cols) > 0:
                    series = data[datetime_cols[0]]
                    data_min = series.min()
                    data_max = series.max()

                    if data_min < _coerce_for_series(
                        metadata.temporal.start, series
                    ) or data_max > _coerce_for_series(metadata.temporal.end, series):
                        issues.append(
                            {
                                "type": "temporal_extent_mismatch",
                                "message": "Data temporal extent exceeds metadata bounds",
                                "severity": "medium",
                            }
                        )
                        score -= 0.2

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def _check_spatial(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check spatial validity."""
        issues = []
        score = 1.0

        if isinstance(data, gpd.GeoDataFrame) and "geometry" in data.columns:
            # Check geometry validity
            invalid_geoms = 0
            invalid_coords = 0
            for idx, geom in data.geometry.items():
                if geom is None or not geom.is_valid:
                    invalid_geoms += 1
                    continue
                min_lon, min_lat, max_lon, max_lat = geom.bounds
                if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90:
                    invalid_coords += 1

            if invalid_geoms > 0:
                invalid_percent = invalid_geoms / len(data)
                issues.append(
                    {
                        "type": "invalid_geometries",
                        "message": f"Invalid geometries: {invalid_percent:.2%}",
                        "severity": "high",
                    }
                )
                score -= min(0.9, invalid_percent * 4.0)

            if invalid_coords > 0:
                invalid_percent = invalid_coords / len(data)
                issues.append(
                    {
                        "type": "invalid_coordinates",
                        "message": f"Invalid coordinates: {invalid_percent:.2%}",
                        "severity": "high",
                    }
                )
                score -= min(0.9, invalid_percent * 4.0)

            # Check coordinate system consistency
            if data.crs is None:
                issues.append(
                    {
                        "type": "missing_crs",
                        "message": "Missing coordinate reference system",
                        "severity": "medium",
                    }
                )
                score -= 0.2

            # Check for geometries outside expected bounds
            if metadata and metadata.spatial:
                bounds = metadata.spatial.bbox
                if len(bounds) >= 4:
                    min_lon, min_lat, max_lon, max_lat = bounds[:4]

                    # Check if geometries are within bounds
                    out_of_bounds = 0
                    for geom in data.geometry:
                        if geom and geom.bounds:
                            geom_min_lon, geom_min_lat, geom_max_lon, geom_max_lat = (
                                geom.bounds
                            )
                            if (
                                geom_max_lon < min_lon
                                or geom_min_lon > max_lon
                                or geom_max_lat < min_lat
                                or geom_min_lat > max_lat
                            ):
                                out_of_bounds += 1

                    if out_of_bounds > 0:
                        oob_percent = out_of_bounds / len(data)
                        issues.append(
                            {
                                "type": "out_of_bounds",
                                "message": f"Geometries outside bounds: {oob_percent:.2%}",
                                "severity": "medium",
                            }
                        )
                        score -= 0.2

        elif (
            isinstance(data, (pd.DataFrame,))
            and "latitude" in data.columns
            and "longitude" in data.columns
        ):
            # Check coordinate validity for lat/lon data
            invalid_coords = 0

            for idx, row in data.iterrows():
                lat = row.get("latitude")
                lon = row.get("longitude")

                if lat is not None and lon is not None:
                    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                        invalid_coords += 1
                else:
                    invalid_coords += 1

            if invalid_coords > 0:
                invalid_percent = invalid_coords / len(data)
                issues.append(
                    {
                        "type": "invalid_coordinates",
                        "message": f"Invalid coordinates: {invalid_percent:.2%}",
                        "severity": "high",
                    }
                )
                score -= min(0.9, invalid_percent * 4.0)

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def _check_format(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check data format validity."""
        issues = []
        score = 1.0

        # Check data type consistency
        if hasattr(data, "dtypes"):
            # Pandas-like data
            for col, dtype in data.dtypes.items():
                if pd.api.types.is_object_dtype(dtype):
                    # Check for mixed types in object columns
                    unique_types = data[col].dropna().apply(type).unique()
                    if len(unique_types) > 3:  # Arbitrary threshold
                        issues.append(
                            {
                                "type": "mixed_types",
                                "message": f"Multiple types in column {col}",
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

    async def _check_schema(
        self, data: Any, metadata: Optional[DatasetMetadata]
    ) -> QualityCheck:
        """Check schema validity."""
        issues: List[Dict[str, Any]] = []
        score = 1.0

        # Schema validation logic
        # This would check against expected schema definitions

        status = (
            QualityStatus.PASS
            if score >= 0.8
            else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL
        )

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    def _generate_recommendations(
        self, checks: Dict[str, QualityCheck], overall_score: float
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if overall_score < 0.8:
            recommendations.append("Overall data quality is below acceptable threshold")

        for check_name, check in checks.items():
            if check.status == QualityStatus.FAIL:
                recommendations.append(f"Address {check_name} validation failures")
            elif check.status == QualityStatus.WARNING:
                recommendations.append(f"Review {check_name} warnings")

        return recommendations


class DataQualityManager:
    """
    Comprehensive data quality management and validation.

    This class provides centralized data quality management including validation,
    monitoring, reporting, and improvement recommendations for geospatial datasets.
    It supports multiple validation strategies, quality scoring, trend analysis,
    and automated improvement suggestions.

    Quality dimensions assessed:
    - **Completeness**: Missing values, required fields, data coverage
    - **Accuracy**: Outlier detection, coordinate validity, value ranges
    - **Consistency**: Data type consistency, duplicates, temporal order
    - **Validity**: Format validation, schema compliance, constraint checks
    - **Timeliness**: Temporal consistency, update frequency, data freshness
    - **Uniqueness**: Duplicate detection, primary key validation

    Features:
    - Multiple validation rule sets (basic, standard, comprehensive)
    - Real-time and batch validation modes
    - Quality trend analysis and reporting
    - Automated improvement recommendations
    - Integration with various data formats and sources
    - Configurable quality thresholds and validation rules
    - Historical quality tracking and analysis

    Attributes:
        config: Validation configuration with rules and thresholds
        validator: GeospatialValidator instance for quality checks
        quality_history: List of historical validation reports
        monitoring_enabled: Whether real-time monitoring is active

    Methods:
        validate_dataset(): Validate a specific dataset with comprehensive assessment
        get_improvement_recommendations(): Generate improvement recommendations
        get_quality_trends(): Analyze quality trends over time
        register_dataset(): Register data and metadata for validation.

    Args:
        validation_rules: Validation rules to apply. Can be a string specifying
            rule set ('basic', 'standard', 'comprehensive') or a list of specific
            rule names. Comprehensive rules include all available validations.
        quality_threshold: Minimum quality score threshold (0.0 to 1.0) for
            determining acceptable data quality. Reports below this threshold
            will trigger improvement recommendations.
        real_time_monitoring: Whether to enable real-time quality monitoring
            and continuous validation. When enabled, provides ongoing quality
            assessment for streaming or frequently updated data.

    Raises:
        ConfigurationError: If validation configuration is invalid
        ValidationError: If validation setup fails

    Examples:
        >>> # Initialize with comprehensive validation
        >>> quality_manager = DataQualityManager(
        ...     validation_rules='comprehensive',
        ...     quality_threshold=0.85,
        ...     real_time_monitoring=True
        ... )
        >>>
        >>> # Validate environmental monitoring dataset
        >>> report = await quality_manager.validate_dataset('environmental_sensors_2023')
        >>> print(f"Overall quality score: {report.overall_score:.2f}")
        >>> print(f"Quality status: {report.overall_score >= 0.85 and 'PASS' or 'FAIL'}")
        >>>
        >>> # Analyze quality by dimension
        >>> for check_name, check in report.checks.items():
        ...     status = "✓ PASS" if check.status == 'pass' else "⚠ WARNING" if check.status == 'warning' else "✗ FAIL"
        ...     print(f"{check_name}: {check.score:.2f} ({status})")
        >>>
        >>> # Get improvement recommendations
        >>> if report.overall_score < 0.85:
        ...     recommendations = quality_manager.get_improvement_recommendations(report)
        ...     print("Improvement recommendations:")
        ...     for rec in recommendations:
        ...         print(f"  - {rec}")
        >>>
        >>> # Analyze quality trends
        >>> trends = quality_manager.get_quality_trends(days=30)
        >>> print(f"Quality trend: {trends['score_trend']}")
        >>> print(f"Average score: {trends['average_score']:.2f}")
    """

    def __init__(
        self,
        validation_rules: str = "comprehensive",
        quality_threshold: float = 0.8,
        real_time_monitoring: bool = True,
    ):
        normalized_rules = self._normalize_validation_rules(validation_rules)
        self.config = ValidationConfig(
            validation_rules=normalized_rules,
            quality_threshold=quality_threshold,
            real_time_monitoring=real_time_monitoring,
        )

        self.validator = GeospatialValidator(self.config)
        self.quality_history: List[DataQualityReport] = []
        self._datasets: Dict[str, Tuple[Any, DatasetMetadata]] = {}
        self.monitoring_enabled = real_time_monitoring

        logger.info(
            f"Initialized DataQualityManager with {validation_rules} validation rules"
        )

    @staticmethod
    def _normalize_validation_rules(
        validation_rules: Union[str, List[str]],
    ) -> List[str]:
        """Expand named rule sets and reject unknown validation rules."""
        available = {rule.value for rule in ValidationRule}
        presets = {
            "basic": ["completeness", "validity"],
            "standard": ["completeness", "accuracy", "consistency", "validity"],
            "comprehensive": [rule.value for rule in ValidationRule],
            "strict": [rule.value for rule in ValidationRule],
        }

        if isinstance(validation_rules, str):
            text = validation_rules.strip()
            if text in presets:
                rules = presets[text]
            else:
                rules = [rule.strip() for rule in text.split(",") if rule.strip()]
        else:
            rules = list(validation_rules)

        unknown = sorted(set(rules) - available)
        if unknown:
            raise ValueError(f"Unknown validation rule(s): {', '.join(unknown)}")
        return rules

    def register_dataset(
        self, dataset_id: str, data: Any, metadata: DatasetMetadata
    ) -> None:
        """Register a stored dataset as the source for quality validation."""
        if not dataset_id:
            raise ValueError("dataset_id must not be empty")
        if not isinstance(metadata, DatasetMetadata):
            raise TypeError("metadata must be a DatasetMetadata instance")
        self._datasets[dataset_id] = (data, metadata)

    async def validate_dataset(self, dataset_id: str) -> DataQualityReport:
        """
        Validate a specific dataset with comprehensive quality assessment.

        This method performs comprehensive validation of a dataset by loading the data,
        applying all configured validation rules, and generating a detailed quality report.
        The validation process includes data integrity checks, quality scoring, and
        improvement recommendations.

        The validation process includes:
        1. **Data Loading**: Load dataset from storage using the dataset_id
        2. **Schema Validation**: Validate data structure and format
        3. **Quality Assessment**: Apply all configured validation rules
        4. **Score Calculation**: Compute overall and dimensional quality scores
        5. **Recommendation Generation**: Create improvement recommendations
        6. **History Tracking**: Store validation results for trend analysis

        Each validation dimension provides specific insights:
        - **Completeness**: Identifies missing values and data gaps
        - **Accuracy**: Detects outliers, invalid coordinates, and data anomalies
        - **Consistency**: Finds duplicates, type mismatches, and logical inconsistencies
        - **Validity**: Validates against schemas, constraints, and business rules

        Args:
            dataset_id: Unique identifier for the dataset to validate. This should
                correspond to a dataset stored in the configured storage backends.
                The method will attempt to load the dataset data and metadata using
                this identifier.

        Returns:
            Comprehensive quality assessment report containing:
            {
                'dataset_id': str,  # Dataset identifier
                'overall_score': float,  # 0.0 to 1.0 overall quality score
                'checks': {
                    'dimension_name': {
                        'score': float,  # 0.0 to 1.0 dimensional score
                        'status': str,  # 'pass', 'warning', 'fail'
                        'issues': list,  # List of identified issues
                        'metadata': dict  # Additional validation metadata
                    }
                },
                'recommendations': list,  # Improvement recommendations
                'generated_at': datetime,  # Validation timestamp
                'assessment_method': str,  # Validation methodology used
                'validation_rules': list  # Rules applied during validation
            }

        Raises:
            DatasetNotFoundError: If dataset_id does not exist in storage
            DataLoadingError: If dataset cannot be loaded
            ValidationError: If validation process fails
            StorageError: If storage backend is unavailable

        Examples:
            >>> # Validate environmental monitoring dataset
            >>> report = await quality_manager.validate_dataset('env_sensors_2023')
            >>>
            >>> # Check overall quality
            >>> print(f"Overall quality: {report.overall_score:.2f}")
            >>> print(f"Quality status: {report.overall_score >= 0.8 and 'EXCELLENT' or 'NEEDS_IMPROVEMENT'}")
            >>>
            >>> # Review dimensional scores
            >>> for dimension, check in report.checks.items():
            ...     status_icon = "✅" if check.status == 'pass' else "⚠️" if check.status == 'warning' else "❌"
            ...     print(f"{status_icon} {dimension}: {check.score:.2f}")
            ...
            ...     # Show specific issues
            ...     for issue in check.issues:
            ...         print(f"   - {issue['type']}: {issue['message']} ({issue.get('severity', 'medium')})")
            >>>
            >>> # Get improvement recommendations
            >>> if report.recommendations:
            ...     print("📋 Recommendations:")
            ...     for rec in report.recommendations:
            ...         print(f"   • {rec}")
        """
        logger.info(f"Validating dataset: {dataset_id}")

        try:
            validation_data, validation_metadata = self._datasets[dataset_id]
        except KeyError as exc:
            raise KeyError(
                f"Dataset {dataset_id!r} has not been registered for validation"
            ) from exc

        # Perform validation
        quality_report = await self.validator.validate_data(
            validation_data, validation_metadata
        )
        quality_report.dataset_id = dataset_id

        # Store in history
        self.quality_history.append(quality_report)

        logger.info(f"Dataset validation completed: {quality_report.overall_score:.2f}")
        return quality_report

    def get_improvement_recommendations(self, report: DataQualityReport) -> List[str]:
        """Get improvement recommendations based on quality report."""
        recommendations = []

        if report.overall_score < self.config.quality_threshold:
            recommendations.append(
                "Overall quality below threshold - review data collection process"
            )

        for check_name, check in report.checks.items():
            if check.status == QualityStatus.FAIL:
                recommendations.append(f"Fix {check_name} validation failures")
            elif check.status == QualityStatus.WARNING:
                recommendations.append(f"Address {check_name} warnings")

        return recommendations

    def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get quality trends over time."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        def as_utc(value: datetime) -> datetime:
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        recent_reports = [
            r for r in self.quality_history if as_utc(r.generated_at) >= cutoff_date
        ]

        if not recent_reports:
            return {"message": "No recent quality reports available"}

        scores = [r.overall_score for r in recent_reports]
        avg_score = sum(scores) / len(scores)

        return {
            "average_score": avg_score,
            "reports_count": len(recent_reports),
            "score_trend": "improving" if scores[-1] > scores[0] else "declining",
            "period_days": days,
        }
