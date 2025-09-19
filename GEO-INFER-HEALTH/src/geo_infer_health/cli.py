#!/usr/bin/env python3
"""
Command Line Interface for GEO-INFER-HEALTH module.

Provides command-line tools for running health analysis, data processing,
and API server management.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

import uvicorn
from loguru import logger

# Add the src directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_infer_health.api import router
from geo_infer_health.core import (
    DiseaseHotspotAnalyzer,
    HealthcareAccessibilityAnalyzer,
    EnvironmentalHealthAnalyzer
)
from geo_infer_health.utils.config import load_config
from geo_infer_health.utils.logging import setup_logging


def setup_cli():
    """Set up the command line interface."""
    parser = argparse.ArgumentParser(
        description="GEO-INFER-HEALTH: Geospatial Health Analytics Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the API server
  geo-infer-health serve --host 0.0.0.0 --port 8000

  # Run disease hotspot analysis
  geo-infer-health analyze hotspots --input data/disease_reports.geojson

  # Run healthcare accessibility analysis
  geo-infer-health analyze accessibility --facilities hospitals.geojson --population census.geojson

  # Process environmental health data
  geo-infer-health analyze environment --air-quality pm25.tif --population census.geojson
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/health_config.yaml',
        help='Path to configuration file'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start the API server')
    serve_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    serve_parser.add_argument('--workers', type=int, default=1, help='Number of workers')
    serve_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run health analysis')
    analyze_subparsers = analyze_parser.add_subparsers(dest='analysis_type', help='Analysis type')

    # Disease hotspots
    hotspots_parser = analyze_subparsers.add_parser('hotspots', help='Disease hotspot analysis')
    hotspots_parser.add_argument('--input', required=True, help='Input disease reports file')
    hotspots_parser.add_argument('--population', help='Population data file')
    hotspots_parser.add_argument('--output', default='hotspots.geojson', help='Output file')
    hotspots_parser.add_argument('--threshold', type=int, default=5, help='Case threshold for hotspots')
    hotspots_parser.add_argument('--radius', type=float, default=1.0, help='Analysis radius in km')

    # Healthcare accessibility
    accessibility_parser = analyze_subparsers.add_parser('accessibility', help='Healthcare accessibility analysis')
    accessibility_parser.add_argument('--facilities', required=True, help='Healthcare facilities file')
    accessibility_parser.add_argument('--population', required=True, help='Population data file')
    accessibility_parser.add_argument('--output', default='accessibility.geojson', help='Output file')
    accessibility_parser.add_argument('--method', choices=['distance', 'gravity', '2sfca'], default='distance', help='Accessibility method')

    # Environmental health
    environment_parser = analyze_subparsers.add_parser('environment', help='Environmental health analysis')
    environment_parser.add_argument('--air-quality', help='Air quality data file')
    environment_parser.add_argument('--water-quality', help='Water quality data file')
    environment_parser.add_argument('--population', required=True, help='Population data file')
    environment_parser.add_argument('--output', default='env_health.geojson', help='Output file')

    # Batch processing
    batch_parser = subparsers.add_parser('batch', help='Batch processing of multiple files')
    batch_parser.add_argument('--config', required=True, help='Batch processing configuration file')
    batch_parser.add_argument('--output-dir', default='output', help='Output directory')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data files')
    validate_parser.add_argument('--input', required=True, help='Input file to validate')
    validate_parser.add_argument('--schema', help='Schema file for validation')
    validate_parser.add_argument('--type', choices=['disease', 'facility', 'population', 'environment'], help='Data type')

    return parser


def main():
    """Main CLI entry point."""
    parser = setup_cli()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Setup logging
    setup_logging(level=args.log_level, verbose=args.verbose)

    try:
        # Load configuration
        config = load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")

        # Execute command
        if args.command == 'serve':
            run_server(args, config)
        elif args.command == 'analyze':
            run_analysis(args, config)
        elif args.command == 'batch':
            run_batch_processing(args, config)
        elif args.command == 'validate':
            run_validation(args, config)
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_server(args, config):
    """Run the API server."""
    logger.info(f"Starting GEO-INFER-HEALTH API server on {args.host}:{args.port}")

    # Import FastAPI app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(
        title="GEO-INFER-HEALTH API",
        description="Spatial Health Analytics and Epidemiological Intelligence",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"message": "GEO-INFER-HEALTH API", "version": "1.0.0"}

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        log_level=args.log_level.lower()
    )


def run_analysis(args, config):
    """Run health analysis."""
    logger.info(f"Running {args.analysis_type} analysis")

    if args.analysis_type == 'hotspots':
        run_hotspot_analysis(args, config)
    elif args.analysis_type == 'accessibility':
        run_accessibility_analysis(args, config)
    elif args.analysis_type == 'environment':
        run_environment_analysis(args, config)
    else:
        logger.error(f"Unknown analysis type: {args.analysis_type}")


def run_hotspot_analysis(args, config):
    """Run disease hotspot analysis."""
    try:
        # Load disease reports
        import geopandas as gpd
        reports_gdf = gpd.read_file(args.input)
        logger.info(f"Loaded {len(reports_gdf)} disease reports")

        # Convert to internal format
        from geo_infer_health.models import DiseaseReport, Location
        reports = []
        for _, row in reports_gdf.iterrows():
            location = Location(
                latitude=row.geometry.y,
                longitude=row.geometry.x
            )
            report = DiseaseReport(
                report_id=str(row.get('report_id', f"report_{len(reports)}")),
                disease_code=row.get('disease_code', 'UNKNOWN'),
                location=location,
                report_date=row.get('report_date', None),
                case_count=int(row.get('case_count', 1))
            )
            reports.append(report)

        # Load population data if provided
        population_data = None
        if args.population:
            pop_gdf = gpd.read_file(args.population)
            from geo_infer_health.models import PopulationData
            population_data = []
            for _, row in pop_gdf.iterrows():
                pop_data = PopulationData(
                    area_id=str(row.get('area_id', f"area_{len(population_data)}")),
                    population_count=int(row.get('population', 0))
                )
                population_data.append(pop_data)
            logger.info(f"Loaded {len(population_data)} population areas")

        # Run analysis
        analyzer = DiseaseHotspotAnalyzer(reports=reports, population_data=population_data)
        hotspots = analyzer.identify_simple_hotspots(
            threshold_case_count=args.threshold,
            scan_radius_km=args.radius
        )

        # Save results
        import json
        with open(args.output, 'w') as f:
            json.dump(hotspots, f, indent=2)

        logger.info(f"Found {len(hotspots)} hotspots, saved to {args.output}")

    except Exception as e:
        logger.error(f"Hotspot analysis failed: {e}")
        raise


def run_accessibility_analysis(args, config):
    """Run healthcare accessibility analysis."""
    try:
        # Load facilities and population data
        import geopandas as gpd

        facilities_gdf = gpd.read_file(args.facilities)
        population_gdf = gpd.read_file(args.population)

        logger.info(f"Loaded {len(facilities_gdf)} facilities")
        logger.info(f"Loaded {len(population_gdf)} population areas")

        # Convert to internal format
        from geo_infer_health.models import HealthFacility, PopulationData, Location

        facilities = []
        for _, row in facilities_gdf.iterrows():
            location = Location(
                latitude=row.geometry.y,
                longitude=row.geometry.x
            )
            facility = HealthFacility(
                facility_id=str(row.get('facility_id', f"facility_{len(facilities)}")),
                name=row.get('name', 'Unknown'),
                facility_type=row.get('facility_type', 'Unknown'),
                location=location,
                capacity=int(row.get('capacity', 0)) if row.get('capacity') else None
            )
            facilities.append(facility)

        population_data = []
        for _, row in population_gdf.iterrows():
            pop_data = PopulationData(
                area_id=str(row.get('area_id', f"area_{len(population_data)}")),
                population_count=int(row.get('population', 0))
            )
            population_data.append(pop_data)

        # Run analysis
        analyzer = HealthcareAccessibilityAnalyzer(facilities=facilities, population_data=population_data)

        # For now, just calculate basic statistics
        total_facilities = len(facilities)
        total_population = sum(p.population_count for p in population_data)
        ratio = total_facilities / total_population * 1000 if total_population > 0 else 0

        results = {
            "total_facilities": total_facilities,
            "total_population": total_population,
            "facility_ratio_per_1000": ratio,
            "method": args.method
        }

        # Save results
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Accessibility analysis completed, saved to {args.output}")

    except Exception as e:
        logger.error(f"Accessibility analysis failed: {e}")
        raise


def run_environment_analysis(args, config):
    """Run environmental health analysis."""
    try:
        # Load environmental and population data
        import geopandas as gpd

        population_gdf = gpd.read_file(args.population)
        logger.info(f"Loaded {len(population_gdf)} population areas")

        # Convert population data
        from geo_infer_health.models import PopulationData
        population_data = []
        for _, row in population_gdf.iterrows():
            pop_data = PopulationData(
                area_id=str(row.get('area_id', f"area_{len(population_data)}")),
                population_count=int(row.get('population', 0))
            )
            population_data.append(pop_data)

        results = {
            "analysis_type": "environmental_health",
            "population_areas": len(population_data),
            "total_population": sum(p.population_count for p in population_data)
        }

        # Add air quality analysis if provided
        if args.air_quality:
            results["air_quality_file"] = args.air_quality
            logger.info("Air quality analysis would be implemented here")

        # Add water quality analysis if provided
        if args.water_quality:
            results["water_quality_file"] = args.water_quality
            logger.info("Water quality analysis would be implemented here")

        # Save results
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Environmental health analysis completed, saved to {args.output}")

    except Exception as e:
        logger.error(f"Environmental health analysis failed: {e}")
        raise


def run_batch_processing(args, config):
    """Run batch processing of multiple files."""
    logger.info(f"Running batch processing with config: {args.config}")
    # Implementation would go here
    logger.warning("Batch processing not yet implemented")


def run_validation(args, config):
    """Validate data files."""
    logger.info(f"Validating file: {args.input}")
    try:
        import geopandas as gpd
        gdf = gpd.read_file(args.input)

        # Basic validation
        if gdf.empty:
            logger.error("File contains no data")
            return

        if gdf.crs is None:
            logger.warning("File has no coordinate reference system")

        logger.info(f"Validation passed for {args.input}")
        logger.info(f"Features: {len(gdf)}, Columns: {list(gdf.columns)}")

    except Exception as e:
        logger.error(f"Validation failed: {e}")


if __name__ == "__main__":
    main()
