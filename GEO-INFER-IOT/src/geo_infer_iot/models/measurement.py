"""
Measurement Data Models

This module defines comprehensive data models for IoT sensor measurements,
including batch processing, quality metadata, and temporal analysis.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator, root_validator
import numpy as np
import h3

logger = logging.getLogger(__name__)

class MeasurementQuality(BaseModel):
    """Quality metadata for sensor measurements."""
    quality_score: float = Field(1.0, ge=0.0, le=1.0, description="Overall quality score")
    validation_checks: List[str] = Field(default_factory=list, description="Validation checks performed")
    outlier_score: Optional[float] = Field(None, description="Outlier detection score")
    calibration_applied: bool = Field(False, description="Whether calibration was applied")
    uncertainty_estimate: Optional[float] = Field(None, description="Measurement uncertainty")
    quality_flags: List[str] = Field(default_factory=list, description="Quality flags")

    def add_flag(self, flag: str):
        """Add a quality flag."""
        if flag not in self.quality_flags:
            self.quality_flags.append(flag)

    def is_valid(self) -> bool:
        """Check if measurement meets quality standards."""
        return self.quality_score >= 0.7 and not any(flag in ['invalid', 'corrupted'] for flag in self.quality_flags)

class Measurement(BaseModel):
    """Individual sensor measurement data model."""
    measurement_id: str = Field(..., description="Unique measurement identifier")
    sensor_id: str = Field(..., description="ID of the sensor that made this measurement")

    # Core measurement data
    variable: str = Field(..., description="Measured variable (e.g., temperature, humidity)")
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.now, description="Measurement timestamp")

    # Location information
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude in decimal degrees")
    h3_index: Optional[str] = Field(None, description="H3 hexagonal index")
    h3_resolution: int = Field(8, ge=0, le=15, description="H3 resolution level")

    # Quality and metadata
    quality: MeasurementQuality = Field(default_factory=MeasurementQuality, description="Quality metadata")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional measurement metadata")

    # Processing information
    processed_at: Optional[datetime] = Field(None, description="When measurement was processed")
    processing_version: Optional[str] = Field(None, description="Processing pipeline version")

    @validator('h3_index')
    def validate_h3_index(cls, v, values):
        """Validate H3 index format."""
        if v and not h3.h3_is_valid(v):
            raise ValueError(f"Invalid H3 index: {v}")
        return v

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-generate H3 index if coordinates provided but not h3_index
        if (self.latitude is not None and self.longitude is not None and
            not self.h3_index and self.h3_resolution):
            self.h3_index = h3.latlng_to_cell(self.latitude, self.longitude, self.h3_resolution)

    def update_location(self, latitude: float, longitude: float, h3_resolution: int = None):
        """Update measurement location and recalculate H3 index."""
        self.latitude = latitude
        self.longitude = longitude

        if h3_resolution:
            self.h3_resolution = h3_resolution

        self.h3_index = h3.latlng_to_cell(latitude, longitude, self.h3_resolution)

    def apply_calibration(self, calibration_params: Dict):
        """Apply calibration to the measurement value."""
        if calibration_params.get('method') == 'linear':
            slope = calibration_params.get('slope', 1.0)
            offset = calibration_params.get('offset', 0.0)
            self.value = slope * self.value + offset
            self.quality.calibration_applied = True
        elif calibration_params.get('method') == 'polynomial':
            coeffs = calibration_params.get('coefficients', [1.0])
            self.value = np.polyval(coeffs, self.value)
            self.quality.calibration_applied = True

    def get_location_info(self) -> Dict:
        """Get comprehensive location information."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'h3_index': self.h3_index,
            'h3_resolution': self.h3_resolution,
            'coordinate_system': 'WGS84'
        }

    def get_temporal_info(self) -> Dict:
        """Get temporal information about the measurement."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'age_seconds': (datetime.now() - self.timestamp).total_seconds(),
            'processing_version': self.processing_version
        }

class MeasurementBatch(BaseModel):
    """Batch of sensor measurements for efficient processing."""
    batch_id: str = Field(..., description="Unique batch identifier")
    measurements: List[Measurement] = Field(..., description="List of measurements in batch")

    # Batch metadata
    sensor_ids: List[str] = Field(default_factory=list, description="Unique sensor IDs in batch")
    variables: List[str] = Field(default_factory=list, description="Unique variables in batch")
    time_range: Dict[str, datetime] = Field(default_factory=dict, description="Time range of batch")

    # Batch processing information
    batch_size: int = Field(..., description="Number of measurements in batch")
    created_at: datetime = Field(default_factory=datetime.now, description="Batch creation timestamp")
    processed_at: Optional[datetime] = Field(None, description="Batch processing timestamp")

    # Quality summary
    quality_summary: Dict[str, Any] = Field(default_factory=dict, description="Quality summary for batch")

    @validator('measurements')
    def validate_measurements(cls, v):
        """Validate measurements in batch."""
        if len(v) == 0:
            raise ValueError("Batch must contain at least one measurement")
        return v

    def __init__(self, **data):
        super().__init__(**data)

        # Calculate derived fields
        self.sensor_ids = list(set(m.sensor_id for m in self.measurements))
        self.variables = list(set(m.variable for m in self.measurements))

        if self.measurements:
            timestamps = [m.timestamp for m in self.measurements]
            self.time_range = {
                'start': min(timestamps),
                'end': max(timestamps)
            }

        # Calculate quality summary
        self._calculate_quality_summary()

    def _calculate_quality_summary(self):
        """Calculate quality summary for the batch."""
        if not self.measurements:
            return

        quality_scores = [m.quality.quality_score for m in self.measurements]
        valid_measurements = [m for m in self.measurements if m.quality.is_valid()]

        self.quality_summary = {
            'total_measurements': len(self.measurements),
            'valid_measurements': len(valid_measurements),
            'invalid_measurements': len(self.measurements) - len(valid_measurements),
            'average_quality_score': np.mean(quality_scores),
            'quality_score_std': np.std(quality_scores),
            'quality_distribution': {
                'excellent': len([m for m in self.measurements if m.quality.quality_score >= 0.9]),
                'good': len([m for m in self.measurements if 0.7 <= m.quality.quality_score < 0.9]),
                'poor': len([m for m in self.measurements if m.quality.quality_score < 0.7])
            }
        }

    def add_measurement(self, measurement: Measurement):
        """Add a measurement to the batch."""
        self.measurements.append(measurement)
        self.batch_size = len(self.measurements)

        # Update derived fields
        if measurement.sensor_id not in self.sensor_ids:
            self.sensor_ids.append(measurement.sensor_id)
        if measurement.variable not in self.variables:
            self.variables.append(measurement.variable)

        # Update time range
        if not self.time_range:
            self.time_range = {'start': measurement.timestamp, 'end': measurement.timestamp}
        else:
            self.time_range['start'] = min(self.time_range['start'], measurement.timestamp)
            self.time_range['end'] = max(self.time_range['end'], measurement.timestamp)

        # Recalculate quality summary
        self._calculate_quality_summary()

    def filter_by_quality(self, min_quality_score: float = 0.7) -> 'MeasurementBatch':
        """Filter batch to measurements meeting quality threshold."""
        filtered_measurements = [m for m in self.measurements if m.quality.quality_score >= min_quality_score]

        if not filtered_measurements:
            # Return empty batch if no measurements meet criteria
            return MeasurementBatch(
                batch_id=f"{self.batch_id}_filtered",
                measurements=[],
                batch_size=0
            )

        return MeasurementBatch(
            batch_id=f"{self.batch_id}_filtered",
            measurements=filtered_measurements,
            batch_size=len(filtered_measurements)
        )

    def filter_by_variable(self, variable: str) -> 'MeasurementBatch':
        """Filter batch to specific variable."""
        filtered_measurements = [m for m in self.measurements if m.variable == variable]

        return MeasurementBatch(
            batch_id=f"{self.batch_id}_{variable}",
            measurements=filtered_measurements,
            batch_size=len(filtered_measurements)
        )

    def filter_by_sensor(self, sensor_id: str) -> 'MeasurementBatch':
        """Filter batch to specific sensor."""
        filtered_measurements = [m for m in self.measurements if m.sensor_id == sensor_id]

        return MeasurementBatch(
            batch_id=f"{self.batch_id}_{sensor_id}",
            measurements=filtered_measurements,
            batch_size=len(filtered_measurements)
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of the batch."""
        if not self.measurements:
            return {}

        values = [m.value for m in self.measurements]

        # Basic statistics
        stats = {
            'count': len(values),
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'median': np.median(values)
        }

        # Variable-specific statistics
        variable_stats = {}
        for variable in self.variables:
            var_values = [m.value for m in self.measurements if m.variable == variable]
            if var_values:
                variable_stats[variable] = {
                    'count': len(var_values),
                    'mean': np.mean(var_values),
                    'std': np.std(var_values),
                    'min': np.min(var_values),
                    'max': np.max(var_values)
                }

        return {
            'batch_statistics': stats,
            'variable_statistics': variable_stats,
            'sensor_count': len(self.sensor_ids),
            'time_range': {
                'start': self.time_range['start'].isoformat(),
                'end': self.time_range['end'].isoformat(),
                'duration_seconds': (self.time_range['end'] - self.time_range['start']).total_seconds()
            },
            'quality_summary': self.quality_summary
        }

