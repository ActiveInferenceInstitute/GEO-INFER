---
title: "GEO-INFER Module Integration Guide"
description: "Comprehensive guide for integrating multiple GEO-INFER modules"
purpose: "Learn how to combine GEO-INFER modules for complex geospatial workflows"
difficulty: "Intermediate"
estimated_time: "90"
last_updated: "2025-01-19"
---

# 🔗 GEO-INFER Module Integration Guide

## 🎯 Overview

This comprehensive guide demonstrates how to effectively integrate multiple GEO-INFER modules to build sophisticated geospatial analysis workflows. Learn proven integration patterns, best practices, and real-world examples.

## 📋 Integration Patterns

### Pattern 1: Linear Pipeline Integration

#### Spatial Data Processing Pipeline
```python
# GEO-INFER-DATA → GEO-INFER-SPACE → GEO-INFER-ACT → Results
from geo_infer_data import DataManager
from geo_infer_space import SpatialAnalyzer
from geo_infer_act import ActiveInferenceModel

# Initialize modules
data_manager = DataManager()
spatial_analyzer = SpatialAnalyzer()
act_model = ActiveInferenceModel(
    state_space=['spatial_patterns', 'temporal_trends'],
    observation_space=['sensor_data', 'environmental_indicators']
)

# Create integrated pipeline
class SpatialAnalysisPipeline:
    def __init__(self):
        self.data_manager = data_manager
        self.spatial_analyzer = spatial_analyzer
        self.act_model = act_model

    def process_environmental_data(self, raw_data):
        # Step 1: Data preprocessing
        clean_data = self.data_manager.preprocess_spatial_data(raw_data)

        # Step 2: Spatial analysis
        spatial_features = self.spatial_analyzer.extract_spatial_features(clean_data)

        # Step 3: Active inference
        self.act_model.update_beliefs({
            'spatial_features': spatial_features,
            'environmental_context': clean_data
        })

        # Step 4: Generate insights
        insights = self.act_model.generate_environmental_insights()

        return insights

# Usage
pipeline = SpatialAnalysisPipeline()
results = pipeline.process_environmental_data(sensor_data)
```

#### Benefits
- **Modular Processing**: Each step handles specific data transformations
- **Error Isolation**: Issues in one module don't affect others
- **Scalability**: Easy to add/remove processing steps
- **Reusability**: Pipeline components can be reused

### Pattern 2: Hub and Spoke Integration

#### API-Centric Integration
```python
# GEO-INFER-API as central hub with multiple spokes
from geo_infer_api import APIManager
from geo_infer_space import SpatialAnalyzer
from geo_infer_time import TemporalAnalyzer
from geo_infer_act import ActiveInferenceModel

class GeospatialAnalysisHub:
    def __init__(self):
        self.api_manager = APIManager()
        self.spatial_analyzer = SpatialAnalyzer()
        self.temporal_analyzer = TemporalAnalyzer()
        self.act_model = ActiveInferenceModel()

        # Register analysis endpoints
        self._setup_endpoints()

    def _setup_endpoints(self):
        # Spatial analysis endpoint
        self.api_manager.add_endpoint('/api/v1/spatial/analyze', self.spatial_analysis_handler)

        # Temporal analysis endpoint
        self.api_manager.add_endpoint('/api/v1/temporal/analyze', self.temporal_analysis_handler)

        # Integrated analysis endpoint
        self.api_manager.add_endpoint('/api/v1/integrated/analyze', self.integrated_analysis_handler)

    def spatial_analysis_handler(self, request):
        data = request.get_json()
        results = self.spatial_analyzer.analyze_spatial_patterns(data)
        return {'results': results, 'module': 'spatial'}

    def temporal_analysis_handler(self, request):
        data = request.get_json()
        results = self.temporal_analyzer.analyze_temporal_patterns(data)
        return {'results': results, 'module': 'temporal'}

    def integrated_analysis_handler(self, request):
        data = request.get_json()

        # Parallel processing of spatial and temporal analysis
        spatial_results = self.spatial_analyzer.analyze_spatial_patterns(data)
        temporal_results = self.temporal_analyzer.analyze_temporal_patterns(data)

        # Combine results with active inference
        combined_data = {
            'spatial_features': spatial_results,
            'temporal_patterns': temporal_results,
            'context': data
        }

        self.act_model.update_beliefs(combined_data)
        integrated_insights = self.act_model.generate_integrated_insights()

        return {
            'spatial_results': spatial_results,
            'temporal_results': temporal_results,
            'integrated_insights': integrated_insights,
            'module': 'integrated'
        }

# Deploy the hub
hub = GeospatialAnalysisHub()
hub.api_manager.start_server(host='0.0.0.0', port=8000)
```

