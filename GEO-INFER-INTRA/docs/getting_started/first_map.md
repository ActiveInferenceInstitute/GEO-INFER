# Your First Map

> **Tutorial**: Create a geospatial visualization using GEO-INFER-SPACE
>
> This step-by-step tutorial walks you through loading spatial data, building
> an interactive map, visualizing H3 hexagonal grids, and exporting results.

## Prerequisites

From the repository root, sync the workspace before starting:

```bash
uv sync --package geo-infer-space
```

You also need these Python packages (installed as GEO-INFER-SPACE dependencies):

- `geopandas` -- spatial data manipulation
- `folium` -- interactive Leaflet maps
- `h3` (v4+) -- hexagonal spatial indexing
- `shapely` -- geometric operations
- `matplotlib` -- static map rendering
- `numpy` -- numerical operations

Verify your environment:

```
```python
import geopandas as gpd
import folium
import h3
import numpy as np
from geo_infer_space import latlng_to_cell, cell_to_latlng

print(f"geopandas: {gpd.__version__}")
print(f"h3: {h3.__version__}")
print(f"GEO-INFER-SPACE loaded")
```

## Step 1: Load Spatial Data

We will work with point data representing sensor readings across a metro area.
In practice, you would load data from a GeoJSON file, shapefile, or database.
For this tutorial, we generate sample data:

```
```python
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

np.random.seed(42)
n_sensors = 60

# San Francisco Bay Area bounding box
lats = np.random.uniform(37.3, 37.9, n_sensors)
lngs = np.random.uniform(-122.6, -122.0, n_sensors)

# Simulated air quality index (AQI) readings
aqi_values = np.random.gamma(shape=3, scale=15, size=n_sensors).clip(10, 200)

sensors = gpd.GeoDataFrame({
    "sensor_id": [f"AQ-{i:03d}" for i in range(n_sensors)],
    "aqi": np.round(aqi_values, 1),
    "geometry": [Point(lng, lat) for lng, lat in zip(lngs, lats)]
}, crs="EPSG:4326")

print(f"Loaded {len(sensors)} sensors")
print(sensors.head())
```

To load from a file instead:

```
```python
# GeoJSON
sensors = gpd.read_file("path/to/sensors.geojson")

# Shapefile
sensors = gpd.read_file("path/to/sensors.shp")

# CSV with lat/lng columns
import pandas as pd
df = pd.read_csv("sensors.csv")
sensors = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.longitude, df.latitude),
    crs="EPSG:4326"
)
```

## Step 2: Create a Basic Interactive Map

`folium` generates Leaflet.js maps that run in any browser. Each marker
represents a sensor, colored by AQI category.

```
```python
import folium

# Center the map on the data
center_lat = sensors.geometry.y.mean()
center_lng = sensors.geometry.x.mean()

m = folium.Map(
    location=[center_lat, center_lng],
    zoom_start=10,
    tiles="CartoDB positron"
)

def aqi_color(aqi: float) -> str:
    """Return a color based on EPA AQI breakpoints."""
    if aqi <= 50:
        return "green"
    elif aqi <= 100:
        return "orange"
    elif aqi <= 150:
        return "red"
    else:
        return "darkred"

# Add sensor markers
for _, row in sensors.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=6,
        color=aqi_color(row["aqi"]),
        fill=True,
        fill_opacity=0.7,
        popup=f"<b>{row['sensor_id']}</b><br>AQI: {row['aqi']}",
        tooltip=f"{row['sensor_id']}: AQI {row['aqi']}"
    ).add_to(m)

# Save to HTML
m.save("sensor_map.html")
print("Map saved to sensor_map.html")
```

Open `sensor_map.html` in a browser to see an interactive map with clickable
markers showing sensor IDs and AQI values.

## Step 3: Add H3 Hexagonal Grid Visualization

H3 hexagonal grids aggregate point data into uniform spatial bins. This is
useful for density analysis, heatmaps, and feeding data into Active Inference
models that operate on discrete spatial cells.

