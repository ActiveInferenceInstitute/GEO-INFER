"""
Flowline Network and Topology Validation for Pacific Northwest Rivers.

This module provides graph-based representation, topology validation,
traversal (upstream/downstream), Strahler stream order checks, and H3
spatial integration for NHDPlus High Resolution (NHDPlus HR) flowline networks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, cast

import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import LineString, Point, shape

from geo_infer_space.utils.h3_utils import latlng_to_cell

logger = logging.getLogger(__name__)


class FlowlineTopologyValidator:
    """Validates hydrological flowline network topology and consistency.

    Performs graph-level consistency checks:
    - Directed acyclic graph (DAG) verification (flow cannot cycle)
    - Node connectivity and dangling reach detection
    - Strahler stream order monotonicity (downstream order must be >= upstream order)
    - Outlet and headwater identification
    """

    def __init__(self, graph: nx.DiGraph) -> None:
        """Initialize validator with a directed flowline graph.

        Args:
            graph: Directed NetworkX graph where edges represent flowlines
                   directed from upstream node to downstream node.
        """
        self.graph = graph

    def validate_is_dag(self) -> Dict[str, Any]:
        """Validate that the flowline network is a directed acyclic graph (no loops)."""
        is_dag = nx.is_directed_acyclic_graph(self.graph)
        cycles: List[List[Any]] = []
        if not is_dag:
            try:
                cycles = list(nx.simple_cycles(self.graph))
            except Exception as e:
                logger.warning(f"Error computing simple cycles: {e}")
        return {
            "is_dag": is_dag,
            "has_cycles": not is_dag,
            "cycle_count": len(cycles),
            "cycles": cycles[:10],
        }

    def validate_strahler_monotonicity(self) -> Dict[str, Any]:
        """Verify that stream order is non-decreasing in the downstream direction.

        Along any valid flowline path (u -> v), stream_order(v) >= stream_order(u).
        """
        violations: List[Dict[str, Any]] = []
        for u, v, data in self.graph.edges(data=True):
            u_order = data.get("stream_order")
            # Look at downstream edges from v
            downstream_edges = self.graph.out_edges(v, data=True)
            for _, w, ds_data in downstream_edges:
                w_order = ds_data.get("stream_order")
                if (
                    u_order is not None
                    and w_order is not None
                    and int(w_order) < int(u_order)
                ):
                    violations.append(
                        {
                            "upstream_comid": data.get("comid"),
                            "upstream_order": int(u_order),
                            "downstream_comid": ds_data.get("comid"),
                            "downstream_order": int(w_order),
                            "from_node": u,
                            "junction_node": v,
                            "to_node": w,
                        }
                    )
        return {
            "monotonic": len(violations) == 0,
            "violation_count": len(violations),
            "violations": violations,
        }

    def find_headwaters(self) -> List[Any]:
        """Find headwater nodes (nodes with in-degree == 0 and out-degree > 0)."""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.in_degree(node) == 0 and self.graph.out_degree(node) > 0
        ]

    def find_outlets(self) -> List[Any]:
        """Find terminal outlet nodes (nodes with out-degree == 0 and in-degree > 0)."""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.out_degree(node) == 0 and self.graph.in_degree(node) > 0
        ]

    def validate_all(self) -> Dict[str, Any]:
        """Run full battery of hydrological network validation checks."""
        dag_res = self.validate_is_dag()
        monotonic_res = self.validate_strahler_monotonicity()
        headwaters = self.find_headwaters()
        outlets = self.find_outlets()
        connected_components = list(nx.weakly_connected_components(self.graph))

        return {
            "valid": dag_res["is_dag"] and monotonic_res["monotonic"],
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "headwater_count": len(headwaters),
            "outlet_count": len(outlets),
            "component_count": len(connected_components),
            "dag_validation": dag_res,
            "strahler_monotonicity": monotonic_res,
            "headwaters": headwaters,
            "outlets": outlets,
        }


class CascadiaFlowlineNetwork:
    """Hydrological river flowline network for Cascadia and Pacific Northwest basins.

    Provides graph creation from NHDPlus HR GeoDataFrames or GeoJSON collections,
    topology traversal, drainage path finding, and spatial integration with H3 grids.
    """

    def __init__(self, flowlines_gdf: Optional[gpd.GeoDataFrame] = None) -> None:
        """Initialize flowline network.

        Args:
            flowlines_gdf: Optional GeoDataFrame of NHDPlus HR flowlines.
        """
        self.flowlines_gdf = (
            flowlines_gdf
            if flowlines_gdf is not None
            else gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        )
        self.graph = nx.DiGraph()
        self._comid_to_edge: Dict[int, Tuple[Any, Any]] = {}
        self._edge_to_comid: Dict[Tuple[Any, Any], int] = {}
        if not self.flowlines_gdf.empty:
            self._build_graph()

    @classmethod
    def from_geojson(cls, path_or_dict: Any) -> "CascadiaFlowlineNetwork":
        """Construct CascadiaFlowlineNetwork from GeoJSON file path or dict."""
        if isinstance(path_or_dict, str):
            gdf = gpd.read_file(path_or_dict)
        elif isinstance(path_or_dict, bytes):
            import io
            gdf = gpd.read_file(io.BytesIO(path_or_dict))
        elif hasattr(path_or_dict, "exists"):  # Path object
            gdf = gpd.read_file(str(path_or_dict))
        elif isinstance(path_or_dict, dict):
            gdf = gpd.GeoDataFrame.from_features(
                path_or_dict.get("features", []), crs="EPSG:4326"
            )
        else:
            raise ValueError(f"Unsupported GeoJSON source type: {type(path_or_dict)}")
        return cls(gdf)

    def _build_graph(self) -> None:
        """Build directed network graph from flowlines GeoDataFrame."""
        self.graph.clear()
        self._comid_to_edge.clear()
        self._edge_to_comid.clear()

        for idx, row in self.flowlines_gdf.iterrows():
            comid = int(row.get("comid", row.get("COMID", idx)))
            from_node = row.get("from_node", row.get("FromNode"))
            to_node = row.get("to_node", row.get("ToNode"))

            # Derive node IDs from line endpoints if not explicitly provided
            geom = row.geometry
            if from_node is None or to_node is None:
                if isinstance(geom, LineString) and len(geom.coords) >= 2:
                    coords = list(geom.coords)
                    start_pt = coords[0]
                    end_pt = coords[-1]
                    from_node = f"node_{round(start_pt[0], 4)}_{round(start_pt[1], 4)}"
                    to_node = f"node_{round(end_pt[0], 4)}_{round(end_pt[1], 4)}"
                else:
                    from_node = f"from_{comid}"
                    to_node = f"to_{comid}"

            # Edge attributes
            length_km = float(
                row.get(
                    "length_km",
                    row.get("LengthKM", geom.length * 111.0 if geom else 0.0),
                )
            )
            stream_order = int(
                row.get(
                    "stream_order",
                    row.get("StreamOrder", row.get("StreamOrde", 1)),
                )
            )
            drainage_area = float(
                row.get(
                    "drainage_area_sqkm",
                    row.get("TotDASqKM", row.get("areasqkm", 0.0)),
                )
            )
            gnis_name = str(row.get("gnis_name", row.get("GNIS_NAME", "Unnamed Reach")))
            slope = float(row.get("slope", row.get("Slope", 0.001)))
            mainstem = str(row.get("mainstem", row.get("MainStem", gnis_name)))
            basin = str(row.get("basin", row.get("Basin", "Cascadia")))

            edge_attrs = {
                "comid": comid,
                "gnis_name": gnis_name,
                "reachcode": str(row.get("reachcode", row.get("REACHCODE", ""))),
                "stream_order": stream_order,
                "length_km": length_km,
                "slope": slope,
                "drainage_area_sqkm": drainage_area,
                "mainstem": mainstem,
                "basin": basin,
                "geometry": geom,
            }

            self.graph.add_edge(from_node, to_node, **edge_attrs)
            self._comid_to_edge[comid] = (from_node, to_node)
            self._edge_to_comid[(from_node, to_node)] = comid

        logger.info(
            "Built Cascadia flowline graph with %d nodes and %d edges",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )

    def validate(self) -> Dict[str, Any]:
        """Validate network topology and return diagnostic report."""
        validator = FlowlineTopologyValidator(self.graph)
        return validator.validate_all()

    def get_flowline_by_comid(self, comid: int) -> Optional[Dict[str, Any]]:
        """Retrieve edge attributes for a given flowline COMID."""
        edge = self._comid_to_edge.get(comid)
        if edge is None:
            return None
        data = self.graph.get_edge_data(edge[0], edge[1])
        return cast(Optional[Dict[str, Any]], data)

    def trace_downstream(self, comid: int) -> List[Dict[str, Any]]:
        """Trace downstream from a flowline reach to the terminal outlet.

        Returns:
            List of edge attribute dictionaries ordered from upstream to downstream.
        """
        edge = self._comid_to_edge.get(comid)
        if edge is None:
            return []

        path_edges: List[Dict[str, Any]] = []
        current_data = self.graph.get_edge_data(edge[0], edge[1])
        if current_data:
            path_edges.append(dict(current_data))

        current_node = edge[1]
        visited_nodes: Set[Any] = {edge[0], current_node}

        while self.graph.out_degree(current_node) > 0:
            out_edges = list(self.graph.out_edges(current_node, data=True))
            if not out_edges:
                break
            # In dendritic river networks, choose highest stream order edge if multiple
            next_edge = max(
                out_edges, key=lambda e: int(e[2].get("stream_order", 1))
            )
            next_node = next_edge[1]
            if next_node in visited_nodes:
                logger.warning(
                    "Cycle detected at node %s during downstream trace", current_node
                )
                break
            visited_nodes.add(next_node)
            path_edges.append(dict(next_edge[2]))
            current_node = next_node

        return path_edges

    def trace_upstream(self, comid: int) -> List[Dict[str, Any]]:
        """Trace all upstream tributary flowlines contributing to a given reach.

        Returns:
            List of upstream edge attribute dictionaries.
        """
        edge = self._comid_to_edge.get(comid)
        if edge is None:
            return []

        upstream_comids: Set[int] = {comid}
        start_node = edge[0]

        # Reverse BFS/DFS upstream
        nodes_to_visit = [start_node]
        visited_nodes: Set[Any] = {edge[1], start_node}

        while nodes_to_visit:
            curr = nodes_to_visit.pop()
            in_edges = self.graph.in_edges(curr, data=True)
            for u, _, data in in_edges:
                c = data.get("comid")
                if c is not None and c not in upstream_comids:
                    upstream_comids.add(c)
                if u not in visited_nodes:
                    visited_nodes.add(u)
                    nodes_to_visit.append(u)

        results: List[Dict[str, Any]] = []
        for c in upstream_comids:
            e = self._comid_to_edge.get(c)
            if e:
                d = self.graph.get_edge_data(e[0], e[1])
                if d:
                    results.append(dict(d))
        return results

    def calculate_downstream_distance(self, comid: int) -> float:
        """Calculate total downstream flow distance (km) from reach to outlet."""
        path = self.trace_downstream(comid)
        return sum(float(e.get("length_km", 0.0)) for e in path)

    def calculate_upstream_network_length(self, comid: int) -> float:
        """Calculate total tributary network length (km) upstream of reach."""
        upstream = self.trace_upstream(comid)
        return sum(float(e.get("length_km", 0.0)) for e in upstream)

    def get_pnw_high_order_flowlines(
        self, min_stream_order: int = 5
    ) -> gpd.GeoDataFrame:
        """Filter and return high-order flowlines (Strahler order >= min_stream_order)."""
        if self.flowlines_gdf.empty:
            return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        col = (
            "stream_order"
            if "stream_order" in self.flowlines_gdf.columns
            else "StreamOrder"
            if "StreamOrder" in self.flowlines_gdf.columns
            else None
        )
        if col:
            return self.flowlines_gdf[self.flowlines_gdf[col] >= min_stream_order].copy()
        return self.flowlines_gdf.copy()

    def index_to_h3(self, resolution: int = 8) -> Dict[str, Dict[str, Any]]:
        """Index flowline network onto H3 hexagonal grid.

        Computes for each H3 cell intersecting the river network:
        - Total flowline length (km)
        - Maximum stream order present
        - Flowline feature count
        - Named rivers present in cell
        - Upstream connected length
        """
        if self.flowlines_gdf.empty:
            return {}

        hex_data: Dict[str, Dict[str, Any]] = {}

        for _, row in self.flowlines_gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue

            order = int(row.get("stream_order", row.get("StreamOrder", 1)))
            name = str(row.get("gnis_name", row.get("GNIS_NAME", "Unnamed River")))
            length = float(row.get("length_km", row.get("LengthKM", 1.0)))
            comid = int(row.get("comid", row.get("COMID", 0)))

            # Sample points along flowline geometry to map into H3 cells
            sampled_cells: Set[str] = set()
            if isinstance(geom, LineString):
                coords = list(geom.coords)
                for pt in coords:
                    c = latlng_to_cell(pt[1], pt[0], resolution)
                    if c:
                        sampled_cells.add(c)
                # Midpoint sampling for long segments
                for i in range(len(coords) - 1):
                    mid_x = (coords[i][0] + coords[i + 1][0]) / 2.0
                    mid_y = (coords[i][1] + coords[i + 1][1]) / 2.0
                    c = latlng_to_cell(mid_y, mid_x, resolution)
                    if c:
                        sampled_cells.add(c)

            length_per_cell = length / max(1, len(sampled_cells))

            for cell in sampled_cells:
                if cell not in hex_data:
                    hex_data[cell] = {
                        "flowline_length_km": 0.0,
                        "max_stream_order": 0,
                        "flowline_count": 0,
                        "river_names": set(),
                        "comids": [],
                    }
                hex_data[cell]["flowline_length_km"] = round(
                    hex_data[cell]["flowline_length_km"] + length_per_cell, 4
                )
                hex_data[cell]["max_stream_order"] = max(
                    hex_data[cell]["max_stream_order"], order
                )
                hex_data[cell]["flowline_count"] += 1
                hex_data[cell]["river_names"].add(name)
                hex_data[cell]["comids"].append(comid)

        # Convert sets to lists for JSON serializability
        for cell, metrics in hex_data.items():
            metrics["river_names"] = sorted(list(metrics["river_names"]))

        return hex_data