#### Benefits
- **Centralized Access**: Single entry point for all analyses
- **Load Balancing**: API layer can distribute requests
- **Monitoring**: Centralized logging and performance tracking
- **Security**: Unified authentication and authorization

### Pattern 3: Event-Driven Integration

#### Real-Time Environmental Monitoring
```python
# GEO-INFER-IOT → GEO-INFER-ACT → GEO-INFER-SPACE → GEO-INFER-API
from geo_infer_iot import IoTManager
from geo_infer_act import ActiveInferenceModel
from geo_infer_space import SpatialAnalyzer
from geo_infer_api import APIManager
import asyncio

class RealTimeEnvironmentalMonitor:
    def __init__(self):
        self.iot_manager = IoTManager()
        self.act_model = ActiveInferenceModel()
        self.spatial_analyzer = SpatialAnalyzer()
        self.api_manager = APIManager()

        # Event queues for inter-module communication
        self.spatial_events = asyncio.Queue()
        self.act_events = asyncio.Queue()
        self.api_events = asyncio.Queue()

    async def start_monitoring(self):
        # Start all monitoring tasks
        await asyncio.gather(
            self._monitor_iot_data(),
            self._process_spatial_analysis(),
            self._run_active_inference(),
            self._handle_api_requests()
        )

    async def _monitor_iot_data(self):
        """Monitor real-time IoT sensor data."""
        async for sensor_data in self.iot_manager.stream_sensor_data():
            # Send data to spatial analysis
            await self.spatial_events.put(sensor_data)

            # Send data to active inference
            await self.act_events.put(sensor_data)

    async def _process_spatial_analysis(self):
        """Process spatial patterns from sensor data."""
        while True:
            sensor_data = await self.spatial_events.get()

            # Perform spatial analysis
            spatial_patterns = self.spatial_analyzer.analyze_realtime_spatial_patterns(sensor_data)

            # Send results to active inference
            await self.act_events.put({
                'type': 'spatial_analysis',
                'data': spatial_patterns,
                'timestamp': sensor_data['timestamp']
            })

            self.spatial_events.task_done()

    async def _run_active_inference(self):
        """Run active inference on incoming data."""
        while True:
            event = await self.act_events.get()

            if event['type'] == 'sensor_data':
                # Update beliefs with sensor data
                self.act_model.update_beliefs(event)
            elif event['type'] == 'spatial_analysis':
                # Update beliefs with spatial analysis
                self.act_model.update_beliefs(event)

            # Generate real-time insights
            insights = self.act_model.generate_realtime_insights()

            # Send to API for external access
            await self.api_events.put(insights)

            self.act_events.task_done()

    async def _handle_api_requests(self):
        """Handle API requests for real-time data."""
        while True:
            insights = await self.api_events.get()

            # Make insights available via API
            self.api_manager.update_realtime_data(insights)

            self.api_events.task_done()

# Start real-time monitoring
monitor = RealTimeEnvironmentalMonitor()
asyncio.run(monitor.start_monitoring())
```

#### Benefits
- **Real-Time Processing**: Immediate response to data changes
- **Decoupled Architecture**: Modules operate independently
- **Scalability**: Easy to add new event handlers
- **Fault Tolerance**: System continues operating if one module fails

### Pattern 4: Feedback Loop Integration

