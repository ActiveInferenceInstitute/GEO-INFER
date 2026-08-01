"""
DOMAIN-02 Acceptance tests for GEO-INFER-TRANSPORT documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. TrafficAnalyzer — BPR congestion modeling, flow analysis, traffic
   simulation, EWMA forecasting, incident detection.
2. TransportNetwork — edge-based network construction, connectivity analysis,
   centrality calculation, network statistics.
3. RoutingEngine — Dijkstra routing, multi-waypoint optimization, OD matrix,
   alternative route finding.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest

from geo_infer_transport.core.traffic import (
    TrafficAnalyzer,
    TrafficCondition,
    FlowResult,
)
from geo_infer_transport.core.network import (
    TransportNetwork,
    RoadClass,
    TransportMode,
)
from geo_infer_transport.core.routing import (
    RoutingEngine,
    Route,
    RoutingAlgorithm,
    OptimizationCriteria,
)


# ---------------------------------------------------------------------------
# TrafficAnalyzer
# ---------------------------------------------------------------------------

class TestTrafficAnalyzer:
    """Acceptance: traffic flow analysis, congestion, and forecasting."""

    @pytest.fixture
    def analyzer(self) -> TrafficAnalyzer:
        return TrafficAnalyzer(model_type="bpr")

    def test_analyze_flow_returns_flow_result(self, analyzer):
        """analyze_flow returns a FlowResult with LOS classification."""
        result = analyzer.analyze_flow(
            segment={"id": "seg1", "capacity": 2000, "speed_limit": 50},
            counts=[
                {"count": 200, "speed_kmh": 45},
                {"count": 180, "speed_kmh": 48},
            ],
            time_period="peak",
        )
        assert isinstance(result, FlowResult)
        assert result.segment_id == "seg1"
        assert result.volume > 0
        assert result.level_of_service in ["A", "B", "C", "D", "E", "F"]

    def test_model_congestion_bpr_delay(self, analyzer):
        """model_congestion applies BPR delay factor t = t0 * (1 + 0.15*(v/c)^4)."""
        result = analyzer.model_congestion(
            network_flows={"s1": 1000, "s2": 2500},
            capacity_data={"s1": 2000, "s2": 2000},
            algorithm="bpr",
        )
        assert result["algorithm"] == "bpr"
        assert len(result["segments"]) == 2
        # s1: v/c = 0.5 → delay = 1 + 0.15 * 0.5^4 = 1 + 0.15*0.0625 ≈ 1.009
        # s2: v/c = 1.25 → delay = 1 + 0.15 * 1.25^4 ≈ 1 + 0.15*2.441 ≈ 1.366
        seg2 = [s for s in result["segments"] if s["segment_id"] == "s2"][0]
        assert seg2["delay_factor"] > 1.2  # congested
        assert seg2["condition"] == TrafficCondition.MODERATE.value

    def test_model_congestion_free_flow_classification(self, analyzer):
        """Low V/C ratio yields free_flow condition."""
        result = analyzer.model_congestion(
            network_flows={"s1": 100},
            capacity_data={"s1": 2000},
            algorithm="bpr",
        )
        seg = result["segments"][0]
        assert seg["condition"] == TrafficCondition.FREE_FLOW.value
        assert seg["delay_factor"] < 1.05

    def test_simulate_traffic_completes_trips(self, analyzer):
        """simulate_traffic produces results with completed trips."""
        result = analyzer.simulate_traffic(
            network=None,
            demand_matrix={"matrix": [[100, 50], [30, 80]]},
            simulation_hours=1,
            time_step_seconds=60,
        )
        assert result["statistics"]["total_trips"] == 260
        assert result["statistics"]["completed_trips"] >= 0
        assert len(result["results"]) > 0
        # Each result step has required fields
        first = result["results"][0]
        assert "vehicles_in_network" in first
        assert "average_speed_kmh" in first
        assert "congestion_level" in first
        assert "bpr_delay_factor" in first

    def test_forecast_traffic_ewma(self, analyzer):
        """forecast_traffic uses EWMA and returns widening confidence intervals."""
        historical = [
            {"volume": v} for v in [800, 850, 900, 950, 1000, 1050, 1100, 1150]
        ]
        result = analyzer.forecast_traffic(
            historical_data=historical,
            forecast_horizon="1h",
            model="ewma",
        )
        assert len(result["forecasts"]) == 4  # 1h = 4 × 15min steps
        first = result["forecasts"][0]
        assert "predicted_volume" in first
        assert "confidence_lower" in first
        assert "confidence_upper" in first
        # Confidence interval should widen over horizon
        first_width = first["confidence_upper"] - first["confidence_lower"]
        last_width = result["forecasts"][-1]["confidence_upper"] - result["forecasts"][-1]["confidence_lower"]
        assert last_width >= first_width

    def test_forecast_traffic_empty_data(self, analyzer):
        """forecast_traffic handles empty historical data gracefully."""
        result = analyzer.forecast_traffic(
            historical_data=[],
            forecast_horizon="1h",
        )
        assert len(result["forecasts"]) == 4
        assert result["forecasts"][0]["predicted_volume"] >= 0

    def test_detect_incidents_finds_anomaly(self, analyzer):
        """detect_incidents flags segments with significant speed drop."""
        incidents = analyzer.detect_incidents(
            current_data={"s1": {"speed": 30}, "s2": {"speed": 50}},
            historical_baseline={"s1": {"speed": 60}, "s2": {"speed": 50}},
            threshold=0.3,
        )
        assert len(incidents) == 1
        assert incidents[0]["segment_id"] == "s1"
        assert incidents[0]["severity"] in ["moderate", "high"]

    def test_detect_incidents_no_false_positive(self, analyzer):
        """Normal speed segments are not flagged as incidents."""
        incidents = analyzer.detect_incidents(
            current_data={"s1": {"speed": 55}},
            historical_baseline={"s1": {"speed": 60}},
            threshold=0.3,
        )
        assert len(incidents) == 0


# ---------------------------------------------------------------------------
# TransportNetwork
# ---------------------------------------------------------------------------

class TestTransportNetwork:
    """Acceptance: network topology construction and analysis."""

    @pytest.fixture
    def edges(self) -> list:
        """Simple grid network edges."""
        return [
            {"id": "e1", "from": "A", "to": "B", "road_class": "primary", "length_m": 1000, "speed_limit": 60},
            {"id": "e2", "from": "B", "to": "C", "road_class": "secondary", "length_m": 800, "speed_limit": 50},
            {"id": "e3", "from": "C", "to": "D", "road_class": "secondary", "length_m": 600, "speed_limit": 50},
            {"id": "e4", "from": "A", "to": "D", "road_class": "motorway", "length_m": 2000, "speed_limit": 100},
        ]

    @pytest.fixture
    def network(self, edges) -> TransportNetwork:
        net = TransportNetwork()
        net.build_from_edges(edges)
        return net

    def test_build_from_edges_creates_bidirectional(self, edges):
        """build_from_edges adds reverse edges for two-way roads."""
        net = TransportNetwork()
        summary = net.build_from_edges(edges)
        assert summary["nodes_created"] == 4
        assert summary["edges_created"] == 4
        # Each non-one-way edge gets a reverse edge → 8 directed edges
        assert net.graph.number_of_edges() == 8

    def test_build_from_edges_one_way(self):
        """One-way edges are not duplicated in reverse."""
        net = TransportNetwork()
        net.build_from_edges([
            {"id": "e1", "from": "A", "to": "B", "road_class": "primary", "length_m": 500, "one_way": True},
        ])
        assert net.graph.number_of_edges() == 1

    def test_analyze_connectivity_components(self, network):
        """analyze_connectivity returns strongly/weakly connected components."""
        result = network.analyze_connectivity(method="components")
        assert result["edge_count"] == 8
        assert "strongly_connected_components" in result
        assert "weakly_connected_components" in result
        # A-B-C-D with A-D is connected
        assert result["weakly_connected_components"] == 1

    def test_analyze_connectivity_reachability(self, network):
        """analyze_connectivity reachability finds all reachable nodes."""
        result = network.analyze_connectivity(method="reachability", origin="A")
        assert result["origin"] == "A"
        assert result["reachable_nodes"] == 4  # A, B, C, D

    def test_calculate_centrality_betweenness(self, network):
        """calculate_centrality returns top nodes by betweenness."""
        result = network.calculate_centrality(centrality_type="betweenness", weight="length")
        assert "top_nodes" in result
        assert len(result["top_nodes"]) <= 4
        assert all("node_id" in n for n in result["top_nodes"])

    def test_get_statistics(self, network):
        """get_statistics returns node/edge counts and density."""
        stats = network.get_statistics()
        assert stats["node_count"] == 4
        assert stats["edge_count"] == 8
        assert "density" in stats
        assert stats["total_length_km"] > 0
        assert "road_class_distribution" in stats


# ---------------------------------------------------------------------------
# RoutingEngine
# ---------------------------------------------------------------------------

class TestRoutingEngine:
    """Acceptance: routing and optimization."""

    @pytest.fixture
    def network_with_routes(self) -> tuple:
        """Build a network and routing engine for route tests."""
        edges = [
            {"id": "e1", "from": "A", "to": "B", "road_class": "primary", "length_m": 1000, "speed_limit": 60},
            {"id": "e2", "from": "B", "to": "C", "road_class": "secondary", "length_m": 800, "speed_limit": 50},
            {"id": "e3", "from": "C", "to": "D", "road_class": "secondary", "length_m": 600, "speed_limit": 50},
            {"id": "e4", "from": "A", "to": "D", "road_class": "motorway", "length_m": 2000, "speed_limit": 100},
            {"id": "e5", "from": "B", "to": "D", "road_class": "primary", "length_m": 500, "speed_limit": 60},
        ]
        net = TransportNetwork()
        net.build_from_edges(edges)
        engine = RoutingEngine(network=net, algorithm="dijkstra")
        return net, engine

    def test_route_finds_path(self, network_with_routes):
        """route() returns a Route with a valid path."""
        _, engine = network_with_routes
        route = engine.route(
            origin={"node_id": "A"},
            destination={"node_id": "D"},
            optimization="time",
        )
        assert isinstance(route, Route)
        assert route.origin == "A"
        assert route.destination == "D"
        assert len(route.path) >= 2
        assert route.total_distance_m > 0
        assert route.total_time_s > 0

    def test_route_includes_instructions(self, network_with_routes):
        """route() generates turn-by-turn instructions."""
        _, engine = network_with_routes
        route = engine.route(
            origin={"node_id": "A"},
            destination={"node_id": "C"},
        )
        assert len(route.instructions) >= 2
        assert route.instructions[0].startswith("Start at")

    def test_route_no_path_returns_empty(self):
        """route() on disconnected network returns empty path."""
        net = TransportNetwork()
        net.build_from_edges([
            {"id": "e1", "from": "A", "to": "B", "road_class": "primary", "length_m": 500},
            {"id": "e2", "from": "C", "to": "D", "road_class": "primary", "length_m": 500},
        ])
        engine = RoutingEngine(network=net, algorithm="dijkstra")
        route = engine.route({"node_id": "A"}, {"node_id": "D"})
        assert route.path == []

    def test_optimize_route_nearest_neighbor(self):
        """optimize_route orders waypoints via nearest-neighbor heuristic."""
        engine = RoutingEngine()
        waypoints = [
            {"id": "w0", "lat": 40.0, "lon": -74.0},
            {"id": "w1", "lat": 40.01, "lon": -74.01},
            {"id": "w2", "lat": 40.02, "lon": -74.02},
            {"id": "w3", "lat": 40.005, "lon": -74.005},
        ]
        result = engine.optimize_route(waypoints, constraints={}, objective="minimize_time")
        assert "optimized_order" in result
        assert len(result["optimized_order"]) == 4
        assert result["estimated_distance_m"] > 0

    def test_calculate_matrix(self, network_with_routes):
        """calculate_matrix returns an OD cost matrix."""
        _, engine = network_with_routes
        result = engine.calculate_matrix(
            origins=[{"node_id": "A"}, {"node_id": "B"}],
            destinations=[{"node_id": "C"}, {"node_id": "D"}],
            metric="time",
        )
        assert result["shape"] == [2, 2]
        assert len(result["matrix"]) == 2
        assert all(len(row) == 2 for row in result["matrix"])

    def test_find_alternatives_includes_primary(self, network_with_routes):
        """find_alternatives returns at least the primary route."""
        _, engine = network_with_routes
        alternatives = engine.find_alternatives(
            origin={"node_id": "A"},
            destination={"node_id": "D"},
            count=3,
        )
        assert len(alternatives) >= 1
        assert all(isinstance(r, Route) for r in alternatives)

    def test_update_traffic_data(self, network_with_routes):
        """update_traffic stores traffic factors for real-time routing."""
        _, engine = network_with_routes
        engine.update_traffic({"e1": 1.5, "e2": 2.0})
        assert engine._traffic_data["e1"] == 1.5
        assert engine._traffic_data["e2"] == 2.0
