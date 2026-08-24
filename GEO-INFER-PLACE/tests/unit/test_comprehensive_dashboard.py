"""Unit tests for DelNorteComprehensiveDashboard.

Source: src/geo_infer_place/core/comprehensive_dashboard.py

These tests exercise the implemented dashboard contract.
"""

import folium

try:
    from geo_infer_place.core.comprehensive_dashboard import (
        DelNorteComprehensiveDashboard,
    )

    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False


class TestDelNorteComprehensiveDashboard:
    def test_init(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        assert dashboard is not None

    def test_run_analysis_returns_dict(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert isinstance(result, dict)

    def test_run_analysis_has_forest_health_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "forest_health" in result

    def test_run_analysis_has_coastal_resilience_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "coastal_resilience" in result

    def test_run_analysis_has_fire_risk_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "fire_risk" in result

    def test_run_analysis_has_seismic_hazard_section(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "seismic_hazard" in result

    def test_cross_domain_integrated_risk_present(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        result = dashboard.run_analysis()
        assert "integrated_risk" in result or any(
            "integrated" in str(k).lower() for k in result
        )

    def test_map_html_file_created(self, temp_output_dir):
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        dashboard.run_analysis()
        html_files = list(temp_output_dir.glob("*.html"))
        assert len(html_files) >= 1

    def test_civic_panels_follow_overlay_visibility(self, temp_output_dir):
        """The off-by-default civic panels follow their Leaflet overlay."""
        dashboard = DelNorteComprehensiveDashboard(output_dir=str(temp_output_dir))
        dashboard.analysis_results = {
            "crescent_city_intel": {
                "status": "ok",
                "municipality": "Crescent City",
                "anchor": {"latitude": 41.76, "longitude": -124.20},
                "h3_cells": {},
                "hazard": {
                    "domains": [
                        {
                            "id": "emergency-management",
                            "name": "Emergency Management",
                            "icon": "warning",
                            "hazardTags": ["tsunami", "seismic"],
                            "topics": [
                                {
                                    "name": "Tsunami readiness",
                                    "sections": ["2.30.010"],
                                }
                            ],
                            "coverage": 0.75,
                        }
                    ]
                },
            }
        }
        dashboard_map = folium.Map(location=[41.76, -124.20], zoom_start=10)
        layer_groups = dashboard._create_advanced_layer_groups()
        dashboard._add_crescent_city_intel_layer(dashboard_map, layer_groups)
        layer_groups["crescent_city_intel"].add_to(dashboard_map)

        html = dashboard_map.get_root().render()
        civic_layer_name = layer_groups["crescent_city_intel"].get_name()

        assert 'id="civic-intel-legend" style="display: none;' in html
        assert 'id="civic-intel-summary" style="display: none;' in html
        assert f"var civicLayer = {civic_layer_name};" in html
        assert "civicMap.hasLayer(civicLayer)" in html
        assert 'civicMap.on("overlayadd"' in html
        assert 'civicMap.on("overlayremove"' in html
