"""Regression tests for GS-186/187/188.

- Unroutable origin/destination nodes must degrade (empty path, route_source
  "network") instead of raising nx.NodeNotFound.
- TrafficAnalyzer only accepts the implemented 'bpr' model.
- simulate_traffic rejects non-positive time_step_seconds; route() no longer
  accepts silently-ignored mode/avoid/via parameters.
"""

import inspect

import pytest

from geo_infer_transport import TransportNetwork
from geo_infer_transport.core.routing import RoutingEngine
from geo_infer_transport.core.traffic import TrafficAnalyzer


@pytest.fixture
def small_network():
    network = TransportNetwork()
    network.build_from_edges(
        [{"id": "e1", "from": "a", "to": "b", "length_m": 1000, "speed_limit": 50}]
    )
    return network


def test_route_unknown_origin_degrades_to_empty_network_route(small_network):
    engine = RoutingEngine(network=small_network)
    route = engine.route({"node_id": "zz"}, {"node_id": "b"})
    assert route.route_source == "network"
    assert route.path == []
    assert route.total_distance_m == 0
    assert route.total_time_s == 0


def test_route_unknown_destination_degrades_to_empty_network_route(small_network):
    engine = RoutingEngine(network=small_network)
    route = engine.route({"node_id": "a"}, {"node_id": "zz"})
    assert route.route_source == "network"
    assert route.path == []


def test_route_known_endpoints_still_compute(small_network):
    engine = RoutingEngine(network=small_network)
    route = engine.route({"node_id": "a"}, {"node_id": "b"})
    assert route.route_source == "network"
    assert route.path == ["a", "b"]
    assert route.total_time_s == pytest.approx(72.0)


def test_calculate_isochrone_unknown_origin_degenerates(small_network):
    from geo_infer_transport.core.accessibility import AccessibilityAnalyzer

    analyzer = AccessibilityAnalyzer(network=small_network)
    isochrones = analyzer.calculate_isochrone({"node_id": "zz"}, [5])
    assert len(isochrones) == 1
    assert isochrones[0].reachable_nodes == ["zz"]


def test_traffic_analyzer_rejects_unimplemented_model():
    with pytest.raises(ValueError, match="model_type"):
        TrafficAnalyzer(model_type="akcelik")
    with pytest.raises(ValueError, match="model_type"):
        TrafficAnalyzer(model_type="hcm")


def test_traffic_analyzer_accepts_bpr():
    analyzer = TrafficAnalyzer(model_type="bpr")
    assert analyzer.model_type == "bpr"


def test_simulate_traffic_rejects_non_positive_time_step():
    analyzer = TrafficAnalyzer(model_type="bpr")
    with pytest.raises(ValueError, match="time_step_seconds"):
        analyzer.simulate_traffic(
            None, {"matrix": [[1]]}, simulation_hours=1, time_step_seconds=0
        )
    with pytest.raises(ValueError, match="time_step_seconds"):
        analyzer.simulate_traffic(
            None, {"matrix": [[1]]}, simulation_hours=1, time_step_seconds=-30
        )


def test_route_signature_has_no_unused_mode_avoid_via_params():
    params = set(inspect.signature(RoutingEngine.route).parameters)
    assert "avoid" not in params
    assert "via" not in params
    assert "mode" not in params
