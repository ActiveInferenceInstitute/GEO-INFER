"""
GEO-INFER-TIME: Temporal Methods for Geospatial Data

This module provides comprehensive temporal analysis, time series processing,
forecasting, and spatio-temporal data fusion for dynamic geospatial applications.
"""

__version__ = "0.2.0"
__author__ = "GEO-INFER Development Team"

from geo_infer_time.core.analysis import TemporalAnalyzer
from geo_infer_time.core.forecasting import ForecastingEngine
from geo_infer_time.core.stream_processing import (
    StreamProcessor,
    StreamIngestAdapter,
    ReplayIngestAdapter,
    WebSocketIngestAdapter,
    KafkaIngestAdapter,
)
from geo_infer_time.core.interpolation import TemporalInterpolator
from geo_infer_time.core.event_detection import EventDetector
from geo_infer_time.core.statistics import TemporalStatistics
from geo_infer_time.core.visualization import TemporalVisualization
from geo_infer_time.models.timeseries import TimeSeries

from geo_infer_time.core.advanced_forecasting import AdvancedForecastingEngine
from geo_infer_time import db, io, utils

__all__ = [
    "TemporalAnalyzer",
    "ForecastingEngine",
    "StreamProcessor",
    "StreamIngestAdapter",
    "ReplayIngestAdapter",
    "WebSocketIngestAdapter",
    "KafkaIngestAdapter",
    "TemporalInterpolator",
    "EventDetector",
    "TemporalStatistics",
    "TemporalVisualization",
    "TimeSeries",
    "AdvancedForecastingEngine",
    "db",
    "io",
    "utils",
]
