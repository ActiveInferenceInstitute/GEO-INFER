"""
Tests for disease surveillance module.

Uses real Pydantic models and geospatial utilities instead of mocks.
"""

import pytest
from datetime import datetime, timedelta

from geo_infer_health.models import DiseaseReport, Location, PopulationData
from geo_infer_health.utils.geospatial_utils import haversine_distance, create_bounding_box
from geo_infer_health.core.disease_surveillance import DiseaseHotspotAnalyzer


def _make_report(lat: float, lon: float, case_count: int, report_date: datetime, idx: int = 0) -> DiseaseReport:
    """Create a real DiseaseReport using the Pydantic model."""
    return DiseaseReport(
        report_id=f"RPT-{idx:04d}",
        disease_code="A00",
        location=Location(latitude=lat, longitude=lon),
        report_date=report_date,
        case_count=case_count,
    )


class TestDiseaseHotspotAnalyzer:
    """Test suite for DiseaseHotspotAnalyzer."""

    @pytest.fixture
    def sample_reports(self):
        """Create sample disease reports."""
        base_date = datetime(2024, 1, 1)
        return [
            _make_report(34.0, -118.0, 5, base_date, 0),
            _make_report(34.01, -118.01, 3, base_date + timedelta(days=1), 1),
            _make_report(34.02, -118.01, 2, base_date + timedelta(days=2), 2),
            _make_report(34.5, -118.5, 10, base_date + timedelta(days=3), 3),
            _make_report(34.51, -118.51, 8, base_date + timedelta(days=4), 4),
            _make_report(35.0, -119.0, 1, base_date + timedelta(days=5), 5),
        ]

    @pytest.fixture
    def analyzer(self, sample_reports):
        """Create analyzer with sample reports."""
        return DiseaseHotspotAnalyzer(sample_reports)

    def test_init(self, sample_reports):
        """Test initialization."""
        analyzer = DiseaseHotspotAnalyzer(sample_reports)
        assert len(analyzer.reports) == 6

    def test_get_cases_in_radius(self, analyzer):
        """Test getting cases within a radius."""
        center = Location(latitude=34.0, longitude=-118.0)
        cases = analyzer.get_cases_in_radius(center, 5.0)
        assert len(cases) >= 1

    def test_calculate_local_incidence_rate(self, analyzer):
        """Test incidence rate calculation."""
        center = Location(latitude=34.0, longitude=-118.0)
        rate, cases, pop, population_estimated = analyzer.calculate_local_incidence_rate(center, 10.0)
        assert cases >= 0

    def test_identify_simple_hotspots(self, analyzer):
        """Test hotspot identification."""
        hotspots = analyzer.identify_simple_hotspots(
            threshold_case_count=5,
            scan_radius_km=10.0
        )
        assert isinstance(hotspots, list)


class TestSIRModel:
    """Test suite for SIR model simulation."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer with minimal reports."""
        reports = [_make_report(34.0, -118.0, 10, datetime.now(), 0)]
        return DiseaseHotspotAnalyzer(reports)

    def test_simulate_sir_model(self, analyzer):
        """Test SIR model simulation."""
        result = analyzer.simulate_sir_model(
            initial_infected=10,
            population=10000,
            beta=0.3,
            gamma=0.1,
            days=100
        )

        assert "susceptible" in result
        assert "infected" in result
        assert "recovered" in result
        assert len(result["susceptible"]) == 100
        assert result["basic_reproduction_number"] == pytest.approx(3.0)

    def test_sir_model_peak(self, analyzer):
        """Test that SIR model produces a peak."""
        result = analyzer.simulate_sir_model(
            initial_infected=100,
            population=100000,
            beta=0.4,
            gamma=0.1,
            days=200
        )

        # Peak should be greater than initial
        assert result["peak_infected"] > 100
        assert result["peak_day"] > 0


class TestContactTracing:
    """Test suite for contact tracing functionality."""

    @pytest.fixture
    def reports_with_contacts(self):
        """Create reports with potential contacts."""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        return [
            _make_report(34.0, -118.0, 1, base_date, 0),
            _make_report(34.0001, -118.0001, 1, base_date + timedelta(hours=2), 1),
            _make_report(34.0002, -118.0001, 1, base_date + timedelta(hours=5), 2),
            _make_report(35.0, -119.0, 1, base_date + timedelta(hours=1), 3),  # Far away
        ]

    @pytest.fixture
    def analyzer(self, reports_with_contacts):
        """Create analyzer."""
        return DiseaseHotspotAnalyzer(reports_with_contacts)

    def test_find_potential_contacts(self, analyzer, reports_with_contacts):
        """Test finding potential contacts."""
        index_case = reports_with_contacts[0]

        contacts = analyzer.find_potential_contacts(
            case_report=index_case,
            search_radius_km=1.0,
            time_window_hours=24
        )

        assert isinstance(contacts, list)
        # Should find nearby cases but not the far one
        for contact in contacts:
            assert "distance_km" in contact
            assert "risk_score" in contact

    def test_contact_risk_calculation(self, analyzer):
        """Test contact risk score calculation."""
        risk = analyzer._calculate_contact_risk(
            distance_km=0.05,
            time_diff_hours=2.0,
            max_distance=1.0,
            max_time=48
        )

        assert 0 <= risk <= 100

        # Closer and more recent should be higher risk
        high_risk = analyzer._calculate_contact_risk(0.01, 1.0, 1.0, 48)
        low_risk = analyzer._calculate_contact_risk(0.5, 40.0, 1.0, 48)

        assert high_risk > low_risk


