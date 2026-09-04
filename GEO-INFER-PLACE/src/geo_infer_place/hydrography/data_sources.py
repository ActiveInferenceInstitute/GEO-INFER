"""Explicit local or bounded USGS hydrography access without synthetic fallbacks."""

from __future__ import annotations

import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import tempfile

import geopandas as gpd
from shapely.geometry import box

from .flowline_network import CascadiaFlowlineNetwork, normalize_flowlines
from .ingestion import (
    HydrographySelection,
    IncompleteHydrographyError,
    NHDPlusHRIngestor,
)


def load_flowlines(path: str | Path) -> gpd.GeoDataFrame:
    """Load an explicit dataset and verify its adjacent ingestion manifest if present."""
    path = Path(path)
    payload = path.read_bytes()
    manifest_path = path.parent / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_bytes())
        if manifest.get("status") not in {"complete", "empty"}:
            raise IncompleteHydrographyError("Dataset manifest is not complete")
        if manifest.get("dataset") != path.name or hashlib.sha256(
            payload
        ).hexdigest() != manifest.get("sha256"):
            raise IncompleteHydrographyError("Dataset does not match its manifest")
    data = json.loads(payload)
    crs = data.get("crs", {}).get("properties", {}).get("name", "EPSG:4326")
    if crs not in {
        "EPSG:4326",
        "urn:ogc:def:crs:EPSG::4326",
        "urn:ogc:def:crs:OGC:1.3:CRS84",
    }:
        raise ValueError(
            "Flowline GeoJSON requires WGS84; reproject the source explicitly"
        )
    if data.get("type") != "FeatureCollection" or not isinstance(
        data.get("features"), list
    ):
        raise ValueError("Expected a GeoJSON FeatureCollection")
    frame = (
        gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
        if data["features"]
        else gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
    )
    return normalize_flowlines(frame)


def sample_flowlines() -> gpd.GeoDataFrame:
    """Load the verified 34-reach lower Smith River excerpt, not a regional catalog."""
    root = files(__package__).joinpath("data")
    payload = root.joinpath("smith_river_flowlines.geojson").read_bytes()
    manifest = json.loads(root.joinpath("smith_river_manifest.json").read_bytes())
    if hashlib.sha256(payload).hexdigest() != manifest["sha256"]:
        raise IncompleteHydrographyError(
            "Packaged Smith River excerpt checksum mismatch"
        )
    data = json.loads(payload)
    frame = normalize_flowlines(
        gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
    )
    frame.attrs["provenance"] = manifest
    return frame


class CascadianSurfaceWaterDataSources:
    """Access supplied flowlines or acquire an explicitly selected USGS region.

    Graph methods require dataset_path or flowlines; no bundled excerpt is used
    implicitly. Network fetches use persisted ingestion when cache_dir is given.
    Waterbodies are outside this network-flowline service and are marked unqueried.
    """

    def __init__(
        self,
        dataset_path: str | Path | None = None,
        *,
        flowlines: gpd.GeoDataFrame | None = None,
        cache_dir: str | Path | None = None,
        ingestor: NHDPlusHRIngestor | None = None,
        offline: bool | None = None,
    ) -> None:
        if dataset_path is not None and flowlines is not None:
            raise ValueError("Supply dataset_path or flowlines, not both")
        if dataset_path is None and flowlines is None:
            dataset_path = os.environ.get("GEO_INFER_CASCADIA_FLOWLINES_PATH") or None
        self.dataset_path = Path(dataset_path) if dataset_path is not None else None
        self.offline = (
            bool(os.environ.get("GEO_INFER_SURFACE_WATER_OFFLINE"))
            if offline is None
            else offline
        )
        self._flowlines = (
            normalize_flowlines(flowlines) if flowlines is not None else None
        )
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        self.ingestor = ingestor or NHDPlusHRIngestor()

    def _load(self) -> gpd.GeoDataFrame:
        if self._flowlines is not None:
            return self._flowlines.copy()
        if self.dataset_path is None:
            raise FileNotFoundError(
                "Supply an ingested dataset_path or explicit flowlines for network analysis"
            )
        return load_flowlines(self.dataset_path)

    def load_pnw_high_order_flowlines(
        self, min_stream_order: int = 4
    ) -> gpd.GeoDataFrame:
        """Return a high-order view after validating the complete supplied network."""
        network = self.get_flowline_network(min_stream_order)
        selected = network.get_pnw_high_order_flowlines(min_stream_order)
        selected.attrs["full_network_validation"] = network.full_network_validation
        return selected

    def get_flowline_network(
        self, min_stream_order: int = 4
    ) -> CascadiaFlowlineNetwork:
        """Retain all reaches for traversal; threshold controls selected_comids only."""
        if type(min_stream_order) is not int or min_stream_order < 0:
            raise ValueError("min_stream_order must be a nonnegative integer")
        network = CascadiaFlowlineNetwork(self._load())
        network.full_network_validation = network.validate()
        network.selected_comids = set(
            network.get_pnw_high_order_flowlines(min_stream_order).get("comid", [])
        )
        return network

    def fetch_surface_water_features(
        self, bbox: tuple[float, float, float, float]
    ) -> dict[str, gpd.GeoDataFrame]:
        """Fetch whole intersecting flowlines; failures propagate instead of becoming empty data."""
        selection = HydrographySelection(bbox=bbox)
        if self._flowlines is not None or self.dataset_path is not None:
            frame = self._load()
        elif self.offline:
            if self.cache_dir is None:
                raise FileNotFoundError(
                    "Offline surface-water access requires local flowlines or a completed cache"
                )
            key = hashlib.sha256(
                json.dumps(selection.query(), sort_keys=True).encode()
            ).hexdigest()[:20]
            cached = self.cache_dir / key
            if not (cached / "manifest.json").is_file():
                raise FileNotFoundError(
                    "Offline cache requires a completed ingestion manifest"
                )
            frame = load_flowlines(cached / "flowlines.geojson")
        elif self.cache_dir is not None:
            key = hashlib.sha256(
                json.dumps(selection.query(), sort_keys=True).encode()
            ).hexdigest()[:20]
            frame = load_flowlines(
                self.ingestor.ingest(selection, self.cache_dir / key)
            )
        else:
            with tempfile.TemporaryDirectory(prefix="geo-infer-nhd-") as directory:
                frame = load_flowlines(self.ingestor.ingest(selection, directory))
        frame = frame[frame.intersects(box(*bbox))].copy()
        waterbodies = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        waterbodies.attrs["status"] = "not_queried"
        return {"flowlines": frame, "waterbodies": waterbodies}
