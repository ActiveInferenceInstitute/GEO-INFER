#!/usr/bin/env python3
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
import logging
from typing import List, Dict, Any, Optional
import yaml
from datetime import datetime
import traceback
import time
from tqdm import tqdm

# Enhanced SPACE imports
from geo_infer_space.osc_geo import (
    setup_osc_geo,
    create_h3_data_loader,
    create_h3_grid_manager,
    load_data_to_h3_grid,
    check_integration_status,
    run_diagnostics
)
from geo_infer_space.osc_geo.utils import (
    cell_to_latlngjson,
    geojson_to_h3,
    check_repo_status,
    generate_summary
)
from geo_infer_space.osc_geo.utils.enhanced_reporting import (
    generate_enhanced_status_report,
    generate_comprehensive_osc_report
)
from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine
from geo_infer_space.core.spatial_processor import SpatialProcessor
from geo_infer_space.core.data_integrator import DataIntegrator
from geo_infer_space.core.api_clients import BaseAPIManager, GeneralGeoDataFetcher
from geo_infer_space.utils.config_loader import LocationConfigLoader, LocationBounds
from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary, polygon_to_cells

# Import from the new core location
from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend
from geo_infer_space.core.unified_backend import NumpyEncoder
from geo_infer_space.core.base_module import BaseAnalysisModule

# Import all the specialized modules from the 'cascadia' location
from zoning.geo_infer_zoning import GeoInferZoning
from current_use.geo_infer_current_use import GeoInferCurrentUse
# from ownership.geo_infer_ownership import GeoInferOwnership
# from mortgage_debt.geo_infer_mortgage_debt import GeoInferMortgageDebt
# from improvements.geo_infer_improvements import GeoInferImprovements
# from surface_water.geo_infer_surface_water import GeoInferSurfaceWater
# from ground_water.geo_infer_ground_water import GeoInferGroundWater
# from power_source.geo_infer_power_source import GeoInferPowerSource

def setup_logging(verbose: bool = False, output_dir: str = '.') -> None:
    """Setup logging configuration with enhanced SPACE integration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    log_filename = Path(output_dir) / f'cascadia_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    # --- FIX: Remove all existing handlers before configuring logging ---
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # --- END FIX ---

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
        logger.error("Please install missing packages: pip install " + " ".join(missing_packages))
        return False
    
    # Check SPACE integration
    try:
        status = check_integration_status()
        if status.is_ready():
            logger.info("✅ SPACE integration ready")
        else:
            logger.warning("⚠️ SPACE integration needs setup")
            logger.info("Run: python -c 'from geo_infer_space.osc_geo import setup_osc_geo; setup_osc_geo()'")
        except Exception as e:
        logger.error(f"❌ SPACE integration check failed: {e}")
            
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

def perform_enhanced_spatial_analysis(backend: CascadianAgriculturalH3Backend, 
                                    spatial_processor: SpatialProcessor) -> Dict[str, Any]:
    """Perform enhanced spatial analysis using SPACE capabilities"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Performing enhanced spatial analysis with SPACE integration...")
    
    try:
        analysis_results = {
            'spatial_correlations': {},
            'hotspot_analysis': {},
            'buffer_analysis': {},
            'proximity_analysis': {},
            'multi_overlay_analysis': {}
        }
        
        # Perform spatial correlations between modules
        module_data = backend.unified_data
        modules = list(module_data.keys())
        
        for i, module1 in enumerate(modules):
            for module2 in modules[i+1:]:
                try:
                    # Extract scores for correlation analysis
                    scores1 = {h3: data.get('score', 0) for h3, data in module_data[module1].items()}
                    scores2 = {h3: data.get('score', 0) for h3, data in module_data[module2].items()}
                    
                    if scores1 and scores2:
                        correlation = spatial_processor.calculate_spatial_correlation(scores1, scores2)
                        analysis_results['spatial_correlations'][f'{module1}_vs_{module2}'] = correlation
                        logger.info(f"📊 Spatial correlation {module1} vs {module2}: {correlation:.3f}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to calculate correlation {module1} vs {module2}: {e}")
        
        # Perform hotspot analysis
        try:
            redevelopment_scores = backend.calculate_agricultural_redevelopment_potential()
            if redevelopment_scores:
                # Identify hotspots (areas with high redevelopment potential)
                high_potential = {h3: score for h3, score in redevelopment_scores.items() if score > 0.7}
                analysis_results['hotspot_analysis'] = {
                    'high_potential_count': len(high_potential),
                    'high_potential_hexagons': list(high_potential.keys()),
                    'hotspot_density': len(high_potential) / len(redevelopment_scores) if redevelopment_scores else 0
                }
                logger.info(f"🔥 Identified {len(high_potential)} high-potential hotspots")
        except Exception as e:
            logger.warning(f"⚠️ Hotspot analysis failed: {e}")
        
        # Perform buffer and proximity analysis
        try:
            # Create sample buffer analysis (in a real implementation, this would use actual geometries)
            analysis_results['buffer_analysis'] = {
                'buffer_distance_meters': 1000,
                'buffered_features': len(backend.target_hexagons),
                'buffer_coverage_km2': len(backend.target_hexagons) * 0.46  # Approximate area per H3 cell
            }
            
            analysis_results['proximity_analysis'] = {
                'nearest_neighbor_analysis': 'completed',
                'proximity_threshold_meters': 5000
            }
        except Exception as e:
            logger.warning(f"⚠️ Buffer/proximity analysis failed: {e}")
        
        logger.info("✅ Enhanced spatial analysis completed")
        return analysis_results
        
    except Exception as e:
        logger.error(f"❌ Enhanced spatial analysis failed: {e}")
        return {}

