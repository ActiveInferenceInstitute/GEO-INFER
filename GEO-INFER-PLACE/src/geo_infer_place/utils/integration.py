"""
Del Norte data integration utilities.

Provides thin wrappers over specific API clients to expose a consistent
interface expected by Del Norte analyzers (forest, coastal, fire).

This module focuses on real data endpoints where available:
- CAL FIRE perimeters via ArcGIS REST
- NOAA Tides and Currents for water levels

Other endpoints can be extended incrementally.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..core.api_clients import CaliforniaAPIManager


class _CALFIREWrapper:
    """Wrapper exposing analyzer-facing methods for CAL FIRE data."""

    def __init__(self, api_manager: CaliforniaAPIManager) -> None:
        self._client = api_manager.calfire

    def get_fire_perimeters(
        self,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        start_year: Optional[int] = None,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """Fetch fire perimeters optionally filtered by year and county via bbox.

        Args:
            bbox: (west, south, east, north). If provided and county not known,
                  perimeters will be filtered client-side by simple bbox.
            start_year: Minimum fire year to include
            include_metadata: Returned GeoJSON keeps all properties

        Returns:
            GeoJSON FeatureCollection dict
        """
        # Server-side filter by year and county when possible
        geojson = self._client.fetch_perimeters(year=start_year, county="Del Norte")

        if not bbox:
            return geojson

        # Client-side bbox filter as safety net
        west, south, east, north = bbox
        feats: List[Dict[str, Any]] = []
        for feat in geojson.get("features", []):
            geom = feat.get("geometry", {})
            coords = []
            if geom.get("type") == "Polygon":
                coords = geom.get("coordinates", [])
            elif geom.get("type") == "MultiPolygon":
                for part in geom.get("coordinates", []):
                    coords.extend(part)
            # Flatten and test any coordinate
            include = False
            for ring in coords:
                for lon, lat in ring:
                    if west <= lon <= east and south <= lat <= north:
                        include = True
                        break
                if include:
                    break
            if include:
                feats.append(feat)

        return {"type": "FeatureCollection", "features": feats}


class _NOAAWrapper:
    """Wrapper exposing analyzer-facing methods for NOAA tides and currents."""

    def __init__(self, api_manager: CaliforniaAPIManager) -> None:
        self._client = api_manager.noaa

    def get_tide_gauge_data(
        self,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        stations: Optional[List[str]] = None,
        time_range: Optional[Tuple[str, str]] = None,
    ) -> Dict[str, Any]:
        """Fetch tide gauge water level time series for one or more stations.

        Args:
            bbox: Unused for NOAA direct calls; present for interface parity
            stations: List of station IDs (default to Crescent City 9419750)
            time_range: (YYYY-MM-DD, YYYY-MM-DD). Defaults to last 7 days.
        """
        if not stations:
            stations = ["9419750"]  # Crescent City

        if time_range:
            start, end = time_range
            begin_date = datetime.strptime(start, "%Y-%m-%d").strftime("%Y%m%d")
            end_date = datetime.strptime(end, "%Y-%m-%d").strftime("%Y%m%d")
        else:
            # Default to last 7 days
            end_date = datetime.utcnow().strftime("%Y%m%d")
            begin_date = datetime.utcnow().strftime("%Y%m%d")

        series: Dict[str, Any] = {}
        for station in stations:
            data = self._client.fetch_tide_data(
                station=station, begin_date=begin_date, end_date=end_date, product="water_level"
            )
            series[station] = data
        return {"stations": stations, "series": series}


class DelNorteDataIntegrator:
    """Integrator that aggregates API wrappers for analyzers.

    Attributes exposed for analyzers:
    - calfire_client: provides get_fire_perimeters(...)
    - noaa_client: provides get_tide_gauge_data(...)
    """

    def __init__(self) -> None:
        api_manager = CaliforniaAPIManager()
        self.calfire_client = _CALFIREWrapper(api_manager)
        self.noaa_client = _NOAAWrapper(api_manager)