#### Adaptive Learning System
```python
# GEO-INFER-ACT → GEO-INFER-AI → GEO-INFER-ACT (Continuous Learning)
from geo_infer_act import ActiveInferenceModel
from geo_infer_ai import AIModel
from geo_infer_space import SpatialAnalyzer

class AdaptiveSpatialLearningSystem:
    def __init__(self):
        self.act_model = ActiveInferenceModel(
            state_space=['spatial_patterns', 'environmental_conditions'],
            observation_space=['sensor_data', 'spatial_features']
        )
        self.ai_model = AIModel()
        self.spatial_analyzer = SpatialAnalyzer()

        # Learning parameters
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.05

    def process_and_adapt(self, sensor_data, iterations=10):
        """Process data and adapt the system through feedback loops."""

        for iteration in range(iterations):
            # Step 1: Extract spatial features
            spatial_features = self.spatial_analyzer.extract_spatial_features(sensor_data)

            # Step 2: Update active inference model
            observation = {
                'sensor_data': sensor_data,
                'spatial_features': spatial_features
            }
            self.act_model.update_beliefs(observation)

            # Step 3: Generate predictions with AI
            ai_predictions = self.ai_model.predict_spatial_patterns(spatial_features)

            # Step 4: Compare predictions with observations
            prediction_accuracy = self._evaluate_prediction_accuracy(
                ai_predictions, sensor_data
            )

            # Step 5: Adapt if accuracy is below threshold
            if prediction_accuracy < self.adaptation_threshold:
                self._adapt_system(spatial_features, sensor_data, prediction_accuracy)

            # Step 6: Update AI model with new data
            self.ai_model.update_model(sensor_data, spatial_features)

        return self.act_model.get_current_beliefs()

    def _evaluate_prediction_accuracy(self, predictions, actual_data):
        """Evaluate how well predictions match actual data."""
        # Implementation of accuracy evaluation
        return self._calculate_spatial_accuracy(predictions, actual_data)

    def _adapt_system(self, features, data, accuracy):
        """Adapt the system based on prediction accuracy."""
        # Update active inference precision
        if accuracy < 0.5:
            self.act_model.adjust_precision(increase_factor=1.2)
        else:
            self.act_model.adjust_precision(decrease_factor=0.9)

        # Update learning rate
        self.learning_rate = min(0.5, self.learning_rate * 1.1)

        # Retrain AI model with emphasis on poorly predicted areas
        self.ai_model.retrain_with_emphasis(features, data, accuracy)

    def _calculate_spatial_accuracy(self, predictions, actual):
        """Calculate spatial prediction accuracy."""
        # Implementation of spatial accuracy calculation
        return 0.85  # Placeholder

# Usage
adaptive_system = AdaptiveSpatialLearningSystem()
final_beliefs = adaptive_system.process_and_adapt(sensor_data, iterations=20)
```

#### Benefits
- **Continuous Improvement**: System learns and adapts over time
- **Self-Correction**: Automatic adjustment based on performance
- **Robustness**: Better handling of changing conditions
- **Optimization**: Improved accuracy through feedback

## 🎯 Real-World Integration Examples

### Example 1: Smart City Environmental Monitoring

#### Problem
Monitor urban air quality, predict pollution patterns, and provide real-time alerts to citizens and city officials.

#### Solution Architecture
```
GEO-INFER-IOT → GEO-INFER-DATA → GEO-INFER-SPACE → GEO-INFER-TIME → GEO-INFER-ACT → GEO-INFER-API
```

