"""
API endpoints for GeoJSON polygon operations.

This module implements OGC API Features compatible endpoints for working with GeoJSON polygons.
"""
from typing import Dict, List, Optional, Tuple, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse

from geo_infer_api.core.config import get_settings, Settings
from geo_infer_api.core.exceptions import BadRequestError, ConflictError, GeometryError, NotFoundError, ValidationError
from geo_infer_api.models.geojson import (
    Feature, FeatureCollection, GeoJSONType, Polygon, PolygonFeature, PolygonFeatureCollection
)
from geo_infer_api.utils.geojson_helpers import (
    calculate_polygon_area, create_polygon_feature, polygon_contains_point, simplify_polygon,
    create_buffer, calculate_intersection, calculate_union, calculate_distance
)

# Create router
router = APIRouter()

# In-memory storage for demo purposes
# In a real application, this would be replaced with a database
POLYGON_FEATURES: Dict[str, PolygonFeature] = {}


@router.get("/collections", summary="List available feature collections")
async def list_collections(settings: Settings = Depends(get_settings)):
    """
    List available feature collections.
    
    This endpoint follows the OGC API Features standard for listing collections.
    """
    return {
        "collections": [
            {
                "id": "polygons",
                "title": "GeoJSON Polygons",
                "description": "Collection of polygon features",
                "links": [
                    {
                        "href": f"{settings.api_prefix}/collections/polygons",
                        "rel": "self",
                        "type": "application/json",
                        "title": "This collection"
                    },
                    {
                        "href": f"{settings.api_prefix}/collections/polygons/items",
                        "rel": "items",
                        "type": "application/geo+json",
                        "title": "Items in this collection"
                    }
                ]
            }
        ],
        "links": [
            {
                "href": f"{settings.api_prefix}/collections",
                "rel": "self",
                "type": "application/json",
                "title": "Collections"
            }
        ]
    }


@router.get(
    "/collections/polygons",
    summary="Get polygon collection metadata"
)
async def get_polygon_collection(settings: Settings = Depends(get_settings)):
    """
    Get metadata about the polygon collection.
    
    This endpoint follows the OGC API Features standard for describing a collection.
    """
    return {
        "id": "polygons",
        "title": "GeoJSON Polygons",
        "description": "Collection of polygon features",
        "extent": {
            "spatial": {
                "bbox": [[-180, -90, 180, 90]]
            },
            "temporal": {
                "interval": [["2020-01-01T00:00:00Z", "2025-01-01T00:00:00Z"]]
            }
        },
        "links": [
            {
                "href": f"{settings.api_prefix}/collections/polygons",
                "rel": "self",
                "type": "application/json",
                "title": "This collection"
            },
            {
                "href": f"{settings.api_prefix}/collections/polygons/items",
                "rel": "items",
                "type": "application/geo+json",
                "title": "Items in this collection"
            }
        ]
    }


@router.get(
    "/collections/polygons/items",
    response_model=PolygonFeatureCollection,
    response_model_exclude_none=True,
    summary="List polygon features"
)
async def list_polygon_features(
    bbox: Optional[str] = Query(
        None,
        description="Bounding box (minLon,minLat,maxLon,maxLat)"
    ),
    limit: int = Query(10, ge=1, le=1000, description="Maximum number of features to return")
):
    """
    List polygon features with optional filtering.
    
    This endpoint follows the OGC API Features standard for listing items in a collection.
    
    Args:
        bbox: Optional bounding box filter in format "minLon,minLat,maxLon,maxLat"
        limit: Maximum number of features to return (1-1000)
    
    Returns:
        GeoJSON FeatureCollection of polygon features
    """
    features = list(POLYGON_FEATURES.values())
    
    # Apply bounding box filter if provided
    if bbox:
        try:
            min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
            
            # Filter features that intersect with the bounding box
            # This is a simplified intersection check
            def polygon_intersects_bbox(polygon_feature):
                for ring in polygon_feature.geometry.coordinates:
                    for lon, lat in ring:
                        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                            return True
                return False
            
            features = [f for f in features if polygon_intersects_bbox(f)]
        except ValueError:
            raise BadRequestError(
                "Invalid bbox format. Expected 'minLon,minLat,maxLon,maxLat'",
                field="bbox"
            )
    
    # Apply limit
    features = features[:limit]
    
    return PolygonFeatureCollection(
        type=GeoJSONType.FEATURE_COLLECTION,
        features=features
    )


