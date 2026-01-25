"""
Unit tests for TrafficAnalyzer, AccessibilityAnalyzer, and TransitOptimizer.
"""

import pytest
from datetime import datetime
from geo_infer_transport.core.traffic import (
    TrafficAnalyzer,
    TrafficCondition,
    FlowResult
)
from geo_infer_transport.core.accessibility import (
    AccessibilityAnalyzer,
    Isochrone,
    ServiceArea
)
from geo_infer_transport.core.transit import (
    TransitOptimizer,
    TransitMode
)


class TestTrafficAnalyzer:
    """Test suite for TrafficAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a TrafficAnalyzer instance."""
        return TrafficAnalyzer(
            data_sources=["sensor"],
            model_type="bpr",
            time_resolution="15min"
        )
    
    def test_init_default(self):
        """Test default initialization."""
        analyzer = TrafficAnalyzer()
        assert analyzer.model_type == "bpr"
    
    def test_analyze_flow(self, analyzer):
        """Test flow analysis."""
        segment = {"id": "seg_1", "capacity": 2000, "speed_limit": 50}
        counts = [
            {"count": 400, "speed_kmh": 45},
            {"count": 450, "speed_kmh": 42},
            {"count": 380, "speed_kmh": 48}
        ]
        
        result = analyzer.analyze_flow(segment, counts)
        
        assert isinstance(result, FlowResult)
        assert result.level_of_service in ["A", "B", "C", "D", "E", "F"]
    
    def test_model_congestion(self, analyzer):
        """Test congestion modeling."""
        flows = {"seg_1": 1000, "seg_2": 1800, "seg_3": 2500}
        capacities = {"seg_1": 2000, "seg_2": 2000, "seg_3": 2000}
        
        result = analyzer.model_congestion(flows, capacities)
        
        assert len(result["segments"]) == 3
        assert result["summary"]["total_segments"] == 3
    
    def test_detect_incidents(self, analyzer):
        """Test incident detection."""
        current = {"seg_1": {"speed": 25}, "seg_2": {"speed": 50}}
        baseline = {"seg_1": {"speed": 50}, "seg_2": {"speed": 50}}
        
        incidents = analyzer.detect_incidents(current, baseline, threshold=0.3)
        
        # seg_1 has 50% speed drop, should be detected
        assert len(incidents) >= 1
        assert incidents[0]["segment_id"] == "seg_1"
    
    def test_forecast_traffic(self, analyzer):
        """Test traffic forecasting."""
        historical = [
            {"volume": 1000},
            {"volume": 1100},
            {"volume": 950}
        ]
        
        forecast = analyzer.forecast_traffic(historical, forecast_horizon="1h")
        
        assert len(forecast["forecasts"]) == 4  # 4 x 15min intervals
    
    def test_simulate_traffic(self, analyzer):
        """Test traffic simulation."""
        demand = {"matrix": [[100, 200], [150, 50]]}
        
        result = analyzer.simulate_traffic(
            network=None,
            demand_matrix=demand,
            simulation_hours=1
        )
        
        assert result["duration_hours"] == 1
        assert len(result["results"]) > 0


class TestAccessibilityAnalyzer:
    """Test suite for AccessibilityAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create an AccessibilityAnalyzer instance."""
        return AccessibilityAnalyzer(
            default_mode="car",
            population_data={"average_density": 2000}
        )
    
    def test_init_default(self):
        """Test default initialization."""
        analyzer = AccessibilityAnalyzer()
        assert analyzer.default_mode == "car"
    
    def test_calculate_isochrone(self, analyzer):
        """Test isochrone calculation."""
        isochrones = analyzer.calculate_isochrone(
            origin={"id": "o1", "location": {"lat": 34.0, "lon": -118.0}},
            travel_times=[5, 10, 15],
            mode="car"
        )
        
        assert len(isochrones) == 3
        assert all(isinstance(i, Isochrone) for i in isochrones)
        # area should increase with time
        assert isochrones[0].area_sq_km < isochrones[1].area_sq_km < isochrones[2].area_sq_km
    
    def test_generate_service_area(self, analyzer):
        """Test service area generation."""
        facilities = [
            {"id": "f1", "location": {"lat": 34.0, "lon": -118.0}},
            {"id": "f2", "location": {"lat": 34.1, "lon": -118.1}}
        ]
        
        areas = analyzer.generate_service_area(
            facilities=facilities,
            breaks=[1, 2, 5],
            mode="car"
        )
        
        assert len(areas) == 2
        assert all(isinstance(a, ServiceArea) for a in areas)
    
    def test_analyze_equity(self, analyzer):
        """Test equity analysis."""
        groups = {
            "group_a": {"population": 10000, "areas": ["z1", "z2"]},
            "group_b": {"population": 5000, "areas": ["z3"]}
        }
        scores = {"z1": 0.8, "z2": 0.9, "z3": 0.4}
        
        result = analyzer.analyze_equity(groups, scores)
        
        assert "gini_coefficient" in result["equity_metrics"]
        assert "disparities" in result
    
    def test_calculate_accessibility_index(self, analyzer):
        """Test accessibility index calculation."""
        origin = {"id": "o1", "location": {"lat": 34.0, "lon": -118.0}}
        destinations = [
            {"id": "d1", "location": {"lat": 34.01, "lon": -118.01}, "weight": 100},
            {"id": "d2", "location": {"lat": 34.1, "lon": -118.1}, "weight": 50}
        ]
        
        result = analyzer.calculate_accessibility_index(
            origin=origin,
            destinations=destinations,
            decay_function="exponential"
        )
        
        assert result["accessibility_index"] > 0
        assert len(result["components"]) == 2