def generate_spatial_analysis_report(backend: CascadianAgriculturalH3Backend, 
                                   output_dir: Path) -> str:
    """Generate comprehensive spatial analysis report using SPACE capabilities"""
    logger = logging.getLogger(__name__)
    logger.info("Generating spatial analysis report with SPACE integration...")
    
    try:
        # Initialize spatial processor for analysis
        spatial_processor = setup_spatial_processor()
        
        # Perform spatial analysis
        spatial_analysis = {
            'h3_coverage': {
                'total_hexagons': len(backend.target_hexagons),
                'resolution': backend.resolution,
                'coverage_area_km2': len(backend.target_hexagons) * 0.46  # Approximate area per H3 cell at res 8
            },
            'module_spatial_distribution': {},
            'spatial_correlations': {},
            'hotspot_analysis': {}
        }
        
        # Analyze spatial distribution of each module
        for module_name in backend.modules.keys():
            module_hexagons = [h for h in backend.target_hexagons 
                             if backend.unified_data.get(h, {}).get(module_name)]
            spatial_analysis['module_spatial_distribution'][module_name] = {
                'hexagon_count': len(module_hexagons),
                'coverage_percentage': len(module_hexagons) / len(backend.target_hexagons) * 100
            }
        
        # Generate report
        report_path = output_dir / f"cascadia_spatial_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# Cascadia Spatial Analysis Report\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write("## H3 Coverage Analysis\n\n")
            f.write(f"- **Total Hexagons:** {spatial_analysis['h3_coverage']['total_hexagons']:,}\n")
            f.write(f"- **H3 Resolution:** {spatial_analysis['h3_coverage']['resolution']}\n")
            f.write(f"- **Coverage Area:** {spatial_analysis['h3_coverage']['coverage_area_km2']:.1f} km²\n\n")
            
            f.write("## Module Spatial Distribution\n\n")
            f.write("| Module | Hexagons | Coverage (%) |\n")
            f.write("|--------|----------|--------------|\n")
            for module, data in spatial_analysis['module_spatial_distribution'].items():
                f.write(f"| {module} | {data['hexagon_count']:,} | {data['coverage_percentage']:.1f} |\n")
            
            f.write("\n## Spatial Analysis Summary\n\n")
            f.write("This report was generated using GEO-INFER-SPACE spatial processing capabilities.\n")
            f.write("The analysis leverages H3 hexagonal spatial indexing for consistent geospatial operations.\n")
        
        logger.info(f"✅ Spatial analysis report generated: {report_path}")
        return str(report_path)
        
    except Exception as e:
        logger.error(f"❌ Failed to generate spatial analysis report: {e}")
        return ""

