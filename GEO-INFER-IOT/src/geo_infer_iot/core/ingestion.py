"""
IoT Data Ingestion Module

This module handles the ingestion and processing of IoT sensor data streams,
integrating with GEO-INFER-SPACE for H3 spatial indexing and GEO-INFER-BAYES 
for Bayesian spatial inference.

Key features:
- Multi-protocol IoT data ingestion (MQTT, CoAP, LoRaWAN, HTTP)
- Real-time H3 spatial indexing
- Integration with OSC (Open Science Catalog) methods from GEO-INFER-SPACE
- Bayesian spatial inference for converting point measurements to surfaces
- Quality control and data validation
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import uuid
import time
from abc import ABC, abstractmethod

# Core dependencies
import h3
import numpy as np
import pandas as pd

# Optional dependencies (graceful degradation if not available)
try:
    from geo_infer_space.osc_geo.utils.h3_utils import (
        h3_to_geojson, geojson_to_h3, get_h3_neighbors, 
        h3_distance, h3_resolution_stats
    )
    from geo_infer_space.osc_geo.utils.spatial_operations import (
        SpatialOperations, CoordinateTransform
    )
    from geo_infer_space.osc_geo.core.osc_catalog import OSCCatalog
    HAS_GEO_SPACE = True
except ImportError:
    HAS_GEO_SPACE = False
    logging.warning("GEO-INFER-SPACE not available, using basic H3 operations")

try:
    from geo_infer_bayes import (
        GaussianProcess, BayesianInference, SpatialCovariance,
        VariationalInference, MCMCSampler
    )
    HAS_GEO_BAYES = True
except ImportError:
    HAS_GEO_BAYES = False
    logging.warning("GEO-INFER-BAYES not available, spatial inference disabled")

# Protocol handlers
try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

try:
    import asyncio_mqtt
    HAS_ASYNC_MQTT = True
except ImportError:
    HAS_ASYNC_MQTT = False

logger = logging.getLogger(__name__)

@dataclass
class SensorMeasurement:
    """Data class for sensor measurements with spatial context."""
    sensor_id: str
    timestamp: datetime
    variable: str
    value: float
    unit: str
    latitude: float
    longitude: float
    h3_index: Optional[str] = None
    h3_resolution: int = 8
    quality_flags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Automatically compute H3 index from coordinates."""
        if self.h3_index is None and self.latitude and self.longitude:
            self.h3_index = h3.geo_to_h3(
                self.latitude, self.longitude, self.h3_resolution
            )

@dataclass
class SpatialInferenceConfig:
    """Configuration for Bayesian spatial inference."""
    variable: str
    h3_resolution: int = 8
    temporal_window_hours: float = 1.0
    spatial_range_km: float = 10.0
    covariance_function: str = "matern_52"
    mean_function: str = "constant"
    length_scale: float = 1000.0  # meters
    noise_variance: float = 0.01
    update_interval_minutes: int = 15
    confidence_levels: List[float] = field(default_factory=lambda: [0.68, 0.95])

