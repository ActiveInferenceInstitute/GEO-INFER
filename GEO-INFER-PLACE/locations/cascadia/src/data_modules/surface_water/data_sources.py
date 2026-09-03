"""
Cascadian Surface Water Data Sources

This module is responsible for fetching surface water data (flowlines and
water bodies) from the USGS National Hydrography Dataset (NHD / NHDPlus HR)
and local fallback datasets for the Cascadia Bioregion.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import requests
from shapely.geometry import box

from .flowline_network import CascadiaFlowlineNetwork

logger = logging.getLogger(__name__)


class CascadianSurfaceWaterDataSources:
    """Handles fetching of surface water data from USGS NHD / NHDPlus HR services

    and local Cascadia flowline catalogs.
    """

    def __init__(self) -> None:
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "data_urls.json"
        )
        try:
            with open(config_path) as f:
                self.config: Dict[str, Any] = json.load(f).get("surface_water", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse surface_water config: {e}")
            self.config = {}

        self.flowlines_url: Optional[str] = self.config.get("nhd_flowlines_url")
        self.waterbodies_url: Optional[str] = self.config.get("nhd_waterbodies_url")
        # The packaged local NHDPlus HR extract lives next to the cascadia
        # config; deployments (and deterministic tests) can point at a
        # different dataset via GEO_INFER_CASCADIA_FLOWLINES_PATH.
        env_override = os.environ.get("GEO_INFER_CASCADIA_FLOWLINES_PATH")
        self._local_flowlines_path = (
            Path(env_override)
            if env_override
            else (
                Path(__file__).resolve().parents[3]
                / "config"
                / "cascadia_nhdplus_flowlines.geojson"
            )
        )

    def load_pnw_high_order_flowlines(
        self, min_stream_order: int = 4
    ) -> gpd.GeoDataFrame:
        """Load Cascadia high-order Pacific Northwest river flowlines from local

        NHDPlus HR dataset.

        Args:
            min_stream_order: Minimum Strahler stream order (default: 4 for mainstem/large tributaries)

        Returns:
            GeoDataFrame of high-order PNW flowlines with connectivity attributes.
        """
        if self._local_flowlines_path.exists():
            try:
                gdf = gpd.read_file(self._local_flowlines_path)
                if "stream_order" in gdf.columns:
                    filtered_gdf = gdf[gdf["stream_order"] >= min_stream_order].copy()
                    return filtered_gdf
                return gdf
            except Exception as e:
                logger.error(
                    f"Error reading local PNW flowlines from {self._local_flowlines_path}: {e}"
                )

        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

    def get_flowline_network(
        self, min_stream_order: int = 4
    ) -> CascadiaFlowlineNetwork:
        """Build and return a CascadiaFlowlineNetwork for high-order PNW tributaries."""
        flowlines_gdf = self.load_pnw_high_order_flowlines(
            min_stream_order=min_stream_order
        )
        return CascadiaFlowlineNetwork(flowlines_gdf)

    def _query_nhd_layer(
        self,
        service_url: Optional[str],
        layer_name: str,
        bbox: Tuple[float, float, float, float],
    ) -> gpd.GeoDataFrame:
        """Queries a specific layer from the NHD ArcGIS REST service for a given bounding box.

        Args:
            service_url: The full URL to the map service layer.
            layer_name: A descriptive name for logging (e.g., "flowlines").
            bbox: A tuple representing the bounding box (xmin, ymin, xmax, ymax)
                  in WGS84 (EPSG:4326).

        Returns:
            A GeoDataFrame containing the queried features, or an empty one on failure.
        """
        if os.environ.get("GEO_INFER_SURFACE_WATER_OFFLINE"):
            # Air-gapped / hermetic-test mode: use local datasets only.
            logger.info(
                "Surface water offline mode enabled; skipping NHD query for %s.",
                layer_name,
            )
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

        if not service_url:
            logger.error(f"No URL configured for NHD layer '{layer_name}'.")
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

        query_url = f"{service_url}/query"
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

        params = {
            "where": "1=1",
            "geometry": bbox_str,
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        }

        logger.info(f"Querying NHD {layer_name} with bbox: {bbox_str}")

        try:
            response = requests.get(query_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if not data.get("features"):
                logger.info(
                    f"No features found in {layer_name} for the given bounding box."
                )
                return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

            gdf = gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
            logger.info(f"Successfully fetched {len(gdf)} features from {layer_name}.")
            return gdf

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query NHD layer {layer_name}: {e}", exc_info=True)
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")
        except (KeyError, ValueError) as e:
            logger.error(
                f"Failed to parse GeoJSON response from NHD {layer_name}: {e}",
                exc_info=True,
            )
            return gpd.GeoDataFrame([], geometry=[], crs="EPSG:4326")

    def _query_osm_overpass_water(
        self, bbox: Tuple[float, float, float, float]
    ) -> Dict[str, gpd.GeoDataFrame]:
        """Query OSM Overpass for surface water features."""
        min_lon, min_lat, max_lon, max_lat = bbox

        # Query for both water polygons (lakes, reservoirs) and waterways (rivers, streams)
        overpass_query = f"""
        [out:json][timeout:120];
        (
          way["natural"="water"]({min_lat},{min_lon},{max_lat},{max_lon});
          relation["natural"="water"]({min_lat},{min_lon},{max_lat},{max_lon});
          way["waterway"]({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out body;
        >;
        out skel qt;
        """

        overpass_url = "https://overpass-api.de/api/interpreter"
        logger.info("Querying OpenStreetMap Overpass API for surface water...")

        try:
            response = requests.post(
                overpass_url, data={"data": overpass_query}, timeout=120
            )
            response.raise_for_status()
            data = response.json()

            nodes = {
                e["id"]: (e["lon"], e["lat"])
                for e in data.get("elements", [])
                if e["type"] == "node"
            }
            flowlines: List[Dict[str, Any]] = []
            waterbodies: List[Dict[str, Any]] = []

            from shapely.geometry import LineString, Polygon

            for element in data.get("elements", []):
                if element["type"] == "way" and "tags" in element:
                    coords = [nodes.get(n) for n in element.get("nodes", [])]
                    valid_coords = [c for c in coords if c is not None]

                    # Waterways are typically flowlines
                    if "waterway" in element["tags"]:
                        if len(valid_coords) >= 2:
                            flowlines.append(
                                {
                                    "geometry": LineString(valid_coords),
                                    "gnis_name": element["tags"].get(
                                        "name", "Unknown"
                                    ),
                                    "ftype": element["tags"].get("waterway"),
                                    "stream_order": 1,
                                }
                            )

                    # Natural=water are typically waterbodies
                    elif element["tags"].get("natural") == "water":
                        if len(valid_coords) >= 4:
                            try:
                                poly = Polygon(valid_coords)
                                if poly.is_valid:
                                    waterbodies.append(
                                        {
                                            "geometry": poly,
                                            "gnis_name": element["tags"].get(
                                                "name", "Unknown"
                                            ),
                                            "areasqkm": poly.area
                                            * 111
                                            * 111,  # rough estimate
                                        }
                                    )
                            except Exception as exc:
                                logger.warning('OSM water feature construction failed; skipping feature: %s', exc)

            flowlines_gdf = (
                gpd.GeoDataFrame(flowlines, crs="EPSG:4326")
                if flowlines
                else gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
            )
            waterbodies_gdf = (
                gpd.GeoDataFrame(waterbodies, crs="EPSG:4326")
                if waterbodies
                else gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
            )

            logger.info(
                f"Fetched {len(flowlines_gdf)} flowlines and {len(waterbodies_gdf)} waterbodies from OSM."
            )
            return {"flowlines": flowlines_gdf, "waterbodies": waterbodies_gdf}

        except Exception as e:
            logger.error(f"OSM Overpass query failed: {e}")
            return {
                "flowlines": gpd.GeoDataFrame(geometry=[], crs="EPSG:4326"),
                "waterbodies": gpd.GeoDataFrame(geometry=[], crs="EPSG:4326"),
            }

    def fetch_surface_water_features(
        self, bbox: Tuple[float, float, float, float]
    ) -> Dict[str, gpd.GeoDataFrame]:
        """Fetches all relevant surface water features (flowlines and waterbodies)

        from the NHD/NHDPlus HR for a given bounding box, falling back to local
        PNW high-order flowlines and OSM if NHD fails or is unavailable.
        """
        logger.info("Fetching all surface water features from NHD...")
        flowlines_gdf = self._query_nhd_layer(self.flowlines_url, "flowlines", bbox)
        waterbodies_gdf = self._query_nhd_layer(
            self.waterbodies_url, "waterbodies", bbox
        )

        # Fallback 1: If NHD flowlines is empty, check if bbox intersects local PNW high-order flowlines
        if flowlines_gdf.empty and self._local_flowlines_path.exists():
            local_flowlines = self.load_pnw_high_order_flowlines(min_stream_order=4)
            if not local_flowlines.empty:
                bbox_geom = box(*bbox)
                matched = local_flowlines[local_flowlines.intersects(bbox_geom)].copy()
                if not matched.empty:
                    logger.info(
                        f"Using {len(matched)} local NHDPlus HR high-order PNW flowlines for bbox {bbox}."
                    )
                    flowlines_gdf = matched

        # Fallback 2: Basic validation: If both return nothing, try OSM
        if (
            flowlines_gdf.empty
            and waterbodies_gdf.empty
            and not os.environ.get("GEO_INFER_SURFACE_WATER_OFFLINE")
        ):
            logger.info("NHD returned no data. Falling back to OSM.")
            return self._query_osm_overpass_water(bbox)

        return {"flowlines": flowlines_gdf, "waterbodies": waterbodies_gdf}
