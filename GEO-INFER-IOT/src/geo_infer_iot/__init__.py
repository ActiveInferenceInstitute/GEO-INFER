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
from geo_infer_iot.core.ingestion import IoTDataIngestion
from geo_infer_iot.core.registry import SensorRegistry

# These modules don't exist yet - commenting out for now
# from geo_infer_iot.core.spatial_fusion import SpatialDataFusion
# from geo_infer_iot.core.quality_control import QualityController
# from geo_infer_iot.api.sensor_api import SensorAPI
# from geo_infer_iot.api.streaming_api import StreamingAPI
# from geo_infer_iot.api.inference_api import BayesianInferenceAPI
# from geo_infer_iot.models.sensor import Sensor, SensorNetwork
# from geo_infer_iot.models.measurement import Measurement, MeasurementBatch
# from geo_infer_iot.models.network import NetworkTopology
# from geo_infer_iot.utils.calibration import SensorCalibration
# from geo_infer_iot.utils.interpolation import SpatialInterpolation
# from geo_infer_iot.utils.visualization import IoTVisualization

__version__ = "0.1.0"

__all__ = [
    # Core functionality (available)
    "IoTDataIngestion",
    "SensorRegistry", 
    
    # High-level convenience classes
    "IoTSystem",
    "BayesianSpatialInference", 
    "GlobalMonitoringSystem",
    "MultiModalFusion",
    "AdaptiveSampling",
    "PredictiveMaintenance"
]

# High-level convenience classes
class IoTSystem:
    """
    High-level interface for IoT sensor systems integration.
    
    This class provides a simplified interface for setting up and managing
    IoT sensor networks with spatial analysis capabilities.
    """
    
    def __init__(self, config=None):
        self.registry = SensorRegistry(config)
        self.ingestion = IoTDataIngestion(self.registry, config)
        # self.fusion = SpatialDataFusion()  # Not implemented yet
        # self.quality = QualityController()  # Not implemented yet
        
    def register_network(self, **kwargs):
        """Register a new sensor network."""
        return self.registry.register_network(**kwargs)
        
    def start_processing(self):
        """Start real-time data processing."""
        return self.ingestion.start_stream_processing()
        
    def setup_spatial_inference(self, **kwargs):
        """Setup Bayesian spatial inference."""
        return BayesianSpatialInference(**kwargs)

class BayesianSpatialInference:
    """
    Bayesian spatial inference for IoT sensor data.
    
    Converts point sensor measurements to continuous spatial distributions
    using Gaussian process models and H3 spatial indexing.
    """
    
    def __init__(self, variable, spatial_resolution, temporal_window):
        self.variable = variable
        self.spatial_resolution = spatial_resolution  
        self.temporal_window = temporal_window
        
    def infer_spatial_distribution(self, sensor_data, priors, update_interval):
        """Perform Bayesian spatial inference."""
        # Implementation would integrate with GEO-INFER-BAYES
        pass
        
    def get_posterior_map(self, confidence_intervals):
        """Get current posterior spatial distribution."""
        # Implementation would return spatial map with uncertainties
        pass

class GlobalMonitoringSystem:
    """
    Global-scale environmental monitoring system.
    
    Integrates multiple sensor networks for global environmental monitoring
    with real-time updates and alert systems.
    """
    
    def __init__(self, variable, sensor_networks, update_frequency):
        self.variable = variable
        self.sensor_networks = sensor_networks
        self.update_frequency = update_frequency
        
    def get_current_global_distribution(self, confidence_level, spatial_resolution):
        """Get current global distribution map."""
        # Implementation would aggregate multiple networks
        pass

# Convenience imports for common workflows
class MultiModalFusion:
    """Multi-modal sensor fusion capabilities."""
    pass

class AdaptiveSampling:
    """Adaptive sensor network optimization."""
    pass
    
class PredictiveMaintenance:
    """Predictive maintenance for sensor networks."""
    pass

# Classes already included in __all__ above 