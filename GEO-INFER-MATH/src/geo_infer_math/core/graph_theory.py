"""
Graph Theory Module

This module provides mathematical graph operations and algorithms
for analyzing spatial networks and connectivity in geospatial data.
"""

import numpy as np
from typing import Union, List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass
from collections import defaultdict, deque
import logging
import heapq

logger = logging.getLogger(__name__)

@dataclass
class GraphNode:
    """Representation of a graph node."""
    id: Any
    coordinates: Optional[np.ndarray] = None
    attributes: Dict[str, Any] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

@dataclass
class GraphEdge:
    """Representation of a graph edge."""
    source: Any
    target: Any
    weight: float = 1.0
    attributes: Dict[str, Any] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

class SpatialGraph:
    """Spatial graph representation with geospatial operations."""

    def __init__(self, directed: bool = False):
        """
        Initialize spatial graph.

        Args:
            directed: Whether the graph is directed
        """
        self.directed = directed
        self.nodes = {}  # node_id -> GraphNode
        self.edges = {}  # (source, target) -> GraphEdge
        self.adjacency_list = defaultdict(list)  # node_id -> list of connected nodes
        self.weights = {}  # (source, target) -> weight

    def add_node(self, node_id: Any,
                coordinates: Optional[np.ndarray] = None,
                **attributes) -> None:
        """
        Add a node to the graph.

        Args:
            node_id: Unique identifier for the node
            coordinates: Spatial coordinates of the node
            **attributes: Additional node attributes
        """
        self.nodes[node_id] = GraphNode(
            id=node_id,
            coordinates=coordinates,
            attributes=attributes
        )

    def add_edge(self, source: Any, target: Any,
                weight: float = 1.0, **attributes) -> None:
        """
        Add an edge to the graph.

        Args:
            source: Source node ID
            target: Target node ID
            weight: Edge weight
            **attributes: Additional edge attributes
        """
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("Both source and target nodes must exist in the graph")

        edge = GraphEdge(source=source, target=target, weight=weight, attributes=attributes)
        self.edges[(source, target)] = edge

        self.adjacency_list[source].append(target)
        self.weights[(source, target)] = weight

        if not self.directed:
            # Add reverse edge for undirected graph
            self.edges[(target, source)] = GraphEdge(
                source=target, target=source, weight=weight, attributes=attributes
            )
            self.adjacency_list[target].append(source)
            self.weights[(target, source)] = weight

    def remove_node(self, node_id: Any) -> None:
        """
        Remove a node and all its edges from the graph.

        Args:
            node_id: Node ID to remove
        """
        if node_id not in self.nodes:
            return

        # Remove all edges connected to this node
        edges_to_remove = []
        for (source, target), edge in self.edges.items():
            if source == node_id or target == node_id:
                edges_to_remove.append((source, target))

        for edge_key in edges_to_remove:
            del self.edges[edge_key]
            if edge_key in self.weights:
                del self.weights[edge_key]

        # Remove from adjacency list
        if node_id in self.adjacency_list:
            del self.adjacency_list[node_id]

        # Remove node
        del self.nodes[node_id]

        # Clean up adjacency lists of other nodes
        for neighbors in self.adjacency_list.values():
            if node_id in neighbors:
                neighbors.remove(node_id)

    def get_neighbors(self, node_id: Any) -> List[Any]:
        """Get list of neighboring nodes."""
        return self.adjacency_list.get(node_id, [])

    def get_edge_weight(self, source: Any, target: Any) -> Optional[float]:
        """Get weight of edge between two nodes."""
        return self.weights.get((source, target), None)

    def shortest_path(self, start: Any, end: Any,
                     algorithm: str = 'dijkstra') -> Tuple[List[Any], float]:
        """
        Find shortest path between two nodes.

        Args:
            start: Starting node ID
            end: Ending node ID
            algorithm: Algorithm to use ('dijkstra', 'bellman_ford')

        Returns:
            Tuple of (path, total_distance)
        """
        if algorithm == 'dijkstra':
            return self._dijkstra(start, end)
        elif algorithm == 'bellman_ford':
            return self._bellman_ford(start, end)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def _dijkstra(self, start: Any, end: Any) -> Tuple[List[Any], float]:
        """Dijkstra's shortest path algorithm."""
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous = {node: None for node in self.nodes}

        # Priority queue: (distance, node)
        pq = [(0, start)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_distance > distances[current_node]:
                continue

            if current_node == end:
                break

            for neighbor in self.get_neighbors(current_node):
                weight = self.get_edge_weight(current_node, neighbor)
                if weight is None:
                    continue

                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        # Reconstruct path
        if distances[end] == float('inf'):
            return [], float('inf')  # No path found

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return path, distances[end]

    def _bellman_ford(self, start: Any, end: Any) -> Tuple[List[Any], float]:
        """Bellman-Ford algorithm for shortest path."""
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous = {node: None for node in self.nodes}

        # Relax edges |V| - 1 times
        for _ in range(len(self.nodes) - 1):
            for (source, target), edge in self.edges.items():
                if distances[source] != float('inf'):
                    new_distance = distances[source] + edge.weight
                    if new_distance < distances[target]:
                        distances[target] = new_distance
                        previous[target] = source

        # Reconstruct path
        if distances[end] == float('inf'):
            return [], float('inf')

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return path, distances[end]

    def minimum_spanning_tree(self, algorithm: str = 'kruskal') -> 'SpatialGraph':
        """
        Compute minimum spanning tree of the graph.

        Args:
            algorithm: Algorithm to use ('kruskal', 'prim')

        Returns:
            Minimum spanning tree as a new SpatialGraph
        """
        if algorithm == 'kruskal':
            return self._kruskal_mst()
        elif algorithm == 'prim':
            return self._prim_mst()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def _kruskal_mst(self) -> 'SpatialGraph':
        """Kruskal's algorithm for minimum spanning tree."""
        # Sort edges by weight
        sorted_edges = sorted(self.edges.values(), key=lambda x: x.weight)

        # Initialize MST
        mst = SpatialGraph(directed=False)

        # Add all nodes to MST
        for node_id, node in self.nodes.items():
            mst.add_node(node_id, node.coordinates, **node.attributes)

        # Union-Find structure
        parent = {node_id: node_id for node_id in self.nodes}

        def find(node):
            if parent[node] != node:
                parent[node] = find(parent[node])
            return parent[node]

        def union(node1, node2):
            root1 = find(node1)
            root2 = find(node2)
            if root1 != root2:
                parent[root1] = root2
                return True
            return False

        # Add edges to MST if they don't create cycles
        for edge in sorted_edges:
            if union(edge.source, edge.target):
                mst.add_edge(edge.source, edge.target, edge.weight, **edge.attributes)

        return mst

    def _prim_mst(self) -> 'SpatialGraph':
        """Prim's algorithm for minimum spanning tree."""
        if not self.nodes:
            return SpatialGraph(directed=False)

        start_node = next(iter(self.nodes.keys()))

        # Initialize MST
        mst = SpatialGraph(directed=False)

        # Add all nodes to MST
        for node_id, node in self.nodes.items():
            mst.add_node(node_id, node.coordinates, **node.attributes)

        # Track visited nodes
        visited = set([start_node])

        # Priority queue for edges: (weight, source, target)
        edge_queue = []

        # Add edges from start node
        for neighbor in self.get_neighbors(start_node):
            weight = self.get_edge_weight(start_node, neighbor)
            heapq.heappush(edge_queue, (weight, start_node, neighbor))

        while edge_queue and len(visited) < len(self.nodes):
            weight, source, target = heapq.heappop(edge_queue)

            if target in visited:
                continue

            # Add edge to MST
            mst.add_edge(source, target, weight)
            visited.add(target)

            # Add new edges from target
            for neighbor in self.get_neighbors(target):
                if neighbor not in visited:
                    weight = self.get_edge_weight(target, neighbor)
                    heapq.heappush(edge_queue, (weight, target, neighbor))

        return mst

    def connected_components(self) -> List[List[Any]]:
        """
        Find connected components in the graph.

        Returns:
            List of connected component node lists
        """
        visited = set()
        components = []

        for node_id in self.nodes:
            if node_id not in visited:
                # Start DFS/BFS from this node
                component = []
                queue = deque([node_id])

                while queue:
                    current = queue.popleft()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)

                        # Add unvisited neighbors
                        for neighbor in self.get_neighbors(current):
                            if neighbor not in visited:
                                queue.append(neighbor)

                components.append(component)

        return components

    def centrality_measures(self) -> Dict[str, Dict[Any, float]]:
        """
        Calculate various centrality measures for nodes.

        Returns:
            Dictionary of centrality measures
        """
        centrality = {
            'degree': self._degree_centrality(),
            'betweenness': self._betweenness_centrality(),
            'closeness': self._closeness_centrality()
        }

        return centrality

    def _degree_centrality(self) -> Dict[Any, float]:
        """Calculate degree centrality."""
        centrality = {}
        n_nodes = len(self.nodes)

        for node_id in self.nodes:
            degree = len(self.get_neighbors(node_id))
            centrality[node_id] = degree / (n_nodes - 1) if n_nodes > 1 else 0

        return centrality

    def _betweenness_centrality(self) -> Dict[Any, float]:
        """Calculate betweenness centrality."""
        centrality = {node: 0.0 for node in self.nodes}

        for source in self.nodes:
            # Run BFS from source
            distances = {node: -1 for node in self.nodes}
            distances[source] = 0
            predecessors = {node: [] for node in self.nodes}
            sigma = {node: 0 for node in self.nodes}
            sigma[source] = 1

            queue = deque([source])

            while queue:
                current = queue.popleft()

                for neighbor in self.get_neighbors(current):
                    if distances[neighbor] == -1:
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)

                    if distances[neighbor] == distances[current] + 1:
                        sigma[neighbor] += sigma[current]
                        predecessors[neighbor].append(current)

            # Calculate dependency
            delta = {node: 0.0 for node in self.nodes}

            # Process nodes in reverse order of distance
            nodes_by_distance = sorted(self.nodes.keys(),
                                     key=lambda x: distances[x],
                                     reverse=True)

            for node in nodes_by_distance:
                for predecessor in predecessors[node]:
                    delta[predecessor] += (sigma[predecessor] / sigma[node]) * (1 + delta[node])

                if node != source:
                    centrality[node] += delta[node]

        # Normalize
        n_nodes = len(self.nodes)
        if n_nodes > 2:
            for node in centrality:
                centrality[node] /= ((n_nodes - 1) * (n_nodes - 2)) / 2

        return centrality

    def _closeness_centrality(self) -> Dict[Any, float]:
        """Calculate closeness centrality."""
        centrality = {}

        for node in self.nodes:
            total_distance = 0
            reachable_nodes = 0

            for target in self.nodes:
                if node != target:
                    _, distance = self.shortest_path(node, target)
                    if distance != float('inf'):
                        total_distance += distance
                        reachable_nodes += 1

            if reachable_nodes > 0:
                centrality[node] = reachable_nodes / total_distance
            else:
                centrality[node] = 0.0

        return centrality

    def spatial_network_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive spatial network analysis.

        Returns:
            Dictionary of network analysis results
        """
        analysis = {}

        # Basic network statistics
        analysis['n_nodes'] = len(self.nodes)
        analysis['n_edges'] = len(self.edges)
        analysis['density'] = len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1) / 2) if len(self.nodes) > 1 else 0

        # Connected components
        components = self.connected_components()
        analysis['n_components'] = len(components)
        analysis['components'] = components
        analysis['largest_component_size'] = max(len(comp) for comp in components) if components else 0

        # Centrality measures
        analysis['centrality'] = self.centrality_measures()

        # Minimum spanning tree
        if not self.directed:
            mst = self.minimum_spanning_tree()
            analysis['mst_edges'] = len(mst.edges)
            analysis['mst_total_weight'] = sum(edge.weight for edge in mst.edges.values())

        return analysis

class NetworkFlow:
    """Network flow algorithms for spatial networks."""

    @staticmethod
    def max_flow(graph: SpatialGraph, source: Any, sink: Any) -> Tuple[float, Dict[Tuple[Any, Any], float]]:
        """
        Calculate maximum flow from source to sink using Ford-Fulkerson algorithm.

        Args:
            graph: Input graph
            source: Source node
            sink: Sink node

        Returns:
            Tuple of (max_flow_value, flow_along_each_edge)
        """
        # Create residual graph
        residual = NetworkFlow._create_residual_graph(graph)

        # Initialize flow
        flow = {(u, v): 0 for (u, v) in graph.edges}
        max_flow = 0

        while True:
            # Find augmenting path
            path = NetworkFlow._find_augmenting_path(residual, source, sink)
            if not path:
                break

            # Find minimum residual capacity along path
            path_flow = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if residual.get((u, v), 0) < path_flow:
                    path_flow = residual[(u, v)]

            # Update residual capacities
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                residual[(u, v)] -= path_flow
                residual[(v, u)] += path_flow

                # Update flow
                if (u, v) in flow:
                    flow[(u, v)] += path_flow
                else:
                    flow[(v, u)] -= path_flow

            max_flow += path_flow

        return max_flow, flow

    @staticmethod
    def _create_residual_graph(graph: SpatialGraph) -> Dict[Tuple[Any, Any], float]:
        """Create residual graph for max flow algorithm."""
        residual = {}

        # Add forward edges
        for (u, v), edge in graph.edges.items():
            residual[(u, v)] = edge.weight
            residual[(v, u)] = 0  # Reverse edge initially 0

        return residual

    @staticmethod
    def _find_augmenting_path(residual: Dict[Tuple[Any, Any], float],
                            source: Any, sink: Any) -> Optional[List[Any]]:
        """Find augmenting path using BFS."""
        visited = set()
        parent = {}

        queue = deque([source])
        visited.add(source)

        while queue:
            current = queue.popleft()

            for neighbor in residual:
                u, v = neighbor
                if u == current and residual[neighbor] > 0 and v not in visited:
                    queue.append(v)
                    visited.add(v)
                    parent[v] = current

                    if v == sink:
                        # Reconstruct path
                        path = [sink]
                        while path[-1] != source:
                            path.append(parent[path[-1]])
                        path.reverse()
                        return path

        return None

__all__ = [
    "GraphNode",
    "GraphEdge",
    "SpatialGraph",
    "NetworkFlow"
]