```
```python
import h3
import json
from geo_infer_space import latlng_to_cell

# Assign each sensor to an H3 cell at resolution 7
sensors["h3_cell"] = [
    latlng_to_cell(row.geometry.y, row.geometry.x, 7)
    for _, row in sensors.iterrows()
]

# Aggregate AQI by H3 cell (mean value per cell)
cell_aqi = sensors.groupby("h3_cell")["aqi"].agg(["mean", "count"]).reset_index()
cell_aqi.columns = ["h3_cell", "mean_aqi", "sensor_count"]

print(f"Aggregated into {len(cell_aqi)} H3 cells")
print(cell_aqi.head())
```

Now draw the hexagons on the map:

```
```python
import folium

m_hex = folium.Map(
    location=[center_lat, center_lng],
    zoom_start=10,
    tiles="CartoDB positron"
)

# Draw each H3 cell as a polygon
for _, row in cell_aqi.iterrows():
    # h3.cell_to_boundary returns list of (lat, lng) tuples in v4
    boundary = h3.cell_to_boundary(row["h3_cell"])
    # folium expects [[lat, lng], ...] -- boundary is already in that format
    boundary_coords = [[coord[0], coord[1]] for coord in boundary]

    color = aqi_color(row["mean_aqi"])

    folium.Polygon(
        locations=boundary_coords,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.4,
        weight=1,
        popup=(
            f"<b>Cell:</b> {row['h3_cell']}<br>"
            f"<b>Mean AQI:</b> {row['mean_aqi']:.1f}<br>"
            f"<b>Sensors:</b> {row['sensor_count']}"
        ),
    ).add_to(m_hex)

m_hex.save("hex_map.html")
print("H3 hex map saved to hex_map.html")
```

## Step 4: Multi-Layer Map with Layer Control

Combine the point and hex layers into a single map with toggle controls:

```
```python
import folium
from folium.plugins import MarkerCluster

m_combined = folium.Map(
    location=[center_lat, center_lng],
    zoom_start=10,
    tiles="CartoDB positron"
)

# Layer 1: H3 hexagons
hex_layer = folium.FeatureGroup(name="H3 Hexagons")
for _, row in cell_aqi.iterrows():
    boundary = h3.cell_to_boundary(row["h3_cell"])
    boundary_coords = [[c[0], c[1]] for c in boundary]
    color = aqi_color(row["mean_aqi"])
    folium.Polygon(
        locations=boundary_coords,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.35,
        weight=1,
    ).add_to(hex_layer)
hex_layer.add_to(m_combined)

# Layer 2: Individual sensor markers (clustered)
sensor_layer = folium.FeatureGroup(name="Sensors")
cluster = MarkerCluster().add_to(sensor_layer)
for _, row in sensors.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color=aqi_color(row["aqi"]),
        fill=True,
        fill_opacity=0.8,
        popup=f"<b>{row['sensor_id']}</b><br>AQI: {row['aqi']}",
    ).add_to(cluster)
sensor_layer.add_to(m_combined)

# Add layer toggle
folium.LayerControl().add_to(m_combined)

m_combined.save("combined_map.html")
print("Combined map saved to combined_map.html")
```

## Step 5: Static Map with Matplotlib

For reports and publications, you may need a static image rather than an
interactive HTML file.

```
```python
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# Plot sensors colored by AQI
scatter = sensors.plot(
    ax=ax,
    column="aqi",
    cmap="RdYlGn_r",
    legend=True,
    legend_kwds={"label": "Air Quality Index (AQI)", "shrink": 0.6},
    markersize=40,
    edgecolor="black",
    linewidth=0.5,
)

ax.set_title("Bay Area Air Quality Sensors", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_aspect("equal")

plt.tight_layout()
plt.savefig("sensor_map.png", dpi=150, bbox_inches="tight")
print("Static map saved to sensor_map.png")
```

