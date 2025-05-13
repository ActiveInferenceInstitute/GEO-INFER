# GEO-INFER Cookbook

This cookbook provides practical examples for common operations in the GEO-INFER framework. Each recipe includes code snippets and explanations for specific tasks.

## Spatial Data Processing

### Loading and Transforming Vector Data

```python
from geo_infer_space import io, transformations
import geopandas as gpd

# Load vector data
gdf = io.read_vector("path/to/data.geojson")

# Reproject to Web Mercator
gdf_projected = transformations.reproject(gdf, target_crs="EPSG:3857")

# Buffer points (e.g., to create service areas)
buffered = transformations.buffer(
    gdf, 
    distance=1000,  # 1km buffer
    dissolve=True   # Merge overlapping buffers
)

# Simplify complex geometries
simplified = transformations.simplify(
    gdf,
    tolerance=100,  # Simplification tolerance
    preserve_topology=True
)

# Export to different format
io.write_vector(gdf, "output.gpkg", driver="GPKG")
```

### Working with Raster Data

```python
from geo_infer_space import raster
import numpy as np

# Load raster data
dem = raster.read_raster("path/to/elevation.tif")

# Calculate derived products
slope = raster.calculate_slope(dem)
aspect = raster.calculate_aspect(dem)

# Reclassify values
slope_classes = raster.reclassify(
    slope,
    breaks=[0, 5, 15, 30, 90],
    labels=["Flat", "Gentle", "Moderate", "Steep"]
)

# Zonal statistics
zones = raster.read_vector("path/to/zones.geojson")
stats = raster.zonal_statistics(
    dem,
    zones,
    stats=['min', 'mean', 'max', 'std']
)

# Export results
raster.write_raster(slope, "slope.tif")
```

### H3 Spatial Indexing

```python
from geo_infer_space import indexing
import geopandas as gpd

# Create H3 indexes for points
points = gpd.read_file("path/to/points.geojson")
h3_indexes = indexing.points_to_h3(
    points.geometry,
    resolution=9  # H3 resolution level
)

# Create H3 indexes for polygons
polygons = gpd.read_file("path/to/polygons.geojson")
h3_indexes = indexing.polygons_to_h3(
    polygons.geometry,
    resolution=8
)

# Get neighboring cells
neighbors = indexing.get_h3_neighbors(h3_indexes[0])

# Convert H3 indexes to polygons
h3_polygons = indexing.h3_to_polygons(h3_indexes)

# Visualize H3 cells
indexing.plot_h3_cells(h3_indexes, figsize=(10, 8))
```

## Temporal Data Analysis

### Time Series Processing

```python
from geo_infer_time import processing
import pandas as pd

# Load time series data
df = pd.read_csv("path/to/timeseries.csv", parse_dates=["timestamp"])

# Detect and handle outliers
cleaned = processing.remove_outliers(
    df,
    value_column="temperature",
    method="iqr",  # Interquartile range method
    threshold=1.5
)

# Fill missing values
filled = processing.fill_missing(
    cleaned,
    value_column="temperature",
    method="linear"  # Linear interpolation
)

# Aggregate to different time resolution
daily = processing.aggregate_time(
    filled,
    time_column="timestamp",
    value_column="temperature",
    freq="1D",
    agg_func="mean"
)

# Detrend time series
detrended = processing.detrend(
    daily,
    value_column="temperature",
    method="linear"
)
```

### Detecting Temporal Patterns

```python
from geo_infer_time import patterns
import pandas as pd

# Load time series data
df = pd.read_csv("path/to/timeseries.csv", parse_dates=["timestamp"])

# Detect seasonality
seasonality = patterns.detect_seasonality(
    df,
    value_column="temperature",
    time_column="timestamp"
)
print(f"Detected seasonality: {seasonality['period']} days")

# Detect trend
trend_results = patterns.detect_trend(
    df,
    value_column="temperature",
    time_column="timestamp",
    method="mann_kendall"
)
print(f"Trend p-value: {trend_results['p_value']}")

# Extract periodic components
components = patterns.extract_components(
    df,
    value_column="temperature",
    time_column="timestamp"
)
trend = components['trend']
seasonal = components['seasonal']
residual = components['residual']

# Detect change points
changes = patterns.detect_changepoints(
    df,
    value_column="temperature",
    time_column="timestamp",
    method="binary_segmentation"
)
```

### Time Series Forecasting

```python
from geo_infer_time import forecasting
import pandas as pd

# Load time series data
df = pd.read_csv("path/to/timeseries.csv", parse_dates=["timestamp"])

# Create and train forecasting model
model = forecasting.TimeSeriesForecaster(
    method="arima",
    time_column="timestamp",
    value_column="temperature"
)
model.fit(df)

# Generate forecast
forecast = model.forecast(
    horizon=30,  # 30 time steps ahead
    return_conf_int=True,
    conf_level=0.95
)

# Visualize results
forecasting.plot_forecast(
    historical_data=df,
    forecast=forecast,
    time_column="timestamp",
    value_column="temperature"
)
```

