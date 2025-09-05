"""
Pydantic schemas for API request/response validation.

This module defines data models for spatial analysis API endpoints
using Pydantic for automatic validation and documentation generation.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from geojson_pydantic import Feature, FeatureCollection, Polygon, Point, LineString


class SpatialAnalysisRequest(BaseModel):
    """Base request model for spatial analysis operations."""
    
    data: Union[Feature, FeatureCollection] = Field(
        ..., description="GeoJSON data for analysis"
    )
    crs: Optional[str] = Field(
        "EPSG:4326", description="Coordinate reference system"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        {}, description="Analysis-specific parameters"
    )


class SpatialAnalysisResponse(BaseModel):
    """Base response model for spatial analysis results."""
    
    success: bool = Field(..., description="Whether the operation succeeded")
    result: Optional[Union[Feature, FeatureCollection, Dict[str, Any]]] = Field(
        None, description="Analysis results"
    )
    message: Optional[str] = Field(None, description="Status or error message")
    metadata: Optional[Dict[str, Any]] = Field(
        {}, description="Additional metadata about the operation"
    )


class BufferAnalysisRequest(SpatialAnalysisRequest):
    """Request model for buffer analysis operations."""
    
    buffer_distance: float = Field(
        ..., gt=0, description="Buffer distance in CRS units"
    )
    dissolve: bool = Field(
        False, description="Whether to dissolve overlapping buffers"
    )


class ProximityAnalysisRequest(BaseModel):
    """Request model for proximity analysis operations."""
    
    source_data: Union[Feature, FeatureCollection] = Field(
        ..., description="Source geometries"
    )
    target_data: Union[Feature, FeatureCollection] = Field(
        ..., description="Target geometries"
    )
    max_distance: Optional[float] = Field(
        None, description="Maximum distance to consider"
    )
    crs: Optional[str] = Field("EPSG:4326", description="Coordinate reference system")


class InterpolationRequest(BaseModel):
    """Request model for spatial interpolation operations."""
    
    points: FeatureCollection = Field(
        ..., description="Point observations for interpolation"
    )
    value_column: str = Field(
        ..., description="Column name containing values to interpolate"
    )
    bounds: List[float] = Field(
        ..., min_items=4, max_items=4, 
        description="Interpolation bounds [minx, miny, maxx, maxy]"
    )
    resolution: float = Field(
        ..., gt=0, description="Grid resolution for interpolation"
    )
    method: str = Field(
        "idw", description="Interpolation method (idw, kriging, rbf, nearest)"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        {}, description="Method-specific parameters"
    )
    crs: Optional[str] = Field("EPSG:4326", description="Coordinate reference system")
    
    @validator('method')
    def validate_method(cls, v):
        valid_methods = ['idw', 'kriging', 'rbf', 'nearest']
        if v not in valid_methods:
            raise ValueError(f'Method must be one of {valid_methods}')
        return v


class ClusteringRequest(BaseModel):
    """Request model for spatial clustering operations."""
    
    points: FeatureCollection = Field(
        ..., description="Point data for clustering"
    )
    method: str = Field(
        "dbscan", description="Clustering method (dbscan, kmeans, hierarchical)"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        {}, description="Clustering parameters (eps, min_samples, n_clusters, etc.)"
    )
    crs: Optional[str] = Field("EPSG:4326", description="Coordinate reference system")
    
    @validator('method')
    def validate_method(cls, v):
        valid_methods = ['dbscan', 'kmeans', 'hierarchical']
        if v not in valid_methods:
            raise ValueError(f'Method must be one of {valid_methods}')
        return v


class HotspotRequest(BaseModel):
    """Request model for hotspot detection operations."""
    
    points: FeatureCollection = Field(
        ..., description="Point data for hotspot analysis"
    )
    value_column: Optional[str] = Field(
        None, description="Column with values (if None, uses point density)"
    )
    method: str = Field(
        "getis_ord", description="Hotspot detection method"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        {}, description="Method-specific parameters"
    )
    crs: Optional[str] = Field("EPSG:4326", description="Coordinate reference system")
    
    @validator('method')
    def validate_method(cls, v):
        valid_methods = ['getis_ord', 'local_moran', 'kernel_density']
        if v not in valid_methods:
            raise ValueError(f'Method must be one of {valid_methods}')
        return v


class NetworkAnalysisRequest(BaseModel):
    """Request model for network analysis operations."""
    
    network: FeatureCollection = Field(
        ..., description="Network edges as LineString features"
    )
    origins: Optional[FeatureCollection] = Field(
        None, description="Origin points for routing analysis"
    )
    destinations: Optional[FeatureCollection] = Field(
        None, description="Destination points for routing analysis"
    )
    analysis_type: str = Field(
        ..., description="Type of network analysis"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        {}, description="Analysis-specific parameters"
    )
    crs: Optional[str] = Field("EPSG:4326", description="Coordinate reference system")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = ['shortest_path', 'service_area', 'connectivity', 'routing', 'accessibility']
        if v not in valid_types:
            raise ValueError(f'Analysis type must be one of {valid_types}')
        return v


class TerrainAnalysisRequest(BaseModel):
    """Request model for terrain analysis operations."""
    
    dem_data: str = Field(
        ..., description="Path to DEM raster or base64 encoded raster data"
    )
    analyses: List[str] = Field(
        ["slope", "aspect", "hillshade"], 
        description="List of terrain analyses to perform"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        {}, description="Analysis-specific parameters"
    )
    
    @validator('analyses')
    def validate_analyses(cls, v):
        valid_analyses = ['slope', 'aspect', 'hillshade', 'curvature', 'tpi']
        for analysis in v:
            if analysis not in valid_analyses:
                raise ValueError(f'Analysis must be one of {valid_analyses}')
        return v


class H3AnalysisRequest(BaseModel):
    """Request model for H3 hexagonal grid operations."""
    
    geometry: Union[Feature, FeatureCollection, Polygon] = Field(
        ..., description="Geometry to convert to H3 cells"
    )
    resolution: int = Field(
        ..., ge=0, le=15, description="H3 resolution (0-15)"
    )
    operation: str = Field(
        "polygon_to_cells", description="H3 operation to perform"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        {}, description="Operation-specific parameters"
    )
    
    @validator('operation')
    def validate_operation(cls, v):
        valid_ops = ['polygon_to_cells', 'grid_disk', 'compact_cells', 'cell_to_boundary']
        if v not in valid_ops:
            raise ValueError(f'Operation must be one of {valid_ops}')
        return v


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
