#!/usr/bin/env python3
"""
County Boundary Loader for Cascadia Analysis

This utility loads county boundary data from YAML configuration and GeoJSON files,
providing proper geometry objects for H3 polygon_to_cells operations and spatial analysis.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import requests
import tempfile
import zipfile
import io

logger = logging.getLogger(__name__)

class CountyBoundaryLoader:
    """Loads and manages county boundary data for the Cascadia analysis"""
    
    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self.boundaries_config = self._load_boundaries_config()
        self.county_geometries = {}
        
    def _load_boundaries_config(self) -> Dict[str, Any]:
        """Load the county boundaries configuration file"""
        config_path = self.config_dir / "county_boundaries.yaml"
        
        if not config_path.exists():
            logger.warning(f"County boundaries config not found: {config_path}")
            return {}
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded county boundaries configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load county boundaries config: {e}")
            return {}
    
    def get_county_info(self, county_key: str) -> Optional[Dict[str, Any]]:
        """Get county information from configuration"""
        counties = self.boundaries_config.get('counties', {})
        return counties.get(county_key)
    
    def load_county_geometry(self, county_key: str) -> Optional[Polygon]:
        """Load county geometry from GeoJSON file"""
        if county_key in self.county_geometries:
            return self.county_geometries[county_key]
        
        county_info = self.get_county_info(county_key)
        if not county_info:
            logger.error(f"County info not found for: {county_key}")
            return None
        
        geometry_file = county_info.get('geometry_file')
        if not geometry_file:
            logger.error(f"No geometry file specified for county: {county_key}")
            return None
        
        geometry_path = self.config_dir / geometry_file
        
        try:
            if geometry_path.exists():
                # Load from local GeoJSON file
                gdf = gpd.read_file(geometry_path)
                if not gdf.empty:
                    geometry = gdf.iloc[0].geometry
                    if isinstance(geometry, (Polygon, MultiPolygon)):
                        self.county_geometries[county_key] = geometry
                        logger.info(f"Loaded geometry for {county_key} from {geometry_path}")
                        return geometry
                    else:
                        logger.error(f"Invalid geometry type for {county_key}: {type(geometry)}")
                        return None
                else:
                    logger.error(f"Empty GeoJSON file for {county_key}")
                    return None
            else:
                logger.warning(f"Geometry file not found: {geometry_path}")
                # Try to create from bounds
                return self._create_geometry_from_bounds(county_info)
                
        except Exception as e:
            logger.error(f"Failed to load geometry for {county_key}: {e}")
            return None
    
    def _create_geometry_from_bounds(self, county_info: Dict[str, Any]) -> Optional[Polygon]:
        """Create a simple polygon from county bounds"""
        bounds = county_info.get('bounds', {})
        if not bounds:
            logger.error("No bounds information available")
            return None
        
        try:
            # Create a simple bounding box polygon
            west = bounds.get('west', -121.5)
            east = bounds.get('east', -119.5)
            south = bounds.get('south', 40.0)
            north = bounds.get('north', 41.2)
            
            polygon = Polygon([
                (west, south),
                (east, south),
                (east, north),
                (west, north),
                (west, south)
            ])
            
            county_key = county_info.get('name', 'unknown').lower().replace(' ', '_')
            self.county_geometries[county_key] = polygon
            logger.info(f"Created geometry from bounds for {county_key}")
            return polygon
            
        except Exception as e:
            logger.error(f"Failed to create geometry from bounds: {e}")
            return None
    
    def download_county_boundary(self, county_key: str) -> bool:
        """Download county boundary from official sources"""
        county_info = self.get_county_info(county_key)
        if not county_info:
            logger.error(f"County info not found for: {county_key}")
            return False
        
        data_sources = county_info.get('data_sources', {})
        primary_source = data_sources.get('primary', {})
        
        if not primary_source:
            logger.error(f"No primary data source for {county_key}")
            return False
        
        url = primary_source.get('url')
        format_type = primary_source.get('format')
        
        if not url or not format_type:
            logger.error(f"Invalid data source configuration for {county_key}")
            return False
        
        try:
            logger.info(f"Downloading boundary data for {county_key} from {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if format_type == 'shapefile':
                return self._process_shapefile(response.content, county_key)
            elif format_type == 'geojson':
                return self._process_geojson(response.content, county_key)
            else:
                logger.error(f"Unsupported format: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to download boundary for {county_key}: {e}")
            return False
    
    def _process_shapefile(self, content: bytes, county_key: str) -> bool:
        """Process downloaded shapefile content"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_path = temp_path / "county_boundary.zip"
                
                # Save zip content
                with open(zip_path, 'wb') as f:
                    f.write(content)
                
                # Extract shapefile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find the .shp file
                shp_files = list(temp_path.glob("*.shp"))
                if not shp_files:
                    logger.error("No shapefile found in downloaded content")
                    return False
                
                # Load with geopandas
                gdf = gpd.read_file(shp_files[0])
                
                # Filter for the specific county if needed
                county_info = self.get_county_info(county_key)
                fips_code = county_info.get('fips_code')
                
                if fips_code and 'GEOID' in gdf.columns:
                    gdf = gdf[gdf['GEOID'] == fips_code]
                
                if not gdf.empty:
                    geometry = gdf.iloc[0].geometry
                    self.county_geometries[county_key] = geometry
                    
                    # Save to local file
                    geometry_file = county_info.get('geometry_file', f"{county_key}_boundary.geojson")
                    geometry_path = self.config_dir / geometry_file
                    gdf.to_file(geometry_path, driver='GeoJSON')
                    
                    logger.info(f"Successfully processed and saved boundary for {county_key}")
                    return True
                else:
                    logger.error(f"No geometry found for {county_key}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to process shapefile for {county_key}: {e}")
            return False
    
    def _process_geojson(self, content: bytes, county_key: str) -> bool:
        """Process downloaded GeoJSON content"""
        try:
            # Parse GeoJSON
            geojson_data = json.loads(content.decode('utf-8'))
            
            # Load with geopandas
            gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
            
            # Filter for the specific county if needed
            county_info = self.get_county_info(county_key)
            fips_code = county_info.get('fips_code')
            
            if fips_code and 'GEOID' in gdf.columns:
                gdf = gdf[gdf['GEOID'] == fips_code]
            
            if not gdf.empty:
                geometry = gdf.iloc[0].geometry
                self.county_geometries[county_key] = geometry
                
                # Save to local file
                geometry_file = county_info.get('geometry_file', f"{county_key}_boundary.geojson")
                geometry_path = self.config_dir / geometry_file
                gdf.to_file(geometry_path, driver='GeoJSON')
                
                logger.info(f"Successfully processed and saved boundary for {county_key}")
                return True
            else:
                logger.error(f"No geometry found for {county_key}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process GeoJSON for {county_key}: {e}")
            return False
    
    def get_all_county_geometries(self, target_counties: Dict[str, List[str]]) -> Dict[str, Polygon]:
        """Get geometries for all target counties"""
        geometries = {}
        
        for state, counties in target_counties.items():
            if counties == ['all'] or 'all' in counties:
                # Get all counties for this state
                state_counties = [key for key in self.boundaries_config.get('counties', {}).keys() 
                                if key.startswith(f"{state.lower()}_")]
            else:
                # Get specific counties
                state_counties = [f"{state.lower()}_{county.lower().replace(' ', '_')}" 
                                for county in counties]
            
            for county_key in state_counties:
                geometry = self.load_county_geometry(county_key)
                if geometry:
                    geometries[county_key] = geometry
                else:
                    logger.warning(f"Could not load geometry for {county_key}")
        
        return geometries
    
    def validate_geometry(self, geometry: Polygon) -> bool:
        """Validate that a geometry is suitable for H3 polygon_to_cells"""
        if not geometry.is_valid:
            logger.warning("Geometry is not valid")
            return False
        
        if geometry.is_empty:
            logger.warning("Geometry is empty")
            return False
        
        if geometry.area < 0.001:  # Very small area
            logger.warning("Geometry area is too small")
            return False
        
        return True

def create_county_boundary_loader() -> CountyBoundaryLoader:
    """Factory function to create a county boundary loader"""
    config_dir = Path(__file__).parent
    return CountyBoundaryLoader(config_dir)

if __name__ == "__main__":
    # Test the county boundary loader
    logging.basicConfig(level=logging.INFO)
    
    loader = create_county_boundary_loader()
    
    # Test loading Lassen County
    lassen_geometry = loader.load_county_geometry('ca_lassen')
    if lassen_geometry:
        print(f"Successfully loaded Lassen County geometry: {lassen_geometry}")
        print(f"Geometry type: {type(lassen_geometry)}")
        print(f"Geometry area: {lassen_geometry.area}")
    else:
        print("Failed to load Lassen County geometry") 