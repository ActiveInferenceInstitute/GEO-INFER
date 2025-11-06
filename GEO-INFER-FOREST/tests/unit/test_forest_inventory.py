"""
Unit tests for forest inventory.
"""

import pytest
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
        result = inventory.estimate_biomass(
            tree_density=100,  # trees per hectare
            average_dbh=30.0,  # cm
            height=20.0  # meters
        )
        assert result is not None

