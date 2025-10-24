"""
Test fixtures for GEO-INFER-DATA.

This module contains test fixtures, mock data, and test utilities
for comprehensive testing of all GEO-INFER-DATA components.

Fixtures:
    mock_environmental_data: Sample environmental monitoring data
    mock_geospatial_data: Sample geospatial vector data
    mock_raster_data: Sample raster/imagery data
    mock_time_series_data: Sample time series data
    mock_metadata: Sample dataset metadata
    mock_api_responses: Mock API response data
    mock_database_config: Mock database configuration

Examples:
    >>> # Use fixtures in tests
    >>> def test_ingestion(mock_environmental_data, mock_metadata):
    ...     # Test data ingestion
    ...     result = await ingestion.ingest_multi_source(sensors=mock_environmental_data)
    ...     assert result['quality_score'] > 0.8
"""

import pytest
import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import datetime

from geo_infer_data.models.schemas import (
    DatasetMetadata,
    SpatialExtent,
    TemporalExtent,
    DataLineage
)


@pytest.fixture
def mock_environmental_data():
    """Create mock environmental monitoring data."""
    n_records = 1000

    return pd.DataFrame({
        'sensor_id': [f'sensor_{i%10}' for i in range(n_records)],
        'timestamp': pd.date_range('2023-01-01', periods=n_records, freq='H'),
        'temperature': np.random.normal(20, 5, n_records),
        'humidity': np.random.normal(60, 10, n_records),
        'air_quality': np.random.normal(50, 15, n_records),
        'latitude': np.random.normal(37.7749, 0.1, n_records),
        'longitude': np.random.normal(-122.4194, 0.1, n_records),
        'wind_speed': np.random.normal(5, 2, n_records),
        'precipitation': np.random.exponential(0.1, n_records)
    })


@pytest.fixture
def mock_geospatial_data():
    """Create mock geospatial vector data."""
    n_points = 5000

    return gpd.GeoDataFrame({
        'id': range(n_points),
        'temperature': np.random.normal(20, 5, n_points),
        'humidity': np.random.normal(60, 10, n_points),
        'population': np.random.normal(1000, 200, n_points),
        'land_use': np.random.choice(['residential', 'commercial', 'industrial', 'park'], n_points)
    }, geometry=gpd.points_from_xy(
        np.random.normal(-122.4194, 0.2, n_points),
        np.random.normal(37.7749, 0.2, n_points)
    ), crs="EPSG:4326")


@pytest.fixture
def mock_raster_data():
    """Create mock raster/imagery data."""
    # Create multi-band raster data
    bands = 4  # RGB + NIR
    height = 1000
    width = 1000

    # Generate realistic-looking raster data
    raster_data = np.random.normal(0, 50, (bands, height, width)).astype(np.uint8)

    # Add some spatial patterns
    for band in range(bands):
        # Add gradient pattern
        gradient = np.linspace(0, 255, width)
        for row in range(height):
            raster_data[band, row, :] += gradient * (row / height)

    return raster_data


@pytest.fixture
def mock_time_series_data():
    """Create mock time series data."""
    n_records = 50000

    return pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=n_records, freq='15min'),
        'temperature': np.random.normal(20, 5, n_records),
        'humidity': np.random.normal(60, 10, n_records),
        'pressure': np.random.normal(1013, 5, n_records),
        'wind_speed': np.random.normal(5, 2, n_records),
        'wind_direction': np.random.uniform(0, 360, n_records),
        'precipitation': np.random.exponential(0.05, n_records),
        'solar_radiation': np.random.normal(400, 100, n_records)
    })


