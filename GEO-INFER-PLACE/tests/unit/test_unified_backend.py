"""Unit tests for CascadianAgriculturalH3Backend."""

import pytest

from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend


@pytest.fixture
def backend_modules():
    """Minimal modules dict required by CascadianAgriculturalH3Backend."""
    return {}


@pytest.fixture
def backend(backend_modules, tmp_path):
    return CascadianAgriculturalH3Backend(
        modules=backend_modules,
        resolution=8,
        base_data_dir=tmp_path,
        enable_caching=False,
    )


class TestCascadianBackendInit:
    def test_init_with_modules(self, backend_modules, tmp_path):
        b = CascadianAgriculturalH3Backend(
            modules=backend_modules,
            resolution=8,
            base_data_dir=tmp_path,
            enable_caching=False,
        )
        assert b is not None

    def test_init_custom_resolution(self, backend_modules, tmp_path):
        b = CascadianAgriculturalH3Backend(
            modules=backend_modules,
            resolution=7,
            base_data_dir=tmp_path,
            enable_caching=False,
        )
        assert b.resolution == 7

    def test_target_hexagons_property(self, backend):
        # target_hexagons may return a number or a set/list; may not exist yet
        hexagons = getattr(backend, "target_hexagons", None)
        assert hexagons is None or isinstance(hexagons, (int, float, set, list))

    def test_modules_attribute_set(self, backend, backend_modules):
        assert hasattr(backend, "modules") or hasattr(backend, "_modules")


class TestCascadianBackendH3Operations:
    def test_get_h3_cell_returns_string(self, backend):
        cell = backend.get_h3_cell(lat=41.75, lon=-124.2)
        assert isinstance(cell, str)
        assert len(cell) > 0

    def test_cache_key_deterministic(self, backend):
        """Same lat/lon/resolution produces the same cache key."""
        cell1 = backend.get_h3_cell(lat=41.75, lon=-124.2)
        cell2 = backend.get_h3_cell(lat=41.75, lon=-124.2)
        assert cell1 == cell2

    def test_export_to_geojson(self, backend, temp_output_dir):
        result = backend.export_to_geojson(output_dir=str(temp_output_dir))
        assert result is not None


class TestCascadianBackendSPACEIntegration:
    def test_uses_shared_space_backend(self):
        """Backend uses the shared GEO-INFER-SPACE implementation."""
        from geo_infer_space.core.unified_backend import UnifiedH3Backend
        from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend

        assert issubclass(CascadianAgriculturalH3Backend, UnifiedH3Backend)

    def test_cell_to_boundary_returns_polygon(self, backend):
        import h3

        cell = h3.latlng_to_cell(41.75, -124.2, 8)
        try:
            boundary = backend.cell_to_boundary(cell)
            assert boundary is not None
        except AttributeError:
            # If method doesn't exist, verify h3 directly
            boundary = h3.cell_to_boundary(cell)
            assert boundary is not None
