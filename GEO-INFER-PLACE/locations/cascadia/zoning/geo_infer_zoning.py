"""
GeoInfer Zoning Module

This module performs H3-based analysis of agricultural zoning data by
intelligently classifying and standardizing data from multiple state sources.
"""
import logging
from typing import Dict, List, Any
import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd # Added missing import for pandas

from .data_sources import CascadianZoningDataSources
from utils_h3 import h3_to_geo_boundary

logger = logging.getLogger(__name__)

class GeoInferZoning:
    """
    Processes and analyzes multi-source agricultural zoning data, standardizing
    classifications and assessing redevelopment potential.
    """

    def __init__(self, resolution: int):
        self.resolution = resolution
        self.data_source = CascadianZoningDataSources()
        # Define a standardized internal schema for agricultural zoning
        self.ZONING_SCHEMA = {
            'PRIME_AG': 'Prime Agricultural Land',
            'IMPORTANT_AG': 'Farmland of Statewide or Local Importance',
            'GRAZING': 'Grazing Land',
            'RURAL_RESIDENTIAL': 'Rural Residential',
            'MIXED_FARM_FOREST': 'Mixed Farm and Forest Land',
            'URBAN': 'Urban or Built-up Land',
            'OTHER': 'Other Land'
        }
        logger.info(f"Initialized GeoInferZoning with resolution {self.resolution}")

    def _find_col(self, df, potential_names):
        """Finds the first matching column name from a list of potential names."""
        for name in potential_names:
            if name in df.columns and not df[name].isnull().all():
                return name
        return None

    def _classify_ca_fmmp(self, row: pd.Series, class_col: str) -> str:
        """Classifies a row of California FMMP data into the standard schema."""
        val = row[class_col].lower()
        if 'prime farmland' in val:
            return 'PRIME_AG'
        if 'farmland of statewide importance' in val or 'farmland of local importance' in val:
            return 'IMPORTANT_AG'
        if 'unique farmland' in val:
            return 'IMPORTANT_AG'
        if 'grazing land' in val:
            return 'GRAZING'
        if 'urban and built-up land' in val:
            return 'URBAN'
        return 'OTHER'

    def _classify_or_dlcd(self, row: pd.Series, class_col: str) -> str:
        """Classifies a row of Oregon DLCD data into the standard schema."""
        val = str(row[class_col]).upper()
        # Exclusive Farm Use (EFU) is a common prime ag designation in Oregon
        if 'EFU' in val or 'EXCLUSIVE FARM USE' in val:
            return 'PRIME_AG'
        if 'FARM' in val or 'AGRICULTURE' in val:
            return 'IMPORTANT_AG'
        if 'FOREST' in val and 'FARM' in val:
            return 'MIXED_FARM_FOREST'
        if 'RURAL RESIDENTIAL' in val or val.startswith('RR'):
            return 'RURAL_RESIDENTIAL'
        return 'OTHER'

    def _classify_wa_king(self, row: pd.Series, class_col: str) -> str:
        """Classifies a row of Washington King County data into the standard schema."""
        val = str(row[class_col]).upper()
        # King County uses 'A' for agricultural zones
        if val.startswith('A-'):
            return 'IMPORTANT_AG'
        if val.startswith('RA-'): # Rural Area
            return 'RURAL_RESIDENTIAL'
        if val.startswith('F'): # Forest
            return 'MIXED_FARM_FOREST'
        if val in ['UR', 'R-']: # Urban Residential
            return 'URBAN'
        return 'OTHER'

    def _classify_zoning(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Applies the correct classification function based on the data source."""
        if gdf.empty:
            return gdf

        source = gdf['source'].iloc[0]
        logger.info(f"Classifying data from source: {source}")

        if source == 'CA_FMMP':
            class_col = self._find_col(gdf, ['CI_CLASSNM', 'CLASS1_LBL'])
            classifier = self._classify_ca_fmmp
        elif source == 'OR_DLCD':
            class_col = self._find_col(gdf, ['ZONE_CLASS', 'ZONE_CODE', 'ALT_ZONE'])
            classifier = self._classify_or_dlcd
        elif source == 'WA_King_County':
            class_col = self._find_col(gdf, ['CURRZONE', 'ZONING_SUM'])
            classifier = self._classify_wa_king
        else:
            logger.warning(f"No classifier found for unknown source: {source}")
            gdf['standard_zone'] = 'OTHER'
            return gdf

        if not class_col:
            logger.error(f"No classification column found for source: {source}. Marking as OTHER.")
            gdf['standard_zone'] = 'OTHER'
        else:
            logger.info(f"Using column '{class_col}' for {source} classification.")
            gdf['standard_zone'] = gdf.apply(classifier, axis=1, class_col=class_col)
        
        return gdf

    def _assess_redevelopment_potential(self, std_zone: str) -> float:
        """Calculates a redevelopment potential score based on the standard zone."""
        potential_map = {
            'PRIME_AG': 0.1,
            'IMPORTANT_AG': 0.3,
            'GRAZING': 0.5,
            'MIXED_FARM_FOREST': 0.4,
            'RURAL_RESIDENTIAL': 0.8,
            'URBAN': 0.9,
            'OTHER': 0.2
        }
        return potential_map.get(std_zone, 0.2)

    def run_analysis(self, target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Performs a comprehensive, multi-source zoning analysis.
        """
        logger.info(f"Starting zoning analysis for {len(target_hexagons)} hexagons.")
        
        zoning_gdf = self.data_source.fetch_all_zoning_data(target_hexagons)
        if zoning_gdf.empty:
            logger.warning("No zoning polygons found. Aborting analysis.")
            return {hex_id: {'error': 'No zoning data available.'} for hex_id in target_hexagons}

        classified_gdfs = [self._classify_zoning(group) for _, group in zoning_gdf.groupby('source')]
        classified_gdf = pd.concat(classified_gdfs, ignore_index=True)
        
        hex_gdf = gpd.GeoDataFrame(
            {'hex_id': target_hexagons}, 
            geometry=[Polygon(h3_to_geo_boundary(h)) for h in target_hexagons], 
            crs="EPSG:4326"
        )
        
        classified_gdf = classified_gdf.to_crs(hex_gdf.crs)
        logger.info("Performing spatial join...")
        joined_gdf = gpd.sjoin(hex_gdf, classified_gdf, how="inner", predicate="intersects")
        
        h3_results = {}
        if joined_gdf.empty:
            logger.info("No zoning polygons intersect the target hexagons.")
        else:
            for hex_id, group in joined_gdf.groupby('hex_id'):
                unique_zones = list(group['standard_zone'].unique())
                redevelopment_scores = [self._assess_redevelopment_potential(zone) for zone in unique_zones]
                
                h3_results[hex_id] = {
                    'zoning_classes': unique_zones,
                    'is_ag_zone': any(zone in ['PRIME_AG', 'IMPORTANT_AG'] for zone in unique_zones),
                    'avg_redevelopment_potential': sum(redevelopment_scores) / len(redevelopment_scores) if redevelopment_scores else 0.0,
                    'data_sources': list(group['source'].unique())
                }

        # Ensure all requested hexagons get a result, even if empty
        for hex_id in target_hexagons:
            if hex_id not in h3_results:
                h3_results[hex_id] = {
                    'zoning_classes': [],
                    'is_ag_zone': False,
                    'avg_redevelopment_potential': 0.0,
                    'data_sources': []
                }
        
        logger.info(f"Completed zoning analysis for {len(h3_results)} hexagons.")
        return h3_results 