#### Implementation
```python
from geo_infer_iot import IoTManager
from geo_infer_data import DataManager
from geo_infer_space import SpatialAnalyzer
from geo_infer_time import TemporalAnalyzer
from geo_infer_act import ActiveInferenceModel
from geo_infer_api import APIManager

class SmartCityAirQualityMonitor:
    def __init__(self):
        self.iot_manager = IoTManager()
        self.data_manager = DataManager()
        self.spatial_analyzer = SpatialAnalyzer()
        self.temporal_analyzer = TemporalAnalyzer()
        self.act_model = ActiveInferenceModel()
        self.api_manager = APIManager()

    def setup_monitoring_system(self):
        """Set up the complete air quality monitoring system."""

        # Configure IoT sensors
        self.iot_manager.configure_sensors([
            {'type': 'air_quality', 'location': 'downtown', 'sensors': ['PM2.5', 'PM10', 'NO2', 'O3']},
            {'type': 'air_quality', 'location': 'residential', 'sensors': ['PM2.5', 'PM10', 'NO2']},
            {'type': 'weather', 'location': 'central', 'sensors': ['temperature', 'humidity', 'wind_speed']}
        ])

        # Set up data processing pipeline
        self.data_manager.configure_pipeline([
            'data_validation',
            'outlier_detection',
            'spatial_interpolation',
            'temporal_smoothing'
        ])

        # Configure spatial analysis
        self.spatial_analyzer.configure_analysis({
            'resolution': 100,  # meters
            'interpolation_method': 'kriging',
            'clustering_method': 'hdbscan'
        })

        # Configure temporal analysis
        self.temporal_analyzer.configure_analysis({
            'seasonal_decomposition': True,
            'forecast_horizon': 24,  # hours
            'anomaly_detection': True
        })

        # Configure active inference
        self.act_model.configure_model({
            'state_space': ['pollution_levels', 'weather_conditions', 'traffic_patterns'],
            'observation_space': ['sensor_readings', 'spatial_patterns', 'temporal_trends'],
            'precision': 1.0,
            'learning_rate': 0.1
        })

    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle."""

        # Collect sensor data
        sensor_data = self.iot_manager.collect_sensor_data()

        # Process and validate data
        processed_data = self.data_manager.process_data(sensor_data)

        # Perform spatial analysis
        spatial_analysis = self.spatial_analyzer.analyze_spatial_patterns(processed_data)

        # Perform temporal analysis
        temporal_analysis = self.temporal_analyzer.analyze_temporal_patterns(processed_data)

        # Update active inference model
        observation = {
            'sensor_data': processed_data,
            'spatial_patterns': spatial_analysis,
            'temporal_trends': temporal_analysis
        }
        self.act_model.update_beliefs(observation)

        # Generate insights and predictions
        insights = self.act_model.generate_air_quality_insights()
        predictions = self.temporal_analyzer.forecast_air_quality(24)

        # Make results available via API
        results = {
            'current_conditions': processed_data,
            'spatial_analysis': spatial_analysis,
            'temporal_analysis': temporal_analysis,
            'insights': insights,
            'predictions': predictions,
            'alerts': self._generate_alerts(insights)
        }

        self.api_manager.publish_results(results)

        return results

    def _generate_alerts(self, insights):
        """Generate alerts based on insights."""
        alerts = []

        if insights.get('pm25_level', 0) > 50:
            alerts.append({
                'type': 'health_alert',
                'severity': 'high',
                'message': 'High PM2.5 levels detected',
                'affected_areas': insights.get('high_pollution_zones', [])
            })

        if insights.get('prediction_trend') == 'worsening':
            alerts.append({
                'type': 'trend_alert',
                'severity': 'medium',
                'message': 'Air quality expected to worsen',
                'timeframe': 'next 24 hours'
            })

        return alerts

# Deploy the system
monitor = SmartCityAirQualityMonitor()
monitor.setup_monitoring_system()

# Run continuous monitoring
while True:
    results = monitor.run_monitoring_cycle()
    time.sleep(300)  # 5-minute intervals
```

### Example 2: Precision Agriculture System

#### Problem
Optimize crop yields through integrated analysis of soil conditions, weather patterns, satellite imagery, and historical yield data.

#### Solution Architecture
```
GEO-INFER-DATA → GEO-INFER-SPACE → GEO-INFER-TIME → GEO-INFER-AI → GEO-INFER-AG → GEO-INFER-API
```

