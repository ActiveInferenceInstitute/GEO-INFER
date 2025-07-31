# Active Inference Basics

> **Tutorial**: Learn active inference through hands-on examples
> 
> This tutorial teaches you the core concepts of active inference by building working examples. You'll learn by doing, with complete code that you can run immediately.

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- **What active inference is** and why it's powerful for geospatial analysis
- **How to build simple active inference models** with GEO-INFER
- **How to update beliefs** based on new observations
- **How to make predictions** with uncertainty quantification
- **How to apply active inference** to real geospatial problems

## 🚀 Quick Start

Let's start with a simple example that demonstrates the core concepts:

```python
# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
from geo_infer_act import ActiveInferenceModel

# Create a simple active inference model
model = ActiveInferenceModel(
    state_space=['temperature', 'humidity'],
    observation_space=['sensor_reading'],
    precision=1.0
)

# Update beliefs with an observation
observation = {'sensor_reading': 25.5}
model.update_beliefs(observation)

# Make a prediction
prediction = model.predict({'temperature': 20, 'humidity': 60})
print(f"Predicted sensor reading: {prediction['sensor_reading']:.1f}")
```

**Expected Output:**
```
Predicted sensor reading: 25.2
```

## 📚 Understanding Active Inference

### What is Active Inference?

Active inference is an AI framework that models how intelligent systems (like humans, animals, or AI agents) perceive, learn, and act in their environment. It's based on the **Free Energy Principle**, which states that adaptive systems minimize "surprise" by updating their internal models of the world.

### Key Concepts

1. **Generative Model**: Your internal model of how the world works
2. **Observations**: What you can sense or measure
3. **Hidden States**: What you can't directly observe but want to understand
4. **Beliefs**: Your current understanding of hidden states
5. **Actions**: What you can do to change the world
6. **Free Energy**: A measure of how surprised you are by observations

### Why Active Inference for Geospatial Analysis?

Active inference is particularly powerful for geospatial problems because:

- **Spatial Uncertainty**: Geographic data is often incomplete or noisy
- **Temporal Dynamics**: Environmental conditions change over time
- **Multi-scale Analysis**: Processes occur at different spatial scales
- **Adaptive Behavior**: Systems need to respond to changing conditions

## 🏗️ Building Your First Model

### Step 1: Define Your State Space

The state space represents what you want to understand about your environment:

```python
from geo_infer_act import ActiveInferenceModel

# Define what you want to model
state_space = ['temperature', 'humidity', 'elevation']
observation_space = ['sensor_reading', 'satellite_data']

# Create your model
model = ActiveInferenceModel(
    state_space=state_space,
    observation_space=observation_space,
    precision=1.0  # Controls exploration vs exploitation
)

print("✅ Model created successfully!")
print(f"State space: {model.state_space}")
print(f"Observation space: {model.observation_space}")
```

### Step 2: Update Beliefs with Observations

Active inference models learn by updating their beliefs based on new observations:

```python
# Simulate some observations
observations = [
    {'sensor_reading': 25.5, 'satellite_data': 0.8},
    {'sensor_reading': 28.2, 'satellite_data': 0.9},
    {'sensor_reading': 22.1, 'satellite_data': 0.6}
]

# Update beliefs with each observation
for i, obs in enumerate(observations):
    model.update_beliefs(obs)
    print(f"Updated beliefs with observation {i+1}: {obs}")
    
    # Check current beliefs
    beliefs = model.get_beliefs()
    print(f"Current beliefs: {beliefs}")
    print()
```

### Step 3: Make Predictions

Once your model has learned from observations, you can make predictions:

```python
# Make predictions for new conditions
new_conditions = {
    'temperature': 26.0,
    'humidity': 65.0,
    'elevation': 100.0
}

prediction = model.predict(new_conditions)
print("Prediction Results:")
print(f"Expected sensor reading: {prediction['sensor_reading']:.2f}")
print(f"Expected satellite data: {prediction['satellite_data']:.2f}")
```

