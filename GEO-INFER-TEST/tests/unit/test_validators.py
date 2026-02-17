"""
Unit tests for core validators using Property-Based Testing.
"""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.extra.pandas import data_frames, column, range_indexes

from geo_infer_test.core.validators import (
    DataQualityValidator,
    SpatialValidator,
    IoTValidator,
    BayesianValidator,
    ValidationRule
)
from geo_infer_test.models.types import TestResult

# Strategies for DataQualityValidator
@st.composite
def quality_dataframe(draw):
    """Generate a DataFrame for quality validation."""
    return draw(data_frames(
        columns=[
            column('timestamp', elements=st.datetimes().map(lambda dt: dt.isoformat())),
            column('value', elements=st.floats(allow_nan=True, allow_infinity=True)),
            column('category', elements=st.text(min_size=1, max_size=10)),
        ],
        index=range_indexes(min_size=0, max_size=50)
    ))

class TestHypothesisValidators:
    """Property-based tests for validators."""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
    @given(quality_dataframe())
    def test_data_quality_fuzz(self, df):
        """Fuzz DataQualityValidator with random DataFrames."""
        validator = DataQualityValidator()
        result = validator.validate(df)
        
        assert "quality_score" in result
        assert 0.0 <= result["quality_score"] <= 1.0
        assert result["total_records"] == len(df)
        
        # Verify error tracking
        if result["quality_score"] < 1.0:
            assert len(result["validation_errors"]) > 0 or len(result["warnings"]) > 0

    @settings(max_examples=50)
    @given(st.lists(
        st.dictionaries(
            keys=st.sampled_from(["latitude", "longitude", "h3_index"]),
            values=st.one_of(
                st.floats(min_value=-200, max_value=200),  # Lats/Lons (including invalid)
                st.text(min_size=15, max_size=15)          # H3-like strings
            )
        ),
        min_size=1, max_size=50
    ))
    def test_spatial_validator_fuzz(self, data):
        """Fuzz SpatialValidator with random dictionaries."""
        validator = SpatialValidator()
        # Ensure we have some structure that resembles expected input
        # Filter to ensure at least some valid keys exist to trigger checks
        # But validator handles missing keys gracefully (by skipping checks)
        
        result = validator.validate(data)
        assert "spatial_validation" in result
        assert result["total_records"] == len(data)

    @settings(max_examples=50)
    @given(st.lists(
        st.dictionaries(
            keys=st.sampled_from(["sensor_id", "timestamp", "radiation_level"]),
            values=st.one_of(
                st.text(min_size=1),
                st.floats(allow_nan=True),
                st.datetimes().map(str)
            )
        ),
        min_size=1, max_size=20
    ))
    def test_iot_validator_fuzz(self, data):
        """Fuzz IoTValidator with random sensor data."""
        validator = IoTValidator()
        result = validator.validate(data)
        
        assert "sensor_validation" in result
        assert result["total_sensors"] == len(data)
        
        # Check specific validation outputs if fields exist
        if any("radiation_level" in d for d in data):
            assert "anomaly_detection" in result["sensor_validation"]

    @settings(max_examples=50)
    @given(st.dictionaries(
        keys=st.sampled_from(["converged", "predictions", "uncertainty"]),
        values=st.one_of(
            st.booleans(),
            st.lists(st.floats(), max_size=100),
            st.lists(st.floats(min_value=0), max_size=100)
        )
    ))
    def test_bayesian_validator_fuzz(self, data):
        """Fuzz BayesianValidator with inference results."""
        validator = BayesianValidator()
        result = validator.validate(data)
        
        assert "inference_validation" in result
        assert "overall_quality" in result
        
        # Convergence logic
        if data.get("converged") is True:
             # Should be at least acceptable unless predictions are missing
             pass