class TestTransitOptimizer:
    """Test suite for TransitOptimizer class."""
    
    @pytest.fixture
    def optimizer(self):
        """Create a TransitOptimizer instance."""
        return TransitOptimizer(
            optimization_objectives=["coverage", "ridership"]
        )
    
    def test_init_default(self):
        """Test default initialization."""
        optimizer = TransitOptimizer()
        assert "coverage" in optimizer.optimization_objectives
    
    def test_optimize_frequencies(self, optimizer):
        """Test frequency optimization."""
        routes = [
            {"id": "r1", "headway_minutes": 30, "cycle_time_hours": 1.5, "vehicle_capacity": 50},
            {"id": "r2", "headway_minutes": 15, "cycle_time_hours": 2.0, "vehicle_capacity": 40}
        ]
        demand = {
            "r1": {"peak_hourly": 300},
            "r2": {"peak_hourly": 500}
        }
        fleet = {"bus": 20}
        
        result = optimizer.optimize_frequencies(routes, demand, fleet)
        
        assert len(result["routes"]) == 2
        assert "total_vehicles_required" in result["summary"]
    
    def test_analyze_coverage(self, optimizer):
        """Test coverage analysis."""
        stops = [
            {"id": "s1", "location": {"lat": 34.0, "lon": -118.0}},
            {"id": "s2", "location": {"lat": 34.01, "lon": -118.01}}
        ]
        zones = [
            {"id": "z1", "centroid": {"lat": 34.0, "lon": -118.0}, "population": 5000},
            {"id": "z2", "centroid": {"lat": 34.1, "lon": -118.1}, "population": 3000}
        ]
        
        result = optimizer.analyze_coverage(
            stops=stops,
            population_zones=zones,
            walk_radius_m=400
        )
        
        assert "coverage_rate" in result
        assert result["total_stops"] == 2
    
    def test_design_network(self, optimizer):
        """Test network design."""
        demand_zones = [
            {"id": "z1", "demand": 1000, "centroid": {"lat": 34.0, "lon": -118.0}},
            {"id": "z2", "demand": 800, "centroid": {"lat": 34.1, "lon": -118.1}},
            {"id": "z3", "demand": 500, "centroid": {"lat": 34.2, "lon": -118.0}}
        ]
        
        result = optimizer.design_network(
            demand_zones=demand_zones,
            constraints={"max_routes": 3},
            mode="bus"
        )
        
        assert len(result["proposed_routes"]) > 0
        assert "metrics" in result
    
    def test_evaluate_scenario(self, optimizer):
        """Test scenario evaluation."""
        changes = [
            {"type": "add_route", "expected_ridership": 2000}
        ]
        
        result = optimizer.evaluate_scenario(
            base_network={},
            proposed_changes=changes
        )
        
        assert "benefit_cost_ratio" in result
        assert "recommendation" in result


class TestTrafficCondition:
    """Test suite for TrafficCondition enum."""
    
    def test_condition_values(self):
        """Test all condition values exist."""
        conditions = [
            TrafficCondition.FREE_FLOW,
            TrafficCondition.LIGHT,
            TrafficCondition.MODERATE,
            TrafficCondition.HEAVY,
            TrafficCondition.CONGESTED
        ]
        
        assert len(conditions) >= 5


class TestTransitMode:
    """Test suite for TransitMode enum."""
    
    def test_mode_values(self):
        """Test all mode values exist."""
        modes = [
            TransitMode.BUS,
            TransitMode.RAIL,
            TransitMode.SUBWAY,
            TransitMode.TRAM
        ]
        
        assert len(modes) >= 4
