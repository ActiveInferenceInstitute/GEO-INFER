"""Tests for accessibility analysis module."""

import pytest
import math
from geo_infer_transport.core.accessibility import (
    AccessibilityAnalyzer,
    Isochrone,
    ServiceArea,
)


class TestAccessibilityDataclasses:
    """Tests for accessibility dataclass creation."""

    def test_isochrone_creation(self) -> None:
        iso = Isochrone(
            center={"lat": 34.0, "lon": -118.0},
            time_minutes=15.0,
            mode="car",
            geometry={"type": "Polygon", "coordinates": []},
            area_sq_km=50.0,
        )
        assert iso.time_minutes == 15.0
        assert iso.mode == "car"

    def test_service_area_creation(self) -> None:
        sa = ServiceArea(
            facility_id="f1",
            location={"lat": 34.0, "lon": -118.0},
            break_values=[5, 10, 15],
            polygons=[],
        )
        assert sa.facility_id == "f1"
        assert sa.population_covered == 0


class TestAccessibilityAnalyzerInit:
    """Tests for AccessibilityAnalyzer initialization."""

    def test_default_initialization(self) -> None:
        analyzer = AccessibilityAnalyzer()
        assert analyzer is not None
        assert analyzer.default_mode == "car"
        assert analyzer.network is None

    def test_custom_initialization(self) -> None:
        analyzer = AccessibilityAnalyzer(
            default_mode="bicycle",
            population_data={"average_density": 2000},
        )
        assert analyzer.default_mode == "bicycle"


class TestIsochrone:
    """Tests for isochrone calculation."""

    def test_calculate_isochrone_no_network(self) -> None:
        analyzer = AccessibilityAnalyzer()
        isochrones = analyzer.calculate_isochrone(
            origin={"id": "o1", "location": {"lat": 34.0, "lon": -118.0}},
            travel_times=[10, 20, 30],
            mode="car",
        )
        assert len(isochrones) == 3
        assert isochrones[0].time_minutes == 10
        assert isochrones[1].time_minutes == 20
        assert isochrones[2].time_minutes == 30
        # Larger times produce larger areas
        assert isochrones[0].area_sq_km < isochrones[2].area_sq_km

    def test_isochrone_mode_affects_area(self) -> None:
        analyzer = AccessibilityAnalyzer()
        car_isos = analyzer.calculate_isochrone(
            origin={"id": "o1", "location": {"lat": 34.0, "lon": -118.0}},
            travel_times=[15],
            mode="car",
        )
        bike_isos = analyzer.calculate_isochrone(
            origin={"id": "o1", "location": {"lat": 34.0, "lon": -118.0}},
            travel_times=[15],
            mode="bicycle",
        )
        assert car_isos[0].area_sq_km > bike_isos[0].area_sq_km

    def test_isochrone_geometry_is_polygon(self) -> None:
        analyzer = AccessibilityAnalyzer()
        isochrones = analyzer.calculate_isochrone(
            origin={"id": "o1", "location": {"lat": 34.0, "lon": -118.0}},
            travel_times=[10],
        )
        assert isochrones[0].geometry["type"] == "Polygon"
        coords = isochrones[0].geometry["coordinates"][0]
        assert len(coords) > 10  # At least several vertices
        assert coords[0] == coords[-1]  # Closed polygon


class TestServiceArea:
    """Tests for service area generation."""

    def test_generate_service_area(self) -> None:
        analyzer = AccessibilityAnalyzer()
        areas = analyzer.generate_service_area(
            facilities=[
                {"id": "f1", "location": {"lat": 34.0, "lon": -118.0}},
                {"id": "f2", "location": {"lat": 34.1, "lon": -118.1}},
            ],
            breaks=[5, 10],
        )
        assert len(areas) == 2
        assert areas[0].facility_id == "f1"
        assert len(areas[0].polygons) == 2
        assert areas[0].population_covered > 0

    def test_service_area_population_estimate(self) -> None:
        analyzer = AccessibilityAnalyzer(
            population_data={"average_density": 5000},
        )
        areas = analyzer.generate_service_area(
            facilities=[{"id": "f1", "location": {"lat": 34.0, "lon": -118.0}}],
            breaks=[1],
        )
        expected_area = math.pi * 1**2
        expected_pop = int(5000 * expected_area)
        assert areas[0].population_covered == expected_pop


class TestEquityAnalysis:
    """Tests for accessibility equity analysis."""

    def test_analyze_equity(self) -> None:
        analyzer = AccessibilityAnalyzer()
        result = analyzer.analyze_equity(
            population_groups={
                "group_a": {"population": 1000, "areas": ["a1", "a2"]},
                "group_b": {"population": 2000, "areas": ["a3", "a4"]},
            },
            accessibility_scores={"a1": 0.8, "a2": 0.9, "a3": 0.3, "a4": 0.4},
        )
        assert "group_analysis" in result
        assert "equity_metrics" in result
        assert "gini_coefficient" in result["equity_metrics"]
        # Group B has lower scores, should show disparity
        assert len(result["disparities"]) > 0

    def test_equity_no_disparity(self) -> None:
        analyzer = AccessibilityAnalyzer()
        result = analyzer.analyze_equity(
            population_groups={
                "group_a": {"population": 1000, "areas": ["a1"]},
                "group_b": {"population": 1000, "areas": ["a2"]},
            },
            accessibility_scores={"a1": 0.8, "a2": 0.8},
        )
        assert len(result["disparities"]) == 0


class TestAccessibilityIndex:
    """Tests for gravity-based accessibility index."""

    def test_calculate_accessibility_index(self) -> None:
        analyzer = AccessibilityAnalyzer()
        result = analyzer.calculate_accessibility_index(
            origin={"id": "o1", "location": {"lat": 34.0, "lon": -118.0}},
            destinations=[
                {"id": "d1", "location": {"lat": 34.01, "lon": -118.01}, "weight": 10.0},
                {"id": "d2", "location": {"lat": 34.05, "lon": -118.05}, "weight": 5.0},
            ],
            decay_function="exponential",
            beta=0.1,
        )
        assert result["accessibility_index"] > 0
        assert len(result["components"]) == 2
        # Closer destination contributes more
        assert result["components"][0]["contribution"] >= result["components"][1]["contribution"]

    def test_power_decay_function(self) -> None:
        analyzer = AccessibilityAnalyzer()
        result = analyzer.calculate_accessibility_index(
            origin={"id": "o1", "location": {"lat": 34.0, "lon": -118.0}},
            destinations=[
                {"id": "d1", "location": {"lat": 34.01, "lon": -118.01}, "weight": 1.0},
            ],
            decay_function="power",
            beta=1.0,
        )
        assert result["accessibility_index"] > 0
        assert result["decay_function"] == "power"
