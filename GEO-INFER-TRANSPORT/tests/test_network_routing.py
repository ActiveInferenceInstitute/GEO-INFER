"""
Unit tests for TransportNetwork and RoutingEngine.
"""

import pytest
from geo_infer_transport.core.network import (
    TransportNetwork,
    NetworkNode,
    NetworkEdge,
    RoadClass
)
from geo_infer_transport.core.routing import (
    RoutingEngine,
    Route,
    RoutingAlgorithm
)


class TestTransportNetwork:
    """Test suite for TransportNetwork class."""
    
    @pytest.fixture
    def network(self):
        """Create a TransportNetwork instance."""
        return TransportNetwork(
            network_type="road",
            modes=["car", "bicycle"],
            crs="EPSG:4326"
        )
    
    @pytest.fixture
    def sample_edges(self):
        """Sample edge data for testing."""
        return [
            {"id": "e1", "from": "n1", "to": "n2", "road_class": "primary", "length_m": 1000, "speed_limit": 50},
            {"id": "e2", "from": "n2", "to": "n3", "road_class": "secondary", "length_m": 500, "speed_limit": 40},
            {"id": "e3", "from": "n3", "to": "n4", "road_class": "tertiary", "length_m": 800, "speed_limit": 30},
            {"id": "e4", "from": "n1", "to": "n3", "road_class": "primary", "length_m": 1200, "speed_limit": 60}
        ]
    
    def test_init_default(self):
        """Test default initialization."""
        network = TransportNetwork()
        assert network.network_type == "road"
        assert "car" in network.modes
    
    def test_build_from_edges(self, network, sample_edges):
        """Test building network from edges."""
        result = network.build_from_edges(sample_edges)
        
        assert result["nodes_created"] == 4
        assert result["edges_created"] == 4
    
    def test_analyze_connectivity_components(self, network, sample_edges):
        """Test connectivity analysis using components method."""
        network.build_from_edges(sample_edges)
        
        result = network.analyze_connectivity(method="components")
        
        assert result["node_count"] == 4
        assert "weakly_connected_components" in result
    
    def test_analyze_connectivity_reachability(self, network, sample_edges):
        """Test connectivity analysis using reachability."""
        network.build_from_edges(sample_edges)
        
        result = network.analyze_connectivity(
            method="reachability",
            origin="n1",
            destinations=["n3", "n4"]
        )
        
        assert result["origin"] == "n1"
        assert result["reachable_nodes"] > 0
    
    def test_calculate_centrality(self, network, sample_edges):
        """Test centrality calculation."""
        network.build_from_edges(sample_edges)
        
        result = network.calculate_centrality(
            centrality_type="betweenness",
            top_n=5
        )
        
        assert "top_nodes" in result
        assert len(result["top_nodes"]) <= 5
    
    def test_get_statistics(self, network, sample_edges):
        """Test getting network statistics."""
        network.build_from_edges(sample_edges)
        
        stats = network.get_statistics()
        
        assert stats["node_count"] == 4
        assert stats["edge_count"] > 0
        assert "total_length_km" in stats
    
    def test_get_subgraph(self, network, sample_edges):
        """Test extracting subgraph."""
        network.build_from_edges(sample_edges)
        
        subgraph = network.get_subgraph(nodes=["n1", "n2", "n3"])
        
        assert len(subgraph._nodes) == 3


