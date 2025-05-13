# GEO-INFER Data Dictionary

This data dictionary defines the core data structures, formats, and models used across the GEO-INFER framework. It serves as a reference for developers working with multiple modules and ensures consistency in data representation.

## Core Data Structures

### GeospatialDataset

The fundamental data structure for representing geospatial data across the GEO-INFER framework.

```python
from geo_infer_data.core import GeospatialDataset

# Creating a GeospatialDataset from various sources
dataset = GeospatialDataset.from_geodataframe(gdf)
dataset = GeospatialDataset.from_file("path/to/data.geojson")
dataset = GeospatialDataset.from_raster("path/to/raster.tif")
```

| Property | Type | Description |
|----------|------|-------------|
| `data` | varies | The underlying data container (GeoDataFrame, xarray.Dataset, etc.) |
| `crs` | str or pyproj.CRS | Coordinate reference system |
| `bounds` | tuple | Geographic bounds as (minx, miny, maxx, maxy) |
| `geometry_type` | str | Type of geometries (Point, LineString, Polygon, etc.) |
| `attributes` | dict | Dictionary of dataset attributes |
| `metadata` | dict | Dictionary of metadata information |

| Method | Description |
|--------|-------------|
| `to_geodataframe()` | Convert to GeoDataFrame |
| `to_xarray()` | Convert to xarray Dataset/DataArray |
| `to_raster()` | Convert to raster representation |
| `to_temporal_series()` | Convert to TemporalSeries if time dimension exists |
| `reproject(target_crs)` | Reproject to a new coordinate system |
| `clip(geometry)` | Clip dataset to a geometry |
| `aggregate(by)` | Aggregate by attribute or spatial unit |

### TemporalSeries

Standard representation for time-series data across the framework.

```python
from geo_infer_time.core import TemporalSeries

# Creating a TemporalSeries
series = TemporalSeries.from_dataframe(df, time_column="timestamp")
series = TemporalSeries.from_file("path/to/timeseries.csv")
```

| Property | Type | Description |
|----------|------|-------------|
| `data` | pandas.DataFrame or xarray.Dataset | The underlying data container |
| `time_column` | str | Name of the column containing time information |
| `frequency` | str | Inferred or specified data frequency |
| `start_time` | datetime | Start time of the series |
| `end_time` | datetime | End time of the series |
| `duration` | timedelta | Duration of the time series |
| `metadata` | dict | Dictionary of metadata information |

| Method | Description |
|--------|-------------|
| `to_dataframe()` | Convert to pandas DataFrame |
| `to_xarray()` | Convert to xarray Dataset |
| `resample(freq)` | Resample to a different frequency |
| `slice(start_time, end_time)` | Extract a time slice |
| `split(train_ratio)` | Split into training and validation sets |
| `detect_frequency()` | Detect the time series frequency |
| `to_geospatial_dataset()` | Convert to GeospatialDataset if spatial coordinates exist |

### SpatioTemporalCube

For data with both spatial and temporal dimensions.

```python
from geo_infer_data.core import SpatioTemporalCube

# Creating a SpatioTemporalCube
cube = SpatioTemporalCube.from_xarray(xr_dataset)
cube = SpatioTemporalCube.from_raster_sequence("path/to/rasters/*.tif", time_format="%Y%m%d")
```

| Property | Type | Description |
|----------|------|-------------|
| `data` | xarray.Dataset | The underlying data container |
| `spatial_dims` | list | Names of spatial dimensions |
| `time_dim` | str | Name of time dimension |
| `crs` | str or pyproj.CRS | Coordinate reference system |
| `bounds` | tuple | Geographic bounds as (minx, miny, maxx, maxy) |
| `time_range` | tuple | Time range as (start_time, end_time) |
| `variables` | list | List of data variables |
| `metadata` | dict | Dictionary of metadata information |

| Method | Description |
|--------|-------------|
| `to_xarray()` | Convert to xarray Dataset |
| `to_geodataframes()` | Convert to dictionary of GeoDataFrames by time |
| `to_raster_sequence()` | Export as a sequence of raster files |
| `slice_time(start_time, end_time)` | Extract a time slice |
| `slice_space(bounds)` | Extract a spatial slice |
| `aggregate_time(freq)` | Aggregate along time dimension |
| `aggregate_space(scale)` | Aggregate along spatial dimensions |
| `visualize()` | Generate interactive visualization |

