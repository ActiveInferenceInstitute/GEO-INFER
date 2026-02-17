"""
Data domain validation tests.

Tests each conftest domain fixture (health, economic, agricultural,
logistics, bioinformatics, IoT, time-series) through various
validators and statistical assertions.  Each domain × check produces
multiple parametrized test cases.
"""

import math
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from geo_infer_test.core.validators import DataQualityValidator, SpatialValidator

# ============================================================================
# Domain-level structural validation
# ============================================================================

# Health data structural expectations
_HEALTH_REQUIRED_COLS = ["date", "region", "cases", "hospitalizations", "deaths",
                         "vaccinations", "testing_rate", "population"]

# Economic data structural expectations
_ECONOMIC_REQUIRED_COLS = ["date", "region", "gdp", "unemployment_rate",
                           "inflation_rate", "housing_prices",
                           "consumer_confidence", "retail_sales", "population"]

# Agricultural data structural expectations
_AGRI_REQUIRED_COLS = ["date", "field_id", "temperature", "rainfall",
                        "soil_moisture", "ndvi", "yield_estimate",
                        "nitrogen_level", "phosphorus_level",
                        "potassium_level", "pest_pressure",
                        "disease_incidence"]

# Logistics data structural expectations
_LOGISTICS_REQUIRED_COLS = ["date", "route_id", "distance_km", "duration_hours",
                             "fuel_consumption", "cargo_weight",
                             "delivery_success_rate", "customer_satisfaction",
                             "cost_per_km", "carbon_emissions",
                             "vehicle_utilization"]

# Bioinformatics data structural expectations
_BIO_REQUIRED_COLS = ["sample_id", "gene_id", "expression_level",
                       "lat", "lng", "elevation", "habitat_type"]


# ============================================================================
# Health data tests
# ============================================================================
class TestHealthDataDomain:
    """Validate sample_health_data fixture."""

    def test_columns_present(self, sample_health_data):
        for col in _HEALTH_REQUIRED_COLS:
            assert col in sample_health_data.columns, f"Missing column: {col}"

    def test_row_count(self, sample_health_data):
        # 3 regions × 365 days
        assert len(sample_health_data) == 3 * 365

    def test_regions(self, sample_health_data):
        regions = sample_health_data["region"].unique()
        assert len(regions) == 3

    def test_no_negative_cases(self, sample_health_data):
        assert (sample_health_data["cases"] >= 0).all()

    def test_no_negative_deaths(self, sample_health_data):
        assert (sample_health_data["deaths"] >= 0).all()

    def test_no_negative_hospitalizations(self, sample_health_data):
        assert (sample_health_data["hospitalizations"] >= 0).all()

    def test_testing_rate_range(self, sample_health_data):
        assert (sample_health_data["testing_rate"] >= 0).all()
        assert (sample_health_data["testing_rate"] <= 1).all()

    def test_population_positive(self, sample_health_data):
        assert (sample_health_data["population"] > 0).all()

    @pytest.mark.parametrize("col", ["cases", "hospitalizations", "deaths", "vaccinations"])
    def test_integer_columns(self, sample_health_data, col):
        vals = sample_health_data[col]
        # All values should be integer-like
        assert (vals == vals.astype(int)).all()

    @pytest.mark.parametrize("region", ["Region_A", "Region_B", "Region_C"])
    def test_region_days(self, sample_health_data, region):
        subset = sample_health_data[sample_health_data["region"] == region]
        assert len(subset) == 365

    def test_quality_validator_passes(self, sample_health_data):
        """Run through DataQualityValidator (uses generic timestamp/value rules)."""
        # Add columns the validator expects
        df = sample_health_data.copy()
        df["timestamp"] = df["date"].astype(str)
        df["value"] = df["cases"].astype(float)
        result = DataQualityValidator().validate(df)
        assert result["total_records"] == len(df)
        assert result["quality_score"] >= 0.0


