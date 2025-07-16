"""
GeoInfer Ownership Module

This module analyzes agricultural land ownership patterns using H3 indexing
by fetching real-time data from public GIS services.
"""
import logging
from typing import Dict, List, Any
from pathlib import Path
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

from .data_sources import CascadianOwnershipDataSources
from geo_infer_space.core.base_module import BaseAnalysisModule
from geo_infer_space.utils.h3_utils import cell_to_latlng_boundary

# A forward declaration for type hinting the backend without circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend

logger = logging.getLogger(__name__)

class GeoInferOwnership(BaseAnalysisModule):
    """
    Processes and analyzes ownership data within an H3 grid. It adapts its
    analysis based on the richness of the data available from the source.
    """

    def __init__(self, backend: 'CascadianAgriculturalH3Backend'):
        super().__init__(backend, 'ownership')
        self.data_source = CascadianOwnershipDataSources()
        logger.info(f"Initialized GeoInferOwnership module.")

    def acquire_raw_data(self) -> Path:
        """
        Fetch parcel data from ArcGIS services and cache locally.
        
        Returns:
            Path to cached raw data file
        """
        logger.info("Acquiring raw ownership/parcel data...")
        
        # Use the target hexagons from the backend to define our area of interest
        parcels_gdf = self.data_source.fetch_all_parcel_data(self.target_hexagons)
        
        if parcels_gdf.empty:
            logger.warning("No parcel data found for target area")
            return None
        
        # Cache the raw data
        raw_data_path = self.data_dir / 'raw_ownership_data.geojson'
        parcels_gdf.to_file(raw_data_path, driver='GeoJSON')
        logger.info(f"Cached {len(parcels_gdf)} parcels to {raw_data_path}")
        
        return raw_data_path

    def run_final_analysis(self, h3_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform ownership analysis on H3-indexed data.
        
        Args:
            h3_data: Dictionary of H3 cell ID -> parcel data
            
        Returns:
            Dictionary of H3 cell ID -> ownership analysis results
        """
        logger.info(f"Running ownership analysis on {len(h3_data)} H3 cells...")
        
        if not h3_data:
            logger.warning("No H3 data available for ownership analysis")
            return {}
        
        analysis_results = {}
        
        for h3_id, cell_data in h3_data.items():
            if not cell_data or 'parcels' not in cell_data:
                continue
                
            parcels = cell_data['parcels']
            if not parcels:
                continue
            
            # Convert parcels list back to GeoDataFrame for analysis
            parcels_gdf = gpd.GeoDataFrame(parcels)
            
            # Perform ownership analysis
            ownership_metrics = self._analyze_ownership_patterns(parcels_gdf)
            
            analysis_results[h3_id] = {
                'ownership_concentration_hhi': ownership_metrics.get('hhi', 0.0),
                'largest_owner_share_pct': ownership_metrics.get('largest_share', 0.0),
                'number_of_unique_owners': ownership_metrics.get('unique_owners', 0),
                'number_of_parcels': ownership_metrics.get('parcel_count', 0),
                'average_parcel_size_acres': ownership_metrics.get('avg_parcel_size', 0.0),
                'total_parcel_area_acres': ownership_metrics.get('total_area', 0.0),
                'score': ownership_metrics.get('redevelopment_score', 0.0)
            }
        
        logger.info(f"Completed ownership analysis for {len(analysis_results)} cells")
        return analysis_results

    def _find_col(self, gdf: gpd.GeoDataFrame, potential_names: List[str]) -> str:
        """Finds the first matching column name in the GeoDataFrame."""
        for name in potential_names:
            if name in gdf.columns:
                return name
        return None

    def _analyze_ownership_patterns(self, parcels_gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Analyze ownership patterns in a set of parcels.
        
        Args:
            parcels_gdf: GeoDataFrame of parcels
            
        Returns:
            Dictionary of ownership metrics
        """
        if parcels_gdf.empty:
            return {
                'hhi': 0.0,
                'largest_share': 0.0,
                'unique_owners': 0,
                'parcel_count': 0,
                'avg_parcel_size': 0.0,
                'total_area': 0.0,
                'redevelopment_score': 0.0
            }
        
        # Dynamically identify relevant columns
        owner_col = self._find_col(parcels_gdf, ['owner_name', 'OWNERNAME', 'OWNER', 'PAROWNER'])
        area_col = self._find_col(parcels_gdf, ['acreage', 'ACRES', 'GIS_ACRES', 'calca_gis'])

        if not area_col:
            # Calculate area from geometry if no area column exists
            try:
                # Project to equal-area projection for accurate calculation
                parcels_projected = parcels_gdf.to_crs('EPSG:3310')
                parcels_gdf['calculated_acres'] = parcels_projected.geometry.area * 0.000247105
                area_col = 'calculated_acres'
            except:
                # Fallback to rough area calculation
                parcels_gdf['calculated_acres'] = parcels_gdf.geometry.area * 111000 * 111000 * 0.000247105
            area_col = 'calculated_acres'
        
        total_area = parcels_gdf[area_col].sum()
        num_parcels = len(parcels_gdf)
        avg_parcel_size = parcels_gdf[area_col].mean()
        
        # Initialize metrics
        hhi = 0.0
        largest_share = 0.0
        unique_owners = 0
        
        # Perform ownership concentration analysis if owner column exists
        if owner_col and owner_col in parcels_gdf.columns:
            # Group by owner and sum their area
            owner_areas = parcels_gdf.groupby(owner_col)[area_col].sum()
            unique_owners = len(owner_areas)
            
            if total_area > 0:
                # Calculate ownership shares as percentages
                owner_shares = (owner_areas / total_area) * 100
                
                # Calculate Herfindahl-Hirschman Index (HHI) for concentration
                hhi = (owner_shares ** 2).sum()
                largest_share = owner_shares.max()
        
        # Calculate redevelopment potential score based on ownership patterns
        redevelopment_score = self._calculate_redevelopment_score(
            hhi, largest_share, unique_owners, num_parcels, avg_parcel_size
        )
        
        return {
            'hhi': hhi,
            'largest_share': largest_share,
            'unique_owners': unique_owners,
            'parcel_count': num_parcels,
            'avg_parcel_size': avg_parcel_size,
            'total_area': total_area,
            'redevelopment_score': redevelopment_score
        }

    def _calculate_redevelopment_score(self, hhi: float, largest_share: float, 
                                     unique_owners: int, parcel_count: int, 
                                     avg_parcel_size: float) -> float:
        """
        Calculate redevelopment potential score based on ownership patterns.
        
        Higher scores indicate better redevelopment potential:
        - Lower ownership concentration (easier to negotiate)
        - Moderate parcel sizes (not too fragmented, not too consolidated)
        - Multiple owners (more potential for development partnerships)
        
        Args:
            hhi: Herfindahl-Hirschman Index
            largest_share: Percentage owned by largest owner
            unique_owners: Number of unique owners
            parcel_count: Total number of parcels
            avg_parcel_size: Average parcel size in acres
            
        Returns:
            Redevelopment potential score (0.0 to 1.0)
        """
        score = 0.0
        
        # Ownership concentration factor (lower concentration = higher score)
        if hhi > 0:
            # Normalize HHI (range 0-10000, where 10000 = monopoly)
            concentration_score = max(0, 1 - (hhi / 10000))
        else:
            concentration_score = 0.5  # Default if no ownership data
        
        # Parcel size factor (moderate sizes preferred)
        if avg_parcel_size > 0:
            # Optimal range: 40-160 acres (good for agricultural development)
            if 40 <= avg_parcel_size <= 160:
                size_score = 1.0
            elif avg_parcel_size < 40:
                size_score = avg_parcel_size / 40  # Too small
            else:
                size_score = max(0.2, 160 / avg_parcel_size)  # Too large
        else:
            size_score = 0.0
        
        # Owner diversity factor
        if unique_owners > 0:
            # Sweet spot: 3-8 owners (diverse but manageable)
            if 3 <= unique_owners <= 8:
                diversity_score = 1.0
            elif unique_owners < 3:
                diversity_score = unique_owners / 3
            else:
                diversity_score = max(0.3, 8 / unique_owners)
        else:
            diversity_score = 0.0
        
        # Parcel count factor (avoid excessive fragmentation)
        if parcel_count > 0:
            # Prefer 5-20 parcels per H3 cell
            if 5 <= parcel_count <= 20:
                fragmentation_score = 1.0
            elif parcel_count < 5:
                fragmentation_score = parcel_count / 5
            else:
                fragmentation_score = max(0.2, 20 / parcel_count)
        else:
            fragmentation_score = 0.0
        
        # Weighted combination
        score = (
            concentration_score * 0.3 +
            size_score * 0.3 +
            diversity_score * 0.25 +
            fragmentation_score * 0.15
        )
        
        return min(1.0, max(0.0, score)) 