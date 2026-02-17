"""
Tests for FormatDetector in geo_infer_data.utils.format_detection.
"""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from geo_infer_data.models.schemas import DataFormat
from geo_infer_data.utils.format_detection import FormatDetector


class TestFormatDetector:
    def test_detect_dataframe_format(self):
        detector = FormatDetector()
        df = pd.DataFrame({"a": [1, 2, 3]})
        fmt = detector.detect_format(df)
        assert fmt == DataFormat.CSV

    def test_detect_numpy_array_format(self):
        detector = FormatDetector()
        arr = np.random.rand(10, 10)
        fmt = detector.detect_format(arr)
        assert fmt == DataFormat.GEOTIFF

    def test_detect_geojson_dict(self):
        detector = FormatDetector()
        geojson = {
            "type": "FeatureCollection",
            "features": [],
        }
        fmt = detector.detect_format(geojson)
        assert fmt == DataFormat.GEOJSON

    def test_detect_non_geojson_dict(self):
        detector = FormatDetector()
        plain_dict = {"key": "value", "numbers": [1, 2]}
        fmt = detector.detect_format(plain_dict)
        assert fmt == DataFormat.CSV  # fallback

    def test_detect_geojson_feature(self):
        detector = FormatDetector()
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": {},
        }
        fmt = detector.detect_format(feature)
        assert fmt == DataFormat.GEOJSON

    def test_detect_geometry_dict(self):
        detector = FormatDetector()
        point = {"type": "Point", "coordinates": [0, 0]}
        fmt = detector.detect_format(point)
        assert fmt == DataFormat.GEOJSON

    def test_is_geojson_structure_false(self):
        detector = FormatDetector()
        assert detector._is_geojson_structure({"not": "geojson"}) is False
        assert detector._is_geojson_structure("string") is False

    def test_get_supported_formats(self):
        detector = FormatDetector()
        formats = detector.get_supported_formats()
        assert len(formats) > 0
        assert DataFormat.GEOJSON in formats
        assert DataFormat.CSV in formats

    def test_detect_from_path_csv(self):
        detector = FormatDetector()
        with tempfile.NamedTemporaryFile(
            suffix=".csv", mode="w", delete=False
        ) as f:
            f.write("a,b,c\n1,2,3\n4,5,6\n")
            f.flush()
            fmt = detector.detect_from_path(f.name)
            assert fmt == DataFormat.CSV

    def test_detect_from_path_geojson(self):
        detector = FormatDetector()
        geojson_content = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"name": "test"},
                }
            ],
        }
        with tempfile.NamedTemporaryFile(
            suffix=".geojson", mode="w", delete=False
        ) as f:
            json.dump(geojson_content, f)
            f.flush()
            fmt = detector.detect_from_path(f.name)
            assert fmt == DataFormat.GEOJSON

    def test_detect_from_path_nonexistent_raises(self):
        detector = FormatDetector()
        with pytest.raises(ValueError, match="File not found"):
            detector.detect_from_path("/nonexistent/path/data.csv")

    def test_detect_from_content_csv(self):
        detector = FormatDetector()
        with tempfile.NamedTemporaryFile(
            suffix=".txt", mode="w", delete=False
        ) as f:
            f.write("col1,col2\n1,2\n3,4\n")
            f.flush()
            fmt = detector.detect_from_content(f.name)
            # Should detect as CSV based on content
            assert fmt in (DataFormat.CSV, DataFormat.GEOJSON)
