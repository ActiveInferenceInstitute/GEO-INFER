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
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
import traceback

# Add the cascadia directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add import for shared H3 utility
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

def setup_logging(verbose: bool = False, output_dir: str = '.') -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
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
    Check and install required dependencies
    
    Returns:
        True if all dependencies are available
    """
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'h3',
        'numpy',
        'pandas',
        'geopandas',
        'shapely',
        'requests',
        'rasterio',
        'folium'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is available")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ {package} is missing")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Installing missing packages...")
        
        try:
            import subprocess
            import sys
            
            for package in missing_packages:
                logger.info(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"✓ {package} installed successfully")
                
        except Exception as e:
            logger.error(f"Failed to install dependencies: {str(e)}")
            return False
    
    logger.info("All dependencies are available")
    return True

def validate_configuration(args: argparse.Namespace) -> bool:
    """
    Validate configuration and arguments
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        True if configuration is valid
    """
    logger = logging.getLogger(__name__)
    
    # Validate H3 resolution
    if args.resolution < 1 or args.resolution > 15:
        logger.error(f"Invalid H3 resolution: {args.resolution}. Must be between 1 and 15")
        return False
    
    # Validate output directory
    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir.absolute()}")
    except Exception as e:
        logger.error(f"Cannot create output directory {output_dir}: {str(e)}")
        return False
    
    # Validate export format
    valid_formats = ['geojson', 'csv', 'json']
    if args.export_format not in valid_formats:
        logger.error(f"Invalid export format: {args.export_format}. Must be one of {valid_formats}")
        return False
    
    # Validate modules
    valid_modules = [
        'zoning', 'current_use', 'ownership', 'mortgage_debt', 
        'improvements', 'surface_water', 'ground_water', 'power_source'
    ]
    
    if args.modules != 'all':
        requested_modules = [m.strip() for m in args.modules.split(',')]
        invalid_modules = [m for m in requested_modules if m not in valid_modules]
        if invalid_modules:
            logger.error(f"Invalid modules: {', '.join(invalid_modules)}")
            logger.info(f"Valid modules: {', '.join(valid_modules)}")
            return False
    
    logger.info("Configuration validation successful")
    return True

def main():
    """Main execution function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Cascadian Agricultural Land Analysis Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cascadia_main.py --resolution 8 --output-dir ./results
    python cascadia_main.py --counties "Humboldt,Mendocino" --modules "zoning,current_use"
    python cascadia_main.py --check-deps --verbose
        """
    )
    
    parser.add_argument('--bioregion', type=str, default='Cascadia',
                       choices=['Cascadia', 'Columbia'],
                       help='Bioregion to analyze (default: Cascadia)')
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
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose, args.output_dir)
    logger = logging.getLogger(__name__)
    
    logger.info("="*80)
    logger.info(f"{args.bioregion} Agricultural Land Analysis Framework")
    logger.info("="*80)
    
    # Check dependencies by default, or if specifically requested
    if args.check_deps or len(sys.argv) == 1:  # Check deps by default with no args
        if not check_and_install_dependencies():
            logger.error("Dependency check failed. Exiting.")
            sys.exit(1)
    
    # Validate configuration
    if not validate_configuration(args):
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    try:
        # Import the unified backend (after dependency check)
        from unified_backend import CascadianAgriculturalH3Backend
        
        logger.info(f"Initializing {args.bioregion} Agricultural H3 Backend (resolution: {args.resolution})")
        
        # Initialize the backend
        backend = CascadianAgriculturalH3Backend(resolution=args.resolution, bioregion=args.bioregion)
        
        # Run comprehensive analysis
        logger.info("Starting comprehensive agricultural analysis...")
        unified_data = backend.run_comprehensive_analysis()
        
        # Calculate redevelopment potential
        logger.info("Calculating agricultural redevelopment potential...")
        redevelopment_scores = backend.calculate_agricultural_redevelopment_potential()
        
        # Generate comprehensive summary
        logger.info("Generating comprehensive summary...")
        summary = backend.get_comprehensive_summary()
        
        # Create output directory
        output_dir = Path(args.output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export unified data
        bioregion_lower = args.bioregion.lower()
        unified_output_path = output_dir / f"{bioregion_lower}_unified_data_{timestamp}.{args.export_format}"
        logger.info(f"Exporting unified data to {unified_output_path}")
        backend.export_unified_data(str(unified_output_path), args.export_format)
        
        # Export redevelopment scores
        redevelopment_output_path = output_dir / f"{bioregion_lower}_redevelopment_scores_{timestamp}.json"
        logger.info(f"Exporting redevelopment scores to {redevelopment_output_path}")
        with open(redevelopment_output_path, 'w') as f:
            json.dump(redevelopment_scores, f, indent=2)
        
        # Export comprehensive summary
        summary_output_path = output_dir / f"{bioregion_lower}_summary_{timestamp}.json"
        logger.info(f"Exporting comprehensive summary to {summary_output_path}")
        with open(summary_output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate analysis report
        report_output_path = output_dir / f"{bioregion_lower}_analysis_report_{timestamp}.md"
        logger.info(f"Generating analysis report to {report_output_path}")
        generate_analysis_report(summary, redevelopment_scores, report_output_path, args.bioregion)

        # Generate interactive dashboard
        dashboard_output_path = output_dir / f"{bioregion_lower}_dashboard_{timestamp}.html"
        logger.info(f"Generating interactive dashboard to {dashboard_output_path}")
        backend.generate_interactive_dashboard(str(dashboard_output_path))

        # Print summary to console
        print_summary(summary, redevelopment_scores, args.bioregion)
        
        logger.info("="*80)
        logger.info("Analysis completed successfully!")
        logger.info(f"Results saved to: {output_dir.absolute()}")
        logger.info("="*80)
        
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Please ensure all dependencies are installed. Run with --check-deps flag.")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def generate_analysis_report(summary: Dict, redevelopment_scores: Dict, output_path: Path, bioregion: str = 'Cascadia') -> None:
    """
    Generate a comprehensive analysis report in Markdown format
    
    Args:
        summary: Comprehensive summary data
        redevelopment_scores: Redevelopment potential scores
        output_path: Output file path
        bioregion: Bioregion name for the report
    """
    
    bioregion_descriptions = {
        'Cascadia': 'encompassing northern California counties and all of Oregon',
        'Columbia': 'encompassing the Columbia River Basin region'
    }
    
    bioregion_desc = bioregion_descriptions.get(bioregion, f'in the {bioregion} bioregion')
    
    # Helper function to format numbers with commas
    def format_number(value):
        if isinstance(value, (int, float)):
            return f"{value:,}"
        return str(value)
    
    report_content = f"""# {bioregion} Agricultural Land Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report presents the results of a comprehensive agricultural land analysis across the {bioregion} bioregion, {bioregion_desc}. The analysis utilized H3 spatial indexing at resolution {summary.get('h3_resolution', 'Unknown')} to integrate data from 8 specialized modules.