class IoTDataIngestion:
    """
    IoT data ingestion engine with spatial indexing and Bayesian inference.
    
    This class handles real-time ingestion of IoT sensor data, performs
    H3 spatial indexing, and integrates with Bayesian inference for
    converting point measurements to continuous spatial distributions.
    """
    
    def __init__(self, registry, config: Optional[Dict] = None):
        self.registry = registry
        self.config = config or {}
        
        # Data storage
        self.measurements: List[SensorMeasurement] = []
        self.spatial_index: Dict[str, List[SensorMeasurement]] = defaultdict(list)
        
        # Spatial inference configuration
        self.inference_configs: Dict[str, SpatialInferenceConfig] = {}
        self.spatial_models: Dict[str, object] = {}
        
        # OSC integration
        if HAS_GEO_SPACE:
            self.spatial_ops = SpatialOperations()
            self.osc_catalog = OSCCatalog()
            self.coord_transform = CoordinateTransform()
        
        # Protocol handlers
        self.protocol_handlers = {}
        self._setup_protocol_handlers()
        
        # Processing state
        self.is_processing = False
        self.processing_tasks = []
        
        logger.info("IoT Data Ingestion engine initialized")
    
    def _setup_protocol_handlers(self):
        """Setup handlers for different IoT protocols."""
        if HAS_MQTT:
            self.protocol_handlers['mqtt'] = self._handle_mqtt
        if HAS_ASYNC_MQTT:
            self.protocol_handlers['async_mqtt'] = self._handle_async_mqtt
        # Additional protocols (CoAP, LoRaWAN, etc.) would go here
    
    async def ingest_measurement(self, measurement: Union[Dict, SensorMeasurement]) -> bool:
        """
        Ingest a single sensor measurement.
        
        Args:
            measurement: Either a dictionary with measurement data or SensorMeasurement object
            
        Returns:
            bool: True if measurement was successfully ingested and processed
        """
        try:
            # Convert to SensorMeasurement if needed
            if isinstance(measurement, dict):
                measurement = self._dict_to_measurement(measurement)
            
            # Validate measurement
            if not self._validate_measurement(measurement):
                logger.warning(f"Invalid measurement from sensor {measurement.sensor_id}")
                return False
            
            # Add H3 spatial index
            self._add_spatial_index(measurement)
            
            # Store measurement
            self.measurements.append(measurement)
            self.spatial_index[measurement.h3_index].append(measurement)
            
            # Trigger spatial inference update if configured
            if measurement.variable in self.inference_configs:
                await self._update_spatial_inference(measurement.variable)
            
            logger.debug(f"Ingested measurement: {measurement.sensor_id} -> {measurement.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting measurement: {e}")
            return False
    
    def _dict_to_measurement(self, data: Dict) -> SensorMeasurement:
        """Convert dictionary to SensorMeasurement object."""
        return SensorMeasurement(
            sensor_id=data['sensor_id'],
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            variable=data['variable'],
            value=float(data['value']),
            unit=data.get('unit', ''),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            h3_resolution=data.get('h3_resolution', 8),
            quality_flags=data.get('quality_flags', []),
            metadata=data.get('metadata', {})
        )
    
    def _validate_measurement(self, measurement: SensorMeasurement) -> bool:
        """Validate sensor measurement data."""
        # Basic validation
        if not measurement.sensor_id or not measurement.variable:
            return False
        
        # Coordinate validation
        if not (-90 <= measurement.latitude <= 90):
            return False
        if not (-180 <= measurement.longitude <= 180):
            return False
        
        # Value validation (basic range check)
        if not isinstance(measurement.value, (int, float)) or np.isnan(measurement.value):
            return False
        
        return True
    
    def _add_spatial_index(self, measurement: SensorMeasurement):
        """Add H3 spatial index to measurement and integrate with OSC methods."""
        # Basic H3 indexing
        if not measurement.h3_index:
            measurement.h3_index = h3.geo_to_h3(
                measurement.latitude, measurement.longitude, measurement.h3_resolution
            )
        
        # Enhanced spatial operations using GEO-INFER-SPACE OSC methods
        if HAS_GEO_SPACE:
            try:
                # Get neighbor cells for spatial context
                neighbors = get_h3_neighbors(measurement.h3_index, ring_size=1)
                measurement.metadata['h3_neighbors'] = neighbors
                
                # Calculate H3 resolution statistics
                stats = h3_resolution_stats(measurement.h3_resolution)
                measurement.metadata['h3_stats'] = stats
                
                # Add to OSC catalog if configured
                if hasattr(self.osc_catalog, 'add_measurement'):
                    self.osc_catalog.add_measurement(measurement)
                    
            except Exception as e:
                logger.warning(f"Error in enhanced spatial indexing: {e}")
    
    def setup_spatial_inference(self, config: SpatialInferenceConfig):
        """
        Setup Bayesian spatial inference for a specific variable.
        
        Args:
            config: Configuration for spatial inference
        """
        if not HAS_GEO_BAYES:
            logger.error("GEO-INFER-BAYES not available, cannot setup spatial inference")
            return
        
        self.inference_configs[config.variable] = config
        
        # Initialize Gaussian Process model
        try:
            # Setup covariance function
            if config.covariance_function == "matern_52":
                cov_func = SpatialCovariance.matern_52(
                    length_scale=config.length_scale,
                    variance=1.0
                )
            elif config.covariance_function == "rbf":
                cov_func = SpatialCovariance.rbf(
                    length_scale=config.length_scale,
                    variance=1.0
                )
            else:
                cov_func = SpatialCovariance.matern_52(
                    length_scale=config.length_scale,
                    variance=1.0
                )
            
            # Initialize Gaussian Process
            gp_model = GaussianProcess(
                covariance_function=cov_func,
                mean_function=config.mean_function,
                noise_variance=config.noise_variance
            )
            
            self.spatial_models[config.variable] = gp_model
            
            logger.info(f"Setup spatial inference for variable: {config.variable}")
            
        except Exception as e:
            logger.error(f"Error setting up spatial inference: {e}")
    
    async def _update_spatial_inference(self, variable: str):
        """Update Bayesian spatial inference for a variable."""
        if not HAS_GEO_BAYES or variable not in self.spatial_models:
            return
        
        try:
            config = self.inference_configs[variable]
            model = self.spatial_models[variable]
            
            # Get recent measurements for this variable
            recent_data = self._get_recent_measurements(
                variable=variable,
                hours=config.temporal_window_hours
            )
            
            if len(recent_data) < 3:  # Need minimum data for inference
                return
            
            # Prepare spatial coordinates (convert to meters)
            coords = []
            values = []
            h3_indices = []
            
            for measurement in recent_data:
                # Convert lat/lon to local coordinate system
                if HAS_GEO_SPACE:
                    x, y = self.coord_transform.latlon_to_meters(
                        measurement.latitude, measurement.longitude
                    )
                else:
                    # Simple approximation
                    x = measurement.longitude * 111000  # rough meters per degree
                    y = measurement.latitude * 111000
                
                coords.append([x, y])
                values.append(measurement.value)
                h3_indices.append(measurement.h3_index)
            
            coords = np.array(coords)
            values = np.array(values)
            
            # Perform Bayesian inference
            posterior = await model.fit_async(coords, values)
            
            # Generate predictions on H3 grid
            prediction_grid = self._generate_h3_prediction_grid(
                h3_indices, config.h3_resolution
            )
            
            predictions = await model.predict_async(
                prediction_grid, return_std=True
            )
            
            # Store results
            self._store_spatial_predictions(
                variable, predictions, prediction_grid, config
            )
            
            logger.info(f"Updated spatial inference for {variable}: {len(recent_data)} measurements")
            
        except Exception as e:
            logger.error(f"Error updating spatial inference for {variable}: {e}")
    
    def _get_recent_measurements(self, variable: str, hours: float) -> List[SensorMeasurement]:
        """Get recent measurements for a specific variable."""
        cutoff_time = datetime.now(timezone.utc) - pd.Timedelta(hours=hours)
        
        recent = [
            m for m in self.measurements
            if (m.variable == variable and 
                m.timestamp.replace(tzinfo=timezone.utc) > cutoff_time)
        ]
        
        return recent
    
    def _generate_h3_prediction_grid(self, measurement_h3_indices: List[str], 
                                   resolution: int) -> np.ndarray:
        """Generate H3 grid for spatial predictions."""
        # Get unique H3 cells and their neighbors for prediction
        h3_cells = set(measurement_h3_indices)
        
        # Add neighbor cells for smoother interpolation
        for h3_index in list(h3_cells):
            if HAS_GEO_SPACE:
                neighbors = get_h3_neighbors(h3_index, ring_size=2)
                h3_cells.update(neighbors)
            else:
                # Use basic H3 neighbor function
                neighbors = h3.k_ring(h3_index, 2)
                h3_cells.update(neighbors)
        
        # Convert H3 cells to coordinates
        grid_coords = []
        for h3_index in h3_cells:
            lat, lon = h3.h3_to_geo(h3_index)
            
            if HAS_GEO_SPACE:
                x, y = self.coord_transform.latlon_to_meters(lat, lon)
            else:
                x = lon * 111000
                y = lat * 111000
            
            grid_coords.append([x, y])
        
        return np.array(grid_coords)
    
    def _store_spatial_predictions(self, variable: str, predictions: Dict, 
                                 grid_coords: np.ndarray, config: SpatialInferenceConfig):
        """Store spatial prediction results."""
        # This would typically store to a database or cache
        # For now, we'll store in memory
        if not hasattr(self, 'spatial_predictions'):
            self.spatial_predictions = {}
        
        self.spatial_predictions[variable] = {
            'predictions': predictions,
            'grid_coords': grid_coords,
            'config': config,
            'timestamp': datetime.now(timezone.utc)
        }
    
    async def start_stream_processing(self):
        """Start real-time stream processing."""
        if self.is_processing:
            logger.warning("Stream processing already running")
            return
        
        self.is_processing = True
        logger.info("Starting IoT stream processing")
        
        # Start protocol handlers
        for protocol, handler in self.protocol_handlers.items():
            task = asyncio.create_task(handler())
            self.processing_tasks.append(task)
        
        # Start periodic spatial inference updates
        task = asyncio.create_task(self._periodic_spatial_updates())
        self.processing_tasks.append(task)
    
    async def stop_stream_processing(self):
        """Stop stream processing."""
        self.is_processing = False
        
        # Cancel all tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        self.processing_tasks.clear()
        
        logger.info("Stopped IoT stream processing")
    
    async def _periodic_spatial_updates(self):
        """Periodically update spatial inference models."""
        while self.is_processing:
            try:
                for variable in self.inference_configs:
                    await self._update_spatial_inference(variable)
                
                # Wait for next update cycle
                update_interval = min(
                    config.update_interval_minutes 
                    for config in self.inference_configs.values()
                ) if self.inference_configs else 15
                
                await asyncio.sleep(update_interval * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic spatial updates: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _handle_mqtt(self):
        """Handle MQTT protocol (placeholder)."""
        # This would implement MQTT message handling
        logger.info("MQTT handler started (placeholder)")
        while self.is_processing:
            await asyncio.sleep(1)
    
    async def _handle_async_mqtt(self):
        """Handle async MQTT protocol (placeholder)."""
        # This would implement async MQTT message handling
        logger.info("Async MQTT handler started (placeholder)")
        while self.is_processing:
            await asyncio.sleep(1)
    
    def get_spatial_distribution(self, variable: str, 
                               confidence_level: float = 0.95) -> Optional[Dict]:
        """
        Get current spatial distribution for a variable.
        
        Args:
            variable: Variable name
            confidence_level: Confidence level for uncertainty bounds
            
        Returns:
            Dictionary with spatial distribution data or None if not available
        """
        if not hasattr(self, 'spatial_predictions') or variable not in self.spatial_predictions:
            return None
        
        prediction_data = self.spatial_predictions[variable]
        
        # Format results for API consumption
        result = {
            'variable': variable,
            'timestamp': prediction_data['timestamp'].isoformat(),
            'h3_resolution': prediction_data['config'].h3_resolution,
            'confidence_level': confidence_level,
            'predictions': prediction_data['predictions'],
            'grid_coordinates': prediction_data['grid_coords'].tolist()
        }
        
        return result
    
    def get_measurement_statistics(self) -> Dict:
        """Get statistics about ingested measurements."""
        if not self.measurements:
            return {}
        
        # Basic statistics
        total_measurements = len(self.measurements)
        unique_sensors = len(set(m.sensor_id for m in self.measurements))
        unique_variables = len(set(m.variable for m in self.measurements))
        unique_h3_cells = len(set(m.h3_index for m in self.measurements if m.h3_index))
        
        # Time range
        timestamps = [m.timestamp for m in self.measurements]
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        return {
            'total_measurements': total_measurements,
            'unique_sensors': unique_sensors,
            'unique_variables': unique_variables,
            'unique_h3_cells': unique_h3_cells,
            'time_range': {
                'start': min_time.isoformat(),
                'end': max_time.isoformat()
            },
            'spatial_inference_enabled': len(self.inference_configs) > 0,
            'variables_with_inference': list(self.inference_configs.keys())
        }

class RadiationMonitoringSystem:
    """
    Specialized IoT system for radiation monitoring with enhanced logging and testing.
    
    This class provides a simplified interface for radiation monitoring applications,
    integrating IoT data ingestion, spatial analysis, and Bayesian inference with
    comprehensive logging and quality assurance.
    """
    
    def __init__(self, config: Dict, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        from .registry import SensorRegistry
        self.registry = SensorRegistry(config.get("sensor_networks", {}))
        self.ingestion = IoTDataIngestion(self.registry, config)
        
        # Performance tracking
        self.start_time = time.time()
        self.metrics = {
            "measurements_processed": 0,
            "spatial_inferences": 0,
            "anomalies_detected": 0,
            "errors_encountered": 0
        }
        
        # Quality control
        self.quality_thresholds = config.get("quality_control", {})
        
        self.logger.info("RadiationMonitoringSystem initialized", extra={
            "config_keys": list(config.keys()),
            "sensor_networks": list(config.get("sensor_networks", {}).keys())
        })
    
    def generate_simulated_data(self, sensor_count: int = 100) -> List[Dict]:
        """Generate simulated radiation sensor data for testing."""
        import random
        
        self.logger.info("Generating simulated radiation data", extra={
            "sensor_count": sensor_count,
            "operation": "data_simulation"
        })
        
        start_time = time.time()
        measurements = []
        
        # Global radiation monitoring networks
        networks = ["safecast", "eurdep", "ctbto"]
        
        # Simulate sensors across the globe
        for i in range(sensor_count):
            # Random global coordinates
            lat = random.uniform(-85, 85)  # Avoid extreme polar regions
            lon = random.uniform(-180, 180)
            
            # Background radiation with noise
            background = self.config.get("simulation", {}).get("background_radiation", 0.1)
            noise = self.config.get("simulation", {}).get("noise_level", 0.02)
            radiation_level = max(0, random.gauss(background, noise))
            
            # Add anomalies at specific locations
            anomaly_locations = self.config.get("simulation", {}).get("anomalies", {}).get("locations", [])
            for anomaly in anomaly_locations:
                distance = ((lat - anomaly["lat"])**2 + (lon - anomaly["lon"])**2)**0.5
                if distance < 1.0:  # Within ~111km
                    radiation_level *= anomaly["intensity"]
            
            measurement = {
                "sensor_id": f"sensor_{i:06d}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "variable": "gamma_radiation",
                "value": radiation_level,
                "unit": "μSv/h",
                "latitude": lat,
                "longitude": lon,
                "network": random.choice(networks),
                "quality_flag": "ok" if radiation_level < 10.0 else "high_radiation"
            }
            measurements.append(measurement)
        
        generation_time = time.time() - start_time
        self.logger.info("Simulated data generation complete", extra={
            "measurements_generated": len(measurements),
            "generation_time_seconds": generation_time,
            "operation": "data_simulation"
        })
        
        return measurements
    
    async def process_measurements(self, measurements: List[Dict]) -> Dict:
        """Process a batch of measurements with full logging."""
        self.logger.info("Starting measurement processing", extra={
            "measurement_count": len(measurements),
            "operation": "batch_processing"
        })
        
        start_time = time.time()
        results = {
            "processed": 0,
            "failed": 0,
            "spatial_cells": set(),
            "anomalies": [],
            "quality_issues": []
        }
        
        for measurement in measurements:
            try:
                # Convert to SensorMeasurement object
                sensor_measurement = self.ingestion._dict_to_measurement(measurement)
                
                # Quality control
                quality_result = self._quality_control(sensor_measurement)
                if not quality_result["passed"]:
                    results["quality_issues"].append({
                        "sensor_id": sensor_measurement.sensor_id,
                        "issues": quality_result["issues"]
                    })
                
                # Anomaly detection
                if self._is_anomaly(sensor_measurement):
                    results["anomalies"].append({
                        "sensor_id": sensor_measurement.sensor_id,
                        "location": [sensor_measurement.latitude, sensor_measurement.longitude],
                        "value": sensor_measurement.value,
                        "h3_index": sensor_measurement.h3_index
                    })
                    self.metrics["anomalies_detected"] += 1
                
                # Ingest measurement
                success = await self.ingestion.ingest_measurement(sensor_measurement)
                if success:
                    results["processed"] += 1
                    results["spatial_cells"].add(sensor_measurement.h3_index)
                    self.metrics["measurements_processed"] += 1
                else:
                    results["failed"] += 1
                    self.metrics["errors_encountered"] += 1
                
            except Exception as e:
                self.logger.error("Error processing measurement", extra={
                    "error": str(e),
                    "measurement_id": measurement.get("sensor_id", "unknown"),
                    "operation": "measurement_processing"
                })
                results["failed"] += 1
                self.metrics["errors_encountered"] += 1
        
        processing_time = time.time() - start_time
        results["spatial_cells"] = list(results["spatial_cells"])
        results["processing_time"] = processing_time
        
        self.logger.info("Measurement processing complete", extra={
            "processed": results["processed"],
            "failed": results["failed"],
            "unique_h3_cells": len(results["spatial_cells"]),
            "anomalies_detected": len(results["anomalies"]),
            "processing_time_seconds": processing_time,
            "operation": "batch_processing"
        })
        
        return results
    
    def _quality_control(self, measurement: SensorMeasurement) -> Dict:
        """Perform quality control on a measurement."""
        validation = self.quality_thresholds.get("sensor_validation", {})
        
        issues = []
        
        # Check radiation value range
        min_rad = validation.get("min_radiation", 0.0)
        max_rad = validation.get("max_radiation", 100.0)
        if not (min_rad <= measurement.value <= max_rad):
            issues.append(f"Radiation value {measurement.value} outside range [{min_rad}, {max_rad}]")
        
        # Check coordinate validity
        if not (-90 <= measurement.latitude <= 90):
            issues.append(f"Invalid latitude: {measurement.latitude}")
        if not (-180 <= measurement.longitude <= 180):
            issues.append(f"Invalid longitude: {measurement.longitude}")
        
        # Check timestamp validity
        now = datetime.now(timezone.utc)
        time_diff = abs((now - measurement.timestamp).total_seconds())
        if time_diff > 24 * 3600:  # More than 24 hours old
            issues.append(f"Timestamp too old: {time_diff} seconds")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "quality_score": 1.0 if len(issues) == 0 else max(0, 1.0 - len(issues) * 0.2)
        }
    
    def _is_anomaly(self, measurement: SensorMeasurement) -> bool:
        """Simple anomaly detection based on statistical thresholds."""
        anomaly_config = self.config.get("anomaly_detection", {}).get("statistical", {})
        
        # Get background radiation level
        background = self.config.get("simulation", {}).get("background_radiation", 0.1)
        noise = self.config.get("simulation", {}).get("noise_level", 0.02)
        
        # Calculate z-score
        z_score = abs(measurement.value - background) / noise
        
        # Check against thresholds
        mild_threshold = anomaly_config.get("threshold_mild", 2.0)
        return z_score >= mild_threshold
    
    def setup_spatial_inference(self, variable: str = "gamma_radiation"):
        """Setup Bayesian spatial inference for radiation monitoring."""
        bayes_config = self.config.get("bayesian_inference", {})
        
        inference_config = SpatialInferenceConfig(
            variable=variable,
            h3_resolution=self.config.get("spatial", {}).get("h3_resolution", 5),
            temporal_window_hours=1.0,
            spatial_range_km=bayes_config.get("covariance", {}).get("length_scale", 50000) / 1000,
            covariance_function=bayes_config.get("covariance", {}).get("function", "matern_52"),
            length_scale=bayes_config.get("covariance", {}).get("length_scale", 50000),
            noise_variance=bayes_config.get("covariance", {}).get("noise_variance", 0.01),
            confidence_levels=bayes_config.get("confidence_levels", [0.68, 0.95])
        )
        
        self.ingestion.setup_spatial_inference(inference_config)
        
        self.logger.info("Spatial inference configured", extra={
            "variable": variable,
            "h3_resolution": inference_config.h3_resolution,
            "covariance_function": inference_config.covariance_function,
            "length_scale": inference_config.length_scale,
            "operation": "spatial_inference_setup"
        })
    
    async def perform_spatial_inference(self, variable: str = "gamma_radiation") -> Dict:
        """Perform Bayesian spatial inference on collected measurements."""
        self.logger.info("Starting spatial inference", extra={
            "variable": variable,
            "operation": "spatial_inference"
        })
        
        start_time = time.time()
        
        # Trigger spatial inference update
        await self.ingestion._update_spatial_inference(variable)
        
        # Get results
        results = self.ingestion.get_spatial_distribution(variable)
        
        inference_time = time.time() - start_time
        self.metrics["spatial_inferences"] += 1
        
        if results:
            self.logger.info("Spatial inference complete", extra={
                "variable": variable,
                "prediction_cells": len(results.get("predictions", [])),
                "mean_prediction": np.mean(results.get("predictions", [])) if results.get("predictions") else 0,
                "inference_time_seconds": inference_time,
                "operation": "spatial_inference"
            })
        else:
            self.logger.warning("Spatial inference returned no results", extra={
                "variable": variable,
                "operation": "spatial_inference"
            })
        
        return results or {}
    
    def get_system_metrics(self) -> Dict:
        """Get comprehensive system performance metrics."""
        runtime = time.time() - self.start_time
        
        metrics = {
            "runtime_seconds": runtime,
            "measurements_per_second": self.metrics["measurements_processed"] / max(runtime, 1),
            "error_rate": self.metrics["errors_encountered"] / max(self.metrics["measurements_processed"], 1),
            "anomaly_rate": self.metrics["anomalies_detected"] / max(self.metrics["measurements_processed"], 1),
            **self.metrics
        }
        
        self.logger.info("System metrics collected", extra=metrics)
        return metrics
    
    def validate_system_health(self) -> Dict:
        """Validate overall system health for testing purposes."""
        metrics = self.get_system_metrics()
        
        health_checks = {
            "measurements_processing": metrics["measurements_processed"] > 0,
            "error_rate_acceptable": metrics["error_rate"] < 0.1,  # Less than 10% errors
            "performance_acceptable": metrics["measurements_per_second"] > 10,  # At least 10/sec
            "spatial_inference_working": metrics["spatial_inferences"] > 0
        }
        
        overall_health = all(health_checks.values())
        
        health_result = {
            "overall_healthy": overall_health,
            "checks": health_checks,
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info("System health validation", extra={
            "overall_healthy": overall_health,
            "failed_checks": [k for k, v in health_checks.items() if not v],
            "operation": "health_check"
        })
        
        return health_result


class GlobalMonitoringSystem:
    """Global-scale radiation monitoring system for demonstration."""
    
    def __init__(self, config: Dict, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.radiation_system = RadiationMonitoringSystem(config, logger)
        
    async def run_monitoring_cycle(self) -> Dict:
        """Run a complete monitoring cycle."""
        self.logger.info("Starting global monitoring cycle", extra={
            "operation": "monitoring_cycle"
        })
        
        # Generate simulated data
        sensor_count = self.config.get("simulation", {}).get("sensor_count", 1500)
        measurements = self.radiation_system.generate_simulated_data(sensor_count)
        
        # Setup spatial inference
        self.radiation_system.setup_spatial_inference()
        
        # Process measurements
        processing_results = await self.radiation_system.process_measurements(measurements)
        
        # Perform spatial inference
        inference_results = await self.radiation_system.perform_spatial_inference()
        
        # Get system metrics
        system_metrics = self.radiation_system.get_system_metrics()
        
        # Validate system health
        health_status = self.radiation_system.validate_system_health()
        
        cycle_results = {
            "processing": processing_results,
            "inference": inference_results,
            "metrics": system_metrics,
            "health": health_status
        }
        
        self.logger.info("Global monitoring cycle complete", extra={
            "sensors_processed": processing_results["processed"],
            "anomalies_detected": len(processing_results["anomalies"]),
            "system_healthy": health_status["overall_healthy"],
            "operation": "monitoring_cycle"
        })
        
        return cycle_results 