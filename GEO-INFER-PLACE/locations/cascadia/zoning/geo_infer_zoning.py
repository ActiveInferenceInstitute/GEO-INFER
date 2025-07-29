"""
GeoInfer Zoning Module

This module performs real H3-based analysis of agricultural zoning data using OSC H3 v4 methods,
intelligently classifying and standardizing data from multiple state sources.
"""
import logging
from typing import Dict, Any, List
from pathlib import Path
import geopandas as gpd
import pandas as pd
import h3
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

from .data_sources import CascadianZoningDataSources
from geo_infer_space.core.base_module import BaseAnalysisModule

# A forward declaration for type hinting the backend without circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend

logger = logging.getLogger(__name__)

class GeoInferZoning(BaseAnalysisModule):
    """
    Processes and analyzes multi-source agricultural zoning data using real OSC H3 v4 methods,
    standardizing classifications and assessing redevelopment potential.
    """

    def __init__(self, backend: 'CascadianAgriculturalH3Backend'):
        super().__init__('zoning', h3_resolution=8)
        self.backend = backend
        self.data_dir = Path("output/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.target_hexagons = backend.target_hexagons
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
        logger.info(f"Initialized GeoInferZoning module with real OSC H3 v4 integration.")

    def acquire_raw_data(self) -> Path:
        """
        Acquire raw zoning data for Del Norte county.
        Returns path to the raw data file.
        """
        logger.info(f"[{self.module_name}] 🔍 Acquiring raw zoning data...")
        
        # Check for empirical data first
        empirical_data_path = Path("output/data/empirical_zoning_data.geojson")
        if empirical_data_path.exists():
            logger.info(f"[{self.module_name}] ✅ Found empirical zoning data: {empirical_data_path}")
            return empirical_data_path
        
        # Fallback to synthetic data
        synthetic_data_path = Path("output/data/raw_zoning_data.geojson")
        if synthetic_data_path.exists():
            logger.warning(f"[{self.module_name}] ⚠️ Using synthetic zoning data: {synthetic_data_path}")
            return synthetic_data_path
        
        # Create synthetic data if none exists
        logger.warning(f"[{self.module_name}] ⚠️ No zoning data found, creating synthetic data...")
        return self._create_synthetic_zoning_data()

    def run_final_analysis(self, h3_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs real comprehensive, multi-source zoning analysis on H3-indexed data using OSC H3 v4 methods.
        
        Args:
            h3_data: The H3-indexed data where keys are hexagon IDs and values
                     are dictionaries of properties from the raw data.
                     
        Returns:
            The H3 data dictionary with added real analysis results.
        """
        logger.info(f"[{self.module_name}] Starting real final analysis on {len(h3_data)} hexagons using OSC H3 v4 methods.")
        
        # Load real zoning data for spatial analysis
        try:
            zoning_gdf = gpd.read_file(self.data_dir / "empirical_zoning_data.geojson")
            logger.info(f"Loaded {len(zoning_gdf)} real zoning features for analysis")
        except Exception as e:
            logger.error(f"Failed to load real zoning data: {e}")
            return {}

        for hex_id, properties in h3_data.items():
            try:
                # Get hexagon boundary using real H3 v4 methods
                hex_boundary = h3.cell_to_boundary(hex_id)
                hex_polygon = Polygon(hex_boundary)
                
                # Find intersecting zoning features using real spatial analysis
                intersecting_features = zoning_gdf[zoning_gdf.intersects(hex_polygon)]
                
                if len(intersecting_features) == 0:
                    # No zoning data for this hexagon
                    properties['zoning_class'] = 'OTHER'
                    properties['is_ag_zone'] = False
                    properties['redevelopment_potential'] = 0.2
                    properties['zoning_coverage'] = 0.0
                    properties['primary_zone_type'] = 'Unknown'
                    continue
                
                # Calculate real zoning statistics for this hexagon
                zoning_stats = self._calculate_real_zoning_statistics(intersecting_features, hex_polygon)
                
                # Determine primary zoning using real analysis
                primary_zone = self._determine_primary_zoning(zoning_stats)
                
                # Calculate real redevelopment potential
                redevelopment_score = self._calculate_real_redevelopment_potential(zoning_stats, primary_zone)
                
                # Update the dictionary with real analysis results
                properties['zoning_class'] = primary_zone['class']
                properties['is_ag_zone'] = primary_zone['is_agricultural']
                properties['redevelopment_potential'] = redevelopment_score
                properties['zoning_coverage'] = zoning_stats.get('coverage_percentage', 0.0)
                properties['primary_zone_type'] = primary_zone['name']
                properties['zone_breakdown'] = zoning_stats.get('zone_breakdown', {})
                
            except Exception as e:
                logger.error(f"Real error in zoning analysis for hexagon {hex_id}: {e}")
                continue
        
        logger.info(f"[{self.module_name}] Completed real final analysis using OSC H3 v4 methods.")
        return h3_data

    def _calculate_real_zoning_statistics(self, features: gpd.GeoDataFrame, hex_polygon: Polygon) -> Dict[str, Any]:
        """
        Calculate real zoning statistics for a hexagon using actual spatial analysis.
        """
        zoning_stats = {
            'total_area': 0.0,
            'zone_breakdown': {},
            'coverage_percentage': 0.0
        }
        
        hex_area = hex_polygon.area
        total_intersection_area = 0.0
        
        for idx, feature in features.iterrows():
            try:
                # Calculate real intersection area
                intersection = feature.geometry.intersection(hex_polygon)
                if intersection.is_empty:
                    continue
                
                intersection_area = intersection.area
                total_intersection_area += intersection_area
                
                # Get zoning classification
                zone_class = self._classify_real_zoning(feature)
                
                # Accumulate real statistics
                if zone_class not in zoning_stats['zone_breakdown']:
                    zoning_stats['zone_breakdown'][zone_class] = {
                        'area': 0.0,
                        'percentage': 0.0,
                        'count': 0
                    }
                
                zoning_stats['zone_breakdown'][zone_class]['area'] += intersection_area
                zoning_stats['zone_breakdown'][zone_class]['count'] += 1
                
            except Exception as e:
                logger.warning(f"Error processing zoning feature {idx}: {e}")
                continue
        
        # Calculate coverage percentage
        if hex_area > 0:
            zoning_stats['coverage_percentage'] = (total_intersection_area / hex_area) * 100
            zoning_stats['total_area'] = total_intersection_area
            
            # Calculate percentages for each zone type
            for zone_class, stats in zoning_stats['zone_breakdown'].items():
                if total_intersection_area > 0:
                    stats['percentage'] = (stats['area'] / total_intersection_area) * 100
        
        return zoning_stats

    def _classify_real_zoning(self, feature: gpd.GeoSeries) -> str:
        """
        Apply real zoning classification based on feature properties.
        """
        source = feature.get('source', 'UNKNOWN').upper()
        class_val = feature.get('CI_CLASSNM', '').lower()

        if 'CA_FMMP' in source:
            if 'prime farmland' in class_val: 
                return 'PRIME_AG'
            if 'farmland of statewide importance' in class_val: 
                return 'IMPORTANT_AG'
            if 'farmland of local importance' in class_val: 
                return 'IMPORTANT_AG'
            if 'unique farmland' in class_val: 
                return 'IMPORTANT_AG'
            if 'grazing land' in class_val: 
                return 'GRAZING'
            if 'urban and built-up land' in class_val: 
                return 'URBAN'
        elif 'OR_DLCD' in source:
            zone_class = feature.get('ZONE_CLASS', '').upper()
            if 'EFU' in zone_class or 'EXCLUSIVE FARM USE' in zone_class: 
                return 'PRIME_AG'
            if 'FARM' in zone_class or 'AGRICULTURE' in zone_class: 
                return 'IMPORTANT_AG'
            if 'FOREST' in zone_class and 'FARM' in zone_class: 
                return 'MIXED_FARM_FOREST'
            if 'RURAL RESIDENTIAL' in zone_class: 
                return 'RURAL_RESIDENTIAL'
        elif 'WA_KING_COUNTY' in source:
            zone_class = feature.get('CURRZONE', '').upper()
            if zone_class.startswith('A-'): 
                return 'IMPORTANT_AG'
            if zone_class.startswith('RA-'): 
                return 'RURAL_RESIDENTIAL'
            if zone_class.startswith('F'): 
                return 'MIXED_FARM_FOREST'
            if zone_class in ['UR', 'R-']: 
                return 'URBAN'
        
        return 'OTHER'

    def _determine_primary_zoning(self, zoning_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine the primary zoning classification using real analysis.
        """
        zone_breakdown = zoning_stats.get('zone_breakdown', {})
        
        if not zone_breakdown:
            return {
                'class': 'OTHER',
                'name': 'Unknown',
                'is_agricultural': False
            }
        
        # Find zone with highest area coverage
        primary_zone = max(zone_breakdown.items(), key=lambda x: x[1]['area'])
        zone_class = primary_zone[0]
        zone_data = primary_zone[1]
        
        # Determine if agricultural
        agricultural_zones = ['PRIME_AG', 'IMPORTANT_AG', 'GRAZING', 'MIXED_FARM_FOREST']
        is_agricultural = zone_class in agricultural_zones
        
        # Get zone name from schema
        zone_name = self.ZONING_SCHEMA.get(zone_class, 'Unknown')
        
        return {
            'class': zone_class,
            'name': zone_name,
            'is_agricultural': is_agricultural,
            'coverage_percentage': zone_data.get('percentage', 0.0)
        }

    def _calculate_real_redevelopment_potential(self, zoning_stats: Dict[str, Any], primary_zone: Dict[str, Any]) -> float:
        """
        Calculate real redevelopment potential score based on actual zoning data.
        """
        zone_class = primary_zone['class']
        coverage_percentage = primary_zone.get('coverage_percentage', 0.0)
        
        # Base redevelopment potential scores
        base_potential = {
            'PRIME_AG': 0.1,      # Very low - protected agricultural land
            'IMPORTANT_AG': 0.3,   # Low - important agricultural land
            'GRAZING': 0.5,        # Medium - grazing land
            'MIXED_FARM_FOREST': 0.4,  # Medium-low - mixed use
            'RURAL_RESIDENTIAL': 0.8,   # High - already residential
            'URBAN': 0.9,          # Very high - already urban
            'OTHER': 0.2           # Low - unknown/other
        }
        
        base_score = base_potential.get(zone_class, 0.2)
        
        # Adjust based on coverage percentage
        # Higher coverage of non-agricultural zones increases potential
        if primary_zone['is_agricultural']:
            # Agricultural zones: lower coverage = higher potential
            coverage_factor = 1.0 - (coverage_percentage / 100.0)
        else:
            # Non-agricultural zones: higher coverage = higher potential
            coverage_factor = coverage_percentage / 100.0
        
        # Calculate final score with coverage adjustment
        final_score = base_score + (coverage_factor * 0.2)  # Max 0.2 adjustment
        
        return round(min(1.0, max(0.0, final_score)), 3)

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

    def _create_synthetic_zoning_data(self) -> Path:
        """
        Create synthetic zoning data when no real data is available.
        This method generates realistic zoning data for Del Norte County testing and development.
        """
        logger.info("Creating synthetic Del Norte County zoning data for testing...")
        
        # Del Norte County boundaries (approximate)
        # Del Norte County: roughly 41.4°N to 42.0°N, 124.5°W to 123.5°W
        synthetic_features = [
            # Smith River Valley - Prime agricultural land
            {
                'geometry': Polygon([(-124.2, 41.6), (-124.2, 41.8), (-124.0, 41.8), (-124.0, 41.6), (-124.2, 41.6)]),
                'CI_CLASSNM': 'Prime Farmland',
                'source': 'CA_FMMP',
                'county': 'Del Norte'
            },
            # Crescent City area - Urban and built-up
            {
                'geometry': Polygon([(-124.2, 41.7), (-124.2, 41.8), (-124.1, 41.8), (-124.1, 41.7), (-124.2, 41.7)]),
                'CI_CLASSNM': 'Urban and Built-up Land',
                'source': 'CA_FMMP',
                'county': 'Del Norte'
            },
            # Klamath River Valley - Farmland of statewide importance
            {
                'geometry': Polygon([(-124.0, 41.5), (-124.0, 41.7), (-123.8, 41.7), (-123.8, 41.5), (-124.0, 41.5)]),
                'CI_CLASSNM': 'Farmland of Statewide Importance',
                'source': 'CA_FMMP',
                'county': 'Del Norte'
            },
            # Coastal grazing areas
            {
                'geometry': Polygon([(-124.3, 41.8), (-124.3, 42.0), (-124.1, 42.0), (-124.1, 41.8), (-124.3, 41.8)]),
                'CI_CLASSNM': 'Grazing Land',
                'source': 'CA_FMMP',
                'county': 'Del Norte'
            },
            # Forest conservation areas
            {
                'geometry': Polygon([(-123.8, 41.4), (-123.8, 41.6), (-123.6, 41.6), (-123.6, 41.4), (-123.8, 41.4)]),
                'CI_CLASSNM': 'Forestry',
                'source': 'CA_FMMP',
                'county': 'Del Norte'
            },
            # Rural residential areas
            {
                'geometry': Polygon([(-123.9, 41.6), (-123.9, 41.8), (-123.7, 41.8), (-123.7, 41.6), (-123.9, 41.6)]),
                'CI_CLASSNM': 'Rural Residential',
                'source': 'CA_FMMP',
                'county': 'Del Norte'
            }
        ]
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(synthetic_features, crs="EPSG:4326")
        
        # Save to file
        output_path = self.data_dir / "raw_zoning_data.geojson"
        gdf.to_file(output_path, driver='GeoJSON')
        
        logger.info(f"Created synthetic Del Norte County zoning data with {len(synthetic_features)} features")
        return output_path 