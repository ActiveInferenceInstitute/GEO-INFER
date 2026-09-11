"""Unit tests for bioregion visualization integration layers."""

import logging

import folium
import h3
import pytest

from geo_infer_place.core.bioregion_visualization import _add_integration_layers


def _cell_id() -> str:
    return h3.latlng_to_cell(41.75, -124.2, 8)


class TestForestHealthLayer:
    def test_malformed_hexagon_is_skipped_with_warning(self, caplog):
        """GS-192: a malformed forest hexagon record must produce a warning
        naming the cell and be reported as skipped in the layer summary."""
        m = folium.Map(location=[41.75, -124.2], zoom_start=6)
        cell_a = h3.latlng_to_cell(41.75, -124.2, 8)
        cell_b = h3.latlng_to_cell(42.75, -125.2, 8)
        integration_results = {
            "forest_health": {
                "available": True,
                "results": {
                    cell_a: 0.5,
                    cell_b: {"malformed": object()},  # float() -> TypeError
                },
            }
        }
        with caplog.at_level(
            logging.INFO, logger="geo_infer_place.core.bioregion_visualization"
        ):
            _add_integration_layers(m, {}, integration_results)
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1
        assert "Skipping malformed forest health hexagon" in warnings[0].getMessage()
        summaries = [
            r.getMessage()
            for r in caplog.records
            if "forest health layer" in r.getMessage()
        ]
        assert any("(1 skipped)" in msg for msg in summaries)

    def test_bad_cell_id_is_skipped_with_warning(self, caplog):
        """An invalid H3 cell id is reported as skipped, not silently dropped."""
        m = folium.Map(location=[41.75, -124.2], zoom_start=6)
        integration_results = {
            "forest_health": {
                "available": True,
                "results": {"not-a-real-cell": 0.5},
            }
        }
        with caplog.at_level(
            logging.WARNING, logger="geo_infer_place.core.bioregion_visualization"
        ):
            _add_integration_layers(m, {}, integration_results)
        assert any(
            "Skipping malformed forest health hexagon" in r.getMessage()
            for r in caplog.records
            if r.levelno == logging.WARNING
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
