#!/usr/bin/env python3
"""
Cascadia Agricultural Analysis Framework
Main entry point for comprehensive agricultural land analysis.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Import utility functions
from utils.setup_manager import setup_logging, load_analysis_config
from utils.data_processor import (
    create_shared_backend, 
    initialize_modules, 
    validate_data_acquisition,
    export_results
)
from utils.analysis_engine import run_comprehensive_analysis
from utils.reporting_engine import generate_analysis_report

# Import enhanced modules for H3 geospatial data fusion
from utils.enhanced_data_manager import create_enhanced_data_manager
from utils.enhanced_h3_fusion import create_enhanced_h3_fusion

def parse_counties(counties_str: str) -> dict:
    """Parse counties string into dictionary format"""
    counties_dict = {}
    if counties_str and counties_str != 'all':
        for county_pair in counties_str.split(','):
            if ':' in county_pair:
                state, county = county_pair.strip().split(':', 1)
                if state not in counties_dict:
                    counties_dict[state] = []
                counties_dict[state].append(county)
            else:
                # Default to CA if no state specified
                if 'CA' not in counties_dict:
                    counties_dict['CA'] = []
                counties_dict['CA'].append(county_pair.strip())
    else:
        counties_dict = {'CA': ['all'], 'OR': ['all']}
    return counties_dict

def initialize_analysis(args):
    """Initialize the analysis with backend and modules"""
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = load_analysis_config()
    
    # Parse counties and modules
    counties_dict = parse_counties(args.counties)
    active_modules = args.modules.split(',') if args.modules else []
    
    logger.info(f"Target counties: {counties_dict}")
    logger.info(f"Active modules: {active_modules}")
    
    # Create shared backend
    osc_repo_path = "/home/trim/Documents/GitHub/GEO-INFER/GEO-INFER-SPACE/repo"
    shared_backend = create_shared_backend(args.h3_resolution, counties_dict, Path(args.output_dir), osc_repo_path)
    
    # Initialize enhanced data manager
    data_manager = create_enhanced_data_manager(
        base_data_dir=Path(args.output_dir) / "data",
        h3_resolution=args.h3_resolution
    )
    
    # Initialize enhanced H3 fusion engine
    h3_fusion = create_enhanced_h3_fusion(
        h3_resolution=args.h3_resolution,
        enable_spatial_analysis=args.spatial_analysis
    )
    
    # Validate H3 operations
    h3_validation = h3_fusion.validate_h3_operations()
    logger.info(f"H3 validation result: {h3_validation}")
    
    # Initialize modules with enhanced data management
    modules = initialize_modules_with_enhanced_data_management(
        active_modules, shared_backend, data_manager, h3_fusion, osc_repo_path
    )
    
    if not modules:
        logger.error("❌ No modules could be initialized. Exiting.")
        sys.exit(1)
    
    return shared_backend, modules, data_manager, h3_fusion

def initialize_modules_with_enhanced_data_management(active_modules, shared_backend, data_manager, h3_fusion, osc_repo_path):
    """Initialize modules with enhanced data management and H3 fusion"""
    logger = logging.getLogger(__name__)
    modules = {}
    
    # Import all the specialized modules from the 'cascadia' location
    try:
        from zoning.geo_infer_zoning import GeoInferZoning
        ZONING_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Zoning module not available: {e}")
        ZONING_AVAILABLE = False
        GeoInferZoning = None

    try:
        from current_use.geo_infer_current_use import GeoInferCurrentUse
        CURRENT_USE_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Current use module not available: {e}")
        CURRENT_USE_AVAILABLE = False
        GeoInferCurrentUse = None

    try:
        from ownership.geo_infer_ownership import GeoInferOwnership
        OWNERSHIP_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Ownership module not available: {e}")
        OWNERSHIP_AVAILABLE = False
        GeoInferOwnership = None

    try:
        from improvements.geo_infer_improvements import GeoInferImprovements
        IMPROVEMENTS_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Improvements module not available: {e}")
        IMPROVEMENTS_AVAILABLE = False
        GeoInferImprovements = None
    
    # Initialize available modules using the shared backend with enhanced data management
    if 'zoning' in active_modules and ZONING_AVAILABLE:
        try:
            modules['zoning'] = GeoInferZoning(shared_backend)
            # Integrate enhanced data management
            modules['zoning'].data_manager = data_manager
            modules['zoning'].h3_fusion = h3_fusion
            logger.info("✅ Zoning module initialized with enhanced data management")
        except Exception as e:
            logger.error(f"❌ Failed to initialize zoning module: {e}")
    
    if 'current_use' in active_modules and CURRENT_USE_AVAILABLE:
        try:
            modules['current_use'] = GeoInferCurrentUse(shared_backend)
            # Integrate enhanced data management
            modules['current_use'].data_manager = data_manager
            modules['current_use'].h3_fusion = h3_fusion
            logger.info("✅ Current use module initialized with enhanced data management")
        except Exception as e:
            logger.error(f"❌ Failed to initialize current use module: {e}")
    
    if 'ownership' in active_modules and OWNERSHIP_AVAILABLE:
        try:
            modules['ownership'] = GeoInferOwnership(shared_backend)
            # Integrate enhanced data management
            modules['ownership'].data_manager = data_manager
            modules['ownership'].h3_fusion = h3_fusion
            logger.info("✅ Ownership module initialized with enhanced data management")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ownership module: {e}")
    
    if 'improvements' in active_modules and IMPROVEMENTS_AVAILABLE:
        try:
            modules['improvements'] = GeoInferImprovements(shared_backend)
            # Integrate enhanced data management
            modules['improvements'].data_manager = data_manager
            modules['improvements'].h3_fusion = h3_fusion
            logger.info("✅ Improvements module initialized with enhanced data management")
        except Exception as e:
            logger.error(f"❌ Failed to initialize improvements module: {e}")
    
    if not modules:
        logger.error("❌ No modules could be initialized.")
        return {}
    
    # Update the shared backend with initialized modules
    shared_backend.modules = modules
    logger.info(f"✅ Updated shared backend with {len(modules)} active modules")
    
    return modules

def generate_reports(summary, output_dir, spatial_analysis=False):
    """Generate analysis reports"""
    logger = logging.getLogger(__name__)
    
    # Generate Markdown report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(output_dir) / f"cascadia_analysis_report_{timestamp}.md"
    generate_analysis_report(summary, report_path)
    logger.info(f"📋 Analysis report: {report_path}")

"""
Cascadian Agricultural Land Analysis Framework - Enhanced Main Integration Script

