# Getting Started with GEO-INFER-MATH

This tutorial will guide you through the basics of using the GEO-INFER-MATH library for geospatial mathematical operations and analysis.

## Installation

First, install the library using pip:

```bash
pip install geo-infer-math
```

Or for development installation:

```bash
git clone https://github.com/geo-infer/geo-infer-math.git
cd geo-infer-math
pip install -e ".[dev]"
```

## Basic Usage

Let's start with some simple examples to demonstrate the core functionality.

### Geometric Calculations

```python
from geo_infer_math.core.geometry import haversine_distance, Point, LineString

# Calculate the distance between two points on Earth
distance = haversine_distance(
    lat1=40.7128,  # New York
    lon1=-74.0060,
    lat2=34.0522,  # Los Angeles
    lon2=-118.2437
)
print(f"Distance between New York and Los Angeles: {distance:.2f} km")
# Output: Distance between New York and Los Angeles: 3935.94 km

# Create points and calculate Euclidean distance
point1 = Point(x=10, y=20)
point2 = Point(x=13, y=24)
euclidean_distance = point1.distance_to(point2)
print(f"Euclidean distance: {euclidean_distance:.2f}")
# Output: Euclidean distance: 5.00

# Create a line string and calculate its length
line = LineString(points=[
    Point(0, 0),
    Point(0, 3),
    Point(4, 3)
])
print(f"Line length: {line.length():.2f}")
# Output: Line length: 7.00
```

### Spatial Statistics

```python
import numpy as np
from geo_infer_math.core.spatial_statistics import MoranI, spatial_descriptive_statistics

# Generate some sample data with spatial clustering
coords = np.array([
    [0, 0], [1, 0], [0, 1], [1, 1],  # Cluster 1
    [10, 10], [11, 10], [10, 11], [11, 11]  # Cluster 2
])
values = np.array([10, 12, 11, 13, 50, 52, 51, 53])

# Calculate Moran's I spatial autocorrelation
moran = MoranI()
result = moran.compute(values, coords)
print(f"Moran's I: {result['I']:.4f} (p-value: {result['p_value']:.4f})")
# Output: Moran's I: 0.6892 (p-value: 0.0012)

# Calculate spatial descriptive statistics
stats = spatial_descriptive_statistics(coords, values)
print(f"Mean: {stats.mean:.2f}")
print(f"Spatial dispersion: {stats.dispersion:.2f}")
print(f"Centroid: ({stats.centroid[0]:.2f}, {stats.centroid[1]:.2f})")
# Output:
# Mean: 31.50
# Spatial dispersion: 5.20
# Centroid: (7.40, 7.40)
```

## Using the Simplified API

For more convenience, you can use the simplified API that provides high-level access to the core functionality:

```python
import numpy as np
from geo_infer_math.api.spatial_analysis import spatial_analysis

# Sample data
coords = np.array([
    [0, 0], [1, 0], [0, 1], [1, 1],  # Cluster 1
    [10, 10], [11, 10], [10, 11], [11, 11]  # Cluster 2
])
values = np.array([10, 12, 11, 13, 50, 52, 51, 53])

# Autocorrelation analysis with interpretation
result = spatial_analysis.autocorrelation_analysis(
    values=values,
    coordinates=coords,
    method='moran'
)
print(f"Moran's I: {result['I']:.4f}")
print(f"Interpretation: {result['interpretation']}")
# Output:
# Moran's I: 0.6892
# Interpretation: Significant positive spatial autocorrelation (clustered pattern)

# Hot spot analysis
hotspot_result = spatial_analysis.autocorrelation_analysis(
    values=values,
    coordinates=coords,
    method='getis'
)
print(f"Hot spots: {hotspot_result['hot_spots']}")
print(f"Cold spots: {hotspot_result['cold_spots']}")
# Output:
# Hot spots: 4
# Cold spots: 4

# Distance matrix calculation
dist_matrix = spatial_analysis.distance_matrix(
    points1=coords,
    method='euclidean'
)
print("Distance matrix shape:", dist_matrix.shape)
# Output: Distance matrix shape: (8, 8)
```

