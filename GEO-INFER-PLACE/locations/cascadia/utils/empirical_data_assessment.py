#!/usr/bin/env python3
"""
Empirical Data Assessment for Del Norte County
==============================================

This script focuses on assessing the quality and sources of empirical data
for Del Norte county agricultural analysis. It provides detailed logging
and validation of data sources to ensure we're working with real empirical
data rather than synthetic/mock data.
"""

import logging
import json
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import os

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'empirical_assessment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EmpiricalDataAssessor:
    """Assesses empirical data quality and sources for Del Norte county."""
    
    def __init__(self):
        self.assessment_results = {}
        
    def assess_data_sources(self):
        """Assess all data sources for empirical quality."""
        logger.info("🔍 Starting empirical data assessment for Del Norte county...")
        
        # Check empirical data files first
        empirical_files = [
            "output/data/empirical_zoning_data.geojson",
            "output/data/empirical_current_use_data.geojson", 
            "output/data/empirical_ownership_data.geojson",
            "output/data/empirical_improvements_data.geojson"
        ]
        
        for empirical_file in empirical_files:
            logger.info(f"\n📊 Assessing empirical data: {empirical_file}")
            self.assess_data_file(Path(empirical_file))
        
        # Also check legacy data directories
        data_dirs = [
            "output/data/zoning",
            "output/data/current_use", 
            "output/data/ownership",
            "output/data/improvements"
        ]
        
        for data_dir in data_dirs:
            logger.info(f"\n📊 Assessing legacy data: {data_dir}")
            self.assess_data_directory(Path(data_dir))
    
    def assess_data_directory(self, data_dir: Path):
        """Assess data in a specific directory."""
        if not data_dir.exists():
            logger.warning(f"   ⚠️ Directory does not exist: {data_dir}")
            return
        
        # Find all data files
        data_files = list(data_dir.glob("*.geojson")) + list(data_dir.glob("*.json"))
        
        if not data_files:
            logger.warning(f"   ⚠️ No data files found in {data_dir}")
            return
        
        logger.info(f"   📁 Found {len(data_files)} data files")
        
        for file_path in data_files:
            logger.info(f"   📄 Analyzing: {file_path.name}")
            self.assess_data_file(file_path)
    
    def assess_data_file(self, file_path: Path):
        """Assess the quality of a data file."""
        try:
            # Check file size
            file_size = file_path.stat().st_size
            logger.info(f"      📏 File size: {file_size:,} bytes")
            
            # Check file type and content
            if file_path.suffix.lower() == '.geojson':
                self.assess_geojson_file(file_path)
            elif file_path.suffix.lower() == '.json':
                self.assess_json_file(file_path)
            else:
                logger.warning(f"      ⚠️ Unknown file type: {file_path.suffix}")
                
        except Exception as e:
            logger.error(f"      ❌ Error assessing file {file_path}: {e}")
    
    def assess_geojson_file(self, file_path: Path):
        """Assess GeoJSON file quality and content."""
        try:
            gdf = gpd.read_file(file_path)
            logger.info(f"      📊 GeoJSON loaded successfully")
            logger.info(f"      📈 Features: {len(gdf)}")
            logger.info(f"      🗺️ CRS: {gdf.crs}")
            
            # Check geometry types
            geom_types = gdf.geometry.geom_type.value_counts()
            logger.info(f"      🔷 Geometry types: {dict(geom_types)}")
            
            # Check properties
            if not gdf.empty:
                properties = [col for col in gdf.columns if col != 'geometry']
                logger.info(f"      📋 Properties: {properties}")
                
                # Sample some values
                for prop in properties[:3]:  # Show first 3 properties
                    if gdf[prop].dtype in ['object', 'string']:
                        unique_values = gdf[prop].value_counts().head(5)
                        logger.info(f"      📝 {prop} sample values: {dict(unique_values)}")
                    else:
                        stats = gdf[prop].describe()
                        logger.info(f"      📊 {prop} statistics: mean={stats['mean']:.3f}, std={stats['std']:.3f}")
            
            # Check for empirical indicators
            self.check_empirical_indicators(gdf, file_path.name)
            
        except Exception as e:
            logger.error(f"      ❌ Error reading GeoJSON: {e}")
    
    def assess_json_file(self, file_path: Path):
        """Assess JSON file quality and content."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"      📊 JSON loaded successfully")
            logger.info(f"      📈 Data type: {type(data)}")
            
            if isinstance(data, dict):
                logger.info(f"      📋 Keys: {list(data.keys())}")
            elif isinstance(data, list):
                logger.info(f"      📈 List length: {len(data)}")
                
        except Exception as e:
            logger.error(f"      ❌ Error reading JSON: {e}")
    
    def check_empirical_indicators(self, gdf: gpd.GeoDataFrame, file_name: str):
        """Check for indicators of empirical vs synthetic data."""
        logger.info(f"      🔍 Checking empirical data indicators...")
        
        empirical_indicators = {
            'realistic_coordinates': False,
            'varied_properties': False,
            'realistic_values': False,
            'data_source_attribution': False,
            'temporal_information': False
        }
        
        # Check coordinate realism
        if not gdf.empty:
            bounds = gdf.total_bounds
            # Del Norte county bounds approximately
            del_norte_bounds = [-124.5, 41.4, -123.5, 42.0]
            if (bounds[0] >= del_norte_bounds[0] and bounds[1] >= del_norte_bounds[1] and
                bounds[2] <= del_norte_bounds[2] and bounds[3] <= del_norte_bounds[3]):
                empirical_indicators['realistic_coordinates'] = True
                logger.info(f"      ✅ Coordinates within Del Norte county bounds")
            else:
                logger.warning(f"      ⚠️ Coordinates outside Del Norte county bounds")
                logger.info(f"      📍 Actual bounds: {bounds}")
        
        # Check property variety
        if not gdf.empty:
            properties = [col for col in gdf.columns if col != 'geometry']
            if len(properties) > 2:
                empirical_indicators['varied_properties'] = True
                logger.info(f"      ✅ Multiple properties found: {len(properties)}")
            
            # Check for realistic values
            for prop in properties:
                if gdf[prop].dtype in ['int64', 'float64']:
                    if gdf[prop].std() > 0:
                        empirical_indicators['realistic_values'] = True
                        logger.info(f"      ✅ Property '{prop}' shows variability")
                        break
        
        # Check for data source attribution
        source_columns = [col for col in gdf.columns if 'source' in col.lower() or 'data' in col.lower()]
        if source_columns:
            empirical_indicators['data_source_attribution'] = True
            logger.info(f"      ✅ Data source attribution found: {source_columns}")
        
        # Check for temporal information
        temporal_columns = [col for col in gdf.columns if any(word in col.lower() for word in ['date', 'year', 'time'])]
        if temporal_columns:
            empirical_indicators['temporal_information'] = True
            logger.info(f"      ✅ Temporal information found: {temporal_columns}")
        
        # Summary
        empirical_score = sum(empirical_indicators.values()) / len(empirical_indicators)
        logger.info(f"      📊 Empirical data score: {empirical_score:.1%}")
        
        if empirical_score >= 0.6:
            logger.info(f"      ✅ {file_name} appears to contain empirical data")
        else:
            logger.warning(f"      ⚠️ {file_name} may contain synthetic/mock data")
    
    def generate_assessment_report(self):
        """Generate a comprehensive assessment report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"empirical_assessment_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write("# Empirical Data Assessment Report\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write("## Summary\n")
            f.write("This report assesses the quality and empirical nature of data sources\n")
            f.write("used in the Del Norte county agricultural analysis.\n\n")
            
            f.write("## Key Findings\n")
            f.write("- Data source validation\n")
            f.write("- Empirical vs synthetic data identification\n")
            f.write("- Spatial variability assessment\n")
            f.write("- Data quality metrics\n\n")
            
            f.write("## Recommendations\n")
            f.write("1. Focus on empirical data sources\n")
            f.write("2. Validate spatial coverage\n")
            f.write("3. Ensure data variability\n")
            f.write("4. Track data provenance\n\n")
        
        logger.info(f"📋 Assessment report generated: {report_path}")

def main():
    """Main function to run the empirical data assessment."""
    logger.info("🚀 Starting Del Norte County Empirical Data Assessment")
    
    assessor = EmpiricalDataAssessor()
    assessor.assess_data_sources()
    assessor.generate_assessment_report()
    
    logger.info("✅ Empirical data assessment completed")

if __name__ == "__main__":
    main() 