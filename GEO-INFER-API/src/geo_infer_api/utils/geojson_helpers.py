"""
Utility functions for working with GeoJSON data.
"""
from typing import Dict, List, Tuple, Union

from geo_infer_api.models.geojson import (
    Feature, FeatureCollection, GeoJSONType, Polygon, PolygonFeature
)


def validate_polygon_rings(coordinates: List[List[Tuple[float, float]]]) -> bool:
    """
    Validate that a polygon's rings follow the GeoJSON specification.
    
    Args:
        coordinates: List of rings where each ring is a list of [lon, lat] coordinates
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not coordinates or len(coordinates) < 1:
        return False
    
    for ring in coordinates:
        # Each ring must have at least 4 coordinates (closed loop)
        if len(ring) < 4:
            return False
        
        # First and last positions must be identical (closed loop)
        if ring[0] != ring[-1]:
            return False
        
        # Check coordinate bounds
        for pos in ring:
            lon, lat = pos
            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                return False
    
    return True


def calculate_polygon_area(polygon: Union[Polygon, Dict]) -> float:
    """
    Calculate the approximate area of a polygon in square kilometers.
    Uses a simple planar calculation that is approximate for small areas.
    
    Args:
        polygon: A GeoJSON Polygon object or dict
        
    Returns:
        float: Area in square kilometers
    """
    if isinstance(polygon, Polygon):
        coords = polygon.coordinates[0]  # Use exterior ring only
    elif isinstance(polygon, dict) and polygon.get("type") == GeoJSONType.POLYGON:
        coords = polygon.get("coordinates", [[]])[0]
    else:
        raise ValueError("Input must be a GeoJSON Polygon")
    
    # Simple planar area calculation (approximate for small areas)
    n = len(coords) - 1  # Subtract 1 because the first/last points are the same
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    
    # Convert to square kilometers (very approximate)
    # 1 degree of longitude at the equator is approximately 111 km
    area = abs(area) * 0.5 * 111 * 111
    
    return area


def polygon_contains_point(polygon: Union[Polygon, Dict], point: Tuple[float, float]) -> bool:
    """
    Check if a point is inside a polygon using the ray casting algorithm.
    
    Args:
        polygon: A GeoJSON Polygon object or dict
        point: A (longitude, latitude) tuple
        
    Returns:
        bool: True if the point is inside the polygon, False otherwise
    """
    if isinstance(polygon, Polygon):
        exterior_ring = polygon.coordinates[0]
    elif isinstance(polygon, dict) and polygon.get("type") == GeoJSONType.POLYGON:
        exterior_ring = polygon.get("coordinates", [[]])[0]
    else:
        raise ValueError("Input must be a GeoJSON Polygon")
    
    x, y = point
    n = len(exterior_ring)
    inside = False
    
    p1x, p1y = exterior_ring[0]
    for i in range(1, n):
        p2x, p2y = exterior_ring[i]
        if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def simplify_polygon(polygon: Polygon, tolerance: float = 0.01) -> Polygon:
    """
    Simplify a polygon using the Ramer-Douglas-Peucker algorithm.
    
    Args:
        polygon: A GeoJSON Polygon object
        tolerance: The simplification tolerance
        
    Returns:
        Polygon: A simplified Polygon
    """
    def rdp(points, epsilon):
        """Recursive implementation of Ramer-Douglas-Peucker algorithm."""
        if len(points) <= 2:
            return points
        
        # Find the point with the maximum distance
        dmax = 0
        index = 0
        for i in range(1, len(points) - 1):
            d = perpendicular_distance(points[i], points[0], points[-1])
            if d > dmax:
                index = i
                dmax = d
        
        # If max distance is greater than epsilon, recursively simplify
        if dmax > epsilon:
            results1 = rdp(points[:index + 1], epsilon)
            results2 = rdp(points[index:], epsilon)
            return results1[:-1] + results2
        else:
            return [points[0], points[-1]]
    
    def perpendicular_distance(point, line_start, line_end):
        """Calculate perpendicular distance from point to line."""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Line is vertical
        if x1 == x2:
            return abs(x - x1)
        
        # Calculate the perpendicular distance
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        return abs(slope * x - y + intercept) / ((slope ** 2 + 1) ** 0.5)
    
    # Process each ring
    simplified_rings = []
    for ring in polygon.coordinates:
        # Apply RDP algorithm to the ring (excluding the closing point)
        simplified_ring = rdp(ring[:-1], tolerance)
        
        # Ensure we have at least 3 points in the simplified ring (excluding closing point)
        # If we have fewer than 3 points, keep the original ring
        if len(simplified_ring) < 3:
            simplified_ring = ring[:-1]
        
        # Ensure the ring is closed
        if simplified_ring[0] != simplified_ring[-1]:
            simplified_ring.append(simplified_ring[0])
        
        # Final check to ensure we have at least 4 points total (including closing point)
        if len(simplified_ring) < 4:
            # If simplification resulted in too few points, use the original ring
            simplified_rings.append(ring)
        else:
            simplified_rings.append(simplified_ring)
    
    # Create a new polygon with simplified coordinates
    return Polygon(type=GeoJSONType.POLYGON, coordinates=simplified_rings)


def create_polygon_feature(
    coordinates: List[List[Tuple[float, float]]],
    properties: Dict = None,
    feature_id: str = None
) -> PolygonFeature:
    """
    Create a GeoJSON PolygonFeature from coordinates.
    
    Args:
        coordinates: List of rings where each ring is a list of [lon, lat] coordinates
        properties: Optional properties to attach to the feature
        feature_id: Optional feature ID
        
    Returns:
        PolygonFeature: A GeoJSON Feature with Polygon geometry
    """
    # Validate the coordinates
    if not validate_polygon_rings(coordinates):
        raise ValueError("Invalid polygon coordinates")
    
    # Convert coordinates from list of tuples to list of lists for proper JSON serialization
    json_coordinates = []
    for ring in coordinates:
        json_ring = [[lon, lat] for lon, lat in ring]
        json_coordinates.append(json_ring)
    
    # Create the polygon geometry
    polygon = Polygon(type=GeoJSONType.POLYGON, coordinates=json_coordinates)
    
    # Create the feature
    return PolygonFeature(
        type=GeoJSONType.FEATURE,
        geometry=polygon,
        properties=properties or {},
        id=feature_id
    ) 