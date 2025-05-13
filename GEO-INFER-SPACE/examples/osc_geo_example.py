#!/usr/bin/env python3
"""
Example script demonstrating the use of the OSC-GEO module.

This script shows how to:
1. Set up OSC-GEO by cloning required repositories
2. Start the H3 grid service
3. Load geospatial data into an H3 grid system
4. Convert between GeoJSON and H3 formats
"""

import os
import sys
import logging
import tempfile
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("osc_geo_example")

# Import OSC-GEO functionality
try:
    from geo_infer_space.osc_geo import (
        setup_osc_geo,
        create_h3_grid_manager,
        create_h3_data_loader,
        load_data_to_h3_grid
    )
    from geo_infer_space.osc_geo.utils import (
        h3_to_geojson,
        geojson_to_h3
    )
except ImportError:
    logger.error("Failed to import geo_infer_space.osc_geo module")
    logger.error("Make sure GEO-INFER-SPACE is installed and in your Python path")
    sys.exit(1)

def main():
    """Main function demonstrating OSC-GEO module usage."""
    logger.info("Starting OSC-GEO example")
    
    # Step 1: Set up OSC-GEO by cloning required repositories
    logger.info("Setting up OSC-GEO...")
    try:
        results = setup_osc_geo()
        success = all(results.values())
        
        if success:
            logger.info("OSC-GEO set up successfully")
        else:
            failed_repos = [repo for repo, status in results.items() if not status]
            logger.warning(f"Failed to clone repositories: {', '.join(failed_repos)}")
            logger.warning("Some functionality may not be available")
    except Exception as e:
        logger.error(f"Failed to set up OSC-GEO: {e}")
        logger.error("Continuing with example, but some features may not work")
    
    # Step 2: Start the H3 grid service
    logger.info("Starting H3 grid service...")
    try:
        grid_manager = create_h3_grid_manager(auto_start=True)
        
        if grid_manager.is_server_running():
            logger.info(f"H3 grid service running at: {grid_manager.get_api_url()}")
        else:
            logger.warning("Failed to start H3 grid service")
    except Exception as e:
        logger.error(f"Error with H3 grid service: {e}")
        logger.error("Continuing with example, but some features may not work")
    
    # Step 3: Create a sample GeoJSON for demonstration
    logger.info("Creating sample GeoJSON data...")
    sample_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Sample Area",
                    "value": 42
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-122.4, 37.7],
                            [-122.4, 37.8],
                            [-122.5, 37.8],
                            [-122.5, 37.7],
                            [-122.4, 37.7]
                        ]
                    ]
                }
            }
        ]
    }
    
    # Create a temporary directory for the example
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the sample GeoJSON to a file
        input_file = os.path.join(temp_dir, "sample.geojson")
        with open(input_file, "w") as f:
            json.dump(sample_geojson, f)
        
        logger.info(f"Saved sample GeoJSON to {input_file}")
        
        # Step 4: Load the data into an H3 grid
        output_file = os.path.join(temp_dir, "sample_h3.geojson")
        logger.info(f"Loading data into H3 grid at resolution 8...")
        
        try:
            success = load_data_to_h3_grid(
                input_file=input_file,
                output_file=output_file,
                resolution=8
            )
            
            if success:
                logger.info(f"Data loaded successfully to {output_file}")
            else:
                logger.warning("Failed to load data into H3 grid")
        except Exception as e:
            logger.error(f"Error loading data into H3 grid: {e}")
        
        # Step 5: Convert GeoJSON to H3 directly
        logger.info("Converting GeoJSON to H3 indices...")
        try:
            h3_data = geojson_to_h3(sample_geojson, resolution=9)
            logger.info(f"Converted to {len(h3_data['h3_indices'])} H3 indices at resolution 9")
            
            # Convert back to GeoJSON
            logger.info("Converting H3 indices back to GeoJSON...")
            geojson_result = h3_to_geojson(h3_data["h3_indices"], h3_data["properties"])
            logger.info(f"GeoJSON has {len(geojson_result['features'])} features")
            
            # Save the result
            result_file = os.path.join(temp_dir, "h3_to_geojson.json")
            with open(result_file, "w") as f:
                json.dump(geojson_result, f)
                
            logger.info(f"Saved result to {result_file}")
        except Exception as e:
            logger.error(f"Error during conversion: {e}")
    
    # Step 6: Clean up
    logger.info("Cleaning up...")
    try:
        if 'grid_manager' in locals() and grid_manager.is_server_running():
            grid_manager.stop_server()
            logger.info("H3 grid service stopped")
    except Exception as e:
        logger.error(f"Error stopping H3 grid service: {e}")
    
    logger.info("OSC-GEO example completed")

if __name__ == "__main__":
    main() 