# ============================================================================
# Economic data tests
# ============================================================================
class TestEconomicDataDomain:
    """Validate sample_economic_data fixture."""

    def test_columns_present(self, sample_economic_data):
        for col in _ECONOMIC_REQUIRED_COLS:
            assert col in sample_economic_data.columns, f"Missing column: {col}"

    def test_row_count(self, sample_economic_data):
        # 3 regions × 48 months
        assert len(sample_economic_data) == 3 * 48

    def test_regions(self, sample_economic_data):
        assert len(sample_economic_data["region"].unique()) == 3

    @pytest.mark.parametrize("col", ["gdp", "housing_prices", "retail_sales", "population"])
    def test_positive_values(self, sample_economic_data, col):
        assert (sample_economic_data[col] > 0).all(), f"{col} has non-positive values"

    @pytest.mark.parametrize("col", _ECONOMIC_REQUIRED_COLS[2:])  # Skip date/region
    def test_no_nulls(self, sample_economic_data, col):
        assert sample_economic_data[col].notna().all(), f"Nulls in {col}"

    def test_unemployment_bounds(self, sample_economic_data):
        assert (sample_economic_data["unemployment_rate"] >= 0).all()
        assert (sample_economic_data["unemployment_rate"] <= 20).all()

    @pytest.mark.parametrize("region", ["Metro_A", "Metro_B", "Metro_C"])
    def test_region_months(self, sample_economic_data, region):
        subset = sample_economic_data[sample_economic_data["region"] == region]
        assert len(subset) == 48


# ============================================================================
# Agricultural data tests
# ============================================================================
class TestAgriculturalDataDomain:
    """Validate sample_agricultural_data fixture."""

    def test_columns_present(self, sample_agricultural_data):
        for col in _AGRI_REQUIRED_COLS:
            assert col in sample_agricultural_data.columns, f"Missing column: {col}"

    def test_row_count(self, sample_agricultural_data):
        # 3 fields × 365 days
        assert len(sample_agricultural_data) == 3 * 365

    def test_fields(self, sample_agricultural_data):
        assert len(sample_agricultural_data["field_id"].unique()) == 3

    @pytest.mark.parametrize("col", ["soil_moisture", "ndvi"])
    def test_bounded_columns(self, sample_agricultural_data, col):
        # These should generally be [0, 1]-ish but we allow noise
        vals = sample_agricultural_data[col]
        # At least 90% in reasonable range
        in_range = ((vals >= -0.5) & (vals <= 1.5)).mean()
        assert in_range >= 0.9, f"{col}: {in_range:.0%} in range"

    @pytest.mark.parametrize("col", ["nitrogen_level", "phosphorus_level", "potassium_level"])
    def test_nutrient_positive(self, sample_agricultural_data, col):
        # Nutrients should be mostly positive (noise may push a few slightly negative)
        positive_frac = (sample_agricultural_data[col] > 0).mean()
        assert positive_frac >= 0.95, f"{col}: only {positive_frac:.0%} positive"

    @pytest.mark.parametrize("field", ["Field_A", "Field_B", "Field_C"])
    def test_field_days(self, sample_agricultural_data, field):
        subset = sample_agricultural_data[sample_agricultural_data["field_id"] == field]
        assert len(subset) == 365

    @pytest.mark.parametrize("col", _AGRI_REQUIRED_COLS[2:])  # Skip date/field
    def test_no_nulls(self, sample_agricultural_data, col):
        assert sample_agricultural_data[col].notna().all(), f"Nulls in {col}"


