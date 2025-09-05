"""
Pydantic data models for spatial data structures.

This module defines data models for representing spatial datasets,
geometries, coordinate systems, and analysis results with automatic
validation and serialization capabilities.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from geojson_pydantic import Feature, FeatureCollection, Point, Polygon, LineString


class GeometryType(str, Enum):
    """Enumeration of supported geometry types."""
    POINT = "Point"
    LINESTRING = "LineString"
    POLYGON = "Polygon"
    MULTIPOINT = "MultiPoint"
    MULTILINESTRING = "MultiLineString"
    MULTIPOLYGON = "MultiPolygon"
    GEOMETRYCOLLECTION = "GeometryCollection"


class CoordinateReferenceSystem(BaseModel):
    """Model for coordinate reference system information."""
    
    epsg_code: Optional[int] = Field(None, description="EPSG code")
    proj4_string: Optional[str] = Field(None, description="PROJ4 string")
    wkt: Optional[str] = Field(None, description="Well-Known Text representation")
    name: Optional[str] = Field(None, description="CRS name")
    is_projected: bool = Field(False, description="Whether CRS is projected")
    units: Optional[str] = Field(None, description="Linear units")
    
    @validator('epsg_code')
    def validate_epsg_code(cls, v):
        if v is not None and (v < 1000 or v > 32767):
            raise ValueError('EPSG code must be between 1000 and 32767')
        return v


class GeometryModel(BaseModel):
    """Model for geometry objects with validation."""
    
    geometry: Union[Point, Polygon, LineString] = Field(..., description="GeoJSON geometry")
    crs: Optional[CoordinateReferenceSystem] = Field(None, description="Coordinate reference system")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Geometry properties")
    
    def to_feature(self) -> Feature:
        """Convert to GeoJSON Feature."""
        return Feature(
            geometry=self.geometry,
            properties=self.properties
        )


class SpatialBounds(BaseModel):
    """Model for spatial bounding box."""
    
    minx: float = Field(..., description="Minimum X coordinate")
    miny: float = Field(..., description="Minimum Y coordinate")
    maxx: float = Field(..., description="Maximum X coordinate")
    maxy: float = Field(..., description="Maximum Y coordinate")
    minz: Optional[float] = Field(None, description="Minimum Z coordinate")
    maxz: Optional[float] = Field(None, description="Maximum Z coordinate")
    
    @validator('maxx')
    def validate_x_bounds(cls, v, values):
        if 'minx' in values and v <= values['minx']:
            raise ValueError('maxx must be greater than minx')
        return v
    
    @validator('maxy')
    def validate_y_bounds(cls, v, values):
        if 'miny' in values and v <= values['miny']:
            raise ValueError('maxy must be greater than miny')
        return v
    
    @property
    def width(self) -> float:
        """Calculate width of bounding box."""
        return self.maxx - self.minx
    
    @property
    def height(self) -> float:
        """Calculate height of bounding box."""
        return self.maxy - self.miny
    
    @property
    def area(self) -> float:
        """Calculate area of bounding box."""
        return self.width * self.height


class SpatialIndex(BaseModel):
    """Model for spatial index configuration."""
    
    index_type: str = Field(..., description="Type of spatial index")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Index parameters")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    num_features: int = Field(0, description="Number of indexed features")
    
    @validator('index_type')
    def validate_index_type(cls, v):
        valid_types = ['rtree', 'quadtree', 'h3', 'geohash', 's2']
        if v.lower() not in valid_types:
            raise ValueError(f'Index type must be one of {valid_types}')
        return v.lower()


class SpatialMetadata(BaseModel):
    """Model for spatial dataset metadata."""
    
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    source: Optional[str] = Field(None, description="Data source")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    bounds: Optional[SpatialBounds] = Field(None, description="Spatial bounds")
    crs: Optional[CoordinateReferenceSystem] = Field(None, description="Coordinate reference system")
    num_features: int = Field(0, description="Number of features")
    geometry_types: List[GeometryType] = Field(default_factory=list, description="Geometry types present")
    attributes: Dict[str, str] = Field(default_factory=dict, description="Attribute column types")
    tags: List[str] = Field(default_factory=list, description="Dataset tags")
    license: Optional[str] = Field(None, description="Data license")
    
    @validator('num_features')
    def validate_num_features(cls, v):
        if v < 0:
            raise ValueError('Number of features cannot be negative')
        return v


class SpatialDataset(BaseModel):
    """Model for complete spatial dataset."""
    
    metadata: SpatialMetadata = Field(..., description="Dataset metadata")
    features: Union[FeatureCollection, List[Feature]] = Field(..., description="Spatial features")
    spatial_index: Optional[SpatialIndex] = Field(None, description="Spatial index information")
    
    @validator('features')
    def validate_features(cls, v, values):
        if isinstance(v, list):
            # Convert list of features to FeatureCollection
            v = FeatureCollection(features=v)
        
        # Update metadata with feature count
        if 'metadata' in values:
            values['metadata'].num_features = len(v.features)
        
        return v
    
    def get_bounds(self) -> Optional[SpatialBounds]:
        """Calculate spatial bounds of the dataset."""
        if not self.features.features:
            return None
        
        # Extract coordinates from all geometries
        all_coords = []
        for feature in self.features.features:
            geom = feature.geometry
            coords = self._extract_coordinates(geom.dict())
            all_coords.extend(coords)
        
        if not all_coords:
            return None
        
        # Calculate bounds
        xs, ys = zip(*all_coords)
        return SpatialBounds(
            minx=min(xs),
            miny=min(ys),
            maxx=max(xs),
            maxy=max(ys)
        )
    
    def _extract_coordinates(self, geometry: Dict[str, Any]) -> List[Tuple[float, float]]:
        """Extract coordinate pairs from geometry."""
        geom_type = geometry.get('type')
        coordinates = geometry.get('coordinates', [])
        
        if geom_type == 'Point':
            return [tuple(coordinates[:2])]
        elif geom_type in ['LineString', 'MultiPoint']:
            return [tuple(coord[:2]) for coord in coordinates]
        elif geom_type in ['Polygon', 'MultiLineString']:
            coords = []
            for ring in coordinates:
                coords.extend([tuple(coord[:2]) for coord in ring])
            return coords
        elif geom_type == 'MultiPolygon':
            coords = []
            for polygon in coordinates:
                for ring in polygon:
                    coords.extend([tuple(coord[:2]) for coord in ring])
            return coords
        elif geom_type == 'GeometryCollection':
            coords = []
            for geom in geometry.get('geometries', []):
                coords.extend(self._extract_coordinates(geom))
            return coords
        
        return []


class AnalysisResult(BaseModel):
    """Model for spatial analysis results."""
    
    analysis_type: str = Field(..., description="Type of analysis performed")
    success: bool = Field(..., description="Whether analysis succeeded")
    result_data: Optional[Union[FeatureCollection, Dict[str, Any]]] = Field(
        None, description="Analysis result data"
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    @validator('execution_time')
    def validate_execution_time(cls, v):
        if v is not None and v < 0:
            raise ValueError('Execution time cannot be negative')
        return v


class H3CellData(BaseModel):
    """Model for H3 hexagonal cell data."""
    
    h3_index: str = Field(..., description="H3 cell index")
    resolution: int = Field(..., ge=0, le=15, description="H3 resolution")
    center_lat: float = Field(..., description="Cell center latitude")
    center_lng: float = Field(..., description="Cell center longitude")
    boundary: List[Tuple[float, float]] = Field(..., description="Cell boundary coordinates")
    area_km2: Optional[float] = Field(None, description="Cell area in square kilometers")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Cell properties")
    
    @validator('h3_index')
    def validate_h3_index(cls, v):
        # Basic H3 index validation (should be 15-character hex string for most resolutions)
        if not isinstance(v, str) or len(v) < 8 or len(v) > 16:
            raise ValueError('Invalid H3 index format')
        return v
    
    @validator('center_lat')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('center_lng')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class NetworkEdge(BaseModel):
    """Model for network edge data."""
    
    edge_id: str = Field(..., description="Unique edge identifier")
    source_node: str = Field(..., description="Source node identifier")
    target_node: str = Field(..., description="Target node identifier")
    geometry: LineString = Field(..., description="Edge geometry (LineString)")
    length: float = Field(..., gt=0, description="Edge length")
    weight: Optional[float] = Field(None, description="Edge weight for routing")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Edge attributes")
    
    @validator('geometry')
    def validate_geometry_type(cls, v):
        if v.type != 'LineString':
            raise ValueError('Network edge geometry must be LineString')
        return v


class NetworkNode(BaseModel):
    """Model for network node data."""
    
    node_id: str = Field(..., description="Unique node identifier")
    geometry: Point = Field(..., description="Node geometry (Point)")
    degree: int = Field(0, ge=0, description="Node degree (number of connections)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Node attributes")
    
    @validator('geometry')
    def validate_geometry_type(cls, v):
        if v.type != 'Point':
            raise ValueError('Network node geometry must be Point')
        return v


class SpatialNetwork(BaseModel):
    """Model for spatial network data."""
    
    name: str = Field(..., description="Network name")
    nodes: List[NetworkNode] = Field(..., description="Network nodes")
    edges: List[NetworkEdge] = Field(..., description="Network edges")
    crs: Optional[CoordinateReferenceSystem] = Field(None, description="Coordinate reference system")
    is_directed: bool = Field(False, description="Whether network is directed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Network metadata")
    
    @property
    def num_nodes(self) -> int:
        """Number of nodes in the network."""
        return len(self.nodes)
    
    @property
    def num_edges(self) -> int:
        """Number of edges in the network."""
        return len(self.edges)
    
    def get_bounds(self) -> Optional[SpatialBounds]:
        """Calculate spatial bounds of the network."""
        if not self.nodes:
            return None
        
        coords = []
        for node in self.nodes:
            if node.geometry.type == 'Point':
                coords.append(tuple(node.geometry.coordinates[:2]))
        
        if not coords:
            return None
        
        xs, ys = zip(*coords)
        return SpatialBounds(
            minx=min(xs),
            miny=min(ys),
            maxx=max(xs),
            maxy=max(ys)
        )