class MeasurementStream(BaseModel):
    """Real-time measurement stream configuration."""
    stream_id: str = Field(..., description="Unique stream identifier")
    sensor_ids: List[str] = Field(..., description="Sensor IDs in this stream")
    variables: List[str] = Field(..., description="Variables being streamed")

    # Stream configuration
    protocol: str = Field("websocket", description="Streaming protocol")
    format: str = Field("json", description="Data format")
    compression: Optional[str] = Field(None, description="Compression method")

    # Quality and filtering
    quality_filter: Optional[float] = Field(None, description="Minimum quality score filter")
    outlier_filter: bool = Field(True, description="Enable outlier filtering")

    # Performance settings
    buffer_size: int = Field(1000, description="Stream buffer size")
    flush_interval_seconds: int = Field(5, description="Buffer flush interval")

    # Status
    is_active: bool = Field(True, description="Stream active status")
    created_at: datetime = Field(default_factory=datetime.now)

    def add_sensor(self, sensor_id: str):
        """Add a sensor to the stream."""
        if sensor_id not in self.sensor_ids:
            self.sensor_ids.append(sensor_id)

    def remove_sensor(self, sensor_id: str):
        """Remove a sensor from the stream."""
        if sensor_id in self.sensor_ids:
            self.sensor_ids.remove(sensor_id)

    def add_variable(self, variable: str):
        """Add a variable to the stream."""
        if variable not in self.variables:
            self.variables.append(variable)

    def remove_variable(self, variable: str):
        """Remove a variable from the stream."""
        if variable in self.variables:
            self.variables.remove(variable)

