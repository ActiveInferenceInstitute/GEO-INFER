"""
GEO-INFER-API package.

A standardized API for geospatial interoperability within the GEO-INFER framework.
"""

__version__ = "0.2.0"

try:
    from geo_infer_api.app import main_app
    from geo_infer_api.core.config import Settings, get_settings
    from geo_infer_api.models.geojson import (
        Feature,
        FeatureCollection,
        GeoJSONType,
        Geometry,
        LineString,
        MultiLineString,
        MultiPoint,
        MultiPolygon,
        Point,
        Polygon,
        PolygonFeature,
        PolygonFeatureCollection,
    )
    __all__ = [
        "__version__",
        "main_app",
        "Settings",
        "get_settings",
        "Feature",
        "FeatureCollection",
        "GeoJSONType",
        "Geometry",
        "LineString",
        "MultiLineString",
        "MultiPoint",
        "MultiPolygon",
        "Point",
        "Polygon",
        "PolygonFeature",
        "PolygonFeatureCollection",
    ]
except ImportError:
    # Graceful degradation when optional dependencies are not installed
    __all__ = ["__version__"]
