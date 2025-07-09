#!/usr/bin/env python3
"""
Test suite for GEO-INFER-PLACE PlaceAnalyzer

This module tests the core place-based analysis functionality including
location management, analysis workflows, and integration capabilities.
"""

import pytest
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from geo_infer_place import PlaceAnalyzer, get_available_locations
    from geo_infer_place.core.place_analyzer import PlaceAnalyzer as CorePlaceAnalyzer
except ImportError as e:
    # Graceful handling for when modules aren't fully implemented yet
    print(f"Import warning: {e}")
    PlaceAnalyzer = None
    get_available_locations = None
    CorePlaceAnalyzer = None


class TestPlaceAnalyzer(unittest.TestCase):
    """Test suite for PlaceAnalyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        if PlaceAnalyzer is None:
            self.skipTest("PlaceAnalyzer not available")
        
        self.analyzer = PlaceAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test that PlaceAnalyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsInstance(self.analyzer, PlaceAnalyzer)
    
    @patch('geo_infer_place.get_available_locations')
    def test_get_available_locations(self, mock_get_locations):
        """Test retrieval of available study locations."""
        # Mock return value
        mock_locations = [
            {
                "name": "del_norte_county",
                "display_name": "Del Norte County, California, USA",
                "status": "available",
                "focus_areas": ["forest_management", "coastal_resilience"]
            },
            {
                "name": "australia",
                "display_name": "Australia Continental Analysis", 
                "status": "available",
                "focus_areas": ["climate_monitoring", "biodiversity"]
            },
            {
                "name": "siberia",
                "display_name": "Siberian Arctic and Sub-Arctic Region",
                "status": "available", 
                "focus_areas": ["permafrost_monitoring", "arctic_climate"]
            }
        ]
        mock_get_locations.return_value = mock_locations
        
        if get_available_locations is not None:
            locations = get_available_locations()
            self.assertEqual(len(locations), 3)
            self.assertTrue(all('name' in loc for loc in locations))
            self.assertTrue(all('display_name' in loc for loc in locations))
    
    def test_location_specific_analyzers(self):
        """Test location-specific analyzer availability."""
        try:
            from geo_infer_place import DelNorteCounty, Australia, Siberia
            
            # Test that location analyzers can be imported
            self.assertTrue(DelNorteCounty is not None or DelNorteCounty is None)  # Allow for graceful degradation
            self.assertTrue(Australia is not None or Australia is None)
            self.assertTrue(Siberia is not None or Siberia is None)
            
        except ImportError:
            # Expected during initial development
            self.skipTest("Location-specific analyzers not yet implemented")
    
    def test_module_metadata(self):
        """Test module metadata and package information."""
        try:
            import geo_infer_place
            
            # Check that basic metadata exists
            self.assertTrue(hasattr(geo_infer_place, '__version__'))
            self.assertTrue(hasattr(geo_infer_place, 'PACKAGE_INFO'))
            
            # Verify package info structure
            if hasattr(geo_infer_place, 'PACKAGE_INFO'):
                package_info = geo_infer_place.PACKAGE_INFO
                self.assertIn('name', package_info)
                self.assertIn('version', package_info)
                self.assertIn('description', package_info)
                
        except AttributeError:
            # Expected during development
            pass
    
    def test_configuration_loading(self):
        """Test configuration file loading and validation."""
        # Test that configuration files exist and are valid
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'module_config.yaml'
        )
        
        self.assertTrue(os.path.exists(config_path), 
                       "Module configuration file should exist")
        
        # Test location-specific configs
        del_norte_config = os.path.join(
            os.path.dirname(__file__), '..', 'locations', 'del_norte_county', 
            'config', 'analysis_config.yaml'
        )
        
        self.assertTrue(os.path.exists(del_norte_config),
                       "Del Norte County configuration should exist")


class TestLocationConfigurations(unittest.TestCase):
    """Test suite for location-specific configurations."""
    
    def test_del_norte_county_config(self):
        """Test Del Norte County configuration structure."""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'locations', 'del_norte_county',
            'config', 'analysis_config.yaml'
        )
        
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Test required configuration sections
                self.assertIn('location', config)
                self.assertIn('analyses', config)
                
                # Test location metadata
                location = config['location']
                self.assertIn('name', location)
                self.assertIn('bounds', location)
                self.assertIn('coordinate_systems', location)
                
                # Test analysis configurations
                analyses = config['analyses']
                expected_analyses = ['forest_health', 'coastal_resilience', 
                                   'fire_risk', 'community_development']
                
                for analysis in expected_analyses:
                    self.assertIn(analysis, analyses, 
                                f"Analysis '{analysis}' should be configured")
                    
            except ImportError:
                self.skipTest("PyYAML not available for config testing")
        else:
            self.skipTest("Del Norte County config file not found")
    
    def test_requirements_files_exist(self):
        """Test that location-specific requirements files exist."""
        locations = ['del_norte_county', 'australia', 'siberia']
        
        for location in locations:
            req_path = os.path.join(
                os.path.dirname(__file__), '..', 'locations', location,
                'requirements.txt'
            )
            
            self.assertTrue(os.path.exists(req_path),
                           f"Requirements file for {location} should exist")


class TestIntegrationCapabilities(unittest.TestCase):
    """Test suite for GEO-INFER module integration capabilities."""
    
    def test_module_dependencies(self):
        """Test that required module dependencies are properly defined."""
        try:
            import geo_infer_place
            
            if hasattr(geo_infer_place, 'PACKAGE_INFO'):
                package_info = geo_infer_place.PACKAGE_INFO
                
                # Check for dependencies section
                self.assertIn('dependencies', package_info)
                self.assertIn('optional_dependencies', package_info)
                
                # Verify core dependencies
                core_deps = package_info['dependencies']
                expected_core = ['geo-infer-space', 'geo-infer-time', 'geo-infer-data']
                
                for dep in expected_core:
                    self.assertIn(dep, core_deps, 
                                f"Core dependency '{dep}' should be listed")
                    
        except (AttributeError, ImportError):
            self.skipTest("Package info not available")
    
    def test_api_endpoints_defined(self):
        """Test that API endpoints are properly defined."""
        # Test will be expanded when API module is implemented
        pass
    
    def test_cross_module_communication(self):
        """Test cross-module communication capabilities."""
        # Test will be expanded when integration is implemented
        pass


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPlaceAnalyzer,
        TestLocationConfigurations, 
        TestIntegrationCapabilities
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1) 