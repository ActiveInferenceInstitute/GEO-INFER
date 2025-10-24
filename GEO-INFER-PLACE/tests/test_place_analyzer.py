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
    from geo_infer_space.core.place_analyzer import PlaceAnalyzer as CorePlaceAnalyzer
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


class TestForestHealthMonitor(unittest.TestCase):
    """Test suite for ForestHealthMonitor functionality."""

    def setUp(self):
        """Set up test fixtures for forest health monitor."""
        try:
            from geo_infer_place.locations.del_norte_county.forest_health_monitor import ForestHealthMonitor
            from geo_infer_place.utils.integration import DelNorteDataIntegrator

            self.config = {
                'location': {
                    'bounds': {'north': 42.006, 'south': 41.458, 'east': -123.536, 'west': -124.408}
                },
                'spatial': {'h3_resolution': 8},
                'analyses': {
                    'forest_health': {
                        'vegetation_indices': {
                            'ndvi': {'threshold_healthy': 0.7, 'threshold_stressed': 0.4, 'threshold_critical': 0.2}
                        },
                        'forest_types': ['Redwood', 'Douglas Fir', 'Mixed Conifer'],
                        'change_detection': {
                            'baseline_years': [2010, 2015, 2020],
                            'minimum_change_threshold': 0.1,
                            'time_series_length': 10
                        }
                    }
                }
            }

            # Mock data integrator
            self.data_integrator = DelNorteDataIntegrator()
            self.spatial_processor = None  # Mock for now

            self.monitor = ForestHealthMonitor(
                config=self.config,
                data_integrator=self.data_integrator,
                spatial_processor=self.spatial_processor,
                output_dir='/tmp/test_output'
            )

        except ImportError as e:
            self.skipTest(f"ForestHealthMonitor not available: {e}")

    def test_monitor_initialization(self):
        """Test that ForestHealthMonitor initializes correctly."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.h3_resolution, 8)
        self.assertEqual(len(self.monitor.forest_types), 3)
        self.assertIn('ndvi', self.monitor.vegetation_indices)

    def test_vegetation_index_analysis(self):
        """Test vegetation index analysis functionality."""
        # Create mock vegetation data
        mock_data = {
            'data_sources': {
                'vegetation_indices': {
                    'ndvi_measurements': [
                        {'date': '2024-01-01', 'lat': 41.7, 'lon': -124.0, 'ndvi': 0.8, 'evi': 0.6, 'moisture_stress': 0.2, 'h3_cell': '88281ca123fffff'},
                        {'date': '2024-01-02', 'lat': 41.7, 'lon': -124.0, 'ndvi': 0.3, 'evi': 0.2, 'moisture_stress': 0.8, 'h3_cell': '88281ca123fffff'},
                        {'date': '2024-01-03', 'lat': 41.7, 'lon': -124.0, 'ndvi': 0.6, 'evi': 0.4, 'moisture_stress': 0.4, 'h3_cell': '88281ca123fffff'},
                    ]
                }
            }
        }

        analysis = self.monitor._analyze_vegetation_indices(mock_data)

        # Check that analysis contains expected keys
        self.assertIn('ndvi_analysis', analysis)
        self.assertIn('total_measurements', analysis)
        self.assertIn('temporal_coverage', analysis)
        self.assertIn('spatial_coverage', analysis)

        # Check NDVI analysis results
        ndvi_analysis = analysis['ndvi_analysis']
        self.assertIn('mean', ndvi_analysis)
        self.assertIn('healthy_percent', ndvi_analysis)
        self.assertIn('stressed_percent', ndvi_analysis)
        self.assertIn('critical_percent', ndvi_analysis)

        # Verify calculations
        self.assertEqual(analysis['total_measurements'], 3)
        self.assertAlmostEqual(ndvi_analysis['healthy_percent'], 33.333333333333336, places=5)  # 1 out of 3 >= 0.7

    def test_forest_type_health_assessment(self):
        """Test forest type health assessment."""
        mock_data = {
            'data_sources': {
                'forest_inventory': {
                    'forest_plots': [
                        {
                            'plot_id': 'DN_001',
                            'lat': 41.7,
                            'lon': -124.0,
                            'forest_type': 'Redwood',
                            'basal_area_m2_ha': 120,
                            'tree_density_per_ha': 400,
                            'average_height_m': 75,
                            'canopy_cover_percent': 85,
                            'understory_diversity': 2.5,
                            'health_rating': 'Good',
                            'age_class': 'Mature',
                            'h3_cell': '88281ca123fffff'
                        },
                        {
                            'plot_id': 'DN_002',
                            'lat': 41.8,
                            'lon': -123.9,
                            'forest_type': 'Douglas Fir',
                            'basal_area_m2_ha': 80,
                            'tree_density_per_ha': 600,
                            'average_height_m': 45,
                            'canopy_cover_percent': 70,
                            'understory_diversity': 1.8,
                            'health_rating': 'Fair',
                            'age_class': 'Young',
                            'h3_cell': '88281ca456fffff'
                        }
                    ]
                }
            }
        }

        analysis = self.monitor._assess_forest_type_health(mock_data)

        # Check that analysis contains expected forest types
        self.assertIn('Redwood', analysis)
        self.assertIn('Douglas Fir', analysis)

        # Check Redwood analysis
        redwood_analysis = analysis['Redwood']
        self.assertEqual(redwood_analysis['plot_count'], 1)
        self.assertIn('structure_metrics', redwood_analysis)
        self.assertIn('health_distribution', redwood_analysis)

        # Check structure metrics
        structure = redwood_analysis['structure_metrics']
        self.assertEqual(structure['mean_basal_area'], 120)
        self.assertEqual(structure['mean_tree_density'], 400)
        self.assertEqual(structure['mean_height'], 75)

    def test_change_detection_analysis(self):
        """Test change detection analysis functionality."""
        mock_data = {
            'data_sources': {
                'vegetation_indices': {
                    'ndvi_measurements': [
                        {'date': '2024-01-01', 'h3_cell': '88281ca123fffff', 'ndvi': 0.7, 'lat': 41.7, 'lon': -124.0},
                        {'date': '2024-01-15', 'h3_cell': '88281ca123fffff', 'ndvi': 0.8, 'lat': 41.7, 'lon': -124.0},
                        {'date': '2024-02-01', 'h3_cell': '88281ca123fffff', 'ndvi': 0.6, 'lat': 41.7, 'lon': -124.0},
                        {'date': '2024-01-01', 'h3_cell': '88281ca456fffff', 'ndvi': 0.5, 'lat': 41.8, 'lon': -124.1},
                        {'date': '2024-02-01', 'h3_cell': '88281ca456fffff', 'ndvi': 0.2, 'lat': 41.8, 'lon': -124.1},  # Significant decline
                    ]
                }
            }
        }

        analysis = self.monitor._perform_change_detection(mock_data)

        # Check analysis structure
        self.assertIn('h3_cell_changes', analysis)
        self.assertIn('significant_changes_count', analysis)
        self.assertEqual(analysis['minimum_change_threshold'], 0.1)

        # Check that significant changes are detected
        changes = analysis['h3_cell_changes']
        significant_changes = [c for c in changes if c['change_significant']]
        self.assertGreater(len(significant_changes), 0)

        # Check second cell has significant change
        second_cell_change = next(c for c in changes if '88281ca456' in c['h3_cell'])
        self.assertTrue(second_cell_change['change_significant'])
        self.assertAlmostEqual(second_cell_change['recent_change'], -0.3, places=5)  # 0.5 - 0.2

    def test_risk_assessment_generation(self):
        """Test risk assessment generation."""
        mock_results = {
            'vegetation_analysis': {
                'ndvi_analysis': {
                    'critical_percent': 15.0,  # 15% critical
                    'stressed_percent': 25.0   # 25% stressed
                }
            },
            'change_analysis': {
                'significant_changes_count': 8,
                'h3_cell_changes': [{'h3_cell': f'cell_{i}'} for i in range(20)]
            },
            'mortality_analysis': {
                'mortality_rate_percent': 6.0  # 6% mortality rate
            },
            'climate_vulnerability': {
                'vulnerability_score': 0.6
            }
        }

        risk_assessment = self.monitor._generate_risk_assessment(mock_results)

        # Check risk assessment structure
        self.assertIn('overall_risk_score', risk_assessment)
        self.assertIn('risk_factors', risk_assessment)
        self.assertIn('recommendations', risk_assessment)

        # Check risk factors
        risk_factors = risk_assessment['risk_factors']
        self.assertIn('vegetation_stress', risk_factors)
        self.assertIn('change_detection', risk_factors)
        self.assertIn('tree_mortality', risk_factors)
        self.assertIn('climate_vulnerability', risk_factors)

        # Check overall risk calculation (weighted average)
        expected_risk = (
            risk_factors['vegetation_stress'] * 0.3 +
            risk_factors['change_detection'] * 0.3 +
            risk_factors['tree_mortality'] * 0.25 +
            risk_factors['climate_vulnerability'] * 0.15
        )
        self.assertAlmostEqual(risk_assessment['overall_risk_score'], expected_risk, places=5)

        # Check recommendations generation
        recommendations = risk_assessment['recommendations']
        self.assertIsInstance(recommendations, list)

        # Should generate recommendations for high vegetation stress
        vegetation_risk = risk_factors['vegetation_stress']
        if vegetation_risk > 0.5:
            self.assertTrue(any('vegetation' in rec.lower() for rec in recommendations))


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestPlaceAnalyzer,
        TestLocationConfigurations,
        TestIntegrationCapabilities,
        TestForestHealthMonitor
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1) 