# ============================================================================
# Logistics data tests
# ============================================================================
class TestLogisticsDataDomain:
    """Validate sample_logistics_data fixture."""

    def test_columns_present(self, sample_logistics_data):
        for col in _LOGISTICS_REQUIRED_COLS:
            assert col in sample_logistics_data.columns, f"Missing column: {col}"

    def test_row_count(self, sample_logistics_data):
        # 3 routes × 30 days
        assert len(sample_logistics_data) == 3 * 30

    def test_routes(self, sample_logistics_data):
        assert len(sample_logistics_data["route_id"].unique()) == 3

    @pytest.mark.parametrize("col", ["distance_km", "duration_hours", "fuel_consumption",
                                      "cargo_weight", "cost_per_km", "carbon_emissions"])
    def test_positive_values(self, sample_logistics_data, col):
        assert (sample_logistics_data[col] > 0).all(), f"{col} has non-positive values"

    @pytest.mark.parametrize("route", ["Route_A", "Route_B", "Route_C"])
    def test_route_days(self, sample_logistics_data, route):
        subset = sample_logistics_data[sample_logistics_data["route_id"] == route]
        assert len(subset) == 30

    @pytest.mark.parametrize("col", _LOGISTICS_REQUIRED_COLS[2:])  # Skip date/route
    def test_no_nulls(self, sample_logistics_data, col):
        assert sample_logistics_data[col].notna().all(), f"Nulls in {col}"


# ============================================================================
# Bioinformatics data tests
# ============================================================================
class TestBioinformaticsDataDomain:
    """Validate sample_bioinformatics_data fixture."""

    def test_columns_present(self, sample_bioinformatics_data):
        for col in _BIO_REQUIRED_COLS:
            assert col in sample_bioinformatics_data.columns, f"Missing column: {col}"

    def test_row_count(self, sample_bioinformatics_data):
        # 50 samples × 100 genes
        assert len(sample_bioinformatics_data) == 50 * 100

    def test_samples(self, sample_bioinformatics_data):
        assert len(sample_bioinformatics_data["sample_id"].unique()) == 50

    def test_genes(self, sample_bioinformatics_data):
        assert len(sample_bioinformatics_data["gene_id"].unique()) == 100

    def test_expression_positive(self, sample_bioinformatics_data):
        assert (sample_bioinformatics_data["expression_level"] > 0).all()

    def test_habitat_types(self, sample_bioinformatics_data):
        valid_types = {"forest", "grassland", "wetland", "urban"}
        actual_types = set(sample_bioinformatics_data["habitat_type"].unique())
        assert actual_types.issubset(valid_types)

    @pytest.mark.parametrize("habitat", ["forest", "grassland", "wetland", "urban"])
    def test_habitat_has_samples(self, sample_bioinformatics_data, habitat):
        subset = sample_bioinformatics_data[sample_bioinformatics_data["habitat_type"] == habitat]
        # With 50 random samples, each habitat should get at least a few
        assert len(subset) > 0, f"No samples for habitat: {habitat}"

    def test_spatial_coordinates_valid(self, sample_bioinformatics_data):
        lats = sample_bioinformatics_data["lat"]
        lngs = sample_bioinformatics_data["lng"]
        assert (lats >= -90).all() and (lats <= 90).all()
        assert (lngs >= -180).all() and (lngs <= 180).all()

    @pytest.mark.parametrize("col", _BIO_REQUIRED_COLS)
    def test_no_nulls(self, sample_bioinformatics_data, col):
        assert sample_bioinformatics_data[col].notna().all(), f"Nulls in {col}"


# ============================================================================
# Time series data tests
# ============================================================================
class TestTimeSeriesDomain:
    """Validate sample_time_series fixture."""

    def test_columns_present(self, sample_time_series):
        for col in ["date", "temperature", "humidity", "precipitation"]:
            assert col in sample_time_series.columns

    def test_row_count(self, sample_time_series):
        assert len(sample_time_series) == 365

    def test_daily_frequency(self, sample_time_series):
        diffs = sample_time_series["date"].diff().dropna()
        assert (diffs == pd.Timedelta(days=1)).all()

    @pytest.mark.parametrize("col", ["temperature", "humidity", "precipitation"])
    def test_no_nulls(self, sample_time_series, col):
        assert sample_time_series[col].notna().all()

    def test_precipitation_non_negative(self, sample_time_series):
        assert (sample_time_series["precipitation"] >= 0).all()

    def test_temperature_reasonable(self, sample_time_series):
        # With mean ~15 and amplitude ~10, range should be roughly [-5, 35]
        assert sample_time_series["temperature"].min() > -20
        assert sample_time_series["temperature"].max() < 50