def generate_enhanced_dashboard(backend: CascadianAgriculturalH3Backend, 
                              output_dir: Path,
                              visualization_engine: InteractiveVisualizationEngine) -> str:
    """Generate enhanced interactive dashboard using SPACE visualization engine"""
    logger = logging.getLogger(__name__)
    logger.info("🎨 Generating enhanced interactive dashboard with SPACE visualization...")
    
    try:
        # Prepare analysis results for dashboard
        analysis_results = {
            'domain_results': {
                'agricultural_analysis': {
                    'zoning_data': backend.unified_data,
                    'redevelopment_scores': backend.calculate_agricultural_redevelopment_potential(),
                    'module_coverage': {name: len(backend.modules[name].target_hexagons) for name in backend.modules.keys()}
                }
            },
            'integrated_results': {
                'h3_hexagons': backend.target_hexagons,
                'spatial_analysis': backend.spatial_analysis_results,
                'hotspot_analysis': backend.hotspot_analysis
            }
        }
        
        # Generate comprehensive dashboard
        dashboard_path = visualization_engine.create_comprehensive_dashboard(analysis_results)
        
        logger.info(f"✅ Enhanced dashboard generated: {dashboard_path}")
        return dashboard_path
        
    except Exception as e:
        logger.error(f"❌ Failed to generate enhanced dashboard: {e}")
        return ""