@pytest.fixture
def mock_metadata():
    """Create comprehensive mock dataset metadata."""
    return DatasetMetadata(
        title="Mock Test Dataset",
        description="Comprehensive test dataset for GEO-INFER-DATA testing",
        spatial=SpatialExtent(
            bbox=[-122.6, 37.6, -122.2, 38.0],
            crs="EPSG:4326"
        ),
        temporal=TemporalExtent(
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            resolution="PT1H"
        ),
        lineage=DataLineage(
            source="mock_test_data",
            process="automated_testing",
            created_by="test_framework"
        ),
        keywords=["test", "mock", "environmental", "monitoring"],
        contact={
            "organization": "Test Organization",
            "email": "test@geo-infer.org",
            "phone": "+1-555-TEST"
        },
        license="CC BY 4.0",
        rights="Test data for development purposes"
    )


@pytest.fixture
def mock_api_responses():
    """Create mock API response data."""
    return {
        'weather_api': {
            'status': 200,
            'data': {
                'temperature': 22.5,
                'humidity': 65,
                'pressure': 1013,
                'wind_speed': 5.2,
                'wind_direction': 180,
                'timestamp': datetime.utcnow().isoformat()
            }
        },
        'satellite_api': {
            'status': 200,
            'data': {
                'imagery': 'base64_encoded_image_data',
                'bands': ['red', 'green', 'blue', 'nir'],
                'resolution': 30,
                'acquisition_date': datetime(2023, 6, 15).isoformat(),
                'cloud_cover': 0.1
            }
        },
        'crowdsourced_api': {
            'status': 200,
            'data': {
                'reports': [
                    {
                        'id': 'report_1',
                        'timestamp': datetime(2023, 6, 15, 10, 30).isoformat(),
                        'latitude': 37.7749,
                        'longitude': -122.4194,
                        'category': 'air_quality',
                        'description': 'Poor air quality observed',
                        'user_id': 'user_123'
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_database_config():
    """Create mock database configuration."""
    return {
        'postgresql': {
            'host': 'localhost',
            'port': 5432,
            'database': 'geo_infer_test',
            'user': 'test_user',
            'password': 'test_password',
            'schema': 'public'
        },
        'mongodb': {
            'host': 'localhost',
            'port': 27017,
            'database': 'geo_infer_test',
            'collection': 'test_data'
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None
        }
    }


@pytest.fixture
def mock_storage_config():
    """Create mock storage configuration."""
    return {
        'local': {
            'base_path': '/tmp/geo_infer_test',
            'create_dirs': True
        },
        'minio': {
            'endpoint': 'localhost:9000',
            'access_key': 'test_key',
            'secret_key': 'test_secret',
            'bucket': 'test-bucket',
            'secure': False
        },
        's3': {
            'endpoint': 'https://s3.amazonaws.com',
            'access_key': 'test_aws_key',
            'secret_key': 'test_aws_secret',
            'bucket': 'test-s3-bucket',
            'region': 'us-east-1'
        }
    }


@pytest.fixture
def mock_validation_config():
    """Create mock validation configuration."""
    return {
        'validation_rules': ['completeness', 'accuracy', 'consistency', 'validity'],
        'quality_threshold': 0.8,
        'strict_mode': False,
        'real_time_monitoring': True,
        'custom_rules': {
            'business_rule_check': 'validate_business_constraints',
            'domain_validation': 'validate_domain_specific_rules'
        }
    }


@pytest.fixture
def mock_etl_config():
    """Create mock ETL pipeline configuration."""
    return {
        'name': 'Test ETL Pipeline',
        'description': 'Test pipeline for integration testing',
        'source': {
            'type': 'file',
            'configuration': {
                'file_path': '/tmp/test_input.csv',
                'format': 'csv'
            }
        },
        'destination': {
            'type': 'database',
            'configuration': {
                'table_name': 'processed_test_data',
                'if_exists': 'replace'
            }
        },
        'transformations': [
            {
                'type': 'filter',
                'parameters': {'conditions': {'temperature': {'min': -50, 'max': 100}}},
                'order': 1
            },
            {
                'type': 'clean',
                'parameters': {'remove_nulls': True, 'outlier_method': 'iqr'},
                'order': 2
            },
            {
                'type': 'transform',
                'parameters': {'transformations': {'temperature': {'type': 'normalize'}}},
                'order': 3
            }
        ],
        'schedule': {
            'cron': '0 2 * * *',
            'timezone': 'UTC'
        }
    }


@pytest.fixture
def mock_access_patterns():
    """Create mock access pattern data."""
    return {
        'query_frequency': 'high',
        'spatial_queries': [
            {'bbox': [-122.5, 37.7, -122.3, 37.9], 'frequency': 'hourly'},
            {'bbox': [-122.4, 37.6, -122.2, 37.8], 'frequency': 'daily'}
        ],
        'temporal_queries': [
            {'start': datetime(2023, 6, 1), 'end': datetime(2023, 8, 31), 'frequency': 'daily'},
            {'start': datetime(2023, 1, 1), 'end': datetime(2023, 12, 31), 'frequency': 'weekly'}
        ],
        'peak_hours': [8, 9, 10, 17, 18, 19],
        'batch_processing': False,
        'real_time_access': True,
        'data_growth_rate': 'moderate'
    }


@pytest.fixture
def mock_performance_metrics():
    """Create mock performance metrics."""
    return {
        'execution_time': 45.2,
        'records_processed': 100000,
        'throughput': 2212,
        'memory_usage': 156,
        'cpu_usage': 45,
        'errors': 0,
        'warnings': 2,
        'quality_score': 0.87,
        'optimization_applied': True,
        'cache_hits': 8500,
        'cache_misses': 1500
    }


@pytest.fixture
def mock_error_scenarios():
    """Create mock error scenarios for testing."""
    return {
        'network_error': {
            'type': 'ConnectionError',
            'message': 'Failed to connect to external API',
            'retryable': True
        },
        'validation_error': {
            'type': 'ValidationError',
            'message': 'Data validation failed: missing required fields',
            'retryable': False
        },
        'storage_error': {
            'type': 'StorageError',
            'message': 'Failed to write to storage backend',
            'retryable': True
        },
        'timeout_error': {
            'type': 'TimeoutError',
            'message': 'Operation timed out after 30 seconds',
            'retryable': True
        },
        'permission_error': {
            'type': 'PermissionError',
            'message': 'Access denied to storage location',
            'retryable': False
        }
    }


@pytest.fixture
def mock_quality_reports():
    """Create mock quality assessment reports."""
    return {
        'excellent': {
            'overall_score': 0.95,
            'status': 'pass',
            'checks': {
                'completeness': {'score': 0.98, 'status': 'pass', 'issues': []},
                'accuracy': {'score': 0.96, 'status': 'pass', 'issues': []},
                'consistency': {'score': 0.94, 'status': 'pass', 'issues': []},
                'validity': {'score': 0.93, 'status': 'pass', 'issues': []}
            },
            'recommendations': []
        },
        'good': {
            'overall_score': 0.85,
            'status': 'pass',
            'checks': {
                'completeness': {'score': 0.90, 'status': 'pass', 'issues': []},
                'accuracy': {'score': 0.88, 'status': 'pass', 'issues': []},
                'consistency': {'score': 0.82, 'status': 'warning', 'issues': ['minor_duplicates']},
                'validity': {'score': 0.80, 'status': 'warning', 'issues': ['format_warnings']}
            },
            'recommendations': ['Review duplicate detection', 'Update format validation']
        },
        'poor': {
            'overall_score': 0.45,
            'status': 'fail',
            'checks': {
                'completeness': {'score': 0.60, 'status': 'fail', 'issues': ['high_missing_values']},
                'accuracy': {'score': 0.40, 'status': 'fail', 'issues': ['many_outliers', 'invalid_coordinates']},
                'consistency': {'score': 0.35, 'status': 'fail', 'issues': ['mixed_types', 'duplicates']},
                'validity': {'score': 0.45, 'status': 'fail', 'issues': ['schema_violations']}
            },
            'recommendations': [
                'Fix data collection process',
                'Implement data cleaning',
                'Review validation rules',
                'Update schema definitions'
            ]
        }
    }
