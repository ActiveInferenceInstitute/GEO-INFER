"""Regression tests: reverse graph edges must carry travel_time.

build_from_edges duplicates each two-way edge with a ``<id>_rev`` reverse
edge. Routing (and isochrones) weight on ``travel_time``; a reverse edge
without that attribute defaults to weight 1.0 in networkx, so every route
segment traversed against its digitized direction is under-costed by
orders of magnitude, and traffic-adjusted reverse edges collapse to weight 0.
"""

import networkx as nx
import pytest

from geo_infer_transport.core.network import TransportNetwork
from geo_infer_transport.core.routing import RoutingEngine


@pytest.fixture
def network() -> TransportNetwork:
    net = TransportNetwork()
    net.build_from_edges(
        [{"id": "e1", "from": "a", "to": "b", "length_m": 1000, "speed_limit": 50}]
    )
    return net


class TestReverseEdgeTravelTime:
    """Regression: reverse edges inherit the forward edge's travel_time."""

    def test_reverse_edge_dijkstra_cost_matches_travel_time(
        self, network: TransportNetwork
    ):
        """nx.dijkstra on the reverse edge costs length/speed * 3600, not 1.0."""
        cost = nx.dijkstra_path_length(
            network.graph, "b", "a", weight="travel_time"
        )
        assert cost == pytest.approx((1000 / 1000) / 50 * 3600)  # 72.0 s

    def test_reverse_edge_graph_attribute(self, network: TransportNetwork):
        """The reverse edge stores the same travel_time as the forward edge."""
        forward = network.graph.get_edge_data("a", "b")
        reverse = network.graph.get_edge_data("b", "a")
        assert reverse["travel_time"] == pytest.approx(forward["travel_time"])
        assert reverse["road_class"] == forward["road_class"]

    def test_traffic_adjusted_reverse_edge_not_free(self, network: TransportNetwork):
        """A slowed reverse edge costs travel_time * factor, never 0."""
        engine = RoutingEngine(network=network, real_time_traffic=True)
        engine.update_traffic({"e1_rev": 2.0})
        route = engine.route(
            origin={"node_id": "b"}, destination={"node_id": "a"},
            optimization="time",
        )
        assert route.path == ["b", "a"]
        assert route.total_time_s == pytest.approx(144.0)  # 72 s * 2.0