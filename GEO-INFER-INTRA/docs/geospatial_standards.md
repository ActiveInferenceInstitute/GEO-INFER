# GEO-INFER Geospatial Standards and Best Practices

This guide defines standards and best practices for geospatial data handling and processing across all GEO-INFER modules.

## Coordinate Systems

### Standard Coordinate Reference Systems

GEO-INFER modules should support the following coordinate reference systems by default:

| CRS Name | EPSG Code | Description | Use Case |
|----------|-----------|-------------|----------|
| WGS 84   | EPSG:4326 | World Geodetic System 1984 | Global geographic coordinates, latitude/longitude in degrees |
| Web Mercator | EPSG:3857 | Web Mercator projection | Web mapping and visualization |
| UTM Zones | EPSG:32601-32660 (North)<br>EPSG:32701-32760 (South) | Universal Transverse Mercator | Regional analysis requiring preserved distances |

### Coordinate Ordering

- Use `[latitude, longitude]` ordering consistently in:
  - Function parameters
  - Return values
  - Documentation
  - Variable names

Example:
```python
def calculate_distance(lat1, lon1, lat2, lon2):
    # Implementation
```

### Coordinate Validation

All functions accepting geographic coordinates should:

1. **Validate bounds**:
   - Latitude: -90.0 to 90.0 degrees
   - Longitude: -180.0 to 180.0 degrees

2. **Handle edge cases**:
   - Antimeridian (International Date Line) crossing
   - Polar regions
   - Equatorial regions

Example validation:
```python
def validate_coordinates(lat, lon):
    """Validate geographic coordinates.
    
    Args:
        lat: Latitude in degrees (-90 to 90)
        lon: Longitude in degrees (-180 to 180)
        
    Raises:
        ValueError: If coordinates are outside valid ranges
    """
    if not -90 <= lat <= 90:
        raise ValueError(f"Latitude {lat} outside valid range (-90 to 90)")
    if not -180 <= lon <= 180:
        raise ValueError(f"Longitude {lon} outside valid range (-180 to 180)")
```

## Spatial Data Formats

### Vector Data

Supported vector formats in order of preference:

1. **GeoJSON**
   - Standard format for web applications
   - Use for APIs and data exchange

2. **GeoPackage**
   - Preferred for storing multiple layers
   - Better for larger datasets than GeoJSON

3. **Shapefile**
   - Support for legacy compatibility
   - Not recommended for new data storage

4. **Well-Known Text (WKT)**
   - Use for simple geometry representation
   - Appropriate for database storage

### Raster Data

Supported raster formats in order of preference:

1. **Cloud Optimized GeoTIFF (COG)**
   - Preferred for web-accessible raster data
   - Support HTTP range requests

2. **GeoTIFF**
   - Standard format for georeferenced raster data
   - Use internal tiling for large datasets

3. **NetCDF**
   - Preferred for multi-dimensional data
   - Use for climate/weather data

### Format Conversion

Provide utility functions for common format conversions:

```python
# Vector format conversions
geojson_to_gpkg(geojson_path, gpkg_path)
shapefile_to_geojson(shp_path, geojson_path)

# Raster format conversions
geotiff_to_cog(tiff_path, cog_path)
netcdf_to_geotiff(nc_path, tiff_path)
```

## Spatial Indexing

### H3 Hexagonal Grid

The H3 hierarchical hexagonal grid is the preferred indexing system for:
- Global analytics
- Equal-area spatial binning
- Multi-resolution analysis

Guidelines:
- Use even resolution numbers (e.g., 6, 8, 10) for visualization
- Document resolution-appropriate use cases:
  - Resolution 6: ~36.1 km² per cell (regional analysis)
  - Resolution 8: ~0.7 km² per cell (urban/neighborhood analysis)
  - Resolution 10: ~0.01 km² per cell (building-level analysis)

Implementation:
```python
import h3

def create_h3_index(lat, lon, resolution=9):
    """Create H3 index for a point.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        resolution: H3 resolution (0-15)
        
    Returns:
        H3 index string
    """
    return h3.latlng_to_cell(lat, lon, resolution)
```

### Other Spatial Indexes

Support for alternative spatial indexing methods:

1. **QuadTree**
   - Use for rectangular query regions
   - Appropriate for map tiling

2. **R-Tree**
   - Use for efficient spatial queries
   - Appropriate for point and polygon data

3. **S2 Cells**
   - Alternative to H3 for some use cases
   - Better for hierarchical queries

## Geospatial Operations

### Distance Calculations

For distance calculations on geographic coordinates:

1. **Haversine formula**: For quick approximations
2. **Vincenty's formula**: For more accurate calculations
3. **GeoDjango distance**: For database queries

Example:
```python
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points.
    
    Args:
        lat1, lon1: Coordinates of first point in degrees
        lat2, lon2: Coordinates of second point in degrees
        
    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth radius in kilometers
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
```

### Area Calculations

Guidelines for accurate area calculations:

1. Use equal-area projections for area calculations
2. Document distortions for different regions
3. Provide uncertainty estimates for large areas

### Topology Operations

For vector geometry operations:
1. Validate topology before operations
2. Properly handle multi-part geometries
3. Consider simplification for complex geometries

## Spatial-Temporal Analysis

### Time Series Data

For time series analysis of spatial data:

1. **Standardized time format**: ISO8601 (YYYY-MM-DDTHH:MM:SSZ)
2. **Time zone handling**: Always store in UTC, convert for display
3. **Temporal resolution**: Document appropriate time intervals

