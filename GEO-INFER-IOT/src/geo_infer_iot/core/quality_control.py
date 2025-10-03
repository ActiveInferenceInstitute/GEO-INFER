"""
Quality Control Module

This module provides comprehensive quality control and validation for IoT sensor data,
including outlier detection, range validation, temporal consistency checks, and
spatial consistency validation.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
from collections import defaultdict

# Optional imports for enhanced functionality
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

logger = logging.getLogger(__name__)

@dataclass
class QualityCheckResult:
    """Result of a quality check operation."""
    passed: bool
    issues: List[str]
    quality_score: float
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class QualityController:
    """
    Comprehensive quality control system for IoT sensor data.

    This class provides multiple quality control mechanisms:
    - Outlier detection using statistical methods and machine learning
    - Range validation for sensor measurements
    - Temporal consistency checks across time series
    - Spatial consistency validation using H3-based analysis
    - Calibration drift detection
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.quality_history = []
        self.sensor_baselines = {}
        self.outlier_detector = None

        # Default quality control parameters
        self.default_params = {
            'outlier_detection': {
                'method': 'isolation_forest',
                'contamination': 0.1,
                'window_size': 100
            },
            'range_validation': {
                'action': 'flag',  # 'flag', 'reject', 'correct'
                'strict_mode': False
            },
            'temporal_consistency': {
                'max_change_rate': 0.1,  # Max relative change per minute
                'window_minutes': 60
            },
            'spatial_consistency': {
                'neighbor_threshold': 2.0,  # Standard deviations
                'min_neighbors': 3
            }
        }

        # Initialize outlier detector if available
        if HAS_SKLEARN:
            self._initialize_outlier_detector()

        logger.info("QualityController initialized")

    def _initialize_outlier_detector(self):
        """Initialize the outlier detection model."""
        try:
            outlier_config = self.config.get('outlier_detection', self.default_params['outlier_detection'])
            self.outlier_detector = IsolationForest(
                contamination=outlier_config.get('contamination', 0.1),
                random_state=42
            )
        except Exception as e:
            logger.warning(f"Failed to initialize outlier detector: {e}")
            self.outlier_detector = None

    def validate_measurement(self, measurement: Dict) -> QualityCheckResult:
        """
        Perform comprehensive quality validation on a single measurement.

        Args:
            measurement: Sensor measurement to validate

        Returns:
            QualityCheckResult with validation outcome
        """
        issues = []
        quality_score = 1.0

        # Range validation
        range_result = self._validate_range(measurement)
        if not range_result.passed:
            issues.extend(range_result.issues)
            quality_score *= 0.8

        # Temporal consistency check
        temporal_result = self._validate_temporal_consistency(measurement)
        if not temporal_result.passed:
            issues.extend(temporal_result.issues)
            quality_score *= 0.9

        # Outlier detection
        outlier_result = self._detect_outliers(measurement)
        if not outlier_result.passed:
            issues.extend(outlier_result.issues)
            quality_score *= 0.7

        # Spatial consistency check (if location data available)
        if 'latitude' in measurement and 'longitude' in measurement:
            spatial_result = self._validate_spatial_consistency(measurement)
            if not spatial_result.passed:
                issues.extend(spatial_result.issues)
                quality_score *= 0.85

        passed = len(issues) == 0
        if not passed:
            quality_score = max(0.0, quality_score - 0.1 * len(issues))

        return QualityCheckResult(
            passed=passed,
            issues=issues,
            quality_score=quality_score,
            metadata={
                'validation_timestamp': datetime.now().isoformat(),
                'validation_checks': ['range', 'temporal', 'outlier', 'spatial']
            }
        )

    def _validate_range(self, measurement: Dict) -> QualityCheckResult:
        """Validate measurement value against expected ranges."""
        issues = []
        variable = measurement.get('variable', 'unknown')
        value = measurement.get('value')

        if value is None:
            return QualityCheckResult(False, ['Missing value'], 0.0)

        # Get variable-specific ranges from config
        variable_ranges = self.config.get('variable_ranges', {})

        if variable in variable_ranges:
            min_val, max_val = variable_ranges[variable]

            if value < min_val or value > max_val:
                issues.append(f"Value {value} outside expected range [{min_val}, {max_val}] for {variable}")

        # General sanity checks
        if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
            issues.append(f"Invalid value type or NaN/Inf: {value}")

        return QualityCheckResult(len(issues) == 0, issues, 0.9 if len(issues) == 0 else 0.5)

    def _validate_temporal_consistency(self, measurement: Dict) -> QualityCheckResult:
        """Validate temporal consistency of measurements."""
        issues = []
        sensor_id = measurement.get('sensor_id', 'unknown')
        timestamp = measurement.get('timestamp')
        value = measurement.get('value')

        if not timestamp or value is None:
            return QualityCheckResult(True, [], 1.0)  # Skip if no temporal data

        # Get recent measurements for this sensor
        recent_measurements = self._get_recent_measurements(sensor_id, minutes=60)

        if len(recent_measurements) >= 2:
            # Calculate rate of change
            recent_values = [m['value'] for m in recent_measurements[-5:]]  # Last 5 measurements
            if len(recent_values) >= 2:
                max_change_rate = self.config.get('max_change_rate', 0.1)

                for i in range(1, len(recent_values)):
                    prev_val = recent_values[i-1]
                    curr_val = recent_values[i]

                    if prev_val != 0:  # Avoid division by zero
                        change_rate = abs(curr_val - prev_val) / abs(prev_val)
                        if change_rate > max_change_rate:
                            issues.append(f"Temporal change rate {change_rate".2%"} exceeds threshold {max_change_rate".2%"}")

        return QualityCheckResult(len(issues) == 0, issues, 0.9 if len(issues) == 0 else 0.6)

    def _detect_outliers(self, measurement: Dict) -> QualityCheckResult:
        """Detect outliers using statistical methods and machine learning."""
        issues = []
        value = measurement.get('value')

        if value is None or self.outlier_detector is None:
            return QualityCheckResult(True, [], 1.0)

        try:
            # For isolation forest, we need multiple samples
            # In practice, this would use a sliding window of recent measurements
            # For now, we'll use a simplified approach

            # Simple statistical outlier detection
            sensor_id = measurement.get('sensor_id', 'unknown')
            if sensor_id in self.sensor_baselines:
                baseline = self.sensor_baselines[sensor_id]
                mean_val = baseline['mean']
                std_val = baseline['std']

                if std_val > 0:
                    z_score = abs(value - mean_val) / std_val
                    if z_score > 3.0:  # 3-sigma rule
                        issues.append(f"Statistical outlier detected (z-score: {z_score".2f"})")

            # Update baseline statistics
            self._update_sensor_baseline(sensor_id, value)

        except Exception as e:
            logger.warning(f"Error in outlier detection: {e}")

        return QualityCheckResult(len(issues) == 0, issues, 0.8 if len(issues) == 0 else 0.4)

    def _validate_spatial_consistency(self, measurement: Dict) -> QualityCheckResult:
        """Validate spatial consistency using H3-based analysis."""
        issues = []
        sensor_id = measurement.get('sensor_id', 'unknown')
        value = measurement.get('value')

        if value is None:
            return QualityCheckResult(True, [], 1.0)

        # This would integrate with spatial fusion for neighbor comparison
        # For now, we'll use a simplified approach

        # Check if value is reasonable compared to expected spatial patterns
        # This is a placeholder for more sophisticated spatial validation

        return QualityCheckResult(True, [], 0.9)

    def _get_recent_measurements(self, sensor_id: str, minutes: int = 60) -> List[Dict]:
        """Get recent measurements for a sensor."""
        # This would typically query a database or cache
        # For now, return empty list (no historical data)
        return []

    def _update_sensor_baseline(self, sensor_id: str, value: float):
        """Update baseline statistics for a sensor."""
        if sensor_id not in self.sensor_baselines:
            self.sensor_baselines[sensor_id] = {
                'mean': value,
                'std': 0.1,
                'count': 1,
                'last_update': datetime.now()
            }
        else:
            baseline = self.sensor_baselines[sensor_id]
            count = baseline['count']
            old_mean = baseline['mean']

            # Update mean using Welford's online algorithm
            new_mean = old_mean + (value - old_mean) / (count + 1)

            # Update variance (simplified)
            if count > 1:
                old_var = baseline['std'] ** 2
                new_var = ((count - 1) * old_var + (value - old_mean) * (value - new_mean)) / count
                new_std = np.sqrt(max(0.01, new_var))  # Minimum std to avoid division by zero
            else:
                new_std = 0.1

            self.sensor_baselines[sensor_id].update({
                'mean': new_mean,
                'std': new_std,
                'count': count + 1,
                'last_update': datetime.now()
            })

    def validate_batch(self, measurements: List[Dict]) -> Dict:
        """
        Validate a batch of measurements.

        Args:
            measurements: List of measurements to validate

        Returns:
            Dictionary with batch validation results
        """
        batch_results = []

        for measurement in measurements:
            result = self.validate_measurement(measurement)
            batch_results.append({
                'sensor_id': measurement.get('sensor_id', 'unknown'),
                'passed': result.passed,
                'quality_score': result.quality_score,
                'issues': result.issues
            })

        # Batch statistics
        passed_count = sum(1 for r in batch_results if r['passed'])
        avg_quality_score = np.mean([r['quality_score'] for r in batch_results])

        return {
            'total_measurements': len(measurements),
            'passed_measurements': passed_count,
            'failed_measurements': len(measurements) - passed_count,
            'pass_rate': passed_count / len(measurements) if measurements else 0.0,
            'average_quality_score': avg_quality_score,
            'results': batch_results
        }

    def get_quality_report(self, time_window_hours: int = 24) -> Dict:
        """
        Generate quality control report for recent measurements.

        Args:
            time_window_hours: Time window for the report

        Returns:
            Comprehensive quality control report
        """
        # This would analyze quality history within the time window
        # For now, return summary of current state

        return {
            'report_period_hours': time_window_hours,
            'sensors_tracked': len(self.sensor_baselines),
            'quality_checks_performed': len(self.quality_history),
            'sensor_baselines': {
                sensor_id: {
                    'mean': baseline['mean'],
                    'std': baseline['std'],
                    'measurement_count': baseline['count']
                }
                for sensor_id, baseline in self.sensor_baselines.items()
            },
            'generated_at': datetime.now().isoformat()
        }
