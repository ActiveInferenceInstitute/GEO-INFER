"""
Unit tests for forest inventory.
"""

import numpy as np
import xarray as xr

from geo_infer_forest.core.forest_inventory import ForestInventory


class TestForestInventory:
    """Test suite for ForestInventory."""

    def test_initialization(self):
        """Test inventory initialization."""
        inventory = ForestInventory()
        assert inventory is not None

    def test_estimate_biomass(self):
        """Test biomass estimation."""
        inventory = ForestInventory()
        forest_cover = xr.DataArray(
            np.array([[80.0, 60.0], [40.0, 90.0]]),
            dims=("y", "x"),
        )
        result = inventory.estimate_biomass(forest_cover)
        assert result is not None
        assert float(result.max()) > 0

    def test_estimate_biomass_all_zero_density_finite(self):
        """All-zero tree density must not propagate NaN into biomass."""
        inventory = ForestInventory()
        forest_cover = xr.DataArray(np.full((3, 3), 50.0), dims=("y", "x"))
        tree_density = xr.DataArray(np.zeros((3, 3)), dims=("y", "x"))
        result = inventory.estimate_biomass(forest_cover, tree_density=tree_density)
        assert np.isfinite(result.values).all()
        assert float(result.max()) > 0