## 🗺️ Spatial Active Inference

### Working with Geographic Data

Active inference becomes particularly powerful when applied to spatial data:

```python
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

# Create sample spatial data
np.random.seed(42)
n_locations = 50

# Generate random locations
lats = np.random.uniform(30, 50, n_locations)
lons = np.random.uniform(-120, -70, n_locations)
temperatures = 20 + 10 * np.sin(np.radians(lats)) + np.random.normal(0, 3, n_locations)
humidities = 50 + 30 * np.random.random(n_locations)

# Create GeoDataFrame
locations = gpd.GeoDataFrame({
    'temperature': temperatures,
    'humidity': humidities,
    'geometry': [Point(lon, lat) for lon, lat in zip(lons, lats)]
}, crs="EPSG:4326")

print(f"✅ Created spatial dataset with {len(locations)} locations")
print(locations.head())
```

### Spatial Active Inference Model

Now let's build an active inference model that understands spatial relationships:

```python
from geo_infer_act.spatial import SpatialActiveInferenceModel

# Create spatial active inference model
spatial_model = SpatialActiveInferenceModel(
    state_space=['temperature', 'humidity'],
    observation_space=['sensor_reading'],
    spatial_resolution=0.1,  # 0.1 degree resolution
    precision=1.0
)

# Update with spatial observations
for idx, location in locations.iterrows():
    observation = {
        'sensor_reading': location['temperature'] + np.random.normal(0, 1),
        'geometry': location.geometry
    }
    spatial_model.update_beliefs(observation)

print("✅ Spatial model trained with location data")
```

### Making Spatial Predictions

Predict environmental conditions at new locations:

```python
# Create new locations for prediction
new_locations = gpd.GeoDataFrame({
    'geometry': [
        Point(-100, 40),  # Midwest
        Point(-80, 30),   # Southeast
        Point(-120, 45)   # Northwest
    ]
}, crs="EPSG:4326")

# Make predictions
predictions = spatial_model.predict_spatial(new_locations)
print("Spatial Predictions:")
for i, (loc, pred) in enumerate(zip(new_locations.iterrows(), predictions)):
    print(f"Location {i+1}: Temperature = {pred['temperature']:.1f}°C, "
          f"Humidity = {pred['humidity']:.1f}%")
```

## ⏰ Temporal Active Inference

### Time Series Analysis

Active inference excels at modeling temporal dynamics:

```python
import pandas as pd
from geo_infer_act.temporal import TemporalActiveInferenceModel

# Create time series data
dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
n_days = len(dates)

# Simulate seasonal temperature data
base_temp = 20
seasonal_variation = 10 * np.sin(2 * np.pi * np.arange(n_days) / 365)
noise = np.random.normal(0, 2, n_days)
temperatures = base_temp + seasonal_variation + noise

# Create temporal model
temporal_model = TemporalActiveInferenceModel(
    state_space=['temperature', 'trend'],
    observation_space=['daily_temp'],
    temporal_resolution='D',
    precision=1.0
)

# Update with temporal observations
for date, temp in zip(dates, temperatures):
    observation = {
        'daily_temp': temp,
        'timestamp': date
    }
    temporal_model.update_beliefs(observation)

print("✅ Temporal model trained with daily temperature data")
```

### Forecasting with Uncertainty

Make predictions with quantified uncertainty:

```python
# Predict future temperatures
future_dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
predictions = temporal_model.forecast(future_dates, n_samples=1000)

print("Temperature Forecast (January 2024):")
for i, (date, pred) in enumerate(zip(future_dates, predictions)):
    if i % 7 == 0:  # Show weekly summary
        print(f"{date.strftime('%Y-%m-%d')}: "
              f"{pred['mean']:.1f}°C ± {pred['std']:.1f}°C")
```

## 🔍 Uncertainty Quantification

### Understanding Prediction Uncertainty

Active inference naturally provides uncertainty estimates:

