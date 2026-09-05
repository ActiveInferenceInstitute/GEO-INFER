"""
GEO-INFER-IOT

Internet of Things sensors and spatial web integration for the GEO-INFER framework.
This module provides comprehensive capabilities for ingesting, processing, and analyzing
IoT sensor data in spatial context, enabling real-time environmental monitoring and
Bayesian spatial inference at global scale.

Key components:
- IoT data ingestion from multiple protocols (MQTT, CoAP, LoRaWAN, HTTP)
- Real-time spatial data fusion with H3 indexing
- Bayesian spatial inference for converting point measurements to continuous surfaces
- Quality control and sensor network management
- Integration with environmental monitoring systems
"""

# Import available modules
import asyncio as asyncio
import logging
import numpy as np  # noqa: F401 -- `np` kept as public name for backward compatibility
import h3 as h3
from datetime import datetime as datetime, timedelta as timedelta
from typing import Any as Any, Dict as Dict, List as List, Optional as Optional, Set as Set, cast as cast
from geo_infer_iot.core.ingestion import IoTDataIngestion, RadiationMonitoringSystem
from geo_infer_iot.core.registry import SensorRegistry

logger = logging.getLogger(__name__)

# All public IoT components are required workspace modules. Import them directly
# so a partial installation fails at import time instead of exposing data-less
# stand-ins that appear usable but cannot process measurements.
from geo_infer_iot.core.spatial_fusion import SpatialDataFusion
from geo_infer_iot.core.quality_control import QualityController
from geo_infer_iot.api.sensor_api import SensorAPI
from geo_infer_iot.api.streaming_api import StreamingAPI
from geo_infer_iot.api.inference_api import BayesianInferenceAPI
from geo_infer_iot.core.inference import BayesianSpatialInference
from geo_infer_iot.models.sensor import Sensor, SensorNetwork
from geo_infer_iot.models.measurement import Measurement, MeasurementBatch
from geo_infer_iot.models.network import NetworkTopology
from geo_infer_iot.utils.calibration import SensorCalibration
from geo_infer_iot.utils.interpolation import SpatialInterpolation
from geo_infer_iot.utils.visualization import IoTVisualization


__version__ = "0.2.0"

__all__ = [
    # Core functionality (available)
    "IoTDataIngestion",
    "SensorRegistry",
    "RadiationMonitoringSystem",
    "GlobalMonitoringSystem",
    # High-level convenience classes
    "IoTSystem",
    "BayesianSpatialInference",
    "MultiModalFusion",
    "AdaptiveSampling",
    "PredictiveMaintenance",
    # Module components
    "SpatialDataFusion",
    "QualityController",
    "SensorAPI",
    "StreamingAPI",
    "BayesianInferenceAPI",
    "Sensor",
    "SensorNetwork",
    "Measurement",
    "MeasurementBatch",
    "NetworkTopology",
    "SensorCalibration",
    "SpatialInterpolation",
    "IoTVisualization",
]


# High-level convenience classes
from geo_infer_iot.core.systems import (
    AdaptiveSampling,
    GlobalMonitoringSystem,
    IoTSystem,
    MultiModalFusion,
    PredictiveMaintenance,
)
