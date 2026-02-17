"""
GEO-INFER-TIME: Temporal Methods for Geospatial Data

This module provides comprehensive temporal analysis, time series processing,
forecasting, and spatio-temporal data fusion for dynamic geospatial applications.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Development Team"

from geo_infer_time.core.analysis import TemporalAnalyzer
from geo_infer_time.core.forecasting import ForecastingEngine
from geo_infer_time.core.stream_processing import StreamProcessor
from geo_infer_time.core.interpolation import TemporalInterpolator
from geo_infer_time.core.event_detection import EventDetector
from geo_infer_time.core.statistics import TemporalStatistics
from geo_infer_time.core.visualization import TemporalVisualization
from geo_infer_time.models.timeseries import TimeSeries

try:
    from geo_infer_time.core.advanced_forecasting import AdvancedForecastingEngine
except ImportError:
    AdvancedForecastingEngine = None  # type: ignore[assignment,misc]

__all__ = [
    "TemporalAnalyzer",
    "ForecastingEngine",
    "StreamProcessor",
    "TemporalInterpolator",
    "EventDetector",
    "TemporalStatistics",
    "TemporalVisualization",
    "TimeSeries",
    "AdvancedForecastingEngine",
]