### BeliefDistribution

Probabilistic representation used in active inference components.

```python
from geo_infer_act.core import BeliefDistribution

# Creating a BeliefDistribution
belief = BeliefDistribution(mean=mu, covariance=sigma)
belief = BeliefDistribution.from_samples(samples)
```

| Property | Type | Description |
|----------|------|-------------|
| `mean` | numpy.ndarray | Distribution mean |
| `covariance` | numpy.ndarray | Covariance matrix (for Gaussian) |
| `samples` | numpy.ndarray | Samples from the distribution (for non-parametric) |
| `log_precision` | numpy.ndarray | Log precision (for active inference) |
| `parameters` | dict | Additional distribution parameters |
| `distribution_type` | str | Type of distribution (Gaussian, Categorical, etc.) |

| Method | Description |
|--------|-------------|
| `sample(n_samples)` | Draw samples from the distribution |
| `log_probability(x)` | Compute log probability of x |
| `entropy()` | Calculate distribution entropy |
| `kl_divergence(other)` | Calculate KL divergence with another distribution |
| `update(evidence)` | Update distribution with new evidence |
| `marginalize(dims)` | Marginalize over specified dimensions |
| `to_xarray()` | Convert to xarray Dataset |

### SpatialBeliefMap

Spatial representation of beliefs for active inference on geographic data.

```python
from geo_infer_act.spatial import SpatialBeliefMap

# Creating a SpatialBeliefMap
belief_map = SpatialBeliefMap.from_h3_grid(h3_resolution=8, bbox=bbox)
belief_map = SpatialBeliefMap.from_raster("path/to/belief_raster.tif")
```

| Property | Type | Description |
|----------|------|-------------|
| `beliefs` | dict | Mapping from spatial index to BeliefDistribution |
| `geometry` | GeospatialDataset | Spatial representation of the grid |
| `resolution` | int or float | Spatial resolution |
| `crs` | str or pyproj.CRS | Coordinate reference system |
| `attributes` | list | Names of attributes with beliefs |
| `metadata` | dict | Dictionary of metadata information |

| Method | Description |
|--------|-------------|
| `get_belief(location)` | Get belief at a specific location |
| `update_belief(location, evidence)` | Update belief at a location |
| `to_raster()` | Convert to raster format |
| `to_geodataframe()` | Convert to GeoDataFrame |
| `visualize()` | Generate visualization of belief map |
| `sample()` | Generate a sample realization of the belief map |
| `expected_information_gain(locations)` | Calculate expected information gain for locations |

## Standard File Formats

### Vector Data

| Format | Description | Module Support | Usage |
|--------|-------------|----------------|-------|
| GeoJSON | JSON-based format for geospatial vector data | All spatial modules | Standard interchange format for web |
| GeoPackage | SQLite-based format for vector and raster data | SPACE, DATA, most domains | Preferred for persistent storage |
| Shapefile | Legacy ESRI format for vector data | All spatial modules | Backward compatibility |
| GeoParquet | Columnar format for efficient geospatial data | SPACE, DATA | Big data processing |
| TopoJSON | Topology-preserving extension of GeoJSON | SPACE | Web visualization with shared topology |

### Raster Data

| Format | Description | Module Support | Usage |
|--------|-------------|----------------|-------|
| GeoTIFF | Georeferenced TIFF format | SPACE, DATA, domains | Standard raster storage |
| Cloud Optimized GeoTIFF (COG) | Web-optimized GeoTIFF | SPACE, DATA | Remote access and visualization |
| NetCDF | Self-describing, multidimensional data format | SPACE, TIME, domains | Climate and scientific data |
| Zarr | Chunked, compressed N-D arrays | SPACE, DATA | Cloud-based big data analytics |

### Time Series Data

