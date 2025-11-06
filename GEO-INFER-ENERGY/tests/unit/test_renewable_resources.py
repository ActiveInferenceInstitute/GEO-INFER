"""
Unit tests for renewable resource assessment.
"""

import pytest
import numpy as np
from geo_infer_energy.core.renewable_resources import RenewableResourceAssessor


class TestRenewableResourceAssessor:
    """Test suite for RenewableResourceAssessor."""
    
    def test_initialization(self):
        """Test assessor initialization."""
        assessor = RenewableResourceAssessor()
        assert assessor is not None
    
    def test_solar_potential_assessment(self):
        """Test solar potential assessment."""
        assessor = RenewableResourceAssessor()
        # Mock location data
        latitude = 37.7749
        longitude = -122.4194
        
        result = assessor.assess_solar_potential(latitude, longitude)
        assert result is not None
        assert 'potential' in result or 'capacity' in result or isinstance(result, dict)
    
    def test_wind_potential_assessment(self):
        """Test wind potential assessment."""
        assessor = RenewableResourceAssessor()
        latitude = 37.7749
        longitude = -122.4194
        
        result = assessor.assess_wind_potential(latitude, longitude)
        assert result is not None

