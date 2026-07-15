"""Tests for multimodal transport module."""

import networkx as nx
from geo_infer_log.core.transport import (
    MultiModalPlanner,
    TransportationNetworkAnalyzer,
    TrafficSimulator,
    EmissionsCalculator,
)


class TestMultiModalPlanner:
    """Tests for multimodal transport planning."""

    def test_initialization(self) -> None:
        planner = MultiModalPlanner()
        assert planner is not None

    def test_import(self) -> None:
        assert MultiModalPlanner is not None

    def test_add_transfer_point_connects_networks(self) -> None:
        planner = MultiModalPlanner()
        network = nx.Graph()
        network.add_node("station", x=0.0, y=0.0)
        planner.networks["rail"] = network

        planner.add_transfer_point(
            location=(0.1, 0.1),
            name="Central",
            modes=["rail"],
            transfer_time={("rail", "bus"): 8},
        )

        assert planner.transfer_points[0]["id"] == 0
        transfer_node = "transfer_0_rail"
        assert transfer_node in network
        assert network.edges["station", transfer_node]["weight"] == 8


class TestTransportationNetworkAnalyzer:
    """Tests for transportation network analysis."""

    def test_initialization(self) -> None:
        analyzer = TransportationNetworkAnalyzer()
        assert analyzer is not None

    def test_import(self) -> None:
        assert TransportationNetworkAnalyzer is not None


class TestTrafficSimulator:
    """Tests for traffic simulation."""

    def test_initialization(self) -> None:
        sim = TrafficSimulator()
        assert sim is not None

    def test_import(self) -> None:
        assert TrafficSimulator is not None


class TestEmissionsCalculator:
    """Tests for emissions calculation."""

    def test_initialization(self) -> None:
        calc = EmissionsCalculator()
        assert calc is not None

    def test_import(self) -> None:
        assert EmissionsCalculator is not None
