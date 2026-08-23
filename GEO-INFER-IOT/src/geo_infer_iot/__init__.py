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
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, cast, Union
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
from geo_infer_iot.models.sensor import Sensor, SensorNetwork
from geo_infer_iot.models.measurement import Measurement, MeasurementBatch
from geo_infer_iot.models.network import NetworkTopology
from geo_infer_iot.utils.calibration import SensorCalibration
from geo_infer_iot.utils.interpolation import SpatialInterpolation
from geo_infer_iot.utils.visualization import IoTVisualization


__version__ = "0.1.0"

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
class IoTSystem:
    """
    High-level interface for IoT sensor systems integration.

    This class provides a comprehensive interface for setting up and managing
    IoT sensor networks with spatial analysis, quality control, and real-time
    processing capabilities.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.system_id = f"iot_system_{id(self)}"
        self.start_time = datetime.now()

        # Core components
        self.registry = SensorRegistry(config)
        self.ingestion = IoTDataIngestion(self.registry, config)

        # Enhanced components (initialized as needed)
        self.fusion: Optional[Any] = None
        self.quality_controller: Optional[Any] = None
        self.spatial_inference: Optional[Any] = None
        self.visualization: Optional[Any] = None
        self.calibration: Optional[SensorCalibration] = None

        # System state
        self.is_initialized = False
        self.is_processing = False
        self.error_count = 0
        self.last_error: Optional[str] = None

        # Performance monitoring
        self.metrics: Dict[str, Any] = {
            "measurements_processed": 0,
            "networks_registered": 0,
            "errors_encountered": 0,
            "uptime_seconds": 0,
            "last_update": datetime.now(),
        }

        logger.info(f"IoTSystem initialized with ID: {self.system_id}")

    def initialize(self, auto_start_processing: bool = False) -> Dict[str, Any]:
        """
        Initialize the IoT system with all components.

        Args:
            auto_start_processing: Whether to automatically start processing

        Returns:
            Dictionary with initialization results
        """
        try:
            # Initialize core components
            self._initialize_components()

            # Validate system configuration
            validation_result = self._validate_system()

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "errors": validation_result["errors"],
                    "message": "System initialization failed due to configuration errors",
                }

            # Start processing if requested
            if auto_start_processing:
                self.start_processing()

            self.is_initialized = True

            return {
                "success": True,
                "system_id": self.system_id,
                "components_initialized": len(
                    [
                        c
                        for c in [
                            self.fusion,
                            self.quality_controller,
                            self.spatial_inference,
                            self.visualization,
                            self.calibration,
                        ]
                        if c is not None
                    ]
                ),
                "networks_registered": len(self.registry.networks),
                "sensors_registered": len(self.registry.sensors),
                "processing_active": self.is_processing,
                "initialization_time": (
                    datetime.now() - self.start_time
                ).total_seconds(),
            }

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"System initialization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "initialization_time": (
                    datetime.now() - self.start_time
                ).total_seconds(),
            }

    def _initialize_components(self) -> None:
        """Initialize all system components."""
        # Initialize spatial fusion if available
        try:
            from geo_infer_iot.core.spatial_fusion import SpatialDataFusion

            self.fusion = SpatialDataFusion(self.config)
        except ImportError:
            logger.warning("SpatialDataFusion not available")

        # Initialize quality controller if available
        try:
            from geo_infer_iot.core.quality_control import QualityController

            self.quality_controller = QualityController(self.config)
        except ImportError:
            logger.warning("QualityController not available")

        # Initialize visualization if available
        try:
            from geo_infer_iot.utils.visualization import IoTVisualization

            self.visualization = IoTVisualization(self.config)
        except ImportError:
            logger.warning("IoTVisualization not available")

        # Initialize calibration if available
        try:
            from geo_infer_iot.utils.calibration import SensorCalibration

            self.calibration = SensorCalibration(self.config)
        except ImportError:
            logger.warning("SensorCalibration not available")

    def _validate_system(self) -> Dict[str, Any]:
        """Validate system configuration and dependencies."""
        errors: List[str] = []
        warnings: List[str] = []

        # Check if at least one sensor network is configured
        if not self.registry.networks:
            warnings.append("No sensor networks registered")

        # Check if basic ingestion is configured
        if not self.config.get("protocols", {}).get("mqtt", {}).get("enabled", False):
            warnings.append("MQTT protocol not enabled - some features may not work")

        # Check if required dependencies are available
        if self.fusion is None:
            warnings.append("Spatial fusion not available")

        if self.quality_controller is None:
            warnings.append("Quality control not available")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def register_network(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Register a new sensor network.

        Args:
            **kwargs: Network registration parameters

        Returns:
            Dictionary with registration results
        """
        try:
            network = self.registry.register_network(**kwargs)
            self.metrics["networks_registered"] = cast(int, self.metrics["networks_registered"]) + 1

            return {
                "success": True,
                "network_id": network.network_id,
                "network_name": network.name,
                "total_networks": len(self.registry.networks),
            }

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Network registration failed: {e}")
            return {"success": False, "error": str(e)}

    def register_sensor(self, sensor_data: Dict) -> Dict[str, Any]:
        """
        Register a new sensor.

        Args:
            sensor_data: Sensor registration data

        Returns:
            Dictionary with registration results
        """
        try:
            sensor = self.registry.register_sensor(sensor_data)

            # Auto-setup spatial inference for the sensor's variable
            if self.spatial_inference is None:
                self.spatial_inference = BayesianSpatialInference(
                    variable=sensor_data.get("sensor_type", "unknown"),
                    spatial_resolution=self.config.get("spatial", {}).get(
                        "default_resolution", 8
                    ),
                    temporal_window="1h",
                    config=self.config,
                )

            return {
                "success": True,
                "sensor_id": sensor.sensor_id,
                "network_id": sensor.network_id,
                "total_sensors": len(self.registry.sensors),
            }

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Sensor registration failed: {e}")
            return {"success": False, "error": str(e)}

    def start_processing(self) -> Dict:
        """
        Start real-time data processing.

        Returns:
            Dictionary with processing start results
        """
        try:
            if self.is_processing:
                return {
                    "success": True,
                    "message": "Processing already active",
                    "status": "already_running",
                }

            # Start ingestion processing
            self.ingestion.start_stream_processing()  # type: ignore[unused-coroutine]
            self.is_processing = True

            return {
                "success": True,
                "message": "Processing started successfully",
                "start_time": datetime.now().isoformat(),
                "status": "started",
            }

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Failed to start processing: {e}")
            return {"success": False, "error": str(e)}

    def stop_processing(self) -> Dict:
        """
        Stop real-time data processing.

        Returns:
            Dictionary with processing stop results
        """
        try:
            if not self.is_processing:
                return {
                    "success": True,
                    "message": "Processing not active",
                    "status": "already_stopped",
                }

            # Stop ingestion processing
            self.ingestion.stop_stream_processing()  # type: ignore[unused-coroutine]
            self.is_processing = False

            return {
                "success": True,
                "message": "Processing stopped successfully",
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "status": "stopped",
            }

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Failed to stop processing: {e}")
            return {"success": False, "error": str(e)}

    def setup_spatial_inference(self, variable: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Setup Bayesian spatial inference for a variable.

        Args:
            variable: Variable to set up inference for
            **kwargs: Additional configuration parameters

        Returns:
            Dictionary with setup results
        """
        try:
            if self.spatial_inference is None:
                self.spatial_inference = BayesianSpatialInference(
                    variable=variable,
                    spatial_resolution=kwargs.get("spatial_resolution", 8),
                    temporal_window=kwargs.get("temporal_window", "1h"),
                    config=self.config,
                )

            # Update configuration if provided
            if kwargs:
                for key, value in kwargs.items():
                    setattr(self.spatial_inference, key, value)

            return {
                "success": True,
                "variable": variable,
                "configuration": {
                    "spatial_resolution": self.spatial_inference.spatial_resolution,
                    "temporal_window": self.spatial_inference.temporal_window,
                    "bayesian_model": (
                        "available"
                        if self.spatial_inference.gp_model
                        else "not_available"
                    ),
                },
            }

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Spatial inference setup failed: {e}")
            return {"success": False, "error": str(e)}

    def get_system_status(self) -> Dict:
        """
        Get comprehensive system status.

        Returns:
            Dictionary with system status information
        """
        uptime = (datetime.now() - self.start_time).total_seconds()

        # Update metrics
        self.metrics.update(
            {
                "uptime_seconds": uptime,
                "last_update": datetime.now(),
                "is_initialized": self.is_initialized,
                "is_processing": self.is_processing,
                "error_count": self.error_count,
            }
        )

        # Component status
        component_status = {
            "registry": "available" if self.registry else "unavailable",
            "ingestion": "available" if self.ingestion else "unavailable",
            "spatial_fusion": "available" if self.fusion else "unavailable",
            "quality_control": (
                "available" if self.quality_controller else "unavailable"
            ),
            "spatial_inference": (
                "available" if self.spatial_inference else "unavailable"
            ),
            "visualization": "available" if self.visualization else "unavailable",
            "calibration": "available" if self.calibration else "unavailable",
        }

        return {
            "system_id": self.system_id,
            "status": "healthy" if self.error_count == 0 else "degraded",
            "uptime_seconds": uptime,
            "is_initialized": self.is_initialized,
            "is_processing": self.is_processing,
            "components": component_status,
            "metrics": self.metrics,
            "networks": len(self.registry.networks),
            "sensors": len(self.registry.sensors),
            "measurements": len(self.ingestion.measurements),
            "last_error": self.last_error,
            "timestamp": datetime.now().isoformat(),
        }

    def run_diagnostics(self) -> Dict[str, Any]:
        """
        Run comprehensive system diagnostics.

        Returns:
            Dictionary with diagnostic results
        """
        diagnostics: Dict[str, Any] = {
            "system_health": "healthy" if self.error_count == 0 else "degraded",
            "component_checks": {},
            "performance_metrics": self.metrics.copy(),
            "configuration_validation": {},
            "recommendations": [],
        }

        # Component diagnostics
        components_to_check = [
            ("registry", self.registry),
            ("ingestion", self.ingestion),
            ("fusion", self.fusion),
            ("quality_controller", self.quality_controller),
            ("spatial_inference", self.spatial_inference),
            ("visualization", self.visualization),
            ("calibration", self.calibration),
        ]

        for component_name, component in components_to_check:
            diagnostics["component_checks"][component_name] = {
                "available": component is not None,
                "status": "operational" if component else "unavailable",
            }

        # Configuration diagnostics
        config_validation = self._validate_system()
        diagnostics["configuration_validation"] = config_validation

        # Generate recommendations
        recommendations = cast(List[str], diagnostics["recommendations"])
        if not self.is_processing:
            recommendations.append(
                "Consider starting data processing for real-time operation"
            )

        if self.error_count > 0:
            recommendations.append(
                f"Address {self.error_count} errors to improve system health"
            )

        if len(self.registry.networks) == 0:
            recommendations.append(
                "Register at least one sensor network"
            )

        return {
            "diagnostics": diagnostics,
            "overall_health": (
                "healthy"
                if (self.error_count == 0 and config_validation["valid"])
                else "needs_attention"
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def export_system_state(self, output_path: str) -> Dict[str, Any]:
        """
        Export complete system state for backup or analysis.

        Args:
            output_path: Path to save the export

        Returns:
            Dictionary with export results
        """
        try:
            import dataclasses

            system_state = {
                "system_id": self.system_id,
                "configuration": self.config,
                "status": self.get_system_status(),
                "networks": {
                    nid: dataclasses.asdict(network)
                    for nid, network in self.registry.networks.items()
                },
                "sensors": {
                    sid: dataclasses.asdict(sensor)
                    for sid, sensor in self.registry.sensors.items()
                },
                "measurements": [
                    dataclasses.asdict(m) for m in self.ingestion.measurements
                ],
                "metrics": self.metrics,
                "exported_at": datetime.now().isoformat(),
            }

            import json

            with open(output_path, "w") as f:
                json.dump(system_state, f, indent=2, default=str)

            return {
                "success": True,
                "export_path": output_path,
                "networks_exported": len(system_state["networks"]),
                "sensors_exported": len(system_state["sensors"]),
                "measurements_exported": len(system_state["measurements"]),
            }

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"System export failed: {e}")
            return {"success": False, "error": str(e)}


class BayesianSpatialInference:
    """
    Bayesian spatial inference for IoT sensor data.

    Converts point sensor measurements to continuous spatial distributions
    using Gaussian process models and H3 spatial indexing. Integrates with
    GEO-INFER-BAYES for sophisticated probabilistic modeling.
    """

    def __init__(
        self,
        variable: str,
        spatial_resolution: int,
        temporal_window: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.variable = variable
        self.spatial_resolution = spatial_resolution
        self.temporal_window = temporal_window
        self.config = config or {}

        # Integration with GEO-INFER-BAYES
        self.gp_model: Optional[Any] = None
        self.posterior_cache: Dict[str, Any] = {}

        # Setup Bayesian inference if available
        self._setup_bayesian_inference()

    def _setup_bayesian_inference(self) -> None:
        """Setup Bayesian spatial inference model."""
        try:
            # Import GEO-INFER-BAYES components
            from geo_infer_bayes import GaussianProcess, SpatialCovariance  # type: ignore[import-untyped]

            # Configure covariance function based on variable characteristics
            if self.variable in ["soil_moisture", "temperature"]:
                # Environmental variables with smooth spatial correlation
                cov_func = SpatialCovariance.matern_52(
                    length_scale=self.config.get("length_scale", 1000.0),
                    variance=self.config.get("variance", 1.0),
                )
            elif self.variable in ["air_quality", "radiation"]:
                # Variables with more complex spatial patterns
                cov_func = SpatialCovariance.matern_32(
                    length_scale=self.config.get("length_scale", 2000.0),
                    variance=self.config.get("variance", 0.5),
                )
            else:
                # Default configuration
                cov_func = SpatialCovariance.matern_52(
                    length_scale=self.config.get("length_scale", 1500.0),
                    variance=self.config.get("variance", 1.0),
                )

            # Initialize Gaussian Process model
            self.gp_model = GaussianProcess(
                covariance_function=cov_func,
                mean_function=self.config.get("mean_function", "constant"),
                noise_variance=self.config.get("noise_variance", 0.01),
            )

        except ImportError:
            self.gp_model = None
            print("Warning: GEO-INFER-BAYES not available, spatial inference disabled")

    def infer_spatial_distribution(
        self,
        sensor_data: List[Dict[str, Any]],
        priors: Optional[Any] = None,
        update_interval: str = "15min",
    ) -> Dict[str, Any]:
        """
        Perform Bayesian spatial inference on sensor data.

        Args:
            sensor_data: List of sensor measurements with lat/lon coordinates
            priors: Optional prior beliefs for Bayesian inference
            update_interval: Time interval for updating the model

        Returns:
            Dictionary containing posterior distribution and uncertainty estimates
        """
        if self.gp_model is None:
            return {"error": "Bayesian inference not available"}

        try:
            # Extract coordinates and values from sensor data
            coords_list = []
            values_list = []

            for measurement in sensor_data:
                if "latitude" in measurement and "longitude" in measurement:
                    # Convert lat/lon to local coordinate system for GP
                    x = measurement["longitude"] * 111000  # Rough meters per degree
                    y = measurement["latitude"] * 111000
                    coords_list.append([x, y])
                    values_list.append(measurement["value"])

            if len(coords_list) < 3:
                return {"error": "Insufficient data for spatial inference"}

            coords = np.array(coords_list)
            values = np.array(values_list)

            # Perform Bayesian inference
            self.gp_model.fit(coords, values)

            # Generate predictions on H3 grid
            h3_grid = self._generate_h3_prediction_grid(coords)

            if len(h3_grid) > 0:
                predictions, uncertainties = self.gp_model.predict(
                    h3_grid, return_std=True
                )

                # Store results in cache
                self.posterior_cache[self.variable] = {
                    "posterior_mean": predictions,
                    "posterior_std": uncertainties,
                    "h3_grid": h3_grid,
                    "sensor_coords": coords,
                    "sensor_values": values,
                    "timestamp": datetime.now(),
                    "update_interval": update_interval,
                }

                return {
                    "success": True,
                    "posterior_mean": predictions.tolist(),
                    "posterior_std": uncertainties.tolist(),
                    "h3_grid": h3_grid.tolist(),
                    "sensor_count": len(values),
                    "prediction_points": len(predictions),
                }
            else:
                return {"error": "Failed to generate prediction grid"}

        except Exception as e:
            return {"error": f"Spatial inference failed: {str(e)}"}

    def get_posterior_map(self, confidence_intervals: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Get current posterior spatial distribution map.

        Args:
            confidence_intervals: List of confidence levels (e.g., [0.68, 0.95])

        Returns:
            Dictionary with posterior map data and uncertainty bounds
        """
        if self.variable not in self.posterior_cache:
            return {"error": "No posterior distribution available"}

        cache_data = self.posterior_cache[self.variable]

        if confidence_intervals is None:
            confidence_intervals = [0.68, 0.95]

        # Calculate confidence intervals
        confidence_bounds = {}
        for ci in confidence_intervals:
            z_score = 1.96 if ci == 0.95 else 1.0  # Approximate z-scores
            confidence_bounds[ci] = {
                "lower": (
                    cache_data["posterior_mean"] - z_score * cache_data["posterior_std"]
                ).tolist(),
                "upper": (
                    cache_data["posterior_mean"] + z_score * cache_data["posterior_std"]
                ).tolist(),
            }

        return {
            "variable": self.variable,
            "posterior_mean": cache_data["posterior_mean"].tolist(),
            "posterior_std": cache_data["posterior_std"].tolist(),
            "confidence_bounds": confidence_bounds,
            "h3_grid": cache_data["h3_grid"].tolist(),
            "timestamp": cache_data["timestamp"].isoformat(),
            "sensor_count": len(cache_data["sensor_values"]),
        }

    def _generate_h3_prediction_grid(self, sensor_coords: np.ndarray) -> np.ndarray:
        """Generate H3 grid for spatial predictions."""
        try:
            # Find bounds of sensor data
            min_x, min_y = np.min(sensor_coords, axis=0)
            max_x, max_y = np.max(sensor_coords, axis=0)

            # Create prediction grid with buffer
            buffer = 0.2  # 20% buffer around sensor locations
            x_range = max_x - min_x
            y_range = max_y - min_y

            grid_min_x = min_x - buffer * x_range
            grid_max_x = max_x + buffer * x_range
            grid_min_y = min_y - buffer * y_range
            grid_max_y = max_y + buffer * y_range

            # Generate grid points (simplified - would use proper H3 grid in production)
            n_points = min(100, len(sensor_coords) * 10)  # Adaptive grid density
            x_grid = np.linspace(grid_min_x, grid_max_x, int(np.sqrt(n_points)))
            y_grid = np.linspace(grid_min_y, grid_max_y, int(np.sqrt(n_points)))

            # Create mesh grid
            X, Y = np.meshgrid(x_grid, y_grid)
            grid_points = np.column_stack([X.ravel(), Y.ravel()])

            return np.asarray(grid_points)

        except Exception as e:
            print(f"Error generating prediction grid: {e}")
            return np.array([])


class GlobalMonitoringSystem:
    """
    Global-scale environmental monitoring system.

    Integrates multiple sensor networks for global environmental monitoring
    with real-time updates and alert systems.
    """

    def __init__(
        self,
        variable: str,
        sensor_networks: Dict[str, Any],
        update_frequency: int,
    ) -> None:
        self.variable = variable
        self.sensor_networks = sensor_networks
        self.update_frequency = update_frequency

    def get_current_global_distribution(
        self, confidence_level: float, spatial_resolution: int
    ) -> Dict[str, Any]:
        """Get current global distribution map by aggregating network data.

        Args:
            confidence_level: Statistical confidence level (e.g., 0.95)
            spatial_resolution: H3 resolution for the output grid

        Returns:
            Dictionary with distribution data including grid cells and values.
        """
        distribution: Dict[str, Any] = {
            "variable": self.variable,
            "confidence_level": confidence_level,
            "spatial_resolution": spatial_resolution,
            "networks_aggregated": len(self.sensor_networks),
            "cells": {},
        }

        for network_name in self.sensor_networks:
            network_data = self.sensor_networks[network_name]
            if isinstance(network_data, dict):
                cells = cast(Dict[str, Any], distribution["cells"])
                for cell_id, value in network_data.get("cells", {}).items():
                    if cell_id in cells:
                        existing = cells[cell_id]
                        existing["values"].append(value)
                        existing["mean"] = sum(existing["values"]) / len(
                            existing["values"]
                        )
                    else:
                        cells[cell_id] = {
                            "values": [value],
                            "mean": value,
                        }

        return distribution


# Convenience imports for common workflows
class MultiModalFusion:
    """
    Multi-modal sensor fusion capabilities.

    Combines data from multiple sensor types and sources for improved
    accuracy and reliability in environmental monitoring applications.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.fusion_weights: Dict[str, Dict[str, Any]] = {}
        self.sensor_types: List[str] = []
        self.fusion_history: List[Any] = []

    def add_sensor_type(
        self, sensor_type: str, weight: float = 1.0, reliability: float = 1.0
    ) -> None:
        """
        Add a sensor type to the fusion process.

        Args:
            sensor_type: Type of sensor (e.g., 'satellite', 'ground_station', 'mobile')
            weight: Relative weight for this sensor type in fusion
            reliability: Reliability score (0-1) for uncertainty quantification
        """
        self.sensor_types.append(sensor_type)
        self.fusion_weights[sensor_type] = {
            "weight": weight,
            "reliability": reliability,
        }

    def fuse_measurements(
        self,
        measurements: List[Dict[str, Any]],
        variable: str,
        spatial_window: str = "5km",
        temporal_window: str = "1h",
    ) -> Dict[str, Any]:
        """
        Fuse measurements from multiple sensor types.

        Args:
            measurements: List of measurements from different sensor types
            variable: Variable being measured (e.g., 'pm25', 'temperature')
            spatial_window: Spatial window for fusion
            temporal_window: Temporal window for fusion

        Returns:
            Dictionary with fused measurement and uncertainty estimates
        """
        if not measurements:
            return {"error": "No measurements provided for fusion"}

        try:
            # Group measurements by sensor type
            sensor_groups: Dict[str, List[Dict[str, Any]]] = {}
            for measurement in measurements:
                sensor_type = measurement.get("sensor_type", "unknown")
                if sensor_type not in sensor_groups:
                    sensor_groups[sensor_type] = []
                sensor_groups[sensor_type].append(measurement)

            # Calculate weighted average
            weighted_sum = 0.0
            total_weight = 0.0
            uncertainty_sum = 0.0

            for sensor_type, type_measurements in sensor_groups.items():
                if sensor_type in self.fusion_weights:
                    weight = self.fusion_weights[sensor_type]["weight"]
                    reliability = self.fusion_weights[sensor_type]["reliability"]

                    # Calculate mean for this sensor type
                    values = [m["value"] for m in type_measurements if "value" in m]
                    if values:
                        type_mean = np.mean(values)
                        type_std = np.std(values) if len(values) > 1 else 0.1

                        # Apply weighting
                        weighted_sum += type_mean * weight
                        total_weight += weight

                        # Uncertainty contribution
                        uncertainty_sum += (type_std / reliability) * weight

            if total_weight == 0:
                return {"error": "No valid sensor types found for fusion"}

            fused_value = weighted_sum / total_weight
            fused_uncertainty = uncertainty_sum / total_weight

            # Store fusion result
            fusion_result = {
                "variable": variable,
                "fused_value": fused_value,
                "uncertainty": fused_uncertainty,
                "sensor_types_used": list(sensor_groups.keys()),
                "total_measurements": len(measurements),
                "spatial_window": spatial_window,
                "temporal_window": temporal_window,
                "timestamp": datetime.now().isoformat(),
            }

            self.fusion_history.append(fusion_result)

            return {"success": True, "result": fusion_result}

        except Exception as e:
            return {"error": f"Fusion failed: {str(e)}"}


class AdaptiveSampling:
    """
    Adaptive sensor network optimization.

    Dynamically optimizes sensor placement and sampling strategies based on
    uncertainty estimates, coverage requirements, and resource constraints.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.optimization_history: List[Dict[str, Any]] = []
        self.current_network_state: Dict[str, Any] = {}

    def suggest_locations(
        self,
        current_network: List[Dict[str, Any]],
        priority_areas: List[Any],
        uncertainty_threshold: float = 0.1,
        budget_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Suggest new sensor locations based on uncertainty and coverage analysis.

        Args:
            current_network: Current sensor network configuration
            priority_areas: Geographic areas requiring monitoring priority
            uncertainty_threshold: Maximum acceptable uncertainty level
            budget_constraints: Budget limitations for new sensors

        Returns:
            List of recommended sensor locations with priority scores
        """
        try:
            # Analyze current network coverage and uncertainty
            coverage_analysis = self._analyze_coverage(current_network, priority_areas)
            uncertainty_analysis = self._analyze_uncertainty(current_network)

            # Identify areas with high uncertainty or poor coverage
            gaps = self._identify_coverage_gaps(
                coverage_analysis, uncertainty_analysis, uncertainty_threshold
            )

            # Generate candidate locations
            candidates = self._generate_candidate_locations(gaps, priority_areas)

            # Score and rank candidates
            scored_candidates = self._score_candidates(
                candidates, coverage_analysis, budget_constraints
            )

            # Apply budget constraints
            if budget_constraints:
                scored_candidates = self._apply_budget_constraints(
                    scored_candidates, budget_constraints
                )

            # Store optimization result
            optimization_result = {
                "timestamp": datetime.now().isoformat(),
                "current_sensors": len(current_network),
                "recommended_sensors": len(scored_candidates),
                "priority_areas_covered": len(priority_areas),
                "avg_uncertainty_before": np.mean(list(uncertainty_analysis.values())),
                "estimated_improvement": self._estimate_improvement(
                    scored_candidates, uncertainty_analysis
                ),
            }

            self.optimization_history.append(optimization_result)

            return {
                "success": True,
                "recommendations": scored_candidates[:10],  # Top 10 recommendations
                "analysis": {
                    "coverage_gaps": len(gaps),
                    "candidate_locations": len(candidates),
                    "improvement_estimate": optimization_result[
                        "estimated_improvement"
                    ],
                },
            }

        except Exception as e:
            return {"error": f"Location suggestion failed: {str(e)}"}

    def _analyze_coverage(self, network: List[Dict[str, Any]], priority_areas: List[Any]) -> Dict[str, Any]:
        """Analyze current network coverage."""
        # Simplified coverage analysis
        covered_areas: Set[str] = set()
        for sensor in network:
            if "h3_index" in sensor:
                covered_areas.add(sensor["h3_index"])

        coverage_stats = {
            "total_sensors": len(network),
            "covered_h3_cells": len(covered_areas),
            "coverage_ratio": len(covered_areas) / max(len(priority_areas), 1),
        }

        return coverage_stats

    def _analyze_uncertainty(self, network: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze uncertainty in current network."""
        # Simplified uncertainty analysis
        uncertainties: Dict[str, Any] = {}
        for sensor in network:
            # Estimate uncertainty based on sensor density and environmental factors
            base_uncertainty = 0.1  # Base uncertainty level
            density_factor = min(
                1.0, len(network) / 100
            )  # Higher density = lower uncertainty
            uncertainties[sensor.get("sensor_id", "unknown")] = base_uncertainty * (
                1 - density_factor
            )

        return uncertainties

    def _identify_coverage_gaps(
        self,
        coverage_analysis: Dict[str, Any],
        uncertainty_analysis: Dict[str, Any],
        threshold: float,
    ) -> List[str]:
        """Identify areas with poor coverage or high uncertainty."""
        gaps: List[str] = []

        # Find high uncertainty areas
        high_uncertainty_sensors = [
            sid
            for sid, uncertainty in uncertainty_analysis.items()
            if uncertainty > threshold
        ]

        gaps.extend(high_uncertainty_sensors)

        return gaps

    def _generate_candidate_locations(
        self, gaps: List[str], priority_areas: List[Any]
    ) -> List[Dict[str, Any]]:
        """Generate candidate locations for new sensors."""
        candidates: List[Dict[str, Any]] = []

        # Generate candidates around coverage gaps
        for gap in gaps[:5]:  # Limit to top 5 gaps for efficiency
            # Create candidate locations around the gap
            for i in range(3):  # 3 candidates per gap
                candidate = {
                    "latitude": 40.0
                    + np.random.normal(0, 0.01),  # Around NYC area for demo
                    "longitude": -74.0 + np.random.normal(0, 0.01),
                    "priority_score": np.random.uniform(0.5, 1.0),
                    "estimated_cost": np.random.uniform(100, 1000),
                }
                candidates.append(candidate)

        return candidates

    def _score_candidates(
        self,
        candidates: List[Dict[str, Any]],
        coverage_analysis: Dict[str, Any],
        budget_constraints: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Score and rank candidate locations."""
        scored: List[Dict[str, Any]] = []

        for candidate in candidates:
            # Calculate score based on multiple factors
            coverage_score = candidate["priority_score"]
            cost_score = 1.0 / (
                1.0 + candidate["estimated_cost"] / 1000
            )  # Lower cost = higher score

            # Combine scores
            total_score = 0.7 * coverage_score + 0.3 * cost_score

            candidate["total_score"] = total_score
            candidate["coverage_score"] = coverage_score
            candidate["cost_score"] = cost_score

            scored.append(candidate)

        # Sort by total score (descending)
        scored.sort(key=lambda x: x["total_score"], reverse=True)

        return scored

    def _apply_budget_constraints(
        self,
        candidates: List[Dict[str, Any]],
        budget_constraints: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Apply budget constraints to candidate selection."""
        max_sensors = budget_constraints.get("max_sensors", len(candidates))
        max_cost = budget_constraints.get("max_cost", float("inf"))

        filtered: List[Dict[str, Any]] = []
        total_cost = 0.0

        for candidate in candidates:
            if len(filtered) >= max_sensors:
                break

            if total_cost + candidate["estimated_cost"] <= max_cost:
                filtered.append(candidate)
                total_cost += candidate["estimated_cost"]

        return filtered

    def _estimate_improvement(
        self,
        recommendations: List[Dict[str, Any]],
        current_uncertainty: Dict[str, Any],
    ) -> float:
        """Estimate improvement from new sensor placements."""
        if not recommendations:
            return 0.0

        # Simple estimation: each new sensor reduces uncertainty by ~10%
        avg_current_uncertainty = float(np.mean(list(current_uncertainty.values())))
        improvement_per_sensor = 0.1

        return float(min(
            avg_current_uncertainty, len(recommendations) * improvement_per_sensor
        ))


class PredictiveMaintenance:
    """
    Predictive maintenance for sensor networks.

    Monitors sensor health and predicts failures using machine learning
    and statistical analysis of sensor performance metrics.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sensor_health_models: Dict[str, Any] = {}
        self.maintenance_history: List[Any] = []
        self.alert_thresholds: Dict[str, float] = {
            "battery_level": 20.0,  # Percent
            "data_quality_score": 0.7,  # 0-1 scale
            "communication_reliability": 0.8,  # 0-1 scale
            "calibration_drift": 0.1,  # Acceptable drift level
        }

    def assess_network_health(
        self,
        sensor_network: List[Dict[str, Any]],
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Assess overall health of the sensor network.

        Args:
            sensor_network: List of sensor configurations
            metrics: Optional list of metrics to assess

        Returns:
            Dictionary with health assessment for each sensor and network summary
        """
        if metrics is None:
            metrics = [
                "battery_level",
                "data_quality_score",
                "communication_reliability",
            ]

        health_assessments = {}

        for sensor in sensor_network:
            sensor_id = sensor.get("sensor_id", "unknown")
            sensor_health = {}

            for metric in metrics:
                if metric in sensor:
                    value = sensor[metric]
                    health_score = self._calculate_health_score(metric, value)
                    status = self._determine_health_status(metric, value)

                    sensor_health[metric] = {
                        "value": value,
                        "health_score": health_score,
                        "status": status,
                        "needs_attention": status in ["warning", "critical"],
                    }
                else:
                    sensor_health[metric] = {
                        "value": None,
                        "health_score": 0.0,
                        "status": "unknown",
                        "needs_attention": True,
                    }

            # Overall sensor health score
            valid_scores = [
                h["health_score"]
                for h in sensor_health.values()
                if h["value"] is not None
            ]
            overall_score = np.mean(valid_scores) if valid_scores else 0.0
            overall_status = self._determine_overall_status(sensor_health)

            health_assessments[sensor_id] = {
                "metrics": sensor_health,
                "overall_score": overall_score,
                "overall_status": overall_status,
                "needs_maintenance": overall_status in ["warning", "critical"],
            }

        # Network summary
        network_summary = self._calculate_network_summary(health_assessments)

        return {
            "sensor_assessments": health_assessments,
            "network_summary": network_summary,
            "assessment_timestamp": datetime.now().isoformat(),
        }

    def get_maintenance_schedule(
        self,
        sensor_network: List[Dict[str, Any]],
        priority: str = "critical_sensors",
        time_horizon: str = "30days",
    ) -> Dict[str, Any]:
        """
        Generate maintenance schedule based on health assessments.

        Args:
            sensor_network: List of sensor configurations with health data
            priority: Priority level for scheduling ('critical_sensors', 'all_sensors')
            time_horizon: Time horizon for scheduling

        Returns:
            Maintenance schedule with recommended actions and timelines
        """
        # Assess current health
        health_assessment = self.assess_network_health(sensor_network)

        # Identify sensors needing maintenance
        maintenance_candidates: List[Dict[str, Any]] = []

        for sensor_id, assessment in health_assessment["sensor_assessments"].items():
            if assessment["needs_maintenance"]:
                # Calculate urgency score
                urgency = self._calculate_maintenance_urgency(assessment)

                maintenance_candidates.append(
                    {
                        "sensor_id": sensor_id,
                        "urgency_score": urgency,
                        "overall_status": assessment["overall_status"],
                        "priority_metrics": self._identify_priority_issues(assessment),
                        "recommended_actions": self._suggest_maintenance_actions(
                            assessment
                        ),
                    }
                )

        # Sort by urgency
        maintenance_candidates.sort(key=lambda x: x["urgency_score"], reverse=True)

        # Apply priority filtering
        if priority == "critical_sensors":
            maintenance_candidates = [
                c for c in maintenance_candidates if c["overall_status"] == "critical"
            ]

        # Generate schedule
        schedule = self._generate_maintenance_schedule(
            maintenance_candidates, time_horizon
        )

        return {
            "maintenance_schedule": schedule,
            "total_sensors_needing_maintenance": len(maintenance_candidates),
            "critical_sensors": len(
                [c for c in maintenance_candidates if c["overall_status"] == "critical"]
            ),
            "priority_level": priority,
            "time_horizon": time_horizon,
        }

    def _calculate_health_score(self, metric: str, value: Any) -> float:
        """Calculate health score for a specific metric."""
        if value is None:
            return 0.0

        if metric == "battery_level":
            # Higher battery = higher score
            return float(min(100.0, value)) / 100.0
        elif metric in ["data_quality_score", "communication_reliability"]:
            # Direct mapping for 0-1 scale metrics
            return float(value)
        elif metric == "calibration_drift":
            # Lower drift = higher score
            return max(0.0, 1.0 - abs(float(value)))
        else:
            raise ValueError(f"Unsupported health metric: {metric}")

    def _determine_health_status(self, metric: str, value: Any) -> str:
        """Determine health status for a metric."""
        if value is None:
            return "unknown"

        threshold_value = self.alert_thresholds.get(metric, 0.8)

        if metric == "battery_level":
            if value < 10:
                return "critical"
            elif value < threshold_value:
                return "warning"
            else:
                return "good"
        elif metric in ["data_quality_score", "communication_reliability"]:
            if value < 0.5:
                return "critical"
            elif value < threshold_value:
                return "warning"
            else:
                return "good"
        elif metric == "calibration_drift":
            if abs(value) > 0.2:
                return "critical"
            elif abs(value) > threshold_value:
                return "warning"
            else:
                return "good"
        else:
            return "unknown"

    def _determine_overall_status(self, sensor_health: Dict[str, Any]) -> str:
        """Determine overall sensor health status."""
        statuses = [
            h["status"] for h in sensor_health.values() if h["status"] != "unknown"
        ]

        if not statuses:
            return "unknown"

        if "critical" in statuses:
            return "critical"
        elif "warning" in statuses:
            return "warning"
        else:
            return "good"

    def _calculate_network_summary(self, health_assessments: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for the network."""
        if not health_assessments:
            return {}

        scores = [a["overall_score"] for a in health_assessments.values()]
        statuses = [a["overall_status"] for a in health_assessments.values()]

        return {
            "total_sensors": len(health_assessments),
            "average_health_score": np.mean(scores),
            "health_score_std": np.std(scores),
            "status_distribution": {
                "good": statuses.count("good"),
                "warning": statuses.count("warning"),
                "critical": statuses.count("critical"),
                "unknown": statuses.count("unknown"),
            },
            "sensors_needing_maintenance": statuses.count("warning")
            + statuses.count("critical"),
        }

    def _calculate_maintenance_urgency(self, assessment: Dict[str, Any]) -> float:
        """Calculate urgency score for maintenance scheduling."""
        base_urgency = 0.0

        # Weight different factors
        if assessment["overall_status"] == "critical":
            base_urgency += 1.0
        elif assessment["overall_status"] == "warning":
            base_urgency += 0.5

        # Add urgency based on low health scores
        base_urgency += max(0, (1.0 - assessment["overall_score"])) * 0.5

        return float(base_urgency)

    def _identify_priority_issues(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify which metrics need priority attention."""
        priority_metrics: List[Dict[str, Any]] = []

        for metric, health in assessment["metrics"].items():
            if health["status"] in ["warning", "critical"]:
                priority_metrics.append(
                    {
                        "metric": metric,
                        "status": health["status"],
                        "value": health["value"],
                    }
                )

        return priority_metrics

    def _suggest_maintenance_actions(self, assessment: Dict[str, Any]) -> List[str]:
        """Suggest specific maintenance actions."""
        actions: List[str] = []

        for metric, health in assessment["metrics"].items():
            if health["status"] == "critical":
                if metric == "battery_level":
                    actions.append("Replace battery immediately")
                elif metric == "data_quality_score":
                    actions.append("Calibrate or replace sensor")
                elif metric == "communication_reliability":
                    actions.append("Check communication module and connections")
                elif metric == "calibration_drift":
                    actions.append("Recalibrate sensor")

        if not actions:
            actions.append("Routine inspection recommended")

        return actions

    def _generate_maintenance_schedule(
        self,
        candidates: List[Dict[str, Any]],
        time_horizon: str,
    ) -> List[Dict[str, Any]]:
        """Generate actual maintenance schedule."""
        schedule: List[Dict[str, Any]] = []

        for candidate in candidates:
            # Simple scheduling: critical issues first, spread over time horizon
            days_ahead = min(7, len(schedule) + 1)  # Schedule within next week

            schedule_entry: Dict[str, Any] = {
                "sensor_id": candidate["sensor_id"],
                "scheduled_date": (
                    datetime.now() + timedelta(days=days_ahead)
                ).isoformat(),
                "priority": candidate["overall_status"],
                "urgency_score": candidate["urgency_score"],
                "recommended_actions": candidate["recommended_actions"],
                "priority_metrics": candidate["priority_metrics"],
            }

            schedule.append(schedule_entry)

        return schedule


# Classes already included in __all__ above