## Analysis Overview

- **Total Hexagons Analyzed:** {format_number(summary.get('total_hexagons', 'Unknown'))}
- **Target Region Coverage:** {format_number(summary.get('target_region_size', 'Unknown'))} hexagons
- **Analysis Modules:** {summary.get('modules_analyzed', 'Unknown')}
- **H3 Resolution:** {summary.get('h3_resolution', 'Unknown')}

## Redevelopment Potential Analysis

- **Mean Redevelopment Score:** {summary.get('redevelopment_potential', {}).get('mean_score', 0):.3f}
- **High Potential Hexagons:** {format_number(summary.get('redevelopment_potential', {}).get('high_potential_hexagons', 0))}
- **Low Potential Hexagons:** {format_number(summary.get('redevelopment_potential', {}).get('low_potential_hexagons', 0))}

## Module Results

"""
    
    module_summaries = summary.get('module_summaries', {})
    
    for module_name, module_summary in module_summaries.items():
        if 'error' not in module_summary:
            report_content += f"""### {module_name.replace('_', ' ').title()} Module

- **Total Hexagons:** {module_summary.get('total_hexagons', 'Unknown')}
- **Status:** Completed Successfully

"""
        else:
            report_content += f"""### {module_name.replace('_', ' ').title()} Module

- **Status:** Error - {module_summary.get('error', 'Unknown error')}

