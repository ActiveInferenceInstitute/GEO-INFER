"""
Unit tests for hydrological modeling.
"""

import pytest
from geo_infer_water.core.hydrology import HydrologicalModeler


class TestHydrologicalModeler:
    """Test suite for HydrologicalModeler."""
    
    def test_initialization(self):
        """Test modeler initialization."""
        modeler = HydrologicalModeler()
        assert modeler is not None
    
    def test_water_balance_calculation(self):
        """Test water balance calculation."""
        modeler = HydrologicalModeler()
        result = modeler.calculate_water_balance(
            precipitation=100.0,
            evapotranspiration=50.0,
            runoff=30.0
        )
        assert result is not None