```python
# Get predictions with uncertainty
uncertainty_analysis = model.predict_with_uncertainty(
    {'temperature': 25, 'humidity': 60},
    n_samples=1000
)

print("Prediction with Uncertainty:")
print(f"Mean: {uncertainty_analysis['mean']:.2f}")
print(f"Standard Deviation: {uncertainty_analysis['std']:.2f}")
print(f"95% Confidence Interval: [{uncertainty_analysis['ci_lower']:.2f}, "
      f"{uncertainty_analysis['ci_upper']:.2f}]")

# Visualize uncertainty
plt.figure(figsize=(10, 6))
plt.hist(uncertainty_analysis['samples'], bins=30, alpha=0.7, density=True)
plt.axvline(uncertainty_analysis['mean'], color='red', linestyle='--', 
            label=f"Mean: {uncertainty_analysis['mean']:.2f}")
plt.axvline(uncertainty_analysis['ci_lower'], color='orange', linestyle=':', 
            label=f"95% CI: [{uncertainty_analysis['ci_lower']:.2f}, "
                  f"{uncertainty_analysis['ci_upper']:.2f}]")
plt.axvline(uncertainty_analysis['ci_upper'], color='orange', linestyle=':')
plt.xlabel('Predicted Value')
plt.ylabel('Probability Density')
plt.title('Prediction Uncertainty Distribution')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## 🎯 Real-World Application: Environmental Monitoring

### Building an Environmental Monitoring System

Let's build a complete environmental monitoring system using active inference:

```python
from geo_infer_act import EnvironmentalMonitoringModel

# Create environmental monitoring model
env_model = EnvironmentalMonitoringModel(
    variables=['temperature', 'humidity', 'air_quality', 'soil_moisture'],
    spatial_resolution=0.01,  # 1km resolution
    temporal_resolution='H',  # Hourly updates
    precision=1.0
)

# Simulate sensor network data
sensor_data = {
    'location': Point(-122.4194, 37.7749),  # San Francisco
    'timestamp': pd.Timestamp('2023-06-15 14:00:00'),
    'temperature': 22.5,
    'humidity': 65.0,
    'air_quality': 45.0,  # AQI
    'soil_moisture': 0.3
}

# Update model with sensor data
env_model.update_with_sensor_data(sensor_data)

# Predict environmental conditions
prediction = env_model.predict_conditions(
    location=Point(-122.4194, 37.7749),
    time=pd.Timestamp('2023-06-15 15:00:00')
)

print("Environmental Prediction:")
for var, value in prediction.items():
    print(f"{var}: {value:.2f}")
```

### Anomaly Detection

Active inference can detect unusual environmental conditions:

```python
# Detect anomalies in environmental data
anomalies = env_model.detect_anomalies(
    threshold=2.0  # Standard deviations from expected
)

if anomalies:
    print("🚨 Environmental Anomalies Detected:")
    for anomaly in anomalies:
        print(f"- {anomaly['variable']}: {anomaly['value']:.2f} "
              f"(expected: {anomaly['expected']:.2f})")
else:
    print("✅ No environmental anomalies detected")
```

## 🔧 Advanced Concepts

### Custom Transition Models

You can define custom transition models for domain-specific dynamics:

```python
from geo_infer_act import ActiveInferenceModel

class CustomEnvironmentalModel(ActiveInferenceModel):
    def __init__(self, custom_params):
        super().__init__(state_space, observation_space)
        self.custom_params = custom_params
    
    def custom_transition_model(self, state, action):
        """Custom transition model for environmental dynamics"""
        # Example: Temperature affects humidity
        new_humidity = state['humidity'] * 0.9 + state['temperature'] * 0.1
        new_temperature = state['temperature'] + action.get('heating', 0)
        
        return {
            'temperature': new_temperature,
            'humidity': new_humidity
        }

# Use custom model
custom_model = CustomEnvironmentalModel(custom_params={'season': 'summer'})
```

### Multi-scale Analysis

Active inference can model processes at multiple spatial scales:

```python
from geo_infer_act.multiscale import MultiScaleActiveInferenceModel

