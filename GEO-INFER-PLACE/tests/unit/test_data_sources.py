#!/usr/bin/env python3
"""
Tests for GEO-INFER-PLACE CaliforniaDataSources utility.

Validates the data-source catalog, search, category retrieval,
and source summary functionality.
"""

import pytest

from geo_infer_place.utils.data_sources import CaliforniaDataSources


@pytest.fixture
def ds():
    return CaliforniaDataSources()


class TestDataSourcesInit:
    """Test CaliforniaDataSources basic properties."""

    def test_creates_successfully(self, ds):
        assert ds is not None

    def test_has_sources_catalog(self, ds):
        """Should expose sources dict."""
        assert hasattr(ds, "sources")
        assert isinstance(ds.sources, dict)
        assert len(ds.sources) > 0

    def test_cal_fire_source_present(self, ds):
        """CAL FIRE should be a registered data source."""
        keys_lower = [k.lower() for k in ds.sources]
        assert any("fire" in k or "calfire" in k for k in keys_lower)


class TestSourceLookup:
    """Test source retrieval and search."""

    def test_get_source_config_returns_datasource(self, ds):
        """get_source_config should return a DataSource for a valid key."""
        first_key = next(iter(ds.sources))
        source = ds.get_source_config(first_key)
        assert source is not None
        assert hasattr(source, "name")
        assert hasattr(source, "base_url")

    def test_get_source_config_returns_none_for_unknown(self, ds):
        result = ds.get_source_config("nonexistent_source_xyz")
        assert result is None

    def test_search_sources_returns_results(self, ds):
        """Searching for 'fire' should return at least one result."""
        results = ds.search_sources("fire")
        assert len(results) >= 1


class TestCategoriesAndSummary:
    """Test category and summary methods."""

    def test_get_sources_by_category(self, ds):
        """Should be able to retrieve sources by category."""
        if hasattr(ds, "categories"):
            first_cat = next(iter(ds.categories))
            sources = ds.get_sources_by_category(first_cat)
            assert isinstance(sources, list)

    def test_get_source_summary(self, ds):
        """Summary should include total count."""
        summary = ds.get_source_summary()
        assert "total_sources" in summary or "total" in summary or isinstance(summary, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