class TestRoutingEngine:
    """Test suite for RoutingEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create a RoutingEngine instance."""
        return RoutingEngine(
            algorithm="dijkstra",
            modes=["car"],
            real_time_traffic=False
        )
    
    @pytest.fixture
    def network_with_engine(self, engine):
        """Create a network and attach to engine."""
        network = TransportNetwork()
        edges = [
            {"id": "e1", "from": "n1", "to": "n2", "road_class": "primary", "length_m": 1000, "speed_limit": 50},
            {"id": "e2", "from": "n2", "to": "n3", "road_class": "secondary", "length_m": 500, "speed_limit": 40},
            {"id": "e3", "from": "n1", "to": "n3", "road_class": "tertiary", "length_m": 1800, "speed_limit": 30}
        ]
        network.build_from_edges(edges)
        engine.set_network(network)
        return engine
    
    def test_init_default(self):
        """Test default initialization."""
        engine = RoutingEngine()
        assert engine.algorithm == RoutingAlgorithm.DIJKSTRA
    
    def test_route_without_network(self, engine):
        """Test routing without network uses estimates."""
        route = engine.route(
            origin={"id": "o", "lat": 34.0, "lon": -118.0},
            destination={"id": "d", "lat": 34.1, "lon": -118.1}
        )
        
        assert isinstance(route, Route)
        assert route.total_distance_m > 0
    
    def test_route_with_network(self, network_with_engine):
        """Test routing with network."""
        route = network_with_engine.route(
            origin={"node_id": "n1"},
            destination={"node_id": "n3"}
        )
        
        assert len(route.path) >= 2
        assert route.path[0] == "n1"
        assert route.path[-1] == "n3"
    
    def test_optimize_route(self, engine):
        """Test route optimization through waypoints."""
        waypoints = [
            {"id": "wp1", "lat": 34.0, "lon": -118.0},
            {"id": "wp2", "lat": 34.1, "lon": -118.1},
            {"id": "wp3", "lat": 34.05, "lon": -118.15}
        ]
        
        result = engine.optimize_route(
            waypoints=waypoints,
            constraints={},
            objective="minimize_time"
        )
        
        assert "optimized_order" in result
        assert len(result["optimized_order"]) == 3
    
    def test_calculate_matrix(self, engine):
        """Test OD matrix calculation."""
        origins = [
            {"id": "o1", "lat": 34.0, "lon": -118.0},
            {"id": "o2", "lat": 34.1, "lon": -118.1}
        ]
        destinations = [
            {"id": "d1", "lat": 34.2, "lon": -118.0},
            {"id": "d2", "lat": 34.0, "lon": -118.2}
        ]
        
        result = engine.calculate_matrix(origins, destinations)
        
        assert result["shape"] == [2, 2]
        assert len(result["matrix"]) == 2
        assert len(result["matrix"][0]) == 2
    
    def test_find_alternatives(self, network_with_engine):
        """Test finding alternative routes."""
        alternatives = network_with_engine.find_alternatives(
            origin={"node_id": "n1"},
            destination={"node_id": "n3"},
            count=2
        )
        
        assert len(alternatives) >= 1
        assert all(isinstance(r, Route) for r in alternatives)
    
    def test_update_traffic(self, engine):
        """Test updating traffic data."""
        traffic_data = {"e1": 1.5, "e2": 1.2}
        
        engine.update_traffic(traffic_data)
        
        assert engine._traffic_data["e1"] == 1.5


    def test_route_source_network_vs_fallback(self, network_with_engine):
        """route_source distinguishes network routes from estimates."""
        network_route = network_with_engine.route(
            origin={"node_id": "n1"},
            destination={"node_id": "n3"},
        )
        assert network_route.route_source == "network"

        # A fresh engine without any network falls back to estimates.
        fallback_route = RoutingEngine().route(
            origin={"id": "o", "lat": 34.0, "lon": -118.0},
            destination={"id": "d", "lat": 34.1, "lon": -118.1},
        )
        assert fallback_route.route_source == "estimated_fallback"

    def test_route_uses_traffic_adjusted_weights(self):
        """With adjusted weights present, route() routes on them."""
        network = TransportNetwork()
        network.build_from_edges([
            {"id": "e1", "from": "n1", "to": "n2", "length_m": 1000, "speed_limit": 50},
            {"id": "e2", "from": "n2", "to": "n3", "length_m": 500, "speed_limit": 40},
            {"id": "e3", "from": "n1", "to": "n3", "length_m": 1800, "speed_limit": 30},
        ])
        engine = RoutingEngine(real_time_traffic=True)
        engine.set_network(network)

        # Unadjusted: n1->n2->n3 (117 s) beats the direct 1800 m edge (216 s).
        base_route = engine.route(
            origin={"node_id": "n1"}, destination={"node_id": "n3"}, optimization="time"
        )
        assert base_route.path == ["n1", "n2", "n3"]

        # Slowing e1 by 10x must push the route onto the direct edge, which
        # only happens when route() weights on travel_time_adjusted.
        engine.update_traffic({"e1": 10.0})
        adjusted_route = engine.route(
            origin={"node_id": "n1"}, destination={"node_id": "n3"}, optimization="time"
        )
        assert adjusted_route.path == ["n1", "n3"]
        assert adjusted_route.route_source == "network"


class TestNetworkNode:
    """Test suite for NetworkNode dataclass."""

    def test_create_node(self):
        """Test creating a network node."""
        node = NetworkNode(
            node_id="node_1",
            location={"lat": 34.0, "lon": -118.0}
        )

        assert node.node_id == "node_1"
        assert node.node_type == "intersection"

class TestNetworkEdge:
    """Test suite for NetworkEdge dataclass."""
    
    def test_create_edge(self):
        """Test creating a network edge."""
        edge = NetworkEdge(
            edge_id="edge_1",
            from_node="n1",
            to_node="n2",
            road_class=RoadClass.PRIMARY,
            length_m=1000
        )
        
        assert edge.edge_id == "edge_1"
        assert edge.speed_limit_kmh == 50
        assert edge.lanes == 1


class TestRoute:
    """Test suite for Route dataclass."""
    
    def test_create_route(self):
        """Test creating a route."""
        route = Route(
            route_id="route_1",
            origin="n1",
            destination="n3",
            path=["n1", "n2", "n3"],
            total_distance_m=1500,
            total_time_s=120
        )
        
        assert route.route_id == "route_1"
        assert len(route.path) == 3
        assert route.alternatives == []