# Create multi-scale model
multiscale_model = MultiScaleActiveInferenceModel(
    scales=['local', 'regional', 'global'],
    state_spaces={
        'local': ['temperature', 'humidity'],
        'regional': ['climate_zone', 'elevation'],
        'global': ['latitude', 'longitude']
    }
)

# Update beliefs at multiple scales
observation = {
    'local': {'temperature': 25.5, 'humidity': 60.0},
    'regional': {'climate_zone': 'temperate', 'elevation': 100.0},
    'global': {'latitude': 37.7749, 'longitude': -122.4194}
}

multiscale_model.update_beliefs(observation)
```

## 📊 Performance Optimization

### Efficient Belief Updates

For large-scale applications, optimize belief updates:

```python
# Enable parallel processing
model.enable_parallel_processing(n_workers=4)

# Use batch updates for efficiency
batch_observations = [
    {'sensor_reading': 25.5},
    {'sensor_reading': 28.2},
    {'sensor_reading': 22.1}
]

model.batch_update_beliefs(batch_observations)
```

### Memory Management

Handle large datasets efficiently:

```python
# Enable memory-efficient processing
model.enable_memory_optimization(
    max_memory_gb=8,
    chunk_size=1000
)

# Use streaming for very large datasets
for chunk in data_stream:
    model.update_beliefs_streaming(chunk)
```

## 🎯 What You've Accomplished

Congratulations! You've successfully learned active inference fundamentals:

✅ **Built your first active inference model**  
✅ **Updated beliefs with observations**  
✅ **Made predictions with uncertainty quantification**  
✅ **Applied active inference to spatial data**  
✅ **Modeled temporal dynamics**  
✅ **Built a real-world environmental monitoring system**  

## 🔗 Next Steps

### Explore More Examples
- **[Environmental Monitoring](../examples/environmental_monitoring.md)** - Climate and ecosystem analysis
- **[Urban Planning](../examples/urban_planning.md)** - City and infrastructure analysis
- **[Agricultural Applications](../examples/agricultural_applications.md)** - Crop and soil analysis

### Learn Advanced Techniques
- **[Custom Models](../advanced/custom_models.md)** - Build specialized active inference models
- **[Performance Optimization](../advanced/performance_optimization.md)** - Speed up your analyses
- **[Multi-scale Analysis](../advanced/multiscale_analysis.md)** - Model processes at different scales

### Join the Community
- **[Community Forum](https://forum.geo-infer.org)** - Share your models and get help
- **[GitHub Repository](https://github.com/geo-infer/geo-infer-intra)** - Contribute to the project
- **[Research Papers](https://github.com/geo-infer/geo-infer-intra/tree/main/papers)** - Academic applications

## 🚨 Troubleshooting

### Common Issues

**Model not converging:**
```python
# Reduce precision for more exploration
model = ActiveInferenceModel(precision=0.1)

# Check data quality
print(f"Data range: {data.min()} to {data.max()}")
print(f"Missing values: {data.isnull().sum()}")
```

**Memory issues with large datasets:**
```python
# Use chunked processing
model.enable_memory_optimization(chunk_size=500)

# Process in batches
for batch in data_chunks:
    model.batch_update_beliefs(batch)
```

**Uncertain predictions:**
```python
# Increase model precision
model = ActiveInferenceModel(precision=5.0)

# Add more observations
for obs in additional_observations:
    model.update_beliefs(obs)
```

### Getting Help

If you encounter issues:

1. **Check the [FAQ](../support/faq.md)** for common solutions
2. **Search [GitHub Issues](https://github.com/geo-infer/geo-infer-intra/issues)**
3. **Ask on the [Community Forum](https://forum.geo-infer.org)**
4. **Review the [Troubleshooting Guide](../support/troubleshooting.md)**

---

**Ready for more?** Explore [Custom Model Development](../advanced/custom_models.md) or dive into [Environmental Monitoring Applications](../examples/environmental_monitoring.md)! 