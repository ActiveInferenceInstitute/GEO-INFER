"""Tests for microbiome data processing."""

from geo_infer_bio.microbiome import MicrobiomeDataLoader


class TestMicrobiomeDataLoader:
    """Tests for microbiome data loading."""

    def test_initialization(self) -> None:
        loader = MicrobiomeDataLoader()
        assert loader is not None
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
