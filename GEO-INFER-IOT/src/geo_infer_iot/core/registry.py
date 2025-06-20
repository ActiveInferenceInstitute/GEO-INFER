"""
Sensor Registry Module

This module manages the registration and metadata of IoT sensor networks and devices,
integrating with H3 spatial indexing for efficient spatial queries.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid

import h3

logger = logging.getLogger(__name__)

@dataclass
class SensorMetadata:
    """Metadata for an individual sensor."""
    sensor_id: str
    network_id: str
    sensor_type: str
    latitude: float
    longitude: float
    h3_index: str = ""
    h3_resolution: int = 8
    status: str = "active"
    metadata: Dict = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.h3_index:
            self.h3_index = h3.geo_to_h3(
                self.latitude, self.longitude, self.h3_resolution
            )

@dataclass 
class SensorNetwork:
    """Represents a sensor network with spatial bounds."""
    network_id: str
    name: str
    protocol: str
    spatial_bounds: Dict
    sensor_types: List[str]
    sensor_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
class SensorRegistry:
    """
    Registry for managing IoT sensor networks and individual sensors.
    
    Provides capabilities for:
    - Registering sensor networks and individual sensors
    - Spatial queries using H3 indexing
    - Sensor metadata management
    - Network topology tracking
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.networks: Dict[str, SensorNetwork] = {}
        self.sensors: Dict[str, SensorMetadata] = {}
        self.h3_spatial_index: Dict[str, Set[str]] = {}  # h3_index -> sensor_ids
        
        logger.info("Sensor Registry initialized")
    
    def register_network(self, **kwargs) -> SensorNetwork:
        """Register a new sensor network."""
        network_id = kwargs.get('network_id') or str(uuid.uuid4())
        
        network = SensorNetwork(
            network_id=network_id,
            name=kwargs['name'],
            protocol=kwargs['protocol'],
            spatial_bounds=kwargs['spatial_bounds'],
            sensor_types=kwargs['sensor_types']
        )
        
        self.networks[network_id] = network
        logger.info(f"Registered sensor network: {network.name}")
        return network
    
    def register_sensor(self, sensor_info: Dict) -> SensorMetadata:
        """Register an individual sensor."""
        sensor = SensorMetadata(**sensor_info)
        
        self.sensors[sensor.sensor_id] = sensor
        
        # Add to spatial index
        if sensor.h3_index not in self.h3_spatial_index:
            self.h3_spatial_index[sensor.h3_index] = set()
        self.h3_spatial_index[sensor.h3_index].add(sensor.sensor_id)
        
        # Update network sensor count
        if sensor.network_id in self.networks:
            self.networks[sensor.network_id].sensor_count += 1
        
        logger.info(f"Registered sensor: {sensor.sensor_id}")
        return sensor
    
    def get_sensors_in_h3_cell(self, h3_index: str) -> List[SensorMetadata]:
        """Get all sensors in a specific H3 cell."""
        sensor_ids = self.h3_spatial_index.get(h3_index, set())
        return [self.sensors[sid] for sid in sensor_ids if sid in self.sensors]
    
    def get_sensors_by_type(self, sensor_type: str) -> List[SensorMetadata]:
        """Get all sensors of a specific type."""
        return [s for s in self.sensors.values() if s.sensor_type == sensor_type]
    
    def get_sensors_in_area(self, bounds: Dict, h3_resolution: int = 8) -> List[SensorMetadata]:
        """Get sensors within geographic bounds using H3 spatial indexing."""
        # This would use H3 polyfill to get all cells in the area
        # For now, simple implementation
        matching_sensors = []
        
        lat_min = bounds['lat_min']
        lat_max = bounds['lat_max']
        lon_min = bounds['lon_min']
        lon_max = bounds['lon_max']
        
        for sensor in self.sensors.values():
            if (lat_min <= sensor.latitude <= lat_max and 
                lon_min <= sensor.longitude <= lon_max):
                matching_sensors.append(sensor)
        
        return matching_sensors 