"""Regression tests for economic visualization contracts."""

from pathlib import Path

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")

from geo_infer_econ.utils.visualizer import ResultsVisualizer


def test_indicator_plot_validates_data_and_creates_nested_output(
    tmp_path: Path,
) -> None:
    """Indicator plots validate finite columns and save to nested paths."""
    output_file = tmp_path / "nested" / "indicators.png"
    figure = ResultsVisualizer().plot_economic_indicators(
        pd.DataFrame({"gdp": [1.0, 2.0]}), ["gdp"], save_path=output_file
    )

    assert figure.axes
    assert output_file.exists()

    with pytest.raises(ValueError, match="missing required"):
        ResultsVisualizer().plot_economic_indicators(
            pd.DataFrame({"x": [1.0]}), ["gdp"]
        )


def test_model_diagnostics_accepts_missing_optional_metrics() -> None:
    """Diagnostics render without formatting absent metrics as numbers."""
    figure = ResultsVisualizer().create_model_diagnostics_plot(
        {"residuals": [0.1, -0.2, 0.05]}
    )
    assert len(figure.axes) == 4


def test_dashboard_writes_requested_output(tmp_path: Path) -> None:
    """The dashboard output argument writes the generated HTML."""
    output_file = tmp_path / "nested" / "dashboard.html"
    html = ResultsVisualizer().create_interactive_dashboard(
        {"indicator": [1, 2]}, output_path=output_file
    )

    assert output_file.read_text(encoding="utf-8") == html
