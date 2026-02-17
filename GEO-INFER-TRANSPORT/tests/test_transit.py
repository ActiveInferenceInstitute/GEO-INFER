"""Tests for transit optimization module."""

import pytest
from geo_infer_transport.core.transit import (
    TransitOptimizer,
    TransitMode,
    TransitStop,
    TransitRoute,
)


class TestTransitDataclasses:
    """Tests for transit dataclass creation."""

    def test_transit_mode_values(self) -> None:
        assert TransitMode.BUS.value == "bus"
        assert TransitMode.RAIL.value == "rail"
        assert TransitMode.BRT.value == "brt"

    def test_transit_stop_creation(self) -> None:
        stop = TransitStop(
            stop_id="s1",
            name="Main St Station",
            location={"lat": 34.0, "lon": -118.0},
            routes=["r1", "r2"],
            boarding_daily=500,
        )
        assert stop.boarding_daily == 500
        assert len(stop.routes) == 2

    def test_transit_route_creation(self) -> None:
        route = TransitRoute(
            route_id="r1",
            name="Blue Line",
            mode=TransitMode.BUS,
            stops=["s1", "s2", "s3"],
            headway_minutes=15,
        )
        assert route.headway_minutes == 15
        assert len(route.stops) == 3


class TestTransitOptimizerInit:
    """Tests for TransitOptimizer initialization."""

    def test_default_initialization(self) -> None:
        optimizer = TransitOptimizer()
        assert optimizer is not None
        assert "coverage" in optimizer.optimization_objectives

    def test_custom_initialization(self) -> None:
        optimizer = TransitOptimizer(
            optimization_objectives=["ridership", "equity"],
        )
        assert "equity" in optimizer.optimization_objectives


class TestFrequencyOptimization:
    """Tests for route frequency optimization."""

    def test_optimize_frequencies(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.optimize_frequencies(
            routes=[
                {"id": "r1", "headway_minutes": 30, "vehicle_capacity": 50, "cycle_time_hours": 1.5},
                {"id": "r2", "headway_minutes": 60, "vehicle_capacity": 40, "cycle_time_hours": 2.0},
            ],
            demand_patterns={
                "r1": {"peak_hourly": 200},
                "r2": {"peak_hourly": 50},
            },
            fleet_constraints={"bus": 20},
            optimization_period="peak",
        )
        assert len(result["routes"]) == 2
        assert result["summary"]["total_routes"] == 2
        # High demand route should get shorter headway
        r1 = next(r for r in result["routes"] if r["route_id"] == "r1")
        assert r1["optimal_headway"] <= 30

    def test_fleet_constraint_violation(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.optimize_frequencies(
            routes=[
                {"id": "r1", "headway_minutes": 5, "vehicle_capacity": 50, "cycle_time_hours": 3.0},
            ],
            demand_patterns={"r1": {"peak_hourly": 500}},
            fleet_constraints={"bus": 2},
        )
        if result["summary"]["total_vehicles_required"] > 2:
            assert "constraint_violation" in result


class TestCoverageAnalysis:
    """Tests for transit coverage analysis."""

    def test_analyze_coverage(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.analyze_coverage(
            stops=[
                {"id": "s1", "location": {"lat": 34.050, "lon": -118.250}},
                {"id": "s2", "location": {"lat": 34.055, "lon": -118.245}},
            ],
            population_zones=[
                {"id": "z1", "centroid": {"lat": 34.050, "lon": -118.250}, "population": 1000},
                {"id": "z2", "centroid": {"lat": 34.100, "lon": -118.300}, "population": 2000},
            ],
            walk_radius_m=400,
        )
        assert result["total_stops"] == 2
        assert result["total_population"] == 3000
        assert 0 <= result["coverage_rate"] <= 1
        assert result["covered_population"] <= result["total_population"]

    def test_coverage_with_equity_analysis(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.analyze_coverage(
            stops=[{"id": "s1", "location": {"lat": 34.0, "lon": -118.0}}],
            population_zones=[
                {"id": "z1", "centroid": {"lat": 34.0, "lon": -118.0}, "population": 500},
            ],
            equity_focus=True,
        )
        assert "equity_analysis" in result


class TestNetworkDesign:
    """Tests for network design."""

    def test_design_network(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.design_network(
            demand_zones=[
                {"id": "z1", "demand": 1000, "centroid": {"lat": 34.0, "lon": -118.0}},
                {"id": "z2", "demand": 800, "centroid": {"lat": 34.1, "lon": -118.1}},
                {"id": "z3", "demand": 500, "centroid": {"lat": 34.2, "lon": -118.2}},
            ],
            constraints={"max_routes": 3},
            mode="bus",
        )
        assert len(result["proposed_routes"]) <= 3
        assert result["metrics"]["total_routes"] > 0
        assert result["metrics"]["estimated_daily_ridership"] > 0

    def test_design_network_respects_max_routes(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.design_network(
            demand_zones=[
                {"id": f"z{i}", "demand": 100 * i, "centroid": {"lat": 34.0 + i*0.01, "lon": -118.0}}
                for i in range(10)
            ],
            constraints={"max_routes": 2},
        )
        assert len(result["proposed_routes"]) <= 2


class TestScenarioEvaluation:
    """Tests for scenario evaluation."""

    def test_evaluate_add_route_scenario(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.evaluate_scenario(
            base_network={},
            proposed_changes=[
                {"type": "add_route", "expected_ridership": 2000},
            ],
        )
        assert "impacts" in result
        assert result["impacts"]["ridership_change"] == 2000
        assert "benefit_cost_ratio" in result

    def test_evaluate_frequency_increase(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.evaluate_scenario(
            base_network={},
            proposed_changes=[{"type": "increase_frequency"}],
        )
        assert result["impacts"]["coverage_change_pct"] == 0

    def test_recommendation_based_on_bcr(self) -> None:
        optimizer = TransitOptimizer()
        result = optimizer.evaluate_scenario(
            base_network={},
            proposed_changes=[{"type": "add_route", "expected_ridership": 5000}],
        )
        # 5000 rides * $3 * 365 days / $500000 should be well above 1.5
        assert result["recommendation"] == "Strongly recommended"
