"""
Pydantic models for GeoJSON data structures.

These models follow the GeoJSON specification (RFC 7946)
https://tools.ietf.org/html/rfc7946
"""
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GeoJSONType(str, Enum):
    """Valid GeoJSON types."""
    POINT = "Point"
    MULTI_POINT = "MultiPoint"
    LINE_STRING = "LineString"
    MULTI_LINE_STRING = "MultiLineString"
    POLYGON = "Polygon"
    MULTI_POLYGON = "MultiPolygon"
    GEOMETRY_COLLECTION = "GeometryCollection"
    FEATURE = "Feature"
    FEATURE_COLLECTION = "FeatureCollection"


# Base geometry models
class GeometryBase(BaseModel):
    """Base model for all GeoJSON geometry objects."""
    model_config = ConfigDict(extra="forbid")

    type: GeoJSONType
    coordinates: Any  # Will be validated by subclasses


class Point(GeometryBase):
    """GeoJSON Point geometry."""
    type: Literal[GeoJSONType.POINT] = GeoJSONType.POINT
    coordinates: Tuple[float, float] = Field(..., description="[longitude, latitude]")

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: Tuple[float, float]) -> Tuple[float, float]:
        """Validate point coordinates."""
        if len(v) != 2:
            raise ValueError("Point coordinates must be [longitude, latitude]")
        lon, lat = v
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v


class LineString(GeometryBase):
    """GeoJSON LineString geometry."""
    type: Literal[GeoJSONType.LINE_STRING] = GeoJSONType.LINE_STRING
    coordinates: List[Tuple[float, float]] = Field(
        ..., description="Array of [longitude, latitude] positions"
    )

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Validate LineString has at least 2 points."""
        if len(v) < 2:
            raise ValueError("LineString must have at least 2 points")
        return v


class Polygon(GeometryBase):
    """GeoJSON Polygon geometry.

    The first array of coordinates represents the exterior ring.
    Any subsequent arrays represent interior rings (holes).
    """
    type: Literal[GeoJSONType.POLYGON] = GeoJSONType.POLYGON
    coordinates: List[List[Tuple[float, float]]] = Field(
        ..., description="Array of linear rings"
    )

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(
        cls, v: List[List[Tuple[float, float]]]
    ) -> List[List[Tuple[float, float]]]:
        """Validate Polygon rings."""
        if not v or len(v) < 1:
            raise ValueError("Polygon must have at least one linear ring")

        for ring in v:
            # Each linear ring must have at least 4 positions (first = last)
            if len(ring) < 4:
                raise ValueError("Each polygon ring must have at least 4 positions")

            # First and last positions must be the same (closed ring)
            if ring[0] != ring[-1]:
                raise ValueError("First and last positions in a polygon ring must be the same")

        return v


class MultiPoint(GeometryBase):
    """GeoJSON MultiPoint geometry."""
    type: Literal[GeoJSONType.MULTI_POINT] = GeoJSONType.MULTI_POINT
    coordinates: List[Tuple[float, float]] = Field(..., description="Array of positions")


class MultiLineString(GeometryBase):
    """GeoJSON MultiLineString geometry."""
    type: Literal[GeoJSONType.MULTI_LINE_STRING] = GeoJSONType.MULTI_LINE_STRING
    coordinates: List[List[Tuple[float, float]]] = Field(
        ..., description="Array of line strings"
    )


class MultiPolygon(GeometryBase):
    """GeoJSON MultiPolygon geometry."""
    type: Literal[GeoJSONType.MULTI_POLYGON] = GeoJSONType.MULTI_POLYGON
    coordinates: List[List[List[Tuple[float, float]]]] = Field(
        ..., description="Array of polygons"
    )


# Union of all geometry types
Geometry = Union[Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon]


class Feature(BaseModel):
    """GeoJSON Feature object."""
    model_config = ConfigDict(extra="forbid")

    type: Literal[GeoJSONType.FEATURE] = GeoJSONType.FEATURE
    geometry: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    id: Optional[Union[str, int]] = None


class FeatureCollection(BaseModel):
    """GeoJSON FeatureCollection object."""
    model_config = ConfigDict(extra="forbid")

    type: Literal[GeoJSONType.FEATURE_COLLECTION] = GeoJSONType.FEATURE_COLLECTION
    features: List[Feature] = Field(..., description="Array of features")


# Specialized models for specific API operations

class PolygonFeature(Feature):
    """A GeoJSON Feature with a Polygon geometry."""
    geometry: Polygon  # type: ignore[assignment]

    @model_validator(mode="before")
    @classmethod
    def ensure_polygon_geometry(cls, values: Any) -> Any:
        """Ensure the geometry is a Polygon."""
        geometry = values.get("geometry") if isinstance(values, dict) else None
        if geometry and isinstance(geometry, dict):
            if geometry.get("type") != GeoJSONType.POLYGON:
                raise ValueError("Geometry must be a Polygon")
        return values


class PolygonFeatureCollection(FeatureCollection):
    """A GeoJSON FeatureCollection containing only Polygon features."""
    features: List[PolygonFeature]  # type: ignore[assignment]