| Format | Description | Module Support | Usage |
|--------|-------------|----------------|-------|
| CSV with ISO8601 timestamps | Simple tabular format | All temporal modules | Simple time series exchange |
| NetCDF with time dimension | Multidimensional with time axis | TIME, SPACE, domains | Spatiotemporal scientific data |
| Parquet with timestamp column | Columnar storage with timestamps | TIME, DATA | Efficient large time series |
| JSON with temporal schema | Flexible JSON with time elements | TIME, API | Web-based time series exchange |

### Model Data

| Format | Description | Module Support | Usage |
|--------|-------------|----------------|-------|
| HDF5 | Hierarchical Data Format | ACT, BAYES, ML-based domains | Storing trained models |
| JSON Model Configuration | JSON descriptor of model settings | All modeling modules | Model configuration exchange |
| ONNX | Open Neural Network Exchange | ACT, domains with ML | Cross-platform model deployment |
| PMML | Predictive Model Markup Language | BAYES, risk models | Statistical model interchange |

## Data Models

### Geospatial Core Models

#### Coordinate

```python
class Coordinate:
    """A single coordinate point with optional z and m values."""
    x: float  # Longitude or x-coordinate
    y: float  # Latitude or y-coordinate
    z: Optional[float] = None  # Elevation or z-coordinate
    m: Optional[float] = None  # Measure value
    crs: Optional[str] = "EPSG:4326"  # Coordinate reference system
```

#### BoundingBox

```python
class BoundingBox:
    """Geographic bounding box."""
    min_x: float  # Minimum longitude/x
    min_y: float  # Minimum latitude/y
    max_x: float  # Maximum longitude/x
    max_y: float  # Maximum latitude/y
    crs: Optional[str] = "EPSG:4326"  # Coordinate reference system
```

#### SpatialReference

```python
class SpatialReference:
    """Spatial reference system definition."""
    crs: str  # CRS identifier (EPSG code or WKT)
    units: str  # Units of measurement
    projected: bool  # Whether the CRS is projected
    geodetic: bool  # Whether the CRS is geodetic
    authority: str  # Authority (EPSG, ESRI, etc.)
```

#### GeometryCollection

```python
class GeometryCollection:
    """Collection of geometries with attributes."""
    geometries: List[Any]  # List of geometry objects
    attributes: Dict[str, List[Any]]  # Attributes for each geometry
    crs: Optional[str] = "EPSG:4326"  # Coordinate reference system
```

### Temporal Core Models

#### TimeInstant

```python
class TimeInstant:
    """Single point in time with optional timezone."""
    datetime: datetime  # Datetime value
    timezone: Optional[str] = "UTC"  # Timezone
    precision: Optional[str] = "second"  # Time precision
```

#### TimeInterval

```python
class TimeInterval:
    """Time interval between start and end times."""
    start: TimeInstant  # Start time
    end: TimeInstant  # End time
    inclusive_start: bool = True  # Whether start is inclusive
    inclusive_end: bool = False  # Whether end is inclusive
```

#### TemporalReference

```python
class TemporalReference:
    """Temporal reference system definition."""
    calendar: str = "gregorian"  # Calendar system
    time_scale: str = "utc"  # Time scale (UTC, TAI, etc.)
    epoch: Optional[datetime] = None  # Reference epoch
    units: str = "seconds"  # Time units
```

### Active Inference Core Models

#### StateSpace

```python
class StateSpace:
    """Definition of a state space for active inference."""
    dimensions: List[str]  # Names of state dimensions
    bounds: Optional[Dict[str, Tuple[float, float]]]  # Bounds for each dimension
    discrete: bool  # Whether the space is discrete
    cardinality: Optional[Dict[str, int]]  # Cardinality of discrete dimensions
```

#### ObservationModel

```python
class ObservationModel:
    """Mapping from hidden states to observations."""
    state_space: StateSpace  # Definition of state space
    observation_space: StateSpace  # Definition of observation space
    mapping: Callable  # Function mapping states to observations
    parameters: Dict[str, Any]  # Model parameters
```

#### TransitionModel

```python
class TransitionModel:
    """Model of state transitions under actions."""
    state_space: StateSpace  # Definition of state space
    action_space: Optional[StateSpace]  # Definition of action space
    mapping: Callable  # Function mapping state-action to next state
    parameters: Dict[str, Any]  # Model parameters
```

