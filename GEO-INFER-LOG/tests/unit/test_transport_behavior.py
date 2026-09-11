"""Behavior tests for transport core classes."""

from datetime import datetime

import pickle

import networkx as nx
import pandas as pd
import pytest

from geo_infer_log.core.transport import (
    EmissionsCalculator,
    MultiModalPlanner,
    TrafficSimulator,
    TransportationNetworkAnalyzer,
)
from geo_infer_log.models.schemas import FuelType, Route, Vehicle, VehicleType


def make_vehicle(
    vehicle_id: str,
    vehicle_type: str = "van",
    fuel: str = "diesel",
    emissions_per_km: float = 0.5,
) -> Vehicle:
    return Vehicle(
        id=vehicle_id,
        type=vehicle_type,
        capacity=100.0,
        max_range=500.0,
        speed=40.0,
        cost_per_km=1.0,
        emissions_per_km=emissions_per_km,
        location=(13.405, 52.52),
        fuel_type=fuel,
    )


def make_route(route_id: str, vehicle_id: str, distance: float) -> Route:
    return Route(
        id=route_id,
        vehicle_id=vehicle_id,
        stops=[],
        departure_time=datetime(2026, 1, 1, 8, 0),
        estimated_arrival_time=datetime(2026, 1, 1, 9, 0),
        total_distance=distance,
        total_time=10.0,
        total_cost=distance,
        total_emissions=distance,
        geometry=None,
    )


def road_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node(1, x=13.40, y=52.51)
    graph.add_node(2, x=13.41, y=52.52)
    graph.add_node(3, x=13.42, y=52.53)
    graph.add_edge(1, 2, weight=2, distance=5.0)
    graph.add_edge(2, 3, weight=2, distance=5.0)
    return graph


def rail_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("A", x=13.41, y=52.52)
    graph.add_node("B", x=13.42, y=52.53)
    graph.add_edge("A", "B", weight=1, distance=20.0)
    return graph


class TestMultiModalPlanner:
    """Tests for multimodal route planning."""

    def test_transfer_point_without_networks(self) -> None:
        planner = MultiModalPlanner()
        planner.add_transfer_point((13.4, 52.5), "hub", ["road"], {("road", "rail"): 5})
        assert planner.transfer_points[0]["id"] == 0
        assert planner.transfer_points[0]["name"] == "hub"

    def test_transfer_point_connects_networks(self) -> None:
        planner = MultiModalPlanner()
        planner.networks["road"] = road_graph()
        planner.networks["rail"] = rail_graph()
        planner.add_transfer_point(
            (13.405, 52.515),
            "hub",
            ["road", "rail"],
            {("road", "rail"): 5, ("rail", "road"): 5},
        )
        road = planner.networks["road"]
        rail = planner.networks["rail"]
        assert "transfer_0_road" in road.nodes
        assert "transfer_0_rail" in rail.nodes
        assert road.has_edge(1, "transfer_0_road")

    def test_plan_route_fallback_without_networks(self) -> None:
        planner = MultiModalPlanner()
        route = planner.plan_route((13.40, 52.51), (13.44, 52.55), ["car"])
        assert len(route["segments"]) == 1
        assert route["segments"][0]["mode"] == "car"
        assert route["num_transfers"] == 0
        assert route["total_distance"] > 0

    def test_plan_route_crosses_modes(self) -> None:
        planner = MultiModalPlanner()
        planner.networks["road"] = road_graph()
        planner.networks["rail"] = rail_graph()
        planner.add_transfer_point(
            (13.405, 52.515),
            "hub",
            ["road", "rail"],
            {("road", "rail"): 5, ("rail", "road"): 5},
        )
        route = planner.plan_route((13.40, 52.51), (13.42, 52.53), ["road", "rail"])
        assert route["total_distance"] > 0
        assert route["num_transfers"] >= 0
        assert route["segments"]
        modes = {seg["mode"] for seg in route["segments"]}
        assert modes <= {"road", "rail", "unknown"}

    def test_load_network_from_pickle(self, tmp_path) -> None:
        path = tmp_path / "road.pkl"
        with open(path, "wb") as f:
            pickle.dump(road_graph(), f)
        planner = MultiModalPlanner()
        planner.load_network("road", str(path))
        assert set(planner.networks) == {"road"}
        assert planner.networks["road"].number_of_nodes() == 3

    def test_compare_routes_dataframe(self) -> None:
        planner = MultiModalPlanner()
        frame = planner.compare_routes(
            (13.40, 52.51), (13.44, 52.55), [["car"], ["bike", "car"]]
        )
        assert list(frame["modes"]) == ["car", "bike-car"]
        assert {"total_distance", "num_transfers"} <= set(frame.columns)


