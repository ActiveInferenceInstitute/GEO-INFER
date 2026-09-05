"""Tests for microbiome data processing."""

import pandas as pd
import pytest
from geo_infer_bio.microbiome import MicrobiomeDataLoader, MicrobiomeDataset


def _metadata() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "latitude": [37.7, 38.0, 41.0],
            "longitude": [-122.4, -122.0, -124.0],
            "ph": [7.1, 6.5, 8.0],
            "shannon_diversity": [2.1, 1.8, 3.0],
        },
        index=["sample-1", "sample-2", "sample-3"],
    )


class TestMicrobiomeDataLoader:
    """Tests for microbiome data loading."""

    def test_initialization(self) -> None:
        loader = MicrobiomeDataLoader()
        assert loader.cache_dir.exists()

    def test_emp_config(self) -> None:
        loader = MicrobiomeDataLoader()
        assert "base_url" in loader.emp_config

    def test_load_emp_data_from_file(self, tmp_path) -> None:
        loader = MicrobiomeDataLoader()
        metadata_path = tmp_path / "emp.tsv"
        metadata_path.write_text(
            "sample_id\tlatitude\tlongitude\tph\n" "sample-1\t37.7\t-122.4\t7.1\n",
            encoding="utf-8",
        )
        dataset = loader.load_emp_data(metadata_path=str(metadata_path))
        assert len(dataset) == 1

    def test_load_emp_data_missing_file_raises(self) -> None:
        loader = MicrobiomeDataLoader()
        with pytest.raises(FileNotFoundError, match="EMP metadata file not found"):
            loader.load_emp_data(metadata_path="/nonexistent/emp.tsv")

    def test_load_emp_data_requires_coordinate_columns(self, tmp_path) -> None:
        loader = MicrobiomeDataLoader()
        metadata_path = tmp_path / "emp.tsv"
        metadata_path.write_text("sample_id\tph\nsample-1\t7.1\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing required columns"):
            loader.load_emp_data(metadata_path=str(metadata_path))

    def test_load_emp_data_bbox_filtering(self, tmp_path) -> None:
        loader = MicrobiomeDataLoader()
        metadata_path = tmp_path / "emp.tsv"
        metadata_path.write_text(
            "sample_id\tlatitude\tlongitude\tph\n"
            "s1\t37.7\t-122.4\t7.1\n"
            "s2\t48.0\t2.3\t7.0\n",
            encoding="utf-8",
        )
        dataset = loader.load_emp_data(
            metadata_path=str(metadata_path),
            region_bbox=(-125.0, 35.0, -120.0, 40.0),
        )
        assert list(dataset.metadata.index) == ["s1"]

    def test_load_emp_data_max_samples_validates(self, tmp_path) -> None:
        loader = MicrobiomeDataLoader()
        metadata_path = tmp_path / "emp.tsv"
        metadata_path.write_text(
            "sample_id\tlatitude\tlongitude\tph\n" "s1\t37.7\t-122.4\t7.1\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="max_samples"):
            loader.load_emp_data(metadata_path=str(metadata_path), max_samples=0)

    def test_quality_filters_drop_invalid_rows(self, tmp_path) -> None:
        loader = MicrobiomeDataLoader()
        metadata_path = tmp_path / "emp.tsv"
        metadata_path.write_text(
            "sample_id\tlatitude\tlongitude\tph\n"
            "good\t37.7\t-122.4\t7.1\n"
            "nocoord\t\t-122.4\t7.1\n"
            "badlat\t99.0\t-122.4\t7.1\n"
            "badph\t38.0\t-122.0\t99.0\n",
            encoding="utf-8",
        )
        dataset = loader.load_emp_data(metadata_path=str(metadata_path))
        assert list(dataset.metadata.index) == ["good"]


class TestMicrobiomeDataset:
    """Behavior tests for the microbiome dataset container."""

    def test_missing_coordinate_columns_raise(self) -> None:
        with pytest.raises(ValueError, match="Missing required coordinate columns"):
            MicrobiomeDataset(metadata=pd.DataFrame({"ph": [7.0]}))

    def test_get_coordinates(self) -> None:
        dataset = MicrobiomeDataset(metadata=_metadata())
        assert dataset.get_coordinates() == [(37.7, -122.4), (38.0, -122.0), (41.0, -124.0)]

    def test_len(self) -> None:
        dataset = MicrobiomeDataset(metadata=_metadata())
        assert len(dataset) == 3

    def test_filter_by_coordinates(self) -> None:
        dataset = MicrobiomeDataset(metadata=_metadata())
        filtered = dataset.filter_by_coordinates((-123.0, 36.0, -121.0, 39.0))
        assert len(filtered) == 2
        assert "spatially filtered" in filtered.data_source

    def test_get_coordinates_gdf(self) -> None:
        dataset = MicrobiomeDataset(metadata=_metadata())
        gdf = dataset.get_coordinates_gdf()
        assert gdf.crs.to_epsg() == 4326
        assert len(gdf) == 3

    def test_get_diversity_metrics(self) -> None:
        dataset = MicrobiomeDataset(metadata=_metadata())
        metrics = dataset.get_diversity_metrics()
        assert list(metrics.columns) == ["shannon_diversity"]
        assert len(metrics) == 3

    def test_get_diversity_metrics_empty_without_columns(self) -> None:
        metadata = _metadata().drop(columns=["shannon_diversity"])
        dataset = MicrobiomeDataset(metadata=metadata)
        assert dataset.get_diversity_metrics().empty

    def test_export_for_h3_integration(self) -> None:
        dataset = MicrobiomeDataset(metadata=_metadata())
        export = dataset.export_for_h3_integration()
        assert export["sample_ids"] == ["sample-1", "sample-2", "sample-3"]
        assert len(export["coordinates"]) == 3
        assert "shannon_diversity" in export["diversity_metrics"]["sample-1"]
