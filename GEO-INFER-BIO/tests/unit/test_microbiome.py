"""Tests for microbiome data processing."""

import pytest
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

    def test_load_emp_data(self) -> None:
        loader = MicrobiomeDataLoader()
        dataset = loader.load_emp_data(max_samples=10)
        assert dataset is not None
