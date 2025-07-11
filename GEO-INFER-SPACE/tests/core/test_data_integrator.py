#!/usr/bin/env python3
"""
Tests for DataIntegrator
"""
import pytest
from geo_infer_space.core.data_integrator import DataIntegrator

class TestDataIntegrator:
    @pytest.fixture
    def integrator(self):
        sources = [{'name': 'test', 'path': 'test.geojson'}]
        return DataIntegrator(sources)
    
    def test_integrate_data(self, integrator):
        # Add mock file reading
        pass 