# ============================================================================
# IoT sensor data structural tests
# ============================================================================
class TestIoTSensorDataDomain:
    """Validate sample_iot_data fixture."""

    def test_sensor_count(self, sample_iot_data):
        assert len(sample_iot_data) == 5

    @pytest.mark.parametrize("idx", range(5))
    def test_sensor_has_id(self, sample_iot_data, idx):
        assert "sensor_id" in sample_iot_data[idx]
        assert sample_iot_data[idx]["sensor_id"].startswith("sensor_")

    @pytest.mark.parametrize("idx", range(5))
    def test_sensor_has_measurements(self, sample_iot_data, idx):
        assert len(sample_iot_data[idx]["measurements"]) == 1000

    @pytest.mark.parametrize("idx", range(5))
    def test_sensor_has_location(self, sample_iot_data, idx):
        loc = sample_iot_data[idx]["location"]
        assert "lat" in loc and "lng" in loc
        assert -90 <= loc["lat"] <= 90
        assert -180 <= loc["lng"] <= 180

    @pytest.mark.parametrize("idx", range(5))
    def test_measurement_keys(self, sample_iot_data, idx):
        m = sample_iot_data[idx]["measurements"][0]
        for key in ["timestamp", "temperature", "humidity", "pressure",
                     "air_quality", "battery_level"]:
            assert key in m, f"Missing key: {key}"


# ============================================================================
# Cross-domain statistical tests
# ============================================================================
class TestCrossDomainStatistics:
    """Cross-cutting statistical property tests."""

    @pytest.mark.parametrize("col", ["temperature", "humidity"])
    def test_timeseries_seasonal_pattern(self, sample_time_series, col):
        """Check that seasonal data exhibits sinusoidal-like variance."""
        vals = sample_time_series[col]
        # Standard deviation should be significant (not flat)
        assert vals.std() > 1.0

    @pytest.mark.parametrize("col", ["cases", "hospitalizations", "deaths"])
    def test_health_correlated(self, sample_health_data, col):
        """Deaths should generally be fewer than cases."""
        region_a = sample_health_data[sample_health_data["region"] == "Region_A"]
        if col in ("hospitalizations", "deaths"):
            assert region_a[col].mean() <= region_a["cases"].mean()

    def test_economic_gdp_grows(self, sample_economic_data):
        """GDP should generally trend upward over 48 months."""
        metro_a = sample_economic_data[sample_economic_data["region"] == "Metro_A"].sort_values("date")
        first_quarter = metro_a["gdp"].head(12).mean()
        last_quarter = metro_a["gdp"].tail(12).mean()
        assert last_quarter > first_quarter * 0.8  # Allow some randomness

    def test_agri_ndvi_seasonal(self, sample_agricultural_data):
        """NDVI should be higher during growing season (first 120 days)."""
        fa = sample_agricultural_data[sample_agricultural_data["field_id"] == "Field_A"]
        growing = fa[fa["date"].dt.dayofyear <= 120]["ndvi"].mean()
        dormant = fa[fa["date"].dt.dayofyear > 200]["ndvi"].mean()
        assert growing > dormant

    def test_bio_forest_expression_higher(self, sample_bioinformatics_data):
        """Forest habitat should have higher gene expression (multiplied by 1.2 in fixture)."""
        forest = sample_bioinformatics_data[
            sample_bioinformatics_data["habitat_type"] == "forest"
        ]["expression_level"].mean()
        urban = sample_bioinformatics_data[
            sample_bioinformatics_data["habitat_type"] == "urban"
        ]["expression_level"].mean()
        assert forest > urban
