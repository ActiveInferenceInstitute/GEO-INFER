#!/usr/bin/env python3
"""
Setup and Configuration Manager for Cascadia Analysis Framework

This module handles all setup, configuration, and initialization tasks
for the Cascadia agricultural analysis framework.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from datetime import datetime

# Import the necessary components from the main module
try:
    from geo_infer_space.core.spatial_processor import SpatialProcessor
    from geo_infer_space.core.data_integrator import DataIntegrator
    from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine
    from geo_infer_space.utils.config_loader import LocationBounds
    SPACE_CORE_AVAILABLE = True
except ImportError:
    SPACE_CORE_AVAILABLE = False
    # Create placeholder classes
    class SpatialProcessor:
        def __init__(self, *args, **kwargs): pass
        def calculate_spatial_correlation(self, scores1, scores2): 
            try:
                import numpy as np
                common_hexagons = set(scores1.keys()) & set(scores2.keys())
                if len(common_hexagons) < 2:
                    return 0.0
                values1 = [scores1[h] for h in common_hexagons]
                values2 = [scores2[h] for h in common_hexagons]
                correlation = np.corrcoef(values1, values2)[0, 1]
                return correlation if not np.isnan(correlation) else 0.0
            except Exception:
                return 0.0
    
    class DataIntegrator:
        def __init__(self, sources):
            self.sources = sources
            self.integrated_data = None
    
    class InteractiveVisualizationEngine:
        def __init__(self, *args, **kwargs): pass
        def create_comprehensive_dashboard(self, *args, **kwargs): return "dashboard_not_available.html"
    
    class LocationBounds:
        def __init__(self, north=0, south=0, east=0, west=0):
            self.north = north
            self.south = south
            self.east = east
            self.west = west

def setup_logging(verbose: bool = False, output_dir: str = '.') -> None:
    """Setup logging configuration with enhanced SPACE integration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    log_filename = Path(output_dir) / f'cascadia_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    # Remove all existing handlers before configuring logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_filename)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Enhanced Cascadia Analysis Framework initialized with SPACE integration")
    logger.info(f"Log file: {log_filename}")

