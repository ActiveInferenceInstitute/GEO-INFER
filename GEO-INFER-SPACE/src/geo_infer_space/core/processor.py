import logging
from typing import Optional, Union, Tuple, List, Dict, Any
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
import h3
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
from scipy.spatial.distance import cdist

logger = logging.getLogger(__name__)

class SpatialProcessor:
    """Core spatial processing engine for GEO-INFER-SPACE.

    Provides fundamental spatial operations and workflow orchestration.
    
    Args:
        config_path: Path to configuration YAML file.
    
    Raises:
        ValueError: If configuration is invalid.
        FileNotFoundError: If config file not found.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the spatial processor with configuration."""
        self.config = self._load_config(config_path)
        logger.info("SpatialProcessor initialized with config: %s", self.config)

    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to config file. Uses default if None.
            
        Returns:
            Configuration dictionary.
        """
        import yaml
        if config_path is None:
            config_path = "config/local.yaml"
        
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            logger.error("Configuration file not found: %s", config_path)
            raise
        except yaml.YAMLError as e:
            logger.error("Invalid YAML in config file: %s", e)
            raise ValueError("Invalid configuration file")

    def buffer_analysis(
        self,
        input_data: gpd.GeoDataFrame,
        buffer_distance: Union[int, float],
        dissolve: bool = False
    ) -> gpd.GeoDataFrame:
        """Perform buffer analysis on input geometries.
        
        Creates buffer zones around input features.
        
        Args:
            input_data: Input GeoDataFrame with geometries to buffer.
            buffer_distance: Distance to buffer (in units of CRS).
            dissolve: Whether to dissolve overlapping buffers.
            
        Returns:
            GeoDataFrame with buffered geometries.
            
        Raises:
            ValueError: If input is invalid or empty.
        """
        if input_data.empty:
            raise ValueError("Input GeoDataFrame is empty")
        
        if input_data.crs is None:
            logger.warning("No CRS defined - assuming EPSG:4326")
            input_data = input_data.set_crs("EPSG:4326")
        
        original_crs = input_data.crs
        is_geographic = original_crs.is_geographic
        
        if is_geographic:
            metric_crs = "EPSG:3857"
            input_data = input_data.to_crs(metric_crs)
        
        buffered = input_data.buffer(buffer_distance)
        
        if dissolve:
            union_geom = buffered.unary_union
            buffered = gpd.GeoSeries([union_geom], crs=input_data.crs)
        
        result_gdf = gpd.GeoDataFrame(
            geometry=buffered,
            crs=input_data.crs
        )
        
        if is_geographic:
            result_gdf = result_gdf.to_crs(original_crs)
        
        logger.info(
            "Buffer analysis completed: %d features processed",
            len(result_gdf)
        )
        return result_gdf 

    def proximity_analysis(
        self,
        points: gpd.GeoDataFrame,
        polygons: gpd.GeoDataFrame,
        buffer_distance: Union[int, float]
    ) -> gpd.GeoDataFrame:
        """Perform proximity analysis by buffering points and intersecting with polygons.
        
        Args:
            points: GeoDataFrame of points to buffer.
            polygons: GeoDataFrame of polygons to intersect with.
            buffer_distance: Buffer distance in meters.
            
        Returns:
            GeoDataFrame of intersection results.
            
        Raises:
            ValueError: If inputs are invalid or empty.
        """
        if points.empty or polygons.empty:
            raise ValueError("Input GeoDataFrames cannot be empty")
        
        from geo_infer_space.analytics.vector import buffer_and_intersect
        return buffer_and_intersect(points, polygons, buffer_distance) 

    def h3_to_coordinates(self, h3_cell: str) -> Tuple[float, float]:
        """
        Get the center coordinates (lat, lon) of an H3 cell.
        Args:
            h3_cell: H3 cell identifier.
        Returns:
            Tuple of (latitude, longitude).
        Raises:
            ValueError: If invalid H3 cell.
        """
        try:
            return h3.cell_to_latlng(h3_cell)
        except Exception as e:
            raise ValueError(f"Invalid H3 cell: {e}")

    def create_h3_grid(self, bounds: Tuple[float, float, float, float], resolution: int = 8) -> List[str]:
        """
        Generate H3 cells covering a bounding box.
        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat)
            resolution: H3 resolution level.
        Returns:
            List of H3 cell identifiers covering the bounds.
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        geojson = {
            "type": "Polygon",
            "coordinates": [[
                [min_lon, min_lat],
                [min_lon, max_lat],
                [max_lon, max_lat],
                [max_lon, min_lat],
                [min_lon, min_lat]
            ]]
        }
        cells = h3.polygon_to_cells(geojson, resolution)
        return list(cells) if isinstance(cells, set) else cells

    def perform_multi_overlay(self, spatial_datasets: Dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
        """
        Perform multi-layer spatial overlay on multiple GeoDataFrames.

        Args:
            spatial_datasets: Dictionary of domain names to GeoDataFrames.

        Returns:
            Single GeoDataFrame with overlaid geometries and attributes.

        Raises:
            ValueError: If datasets have incompatible CRS or are empty.
        """
        if not spatial_datasets:
            raise ValueError("No spatial datasets provided")

        assigned = []
        base_crs = next(iter(spatial_datasets.values())).crs
        for name, gdf in spatial_datasets.items():
            if gdf.empty:
                raise ValueError(f"Dataset {name} is empty")
            if gdf.crs != base_crs:
                gdf = gdf.to_crs(base_crs)
            assigned_gdf = gdf.assign(**{f'domain_{name}': name})
            assigned.append(assigned_gdf)

        all_gdf = gpd.GeoDataFrame(pd.concat(assigned, ignore_index=True), crs=base_crs)
        return all_gdf

    def calculate_spatial_correlation(self, map1: Dict[str, float], map2: Dict[str, float]) -> float:
        """
        Calculate spatial correlation between two H3-based maps.

        Args:
            map1: Dict of H3 cell to value for first map.
            map2: Dict of H3 cell to value for second map.

        Returns:
            Pearson correlation coefficient.

        Raises:
            ValueError: If maps have no common cells or insufficient data.
        """
        common_cells = set(map1.keys()) & set(map2.keys())
        if len(common_cells) < 2:
            raise ValueError("Insufficient common cells for correlation")

        values1 = np.array([map1[cell] for cell in common_cells])
        values2 = np.array([map2[cell] for cell in common_cells])

        return np.corrcoef(values1, values2)[0, 1] 