class TestTransportationNetworkAnalyzer:
    """Tests for network analysis."""

    def test_metrics_require_network(self) -> None:
        analyzer = TransportationNetworkAnalyzer()
        with pytest.raises(ValueError, match="Network must be loaded"):
            analyzer.calculate_network_metrics()

    def test_calculate_network_metrics(self, tmp_path) -> None:
        path = tmp_path / "net.pkl"
        with open(path, "wb") as f:
            pickle.dump(road_graph(), f)
        analyzer = TransportationNetworkAnalyzer()
        analyzer.load_network(str(path))
        metrics = analyzer.calculate_network_metrics()
        assert metrics["num_nodes"] == 3
        assert metrics["num_edges"] == 2
        assert metrics["density"] == pytest.approx(2 / 6)
        assert metrics["max_betweenness_centrality"] >= 0

    def test_identify_critical_links(self, tmp_path) -> None:
        path = tmp_path / "net.pkl"
        with open(path, "wb") as f:
            pickle.dump(road_graph(), f)
        analyzer = TransportationNetworkAnalyzer()
        analyzer.load_network(str(path))
        links = analyzer.identify_critical_links(top_n=1)
        assert links == [(1, 2)]

    def test_critical_links_require_network(self) -> None:
        analyzer = TransportationNetworkAnalyzer()
        with pytest.raises(ValueError, match="Network must be loaded"):
            analyzer.identify_critical_links()

    def test_load_flow_data_csv(self, tmp_path) -> None:
        path = tmp_path / "flow.csv"
        pd.DataFrame(
            {"origin": [1, 2], "destination": [2, 3], "flow": [10, 20]}
        ).to_csv(path, index=False)
        with open(tmp_path / "net.pkl", "wb") as f:
            pickle.dump(road_graph(), f)
        analyzer = TransportationNetworkAnalyzer()
        analyzer.load_network(str(tmp_path / "net.pkl"))
        analyzer.load_flow_data(str(path))
        result = analyzer.analyze_flow()
        assert result["total_flow"] == 30
        assert result["max_flow"] == 20
        assert result["max_flow_edge"] == (2, 3)

    def test_analyze_flow_requires_network_and_data(self) -> None:
        analyzer = TransportationNetworkAnalyzer()
        with pytest.raises(ValueError, match="Network and flow data"):
            analyzer.analyze_flow()

    def test_analyze_flow_falls_back_to_max_flow(self, tmp_path) -> None:
        with open(tmp_path / "net.pkl", "wb") as f:
            pickle.dump(road_graph(), f)
        analyzer = TransportationNetworkAnalyzer()
        analyzer.load_network(str(tmp_path / "net.pkl"))
        analyzer.flow_data = pd.DataFrame({"x": [1]})  # no usable flow columns
        result = analyzer.analyze_flow()
        assert result["total_flow"] == 0
        assert result["congestion_points"] == []

    def test_analyze_flow_flags_congestion(self, tmp_path) -> None:
        with open(tmp_path / "net.pkl", "wb") as f:
            pickle.dump(road_graph(), f)
        analyzer = TransportationNetworkAnalyzer()
        analyzer.load_network(str(tmp_path / "net.pkl"))
        analyzer.network[1][2]["capacity"] = 10.0
        analyzer.flow_data = pd.DataFrame(
            {"origin": [1], "destination": [2], "flow": [9]}
        )
        result = analyzer.analyze_flow()
        assert result["congestion_points"][0]["utilization"] == pytest.approx(0.9)