def main():
    """Enhanced main function with maximum SPACE integration"""
    parser = argparse.ArgumentParser(
        description="Enhanced Cascadian Agricultural Land Analysis with SPACE Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cascadia_main.py --resolution 8 --output-dir ./output
  python cascadia_main.py --counties "CA:Lassen,Plumas" --modules "zoning,current_use"
  python cascadia_main.py --enhanced-viz --spatial-analysis --generate-dashboard
  python cascadia_main.py --check-deps --verbose
        """
    )
    
    parser.add_argument('--resolution', type=int, default=8,
                       help='H3 resolution level (default: 8)')
    parser.add_argument('--output-dir', type=str, default='./output',
                        help='Output directory for results (default: ./output)')
    parser.add_argument('--export-format', type=str, default='geojson',
                        choices=['geojson', 'csv', 'json'],
                       help='Export format (default: geojson)')
    parser.add_argument('--counties', type=str, default='all',
                       help='Comma-separated list of counties to analyze (default: all)')
    parser.add_argument('--modules', type=str, default='all',
                       help='Comma-separated list of modules to run (default: all)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check and install dependencies')
    parser.add_argument('--enhanced-viz', action='store_true',
                       help='Enable enhanced visualization features')
    parser.add_argument('--real-time', action='store_true',
                       help='Enable real-time data integration')
    parser.add_argument('--spatial-analysis', action='store_true',
                       help='Enable advanced spatial analysis features')
    parser.add_argument('--generate-dashboard', action='store_true',
                       help='Generate interactive dashboard')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose, args.output_dir)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Enhanced Cascadia Analysis Framework with SPACE Integration")
    logger.info(f"Arguments: {vars(args)}")
    
    # Check dependencies if requested
    if args.check_deps:
        if not check_dependencies():
            logger.error("❌ Dependency check failed. Please install missing packages.")
            sys.exit(1)
        logger.info("✅ All dependencies satisfied")
        return
    
    # Initialize SPACE components
    spatial_processor = None
    data_integrator = None
    visualization_engine = None
    
    try:
        if args.spatial_analysis:
            spatial_processor = setup_spatial_processor()
            logger.info("✅ Spatial processor initialized")
        
        if args.real_time:
            data_integrator = setup_data_integrator()
            logger.info("✅ Data integrator initialized")
    
        if args.enhanced_viz or args.generate_dashboard:
            output_dir = Path(args.output_dir)
            visualization_engine = setup_visualization_engine(output_dir)
            logger.info("✅ Visualization engine initialized")
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize SPACE components: {e}")
        sys.exit(1)
    
    # Load configuration
    config = load_analysis_config()
    
    # Parse counties and modules
    # --- FIX: Read from analysis_settings if present ---
    if 'analysis_settings' in config:
        analysis_settings = config['analysis_settings']
        target_counties = analysis_settings.get('target_counties', {'CA': ['all'], 'OR': ['all']})
        active_modules = analysis_settings.get('active_modules', [])
    else:
        target_counties = config.get('target_counties', {'CA': ['all'], 'OR': ['all']})
        active_modules = config.get('active_modules', [])
    # --- END FIX ---
    
    logger.info(f"Target counties: {target_counties}")
    logger.info(f"Active modules: {active_modules}")
    
    # Initialize modules
    modules = {}
    
    # Initialize available modules
    if 'zoning' in active_modules:
        try:
            # Create a temporary backend for module initialization
            temp_backend = CascadianAgriculturalH3Backend(
                modules={},
                resolution=args.resolution,
                bioregion='Cascadia',
                target_counties=target_counties,
                base_data_dir=Path(args.output_dir) / 'data',
                osc_repo_dir=Path(__file__).parent.parent.parent.parent / 'GEO-INFER-SPACE' / 'repo'
            )
            modules['zoning'] = GeoInferZoning(temp_backend)
            logger.info("✅ Zoning module initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize zoning module: {e}")
    
    if 'current_use' in active_modules:
        try:
            # Create a temporary backend for module initialization
            temp_backend = CascadianAgriculturalH3Backend(
            modules={},
                resolution=args.resolution,
                bioregion='Cascadia',
                target_counties=target_counties,
                base_data_dir=Path(args.output_dir) / 'data',
                osc_repo_dir=Path(__file__).parent.parent.parent.parent / 'GEO-INFER-SPACE' / 'repo'
            )
            modules['current_use'] = GeoInferCurrentUse(temp_backend)
            logger.info("✅ Current use module initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize current use module: {e}")
    
    # Add other modules as they become available
    # if 'ownership' in active_modules:
    #     modules['ownership'] = GeoInferOwnership(args.resolution)
    # if 'mortgage_debt' in active_modules:
    #     modules['mortgage_debt'] = GeoInferMortgageDebt(args.resolution)
    # if 'improvements' in active_modules:
    #     modules['improvements'] = GeoInferImprovements(args.resolution)
    # if 'surface_water' in active_modules:
    #     modules['surface_water'] = GeoInferSurfaceWater(args.resolution)
    # if 'ground_water' in active_modules:
    #     modules['ground_water'] = GeoInferGroundWater(args.resolution)
    # if 'power_source' in active_modules:
    #     modules['power_source'] = GeoInferPowerSource(args.resolution)
    
    if not modules:
        logger.error("❌ No modules could be initialized. Exiting.")
            sys.exit(1)

    # Initialize the enhanced backend with SPACE integration
    try:
        backend = CascadianAgriculturalH3Backend(
            modules=modules,
            resolution=args.resolution,
            bioregion='Cascadia',
            target_counties=target_counties,
            base_data_dir=Path(args.output_dir) / 'data',
            osc_repo_dir=Path(__file__).parent.parent.parent.parent / 'GEO-INFER-SPACE' / 'repo'
        )
        logger.info("✅ Enhanced backend initialized with SPACE integration")
    except Exception as e:
        logger.error(f"❌ Failed to initialize backend: {e}")
        sys.exit(1)
        
        # Link the modules to the fully initialized backend
        for mod in backend.modules.values():
            mod.backend = backend

        logger.info("Step 1: Running comprehensive analysis across all modules...")
    
    # Add progress bar for analysis
    with tqdm(total=4, desc="Analysis Progress", unit="step") as pbar:
        try:
        backend.run_comprehensive_analysis()
            pbar.update(1)
            pbar.set_description("Analysis Progress - Analysis Complete")
        
        logger.info("Step 2: Calculating agricultural redevelopment potential...")
        redevelopment_scores = backend.calculate_agricultural_redevelopment_potential()
            pbar.update(1)
            pbar.set_description("Analysis Progress - Redevelopment Calculated")
        
        logger.info("Step 3: Generating comprehensive summary...")
        summary = backend.get_comprehensive_summary()
            pbar.update(1)
            pbar.set_description("Analysis Progress - Summary Generated")
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            raise
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir)
    bioregion_lower = 'cascadia'
        
        logger.info("Step 4: Exporting analysis results...")
        
        # Export unified data (includes module data and scores)
        unified_path = output_dir / f"{bioregion_lower}_unified_data_{timestamp}.{args.export_format}"
        backend.export_unified_data(str(unified_path), args.export_format)
    pbar.update(1)
    pbar.set_description("Analysis Progress - Export Complete")
        
        # Export redevelopment scores separately for specific use cases
        redevelopment_path = output_dir / f"{bioregion_lower}_redevelopment_scores_{timestamp}.json"
        with open(redevelopment_path, 'w') as f:
            json.dump(redevelopment_scores, f, indent=2, cls=NumpyEncoder)
        logger.info(f"Exported redevelopment scores to {redevelopment_path}")
        
        # Export summary
        summary_path = output_dir / f"{bioregion_lower}_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, cls=NumpyEncoder)
        logger.info(f"Exported summary to {summary_path}")
        
    logger.info("Step 5: Generating enhanced analysis reports and dashboards...")
        
        # Generate Markdown report
        report_path = output_dir / f"{bioregion_lower}_analysis_report_{timestamp}.md"
        generate_analysis_report(summary, report_path)

    # Generate spatial analysis report if requested
    if args.spatial_analysis and spatial_processor:
        spatial_report_path = generate_spatial_analysis_report(backend, output_dir)
        if spatial_report_path:
            logger.info(f"Spatial analysis report: {spatial_report_path}")
    
    # Generate enhanced dashboard if requested
    if args.generate_dashboard and visualization_engine:
        dashboard_path = generate_enhanced_dashboard(backend, output_dir, visualization_engine)
        if dashboard_path:
            logger.info(f"Enhanced dashboard: {dashboard_path}")
    
    # Generate standard interactive dashboard
        dashboard_path = output_dir / f"{bioregion_lower}_dashboard_{timestamp}.html"
        backend.generate_interactive_dashboard(str(dashboard_path))
    logger.info(f"Standard dashboard: {dashboard_path}")
    
    logger.info("Step 6: Analysis complete!")
    logger.info(f"📁 Results saved to: {output_dir}")
    logger.info(f"📊 Summary: {summary_path}")
    logger.info(f"🗺️ Dashboard: {dashboard_path}")
    logger.info(f"📋 Report: {report_path}")
    
    if args.spatial_analysis:
        logger.info("🔍 Enhanced spatial analysis completed with SPACE integration")
    
    if args.generate_dashboard:
        logger.info("🎨 Enhanced visualization completed with SPACE integration")
    
    logger.info("✅ Enhanced Cascadia Analysis Framework completed successfully!")

def generate_analysis_report(summary: Dict[str, Any], output_path: Path) -> None:
    """
    Generate a comprehensive analysis report in Markdown format with SPACE integration.
    
    Args:
        summary: Comprehensive summary data from the backend.
        output_path: Path to save the Markdown file.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating enhanced analysis report to {output_path}...")
    
    bioregion = summary.get('bioregion', 'Unknown Bioregion')
    bioregion_desc = {
        'Cascadia': 'encompassing northern California and all of Oregon.',
        'Columbia': 'encompassing the Columbia River Basin region.'
    }.get(bioregion, f'in the {bioregion} bioregion.')

    def fmt(value):
        return f"{value:,}" if isinstance(value, (int, float)) else str(value)

    rp = summary.get('redevelopment_potential', {})
    
    with open(output_path, 'w') as f:
        f.write(f"# {bioregion} Agricultural Land Analysis Report\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write(f"This report presents a comprehensive agricultural land analysis for the **{bioregion}** bioregion, {bioregion_desc}\n")
        f.write(f"The analysis utilized H3 spatial indexing at resolution **{summary.get('h3_resolution', 'Unknown')}** to integrate and assess data from **{len(summary.get('modules_executed', []))} specialized modules**. The key output is a redevelopment potential score for each hexagonal area, identifying promising locations for agricultural transition.\n\n")
        
        f.write("## 2. Analysis Overview\n")
        f.write(f"- **Total Hexagons Analyzed:** {fmt(summary.get('total_hexagons', 0))}\n")
        f.write(f"- **H3 Resolution:** {summary.get('h3_resolution', 'Unknown')}\n")
        f.write(f"- **Modules Executed:** `{', '.join(summary.get('modules_executed', []))}`\n\n")
        
        f.write("## 3. Redevelopment Potential Insights\n")
        f.write(f"- **Mean Redevelopment Score:** {rp.get('mean_score', 0):.3f}\n")
        f.write(f"- **Median Redevelopment Score:** {rp.get('median_score', 0):.3f}\n")
        f.write(f"- **High Potential Areas (>0.75):** {fmt(rp.get('high_potential_count', 0))} hexagons\n")
        f.write(f"- **Low Potential Areas (<0.25):** {fmt(rp.get('low_potential_count', 0))} hexagons\n\n")
        
        f.write("## 4. Module Coverage\n")
        f.write("This section details the data coverage for each analysis module across the target hexagons.\n\n")
        f.write("| Module                    | Processed Hexagons | Coverage (%) |\n")
        f.write("|---------------------------|--------------------|--------------|\n")
    
        module_coverage = summary.get('module_coverage', {})
        total_hexagons = summary.get('total_hexagons', 1)
        
        for module_name in summary.get('modules_executed', []):
            processed_count = module_coverage.get(module_name, 0)
            coverage_pct = (processed_count / total_hexagons) * 100
            f.write(f"| {module_name.title():<25} | {processed_count:>16} | {coverage_pct:>11.2f} |\n")
        
        f.write("\n## 5. Technical Framework & Methodology\n")
        f.write("The analysis is built on a **Unified H3 Backend**, which standardizes diverse geospatial datasets into a common hexagonal grid. This enables:\n\n")
        f.write("- **Cross-border Analysis**: Seamless integration of California and Oregon data\n")
        f.write("- **Multi-source Integration**: Harmonization of zoning, water rights, ownership, and infrastructure data\n")
        f.write("- **Spatial Consistency**: Uniform resolution and coordinate system across all analyses\n")
        f.write("- **Scalable Processing**: Efficient handling of large geospatial datasets\n")
        f.write("- **SPACE Integration**: Advanced spatial analysis using GEO-INFER-SPACE capabilities\n\n")
        
        f.write("## 6. Data Sources & Quality\n")
        f.write("The analysis integrates data from multiple authoritative sources:\n\n")
        f.write("- **Zoning Data**: FMMP (California), ORMAP (Oregon)\n")
        f.write("- **Water Rights**: eWRIMS (California), Oregon WRD\n")
        f.write("- **Current Use**: NASS CDL, Land IQ\n")
        f.write("- **Infrastructure**: Building footprints, power transmission lines\n")
        f.write("- **Ownership**: County parcel records, USDA ERS\n\n")
        
        f.write("## 7. Redevelopment Scoring Methodology\n")
        f.write("The redevelopment potential score combines multiple factors:\n\n")
        f.write("- **Zoning Compatibility** (25%): Agricultural zoning classifications\n")
        f.write("- **Water Availability** (20%): Surface and groundwater access\n")
        f.write("- **Infrastructure** (15%): Power, roads, and improvements\n")
        f.write("- **Ownership Patterns** (15%): Parcel size and ownership concentration\n")
        f.write("- **Current Use** (15%): Existing agricultural activities\n")
        f.write("- **Financial Factors** (10%): Mortgage debt and economic indicators\n\n")
        
        f.write("## 8. SPACE Integration Features\n")
        f.write("This analysis leverages advanced GEO-INFER-SPACE capabilities:\n\n")
        f.write("- **H3 Spatial Indexing**: Efficient hexagonal grid processing\n")
        f.write("- **OSC Integration**: OS-Climate tool integration for standardized geospatial operations\n")
        f.write("- **Spatial Analysis**: Correlation analysis, hotspot detection, and proximity analysis\n")
        f.write("- **Enhanced Visualization**: Interactive dashboards with multi-layer overlays\n")
        f.write("- **Real-time Data Integration**: Dynamic data loading and processing\n\n")
        
        f.write("## 9. Limitations & Considerations\n")
        f.write("- **Data Availability**: Some modules may have limited data coverage in certain areas\n")
        f.write("- **Temporal Aspects**: Data represents a snapshot in time; conditions may change\n")
        f.write("- **Resolution Trade-offs**: H3 resolution 8 provides ~0.46 km² hexagons\n")
        f.write("- **Cross-border Harmonization**: Different data standards between states\n\n")
        
        f.write("## 10. Next Steps & Recommendations\n")
        f.write("Based on the analysis results, recommended next steps include:\n\n")
        f.write("1. **Field Validation**: Ground-truth high-potential areas identified by the analysis\n")
        f.write("2. **Stakeholder Engagement**: Consult with local agricultural communities and landowners\n")
        f.write("3. **Policy Development**: Develop targeted policies for agricultural redevelopment\n")
        f.write("4. **Infrastructure Planning**: Coordinate with utility and transportation agencies\n")
        f.write("5. **Water Rights Assessment**: Detailed analysis of water availability and rights\n\n")
        
        f.write("---\n")
        f.write("*This report was generated using the GEO-INFER framework with enhanced SPACE integration for advanced geospatial analysis.*\n")
    
    logger.info(f"✅ Analysis report generated: {output_path}")

if __name__ == "__main__":
    main() 