This script orchestrates the complete agricultural land analysis across the 
Cascadian bioregion (Northern California + Oregon) using the unified H3-indexed
backend and all 8 specialized data modules, with maximum integration of 
GEO-INFER-SPACE methods and capabilities.

Enhanced Features:
- Full SPACE module integration (H3 utilities, OSC tools, visualization engines)
- Advanced multi-layer visualization with California demo patterns
- Comprehensive data processing with SPACE utilities
- Enhanced reporting and diagnostics
- Real-time data integration capabilities
- Spatial analysis and correlation features
- Advanced dashboard generation
- Enhanced H3 v4 geospatial data fusion
- Reproducible data module structure with intelligent caching

Usage:
    python cascadia_main.py [options]

Options:
    --resolution: H3 resolution level (default: 8)
    --output-dir: Output directory for results (default: ./output)
    --export-format: Export format (geojson, csv, json) (default: geojson)
    --counties: Comma-separated list of counties to analyze (default: all)
    --modules: Comma-separated list of modules to run (default: all)
    --verbose: Enable verbose logging
    --check-deps: Check and install dependencies
    --enhanced-viz: Enable enhanced visualization features
    --real-time: Enable real-time data integration
    --spatial-analysis: Enable advanced spatial analysis features
    --generate-dashboard: Generate interactive dashboard
    --force-refresh: Force refresh of cached data
    --validate-h3: Validate H3 operations and API usage
