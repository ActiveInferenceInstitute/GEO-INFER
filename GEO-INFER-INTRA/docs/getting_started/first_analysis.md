# Your First Analysis

Welcome to your first GEO-INFER analysis! This guide will walk you through a complete geospatial analysis from start to finish, introducing you to the core concepts and capabilities of the framework.

## 🎯 What You'll Learn

In this tutorial, you'll:

1. **Load and explore** geospatial data
2. **Perform spatial analysis** on point data
3. **Create visualizations** and maps
4. **Apply active inference** for prediction
5. **Analyze temporal patterns** in your data

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **GEO-INFER installed** (see [Installation Guide](installation_guide.md))
- ✅ **Python environment** set up
- ✅ **Sample data** (we'll provide this)

## 🚀 Quick Start

### Step 1: Set Up Your Environment

```python
# Import required libraries
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

# Import GEO-INFER modules
from geo_infer_space import SpatialAnalyzer
from geo_infer_time import TemporalAnalyzer
from geo_infer_act import ActiveInferenceModel
```

### Step 2: Create Sample Data

```python
# Generate sample city data
np.random.seed(42)
n_cities = 100

# Generate random coordinates (US cities)
lats = np.random.uniform(25, 50, n_cities)
lons = np.random.uniform(-125, -65, n_cities)

# Generate city attributes
populations = np.random.exponential(50000, n_cities)
temperatures = 20 + 10 * np.sin(np.radians(lats)) + np.random.normal(0, 5, n_cities)
elevations = np.random.normal(500, 300, n_cities)

# Create GeoDataFrame
cities_data = {
    'name': [f'City_{i}' for i in range(n_cities)],
    'population': populations,
    'temperature': temperatures,
    'elevation': elevations,
    'geometry': [Point(lon, lat) for lon, lat in zip(lons, lats)]
}

cities_gdf = gpd.GeoDataFrame(cities_data, crs="EPSG:4326")
print(f"✅ Created dataset with {len(cities_gdf)} cities")
```

### Step 3: Explore Your Data

```python
# Basic data exploration
print("Dataset Info:")
print(cities_gdf.info())

print("\nFirst 5 cities:")
print(cities_gdf.head())

print("\nStatistical Summary:")
print(cities_gdf.describe())

# Check for missing data
print(f"\nMissing values: {cities_gdf.isnull().sum().sum()}")
```

## 📊 Spatial Analysis

### Basic Spatial Operations

```python
# Initialize spatial analyzer
spatial_analyzer = SpatialAnalyzer()

# Calculate basic spatial statistics
spatial_stats = spatial_analyzer.analyze_points(cities_gdf)
print("Spatial Statistics:")
print(spatial_stats)

# Calculate distances between cities
distance_matrix = spatial_analyzer.calculate_distances(cities_gdf)
print(f"\nDistance matrix shape: {distance_matrix.shape}")
```

### Spatial Clustering

```python
# Perform spatial clustering
clusters = spatial_analyzer.cluster_points(
    cities_gdf, 
    method='kmeans', 
    n_clusters=5
)

# Add cluster information to the dataset
cities_gdf['cluster'] = clusters

print("Clustering Results:")
print(cities_gdf['cluster'].value_counts())
```

### Spatial Relationships

```python
# Create a buffer around each city
cities_gdf['buffer_50km'] = cities_gdf.geometry.buffer(0.5)  # ~50km in degrees

# Find cities within 100km of each other
nearby_cities = spatial_analyzer.find_nearby_points(
    cities_gdf, 
    distance_km=100
)

print(f"Found {len(nearby_cities)} nearby city pairs")
```

## 🗺️ Visualization

### Create Your First Map

```python
# Create a basic map
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Plot cities colored by population
cities_gdf.plot(
    column='population',
    ax=ax,
    legend=True,
    legend_kwds={'label': 'Population'},
    cmap='viridis',
    markersize=50
)

ax.set_title('US Cities by Population')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()
```

### Interactive Map

```python
# Create an interactive map
import folium

# Create a map centered on the US
m = folium.Map(
    location=[39.8283, -98.5795],  # Center of US
    zoom_start=4,
    tiles='OpenStreetMap'
)

# Add cities to the map
for idx, row in cities_gdf.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=row.population / 10000,  # Scale by population
        popup=f"{row['name']}<br>Population: {row['population']:,.0f}<br>Temperature: {row['temperature']:.1f}°C",
        color='red',
        fill=True
    ).add_to(m)

# Display the map
m.save('cities_map.html')
print("✅ Interactive map saved as 'cities_map.html'")
```

### Advanced Visualizations

```python
# Create a multi-panel visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Population distribution
axes[0, 0].hist(cities_gdf['population'], bins=20, alpha=0.7)
axes[0, 0].set_title('Population Distribution')
axes[0, 0].set_xlabel('Population')
axes[0, 0].set_ylabel('Frequency')

# Temperature vs Latitude
axes[0, 1].scatter(cities_gdf.geometry.y, cities_gdf['temperature'], alpha=0.6)
axes[0, 1].set_title('Temperature vs Latitude')
axes[0, 1].set_xlabel('Latitude')
axes[0, 1].set_ylabel('Temperature (°C)')

# Elevation vs Population
axes[1, 0].scatter(cities_gdf['elevation'], cities_gdf['population'], alpha=0.6)
axes[1, 0].set_title('Population vs Elevation')
axes[1, 0].set_xlabel('Elevation (m)')
axes[1, 0].set_ylabel('Population')

# Clusters map
cities_gdf.plot(column='cluster', ax=axes[1, 1], legend=True)
axes[1, 1].set_title('Spatial Clusters')

plt.tight_layout()
plt.show()
```

## 🤖 Active Inference Analysis

### Build Your First Active Inference Model

```python
# Prepare data for active inference
# We'll predict temperature based on location and elevation

# Create feature matrix
X = cities_gdf[['elevation', 'geometry.x', 'geometry.y']].values
y = cities_gdf['temperature'].values

# Initialize active inference model
ai_model = ActiveInferenceModel(
    state_space=['elevation', 'longitude', 'latitude'],
    observation_space=['temperature'],
    precision=1.0
)

# Update model with observations
for i in range(len(X)):
    observation = {
        'elevation': X[i, 0],
        'longitude': X[i, 1], 
        'latitude': X[i, 2],
        'temperature': y[i]
    }
    ai_model.update_beliefs(observation)

print("✅ Active inference model trained!")
```

### Make Predictions

```python
# Create new locations for prediction
new_locations = np.array([
    [1000, -120, 40],  # High elevation, West Coast
    [100, -80, 30],    # Low elevation, Southeast
    [2000, -100, 45],  # High elevation, Northern
])

# Make predictions
predictions = []
for location in new_locations:
    prediction = ai_model.predict({
        'elevation': location[0],
        'longitude': location[1],
        'latitude': location[2]
    })
    predictions.append(prediction['temperature'])

print("Temperature Predictions for New Locations:")
for i, (loc, pred) in enumerate(zip(new_locations, predictions)):
    print(f"Location {i+1}: Elevation={loc[0]}m, Lon={loc[1]}°, Lat={loc[2]}°")
    print(f"  Predicted Temperature: {pred:.1f}°C")
```

## ⏰ Temporal Analysis

### Create Time Series Data

```python
# Create time series data for a few cities
import datetime

# Generate monthly temperature data for the past year
dates = pd.date_range('2023-01-01', '2023-12-31', freq='M')
n_cities_sample = 5

temporal_data = []
for city_idx in range(n_cities_sample):
    city = cities_gdf.iloc[city_idx]
    base_temp = city['temperature']
    
    for date in dates:
        # Add seasonal variation
        seasonal_temp = base_temp + 10 * np.sin(2 * np.pi * date.month / 12)
        # Add some random variation
        final_temp = seasonal_temp + np.random.normal(0, 2)
        
        temporal_data.append({
            'city_name': city['name'],
            'date': date,
            'temperature': final_temp,
            'longitude': city.geometry.x,
            'latitude': city.geometry.y
        })

temporal_df = pd.DataFrame(temporal_data)
print(f"✅ Created temporal dataset with {len(temporal_df)} observations")
```

### Analyze Temporal Patterns

```python
# Initialize temporal analyzer
temporal_analyzer = TemporalAnalyzer()

# Analyze trends for each city
trends = temporal_analyzer.analyze_trends(
    temporal_df, 
    time_column='date',
    value_column='temperature',
    group_column='city_name'
)

print("Temperature Trends by City:")
for city, trend in trends.items():
    print(f"{city}: {trend['slope']:.3f}°C/month ({trend['p_value']:.3f})")

# Detect seasonal patterns
seasonality = temporal_analyzer.detect_seasonality(
    temporal_df,
    time_column='date',
    value_column='temperature'
)

print(f"\nSeasonality detected: {seasonality['is_seasonal']}")
if seasonality['is_seasonal']:
    print(f"Seasonal period: {seasonality['period']} months")
```

### Visualize Temporal Patterns

```python
# Plot temperature time series for each city
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

for city_name in temporal_df['city_name'].unique():
    city_data = temporal_df[temporal_df['city_name'] == city_name]
    ax.plot(city_data['date'], city_data['temperature'], 
            marker='o', label=city_name, alpha=0.7)

ax.set_title('Temperature Time Series by City')
ax.set_xlabel('Date')
ax.set_ylabel('Temperature (°C)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## 🔍 Advanced Analysis

### Spatial-Temporal Analysis

```python
# Combine spatial and temporal analysis
spatiotemporal_analyzer = spatial_analyzer.combine_with_temporal(temporal_analyzer)

# Analyze spatial-temporal patterns
patterns = spatiotemporal_analyzer.analyze_patterns(
    cities_gdf,
    temporal_df,
    spatial_id_column='name',
    temporal_id_column='city_name'
)

print("Spatial-Temporal Analysis Results:")
print(f"Global trend: {patterns['global_trend']:.3f}°C/month")
print(f"Spatial autocorrelation: {patterns['spatial_autocorr']:.3f}")
```

### Uncertainty Quantification

```python
# Quantify uncertainty in predictions
uncertainty_analysis = ai_model.quantify_uncertainty(
    new_locations,
    n_samples=1000
)

print("Prediction Uncertainty:")
for i, (location, uncertainty) in enumerate(zip(new_locations, uncertainty_analysis)):
    print(f"Location {i+1}:")
    print(f"  Mean: {uncertainty['mean']:.1f}°C")
    print(f"  Std: {uncertainty['std']:.1f}°C")
    print(f"  95% CI: [{uncertainty['ci_lower']:.1f}, {uncertainty['ci_upper']:.1f}]°C")
```

## 📈 Results Summary

### Key Findings

```python
# Summarize your analysis
print("=== ANALYSIS SUMMARY ===")
print(f"Dataset: {len(cities_gdf)} cities across the US")
print(f"Population range: {cities_gdf['population'].min():,.0f} - {cities_gdf['population'].max():,.0f}")
print(f"Temperature range: {cities_gdf['temperature'].min():.1f}°C - {cities_gdf['temperature'].max():.1f}°C")
print(f"Elevation range: {cities_gdf['elevation'].min():.0f}m - {cities_gdf['elevation'].max():.0f}m")

print(f"\nSpatial Analysis:")
print(f"- Created {len(set(clusters))} spatial clusters")
print(f"- Found {len(nearby_cities)} nearby city pairs")

print(f"\nTemporal Analysis:")
print(f"- Analyzed {len(temporal_df)} temporal observations")
print(f"- Detected seasonality: {seasonality['is_seasonal']}")

print(f"\nActive Inference:")
print(f"- Trained model on {len(X)} observations")
print(f"- Made predictions for {len(new_locations)} new locations")
```

### Save Your Results

```python
# Save your analysis results
import json

results = {
    'spatial_stats': spatial_stats.to_dict(),
    'clustering': cities_gdf['cluster'].value_counts().to_dict(),
    'temporal_trends': trends,
    'predictions': {
        'locations': new_locations.tolist(),
        'temperatures': predictions
    },
    'uncertainty': uncertainty_analysis
}

with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✅ Analysis results saved to 'analysis_results.json'")
```

## 🎯 What You've Accomplished

Congratulations! You've completed your first comprehensive GEO-INFER analysis:

✅ **Data Loading & Exploration** - Loaded and explored geospatial data  
✅ **Spatial Analysis** - Performed clustering and spatial relationships  
✅ **Visualization** - Created static and interactive maps  
✅ **Active Inference** - Built and used an AI model for prediction  
✅ **Temporal Analysis** - Analyzed time series patterns  
✅ **Uncertainty Quantification** - Assessed prediction confidence  

## 🔗 Next Steps

### Explore More Examples
- **[Environmental Monitoring](../examples/environmental_monitoring.md)** - Climate and ecosystem analysis
- **[Urban Planning](../examples/urban_planning.md)** - City and infrastructure analysis
- **[Agricultural Applications](../examples/agricultural_applications.md)** - Crop and soil analysis

### Learn Advanced Techniques
- **[Custom Models](../advanced/custom_models.md)** - Build specialized active inference models
- **[Performance Optimization](../advanced/performance_optimization.md)** - Speed up your analyses
- **[Large-scale Analysis](../advanced/scaling_guide.md)** - Handle big data

### Join the Community
- **[Community Forum](https://forum.geo-infer.org)** - Share your results and get help
- **[GitHub Repository](https://github.com/geo-infer/geo-infer-intra)** - Contribute to the project
- **[Documentation](../index.md)** - Explore the full documentation

## 🚨 Troubleshooting

### Common Issues

**Issue**: Import errors for GEO-INFER modules
```python
# Solution: Check installation
import geo_infer_space
import geo_infer_time
import geo_infer_act
print("✅ All modules imported successfully!")
```

**Issue**: Memory errors with large datasets
```python
# Solution: Use chunked processing
spatial_analyzer = SpatialAnalyzer(chunk_size=1000)
```

**Issue**: Slow performance
```python
# Solution: Enable parallel processing
import os
os.environ['GEO_INFER_MAX_WORKERS'] = '4'
```

### Getting Help

If you encounter issues:

1. **Check the [FAQ](../support/faq.md)** for common solutions
2. **Search [GitHub Issues](https://github.com/geo-infer/geo-infer-intra/issues)**
3. **Ask on the [Community Forum](https://forum.geo-infer.org)**
4. **Review the [Troubleshooting Guide](../support/troubleshooting.md)**

---

**Ready for more?** Explore the [Advanced Examples](../examples/advanced_examples.md) or dive into [Custom Model Development](../advanced/custom_models.md)! 