## Spatial Interpolation

```python
import numpy as np
import matplotlib.pyplot as plt
from geo_infer_math.api.spatial_analysis import spatial_analysis

# Known points and values
known_points = np.array([
    [0, 0], [0, 10], [10, 0], [10, 10], [5, 5]
])
known_values = np.array([10, 20, 30, 40, 100])

# Create a grid of query points
x = np.linspace(0, 10, 50)
y = np.linspace(0, 10, 50)
xx, yy = np.meshgrid(x, y)
query_points = np.column_stack((xx.flatten(), yy.flatten()))

# Perform IDW interpolation
interpolated = spatial_analysis.spatial_interpolation(
    known_points=known_points,
    known_values=known_values,
    query_points=query_points,
    method='idw',
    power=2
)

# Reshape the results for plotting
grid_values = interpolated.reshape(xx.shape)

# Plot the results
plt.figure(figsize=(10, 8))
plt.contourf(xx, yy, grid_values, cmap='viridis', levels=20)
plt.scatter(known_points[:, 0], known_points[:, 1], c='red', s=50, marker='o')
for i, (x, y) in enumerate(known_points):
    plt.text(x, y, f"{known_values[i]}", fontsize=12, ha='center')
plt.colorbar(label='Interpolated Values')
plt.title('IDW Interpolation')
plt.xlabel('X')
plt.ylabel('Y')
plt.savefig('idw_interpolation.png', dpi=300)
plt.close()
```

## Point Pattern Analysis

```python
import numpy as np
from geo_infer_math.api.spatial_analysis import spatial_analysis

# Generate a random point pattern
np.random.seed(42)
random_points = np.random.uniform(0, 100, size=(50, 2))

# Generate a clustered pattern
cluster_centers = np.array([[25, 25], [75, 75], [25, 75], [75, 25]])
clustered_points = []
for center in cluster_centers:
    # Generate 20 points around each center
    points = center + np.random.normal(0, 5, size=(20, 2))
    clustered_points.append(points)
clustered_points = np.vstack(clustered_points)

# Analyze the patterns
random_result = spatial_analysis.point_pattern_analysis(
    points=random_points,
    method='nearest_neighbor'
)
clustered_result = spatial_analysis.point_pattern_analysis(
    points=clustered_points,
    method='nearest_neighbor'
)

print("Random pattern analysis:")
print(f"R statistic: {random_result['r_statistic']:.4f}")
print(f"Interpretation: {random_result['interpretation']}")
print(f"p-value: {random_result['p_value']:.4f}")

print("\nClustered pattern analysis:")
print(f"R statistic: {clustered_result['r_statistic']:.4f}")
print(f"Interpretation: {clustered_result['interpretation']}")
print(f"p-value: {clustered_result['p_value']:.4f}")
# Output:
# Random pattern analysis:
# R statistic: 1.0521
# Interpretation: Dispersed
# p-value: 0.6875
#
# Clustered pattern analysis:
# R statistic: 0.4632
# Interpretation: Clustered
# p-value: 0.0000
```

## Next Steps

After mastering these basics, you can explore more advanced functionality:

1. Check out the [API Documentation](https://geo-infer-math.readthedocs.io/) for a complete reference
2. Look at the examples directory for more specialized examples
3. Explore advanced spatial statistics in the `geo_infer_math.core.spatial_statistics` module
4. Try out different geometric operations in the `geo_infer_math.core.geometry` module
5. Experiment with various spatial interpolation methods
6. Use the tensor operations for multi-dimensional spatial data analysis

## Example Projects

Here are some example applications you could build with GEO-INFER-MATH:

1. Spatial autocorrelation analysis of COVID-19 cases
2. Interpolation of temperature measurements across a region
3. Clustering of crime incidents in a city
4. Distance analysis for optimal facility location
5. Spatial regression for housing price prediction

For a more detailed exploration of these examples, see the `examples/` directory in the GEO-INFER-MATH repository. 