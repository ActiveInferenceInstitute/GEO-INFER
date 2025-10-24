"""
Validation rules for GEO-INFER-DATA.

This module provides comprehensive validation rules for geospatial data
quality assessment including completeness, accuracy, consistency, and validity checks.
"""

import logging
from typing import Dict, List, Optional, Union, Any
import asyncio

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, LineString

from ..models.schemas import QualityCheck, QualityStatus, DatasetMetadata
from .engine import ValidationRule


logger = logging.getLogger(__name__)


class QualityRules:
    """
    Predefined validation rules for data quality assessment.

    This class provides comprehensive validation rules for geospatial data
    including completeness, accuracy, consistency, and validity checks.

    Examples:
        >>> rules = QualityRules()
        >>>
        >>> # Assess data completeness
        >>> completeness_score = rules.assess_completeness(data)
        >>>
        >>> # Validate coordinates
        >>> coord_check = rules.validate_coordinates(data)
        >>>
        >>> # Check data consistency
        >>> consistency_check = rules.check_consistency(data)
    """

    def __init__(self):
        logger.info("Initialized QualityRules")

    async def assess_completeness(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata] = None,
        parameters: Dict[str, Any] = None
    ) -> QualityCheck:
        """
        Assess data completeness.

        Args:
            data: Data to assess
            metadata: Dataset metadata
            parameters: Assessment parameters

        Returns:
            Completeness quality check
        """
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check for missing values
            total_cells = data.shape[0] * data.shape[1]
            missing_cells = data.isnull().sum().sum()
            missing_percent = missing_cells / total_cells if total_cells > 0 else 0

            if missing_percent > 0.1:  # More than 10% missing
                issues.append({
                    'type': 'high_missing_values',
                    'message': f'High percentage of missing values: {missing_percent:.2%}',
                    'severity': 'high'
                })
                score -= 0.3
            elif missing_percent > 0.05:  # More than 5% missing
                issues.append({
                    'type': 'moderate_missing_values',
                    'message': f'Moderate percentage of missing values: {missing_percent:.2%}',
                    'severity': 'medium'
                })
                score -= 0.1

            # Check for empty records
            if data.empty:
                issues.append({
                    'type': 'empty_dataset',
                    'message': 'Dataset is empty',
                    'severity': 'critical'
                })
                score = 0.0

            # Check required columns if metadata provided
            if metadata and hasattr(metadata, 'required_fields'):
                missing_columns = []
                for field in metadata.required_fields:
                    if field not in data.columns:
                        missing_columns.append(field)

                if missing_columns:
                    issues.append({
                        'type': 'missing_required_columns',
                        'message': f'Missing required columns: {missing_columns}',
                        'severity': 'high'
                    })
                    score -= 0.2

        status = QualityStatus.PASS if score >= 0.8 else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def assess_accuracy(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata] = None,
        parameters: Dict[str, Any] = None
    ) -> QualityCheck:
        """
        Assess data accuracy.

        Args:
            data: Data to assess
            metadata: Dataset metadata
            parameters: Assessment parameters

        Returns:
            Accuracy quality check
        """
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check for outliers in numeric columns
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

                        outliers = values[(values < lower_bound) | (values > upper_bound)]
                        outlier_percent = len(outliers) / len(values)

                        if outlier_percent > 0.1:  # More than 10% outliers
                            issues.append({
                                'type': 'high_outliers',
                                'message': f'High percentage of outliers in {col}: {outlier_percent:.2%}',
                                'severity': 'medium'
                            })
                            score -= 0.2

            # Check coordinate accuracy if geospatial
            if isinstance(data, gpd.GeoDataFrame) and 'geometry' in data.columns:
                # Check for invalid coordinates
                invalid_coords = 0
                total_coords = 0

                for geom in data.geometry:
                    total_coords += 1
                    if geom is None or not geom.is_valid:
                        invalid_coords += 1
                    elif hasattr(geom, 'bounds'):
                        # Check coordinate ranges
                        bounds = geom.bounds
                        if len(bounds) >= 4:
                            min_lon, min_lat, max_lon, max_lat = bounds
                            if not (-180 <= min_lon <= 180) or not (-180 <= max_lon <= 180):
                                invalid_coords += 1
                            elif not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
                                invalid_coords += 1

                if total_coords > 0:
                    invalid_percent = invalid_coords / total_coords
                    if invalid_percent > 0:
                        issues.append({
                            'type': 'invalid_geometries',
                            'message': f'Invalid geometries found: {invalid_percent:.2%}',
                            'severity': 'high'
                        })
                        score -= 0.3

            # Check data types consistency
            for col in data.columns:
                if data[col].dtype in ['object', 'string']:
                    # Check for suspicious values
                    suspicious_values = data[col].dropna().astype(str).str.contains(r'[^\w\s\-.,()&]', regex=True)
                    if suspicious_values.any():
                        suspicious_count = suspicious_values.sum()
                        suspicious_percent = suspicious_count / len(data)
                        issues.append({
                            'type': 'suspicious_characters',
                            'message': f'Suspicious characters in {col}: {suspicious_percent:.2%}',
                            'severity': 'low'
                        })
                        score -= 0.1

        status = QualityStatus.PASS if score >= 0.8 else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def check_consistency(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata] = None,
        parameters: Dict[str, Any] = None
    ) -> QualityCheck:
        """
        Check data consistency.

        Args:
            data: Data to check
            metadata: Dataset metadata
            parameters: Check parameters

        Returns:
            Consistency quality check
        """
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check for duplicate records
            duplicates = data.duplicated().sum()
            if duplicates > 0:
                duplicate_percent = duplicates / len(data)
                issues.append({
                    'type': 'duplicate_records',
                    'message': f'Duplicate records found: {duplicate_percent:.2%}',
                    'severity': 'medium'
                })
                score -= 0.2

            # Check data types consistency
            for col in data.columns:
                unique_types = data[col].dropna().apply(type).unique()
                if len(unique_types) > 1:
                    issues.append({
                        'type': 'mixed_data_types',
                        'message': f'Mixed data types in column {col}',
                        'severity': 'low'
                    })
                    score -= 0.1

            # Check temporal consistency if datetime columns exist
            datetime_cols = data.select_dtypes(include=['datetime']).columns
            for col in datetime_cols:
                if col in data.columns:
                    # Check for chronological order
                    if not data[col].is_monotonic_increasing:
                        issues.append({
                            'type': 'non_chronological',
                            'message': f'Non-chronological order in {col}',
                            'severity': 'low'
                        })
                        score -= 0.1

                    # Check for future dates (might be data entry errors)
                    future_dates = data[col] > datetime.now()
                    if future_dates.any():
                        future_percent = future_dates.sum() / len(data)
                        issues.append({
                            'type': 'future_dates',
                            'message': f'Future dates in {col}: {future_percent:.2%}',
                            'severity': 'medium'
                        })
                        score -= 0.2

        status = QualityStatus.PASS if score >= 0.8 else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def validate_coordinates(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata] = None,
        parameters: Dict[str, Any] = None
    ) -> QualityCheck:
        """
        Validate coordinate data.

        Args:
            data: Data to validate
            metadata: Dataset metadata
            parameters: Validation parameters

        Returns:
            Coordinate validation check
        """
        issues = []
        score = 1.0

        if isinstance(data, gpd.GeoDataFrame):
            # Validate geometry coordinates
            if 'geometry' in data.columns:
                invalid_geoms = 0
                total_geoms = len(data)

                for idx, geom in data.geometry.items():
                    if geom is None:
                        invalid_geoms += 1
                    elif not geom.is_valid:
                        invalid_geoms += 1
                    elif hasattr(geom, 'bounds'):
                        # Check coordinate bounds
                        bounds = geom.bounds
                        if len(bounds) >= 4:
                            min_lon, min_lat, max_lon, max_lat = bounds
                            if not (-180 <= min_lon <= 180) or not (-180 <= max_lon <= 180):
                                invalid_geoms += 1
                            elif not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
                                invalid_geoms += 1

                if total_geoms > 0:
                    invalid_percent = invalid_geoms / total_geoms
                    if invalid_percent > 0:
                        issues.append({
                            'type': 'invalid_coordinates',
                            'message': f'Invalid coordinates found: {invalid_percent:.2%}',
                            'severity': 'high'
                        })
                        score -= 0.3

            # Check CRS
            if data.crs is None:
                issues.append({
                    'type': 'missing_crs',
                    'message': 'Missing coordinate reference system',
                    'severity': 'medium'
                })
                score -= 0.2

        elif isinstance(data, pd.DataFrame):
            # Check for lat/lon columns
            lat_cols = [col for col in data.columns if 'lat' in col.lower()]
            lon_cols = [col for col in data.columns if 'lon' in col.lower()]

            for lat_col in lat_cols:
                invalid_coords = 0
                for value in data[lat_col].dropna():
                    if not (-90 <= value <= 90):
                        invalid_coords += 1

                if invalid_coords > 0:
                    invalid_percent = invalid_coords / len(data)
                    issues.append({
                        'type': 'invalid_latitude',
                        'message': f'Invalid latitude values in {lat_col}: {invalid_percent:.2%}',
                        'severity': 'high'
                    })
                    score -= 0.3

            for lon_col in lon_cols:
                invalid_coords = 0
                for value in data[lon_col].dropna():
                    if not (-180 <= value <= 180):
                        invalid_coords += 1

                if invalid_coords > 0:
                    invalid_percent = invalid_coords / len(data)
                    issues.append({
                        'type': 'invalid_longitude',
                        'message': f'Invalid longitude values in {lon_col}: {invalid_percent:.2%}',
                        'severity': 'high'
                    })
                    score -= 0.3

        status = QualityStatus.PASS if score >= 0.8 else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def validate_temporal(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata] = None,
        parameters: Dict[str, Any] = None
    ) -> QualityCheck:
        """
        Validate temporal data.

        Args:
            data: Data to validate
            metadata: Dataset metadata
            parameters: Validation parameters

        Returns:
            Temporal validation check
        """
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Find datetime columns
            datetime_cols = data.select_dtypes(include=['datetime']).columns

            for col in datetime_cols:
                if col in data.columns:
                    # Check for unreasonable date ranges
                    if not data[col].empty:
                        date_range = data[col].max() - data[col].min()
                        if date_range.days > 365 * 100:  # More than 100 years
                            issues.append({
                                'type': 'unreasonable_date_range',
                                'message': f'Unreasonable date range in {col}: {date_range.days} days',
                                'severity': 'low'
                            })
                            score -= 0.1

                        # Check for gaps in time series
                        if len(data[col]) > 1:
                            time_diffs = data[col].diff().dropna()
                            expected_freq = time_diffs.mode().iloc[0] if len(time_diffs.mode()) > 0 else None

                            if expected_freq:
                                # Check for large gaps (more than 10x expected frequency)
                                large_gaps = time_diffs > expected_freq * 10
                                if large_gaps.any():
                                    gap_count = large_gaps.sum()
                                    gap_percent = gap_count / len(time_diffs)
                                    issues.append({
                                        'type': 'temporal_gaps',
                                        'message': f'Temporal gaps in {col}: {gap_percent:.2%}',
                                        'severity': 'medium'
                                    })
                                    score -= 0.2

            # Check temporal extent consistency with metadata
            if metadata and hasattr(metadata, 'temporal') and metadata.temporal:
                temporal_extent = metadata.temporal

                # Find datetime columns and check against metadata bounds
                datetime_cols = data.select_dtypes(include=['datetime']).columns
                if datetime_cols.any():
                    col = datetime_cols[0]  # Use first datetime column
                    data_min = data[col].min()
                    data_max = data[col].max()

                    if data_min < temporal_extent.start or data_max > temporal_extent.end:
                        issues.append({
                            'type': 'temporal_extent_mismatch',
                            'message': 'Data temporal extent exceeds metadata bounds',
                            'severity': 'medium'
                        })
                        score -= 0.2

        status = QualityStatus.PASS if score >= 0.8 else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)

    async def validate_schema(
        self,
        data: Union[pd.DataFrame, gpd.GeoDataFrame],
        metadata: Optional[DatasetMetadata] = None,
        parameters: Dict[str, Any] = None
    ) -> QualityCheck:
        """
        Validate data schema.

        Args:
            data: Data to validate
            metadata: Dataset metadata
            parameters: Validation parameters

        Returns:
            Schema validation check
        """
        issues = []
        score = 1.0

        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Check for required columns if specified
            if parameters and 'required_columns' in parameters:
                required_columns = parameters['required_columns']
                missing_columns = [col for col in required_columns if col not in data.columns]

                if missing_columns:
                    issues.append({
                        'type': 'missing_required_columns',
                        'message': f'Missing required columns: {missing_columns}',
                        'severity': 'high'
                    })
                    score -= 0.3

            # Check column naming conventions
            for col in data.columns:
                # Check for spaces in column names
                if ' ' in col:
                    issues.append({
                        'type': 'column_name_spaces',
                        'message': f'Column name contains spaces: {col}',
                        'severity': 'low'
                    })
                    score -= 0.05

                # Check for special characters
                if any(char in col for char in ['<', '>', ':', '"', '|', '?', '*']):
                    issues.append({
                        'type': 'column_name_special_chars',
                        'message': f'Column name contains special characters: {col}',
                        'severity': 'low'
                    })
                    score -= 0.05

            # Check data type appropriateness
            for col in data.columns:
                dtype = data[col].dtype

                # Check for object columns that might be numeric
                if dtype == 'object' and col.lower() in ['id', 'count', 'number', 'value', 'amount']:
                    try:
                        pd.to_numeric(data[col], errors='coerce')
                        issues.append({
                            'type': 'non_numeric_column',
                            'message': f'Column {col} appears to contain numeric data but is stored as object',
                            'severity': 'low'
                        })
                        score -= 0.1
                    except Exception:
                        pass  # Not numeric data

        status = QualityStatus.PASS if score >= 0.8 else QualityStatus.WARNING if score >= 0.5 else QualityStatus.FAIL

        return QualityCheck(score=max(0.0, score), status=status, issues=issues)


