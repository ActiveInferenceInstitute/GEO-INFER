"""Tests for the transport network API lifecycle (GS-222).

The network-analysis and traffic-simulation endpoints operate on networks
loaded through the API itself: POST ``/transport/network/load`` backs the
analyzer singleton, and POST ``/transport/traffic/load`` +
``/transport/traffic/time-periods`` back the simulator singleton. Before a
network is loaded, the dependent endpoints must fail with a 400 whose body
names the missing precondition instead of silently computing nothing.
"""

import pickle

import networkx as nx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from geo_infer_log.api.transport import (
    get_network_analyzer,
    get_traffic_simulator,
    router,
)
from geo_infer_log.core.transport import TransportationNetworkAnalyzer, TrafficSimulator


def _write_network(tmp_path, nodes=("a", "b", "c")):
    graph = nx.DiGraph()
    graph.add_edge(nodes[0], nodes[1], distance=2.0, free_flow_speed=60)
    graph.add_edge(nodes[1], nodes[2], distance=3.0, free_flow_speed=40)
    path = tmp_path / "network.gpickle"
    path.write_bytes(pickle.dumps(graph))
    return str(path)


def _client(tmp_path):
    analyzer = TransportationNetworkAnalyzer()
    simulator = TrafficSimulator()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_network_analyzer] = lambda: analyzer
    app.dependency_overrides[get_traffic_simulator] = lambda: simulator
    return TestClient(app), analyzer, simulator


class TestNetworkLifecycle:
    """Load-then-query must return 200; unload must 400 with the precondition."""

    def test_metrics_before_load_returns_400_naming_precondition(self, tmp_path):
        client, analyzer, _ = _client(tmp_path)
        response = client.post("/transport/network/metrics", json={})
        assert response.status_code == 400
        assert "loaded" in response.json()["detail"].lower()

    def test_metrics_after_load_returns_200(self, tmp_path):
        client, _, _ = _client(tmp_path)
        network_file = _write_network(tmp_path)
        loaded = client.post(
            "/transport/network/load", json={"network_file": network_file}
        )
        assert loaded.status_code == 200
        assert loaded.json()["loaded"] is True
        assert loaded.json()["num_nodes"] == 3

        metrics = client.post("/transport/network/metrics", json={})
        assert metrics.status_code == 200
        assert metrics.json()["num_nodes"] == 3
        assert metrics.json()["num_edges"] == 2

    def test_critical_links_after_load_returns_200(self, tmp_path):
        client, _, _ = _client(tmp_path)
        client.post(
            "/transport/network/load",
            json={"network_file": _write_network(tmp_path)},
        )
        links = client.post("/transport/network/critical-links", json={})
        assert links.status_code == 200

    def test_load_failure_returns_400(self, tmp_path):
        client, _, _ = _client(tmp_path)
        missing = tmp_path / "missing.gpickle"
        response = client.post(
            "/transport/network/load", json={"network_file": str(missing)}
        )
        assert response.status_code == 400

    def test_simulate_requires_network_and_time_periods(self, tmp_path):
        client, _, _ = _client(tmp_path)
        unloaded = client.post(
            "/transport/traffic/simulate",
            json={
                "origin": "a",
                "destination": "c",
                "departure_time": "morning_peak",
            },
        )
        assert unloaded.status_code == 400
        assert "loaded" in unloaded.json()["detail"].lower()

        client.post(
            "/transport/traffic/load",
            json={"network_file": _write_network(tmp_path)},
        )
        client.post(
            "/transport/traffic/time-periods",
            json={"periods": ["morning_peak", "evening_peak"]},
        )
        result = client.post(
            "/transport/traffic/simulate",
            json={
                "origin": "a",
                "destination": "c",
                "departure_time": "morning_peak",
            },
        )
        assert result.status_code == 200
        assert result.json()["path"] == ["a", "b", "c"]

    def test_simulate_undefined_period_is_400(self, tmp_path):
        client, _, _ = _client(tmp_path)
        client.post(
            "/transport/traffic/load",
            json={"network_file": _write_network(tmp_path)},
        )
        client.post(
            "/transport/traffic/time-periods",
            json={"periods": ["morning_peak"]},
        )
        result = client.post(
            "/transport/traffic/simulate",
            json={
                "origin": "a",
                "destination": "c",
                "departure_time": "evening_peak",
            },
        )
        assert result.status_code == 400
        assert "evening_peak" in result.json()["detail"]

    def test_congestion_after_load_returns_200(self, tmp_path):
        client, _, _ = _client(tmp_path)
        client.post(
            "/transport/traffic/load",
            json={"network_file": _write_network(tmp_path)},
        )
        client.post(
            "/transport/traffic/time-periods",
            json={"periods": ["morning_peak"]},
        )
        result = client.post("/transport/traffic/congestion")
        assert result.status_code == 200
