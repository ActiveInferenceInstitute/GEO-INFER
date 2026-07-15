"""Regression tests for logistics visualization input contracts."""

import matplotlib
import pytest

matplotlib.use("Agg")

from geo_infer_log.utils.visualization import (
    create_interactive_map,
    plot_network,
    plot_route,
)


def test_plot_route_validates_coordinates_and_preserves_route_geometry() -> None:
    """Route plotting rejects invalid input and draws the supplied path."""
    figure = plot_route([(0.0, 0.0), (1.0, 1.0), (0.0, 2.0)], basemap=False)
    assert figure.axes
    line_collections = [
        collection
        for collection in figure.axes[0].collections
        if collection.__class__.__name__ == "LineCollection"
    ]
    assert any(len(path.vertices) == 3 for path in line_collections[0].get_paths())

    with pytest.raises(ValueError, match="at least two"):
        plot_route([(0.0, 0.0)], basemap=False)


def test_plot_network_rejects_unknown_highlight_nodes() -> None:
    """Network highlighting must reference nodes in the graph."""
    import networkx as nx

    graph = nx.path_graph(2)
    with pytest.raises(ValueError, match="unknown nodes"):
        plot_network(graph, highlight_path=[0, 3])


def test_create_interactive_map_validates_zoom() -> None:
    """Interactive map zoom remains within Folium's supported range."""
    with pytest.raises(ValueError, match="between 0 and 18"):
        create_interactive_map(zoom=19)
