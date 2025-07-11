"""
GeoInfer Ownership Module

This module analyzes agricultural land ownership patterns using H3 indexing
by fetching real-time data from public GIS services.
"""
import logging
from typing import Dict, List, Any
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

from .data_sources import CascadianOwnershipDataSources
from utils_h3 import h3_to_geo_boundary

logger = logging.getLogger(__name__)

class GeoInferOwnership:
    """
    Processes and analyzes ownership data within an H3 grid. It adapts its
    analysis based on the richness of the data available from the source.
    """

    def __init__(self, resolution: int):
        self.resolution = resolution
        self.data_source = CascadianOwnershipDataSources()
        logger.info(f"Initialized GeoInferOwnership with resolution {resolution}")

    def _find_col(self, gdf: gpd.GeoDataFrame, potential_names: List[str]) -> str:
        """Finds the first matching column name in the GeoDataFrame."""
        for name in potential_names:
            if name in gdf.columns:
                return name
        return None

    def run_analysis(self, target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Spatially joins parcel data with H3 hexagons and calculates ownership
        metrics. The analysis is adapted based on available data columns.
        """
        logger.info(f"Starting ownership analysis for {len(target_hexagons)} hexagons.")
        
        # 1. Fetch parcel data from the ArcGIS service
        parcels_gdf = self.data_source.fetch_all_parcel_data(target_hexagons)
        if parcels_gdf.empty:
            logger.warning("No parcel data found. Aborting ownership analysis.")
            return {}
            
        # 2. Dynamically identify relevant columns
        owner_col = self._find_col(parcels_gdf, ['owner_name', 'OWNERNAME', 'OWNER', 'PAROWNER'])
        # Common acreage column names, can be expanded
        area_col = self._find_col(parcels_gdf, ['acreage', 'ACRES', 'GIS_ACRES', 'calca_gis'])

        if not area_col:
            # If no explicit area column, calculate it from the geometry
            logger.info("No acreage column found, calculating area from geometry.")
            # Project to an equal-area projection for accurate calculation (Albers for North America)
            parcels_gdf['calculated_acres'] = parcels_gdf.to_crs('EPSG:3310').geometry.area * 0.000247105
            area_col = 'calculated_acres'
        
        logger.info(f"Using owner column: '{owner_col}' and area column: '{area_col}'")

        # 3. Create a GeoDataFrame for the target hexagons
        hex_geometries = [Polygon(h3_to_geo_boundary(h)) for h in target_hexagons]
        hex_gdf = gpd.GeoDataFrame(
            {'hex_id': target_hexagons}, 
            geometry=hex_geometries, 
            crs="EPSG:4326"
        )
        
        # 4. Ensure CRS alignment
        parcels_gdf = parcels_gdf.to_crs(hex_gdf.crs)

        # 5. Perform the spatial join
        logger.info("Performing spatial join between hexagons and parcel polygons...")
        joined_gdf = gpd.sjoin(hex_gdf, parcels_gdf, how="inner", predicate="intersects")
        
        if joined_gdf.empty:
            logger.warning("Spatial join resulted in no matches between hexagons and parcel data.")
            return {}

        # 6. Aggregate results and calculate metrics based on available data
        logger.info("Aggregating ownership results per hexagon...")
        h3_ownership = {}
        for hex_id, group in joined_gdf.groupby('hex_id'):
            total_area_in_hex = group[area_col].sum()
            num_parcels = len(group)
            
            hex_metrics = {
                'number_of_parcels': num_parcels,
                'average_parcel_size_acres': group[area_col].mean(),
                'total_parcel_area_acres': total_area_in_hex
            }

            # Perform advanced analysis only if owner name is available
            if owner_col and owner_col in group.columns:
                # Group by owner and sum their area within the hex
                owner_areas = group.groupby(owner_col)[area_col].sum()
                
                # HHI Calculation for ownership concentration
                if total_area_in_hex > 0:
                    owner_shares = (owner_areas / total_area_in_hex) * 100
                    hhi = (owner_shares ** 2).sum()
                    largest_owner_share = owner_shares.max()
                else:
                    hhi = 0
                    largest_owner_share = 0

                hex_metrics.update({
                    'ownership_concentration_hhi': hhi,
                    'largest_owner_share_pct': largest_owner_share,
                    'number_of_unique_owners': len(owner_areas)
                })
            else:
                logger.debug(f"No owner column found for hex {hex_id}, performing basic analysis.")
                # Add placeholder values if no owner info is present
                hex_metrics.update({
                    'ownership_concentration_hhi': None,
                    'largest_owner_share_pct': None,
                    'number_of_unique_owners': None
                })
            
            h3_ownership[hex_id] = hex_metrics

        logger.info(f"Completed ownership analysis. Processed {len(h3_ownership)} hexagons.")
        return h3_ownership 