def check_dependencies() -> bool:
    """Check and report on all dependencies with enhanced SPACE integration"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Checking dependencies with enhanced SPACE integration...")
    
    # Check core dependencies
    required_packages = [
        'numpy', 'pandas', 'geopandas', 'folium', 'h3', 'shapely',
        'requests', 'yaml', 'branca'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package}")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages: uv pip install " + " ".join(missing_packages))
        return False
    
    # Check SPACE integration
    try:
        from geo_infer_space.osc_geo import check_integration_status
        status = check_integration_status()
        if hasattr(status, 'status') and status.status == 'ready':
            logger.info("✅ SPACE integration ready")
        else:
            logger.warning("⚠️ SPACE integration needs setup")
            logger.info("Run: python -c 'from geo_infer_space.osc_geo import setup_osc_geo; setup_osc_geo()'")
    except Exception as e:
        logger.warning(f"⚠️ SPACE integration not available: {e}")
    
    logger.info("✅ Dependency check complete")
    return True

def setup_spatial_processor() -> SpatialProcessor:
    """Initialize SPACE spatial processor with Cascadia configuration"""
    logger = logging.getLogger(__name__)
    logger.info("Initializing SPACE spatial processor...")
    
    try:
        processor = SpatialProcessor()
        logger.info("✅ Spatial processor initialized successfully")
        return processor
    except Exception as e:
        logger.error(f"❌ Failed to initialize spatial processor: {e}")
        raise

def setup_data_integrator() -> DataIntegrator:
    """Initialize SPACE data integrator for Cascadia data sources"""
    logger = logging.getLogger(__name__)
    logger.info("Initializing SPACE data integrator...")
    
    try:
        # Define Cascadia data sources
        sources = [
            {'name': 'zoning', 'path': 'data/zoning.geojson'},
            {'name': 'current_use', 'path': 'data/current_use.geojson'},
            {'name': 'water_rights', 'path': 'data/water_rights.geojson'},
            {'name': 'surface_water', 'path': 'data/surface_water.geojson'},
            {'name': 'ground_water', 'path': 'data/ground_water.geojson'},
            {'name': 'power_source', 'path': 'data/power_source.geojson'},
            {'name': 'ownership', 'path': 'data/ownership.geojson'},
            {'name': 'improvements', 'path': 'data/improvements.geojson'}
        ]
        
        integrator = DataIntegrator(sources)
        logger.info("✅ Data integrator initialized successfully")
        return integrator
    except Exception as e:
        logger.error(f"❌ Failed to initialize data integrator: {e}")
        raise

def load_analysis_config() -> Dict[str, Any]:
    """Load analysis configuration with SPACE integration"""
    config_path = Path('config/analysis_config.yaml')
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger = logging.getLogger(__name__)
        logger.info(f"Loaded analysis configuration from {config_path}")
        return config
    else:
        # Enhanced default configuration with SPACE integration
        default_config = {
            'analysis_settings': {
                'active_modules': ['zoning', 'current_use', 'surface_water', 'ground_water', 'water_rights'],
                'target_counties': {
                    'CA': ['all'],
                    'OR': ['all']
                },
                'h3_resolution': 8,
                'enhanced_visualization': True,
                'real_time_integration': False,
                'spatial_analysis': {
                    'buffer_distance': 1000,  # meters
                    'proximity_analysis': True,
                    'multi_overlay': True,
                    'correlation_analysis': True,
                    'hotspot_detection': True
                },
                'data_sources': {
                    'caching_enabled': True,
                    'cache_duration': 86400,  # 24 hours
                    'api_rate_limits': {
                        'requests_per_minute': 60,
                        'requests_per_hour': 1000
                    }
                },
                'visualization': {
                    'base_map': 'CartoDB positron',
                    'default_zoom': 7,
                    'center': [44.0, -120.5],  # Center of Oregon
                    'layers': {
                        'zoning': {'color': '#1f77b4', 'opacity': 0.6},
                        'current_use': {'color': '#2ca02c', 'opacity': 0.6},
                        'water': {'color': '#d62728', 'opacity': 0.6},
                        'ownership': {'color': '#ff7f0e', 'opacity': 0.6},
                        'redevelopment': {'color': '#9467bd', 'opacity': 0.7}
                    }
                }
            }
        }
        logger = logging.getLogger(__name__)
        logger.info("Using enhanced default configuration with SPACE integration")
        return default_config

def setup_visualization_engine(output_dir: Path) -> InteractiveVisualizationEngine:
    """Initialize SPACE visualization engine with Cascadia configuration"""
    logger = logging.getLogger(__name__)
    logger.info("Initializing SPACE visualization engine...")
    
    try:
        # Cascadia-specific location configuration
        location_config = {
            'name': 'Cascadia',
            'bounds': LocationBounds(
                north=46.3,  # Northern Oregon
                south=32.5,  # Southern California
                east=-114.0, # Eastern boundary
                west=-124.8  # Western boundary
            ),
            'h3_resolution': 8,
            'analysis_types': ['agricultural', 'water', 'infrastructure', 'ownership'],
            'visualization': {
                'base_map': 'CartoDB positron',
                'default_zoom': 7,
                'center': [44.0, -120.5],  # Center of Oregon
                'layers': {
                    'zoning': {'color': '#1f77b4', 'opacity': 0.6},
                    'current_use': {'color': '#2ca02c', 'opacity': 0.6},
                    'water': {'color': '#d62728', 'opacity': 0.6},
                    'ownership': {'color': '#ff7f0e', 'opacity': 0.6},
                    'redevelopment': {'color': '#9467bd', 'opacity': 0.7}
                }
            }
        }
        
        engine = InteractiveVisualizationEngine(
            location_config=location_config,
            output_dir=output_dir,
            h3_resolution=8
        )
        logger.info("✅ Visualization engine initialized successfully")
        return engine
    except Exception as e:
        logger.error(f"❌ Failed to initialize visualization engine: {e}")
        raise 