## Active Inference Models

### Creating and Using Generative Models

```python
from geo_infer_act import generative_models
import numpy as np

# Define state and observation spaces
state_space = {
    'temperature': np.linspace(0, 40, 41),
    'humidity': np.linspace(0, 100, 101)
}

# Create generative model
model = generative_models.GenerativeModel(
    state_space=state_space,
    state_prior={'temperature': 20, 'humidity': 50},
    precision=10.0
)

# Define observation model
def observation_fn(state):
    # Simulate noisy observations
    noise = np.random.normal(0, 0.5)
    return {
        'temperature': state['temperature'] + noise,
        'humidity': state['humidity'] + np.random.normal(0, 2)
    }

model.set_observation_model(observation_fn)

# Define transition model
def transition_fn(state, action=None):
    # Simple linear dynamics with some noise
    return {
        'temperature': state['temperature'] + 0.1 + np.random.normal(0, 0.1),
        'humidity': state['humidity'] - 0.2 + np.random.normal(0, 0.3)
    }

model.set_transition_model(transition_fn)

# Update beliefs with an observation
observation = {'temperature': 22.5}
updated_state = model.update_beliefs(observation)

# Predict future state
predicted_state = model.predict(steps=5)
```

### Spatial Active Inference

```python
from geo_infer_act import spatial_inference
from geo_infer_space import io
import geopandas as gpd

# Load spatial data
gdf = io.read_vector("path/to/locations.geojson")

# Create spatial model for temperature prediction
model = spatial_inference.SpatialGenerativeModel(
    spatial_resolution=9,  # H3 resolution
    variables=['temperature', 'elevation'],
    precision=5.0
)

# Initialize with prior knowledge
model.set_prior(
    variable='temperature',
    mean=20,
    variance=4
)

# Add spatial correlation structure
model.set_spatial_correlation(
    variable='temperature',
    correlation_type='exponential',
    range_parameter=1000  # meters
)

# Update with observations
observations = [
    {'location': (37.7749, -122.4194), 'temperature': 18.5},
    {'location': (37.7849, -122.4294), 'temperature': 17.8}
]
model.update(observations)

# Get beliefs at a specific location
belief = model.get_belief(location=(37.7719, -122.4144))
print(f"Mean: {belief.mean}, Variance: {belief.variance}")

# Generate a spatial prediction map
prediction_map = model.predict_map(
    bbox=(-122.5, 37.7, -122.3, 37.9),
    variable='temperature'
)

# Visualize prediction map
spatial_inference.plot_belief_map(
    prediction_map,
    variable='temperature',
    cmap='viridis',
    show_uncertainty=True
)
```

## Data Integration

### Loading and Transforming Data

```python
from geo_infer_data import datasets, transformations
import pandas as pd

# Load dataset from various sources
climate_data = datasets.load_dataset(
    source="path/to/climate_data.nc",
    variables=["temperature", "precipitation"]
)

# Load from remote source
remote_data = datasets.load_dataset(
    source="https://example.com/api/data",
    source_type="api",
    api_key="your_api_key"
)

# Transform data
transformed = transformations.normalize_variables(
    climate_data,
    variables=["temperature"]
)

# Join datasets
joined = datasets.join_datasets(
    left=climate_data,
    right=remote_data,
    on="location_id",
    how="inner"
)

# Filter dataset
filtered = datasets.filter_dataset(
    joined,
    filter_expr="temperature > 25 and precipitation < 10"
)

# Export to standard format
datasets.export_dataset(
    filtered,
    output_path="filtered_data.nc",
    format="netcdf"
)
```

### Working with Common Data Sources

```python
from geo_infer_data import sources
import geopandas as gpd

# Access OpenStreetMap data
osm_data = sources.load_osm_data(
    bbox=(-122.5, 37.7, -122.3, 37.9),
    tags={"highway": True, "building": True}
)

# Access Sentinel-2 imagery
imagery = sources.load_sentinel2(
    bbox=(-122.5, 37.7, -122.3, 37.9),
    start_date="2023-01-01",
    end_date="2023-02-01",
    max_cloud_cover=20,
    bands=["B2", "B3", "B4", "B8"]
)

# Access digital elevation model
dem = sources.load_dem(
    bbox=(-122.5, 37.7, -122.3, 37.9),
    source="srtm",
    resolution=30  # meters
)

# Access climate data
climate = sources.load_climate_data(
    bbox=(-122.5, 37.7, -122.3, 37.9),
    variables=["temperature", "precipitation"],
    start_date="1990-01-01",
    end_date="2020-12-31",
    temporal_resolution="monthly"
)
```