@router.get(
    "/collections/polygons/items/{feature_id}",
    response_model=PolygonFeature,
    response_model_exclude_none=True,
    summary="Get a specific polygon feature"
)
async def get_polygon_feature(
    feature_id: str = Path(..., description="ID of the feature to retrieve")
):
    """
    Get a specific polygon feature by ID.
    
    This endpoint follows the OGC API Features standard for retrieving a single feature.
    
    Args:
        feature_id: ID of the feature to retrieve
    
    Returns:
        GeoJSON Feature with Polygon geometry
    
    Raises:
        HTTPException: If the feature is not found
    """
    if feature_id not in POLYGON_FEATURES:
        raise NotFoundError("Polygon feature", feature_id)
    
    return POLYGON_FEATURES[feature_id]


@router.post(
    "/collections/polygons/items",
    response_model=PolygonFeature,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new polygon feature"
)
async def create_polygon_feature_endpoint(
    feature: PolygonFeature
):
    """
    Create a new polygon feature.
    
    Args:
        feature: GeoJSON Feature with Polygon geometry
    
    Returns:
        The created feature
    
    Raises:
        HTTPException: If the feature ID already exists or has invalid geometry
    """
    # Ensure we have an ID
    if not feature.id:
        raise ValidationError("Feature must have an ID", field="id")
    
    # Check if ID already exists
    if feature.id in POLYGON_FEATURES:
        raise ConflictError("Polygon feature", "already exists", feature.id)
    
    # Store the feature
    POLYGON_FEATURES[feature.id] = feature
    
    return feature


@router.put(
    "/collections/polygons/items/{feature_id}",
    response_model=PolygonFeature,
    summary="Update a polygon feature"
)
async def update_polygon_feature(
    feature: PolygonFeature,
    feature_id: str = Path(..., description="ID of the feature to update")
):
    """
    Update an existing polygon feature.
    
    Args:
        feature: Updated GeoJSON Feature with Polygon geometry
        feature_id: ID of the feature to update
    
    Returns:
        The updated feature
    
    Raises:
        HTTPException: If the feature is not found
    """
    if feature_id not in POLYGON_FEATURES:
        raise NotFoundError("Polygon feature", feature_id)
    
    # Ensure the IDs match
    if feature.id and feature.id != feature_id:
        raise ValidationError("Feature ID in body does not match path parameter", field="id")
    
    # Update the feature
    feature.id = feature_id  # Ensure ID is set
    POLYGON_FEATURES[feature_id] = feature
    
    return feature


@router.delete(
    "/collections/polygons/items/{feature_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a polygon feature"
)
async def delete_polygon_feature(
    feature_id: str = Path(..., description="ID of the feature to delete")
):
    """
    Delete a polygon feature.
    
    Args:
        feature_id: ID of the feature to delete
    
    Raises:
        HTTPException: If the feature is not found
    """
    if feature_id not in POLYGON_FEATURES:
        raise NotFoundError("Polygon feature", feature_id)
    
    # Delete the feature
    del POLYGON_FEATURES[feature_id]
    
    return None


# Enhanced endpoints for polygon operations

@router.post(
    "/operations/polygon/area",
    summary="Calculate polygon area"
)
async def calculate_area(feature: PolygonFeature):
    """
    Calculate the approximate area of a polygon in square kilometers.

    Args:
        feature: GeoJSON Feature with Polygon geometry

    Returns:
        Area in square kilometers
    """
    area = calculate_polygon_area(feature.geometry)

    return {
        "area_sq_km": area,
        "feature_id": feature.id,
        "method": "planar"
    }


@router.post(
    "/operations/polygon/simplify",
    response_model=PolygonFeature,
    summary="Simplify a polygon"
)
async def simplify_polygon_endpoint(
    feature: PolygonFeature,
    tolerance: float = Query(0.01, ge=0.001, le=1.0, description="Simplification tolerance")
):
    """
    Simplify a polygon using the Ramer-Douglas-Peucker algorithm.
    
    Args:
        feature: GeoJSON Feature with Polygon geometry
        tolerance: Simplification tolerance (higher values produce simpler polygons)
    
    Returns:
        Simplified polygon feature
    """
    simplified_geometry = simplify_polygon(feature.geometry, tolerance)
    
    return PolygonFeature(
        type=GeoJSONType.FEATURE,
        geometry=simplified_geometry,
        properties=feature.properties,
        id=feature.id
    )


