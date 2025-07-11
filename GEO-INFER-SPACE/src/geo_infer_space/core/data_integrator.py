#!/usr/bin/env python3
"""
General Data Integrator Module

This module provides capabilities for integrating data from multiple sources
into a unified geospatial dataset.
"""
import logging
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class DataIntegrator:
    """
    Integrates data from multiple sources into a unified geospatial dataset.
    """
    def __init__(self, sources: List[Dict[str, str]]):
        """
        Initialize the integrator with data sources.
        
        Args:
            sources: List of data sources with 'name' and 'path'
        """
        self.sources = sources
        self.integrated_data: gpd.GeoDataFrame = gpd.GeoDataFrame()
        
    def integrate_data(self) -> gpd.GeoDataFrame:
        """
        Integrate all data sources.
        
        Returns:
            Integrated GeoDataFrame
        """
        dataframes = []
        for source in self.sources:
            try:
                if source['path'].endswith('.geojson'):
                    df = gpd.read_file(source['path'])
                elif source['path'].endswith('.csv'):
                    df = pd.read_csv(source['path'])
                    if 'geometry' in df.columns:
                        df = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geometry']))
                else:
                    continue
                
                df['source'] = source['name']
                dataframes.append(df)
            except Exception as e:
                logger.error(f"Failed to load {source['name']}: {e}")
        
        if dataframes:
            self.integrated_data = gpd.GeoDataFrame(pd.concat(dataframes, ignore_index=True))
        return self.integrated_data

    def export_integrated_data(self, output_path: Path, format: str = 'geojson') -> None:
        """
        Export integrated data.
        
        Args:
            output_path: Path to save file
            format: Output format ('geojson', 'shp', etc.)
        """
        if not self.integrated_data.empty:
            self.integrated_data.to_file(output_path, driver=format.upper())
            logger.info(f"Exported integrated data to {output_path}")
        else:
            logger.warning("No data to export") 