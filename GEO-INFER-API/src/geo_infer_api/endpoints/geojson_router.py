"""
API endpoints for GeoJSON polygon operations.

This module implements OGC API Features compatible endpoints for working with GeoJSON polygons.
"""
from typing import Dict, List, Optional, Tuple, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse

from geo_infer_api.core.config import get_settings, Settings
from geo_infer_api.models.geojson import (
    Feature, FeatureCollection, GeoJSONType, Polygon, PolygonFeature, PolygonFeatureCollection
)
from geo_infer_api.utils.geojson_helpers import (
    calculate_polygon_area, create_polygon_feature, polygon_contains_point, simplify_polygon
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bbox format. Expected 'minLon,minLat,maxLon,maxLat'"
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Polygon feature with ID {feature_id} not found"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feature must have an ID"
        )
    
    # Check if ID already exists
    if feature.id in POLYGON_FEATURES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A feature with ID {feature.id} already exists"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Polygon feature with ID {feature_id} not found"
        )
    
    # Ensure the IDs match
    if feature.id and feature.id != feature_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feature ID in body does not match path parameter"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Polygon feature with ID {feature_id} not found"
        )
    
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
        "feature_id": feature.id
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
        "point": [lon, lat]
    } 