"""
    
    report_content += f"""## Data Sources and Methodology

This analysis integrates data from multiple authoritative sources:

1. **California Sources:**
   - FMMP (Farmland Mapping & Monitoring Program)
   - Land IQ crop mapping
   - ParcelQuest parcel data
   - eWRIMS/CalWATRS water rights

2. **Oregon Sources:**
   - EFU (Exclusive Farm Use) zoning
   - ORMAP parcel system
   - Oregon Water Resources Database

3. **Federal Sources:**
   - USDA NASS CDL (Cropland Data Layer)
   - USDA Economic Research Service
   - USGS National Water Information System

## Technical Framework

The analysis employed H3 hierarchical spatial indexing to enable:
- Unified cross-border analysis
- Efficient spatial operations
- Scalable data processing
- Standardized reporting units

## Recommendations

Based on the analysis results, the following recommendations are provided:

1. **High Potential Areas:** Focus development efforts on hexagons with redevelopment scores > 0.7
2. **Data Quality:** Address data gaps in modules with errors or low confidence scores
3. **Cross-Border Coordination:** Leverage unified H3 framework for California-Oregon planning coordination
4. **Monitoring:** Implement temporal analysis to track changes over time

## Limitations and Future Work

- Some modules operated with limited data availability
- Temporal analysis requires multi-year data integration
- Financial data gaps require specialized acquisition strategies
- Energy infrastructure data needs utility partnerships

---

*This report was generated by the {bioregion} Agricultural Land Analysis Framework*
"""
    
    with open(output_path, 'w') as f:
        f.write(report_content)

def print_summary(summary: Dict, redevelopment_scores: Dict, bioregion: str = 'Cascadia') -> None:
    """
    Print analysis summary to console
    
    Args:
        summary: Comprehensive summary data
        redevelopment_scores: Redevelopment potential scores
        bioregion: Bioregion name for the summary
    """
    
    # Helper function to format numbers with commas
    def format_number(value):
        if isinstance(value, (int, float)):
            return f"{value:,}"
        return str(value)
    
    print("\n" + "="*80)
    print(f"{bioregion.upper()} AGRICULTURAL ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"Total Hexagons Analyzed: {format_number(summary.get('total_hexagons', 'Unknown'))}")
    print(f"H3 Resolution: {summary.get('h3_resolution', 'Unknown')}")
    print(f"Modules Analyzed: {summary.get('modules_analyzed', 'Unknown')}")
    
    redevelopment_potential = summary.get('redevelopment_potential', {})
    print(f"\nRedevelopment Potential:")
    print(f"  Mean Score: {redevelopment_potential.get('mean_score', 0):.3f}")
    print(f"  High Potential: {format_number(redevelopment_potential.get('high_potential_hexagons', 0))} hexagons")
    print(f"  Low Potential: {format_number(redevelopment_potential.get('low_potential_hexagons', 0))} hexagons")
    
    print(f"\nModule Status:")
    module_summaries = summary.get('module_summaries', {})
    for module_name, module_summary in module_summaries.items():
        status = "✓ SUCCESS" if 'error' not in module_summary else "✗ ERROR"
        hexagons = module_summary.get('total_hexagons', 'Unknown')
        print(f"  {module_name.replace('_', ' ').title()}: {status} ({hexagons} hexagons)")
    
    print("="*80)

if __name__ == "__main__":
    main() 