## Step 6: Using the InteractiveVisualizationEngine

GEO-INFER-SPACE includes a higher-level visualization engine for creating
dashboards with multiple data layers. It wraps folium with H3 integration and
multi-layer overlay support:

```
```python
from pathlib import Path
from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine

location_config = {
    "location": {
        "name": "Bay Area",
        "bounds": {
            "north": 37.9,
            "south": 37.3,
            "east": -122.0,
            "west": -122.6
        }
    }
}

engine = InteractiveVisualizationEngine(
    location_config=location_config,
    output_dir=Path("./output/maps"),
    h3_resolution=7
)

# Build analysis results dict for the dashboard
analysis_results = {
    "air_quality": {
        "cells": cell_aqi["h3_cell"].tolist(),
        "values": cell_aqi["mean_aqi"].tolist(),
    }
}

dashboard_path = engine.create_comprehensive_dashboard(analysis_results)
print(f"Dashboard saved to: {dashboard_path}")
```

## Exporting Maps

### HTML (Interactive)

All folium maps save directly to HTML:

```
```python
m.save("output/my_map.html")
```

These are self-contained HTML files with embedded JavaScript. They can be
shared, uploaded to a web server, or embedded in an iframe.

### PNG (Static Image)

Use matplotlib for static exports, as shown in Step 5. For higher resolution:

```
```python
plt.savefig("output/my_map.png", dpi=300, bbox_inches="tight")
```

### GeoJSON (Data Exchange)

Export your GeoDataFrame to GeoJSON for use in other GIS tools (QGIS, ArcGIS,
Mapbox):

```
```python
# Export sensor points
sensors.to_file("output/sensors.geojson", driver="GeoJSON")

# Export H3 cell polygons as GeoJSON
from shapely.geometry import Polygon as ShapelyPolygon

hex_polygons = []
for _, row in cell_aqi.iterrows():
    boundary = h3.cell_to_boundary(row["h3_cell"])
    # boundary is [(lat, lng), ...]; shapely wants (lng, lat)
    ring = [(coord[1], coord[0]) for coord in boundary]
    hex_polygons.append(ShapelyPolygon(ring))

hex_gdf = gpd.GeoDataFrame(
    cell_aqi,
    geometry=hex_polygons,
    crs="EPSG:4326"
)
hex_gdf.to_file("output/hex_cells.geojson", driver="GeoJSON")
print("GeoJSON files exported")
```

### SVG (Vector Graphics)

For publication-quality figures:

```
```python
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
sensors.plot(ax=ax, column="aqi", cmap="RdYlGn_r", markersize=40)
plt.savefig("output/my_map.svg", format="svg", bbox_inches="tight")
```

## Common Pitfalls

**CRS mismatch**: If your points appear in the wrong location, check that all
layers share the same CRS. Use `gdf.to_crs("EPSG:4326")` to reproject before
mapping.

**H3 coordinate order**: H3 v4 functions use `(lat, lng)` order. Shapely and
GeoJSON use `(lng, lat)` / `(x, y)`. Be explicit about which convention you
are following.

**Empty maps**: If your folium map renders but shows no data, verify that your
lat/lng values are in the expected range (latitude: -90 to 90, longitude: -180
to 180) and that the map center is near your data.

## Next Steps

- **[Spatial Analysis Basics](spatial_analysis_basics.md)** -- Deeper coverage of spatial operations and the GEO-INFER-SPACE API.
- **[Active Inference Basics](active_inference_basics.md)** -- Feed your spatial data into Active Inference models.
- **[H3 Geospatial Indexing](../geospatial/data_formats/h3/index.md)** -- Full reference for H3 in GEO-INFER.
- **[Visualization Guide](../geospatial/visualization/index.md)** -- More visualization techniques and tools.
- **[Your First Analysis](first_analysis.md)** -- Run a complete geospatial analysis pipeline.

---

**License**: GEO-INFER is released under the [CC BY-NC-SA 4.0 License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