#### Policy

```python
class Policy:
    """Action selection policy."""
    action_space: StateSpace  # Definition of action space
    state_space: StateSpace  # Definition of state space
    mapping: Callable  # Function mapping state to action
    parameters: Dict[str, Any]  # Policy parameters
```

## Domain-Specific Models

### Agricultural Models

#### Field

```python
class Field:
    """Agricultural field with properties."""
    geometry: Any  # Field boundary geometry
    crop_type: str  # Type of crop
    planting_date: Optional[datetime]  # Planting date
    harvest_date: Optional[datetime]  # Harvest date
    attributes: Dict[str, Any]  # Additional field attributes
```

#### CropModel

```python
class CropModel:
    """Model of crop growth and yield."""
    crop_type: str  # Type of crop
    growth_stages: List[str]  # Growth stages
    parameters: Dict[str, Any]  # Model parameters
    prediction_variables: List[str]  # Output variables
```

### Urban Models

#### Building

```python
class Building:
    """Building with properties."""
    geometry: Any  # Building footprint geometry
    height: Optional[float]  # Building height
    stories: Optional[int]  # Number of stories
    building_type: str  # Building type
    attributes: Dict[str, Any]  # Additional building attributes
```

#### TransportationNetwork

```python
class TransportationNetwork:
    """Transportation network with properties."""
    edges: GeometryCollection  # Network edges
    nodes: GeometryCollection  # Network nodes
    network_type: str  # Type of network (road, rail, etc.)
    directed: bool  # Whether the network is directed
    attributes: Dict[str, Any]  # Additional network attributes
```

### Risk Models

#### Hazard

```python
class Hazard:
    """Natural or anthropogenic hazard."""
    hazard_type: str  # Type of hazard
    intensity: Dict[str, Any]  # Intensity measures
    probability: float  # Probability of occurrence
    time_frame: TimeInterval  # Time frame for the hazard
    geometry: Any  # Spatial extent
```

#### Vulnerability

```python
class Vulnerability:
    """Vulnerability assessment."""
    asset_type: str  # Type of vulnerable asset
    hazard_type: str  # Type of hazard
    fragility_curves: Dict[str, Any]  # Fragility curves
    exposure_value: float  # Value of exposed assets
    geometry: Any  # Spatial extent
```

## Standard Metadata

### Dataset Metadata

```python
class DatasetMetadata:
    """Standard metadata for geospatial datasets."""
    title: str  # Dataset title
    description: str  # Dataset description
    keywords: List[str]  # Keywords for discovery
    created: datetime  # Creation date
    updated: datetime  # Last update date
    creator: str  # Creator name or organization
    license: str  # License information
    spatial_coverage: BoundingBox  # Spatial coverage
    temporal_coverage: Optional[TimeInterval]  # Temporal coverage
    crs: str  # Coordinate reference system
    format: str  # Data format
    source: str  # Data source
    lineage: Optional[Dict[str, Any]]  # Processing history
    quality: Optional[Dict[str, Any]]  # Quality information
```

### Model Metadata

```python
class ModelMetadata:
    """Standard metadata for models."""
    name: str  # Model name
    version: str  # Model version
    description: str  # Model description
    author: str  # Model author
    created: datetime  # Creation date
    parameters: Dict[str, Any]  # Model parameters
    dependencies: Dict[str, str]  # Software dependencies
    inputs: Dict[str, Dict[str, str]]  # Input specifications
    outputs: Dict[str, Dict[str, str]]  # Output specifications
    performance_metrics: Optional[Dict[str, float]]  # Performance metrics
    training_data: Optional[str]  # Reference to training data
    license: str  # License information
```

## Data Encoding Standards

### Coordinate Encoding

- **Geographic coordinates**: [latitude, longitude] ordering in arrays and documentation
- **Projected coordinates**: [easting, northing] ordering
- **H3 indexes**: String representation of H3 cell address
- **What3Words**: Three-word encoding for locations

### Time Encoding

