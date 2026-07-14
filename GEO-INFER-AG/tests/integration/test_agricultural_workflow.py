"""Integration coverage for deterministic agricultural seasonal analysis."""

import numpy as np
import pandas as pd

from geo_infer_ag.core.seasonal_analysis import SeasonalAnalysis


def test_seasonal_analysis_produces_documented_result() -> None:
    """Detect a finite growing-season result from a deterministic NDVI series."""
    index = pd.date_range("2024-01-01", periods=90, freq="D")
    values = pd.Series(
        np.where((np.arange(90) >= 20) & (np.arange(90) <= 70), 0.8, 0.1),
        index=index,
        name="ndvi",
    )

    result = SeasonalAnalysis().detect_growing_season(
        values, threshold=0.3, smoothing_window=1, min_length_days=30
    )

    assert result["variable"] == "ndvi"
    assert result["seasons"]
    assert result["seasons"][0]["length_days"] >= 30