def get_validation_rules(rules_config: str = 'standard') -> Dict[str, ValidationRule]:
    """
    Get validation rules based on configuration.

    Args:
        rules_config: Rules configuration ('basic', 'standard', 'comprehensive')

    Returns:
        Dictionary of validation rules
    """
    rules = QualityRules()

    # Create validation rule objects
    validation_rules = {}

    if rules_config in ['standard', 'comprehensive']:
        validation_rules['completeness'] = ValidationRule(
            name='completeness',
            description='Assess data completeness and missing values',
            function=rules.assess_completeness,
            weight=1.0,
            severity='high'
        )

        validation_rules['accuracy'] = ValidationRule(
            name='accuracy',
            description='Assess data accuracy and outlier detection',
            function=rules.assess_accuracy,
            weight=1.0,
            severity='high'
        )

        validation_rules['consistency'] = ValidationRule(
            name='consistency',
            description='Check data consistency and duplicates',
            function=rules.check_consistency,
            weight=0.9,
            severity='medium'
        )

    if rules_config in ['comprehensive']:
        validation_rules['coordinates'] = ValidationRule(
            name='coordinates',
            description='Validate coordinate data and geometry',
            function=rules.validate_coordinates,
            weight=1.0,
            severity='high'
        )

        validation_rules['temporal'] = ValidationRule(
            name='temporal',
            description='Validate temporal data and consistency',
            function=rules.validate_temporal,
            weight=0.8,
            severity='medium'
        )

        validation_rules['schema'] = ValidationRule(
            name='schema',
            description='Validate data schema and structure',
            function=rules.validate_schema,
            weight=0.7,
            severity='low'
        )

    # Basic rules (always included)
    validation_rules['basic_completeness'] = ValidationRule(
        name='basic_completeness',
        description='Basic completeness check',
        function=rules.assess_completeness,
        weight=1.0,
        severity='high'
    )

    logger.info(f"Generated {len(validation_rules)} validation rules for {rules_config} config")
    return validation_rules


async def validate_completeness_basic(
    data: Union[pd.DataFrame, gpd.GeoDataFrame],
    metadata: Optional[DatasetMetadata] = None,
    parameters: Dict[str, Any] = None
) -> QualityCheck:
    """Basic completeness validation."""
    rules = QualityRules()
    return await rules.assess_completeness(data, metadata, parameters)


async def validate_accuracy_basic(
    data: Union[pd.DataFrame, gpd.GeoDataFrame],
    metadata: Optional[DatasetMetadata] = None,
    parameters: Dict[str, Any] = None
) -> QualityCheck:
    """Basic accuracy validation."""
    rules = QualityRules()
    return await rules.assess_accuracy(data, metadata, parameters)


async def validate_coordinates_basic(
    data: Union[pd.DataFrame, gpd.GeoDataFrame],
    metadata: Optional[DatasetMetadata] = None,
    parameters: Dict[str, Any] = None
) -> QualityCheck:
    """Basic coordinate validation."""
    rules = QualityRules()
    return await rules.validate_coordinates(data, metadata, parameters)