#### Implementation
```python
from geo_infer_data import DataManager
from geo_infer_space import SpatialAnalyzer
from geo_infer_time import TemporalAnalyzer
from geo_infer_ai import AIModel
from geo_infer_ag import AgriculturalAnalyzer
from geo_infer_api import APIManager

class PrecisionAgricultureSystem:
    def __init__(self):
        self.data_manager = DataManager()
        self.spatial_analyzer = SpatialAnalyzer()
        self.temporal_analyzer = TemporalAnalyzer()
        self.ai_model = AIModel()
        self.agricultural_analyzer = AgriculturalAnalyzer()
        self.api_manager = APIManager()

    def analyze_field_conditions(self, field_id, date_range):
        """Perform comprehensive field analysis."""

        # Collect all relevant data
        soil_data = self.data_manager.get_soil_data(field_id, date_range)
        weather_data = self.data_manager.get_weather_data(field_id, date_range)
        satellite_data = self.data_manager.get_satellite_imagery(field_id, date_range)
        yield_history = self.data_manager.get_yield_history(field_id)

        # Spatial analysis of field conditions
        spatial_analysis = self.spatial_analyzer.analyze_field_variability(
            soil_data, satellite_data
        )

        # Temporal analysis of weather patterns
        weather_patterns = self.temporal_analyzer.analyze_weather_patterns(weather_data)

        # AI-powered crop health assessment
        crop_health = self.ai_model.assess_crop_health(satellite_data, spatial_analysis)

        # Agricultural optimization
        recommendations = self.agricultural_analyzer.optimize_crop_management({
            'soil_conditions': spatial_analysis,
            'weather_patterns': weather_patterns,
            'crop_health': crop_health,
            'yield_history': yield_history
        })

        # Generate comprehensive report
        report = {
            'field_id': field_id,
            'analysis_date': datetime.now(),
            'soil_analysis': spatial_analysis,
            'weather_analysis': weather_patterns,
            'crop_health': crop_health,
            'recommendations': recommendations,
            'predicted_yield': self.agricultural_analyzer.predict_yield(recommendations),
            'confidence_intervals': self._calculate_confidence_intervals(recommendations)
        }

        return report

    def _calculate_confidence_intervals(self, recommendations):
        """Calculate confidence intervals for recommendations."""
        # Implementation for uncertainty quantification
        return {
            'yield_prediction_ci': [0.85, 0.95],
            'irrigation_ci': [0.80, 0.90],
            'fertilizer_ci': [0.75, 0.85]
        }

# Usage example
precision_ag = PrecisionAgricultureSystem()

# Analyze specific field
field_report = precision_ag.analyze_field_conditions(
    field_id='field_001',
    date_range=['2024-01-01', '2024-12-31']
)

# Make recommendations available via API
precision_ag.api_manager.publish_field_report(field_report)
```

## 🛠️ Integration Best Practices

### 1. Error Handling and Resilience

```python
class ResilientIntegrationManager:
    def __init__(self, modules):
        self.modules = modules
        self.circuit_breakers = {}
        self.fallback_strategies = {}

    def execute_with_resilience(self, operation, *args, **kwargs):
        """Execute operation with comprehensive error handling."""

        for module_name, module in self.modules.items():
            if self._is_circuit_breaker_open(module_name):
                return self._execute_fallback(module_name, operation, *args, **kwargs)

            try:
                result = getattr(module, operation)(*args, **kwargs)
                self._reset_circuit_breaker(module_name)
                return result

            except Exception as e:
                self._handle_module_error(module_name, e)
                continue

        # If all modules fail, execute global fallback
        return self._execute_global_fallback(operation, *args, **kwargs)

    def _is_circuit_breaker_open(self, module_name):
        """Check if circuit breaker is open for module."""
        return self.circuit_breakers.get(module_name, {}).get('open', False)

    def _handle_module_error(self, module_name, error):
        """Handle module-specific errors."""
        # Update circuit breaker state
        if module_name not in self.circuit_breakers:
            self.circuit_breakers[module_name] = {'failures': 0, 'open': False}

        self.circuit_breakers[module_name]['failures'] += 1

        # Open circuit breaker after threshold
        if self.circuit_breakers[module_name]['failures'] >= 5:
            self.circuit_breakers[module_name]['open'] = True

    def _execute_fallback(self, module_name, operation, *args, **kwargs):
        """Execute fallback strategy for failed module."""
        fallback_func = self.fallback_strategies.get(module_name, {}).get(operation)
        if fallback_func:
            return fallback_func(*args, **kwargs)
        else:
            return self._default_fallback(operation, *args, **kwargs)

    def _execute_global_fallback(self, operation, *args, **kwargs):
        """Execute global fallback strategy."""
        return {'error': 'All modules failed', 'operation': operation}
```

### 2. Performance Monitoring and Optimization

