"""Core temporal analysis components."""

from geo_infer_time.core.analysis import TemporalAnalyzer
from geo_infer_time.core.forecasting import ForecastingEngine
from geo_infer_time.core.stream_processing import StreamProcessor
from geo_infer_time.core.interpolation import TemporalInterpolator
from geo_infer_time.core.event_detection import EventDetector
from geo_infer_time.core.statistics import TemporalStatistics
from geo_infer_time.core.visualization import TemporalVisualization

# Advanced forecasting (optional dependency)
try:
    from geo_infer_time.core.advanced_forecasting import AdvancedForecastingEngine
    __all__ = [
        "TemporalAnalyzer",
        "ForecastingEngine",
        "AdvancedForecastingEngine",
        "StreamProcessor",
        "TemporalInterpolator",
        "EventDetector",
        "TemporalStatistics",
        "TemporalVisualization",
    ]
except ImportError:
    __all__ = [
        "TemporalAnalyzer",
        "ForecastingEngine",
        "StreamProcessor",
        "TemporalInterpolator",
        "EventDetector",
        "TemporalStatistics",
        "TemporalVisualization",
    ]