## Visualization

### Creating Maps

```python
from geo_infer_app import maps
import geopandas as gpd

# Load data
gdf = gpd.read_file("path/to/data.geojson")

# Create a basic map
m = maps.create_map(
    gdf,
    column="value",
    cmap="viridis",
    legend=True,
    legend_title="Value",
    title="My Map"
)

# Add basemap
m = maps.add_basemap(
    m,
    source="contextily",
    style="satellite"
)

# Add scale bar and north arrow
m = maps.add_map_elements(
    m,
    scale_bar=True,
    north_arrow=True
)

# Export map
maps.export_map(
    m,
    output_path="map.png",
    dpi=300
)

# Create interactive web map
web_map = maps.create_interactive_map(
    gdf,
    column="value",
    popup_columns=["name", "value"],
    style_function=lambda x: {
        'fillColor': '#ff0000' if x['properties']['value'] > 50 else '#0000ff',
        'weight': 1,
        'opacity': 0.7
    }
)

# Save interactive map
web_map.save("interactive_map.html")
```

### Creating Charts

```python
from geo_infer_app import charts
import pandas as pd

# Load data
df = pd.read_csv("path/to/data.csv", parse_dates=["date"])

# Create time series chart
fig = charts.create_time_series_chart(
    df,
    time_column="date",
    value_column="temperature",
    title="Temperature Over Time",
    y_label="Temperature (°C)",
    show_trend=True
)

# Create comparison chart
fig = charts.create_comparison_chart(
    df,
    value_columns=["temperature", "humidity"],
    time_column="date",
    title="Temperature and Humidity"
)

# Create spatial distribution chart
fig = charts.create_spatial_distribution_chart(
    df,
    value_column="temperature",
    lat_column="latitude",
    lon_column="longitude",
    title="Spatial Distribution of Temperature"
)

# Save chart
charts.save_chart(
    fig,
    output_path="chart.png",
    dpi=300
)
```

## Domain Applications

### Agricultural Analysis

```python
from geo_infer_ag import crop_analysis
import geopandas as gpd

# Load field boundaries
fields = gpd.read_file("path/to/fields.geojson")

# Calculate vegetation indices
indices = crop_analysis.calculate_vegetation_indices(
    fields,
    imagery_path="path/to/imagery.tif",
    indices=["ndvi", "evi", "ndmi"]
)

# Detect crop stress
stress = crop_analysis.detect_crop_stress(
    indices,
    ndvi_threshold=0.4,
    method="zscore"
)

# Calculate zonal statistics
stats = crop_analysis.calculate_field_statistics(
    fields,
    indices,
    statistics=["mean", "std", "min", "max"]
)

# Forecast yield
yield_forecast = crop_analysis.forecast_yield(
    fields,
    historical_yield="path/to/historical_yield.csv",
    current_indices=indices,
    weather_data="path/to/weather_data.csv"
)

# Visualize results
crop_analysis.plot_field_indices(
    fields,
    indices,
    index_name="ndvi",
    cmap="YlGn",
    title="NDVI by Field"
)
```

### Urban Analysis

```python
from geo_infer_civ import urban_analysis
import geopandas as gpd

# Load urban data
buildings = gpd.read_file("path/to/buildings.geojson")
roads = gpd.read_file("path/to/roads.geojson")

# Calculate urban density metrics
density = urban_analysis.calculate_density_metrics(
    buildings,
    metrics=["floor_area_ratio", "building_coverage_ratio"],
    spatial_resolution=100  # meters
)

# Analyze road network
network_metrics = urban_analysis.analyze_road_network(
    roads,
    metrics=["connectivity", "betweenness", "closeness"],
    weight_column="length"
)

# Calculate accessibility
accessibility = urban_analysis.calculate_accessibility(
    points_of_interest="path/to/poi.geojson",
    road_network=roads,
    distance_threshold=1000,  # meters
    population="path/to/population.geojson"
)

# Calculate mixed use metrics
mixed_use = urban_analysis.calculate_mixed_use_metrics(
    buildings,
    use_column="building_use",
    spatial_resolution=250  # meters
)

# Visualize urban form
urban_analysis.visualize_urban_form(
    buildings,
    density,
    title="Urban Density Analysis"
)
```

### Risk Assessment

```python
from geo_infer_risk import assessment
import geopandas as gpd

# Load hazard and asset data
hazard = gpd.read_file("path/to/flood_hazard.geojson")
assets = gpd.read_file("path/to/buildings.geojson")

# Calculate exposure
exposure = assessment.calculate_exposure(
    assets,
    hazard,
    hazard_column="flood_depth"
)

# Calculate vulnerability
vulnerability = assessment.calculate_vulnerability(
    exposure,
    vulnerability_curves="path/to/vulnerability_curves.json",
    asset_type_column="building_type"
)

# Calculate risk
risk = assessment.calculate_risk(
    vulnerability,
    hazard_probability_column="annual_probability",
    asset_value_column="value"
)

# Create risk map
assessment.create_risk_map(
    risk,
    risk_column="risk_value",
    classification_method="quantiles",
    classes=5,
    cmap="OrRd",
    title="Flood Risk Map"
)

# Calculate risk statistics
statistics = assessment.calculate_risk_statistics(
    risk,
    aggregation_units="path/to/admin_boundaries.geojson"
)
```