class TestTemporalAnalysis:
    """Test suite for temporal trend analysis."""

    @pytest.fixture
    def time_series_reports(self):
        """Create reports over time."""
        base_date = datetime(2024, 1, 1)
        reports = []

        # Increasing trend
        for i in range(30):
            case_count = 5 + i // 5  # Gradually increasing
            reports.append(_make_report(34.0, -118.0, case_count, base_date + timedelta(days=i), i))

        return reports

    @pytest.fixture
    def analyzer(self, time_series_reports):
        """Create analyzer."""
        return DiseaseHotspotAnalyzer(time_series_reports)

    def test_analyze_temporal_trends_daily(self, analyzer):
        """Test daily temporal trend analysis."""
        result = analyzer.analyze_temporal_trends(time_resolution="daily")

        assert "time_periods" in result
        assert "case_counts" in result
        assert "statistics" in result
        assert result["statistics"]["trend_direction"] in ["increasing", "decreasing", "stable"]

    def test_analyze_temporal_trends_weekly(self, analyzer):
        """Test weekly temporal trend analysis."""
        result = analyzer.analyze_temporal_trends(time_resolution="weekly")

        assert len(result["time_periods"]) <= 5  # ~4-5 weeks


class TestReproductionNumber:
    """Test suite for Rt estimation."""

    @pytest.fixture
    def epidemic_reports(self):
        """Create epidemic-like reports."""
        base_date = datetime(2024, 1, 1)
        reports = []

        # Exponential-like growth
        idx = 0
        for i in range(30):
            case_count = int(10 * 1.1 ** i)  # Exponential growth
            for _ in range(max(1, case_count // 10)):
                reports.append(_make_report(
                    34.0 + i * 0.01, -118.0,
                    min(case_count, 100),
                    base_date + timedelta(days=i),
                    idx
                ))
                idx += 1

        return reports

    @pytest.fixture
    def analyzer(self, epidemic_reports):
        """Create analyzer."""
        return DiseaseHotspotAnalyzer(epidemic_reports)

    def test_calculate_reproduction_number(self, analyzer):
        """Test Rt calculation."""
        result = analyzer.calculate_reproduction_number(
            serial_interval_days=5.0,
            window_days=7
        )

        assert "rt_time_series" in result
        assert "summary" in result

    def test_reproduction_number_summary(self, analyzer):
        """Test Rt summary statistics."""
        result = analyzer.calculate_reproduction_number()

        if result["summary"]["latest_rt"] is not None:
            assert isinstance(result["summary"]["latest_rt"], float)


class TestRiskMapping:
    """Test suite for risk map generation."""

    @pytest.fixture
    def clustered_reports(self):
        """Create clustered disease reports."""
        base_date = datetime(2024, 1, 1)
        reports = []

        # Cluster 1 - high risk
        for i in range(15):
            reports.append(_make_report(
                34.0 + i * 0.001,
                -118.0 + i * 0.001,
                2, base_date, i
            ))

        # Cluster 2 - medium risk
        for i in range(5):
            reports.append(_make_report(
                34.1 + i * 0.001,
                -118.1 + i * 0.001,
                1, base_date, 15 + i
            ))

        return reports

    @pytest.fixture
    def analyzer(self, clustered_reports):
        """Create analyzer."""
        return DiseaseHotspotAnalyzer(clustered_reports)

    def test_generate_risk_map_data(self, analyzer):
        """Test risk map generation."""
        result = analyzer.generate_risk_map_data(grid_resolution_km=5.0)

        assert "grid_resolution_km" in result
        assert "cells" in result
        assert "summary" in result

    def test_risk_map_with_bbox(self, analyzer):
        """Test risk map with custom bounding box."""
        bbox = {
            "min_lat": 33.9,
            "max_lat": 34.2,
            "min_lon": -118.2,
            "max_lon": -117.9
        }

        result = analyzer.generate_risk_map_data(
            grid_resolution_km=10.0,
            bbox=bbox
        )

        assert result["bounding_box"] == bbox