class TestTrafficSimulator:
    """Tests for traffic simulation."""

    def make_simulator(self) -> TrafficSimulator:
        graph = road_graph()
        graph.add_edge(1, 3, weight=10, distance=100.0)
        return TrafficSimulator(graph)

    def test_simulate_requires_network(self) -> None:
        with pytest.raises(ValueError, match="Network must be loaded"):
            TrafficSimulator().simulate_traffic("1", "3", "morning")

    def test_simulate_requires_defined_period(self) -> None:
        simulator = self.make_simulator()
        simulator.set_time_periods(["morning"])
        with pytest.raises(ValueError, match="Time period"):
            simulator.simulate_traffic("1", "3", "night")

    def test_set_edge_speeds_validates(self) -> None:
        simulator = self.make_simulator()
        simulator.set_time_periods(["morning"])
        with pytest.raises(ValueError, match="not in network"):
            simulator.set_edge_speeds((1, 99), {"morning": 30})
        with pytest.raises(ValueError, match="not defined"):
            simulator.set_edge_speeds((1, 2), {"night": 30})
        simulator.set_edge_speeds((1, 2), {"morning": 10})
        assert simulator.edge_speeds[(1, 2)]["morning"] == 10

    def test_simulate_picks_faster_route(self) -> None:
        simulator = self.make_simulator()
        simulator.set_time_periods(["morning"])
        # Long direct edge is congested; the two-hop path stays fast.
        simulator.set_edge_speeds((1, 2), {"morning": 60})
        simulator.set_edge_speeds((2, 3), {"morning": 60})
        simulator.set_edge_speeds((1, 3), {"morning": 5})
        result = simulator.simulate_traffic(1, 3, "morning")
        assert result["path"] == [1, 2, 3]
        assert result["distance"] == pytest.approx(10.0)
        assert result["travel_time"] < float("inf")

    def test_simulate_no_path_returns_inf(self) -> None:
        graph = nx.DiGraph()
        graph.add_node(1)
        graph.add_node(2)
        simulator = TrafficSimulator(graph)
        simulator.set_time_periods(["morning"])
        result = simulator.simulate_traffic("1", "2", "morning")
        assert result["path"] == []
        assert result["travel_time"] == float("inf")
        assert result["distance"] == 0

    def test_zero_speed_gives_infinite_time(self) -> None:
        simulator = self.make_simulator()
        simulator.set_time_periods(["morning"])
        simulator.set_edge_speeds((1, 2), {"morning": 0})
        simulator.set_edge_speeds((2, 3), {"morning": 0})
        result = simulator.simulate_traffic("1", "3", "morning")
        assert result["travel_time"] == float("inf")

    def test_analyze_congestion(self) -> None:
        simulator = self.make_simulator()
        simulator.set_time_periods(["morning"])
        simulator.set_edge_speeds((1, 2), {"morning": 10})
        simulator.set_edge_speeds((2, 3), {"morning": 80})
        simulator.set_edge_speeds((1, 3), {"morning": 80})
        result = simulator.analyze_congestion("morning")
        assert result["morning"]["total_edges"] == 3
        assert result["morning"]["congested_edges"][0]["edge"] == (1, 2)
        assert result["morning"]["congestion_ratio"] == pytest.approx(1 / 3)

    def test_analyze_congestion_requires_network(self) -> None:
        with pytest.raises(ValueError, match="Network must be loaded"):
            TrafficSimulator().analyze_congestion()


class TestEmissionsCalculator:
    """Tests for emissions calculation."""

    def test_known_factor_route_emissions(self) -> None:
        calc = EmissionsCalculator()
        vehicle = make_vehicle("v1", "truck", "diesel", emissions_per_km=99.0)
        assert calc.calculate_route_emissions(vehicle, 100.0) == pytest.approx(90.0)

    def test_adjustment_factors(self) -> None:
        calc = EmissionsCalculator()
        vehicle = make_vehicle("v1", "van", "diesel")
        # 0.5 * 0.5 load * 2.0 terrain = same as base
        assert calc.calculate_route_emissions(
            vehicle, 100.0, 0.5, 2.0
        ) == pytest.approx(50.0)

    def test_unknown_combination_falls_back_to_vehicle(self) -> None:
        calc = EmissionsCalculator()
        vehicle = make_vehicle("v1", "van", "hydrogen", emissions_per_km=0.7)
        assert calc.calculate_route_emissions(vehicle, 10.0) == pytest.approx(7.0)

    def test_set_emissions_factor(self) -> None:
        calc = EmissionsCalculator()
        calc.set_emissions_factor(VehicleType.VAN, FuelType.HYDROGEN, 0.3)
        vehicle = make_vehicle("v1", "van", "hydrogen")
        assert calc.calculate_route_emissions(vehicle, 10.0) == pytest.approx(3.0)

    def test_compare_emissions_dataframe(self) -> None:
        calc = EmissionsCalculator()
        options = [make_vehicle("van", "van"), make_vehicle("truck", "truck")]
        frame = calc.compare_emissions({"distance": 100.0}, options)
        assert list(frame["vehicle_id"]) == ["van", "truck"]
        assert frame["emissions"].iloc[0] == pytest.approx(50.0)

    def test_fleet_emissions_aggregation(self) -> None:
        calc = EmissionsCalculator()
        fleet = [make_vehicle("v1", "van"), make_vehicle("v2", "truck")]
        routes = [
            make_route("r1", "v1", 100.0),
            make_route("r2", "v2", 100.0),
            make_route("r3", "ghost", 999.0),
        ]
        result = calc.calculate_fleet_emissions(fleet, routes)
        assert result["total_emissions"] == pytest.approx(140.0)
        assert result["total_distance"] == pytest.approx(200.0)
        assert result["average_emissions_per_km"] == pytest.approx(0.7)
        assert set(result["emissions_by_vehicle"]) == {"v1", "v2"}

    def test_fleet_emissions_no_matches(self) -> None:
        calc = EmissionsCalculator()
        result = calc.calculate_fleet_emissions(
            [make_vehicle("v1")], [make_route("r1", "ghost", 10.0)]
        )
        assert result["total_emissions"] == 0
        assert result["emissions_by_vehicle"] == {}
