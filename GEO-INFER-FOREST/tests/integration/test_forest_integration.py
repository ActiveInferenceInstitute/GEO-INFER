"""
Integration tests for GEO-INFER-FOREST: forest health monitoring and carbon sequestration pipeline.

Tests ForestHealthMonitor and CarbonSequestrationModeler working together in a
forest analysis pipeline using synthetic raster data.
"""

import pytest
import numpy as np

try:
    import xarray as xr

    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False

pytestmark = [
    pytest.mark.integration,
]


@pytest.fixture
def ndvi_data():
    """Create synthetic NDVI data (0-1 range, higher = more vegetation)."""
    np.random.seed(42)
    return xr.DataArray(
        np.random.uniform(0.3, 0.9, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(37.0, 38.0, 10),
            "lon": np.linspace(-122.0, -121.0, 10),
        },
    )


@pytest.fixture
def temperature_data():
    """Create synthetic temperature data in Celsius."""
    np.random.seed(43)
    return xr.DataArray(
        np.random.uniform(15.0, 30.0, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(37.0, 38.0, 10),
            "lon": np.linspace(-122.0, -121.0, 10),
        },
    )


@pytest.fixture
def precipitation_data():
    """Create synthetic precipitation data in mm/year."""
    np.random.seed(44)
    return xr.DataArray(
        np.random.uniform(400.0, 1500.0, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(37.0, 38.0, 10),
            "lon": np.linspace(-122.0, -121.0, 10),
        },
    )


@pytest.fixture
def biomass_data():
    """Create synthetic forest biomass data (tons/ha)."""
    np.random.seed(45)
    return xr.DataArray(
        np.random.uniform(50.0, 300.0, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(37.0, 38.0, 10),
            "lon": np.linspace(-122.0, -121.0, 10),
        },
    )


@pytest.fixture
def forest_cover_time_series():
    """Create synthetic forest cover time series (fraction 0-1) with deforestation."""
    np.random.seed(46)
    n_time = 5
    cover = np.zeros((n_time, 10, 10))
    # Start with high cover and reduce over time in some areas
    cover[0] = np.random.uniform(0.7, 1.0, (10, 10))
    for t in range(1, n_time):
        cover[t] = cover[t - 1] - np.random.uniform(0, 0.1, (10, 10))
        cover[t] = np.clip(cover[t], 0, 1)

    return xr.DataArray(
        cover,
        dims=["time", "lat", "lon"],
        coords={
            "time": np.arange(n_time),
            "lat": np.linspace(37.0, 38.0, 10),
            "lon": np.linspace(-122.0, -121.0, 10),
        },
    )


class TestForestHealthPipeline:
    """Test forest health assessment pipeline."""

    def test_basic_health_assessment(self, ndvi_data):
        """Test health assessment from NDVI data alone."""
        from geo_infer_forest.core.forest_health import ForestHealthMonitor

        monitor = ForestHealthMonitor()
        result = monitor.assess_forest_health(ndvi_data)

        assert "health_index" in result
        assert "ndvi" in result
        # Health index should be normalized 0-1
        assert float(result["health_index"].min()) >= 0.0
        assert float(result["health_index"].max()) <= 1.0 + 1e-6

    def test_health_with_climate_data(
        self, ndvi_data, temperature_data, precipitation_data
    ):
        """Test health assessment including climate stress factors."""
        from geo_infer_forest.core.forest_health import ForestHealthMonitor

        monitor = ForestHealthMonitor()
        result = monitor.assess_forest_health(
            ndvi_data,
            temperature=temperature_data,
            precipitation=precipitation_data,
        )

        assert "health_index" in result
        assert "temperature_stress" in result
        assert "water_stress" in result

        # Stress values should be non-negative
        assert float(result["temperature_stress"].min()) >= 0.0
        assert float(result["water_stress"].min()) >= 0.0

    def test_deforestation_detection(self, forest_cover_time_series):
        """Test deforestation detection from cover time series."""
        from geo_infer_forest.core.forest_health import ForestHealthMonitor

        monitor = ForestHealthMonitor()
        result = monitor.detect_deforestation(forest_cover_time_series, threshold=0.1)

        assert "deforestation" in result
        assert "cover_change" in result
        assert "deforestation_area" in result

        # Should detect some deforestation given our declining cover data
        deforestation_count = int(result["deforestation"].sum())
        assert (
            deforestation_count > 0
        ), "Should detect deforestation in declining cover data"