## Workflow Integration

### Creating and Running Workflows

```python
from geo_infer_intra import workflows
import geopandas as gpd

# Define a workflow
workflow = workflows.create_workflow(
    name="Urban Heat Island Analysis",
    description="Analyze urban heat island effect using land cover and temperature data"
)

# Add steps to the workflow
workflow.add_step(
    name="load_data",
    function="geo_infer_data.datasets.load_dataset",
    parameters={
        "source": "path/to/landcover.tif",
        "source_type": "raster"
    }
)

workflow.add_step(
    name="calculate_ndvi",
    function="geo_infer_space.indices.calculate_ndvi",
    parameters={
        "red_band": "B4",
        "nir_band": "B8"
    },
    inputs=["load_data"]
)

workflow.add_step(
    name="load_temperature",
    function="geo_infer_data.datasets.load_dataset",
    parameters={
        "source": "path/to/temperature.csv",
        "source_type": "csv"
    }
)

workflow.add_step(
    name="correlate_ndvi_temperature",
    function="geo_infer_space.statistics.calculate_correlation",
    parameters={
        "method": "pearson"
    },
    inputs=["calculate_ndvi", "load_temperature"]
)

workflow.add_step(
    name="create_visualization",
    function="geo_infer_app.maps.create_map",
    parameters={
        "cmap": "coolwarm",
        "title": "NDVI vs Temperature"
    },
    inputs=["correlate_ndvi_temperature"]
)

# Save workflow
workflows.save_workflow(workflow, "urban_heat_island_workflow.json")

# Execute workflow
results = workflows.execute_workflow(workflow)

# Access results
correlation = results["correlate_ndvi_temperature"]
visualization = results["create_visualization"]
```

### Scheduling and Automation

```python
from geo_infer_intra import automation
import datetime

# Schedule a workflow to run periodically
scheduler = automation.create_scheduler()

# Add a daily task
scheduler.add_task(
    name="daily_vegetation_monitoring",
    workflow="vegetation_monitoring_workflow.json",
    schedule="daily",
    time="02:00"  # 2 AM
)

# Add a weekly task
scheduler.add_task(
    name="weekly_risk_assessment",
    workflow="risk_assessment_workflow.json",
    schedule="weekly",
    day="Monday",
    time="01:00"  # 1 AM
)

# Add a task with specific dates
scheduler.add_task(
    name="monthly_report_generation",
    workflow="report_generation_workflow.json",
    schedule="monthly",
    day=1,  # First day of the month
    time="03:00"  # 3 AM
)

# Start the scheduler
scheduler.start()

# Check task status
status = scheduler.get_task_status("daily_vegetation_monitoring")
print(f"Task status: {status}")

# Manually trigger a task
scheduler.run_task("weekly_risk_assessment")
```

## API Integration

### Using the GEO-INFER API

```python
from geo_infer_api import client
import json

# Initialize API client
api = client.GeoInferAPI(
    base_url="https://api.geo-infer.org/v1",
    api_key="your_api_key"
)

# Load data from a file
with open("path/to/data.geojson", "r") as f:
    data = json.load(f)

# Call spatial analysis endpoint
response = api.space.analyze_vector(
    data=data,
    analysis_type="buffer",
    parameters={"distance": 1000}
)

# Call time series analysis endpoint
response = api.time.analyze_time_series(
    data="path/to/timeseries.csv",
    analysis_type="seasonality_detection",
    parameters={"value_column": "temperature"}
)

# Call active inference endpoint
response = api.act.create_belief_map(
    observations=[
        {"location": [37.7749, -122.4194], "value": 18.5},
        {"location": [37.7849, -122.4294], "value": 17.8}
    ],
    variable="temperature",
    parameters={"resolution": 9, "precision": 5.0}
)

# Access domain-specific endpoints
response = api.risk.assess_flood_risk(
    assets="path/to/buildings.geojson",
    hazard="path/to/flood_depth.geojson",
    parameters={"vulnerability_curves": "default"}
)

# Save response to file
with open("api_results.json", "w") as f:
    json.dump(response, f, indent=2)
```

## Additional Resources

- [Complete API Reference](../api/index.md)
- [Detailed Examples Gallery](../examples_gallery.md)
- [Geospatial Concepts Guide](../geospatial/index.md)
- [Advanced Active Inference Guide](../active_inference_guide.md) 