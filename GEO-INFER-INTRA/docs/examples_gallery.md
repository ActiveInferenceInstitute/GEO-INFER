# GEO-INFER Examples Gallery

This gallery showcases a variety of use cases and examples demonstrating the capabilities of the GEO-INFER framework. Each example includes description, code snippets, visualizations, and links to full notebook implementations.

## 🌎 Spatial Analysis Examples

### H3 Grid Indexing and Analysis

![H3 Indexing](./images/examples/h3_indexing_example.png)

This example demonstrates using the H3 spatial indexing system for efficient geospatial analysis.

```python
from geo_infer_space import indexing
import geopandas as gpd
import matplotlib.pyplot as plt

# Load sample data
gdf = gpd.read_file("data/urban_areas.geojson")

# Create H3 indexes for the geometries at resolution 8
h3_indexes = indexing.geometries_to_h3(gdf.geometry, resolution=8)

# Visualize H3 cells
indexing.plot_h3_cells(h3_indexes, figsize=(12, 8), 
                      title="Urban Areas Indexed with H3")
```

[Full Notebook](../examples/spatial/h3_indexing_example.ipynb) | [Interactive Demo](https://geo-infer.org/demos/h3-indexing)

### Spatial Clustering of Geographic Features

![Spatial Clustering](./images/examples/spatial_clustering_example.png)

This example shows how to perform spatial clustering on geographic features to identify natural groupings.

```python
from geo_infer_space import clustering
import geopandas as gpd

# Load point data
points_gdf = gpd.read_file("data/poi_locations.geojson")

# Perform DBSCAN clustering
clustered_gdf = clustering.dbscan_cluster(
    points_gdf,
    eps=0.01,  # Distance in degrees (approximately 1km at equator)
    min_samples=5,
    return_clusters=True
)

# Visualize the clusters
clustering.plot_spatial_clusters(clustered_gdf, figsize=(14, 10),
                               cluster_column='cluster',
                               title="Spatial Clustering of Points of Interest")
```

[Full Notebook](../examples/spatial/spatial_clustering_example.ipynb)

## ⏱️ Temporal Analysis Examples

### Time Series Forecasting with Geospatial Context

![Time Series Forecasting](./images/examples/geospatial_time_series_example.png)

This example demonstrates time series forecasting for spatial data, incorporating geographic context to improve predictions.

```python
from geo_infer_time import forecasting
from geo_infer_space import features
import pandas as pd
import geopandas as gpd

# Load time series data with spatial coordinates
data = pd.read_csv("data/temperature_readings.csv", parse_dates=['timestamp'])
geometry = gpd.points_from_xy(data.longitude, data.latitude)
gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")

# Extract spatial features
spatial_features = features.extract_topographic_features(gdf, 
                                                     dem_path="data/elevation.tif")

# Create and train forecasting model
model = forecasting.SpatioTemporalForecaster(
    time_column='timestamp',
    value_column='temperature',
    spatial_features=['elevation', 'slope', 'aspect'],
    temporal_features=['hour', 'dayofweek', 'month'],
    forecast_horizon=24  # 24 hour forecast
)

model.fit(gdf)
predictions = model.predict()

# Visualize results
forecasting.plot_spatiotemporal_forecast(gdf, predictions, 
                                      locations=['Station1', 'Station2', 'Station3'])
```

[Full Notebook](../examples/temporal/geospatial_time_series_example.ipynb)

### Change Detection in Satellite Imagery

![Change Detection](./images/examples/change_detection_example.png)

This example shows how to detect changes in land cover using multi-temporal satellite imagery.

```python
from geo_infer_time import change_detection
import rioxarray as rxr
import matplotlib.pyplot as plt

# Load imagery from two time periods
img_t1 = rxr.open_rasterio("data/landsat_2010.tif")
img_t2 = rxr.open_rasterio("data/landsat_2020.tif")

# Perform change detection
change_map = change_detection.detect_changes(
    img_t1, 
    img_t2, 
    method='cvaps',  # Change Vector Analysis in Posterior Space
    threshold=0.8
)

# Visualize the detected changes
fig, ax = plt.subplots(figsize=(12, 12))
change_detection.plot_change_map(change_map, ax=ax, 
                              title="Land Cover Changes 2010-2020",
                              legend=True)
```

[Full Notebook](../examples/temporal/change_detection_example.ipynb)

## 🧠 Active Inference Examples

### Spatial Active Inference for Agent Movement

![Active Inference Agent](./images/examples/active_inference_agent_example.png)

This example demonstrates how to build a spatial agent that navigates using active inference principles.

```python
from geo_infer_agent import spatial_agent
from geo_infer_space import environment
import matplotlib.pyplot as plt

# Create a spatial environment
env = environment.GridEnvironment(
    width=20, 
    height=20,
    obstacles=[(5, 5), (5, 6), (5, 7), (6, 7), (7, 7)],
    goal=(15, 15)
)

# Create an active inference agent
agent = spatial_agent.ActiveInferenceAgent(
    env=env,
    initial_position=(2, 2),
    precision=10.0,  # Confidence in predictions
    planning_horizon=5
)

# Run simulation
trajectories = agent.simulate(steps=30)

# Visualize agent behavior
spatial_agent.plot_agent_trajectory(
    env, 
    trajectories,
    title="Active Inference Navigation in Spatial Environment"
)
```

[Full Notebook](../examples/active_inference/spatial_agent_example.ipynb) | [Interactive Demo](https://geo-infer.org/demos/active-inference-navigation)

### Bayesian Belief Updating with Spatial Observations

![Bayesian Belief Updating](./images/examples/bayesian_belief_updating_example.png)

This example shows how to perform Bayesian belief updating in a spatial context, using active inference principles.

```python
from geo_infer_bayes import spatial_inference
from geo_infer_space import visualization
import numpy as np
import matplotlib.pyplot as plt

# Create a spatial prior (initial belief)
lat_range = np.linspace(34.0, 34.1, 100)
lon_range = np.linspace(-118.4, -118.3, 100)
spatial_prior = spatial_inference.create_gaussian_spatial_prior(
    lat_range=lat_range,
    lon_range=lon_range,
    center=(34.05, -118.35),
    sigma=0.02
)

# Simulated observations with location uncertainty
observations = [
    ((34.07, -118.36), 0.8),  # (location, confidence)
    ((34.06, -118.33), 0.9),
    ((34.03, -118.37), 0.7),
]

# Update beliefs with observations
posterior = spatial_inference.update_spatial_beliefs(
    spatial_prior, 
    observations,
    method='variational'
)

# Visualize prior and posterior beliefs
fig, axes = plt.subplots(1, 2, figsize=(15, 7))
visualization.plot_spatial_distribution(spatial_prior, 
                                     ax=axes[0],
                                     title="Spatial Prior")
visualization.plot_spatial_distribution(posterior, 
                                     ax=axes[1],
                                     title="Posterior After Observations")
```

[Full Notebook](../examples/active_inference/bayesian_updating_example.ipynb)

## 🔄 Integrated Examples

### Cross-Module Urban Analysis Workflow

![Urban Analysis](./images/examples/urban_analysis_example.png)

This comprehensive example demonstrates an integrated workflow combining multiple GEO-INFER modules for urban analysis.

```python
# Import from multiple modules
from geo_infer_space import indexing, features
from geo_infer_time import patterns
from geo_infer_data import loader
from geo_infer_civ import urban_metrics
from geo_infer_act import generative_models
import matplotlib.pyplot as plt

# Load urban data
urban_data = loader.load_geospatial_dataset("urban_analysis")

# Create spatial indexes
h3_indexes = indexing.geoseries_to_h3(urban_data.geometry, resolution=9)

# Extract urban features
urban_features = features.extract_urban_features(
    urban_data,
    include=["building_density", "road_density", "green_space_ratio"]
)

# Analyze temporal patterns
temporal_patterns = patterns.extract_temporal_patterns(
    urban_data["traffic_data"],
    temporal_resolution="1H"
)

# Calculate urban metrics
livability_scores = urban_metrics.calculate_livability_index(
    urban_features,
    weights={
        "building_density": -0.3,
        "road_density": -0.2,
        "green_space_ratio": 0.5
    }
)

# Create active inference model of urban dynamics
urban_model = generative_models.SpatioTemporalGenerativeModel(
    spatial_resolution=9,  # H3 resolution
    temporal_resolution="1D",
    features=urban_features.columns
)

urban_model.fit(urban_features, temporal_patterns)

# Predict future urban development
predictions = urban_model.predict(steps=30)  # 30-day forecast

# Visualize results in a comprehensive dashboard
fig = plt.figure(figsize=(16, 12))
# ... Complex visualization code ...
```

[Full Notebook](../examples/integrated/urban_analysis_example.ipynb)

### Environmental Monitoring and Prediction

![Environmental Monitoring](./images/examples/environmental_monitoring_example.png)

This example shows an integrated approach to environmental monitoring and prediction using multiple GEO-INFER modules.

```python
from geo_infer_space import raster
from geo_infer_time import forecasting
from geo_infer_data import remote_sensing
from geo_infer_act import active_sampling
import xarray as xr
import matplotlib.pyplot as plt

# Load multi-temporal satellite imagery
imagery = remote_sensing.load_satellite_timeseries(
    "data/landsat_timeseries",
    start_date="2020-01-01",
    end_date="2021-12-31",
    frequency="16D"  # Landsat revisit time
)

# Calculate vegetation indices
ndvi = remote_sensing.calculate_index(imagery, index="ndvi")
ndmi = remote_sensing.calculate_index(imagery, index="ndmi")

# Create environmental change model
env_model = forecasting.EnvironmentalChangeModel(
    indices=["ndvi", "ndmi"],
    spatial_resolution="30m",
    temporal_resolution="16D"
)

env_model.fit(xr.merge([ndvi, ndmi]))

# Use active inference to determine optimal sampling locations
optimal_locations = active_sampling.find_optimal_sampling_locations(
    env_model,
    n_locations=5,
    method="expected_information_gain"
)

# Forecast environmental changes
forecast = env_model.predict(steps=23)  # One year forecast

# Visualize environmental indicators and forecasts
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
# ... Complex visualization code ...
```

[Full Notebook](../examples/integrated/environmental_monitoring_example.ipynb)

## 🏙️ Domain-Specific Examples

### Agricultural Yield Prediction

![Agricultural Analysis](./images/examples/agricultural_yield_example.png)

This example demonstrates agricultural yield prediction using satellite imagery, weather data, and active inference principles.

```python
from geo_infer_ag import yield_prediction
from geo_infer_data import weather
from geo_infer_space import features
import geopandas as gpd
import pandas as pd

# Load field boundaries and historical yield data
fields = gpd.read_file("data/field_boundaries.geojson")
yield_history = pd.read_csv("data/historical_yields.csv")

# Get weather data for the region
weather_data = weather.get_weather_data(
    bounds=fields.total_bounds,
    start_date="2021-01-01",
    end_date="2021-12-31",
    variables=["temperature", "precipitation", "solar_radiation"]
)

# Extract satellite-derived vegetation indices
veg_indices = features.extract_vegetation_indices(
    fields.geometry,
    start_date="2021-01-01",
    end_date="2021-12-31",
    frequency="5D",
    indices=["ndvi", "evi", "ndmi"]
)

# Create yield prediction model
model = yield_prediction.ActiveInferenceYieldModel(
    crop_type="corn",
    spatial_features=True,
    weather_features=True,
    vegetation_indices=True
)

model.fit(
    field_geometries=fields.geometry,
    yield_data=yield_history,
    weather_data=weather_data,
    vegetation_data=veg_indices
)

# Make yield predictions
predicted_yield = model.predict(
    fields.geometry,
    current_weather=weather_data.loc["2021-05-01":"2021-07-31"],
    current_vegetation=veg_indices.loc["2021-05-01":"2021-07-31"]
)

# Visualize yield predictions
yield_prediction.plot_yield_forecast(
    fields,
    predicted_yield,
    title="Predicted Corn Yield for 2021",
    uncertainty=True
)
```

[Full Notebook](../examples/domains/agricultural_yield_example.ipynb)

### Urban Traffic Prediction

![Traffic Prediction](./images/examples/traffic_prediction_example.png)

This example shows how to predict urban traffic patterns using spatiotemporal data and active inference models.

```python
from geo_infer_civ import traffic
from geo_infer_time import temporal_patterns
from geo_infer_space import network_analysis
import osmnx as ox
import pandas as pd

# Get road network
G = ox.graph_from_place("San Francisco, CA", network_type="drive")

# Load traffic data
traffic_data = pd.read_csv("data/sf_traffic_data.csv", parse_dates=["timestamp"])

# Analyze road network
network_metrics = network_analysis.calculate_network_metrics(
    G,
    metrics=["betweenness", "closeness", "degree"]
)

# Extract temporal patterns
temporal_features = temporal_patterns.extract_features(
    traffic_data,
    timestamp_column="timestamp",
    value_column="speed",
    freq="1H"
)

# Create traffic prediction model
model = traffic.SpatioTemporalTrafficModel(
    temporal_features=["hour", "dayofweek", "month"],
    spatial_features=["betweenness", "closeness", "degree"],
    prediction_horizon=24  # 24 hours ahead
)

model.fit(
    traffic_data=traffic_data,
    network=G,
    network_metrics=network_metrics
)

# Predict traffic for next 24 hours
predictions = model.predict(horizon=24)

# Visualize predictions
traffic.visualize_traffic_prediction(
    G,
    predictions,
    title="24-Hour Traffic Speed Prediction",
    time_slider=True
)
```

[Full Notebook](../examples/domains/urban_traffic_example.ipynb) | [Interactive Demo](https://geo-infer.org/demos/traffic-prediction)

## 📊 Data Preparation and Visualization Examples

### GeoDataFrame Preprocessing Pipeline

![Data Preprocessing](./images/examples/data_preprocessing_example.png)

This example demonstrates a complete geospatial data preprocessing pipeline.

```python
from geo_infer_data import preprocessing
from geo_infer_space import transformations
import geopandas as gpd

# Load raw data
gdf = gpd.read_file("data/raw_points.geojson")

# Complete preprocessing pipeline
processed_gdf = (
    preprocessing.Pipeline()
    .add_step(preprocessing.CleanGeometries())
    .add_step(preprocessing.RemoveOutliers(columns=["value"], method="iqr"))
    .add_step(preprocessing.NormalizeValues(columns=["value"]))
    .add_step(transformations.ReprojectCRS(target_crs="EPSG:3857"))
    .add_step(preprocessing.SpatialJoin(
        right=gpd.read_file("data/regions.geojson"),
        how="inner"
    ))
    .execute(gdf)
)

# Validate results
validation_results = preprocessing.validate_gdf(
    processed_gdf,
    rules={
        "geometry_types": ["Point"],
        "crs": "EPSG:3857",
        "required_columns": ["value", "region_id"],
        "value_ranges": {"value": (-3, 3)}
    }
)

print(f"Validation passed: {validation_results['passed']}")
if not validation_results['passed']:
    print(validation_results['failed_checks'])
```

[Full Notebook](../examples/data/preprocessing_example.ipynb)

### Advanced Geospatial Visualization

![Advanced Visualization](./images/examples/advanced_visualization_example.png)

This example shows how to create advanced, publication-quality geospatial visualizations.

```python
from geo_infer_app import visualization
from geo_infer_space import cartography
import geopandas as gpd
import matplotlib.pyplot as plt

# Load datasets
counties = gpd.read_file("data/counties.geojson")
rivers = gpd.read_file("data/rivers.geojson")
cities = gpd.read_file("data/cities.geojson")

# Create advanced visualization
fig, ax = plt.subplots(figsize=(15, 10))

# Base layer with thematic coloring
visualization.choropleth(
    counties,
    column="population",
    scheme="quantiles",
    k=5,
    cmap="Blues",
    legend=True,
    legend_title="Population",
    ax=ax
)

# Add rivers with styled lines
visualization.line_layer(
    rivers,
    color="skyblue",
    linewidth=rivers.apply(lambda x: 0.5 + x.flow_volume * 0.1),
    alpha=0.7,
    zorder=2,
    ax=ax
)

# Add cities with sized points
visualization.point_layer(
    cities,
    size=cities.apply(lambda x: 20 + x.population/50000),
    color="red",
    alpha=0.7,
    zorder=3,
    ax=ax
)

# Add cartographic elements
cartography.add_scale_bar(ax)
cartography.add_north_arrow(ax)
cartography.add_basemap(ax, source="contextily", crs=counties.crs)

# Styling and layout
visualization.style_map(
    ax,
    title="Population Distribution with Hydrography",
    title_fontsize=18,
    frame=True,
    grid=True
)
```

[Full Notebook](../examples/visualization/advanced_visualization_example.ipynb)

## Contributing Examples

We welcome contributions to this example gallery! To submit your own example:

1. Follow the [Contribution Guidelines](./developer_guide/contributing.md)
2. Use the [Example Template](./templates/example_template.ipynb)
3. Submit a pull request with your example notebook and a short description

## Additional Resources

- [Interactive Demos](https://geo-infer.org/demos)
- [Video Tutorials](https://geo-infer.org/tutorials)
- [Training Workshops](https://geo-infer.org/workshops)
- [Community Examples](https://github.com/geo-infer/community-examples) 