"""

import sys
import os
from pathlib import Path

# --- Robust Path Setup ---
# This setup allows for imports from the geo_infer_place and geo_infer_space modules.
try:
    # Use os.path for more explicit path construction
    cascadian_dir = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.abspath(os.path.join(cascadian_dir, '..', '..', '..'))

    # --- FIX: Set OSC repository path environment variable early ---
    # Use the correct absolute path to GEO-INFER-SPACE/repo as confirmed by user
    osc_repo_path = "/home/trim/Documents/GitHub/GEO-INFER/GEO-INFER-SPACE/repo"
    os.environ['OSC_REPOS_DIR'] = osc_repo_path
    print(f"INFO: Set OSC_REPOS_DIR to {osc_repo_path}")
    # --- END FIX ---

    # Define the 'src' paths for the required modules
    place_src_path = os.path.join(project_root, 'GEO-INFER-PLACE', 'src')
    space_src_path = os.path.join(project_root, 'GEO-INFER-SPACE', 'src')

    # Add the local directory for specialized modules like 'zoning'
    if cascadian_dir not in sys.path:
        sys.path.insert(0, cascadian_dir)

    # Add the src directories to the path
    for p in [place_src_path, space_src_path]:
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)
            print(f"INFO: Successfully added {p} to sys.path")
        elif not os.path.isdir(p):
            print(f"WARNING: Required src path not found: {p}")

except Exception as e:
    print(f"CRITICAL: Could not set up paths: {e}. Please ensure you are running from the 'GEO-INFER-PLACE/locations/cascadia' directory")
    sys.exit(1)
# --- End Path Setup ---

import argparse
import json
import logging
from typing import List, Dict, Any, Optional
import yaml
from datetime import datetime
import traceback
import time
from tqdm import tqdm
import numpy as np

# Import utils modules
from utils.setup_manager import (
    setup_logging,
    check_dependencies,
    setup_spatial_processor,
    setup_data_integrator,
    load_analysis_config,
    setup_visualization_engine
)
from utils.analysis_engine import (
    perform_enhanced_spatial_analysis,
    run_comprehensive_analysis
)
from utils.reporting_engine import (
    generate_spatial_analysis_report,
    generate_enhanced_dashboard,
    generate_analysis_report
)
from utils.data_processor import (
    initialize_modules,
    create_shared_backend,
    export_results,
    validate_data_acquisition
)

# Import enhanced modules
from utils.enhanced_data_manager import create_enhanced_data_manager
from utils.enhanced_h3_fusion import create_enhanced_h3_fusion

# Existing imports for SPACE and PLACE
try:
    from geo_infer_space.osc_geo import (
        setup_osc_geo,
        create_h3_data_loader,
        create_h3_grid_manager,
        load_data_to_h3_grid,
        check_integration_status,
        run_diagnostics
    )
    SPACE_OSC_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE OSC integration not available: {e}")
    SPACE_OSC_AVAILABLE = False
    # Create placeholder functions
    def setup_osc_geo(*args, **kwargs): return None
    def create_h3_data_loader(*args, **kwargs): return None
    def create_h3_grid_manager(*args, **kwargs): return None
    def load_data_to_h3_grid(*args, **kwargs): return None
    def check_integration_status(*args, **kwargs): return type('MockStatus', (), {'status': 'not_available'})()
    def run_diagnostics(*args, **kwargs): return "Diagnostics not available"

try:
    from geo_infer_space.osc_geo.utils import (
        cell_to_latlngjson,
        geojson_to_h3,
        check_repo_status,
        generate_summary
    )
    SPACE_UTILS_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE utils not available: {e}")
    SPACE_UTILS_AVAILABLE = False
    # Create placeholder functions
    def cell_to_latlngjson(*args, **kwargs): return {}
    def geojson_to_h3(*args, **kwargs): return {}
    def check_repo_status(*args, **kwargs): return "not_available"
    def generate_summary(*args, **kwargs): return "Summary not available"

try:
    from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine
    from geo_infer_space.core.spatial_processor import SpatialProcessor
    from geo_infer_space.core.data_integrator import DataIntegrator
    from geo_infer_space.core.api_clients import BaseAPIManager, GeneralGeoDataFetcher
    SPACE_CORE_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE core modules not available: {e}")
    SPACE_CORE_AVAILABLE = False
    # Create placeholder classes
    class InteractiveVisualizationEngine:
        def __init__(self, *args, **kwargs): pass
        def create_comprehensive_dashboard(self, *args, **kwargs): return "dashboard_not_available.html"
    
    class SpatialProcessor:
        def __init__(self, *args, **kwargs): pass
        def calculate_spatial_correlation(self, *args, **kwargs): return 0.0
    
    class DataIntegrator:
        def __init__(self, *args, **kwargs): pass
    
    class BaseAPIManager:
        def __init__(self, *args, **kwargs): pass
    
    class GeneralGeoDataFetcher:
        def __init__(self, *args, **kwargs): pass

try:
    from geo_infer_space.utils.config_loader import LocationConfigLoader, LocationBounds
    SPACE_CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE config loader not available: {e}")
    SPACE_CONFIG_AVAILABLE = False
    # Create placeholder classes
    class LocationConfigLoader:
        def __init__(self, *args, **kwargs): pass
    
    class LocationBounds:
        def __init__(self, north=0, south=0, east=0, west=0):
            self.north = north
            self.south = south
            self.east = east
            self.west = west

try:
    from geo_infer_space.utils.h3_utils import (
        latlng_to_cell,
        cell_to_latlng,
        cell_to_latlng_boundary,
        geo_to_cells,
        polygon_to_cells,
        grid_disk,
        grid_distance,
        cell_area,
        get_resolution,
        is_valid_cell,
        are_neighbor_cells
    )
    SPACE_H3_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE H3 utils not available: {e}")
    SPACE_H3_AVAILABLE = False
    # Create placeholder functions
    def latlng_to_cell(*args, **kwargs): return "0000000000000000"
    def cell_to_latlng(*args, **kwargs): return (0.0, 0.0)
    def cell_to_latlng_boundary(*args, **kwargs): return [(0.0, 0.0)] * 6
    def geo_to_cells(*args, **kwargs): return []
    def polygon_to_cells(*args, **kwargs): return []
    def grid_disk(*args, **kwargs): return []
    def grid_distance(*args, **kwargs): return 0
    def cell_area(*args, **kwargs): return 0.0
    def get_resolution(*args, **kwargs): return 8
    def is_valid_cell(*args, **kwargs): return True
    def are_neighbor_cells(*args, **kwargs): return False

# Import from the new core location
try:
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend
    PLACE_BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: PLACE backend not available: {e}")
    PLACE_BACKEND_AVAILABLE = False
    CascadianAgriculturalH3Backend = None

try:
    from geo_infer_space.core.unified_backend import NumpyEncoder
    SPACE_BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE backend not available: {e}")
    SPACE_BACKEND_AVAILABLE = False
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NumpyEncoder, self).default(obj)

try:
    from geo_infer_space.core.base_module import BaseAnalysisModule
    SPACE_BASE_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE base module not available: {e}")
    SPACE_BASE_AVAILABLE = False
    class BaseAnalysisModule:
        def __init__(self, *args, **kwargs): pass

# Import all the specialized modules from the 'cascadia' location
try:
    from zoning.geo_infer_zoning import GeoInferZoning
    ZONING_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Zoning module not available: {e}")
    ZONING_AVAILABLE = False
    GeoInferZoning = None

try:
    from current_use.geo_infer_current_use import GeoInferCurrentUse
    CURRENT_USE_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Current use module not available: {e}")
    CURRENT_USE_AVAILABLE = False
    GeoInferCurrentUse = None

try:
    from ownership.geo_infer_ownership import GeoInferOwnership
    OWNERSHIP_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Ownership module not available: {e}")
    OWNERSHIP_AVAILABLE = False
    GeoInferOwnership = None

try:
    from improvements.geo_infer_improvements import GeoInferImprovements
    IMPROVEMENTS_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Improvements module not available: {e}")
    IMPROVEMENTS_AVAILABLE = False
    GeoInferImprovements = None

# Add missing imports for enhanced reporting functions if they don't exist
try:
    from geo_infer_space.osc_geo.utils.enhanced_reporting import (
        generate_enhanced_status_report,
        generate_comprehensive_osc_report
    )
    ENHANCED_REPORTING_AVAILABLE = True
except ImportError:
    ENHANCED_REPORTING_AVAILABLE = False
    # Create placeholder functions if enhanced_reporting doesn't exist
    def generate_enhanced_status_report(*args, **kwargs):
        return "Enhanced reporting not available"
    
    def generate_comprehensive_osc_report(*args, **kwargs):
        return "Comprehensive reporting not available"

# Remove the large method definitions since they're now in utils

def parse_arguments():
    """Parse command line arguments for Cascadia analysis"""
    parser = argparse.ArgumentParser(
        description="Cascadia Agricultural Analysis Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis with default settings
  python3 cascadia_main.py
  
  # Analysis with custom H3 resolution and specific counties
  python3 cascadia_main.py --h3-resolution 8 --counties "CA:Del Norte,CA:Humboldt"
  
  # Analysis with spatial analysis and lightweight visualization
  python3 cascadia_main.py --spatial-analysis --lightweight-viz
  
  # Analysis with Datashader visualization (recommended for large datasets)
  python3 cascadia_main.py --datashader-viz
  
  # Analysis with Deepscatter visualization (web-based, lightweight)
  python3 cascadia_main.py --deepscatter-viz
  
  # Export in different formats
  python3 cascadia_main.py --export-format csv --verbose
  
  # Force refresh of cached data
  python3 cascadia_main.py --force-refresh --verbose
  
  # Validate H3 operations
  python3 cascadia_main.py --validate-h3
        """
    )
    
    # Core analysis parameters
    parser.add_argument(
        '--h3-resolution', 
        type=int, 
        default=8,
        help='H3 resolution for analysis (default: 8)'
    )
    
    parser.add_argument(
        '--counties',
        type=str,
        default="CA:Del Norte",
        help='Target counties in format "STATE:County,STATE:County" (default: CA:Del Norte)'
    )
    
    parser.add_argument(
        '--modules',
        type=str,
        default="zoning,current_use,ownership,improvements",
        help='Comma-separated list of modules to run (default: all modules)'
    )
    
    # Output and export options
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )
    
    parser.add_argument(
        '--export-format',
        type=str,
        choices=['geojson', 'csv', 'json'],
        default='geojson',
        help='Export format for unified data (default: geojson)'
    )
    
    # Visualization options
    parser.add_argument(
        '--generate-dashboard',
        action='store_true',
        help='Generate interactive dashboard (may be large and slow)'
    )
    
    parser.add_argument(
        '--lightweight-viz',
        action='store_true',
        help='Generate lightweight static visualizations (recommended)'
    )
    
    parser.add_argument(
        '--datashader-viz',
        action='store_true',
        help='Generate Datashader visualizations (best for large datasets)'
    )
    
    parser.add_argument(
        '--deepscatter-viz',
        action='store_true',
        help='Generate Deepscatter visualizations (web-based, lightweight)'
    )
    
    # Analysis options
    parser.add_argument(
        '--spatial-analysis',
        action='store_true',
        help='Perform enhanced spatial analysis'
    )
    
    parser.add_argument(
        '--skip-cache',
        action='store_true',
        help='Skip cache and regenerate all data'
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force refresh of cached data'
    )
    
    parser.add_argument(
        '--validate-h3',
        action='store_true',
        help='Validate H3 operations and API usage'
    )
    
    # Logging and debugging
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with detailed error reporting'
    )
    
    return parser.parse_args()