class TestCarbonSequestrationPipeline:
    """Test carbon stock and sequestration calculations."""

    def test_carbon_stock_from_biomass(self, biomass_data):
        """Test carbon stock calculation from biomass."""
        from geo_infer_forest.core.carbon_sequestration import (
            CarbonSequestrationModeler,
        )

        modeler = CarbonSequestrationModeler()
        carbon_stock = modeler.calculate_carbon_stock(biomass_data)

        # Carbon should be ~50% of biomass
        expected = biomass_data * 0.5
        np.testing.assert_allclose(carbon_stock.values, expected.values, rtol=1e-6)

    def test_sequestration_rate_estimation(self):
        """Test sequestration rate from growth data."""
        from geo_infer_forest.core.carbon_sequestration import (
            CarbonSequestrationModeler,
        )

        modeler = CarbonSequestrationModeler()

        growth = xr.DataArray(
            np.full((5, 5), 10.0),  # 10 tons/ha/year growth
            dims=["lat", "lon"],
        )

        rate = modeler.estimate_sequestration_rate(growth, time_period=1.0)
        # Rate should be growth * 0.5 (carbon fraction)
        np.testing.assert_allclose(rate.values, 5.0, rtol=1e-6)

    def test_carbon_credits_calculation(self, biomass_data):
        """Test carbon credit value calculation."""
        from geo_infer_forest.core.carbon_sequestration import (
            CarbonSequestrationModeler,
        )

        modeler = CarbonSequestrationModeler()

        sequestration = xr.DataArray(
            np.full((10, 10), 5.0),  # 5 tons C/ha/year
            dims=["lat", "lon"],
        )
        area = xr.DataArray(
            np.full((10, 10), 100.0),  # 100 ha per cell
            dims=["lat", "lon"],
        )

        credits = modeler.calculate_carbon_credits(
            sequestration, area, price_per_ton=50.0
        )

        # Expected: 5 * 3.67 * 100 * 50 = 91,750 per cell
        expected_per_cell = 5.0 * 3.67 * 100.0 * 50.0
        np.testing.assert_allclose(credits.values, expected_per_cell, rtol=1e-6)


class TestForestCarbonIntegrationPipeline:
    """Test full pipeline: health assessment -> carbon stock -> credits."""

    def test_health_to_carbon_pipeline(self, ndvi_data, biomass_data):
        """Test the full pipeline from health assessment through carbon credit valuation."""
        from geo_infer_forest.core.forest_health import ForestHealthMonitor
        from geo_infer_forest.core.carbon_sequestration import (
            CarbonSequestrationModeler,
        )

        # Step 1: Assess forest health
        monitor = ForestHealthMonitor()
        health = monitor.assess_forest_health(ndvi_data)
        health_index = health["health_index"]

        # Step 2: Estimate effective biomass adjusted by health
        effective_biomass = biomass_data * health_index

        # Step 3: Calculate carbon stock
        modeler = CarbonSequestrationModeler()
        carbon_stock = modeler.calculate_carbon_stock(effective_biomass)

        # Carbon stock should be less than or equal to raw biomass * 0.5
        raw_carbon = biomass_data * 0.5
        assert float(carbon_stock.mean()) <= float(
            raw_carbon.mean()
        ), "Health-adjusted carbon should not exceed raw carbon estimate"
        assert float(carbon_stock.min()) >= 0, "Carbon stock should be non-negative"

    def test_deforestation_impact_on_carbon(
        self, forest_cover_time_series, biomass_data
    ):
        """Test how detected deforestation impacts carbon stock estimates."""
        from geo_infer_forest.core.forest_health import ForestHealthMonitor
        from geo_infer_forest.core.carbon_sequestration import (
            CarbonSequestrationModeler,
        )

        # Detect deforestation
        monitor = ForestHealthMonitor()
        deforestation = monitor.detect_deforestation(
            forest_cover_time_series, threshold=0.05
        )

        # Calculate carbon stock with and without deforestation masking
        modeler = CarbonSequestrationModeler()
        full_carbon = modeler.calculate_carbon_stock(biomass_data)

        # Zero out carbon in deforested areas
        deforest_mask = deforestation["deforestation"].astype(float)
        remaining_carbon = full_carbon * (1 - deforest_mask)

        # Remaining carbon should be less than full carbon
        assert float(remaining_carbon.sum()) < float(
            full_carbon.sum()
        ), "Deforestation should reduce total carbon stock"
