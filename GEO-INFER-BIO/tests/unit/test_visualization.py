"""Tests for BIO visualization utilities."""

import pandas as pd
import pytest
from geo_infer_bio.utils.visualization import BioVisualizer


class TestBioVisualizer:
    """Tests for the bio visualizer."""

    def test_initialization(self) -> None:
        viz = BioVisualizer()
        assert viz is not None

    def test_spatial_plot_returns_figure_and_creates_nested_output(
        self, tmp_path
    ) -> None:
        viz = BioVisualizer()
        data = pd.DataFrame(
            {
                "longitude": [-124.0, -123.9],
                "latitude": [41.7, 41.8],
            }
        )
        output = tmp_path / "nested" / "spatial.png"
        figure = viz.plot_spatial_distribution(data, output_path=str(output))
        assert figure is not None
        assert output.exists()

    def test_spatial_plot_validates_coordinates(self) -> None:
        viz = BioVisualizer()
        with pytest.raises(ValueError, match="required columns"):
            viz.plot_spatial_distribution(pd.DataFrame({"latitude": [1.0]}))

    def test_gc_plot_validates_and_returns_figure(self) -> None:
        viz = BioVisualizer()
        data = pd.DataFrame(
            {
                "longitude": [-124.0, -123.9],
                "latitude": [41.7, 41.8],
                "gc_content": [0.4, 0.6],
            }
        )
        figure = viz.plot_gc_distribution(data)
        assert figure is not None