def main():
    """Main execution function for Cascadia analysis"""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else (logging.INFO if args.verbose else logging.WARNING)
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("🌲 Starting Cascadia Agricultural Analysis Framework")
    logger.info(f"📊 Analysis Parameters:")
    logger.info(f"   H3 Resolution: {args.h3_resolution}")
    logger.info(f"   Target Counties: {args.counties}")
    logger.info(f"   Active Modules: {args.modules}")
    logger.info(f"   Export Format: {args.export_format}")
    logger.info(f"   Output Directory: {args.output_dir}")
    
    # Visualization options
    viz_options = []
    if args.generate_dashboard:
        viz_options.append("Interactive Dashboard")
    if args.lightweight_viz:
        viz_options.append("Lightweight Static Visualizations")
    if args.datashader_viz:
        viz_options.append("Datashader Visualizations")
    if args.deepscatter_viz:
        viz_options.append("Deepscatter Visualizations")
    
    if viz_options:
        logger.info(f"   Visualization Options: {', '.join(viz_options)}")
    else:
        logger.info("   Visualization: None (use --lightweight-viz for efficient options)")
    
    # Enhanced features
    if args.force_refresh:
        logger.info("   Force Refresh: Enabled (will refresh cached data)")
    if args.validate_h3:
        logger.info("   H3 Validation: Enabled")
    
    try:
        # Initialize analysis with enhanced modules
        backend, modules, data_manager, h3_fusion = initialize_analysis(args)
        
        # Validate H3 operations if requested
        if args.validate_h3:
            logger.info("🔍 Validating H3 operations...")
            h3_validation = h3_fusion.validate_h3_operations()
            logger.info(f"H3 validation result: {h3_validation}")
            
            if h3_validation.get('errors'):
                logger.error(f"H3 validation failed: {h3_validation['errors']}")
                return
        
        # Run comprehensive analysis with enhanced data management
        redevelopment_scores, summary = run_comprehensive_analysis_with_enhanced_data(
            backend, modules, data_manager, h3_fusion, args
        )
        
        # Export results with visualization options
        export_paths = export_results_with_visualizations(
            backend, redevelopment_scores, summary, args
        )
        
        # Generate reports
        generate_reports(summary, args.output_dir, args.spatial_analysis)
        
        # Print summary
        print_analysis_summary(summary, export_paths, args)
        
        logger.info("✅ Cascadia analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def run_comprehensive_analysis_with_enhanced_data(backend, modules, data_manager, h3_fusion, args):
    """Run comprehensive analysis with enhanced data management and H3 fusion"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting enhanced comprehensive analysis with H3 geospatial fusion...")
    
    # Collect data from all modules with enhanced data management
    module_data = {}
    
    for module_name, module in modules.items():
        logger.info(f"📊 Processing module: {module_name}")
        
        try:
            # Use enhanced data manager for data acquisition
            data_path = data_manager.acquire_data_with_caching(
                module_name=module_name,
                data_source_func=module.acquire_raw_data,
                force_refresh=args.force_refresh
            )
            
            # Process data to H3 format with enhanced fusion
            h3_data = data_manager.process_to_h3_with_caching(
                data_path=data_path,
                module_name=module_name,
                target_hexagons=list(backend.target_hexagons)
            )
            
            module_data[module_name] = h3_data
            
            # Generate data quality report
            quality_report = data_manager.get_data_quality_report(module_name)
            logger.info(f"📋 {module_name} data quality: {quality_report.get('quality_metrics', {}).get('quality_score', 0):.2f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {module_name}: {e}")
            continue
    
    # Perform enhanced H3 geospatial fusion
    logger.info("🔗 Performing enhanced H3 geospatial fusion...")
    fused_data = h3_fusion.fuse_geospatial_data(
        data_sources=module_data,
        target_hexagons=list(backend.target_hexagons)
    )
    
    # Run final analysis on fused data
    logger.info("🔬 Running final analysis on fused data...")
    redevelopment_scores = {}
    
    for hex_id, hex_data in fused_data.items():
        try:
            # Calculate redevelopment score based on fused data
            score = calculate_enhanced_redevelopment_score(hex_data)
            redevelopment_scores[hex_id] = score
        except Exception as e:
            logger.warning(f"Error calculating score for {hex_id}: {e}")
            redevelopment_scores[hex_id] = 0.0
    
    # Generate summary
    summary = {
        'total_hexagons': len(backend.target_hexagons),
        'processed_hexagons': len(fused_data),
        'module_count': len(modules),
        'data_sources': list(module_data.keys()),
        'h3_resolution': args.h3_resolution,
        'spatial_analysis_enabled': args.spatial_analysis,
        'enhanced_data_management': True,
        'h3_fusion_enabled': True,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    return redevelopment_scores, summary

def calculate_enhanced_redevelopment_score(hex_data):
    """Calculate enhanced redevelopment score based on fused data"""
    score = 0.0
    factors = []
    
    # Analyze zoning data
    if 'zoning' in hex_data:
        zoning_data = hex_data['zoning']
        if isinstance(zoning_data, list) and len(zoning_data) > 0:
            # Extract zoning information
            zoning_score = 0.0
            for zoning_item in zoning_data:
                if isinstance(zoning_item, dict):
                    zone_type = zoning_item.get('zone_type', '').lower()
                    if 'agricultural' in zone_type:
                        zoning_score += 0.3
                    elif 'residential' in zone_type:
                        zoning_score += 0.1
            factors.append(zoning_score)
    
    # Analyze current use data
    if 'current_use' in hex_data:
        current_use_data = hex_data['current_use']
        if isinstance(current_use_data, list) and len(current_use_data) > 0:
            # Extract current use information
            use_score = 0.0
            for use_item in current_use_data:
                if isinstance(use_item, dict):
                    crop_type = use_item.get('crop_type', '').lower()
                    if 'hay' in crop_type or 'alfalfa' in crop_type:
                        use_score += 0.2
                    elif 'vegetables' in crop_type:
                        use_score += 0.3
            factors.append(use_score)
    
    # Analyze ownership data
    if 'ownership' in hex_data:
        ownership_data = hex_data['ownership']
        if isinstance(ownership_data, list) and len(ownership_data) > 0:
            # Extract ownership information
            ownership_score = 0.0
            for ownership_item in ownership_data:
                if isinstance(ownership_item, dict):
                    owner_type = ownership_item.get('owner_type', '').lower()
                    if 'individual' in owner_type:
                        ownership_score += 0.2
                    elif 'corporate' in owner_type:
                        ownership_score += 0.1
            factors.append(ownership_score)
    
    # Analyze improvements data
    if 'improvements' in hex_data:
        improvements_data = hex_data['improvements']
        if isinstance(improvements_data, list) and len(improvements_data) > 0:
            # Extract improvements information
            improvements_score = 0.0
            for improvement_item in improvements_data:
                if isinstance(improvement_item, dict):
                    improvement_type = improvement_item.get('improvement_type', '').lower()
                    if 'barn' in improvement_type:
                        improvements_score += 0.2
                    elif 'house' in improvement_type:
                        improvements_score += 0.1
            factors.append(improvements_score)
    
    # Calculate final score
    if factors:
        score = sum(factors) / len(factors)
    
    return min(score, 1.0)  # Normalize to 0-1 range

def export_results_with_visualizations(backend, redevelopment_scores, summary, args):
    """Export results with selected visualization options"""
    logger = logging.getLogger(__name__)
    
    # Parse counties
    counties_dict = parse_counties(args.counties)
    bioregion_lower = "cascadia"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir)
    
    # Export core data
    export_paths = export_results(
        backend, redevelopment_scores, summary,
        output_dir, timestamp, bioregion_lower, args.export_format
    )
    
    # Generate selected visualizations
    if args.lightweight_viz:
        logger.info("📊 Generating lightweight static visualizations...")
        try:
            from utils.static_visualization import create_static_plots
            static_results = create_static_plots(backend, output_dir)
            export_paths.update(static_results)
            logger.info("✅ Lightweight visualizations created")
        except Exception as e:
            logger.error(f"Failed to create lightweight visualizations: {e}")
    
    if args.datashader_viz:
        logger.info("📊 Generating Datashader visualizations...")
        try:
            from utils.datashader_visualization import create_datashader_visualization
            datashader_results = create_datashader_visualization(backend, output_dir)
            export_paths.update(datashader_results)
            logger.info("✅ Datashader visualizations created")
        except Exception as e:
            logger.error(f"Failed to create Datashader visualizations: {e}")
    
    if args.deepscatter_viz:
        logger.info("📊 Generating Deepscatter visualizations...")
        try:
            from utils.deepscatter_visualization import create_deepscatter_visualization
            deepscatter_results = create_deepscatter_visualization(backend, output_dir)
            export_paths.update(deepscatter_results)
            logger.info("✅ Deepscatter visualizations created")
        except Exception as e:
            logger.error(f"Failed to create Deepscatter visualizations: {e}")
    
    return export_paths

def print_analysis_summary(summary, export_paths, args):
    """Print a comprehensive analysis summary"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*80)
    print("🌲 CASCADIA AGRICULTURAL ANALYSIS SUMMARY")
    print("="*80)
    
    # Analysis statistics
    print(f"\n📊 Analysis Statistics:")
    print(f"   Total Hexagons: {summary.get('total_hexagons', 0):,}")
    print(f"   Processed Hexagons: {summary.get('processed_hexagons', 0):,}")
    print(f"   Data Sources: {len(summary.get('data_sources', []))}")
    print(f"   H3 Resolution: {summary.get('h3_resolution', 8)}")
    
    # Enhanced features
    print(f"\n🔧 Enhanced Features:")
    print(f"   Enhanced Data Management: {summary.get('enhanced_data_management', False)}")
    print(f"   H3 Fusion Enabled: {summary.get('h3_fusion_enabled', False)}")
    print(f"   Spatial Analysis: {summary.get('spatial_analysis_enabled', False)}")
    
    # Data sources
    print(f"\n📋 Data Sources:")
    for source in summary.get('data_sources', []):
        print(f"   • {source}")
    
    # Visualization outputs
    print(f"\n🎨 Generated Visualizations:")
    viz_files = []
    for key, path in export_paths.items():
        if any(keyword in key.lower() for keyword in ['viz', 'dashboard', 'html', 'csv', 'json']):
            viz_files.append(f"   {key}: {path}")
    
    if viz_files:
        for file_info in viz_files:
            print(file_info)
    else:
        print("   No visualizations generated (use --lightweight-viz for efficient options)")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if not any([args.lightweight_viz, args.datashader_viz, args.deepscatter_viz, args.generate_dashboard]):
        print("   • Use --lightweight-viz for efficient static visualizations")
        print("   • Use --datashader-viz for large dataset rendering")
        print("   • Use --deepscatter-viz for web-based interactive plots")
    
    if args.generate_dashboard:
        print("   • Consider using --lightweight-viz instead of --generate-dashboard for better performance")
    
    if not args.spatial_analysis:
        print("   • Use --spatial-analysis for enhanced spatial correlation analysis")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main() 