@router.post(
    "/operations/polygon/contains",
    summary="Check if a polygon contains a point"
)
async def check_polygon_contains_point(
    feature: PolygonFeature,
    lon: float = Query(..., ge=-180, le=180, description="Longitude of the point"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude of the point")
):
    """
    Check if a polygon contains a point.
    
    Args:
        feature: GeoJSON Feature with Polygon geometry
        lon: Longitude of the point to check
        lat: Latitude of the point to check
    
    Returns:
        True if the polygon contains the point, False otherwise
    """
    contains = polygon_contains_point(feature.geometry, (lon, lat))
    
    return {
        "contains": contains,
        "feature_id": feature.id,
        "point": [lon, lat],
        "method": "ray_casting"
    }


@router.post(
    "/operations/polygon/buffer",
    response_model=PolygonFeature,
    summary="Create a buffer around a polygon"
)
async def create_buffer_endpoint(
    feature: PolygonFeature,
    distance: float = Query(..., ge=0, description="Buffer distance in kilometers"),
    unit: str = Query("kilometers", enum=["meters", "kilometers", "miles"], description="Unit for the buffer distance"),
    segments: int = Query(16, ge=8, le=100, description="Number of segments for buffer approximation")
):
    """
    Create a buffer zone around a polygon at a specified distance.

    Args:
        feature: GeoJSON Feature with Polygon geometry
        distance: Buffer distance (in the specified unit)
        unit: Unit for the distance ("meters", "kilometers", or "miles")
        segments: Number of segments for the buffer approximation

    Returns:
        Buffered polygon feature
    """
    buffered_geometry = create_buffer(feature.geometry, distance, unit, segments)

    return PolygonFeature(
        type=GeoJSONType.FEATURE,
        geometry=buffered_geometry,
        properties={
            **feature.properties,
            "buffer_distance": distance,
            "buffer_unit": unit,
            "buffer_segments": segments
        },
        id=f"{feature.id}_buffer" if feature.id else None
    )


@router.post(
    "/operations/polygon/intersection",
    response_model=PolygonFeature,
    summary="Calculate intersection of multiple polygons"
)
async def calculate_intersection_endpoint(
    request: dict
):
    """
    Calculate the intersection area of multiple polygon features.

    Args:
        request: Dictionary containing array of polygon features

    Returns:
        Intersection polygon feature
    """
    polygons = request.get("polygons", [])
    if len(polygons) < 2:
        raise ValidationError("At least 2 polygons required for intersection")

    # Convert to Polygon objects for processing
    polygon_objects = []
    for poly in polygons:
        if isinstance(poly, dict) and poly.get("type") == GeoJSONType.FEATURE:
            polygon_objects.append(poly["geometry"])
        else:
            raise ValidationError("Invalid polygon feature format")

    intersection_geometry = calculate_intersection(polygon_objects)

    return PolygonFeature(
        type=GeoJSONType.FEATURE,
        geometry=intersection_geometry,
        properties={"operation": "intersection"},
        id="intersection_result"
    )


@router.post(
    "/operations/polygon/union",
    response_model=PolygonFeature,
    summary="Calculate union of multiple polygons"
)
async def calculate_union_endpoint(
    request: dict
):
    """
    Calculate the union area of multiple polygon features.

    Args:
        request: Dictionary containing array of polygon features

    Returns:
        Union polygon feature
    """
    polygons = request.get("polygons", [])
    if len(polygons) < 2:
        raise ValidationError("At least 2 polygons required for union")

    # Convert to Polygon objects for processing
    polygon_objects = []
    for poly in polygons:
        if isinstance(poly, dict) and poly.get("type") == GeoJSONType.FEATURE:
            polygon_objects.append(poly["geometry"])
        else:
            raise ValidationError("Invalid polygon feature format")

    union_geometry = calculate_union(polygon_objects)

    return PolygonFeature(
        type=GeoJSONType.FEATURE,
        geometry=union_geometry,
        properties={"operation": "union"},
        id="union_result"
    )


@router.post(
    "/operations/polygon/distance",
    summary="Calculate distance between polygons"
)
async def calculate_distance_endpoint(
    request: dict
):
    """
    Calculate the minimum distance between two polygon features.

    Args:
        request: Dictionary containing polygon1 and polygon2 features

    Returns:
        Distance calculation result
    """
    polygon1 = request.get("polygon1")
    polygon2 = request.get("polygon2")

    if not polygon1 or not polygon2:
        raise ValidationError("Both polygon1 and polygon2 are required")

    # Extract geometries for processing
    if isinstance(polygon1, dict) and polygon1.get("type") == GeoJSONType.FEATURE:
        geom1 = polygon1["geometry"]
    else:
        raise ValidationError("Invalid polygon1 format")

    if isinstance(polygon2, dict) and polygon2.get("type") == GeoJSONType.FEATURE:
        geom2 = polygon2["geometry"]
    else:
        raise ValidationError("Invalid polygon2 format")

    distance = calculate_distance(geom1, geom2, method="centroid")

    return {
        "distance_km": distance,
        "unit": "kilometers",
        "method": "centroid"
    } 