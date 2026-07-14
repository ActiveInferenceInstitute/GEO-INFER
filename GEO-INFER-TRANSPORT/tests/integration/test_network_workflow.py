"""Integration coverage for deterministic transport network construction."""

from geo_infer_transport.core.network import TransportNetwork


def test_network_build_and_statistics_are_consistent() -> None:
    """Build a two-edge network and validate its node and edge statistics."""
    network = TransportNetwork(network_type="road", modes=["car"])
    result = network.build_from_edges(
        [
            {"id": "e1", "from": "a", "to": "b", "length_m": 1000, "speed_limit": 50},
            {"id": "e2", "from": "b", "to": "c", "length_m": 500, "speed_limit": 25},
        ],
        nodes=[{"id": "a"}, {"id": "b"}, {"id": "c"}],
    )
    stats = network.get_statistics()

    assert result["edges_created"] == 2
    assert stats["node_count"] == 3
    assert stats["edge_count"] == 4