class MeasurementValidation(BaseModel):
    """Measurement validation rules and constraints."""
    validation_id: str = Field(..., description="Unique validation rule ID")

    # Target specification
    sensor_id: Optional[str] = Field(None, description="Target sensor ID (None for all sensors)")
    variable: Optional[str] = Field(None, description="Target variable (None for all variables)")

    # Validation rules
    value_range: Optional[Dict[str, float]] = Field(None, description="Min/max value constraints")
    temporal_constraints: Optional[Dict[str, Any]] = Field(None, description="Temporal validation rules")
    spatial_constraints: Optional[Dict[str, Any]] = Field(None, description="Spatial validation rules")

    # Quality requirements
    min_quality_score: float = Field(0.7, description="Minimum required quality score")
    max_uncertainty: Optional[float] = Field(None, description="Maximum allowed uncertainty")

    # Validation behavior
    action_on_failure: str = Field("flag", description="Action when validation fails")
    notification_required: bool = Field(False, description="Send notification on failure")

    # Metadata
    description: str = Field("", description="Validation rule description")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator('action_on_failure')
    def validate_action(cls, v):
        """Validate action on failure."""
        valid_actions = ['flag', 'reject', 'correct', 'notify']
        if v not in valid_actions:
            raise ValueError(f"Invalid action '{v}'. Must be one of: {valid_actions}")
        return v

    def validate_measurement(self, measurement: Measurement) -> bool:
        """Validate a measurement against these rules."""
        # Check sensor ID filter
        if self.sensor_id and measurement.sensor_id != self.sensor_id:
            return True  # Skip validation for non-target sensors

        # Check variable filter
        if self.variable and measurement.variable != self.variable:
            return True  # Skip validation for non-target variables

        # Check quality score
        if measurement.quality.quality_score < self.min_quality_score:
            return False

        # Check uncertainty
        if (self.max_uncertainty and
            measurement.quality.uncertainty_estimate and
            measurement.quality.uncertainty_estimate > self.max_uncertainty):
            return False

        # Check value range
        if self.value_range:
            min_val = self.value_range.get('min')
            max_val = self.value_range.get('max')

            if min_val is not None and measurement.value < min_val:
                return False
            if max_val is not None and measurement.value > max_val:
                return False

        return True
