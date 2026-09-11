"""
Regression tests for GS-243: hotspot loader robustness in
geo_infer_health.cli.run_hotspot_analysis.

- Non-point (polygon) geometries must not crash: the geometry is
  reprojected to EPSG:4326 if needed and collapsed to its centroid.
- A missing (or empty) 'report_date' column must fail with a clear
  ValueError naming the module, not a raw pydantic traceback.
- Well-formed point inputs with report_date still load and run.
"""

import json
from datetime import datetime, timedelta

import pytest

from geo_infer_health.cli import run_hotspot_analysis


class _Args:
    """Minimal argparse.Namespace stand-in for run_hotspot_analysis."""

    def __init__(self, input: str, output: str) -> None:
        self.input = input
        self.population = None
        self.threshold = 2
        self.radius = 10
        self.output = output


def _write_geojson(path, feature_collection: dict) -> str:
    path.write_text(json.dumps(feature_collection))
    return str(path)


def _polygon_feature(report_date: str) -> dict:
    return {
        "type": "Feature",
        "properties": {
            "report_id": "p1",
            "disease_code": "A00",
            "report_date": report_date,
            "case_count": 2,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]],
        },
    }


class TestHotspotLoaderGeometry:
    def test_polygon_geometry_uses_centroid(self, tmp_path) -> None:
        date = (datetime(2024, 1, 1) + timedelta(days=1)).isoformat()
        fc = {"type": "FeatureCollection", "features": [_polygon_feature(date)]}
        input_path = _write_geojson(tmp_path / "reports.geojson", fc)
        output_path = str(tmp_path / "hotspots.json")

        run_hotspot_analysis(_Args(input_path, output_path), None)

        hotspots = json.loads((tmp_path / "hotspots.json").read_text())
        assert isinstance(hotspots, list)

    def test_multipolygon_geometry_uses_centroid(self, tmp_path) -> None:
        date = (datetime(2024, 1, 1) + timedelta(days=1)).isoformat()
        feature = _polygon_feature(date)
        feature["geometry"] = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]],
                [[[2.0, 2.0], [3.0, 2.0], [3.0, 3.0], [2.0, 2.0]]],
            ],
        }
        fc = {"type": "FeatureCollection", "features": [feature]}
        input_path = _write_geojson(tmp_path / "reports.geojson", fc)
        output_path = str(tmp_path / "hotspots.json")

        run_hotspot_analysis(_Args(input_path, output_path), None)
        assert json.loads((tmp_path / "hotspots.json").read_text()) is not None

    def test_projected_crs_polygon_reprojected_to_epsg4326(self, tmp_path) -> None:
        # EPSG:32633 (UTM 33N) coordinates near lon=12, lat=57: without the
        # reprojection the Location validator (lat in [-90, 90]) would reject.
        date = (datetime(2024, 1, 1) + timedelta(days=1)).isoformat()
        fc = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:EPSG::32633"},
            },
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "report_id": "utm",
                        "disease_code": "A00",
                        "report_date": date,
                        "case_count": 1,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [340000.0, 6300000.0],
                                [350000.0, 6300000.0],
                                [350000.0, 6310000.0],
                                [340000.0, 6300000.0],
                            ]
                        ],
                    },
                }
            ],
        }
        input_path = _write_geojson(tmp_path / "reports_utm.geojson", fc)
        output_path = str(tmp_path / "hotspots.json")

        run_hotspot_analysis(_Args(input_path, output_path), None)
        assert json.loads((tmp_path / "hotspots.json").read_text()) is not None


class TestHotspotLoaderMissingDate:
    def test_missing_report_date_column_raises_clear_error(self, tmp_path) -> None:
        fc = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"report_id": "p2", "disease_code": "A00"},
                    "geometry": {"type": "Point", "coordinates": [0.5, 0.5]},
                }
            ],
        }
        input_path = _write_geojson(tmp_path / "no_date.geojson", fc)
        output_path = str(tmp_path / "hotspots.json")

        with pytest.raises(ValueError, match="report_date"):
            run_hotspot_analysis(_Args(input_path, output_path), None)

    def test_null_report_date_value_raises_clear_error(self, tmp_path) -> None:
        fc = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "report_id": "p3",
                        "disease_code": "A00",
                        "report_date": None,
                    },
                    "geometry": {"type": "Point", "coordinates": [0.5, 0.5]},
                }
            ],
        }
        input_path = _write_geojson(tmp_path / "null_date.geojson", fc)
        output_path = str(tmp_path / "hotspots.json")

        with pytest.raises(ValueError, match="report_date"):
            run_hotspot_analysis(_Args(input_path, output_path), None)


class TestHotspotLoaderPointHappyPath:
    def test_point_with_date_runs(self, tmp_path) -> None:
        date = (datetime(2024, 1, 1) + timedelta(days=1)).isoformat()
        fc = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "report_id": f"r{i}",
                        "disease_code": "A00",
                        "report_date": date,
                        "case_count": 3,
                    },
                    "geometry": {"type": "Point", "coordinates": [0.5 + i * 0.01, 0.5]},
                }
                for i in range(4)
            ],
        }
        input_path = _write_geojson(tmp_path / "points.geojson", fc)
        output_path = str(tmp_path / "hotspots.json")

        run_hotspot_analysis(_Args(input_path, output_path), None)
        hotspots = json.loads((tmp_path / "hotspots.json").read_text())
        assert isinstance(hotspots, list)