```python
class IntegrationPerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'response_time': 5000,  # ms
            'error_rate': 0.05,     # 5%
            'throughput': 100       # requests/second
        }

    def monitor_operation(self, operation_name, func, *args, **kwargs):
        """Monitor performance of integrated operations."""

        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            success = True
            error = None

        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        # Record metrics
        self._record_metrics(operation_name, {
            'response_time': response_time,
            'success': success,
            'error': error
        })

        # Check thresholds and alert if necessary
        self._check_thresholds(operation_name)

        return result

    def _record_metrics(self, operation_name, metrics):
        """Record performance metrics."""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []

        self.metrics[operation_name].append(metrics)

        # Keep only last 1000 measurements
        if len(self.metrics[operation_name]) > 1000:
            self.metrics[operation_name] = self.metrics[operation_name][-1000:]

    def _check_thresholds(self, operation_name):
        """Check if metrics exceed thresholds."""
        recent_metrics = self.metrics[operation_name][-10:]  # Last 10 measurements

        avg_response_time = sum(m['response_time'] for m in recent_metrics) / len(recent_metrics)
        error_rate = sum(1 for m in recent_metrics if not m['success']) / len(recent_metrics)

        if avg_response_time > self.thresholds['response_time']:
            self._alert_slow_response(operation_name, avg_response_time)

        if error_rate > self.thresholds['error_rate']:
            self._alert_high_error_rate(operation_name, error_rate)

    def _alert_slow_response(self, operation_name, response_time):
        """Alert on slow response times."""
        print(f"ALERT: {operation_name} response time ({response_time:.2f}ms) exceeds threshold")

    def _alert_high_error_rate(self, operation_name, error_rate):
        """Alert on high error rates."""
        print(f"ALERT: {operation_name} error rate ({error_rate:.2%}) exceeds threshold")
```

### 3. Configuration Management

```python
class IntegrationConfigurationManager:
    def __init__(self):
        self.configurations = {}
        self.validation_rules = {}

    def load_configuration(self, config_file):
        """Load integration configuration from file."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        self._validate_configuration(config)
        self.configurations.update(config)

        return config

    def get_module_configuration(self, module_name, environment='production'):
        """Get configuration for specific module and environment."""

        base_config = self.configurations.get('modules', {}).get(module_name, {})
        env_config = self.configurations.get('environments', {}).get(environment, {})

        # Merge configurations with environment-specific overrides
        module_config = self._deep_merge(base_config, env_config.get(module_name, {}))

        return module_config

    def _validate_configuration(self, config):
        """Validate configuration against rules."""
        for rule_name, rule_func in self.validation_rules.items():
            if not rule_func(config):
                raise ValueError(f"Configuration validation failed: {rule_name}")

    def _deep_merge(self, base, override):
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

# Usage
config_manager = IntegrationConfigurationManager()
config_manager.load_configuration('integration_config.yaml')

spatial_config = config_manager.get_module_configuration('geo-infer-space')
ai_config = config_manager.get_module_configuration('geo-infer-ai')
```

## 📚 Additional Resources

### Tutorials
- **[Module Basics](../getting_started/module_basics.md)** - Fundamental module usage
- **[Integration Patterns](../advanced/integration_patterns.md)** - Advanced integration techniques
- **[Performance Optimization](../advanced/performance_optimization.md)** - Optimizing integrated systems

### Examples
- **[Environmental Monitoring](../examples/environmental_monitoring_integration.md)** - Complete environmental monitoring system
- **[Urban Planning](../examples/urban_planning_integration.md)** - Integrated urban planning workflow
- **[Smart City](../examples/smart_city_integration.md)** - Comprehensive smart city solution

### Reference
- **[API Integration](../api/integration_reference.md)** - Complete integration API reference
- **[Configuration Guide](../advanced/configuration_guide.md)** - Configuration management
- **[Troubleshooting](../troubleshooting/integration_issues.md)** - Common integration problems

---

## 🎯 Next Steps

1. **Choose an Integration Pattern** based on your use case
2. **Start with Core Modules** (DATA, SPACE, ACT)
3. **Add Domain-Specific Modules** for your application
4. **Implement Monitoring** and error handling
5. **Optimize Performance** based on your requirements

**Ready to build?** Check out the **[Module Basics Tutorial](../getting_started/module_basics.md)** to get started!

---

*Last updated: 2025-01-19 | Framework Version: 1.0.0*
