#!/usr/bin/env python3
"""
Cascadian Agricultural Land Analysis Framework - Main Integration Script

This script orchestrates the complete agricultural land analysis across the 
Cascadian bioregion (Northern California + Oregon) using the unified H3-indexed
backend and all 8 specialized data modules.

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
"""

import sys
import os
from pathlib import Path

# --- Robust Path Setup ---
# This setup allows for imports from the geo_infer_place and geo_infer_space modules.
try:
    # Assumes cascadia_main.py is in GEO-INFER-PLACE/locations/cascadia/
    cascadian_dir = Path(__file__).resolve().parent
    place_root = cascadian_dir.parents[2] # GEO-INFER-PLACE
    project_root = place_root.parent # GEO-INFER

    # Add required 'src' directories to the path
    place_src_path = place_root / 'src'
    space_src_path = project_root / 'GEO-INFER-SPACE' / 'src'
    
    # Add the current directory for local module imports (e.g. zoning)
    sys.path.insert(0, str(cascadian_dir))

    for p in [place_src_path, space_src_path]:
        if p.exists() and str(p) not in sys.path:
            sys.path.insert(0, str(p))
            print(f"INFO: Successfully added {p} to sys.path")
        else:
            print(f"WARNING: Required src path not found or already in path: {p}")

except IndexError:
    print("CRITICAL: Could not determine project root. Please ensure you are running from the 'GEO-INFER-PLACE/locations/cascadia' directory")
    sys.exit(1)
# --- End Path Setup ---

import argparse
import logging
from typing import List, Dict, Any
import json
from datetime import datetime
import traceback

# Import from the new core location
from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend, NumpyEncoder
from geo_infer_place.core.base_module import BaseAnalysisModule

# Import all the specialized modules from the 'cascadia' location
# Note: These would need to be created following the pattern of GeoInferZoning
from zoning.geo_infer_zoning import GeoInferZoning
# --- Placeholder imports for other modules ---
# from current_use.geo_infer_current_use import GeoInferCurrentUse
# from ownership.geo_infer_ownership import GeoInferOwnership
# from mortgage_debt.geo_infer_mortgage_debt import GeoInferMortgageDebt
# from improvements.geo_infer_improvements import GeoInferImprovements
# from surface_water.geo_infer_surface_water import GeoInferSurfaceWater
# from ground_water.geo_infer_ground_water import GeoInferGroundWater
# from power_source.geo_infer_power_source import GeoInferPowerSource

def setup_logging(verbose: bool = False, output_dir: str = '.') -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    log_filename = Path(output_dir) / f'cascadia_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_filename)
        ]
    )

def check_and_install_dependencies() -> bool:
    """
    Check and install required dependencies.
    This is a simplified check; more robust dependency management should be
    handled by package managers like pip with a requirements.txt file.
    """
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'h3', 'numpy', 'pandas', 'geopandas',
        'shapely', 'requests', 'rasterio', 'folium'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.debug(f"✓ Dependency '{package}' is available.")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ Dependency '{package}' is missing.")
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Attempting to install missing packages via pip...")
        
        try:
            import subprocess
            for package in missing_packages:
                logger.info(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"✓ {package} installed successfully.")
        except Exception as e:
            logger.critical(f"Failed to install dependencies: {e}", exc_info=True)
            return False
            
    logger.info("All required dependencies are available.")
    return True

def validate_configuration(args: argparse.Namespace) -> bool:
    """Validate script arguments and environment."""
    logger = logging.getLogger(__name__)
    
    if not (1 <= args.resolution <= 15):
        logger.error(f"Invalid H3 resolution: {args.resolution}. Must be between 1 and 15.")
        return False
    
    try:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Using output directory: {Path(args.output_dir).resolve()}")
    except OSError as e:
        logger.error(f"Cannot create or access output directory {args.output_dir}: {e}")
        return False
        
    valid_formats = ['geojson', 'csv', 'json']
    if args.export_format.lower() not in valid_formats:
        logger.error(f"Invalid export format: {args.export_format}. Must be one of {valid_formats}.")
        return False
            
    logger.info("Configuration validation successful.")
    return True