- **Timestamps**: ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)
- **Time intervals**: ISO 8601 interval format (start/end)
- **Durations**: ISO 8601 duration format (PnYnMnDTnHnMnS)
- **Recurring times**: iCalendar RRULE format

### Uncertainty Encoding

- **Distributional parameters**: Mean and covariance for Gaussian
- **Quantiles**: 0.025, 0.25, 0.5, 0.75, 0.975 quantiles
- **Ensemble members**: Array of realizations
- **Fuzzy membership**: Membership grades between 0 and 1

## API Data Formats

### GeoJSON Feature Collection

Standard format for vector data exchange via API:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-122.4194, 37.7749]
      },
      "properties": {
        "name": "San Francisco",
        "population": 884363,
        "area_km2": 121.4
      }
    }
  ],
  "bbox": [-122.5, 37.7, -122.3, 37.8],
  "crs": {
    "type": "name",
    "properties": {
      "name": "EPSG:4326"
    }
  },
  "metadata": {
    "title": "Example Dataset",
    "created": "2023-01-01T00:00:00Z"
  }
}
```

### SpatioTemporal Grid Response

Format for gridded spatiotemporal data:

```json
{
  "type": "SpatioTemporalGrid",
  "dimensions": {
    "x": {
      "values": [-122.5, -122.4, -122.3],
      "units": "degrees_east"
    },
    "y": {
      "values": [37.7, 37.8, 37.9],
      "units": "degrees_north"
    },
    "time": {
      "values": ["2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"],
      "units": "ISO8601"
    }
  },
  "variables": {
    "temperature": {
      "dimensions": ["time", "y", "x"],
      "units": "celsius",
      "data": [[[15.2, 15.5, 15.7], [15.0, 15.3, 15.5], [14.8, 15.1, 15.3]],
               [[16.2, 16.5, 16.7], [16.0, 16.3, 16.5], [15.8, 16.1, 16.3]]]
    }
  },
  "crs": "EPSG:4326",
  "metadata": {
    "title": "Temperature Grid",
    "created": "2023-01-01T00:00:00Z"
  }
}
```

### Inference Result

Format for active inference prediction results:

```json
{
  "type": "InferenceResult",
  "predictions": [
    {
      "location": {"type": "Point", "coordinates": [-122.4194, 37.7749]},
      "time": "2023-01-01T00:00:00Z",
      "variables": {
        "temperature": {
          "mean": 15.5,
          "std": 0.8,
          "quantiles": {
            "0.025": 13.9,
            "0.5": 15.5,
            "0.975": 17.1
          }
        }
      }
    }
  ],
  "model": {
    "name": "TemperatureModel",
    "version": "1.0.0"
  },
  "metadata": {
    "created": "2023-01-01T00:00:00Z",
    "input_data": "temperature_observations_2022.nc"
  }
}
```

## Best Practices

1. **Coordinate Consistency**: Always specify the coordinate reference system (CRS) when creating or sharing geospatial data.

2. **Temporal Precision**: Use appropriate temporal precision for your use case (second, minute, day) and always specify the timezone or use UTC.

3. **Units Documentation**: Always include units of measurement in dataset attributes and documentation.

4. **Uncertainty Representation**: Include uncertainty information with predictions and measurements whenever possible.

5. **Metadata Completeness**: Provide complete metadata including provenance, quality information, and lineage.

6. **Schema Validation**: Validate data against schemas before processing or storing.

7. **Naming Conventions**: Use consistent naming conventions for variables, dimensions, and attributes across modules.

8. **Dimensionality**: For raster and gridded data, use the convention [time, y, x] for dimension ordering.

9. **Efficiency**: For large datasets, use appropriate formats (GeoParquet, Zarr, COG) and chunking strategies.

10. **Standards Compliance**: Follow OGC standards for geospatial data interchange when possible.

## Related Documentation

- [GEO-INFER-SPACE Data Models](../space/data_models.md)
- [GEO-INFER-TIME Data Models](../time/data_models.md)
- [GEO-INFER-ACT Data Models](../act/data_models.md)
- [GEO-INFER-API Data Exchange Formats](../api/data_formats.md)
- [Data Model Validation Guide](../data/validation.md) 