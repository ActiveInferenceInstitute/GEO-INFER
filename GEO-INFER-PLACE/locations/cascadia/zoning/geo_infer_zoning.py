"""
GeoInfer Zoning Module

This module performs H3-based analysis of agricultural zoning data by
intelligently classifying and standardizing data from multiple state sources.
"""
import logging
from typing import Dict, Any
from pathlib import Path
import geopandas as gpd
import pandas as pd

from .data_sources import CascadianZoningDataSources
from geo_infer_space.core.base_module import BaseAnalysisModule

# A forward declaration for type hinting the backend without circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend

logger = logging.getLogger(__name__)

class GeoInferZoning(BaseAnalysisModule):
    """
    Processes and analyzes multi-source agricultural zoning data, standardizing
    classifications and assessing redevelopment potential.
    """

    def __init__(self, backend: 'CascadianAgriculturalH3Backend'):
        super().__init__(backend, 'zoning')
        self.data_source = CascadianZoningDataSources(self.data_dir)
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
        logger.info(f"Initialized GeoInferZoning module.")

    def acquire_raw_data(self) -> Path:
        """
        Acquires raw zoning data from all sources and returns the path to the
        consolidated, cached file.
        """
        return self.data_source.fetch_all_zoning_data()

    def run_final_analysis(self, h3_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a comprehensive, multi-source zoning analysis on H3-indexed data.
        
        Args:
            h3_data: The H3-indexed data where keys are hexagon IDs and values
                     are dictionaries of properties from the raw data.
                     
        Returns:
            The H3 data dictionary with added analysis results.
        """
        logger.info(f"[{self.module_name}] Starting final analysis on {len(h3_data)} hexagons.")
        
        for hex_id, properties in h3_data.items():
            # The properties dict now contains columns from the raw GeoDataFrame
            # as processed by the H3 loader. We need to standardize them.
            standardized_zone = self._classify_zoning(properties)
            redevelopment_score = self._assess_redevelopment_potential(standardized_zone)
            
            # Update the dictionary with analysis results
            properties['zoning_class'] = standardized_zone
            properties['is_ag_zone'] = standardized_zone in ['PRIME_AG', 'IMPORTANT_AG']
            properties['redevelopment_potential'] = redevelopment_score
        
        logger.info(f"[{self.module_name}] Completed final analysis.")
        return h3_data

    def _find_col_value(self, props: Dict, potential_names: list) -> str:
        """Finds the first matching value from a dictionary of properties."""
        for name in potential_names:
            if name in props and props[name] is not None:
                return str(props[name])
        return ""

    def _classify_zoning(self, props: Dict[str, Any]) -> str:
        """Applies the correct classification function based on the data source."""
        source = props.get('source', 'UNKNOWN').upper()

        if 'CA_FMMP' in source:
            class_val = self._find_col_value(props, ['CI_CLASSNM', 'CLASS1_LBL']).lower()
            if 'prime farmland' in class_val: return 'PRIME_AG'
            if 'farmland of statewide importance' in class_val: return 'IMPORTANT_AG'
            if 'farmland of local importance' in class_val: return 'IMPORTANT_AG'
            if 'unique farmland' in class_val: return 'IMPORTANT_AG'
            if 'grazing land' in class_val: return 'GRAZING'
            if 'urban and built-up land' in class_val: return 'URBAN'
        elif 'OR_DLCD' in source:
            class_val = self._find_col_value(props, ['ZONE_CLASS', 'ZONE_CODE', 'ALT_ZONE']).upper()
            if 'EFU' in class_val or 'EXCLUSIVE FARM USE' in class_val: return 'PRIME_AG'
            if 'FARM' in class_val or 'AGRICULTURE' in class_val: return 'IMPORTANT_AG'
            if 'FOREST' in val and 'FARM' in class_val: return 'MIXED_FARM_FOREST'
            if 'RURAL RESIDENTIAL' in class_val or class_val.startswith('RR'): return 'RURAL_RESIDENTIAL'
        elif 'WA_KING_COUNTY' in source:
            class_val = self._find_col_value(props, ['CURRZONE', 'ZONING_SUM']).upper()
            if class_val.startswith('A-'): return 'IMPORTANT_AG'
            if class_val.startswith('RA-'): return 'RURAL_RESIDENTIAL'
            if class_val.startswith('F'): return 'MIXED_FARM_FOREST'
            if class_val in ['UR', 'R-']: return 'URBAN'
        
        return 'OTHER'

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