def load_analysis_config() -> Dict[str, Any]:
    """Loads the analysis_settings from the main JSON config file."""
    logger = logging.getLogger(__name__)
    config_path = Path(__file__).resolve().parent / 'config' / 'analysis_config.json'
    
    if not config_path.exists():
        logger.warning(f"Configuration file not found at {config_path}. Using defaults.")
        return {}
        
    try:
        with open(config_path, 'r') as f:
            full_config = json.load(f)
            analysis_config = full_config.get('analysis_settings', {})
            logger.info("Successfully loaded analysis settings from config file.")
            return analysis_config
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load or parse config file {config_path}: {e}")
        return {}

def main():
    """Main execution function"""
    
    # --- Load settings from config file first ---
    analysis_config = load_analysis_config()
    default_modules = analysis_config.get('active_modules', ['all'])
    # The 'target_counties' is more complex, so we handle it post-argparse
    
    parser = argparse.ArgumentParser(
        description='Cascadian Agricultural Land Analysis Framework',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Run full analysis for Cascadia with default settings
  python cascadia_main.py

  # Run with higher H3 resolution and specific modules for two Oregon counties
  python cascadia_main.py --resolution 9 --counties "Benton,Linn" --modules "zoning,water"

  # Check dependencies and run in verbose mode
  python cascadia_main.py --check-deps --verbose
        """
    )
    
    parser.add_argument('--bioregion', type=str, default='Cascadia',
                        choices=['Cascadia', 'Columbia'],
                        help='Bioregion to analyze (default: Cascadia)')
    parser.add_argument('--resolution', type=int, default=8,
                        help='H3 resolution level (1-15, default: 8)')
    parser.add_argument('--output-dir', type=str, default='./output',
                        help='Output directory for results (default: ./output)')
    parser.add_argument('--export-format', type=str, default='geojson',
                        choices=['geojson', 'csv', 'json'],
                        help='Export format for the unified data file (default: geojson)')
    parser.add_argument('--counties', type=str, default=None,
                        help='Comma-separated list of counties to analyze (e.g., "CA:Lassen,Plumas;OR:all"). Overrides config file.')
    parser.add_argument('--modules', type=str, default=None,
                        help='Comma-separated list of modules to run (default: from config file or all)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose debug logging')
    parser.add_argument('--check-deps', action='store_true',
                        help='Check and install required dependencies before running')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose, args.output_dir)
    logger = logging.getLogger(__name__)
    
    # --- Determine final analysis settings ---
    # Command-line args override config file settings
    
    final_modules = args.modules.split(',') if args.modules else default_modules
    if 'all' in final_modules:
        # Define all possible modules here
        final_modules = [
            'zoning', 
            # 'current_use', 'ownership', 'mortgage_debt', 
            # 'improvements', 'surface_water', 'ground_water', 'power_source'
        ]
    
    logger.info(f"Final analysis settings -- Modules to run: {final_modules}")

    if args.counties:
        # Simple parser for the command-line format, e.g., "CA:Lassen,Plumas;OR:all"
        target_counties = {}
        try:
            for state_part in args.counties.split(';'):
                state, counties_str = state_part.split(':')
                target_counties[state.upper()] = counties_str.split(',')
        except ValueError:
            logger.error(f"Invalid format for --counties argument: '{args.counties}'. Use 'ST:county1,county2;ST2:all'.")
            sys.exit(1)
    else:
        target_counties = analysis_config.get('target_counties', {'CA': ['all'], 'OR': ['all'], 'WA': ['all']})
    
    logger.info(f"Final analysis settings -- Modules: {final_modules}, Counties: {target_counties}")
    # --- End settings determination ---

    logger.info("="*80)
    logger.info(f"STARTING {args.bioregion.upper()} AGRICULTURAL LAND ANALYSIS")
    logger.info("="*80)
    
    if args.check_deps and not check_and_install_dependencies():
        logger.critical("Dependency check failed. Cannot proceed. Exiting.")
        sys.exit(1)
        
    if not validate_configuration(args):
        logger.critical("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    try:
        # --- Initialize Modules ---
        # A placeholder mapping to the actual module classes
        # This would be expanded as each module is implemented
        module_class_map = {
            'zoning': GeoInferZoning,
            # 'current_use': GeoInferCurrentUse,
            # 'ownership': GeoInferOwnership,
        }

        # The backend will be initialized with dummy modules first
        # Then we will instantiate the real ones needed for the run
        backend_for_init = CascadianAgriculturalH3Backend(modules={}, base_data_dir=cascadian_dir / 'data')
        
        active_module_instances: Dict[str, BaseAnalysisModule] = {}
        for mod_name in final_modules:
            if mod_name in module_class_map:
                logger.info(f"Initializing module: {mod_name}")
                active_module_instances[mod_name] = module_class_map[mod_name](backend_for_init)
            else:
                logger.warning(f"Module '{mod_name}' is not implemented or mapped. Skipping.")
        
        if not active_module_instances:
            logger.critical("No valid modules were initialized. Exiting.")
            sys.exit(1)
        # --- End Module Initialization ---

        logger.info(f"Initializing {args.bioregion} H3 Backend (Resolution: {args.resolution})")
        # Now, initialize the backend with the real, active modules
        backend = CascadianAgriculturalH3Backend(
            modules=active_module_instances,
            resolution=args.resolution,
            bioregion=args.bioregion,
            target_counties=target_counties,
            base_data_dir=cascadian_dir / 'data'
        )
        
        # Link the modules to the fully initialized backend
        for mod in backend.modules.values():
            mod.backend = backend

        logger.info("Step 1: Running comprehensive analysis across all modules...")
        backend.run_comprehensive_analysis()
        
        logger.info("Step 2: Calculating agricultural redevelopment potential...")
        redevelopment_scores = backend.calculate_agricultural_redevelopment_potential()
        
        logger.info("Step 3: Generating comprehensive summary...")
        summary = backend.get_comprehensive_summary()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir)
        bioregion_lower = args.bioregion.lower()
        
        logger.info("Step 4: Exporting analysis results...")
        
        # Export unified data (includes module data and scores)
        unified_path = output_dir / f"{bioregion_lower}_unified_data_{timestamp}.{args.export_format}"
        backend.export_unified_data(str(unified_path), args.export_format)
        
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
        
        logger.info("Step 5: Generating analysis report and dashboard...")
        
        # Generate Markdown report
        report_path = output_dir / f"{bioregion_lower}_analysis_report_{timestamp}.md"
        generate_analysis_report(summary, report_path)

        # Generate interactive HTML dashboard
        dashboard_path = output_dir / f"{bioregion_lower}_dashboard_{timestamp}.html"
        backend.generate_interactive_dashboard(str(dashboard_path))
        
        print_summary(summary)
        
        logger.info("="*80)
        logger.info("ANALYSIS COMPLETED SUCCESSFULLY!")
        logger.info(f"All results saved to: {output_dir.resolve()}")
        logger.info("="*80)
        
    except ImportError as e:
        logger.critical(f"Failed to import a required module: {e}. Please check sys.path and module availability.", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.critical(f"A critical error occurred during analysis: {e}", exc_info=True)
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def generate_analysis_report(summary: Dict[str, Any], output_path: Path) -> None:
    """
    Generate a comprehensive analysis report in Markdown format.
    
    Args:
        summary: Comprehensive summary data from the backend.
        output_path: Path to save the Markdown file.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating analysis report to {output_path}...")
    
    bioregion = summary.get('bioregion', 'Unknown Bioregion')
    bioregion_desc = {
        'Cascadia': 'encompassing northern California and all of Oregon.',
        'Columbia': 'encompassing the Columbia River Basin region.'
    }.get(bioregion, f'in the {bioregion} bioregion.')

    def fmt(value):
        return f"{value:,}" if isinstance(value, (int, float)) else str(value)

    rp = summary.get('redevelopment_potential', {})
    
    report = f"""# {bioregion} Agricultural Land Analysis Report
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 1. Executive Summary
This report presents a comprehensive agricultural land analysis for the **{bioregion}** bioregion, {bioregion_desc}
The analysis utilized H3 spatial indexing at resolution **{summary.get('h3_resolution', 'N/A')}** to integrate and assess data from **{len(summary.get('modules_analyzed', []))} specialized modules**. The key output is a redevelopment potential score for each hexagonal area, identifying promising locations for agricultural transition.

## 2. Analysis Overview
- **Total Hexagons Analyzed:** {fmt(summary.get('total_hexagons', 0))}
- **H3 Resolution:** {summary.get('h3_resolution', 'N/A')}
- **Modules Executed:** `{'`, `'.join(summary.get('modules_analyzed', []))}`

## 3. Redevelopment Potential Insights
- **Mean Redevelopment Score:** {rp.get('mean_score', 0):.3f}
- **Median Redevelopment Score:** {rp.get('median_score', 0):.3f}
- **High Potential Areas (>0.75):** {fmt(rp.get('high_potential_hexagons', 0))} hexagons
- **Low Potential Areas (<0.25):** {fmt(rp.get('low_potential_hexagons', 0))} hexagons

## 4. Module Coverage
This section details the data coverage for each analysis module across the target hexagons.

| Module                    | Processed Hexagons | Coverage (%) |
|---------------------------|--------------------|--------------|
"""
    
    module_summaries = summary.get('module_summaries', {})
    for name, data in module_summaries.items():
        report += (f"| {name.replace('_', ' ').title():<25} | "
                   f"{fmt(data.get('processed_hexagons', 0)):<18} | "
                   f"{data.get('coverage', 0):<12.2f} |\n")

    report += """
## 5. Technical Framework & Methodology
The analysis is built on a **Unified H3 Backend**, which standardizes diverse geospatial datasets into a common hexagonal grid. This enables:
- Seamless cross-border (California/Oregon) analysis.
- Efficient spatial queries and data aggregation.
- Scalable processing for large and complex datasets.
- Consistent and comparable reporting units.

Redevelopment potential is calculated as a weighted composite of scores from each module, including zoning, water security, infrastructure, and financial factors.

## 6. Recommendations
1.  **Focus on High-Potential Areas:** Prioritize further investigation and outreach in hexagons with redevelopment scores **> 0.75**.
2.  **Improve Data Gaps:** Address modules with lower coverage by seeking alternative data sources or partnerships.
3.  **Utilize Interactive Dashboard:** Leverage the generated HTML dashboard for detailed, visual exploration of results.

---
*This report was automatically generated by the GEO-INFER Cascadian Analysis Framework.*
"""
    
    with open(output_path, 'w') as f:
        f.write(report)
    logger.info("Successfully generated Markdown analysis report.")

def print_summary(summary: Dict[str, Any]) -> None:
    """
    Print a concise analysis summary to the console.
    
    Args:
        summary: Comprehensive summary data from the backend.
    """
    def fmt(value):
        return f"{value:,}" if isinstance(value, (int, float)) else str(value)
    
    bioregion = summary.get('bioregion', 'Unknown').upper()
    print("\n" + "="*80)
    print(f"ANALYSIS SUMMARY: {bioregion}")
    print("="*80)
    
    rp = summary.get('redevelopment_potential', {})
    print(f"  H3 Resolution: {summary.get('h3_resolution', 'N/A')}")
    print(f"  Total Hexagons Analyzed: {fmt(summary.get('total_hexagons', 0))}\n")
    
    print("  Redevelopment Potential:")
    print(f"    - Mean Score: {rp.get('mean_score', 0):.3f}")
    print(f"    - High Potential (>0.75): {fmt(rp.get('high_potential_hexagons', 0))} hexagons")
    print(f"    - Low Potential (<0.25): {fmt(rp.get('low_potential_hexagons', 0))} hexagons\n")
    
    print("  Module Coverage:")
    module_summaries = summary.get('module_summaries', {})
    for name, data in module_summaries.items():
        print(f"    - {name.replace('_', ' ').title():<20}: {data.get('coverage', 0):.2f}%")
        
    print("="*80)

if __name__ == "__main__":
    main() 