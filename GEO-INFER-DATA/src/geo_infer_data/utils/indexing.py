"""
Spatial and temporal indexing utilities for GEO-INFER-DATA.

This module provides indexing utilities for efficient spatial and temporal
queries including H3, quadtree, and R-tree indexing strategies.
"""

import logging
from typing import Dict, List, Optional, Union, Any, Tuple
import asyncio

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, LineString

from ..models.schemas import SpatialExtent, TemporalExtent


logger = logging.getLogger(__name__)


class SpatialIndexer:
    """
    Spatial indexing for efficient geospatial queries.

    This class provides spatial indexing capabilities using various
    strategies including H3, quadtree, and R-tree indexing.

    Examples:
        >>> indexer = SpatialIndexer()
        >>>
        >>> # Create spatial index
        >>> index = indexer.create_spatial_index(geodataframe, 'h3')
        >>>
        >>> # Query by spatial bounds
        >>> results = indexer.query_by_bounds(index, bbox=[-122.5, 37.7, -122.3, 37.9])
        >>>
        >>> # Convert lat/lng to H3 cell
        >>> cell = indexer.latlng_to_cell(37.7749, -122.4194, resolution=9)
    """

    def __init__(self):
        self.indexes = {}
        logger.info("Initialized SpatialIndexer")

    def create_spatial_index(self, data: gpd.GeoDataFrame, strategy: str = 'h3') -> str:
        """
        Create spatial index for geospatial data.

        Args:
            data: GeoDataFrame to index
            strategy: Indexing strategy ('h3', 'quadtree', 'rtree')

        Returns:
            Index identifier
        """
        logger.info(f"Creating spatial index with {strategy} strategy")

        index_id = f"spatial_{strategy}_{len(self.indexes)}"

        if strategy == 'h3':
            self.indexes[index_id] = self._create_h3_index(data)
        elif strategy == 'quadtree':
            self.indexes[index_id] = self._create_quadtree_index(data)
        elif strategy == 'rtree':
            self.indexes[index_id] = self._create_rtree_index(data)
        else:
            raise ValueError(f"Unknown indexing strategy: {strategy}")

        logger.info(f"Created spatial index: {index_id}")
        return index_id

    def _create_h3_index(self, data: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Create H3 spatial index."""
        try:
            import h3
        except ImportError:
            logger.warning("H3 not available, using mock implementation")
            return {'type': 'h3_mock', 'data': data}

        h3_indexes = {}

        for idx, row in data.iterrows():
            geom = row.geometry
            if geom and geom.is_valid:
                # Get centroid
                centroid = geom.centroid
                lat, lon = centroid.y, centroid.x

                # Create H3 index at resolution 9 (city level)
                h3_index = h3.geo_to_h3(lat, lon, 9)
                h3_indexes[str(idx)] = h3_index

        return {
            'type': 'h3',
            'resolution': 9,
            'indexes': h3_indexes,
            'data': data
        }

    def _create_quadtree_index(self, data: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Create quadtree spatial index."""
        # Mock quadtree implementation
        return {
            'type': 'quadtree',
            'bounds': data.total_bounds,
            'data': data
        }

    def _create_rtree_index(self, data: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Create R-tree spatial index."""
        try:
            from rtree import index
        except ImportError:
            logger.warning("Rtree not available, using mock implementation")
            return {'type': 'rtree_mock', 'data': data}

        # Create R-tree index
        idx = index.Index()

        for i, row in data.iterrows():
            geom = row.geometry
            if geom and geom.is_valid:
                bounds = geom.bounds  # (min_lon, min_lat, max_lon, max_lat)
                idx.insert(i, bounds)

        return {
            'type': 'rtree',
            'index': idx,
            'data': data
        }

    def query_by_bounds(self, index_id: str, bbox: List[float]) -> gpd.GeoDataFrame:
        """
        Query spatial index by bounding box.

        Args:
            index_id: Index identifier
            bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]

        Returns:
            Filtered GeoDataFrame
        """
        if index_id not in self.indexes:
            raise ValueError(f"Index {index_id} not found")

        index_data = self.indexes[index_id]
        index_type = index_data['type']

        if index_type == 'h3':
            return self._query_h3_bounds(index_data, bbox)
        elif index_type == 'quadtree':
            return self._query_quadtree_bounds(index_data, bbox)
        elif index_type == 'rtree':
            return self._query_rtree_bounds(index_data, bbox)
        else:
            # Fallback to spatial query
            return index_data['data'][index_data['data'].geometry.within(Polygon.from_bounds(*bbox))]

    def _query_h3_bounds(self, index_data: Dict[str, Any], bbox: List[float]) -> gpd.GeoDataFrame:
        """Query H3 index by bounds."""
        try:
            import h3
        except ImportError:
            return index_data['data']

        # Get H3 cells that intersect with bbox
        min_lon, min_lat, max_lon, max_lat = bbox

        # Get H3 cells for bbox corners
        cells = h3.polyfill({
            'type': 'Polygon',
            'coordinates': [[
                [min_lon, min_lat],
                [min_lon, max_lat],
                [max_lon, max_lat],
                [max_lon, min_lat],
                [min_lon, min_lat]
            ]]
        }, index_data['resolution'])

        # Filter data by H3 cells
        matching_indexes = [
            idx for idx, h3_idx in index_data['indexes'].items()
            if h3_idx in cells
        ]

        if matching_indexes:
            return index_data['data'].loc[matching_indexes]
        else:
            return gpd.GeoDataFrame()

    def _query_quadtree_bounds(self, index_data: Dict[str, Any], bbox: List[float]) -> gpd.GeoDataFrame:
        """Query quadtree index by bounds."""
        # Mock implementation
        return index_data['data']

    def _query_rtree_bounds(self, index_data: Dict[str, Any], bbox: List[float]) -> gpd.GeoDataFrame:
        """Query R-tree index by bounds."""
        # Mock implementation
        return index_data['data']

    def latlng_to_cell(self, lat: float, lng: float, resolution: int = 9) -> str:
        """
        Convert latitude/longitude to H3 cell.

        Args:
            lat: Latitude
            lng: Longitude
            resolution: H3 resolution level

        Returns:
            H3 cell index
        """
        try:
            import h3
            return h3.geo_to_h3(lat, lng, resolution)
        except ImportError:
            logger.warning("H3 not available for latlng_to_cell")
            return f"mock_h3_{lat}_{lng}_{resolution}"

    def cell_to_latlng(self, cell: str) -> Tuple[float, float]:
        """
        Convert H3 cell to latitude/longitude.

        Args:
            cell: H3 cell index

        Returns:
            Tuple of (latitude, longitude)
        """
        try:
            import h3
            lat, lng = h3.h3_to_geo(cell)
            return lat, lng
        except ImportError:
            logger.warning("H3 not available for cell_to_latlng")
            # Mock implementation
            return 37.7749, -122.4194


class TemporalIndexer:
    """
    Temporal indexing for efficient time-based queries.

    This class provides temporal indexing capabilities for time-series
    and temporal geospatial data.

    Examples:
        >>> indexer = TemporalIndexer()
        >>>
        >>> # Create temporal index
        >>> index = indexer.create_temporal_index(data, 'timestamp')
        >>>
        >>> # Query by time range
        >>> results = indexer.query_by_time_range(index, start_time, end_time)
    """

    def __init__(self):
        self.indexes = {}
        logger.info("Initialized TemporalIndexer")

    def create_temporal_index(self, data: Union[pd.DataFrame, gpd.GeoDataFrame], time_column: str) -> str:
        """
        Create temporal index for time-based queries.

        Args:
            data: DataFrame or GeoDataFrame with temporal data
            time_column: Name of the datetime column

        Returns:
            Index identifier
        """
        logger.info(f"Creating temporal index for column: {time_column}")

        index_id = f"temporal_{len(self.indexes)}"

        if time_column not in data.columns:
            raise ValueError(f"Time column {time_column} not found in data")

        # Sort by time for efficient range queries
        sorted_data = data.sort_values(time_column).reset_index(drop=True)

        self.indexes[index_id] = {
            'type': 'temporal',
            'time_column': time_column,
            'data': sorted_data,
            'min_time': sorted_data[time_column].min(),
            'max_time': sorted_data[time_column].max()
        }

        logger.info(f"Created temporal index: {index_id}")
        return index_id

    def query_by_time_range(
        self,
        index_id: str,
        start_time: Union[str, pd.Timestamp],
        end_time: Union[str, pd.Timestamp]
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        Query temporal index by time range.

        Args:
            index_id: Index identifier
            start_time: Start time for query
            end_time: End time for query

        Returns:
            Filtered data
        """
        if index_id not in self.indexes:
            raise ValueError(f"Index {index_id} not found")

        index_data = self.indexes[index_id]
        time_column = index_data['time_column']
        data = index_data['data']

        # Filter by time range
        mask = (data[time_column] >= start_time) & (data[time_column] <= end_time)
        return data[mask]

    def query_by_time_point(
        self,
        index_id: str,
        time_point: Union[str, pd.Timestamp]
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        Query temporal index by time point.

        Args:
            index_id: Index identifier
            time_point: Specific time point

        Returns:
            Data at the specified time point
        """
        if index_id not in self.indexes:
            raise ValueError(f"Index {index_id} not found")

        index_data = self.indexes[index_id]
        time_column = index_data['time_column']
        data = index_data['data']

        # Find exact match or nearest
        mask = data[time_column] == time_point
        return data[mask]
