#!/usr/bin/env python3
"""
Basic data ingestion example for GEO-INFER-DATA.

This example demonstrates how to use the MultiSourceDataIngestion class
to ingest geospatial data from multiple sources including satellite imagery,
sensor networks, and crowdsourced data.

Usage:
    python basic_ingestion_example.py

Requirements:
    - GEO-INFER-DATA package installed
    - Required dependencies (geopandas, pandas, numpy, etc.)
"""

import asyncio
import logging
from pathlib import Path


from geo_infer_data.core.ingestion import MultiSourceDataIngestion


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main example function."""
    logger.info("Starting basic data ingestion example")

    # Initialize ingestion system
    ingestion = MultiSourceDataIngestion(
        data_sources=["satellite", "sensors", "crowdsourced"],
        format_detection="automatic",
        validation_enabled=True,
        quality_threshold=0.8,
        parallel_processing=True,
        max_workers=4,
    )

    logger.info("Initialized ingestion system")

    # Configure a satellite source request for the ingestion pipeline
    satellite_data = {
        "bbox": [-122.5, 37.7, -122.3, 37.9],  # San Francisco area
        "date_range": "2023-01-01/2023-01-31",
        "bands": ["red", "green", "blue", "nir"],
        "resolution": 30.0,
        "satellite": "Landsat-8",
    }

    # Configure a sensor source request for the ingestion pipeline
    sensor_data = {
        "time_range": "2023-01-01/2023-01-31",
        "sensor_types": ["temperature", "humidity", "air_quality"],
        "locations": [
            {"lat": 37.7749, "lon": -122.4194, "id": "sensor_001"},
            {"lat": 37.7849, "lon": -122.4094, "id": "sensor_002"},
            {"lat": 37.7649, "lon": -122.4294, "id": "sensor_003"},
        ],
    }

    # Configure a crowdsourced source request for the ingestion pipeline
    crowdsourced_data = {
        "category": "environment",
        "time_range": "2023-01-01/2023-01-31",
        "report_types": ["air_quality", "noise", "traffic"],
        "max_reports": 1000,
    }

    logger.info("Configured source requests for ingestion")

    # Ingest data from multiple sources
    try:
        logger.info("Starting multi-source data ingestion")

        ingestion_result = await ingestion.ingest_multi_source(
            satellite=satellite_data,
            sensors=sensor_data,
            crowdsourced=crowdsourced_data,
        )

        logger.info("Ingestion completed successfully")
        logger.info(
            f"Sources processed: {ingestion_result['ingestion_metadata']['sources_processed']}"
        )
        logger.info(
            f"Validation enabled: {ingestion_result['ingestion_metadata']['validation_enabled']}"
        )

        # Print ingestion results
        for source_name, source_data in ingestion_result["ingested_data"].items():
            if "error" not in source_data:
                logger.info(f"✓ Successfully ingested {source_name} data")
                if "validation" in source_data:
                    validation = source_data["validation"]
                    logger.info(
                        f"  Quality score: {validation.score:.2f} ({validation.status})"
                    )
            else:
                logger.error(
                    f"✗ Failed to ingest {source_name}: {source_data['error']}"
                )

        # Validate and clean data
        logger.info("Validating and cleaning ingested data")

        cleaned_result = await ingestion.validate_and_clean(ingestion_result)

        logger.info("Data validation and cleaning completed")
        logger.info(
            f"Sources cleaned: {cleaned_result['cleaning_metadata']['sources_cleaned']}"
        )

        # Generate quality report
        logger.info("Generating comprehensive quality report")

        quality_report = ingestion.generate_quality_report(cleaned_result)

        logger.info("Quality Report:")
        logger.info(f"  Overall Score: {quality_report['overall_score']:.2f}")
        logger.info(f"  Quality Threshold: {quality_report['quality_threshold']:.2f}")
        logger.info(f"  Validation Passed: {quality_report['validation_passed']}")

        for source, score in quality_report["source_scores"].items():
            logger.info(f"  {source}: {score:.2f}")

        if quality_report["recommendations"]:
            logger.info("Recommendations:")
            for rec in quality_report["recommendations"]:
                logger.info(f"  - {rec}")

        # Save results
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Save ingestion results
        with open(output_dir / "ingestion_results.json", "w") as f:
            # Convert datetime objects to strings for JSON serialization
            import json

            json_data = json.dumps(ingestion_result, indent=2, default=str)
            f.write(json_data)

        # Save quality report
        with open(output_dir / "quality_report.json", "w") as f:
            json_data = json.dumps(quality_report, indent=2, default=str)
            f.write(json_data)

        logger.info(f"Results saved to {output_dir}")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise

    logger.info("Basic ingestion example completed successfully")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