Example:
```python
import pandas as pd

def extract_time_series(geometry, start_date, end_date, resolution="1D"):
    """Extract time series data for a geometry.
    
    Args:
        geometry: GeoJSON geometry
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        resolution: Temporal resolution (e.g., "1D", "1H")
        
    Returns:
        DataFrame with time series data
    """
    # Implementation
```

### Spatial Aggregation

Guidelines for aggregating spatial data:

1. Document aggregation method (mean, sum, etc.)
2. Account for area differences in aggregation
3. Provide uncertainty metrics

## Data Visualization

### Map Visualization Standards

For geospatial visualization:

1. **Projections**:
   - Web Mercator (EPSG:3857) for web maps
   - Equal-area projections for thematic maps
   - Document projection limitations

2. **Color Schemes**:
   - Use colorblind-friendly palettes
   - Follow consistent color semantics
   - Document color scale meaning

3. **Scale and Legend**:
   - Always include scale bar
   - Include north arrow when appropriate
   - Provide clear legend for thematic data

Example:
```python
import matplotlib.pyplot as plt
import geopandas as gpd

def create_choropleth(gdf, value_column, title, cmap="viridis"):
    """Create a choropleth map.
    
    Args:
        gdf: GeoDataFrame with geometries
        value_column: Column name for values to map
        title: Map title
        cmap: Colormap name
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    gdf.plot(column=value_column, cmap=cmap, legend=True, ax=ax)
    
    # Add scale bar and north arrow
    # ...
    
    ax.set_title(title)
    return fig
```

## Performance Considerations

### Large Dataset Handling

For operations on large geospatial datasets:

1. **Chunking**: Process data in manageable chunks
2. **Progressive loading**: Load data at appropriate resolution
3. **Spatial filtering**: Filter data spatially before processing

Example:
```python
def process_large_raster(raster_path, chunk_size=(1024, 1024)):
    """Process a large raster dataset in chunks.
    
    Args:
        raster_path: Path to raster file
        chunk_size: Size of chunks to process
        
    Returns:
        Processed data
    """
    # Implementation using chunked reading
```

### Spatial Indexing Optimization

For efficient spatial queries:

1. Use appropriate spatial index for the query pattern
2. Document indexing overhead for different datasets
3. Consider in-memory vs. on-disk indexes based on data size

## Interoperability Standards

### OGC Compliance

Support for Open Geospatial Consortium standards:

1. **WMS/WMTS**: For map layer services
2. **WFS**: For feature services
3. **WCS**: For coverage services
4. **CSW**: For catalog services

### STAC Integration

Support for SpatioTemporal Asset Catalog:

1. Follow STAC metadata standards
2. Provide STAC API compatibility
3. Document STAC extensions used

### Metadata Standards

Implement standard metadata:

1. **ISO 19115**: Geospatial metadata standard
2. **FGDC**: Federal Geographic Data Committee standard
3. **Dublin Core**: For general metadata

## Testing and Validation

### Geospatial Test Data

Guidelines for geospatial testing:

1. Provide sample datasets covering edge cases:
   - Polar regions
   - Antimeridian crossing
   - Different projections
   - Various scales

2. Mock geospatial services for testing

3. Include visual verification tests for map outputs

### Coordinate System Testing

Test with multiple coordinate systems:

```python
def test_coordinate_conversion():
    """Test coordinate conversion between CRSs."""
    # Test WGS84 to Web Mercator
    lon, lat = -74.0060, 40.7128  # NYC
    x, y = convert_coords(lon, lat, "EPSG:4326", "EPSG:3857")
    
    # Assert approximate equality
    assert abs(x - -8242786.4) < 0.1
    assert abs(y - 4970241.3) < 0.1
```

## Integration with GEO-INFER Modules

Guidelines for geospatial functionality across modules:

1. **GEO-INFER-SPACE**: Primary module for core geospatial operations
2. **GEO-INFER-TIME**: Handles temporal aspects of geospatial data
3. **GEO-INFER-DATA**: Manages geospatial data storage and retrieval
4. **GEO-INFER-API**: Provides standardized geospatial API endpoints

Example integration pattern:
```python
from geo_infer_space import coordinates
from geo_infer_time import temporal
from geo_infer_data import storage

def analyze_spatiotemporal_data(location, time_range):
    """Analyze data for a location and time range.
    
    Args:
        location: Geographic coordinates (lat, lon)
        time_range: Time range (start, end) in ISO format
        
    Returns:
        Analysis results
    """
    # Validate coordinates
    coordinates.validate_coordinates(*location)
    
    # Validate time range
    time_period = temporal.create_time_period(*time_range)
    
    # Fetch data
    data = storage.get_data(location, time_period)
    
    # Process and return results
    # ...
```

## Resources

### Recommended Libraries

- **GeoPandas**: For vector data operations
- **Rasterio**: For raster data operations
- **Shapely**: For geometric operations
- **PyProj**: For coordinate system operations
- **Folium/Leaflet**: For interactive web maps
- **H3-Py**: For H3 hexagonal grid indexing

### Geospatial Data Sources

- [Natural Earth](https://www.naturalearthdata.com/): Vector and raster data
- [OpenStreetMap](https://www.openstreetmap.org/): Street and POI data
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/): Satellite imagery
- [NASA Earth Data](https://earthdata.nasa.gov/): Climate and earth observation

### Standards Organizations

- [Open Geospatial Consortium (OGC)](https://www.ogc.org/)
- [International Organization for Standardization (ISO)](https://www.iso.org/)
- [Federal Geographic Data Committee (FGDC)](https://www.fgdc.gov/)

## License

This guide is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. 