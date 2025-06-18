# H3 Dataset Integration Guide

## 🎯 Overview

This guide provides practical patterns and examples for integrating various types of datasets with H3 hexagonal spatial indexing systems within GEO-INFER-SPACE. It covers everything from simple point datasets to complex spatiotemporal collections, with detailed implementation examples and best practices.

## 📊 Dataset Types and Integration Patterns

### 1. Point Datasets

#### Basic Point Data Integration
```python
import h3
import pandas as pd
from typing import List, Dict, Any

class PointDatasetH3Integrator:
    """Integrate point datasets with H3 system"""
    
    def __init__(self, default_resolution: int = 8):
        self.default_resolution = default_resolution
    
    async def integrate_point_dataset(self, 
                                    points_df: pd.DataFrame,
                                    lat_col: str = 'latitude',
                                    lng_col: str = 'longitude',
                                    properties_cols: List[str] = None,
                                    resolution: int = None) -> Dict[str, Any]:
        """Integrate point dataset into H3 grid system"""
        
        resolution = resolution or self.default_resolution
        properties_cols = properties_cols or []
        
        # Convert points to H3 cells
        h3_cells = {}
        
        for idx, row in points_df.iterrows():
            lat, lng = row[lat_col], row[lng_col]
            h3_cell = h3.latlng_to_cell(lat, lng, resolution)
            
            if h3_cell not in h3_cells:
                h3_cells[h3_cell] = {
                    'h3_cell': h3_cell,
                    'resolution': resolution,
                    'center': h3.cell_to_latlng(h3_cell),
                    'boundary': h3.cell_to_boundary(h3_cell),
                    'points': [],
                    'properties': {}
                }
            
            # Add point to cell
            point_data = {'lat': lat, 'lng': lng}
            for col in properties_cols:
                point_data[col] = row[col]
            
            h3_cells[h3_cell]['points'].append(point_data)
        
        # Aggregate properties
        for cell_data in h3_cells.values():
            cell_data['properties'] = self._aggregate_point_properties(
                cell_data['points'], properties_cols
            )
            cell_data['point_count'] = len(cell_data['points'])
        
        return {
            'dataset_type': 'point',
            'resolution': resolution,
            'total_points': len(points_df),
            'total_cells': len(h3_cells),
            'cells': list(h3_cells.values())
        }
    
    def _aggregate_point_properties(self, 
                                   points: List[Dict[str, Any]], 
                                   properties_cols: List[str]) -> Dict[str, Any]:
        """Aggregate point properties for H3 cell"""
        
        if not points or not properties_cols:
            return {}
        
        aggregated = {}
        
        for col in properties_cols:
            values = [p.get(col) for p in points if p.get(col) is not None]
            
            if not values:
                continue
            
            # Determine aggregation method based on data type
            if isinstance(values[0], (int, float)):
                aggregated[f'{col}_mean'] = sum(values) / len(values)
                aggregated[f'{col}_sum'] = sum(values)
                aggregated[f'{col}_min'] = min(values)
                aggregated[f'{col}_max'] = max(values)
                aggregated[f'{col}_count'] = len(values)
            else:
                # For categorical data
                aggregated[f'{col}_mode'] = max(set(values), key=values.count)
                aggregated[f'{col}_unique_count'] = len(set(values))
        
        return aggregated

# Example usage
async def integrate_weather_stations():
    """Example: Integrate weather station data"""
    
    # Sample weather station data
    weather_data = pd.DataFrame({
        'station_id': ['WS001', 'WS002', 'WS003'],
        'latitude': [40.7128, 40.7589, 40.6782],
        'longitude': [-74.0060, -73.9851, -73.9442],
        'temperature': [22.5, 21.8, 23.1],
        'humidity': [65, 70, 60],
        'wind_speed': [12.5, 8.2, 15.3]
    })
    
    integrator = PointDatasetH3Integrator(default_resolution=9)
    
    result = await integrator.integrate_point_dataset(
        points_df=weather_data,
        properties_cols=['temperature', 'humidity', 'wind_speed']
    )
    
    print(f"Integrated {result['total_points']} weather stations into {result['total_cells']} H3 cells")
    return result
```

### 2. Polygon Datasets

#### Polygon Data Integration
```python
import geopandas as gpd
from shapely.geometry import Point, Polygon

class PolygonDatasetH3Integrator:
    """Integrate polygon datasets with H3 system"""
    
    def __init__(self, default_resolution: int = 8):
        self.default_resolution = default_resolution
    
    async def integrate_polygon_dataset(self,
                                      polygons_gdf: gpd.GeoDataFrame,
                                      resolution: int = None,
                                      coverage_threshold: float = 0.5) -> Dict[str, Any]:
        """Integrate polygon dataset into H3 grid system"""
        
        resolution = resolution or self.default_resolution
        h3_cells = {}
        
        for idx, row in polygons_gdf.iterrows():
            polygon = row.geometry
            
            # Get H3 cells that cover the polygon
            covering_cells = self._get_covering_h3_cells(polygon, resolution, coverage_threshold)
            
            for h3_cell in covering_cells:
                if h3_cell not in h3_cells:
                    h3_cells[h3_cell] = {
                        'h3_cell': h3_cell,
                        'resolution': resolution,
                        'center': h3.cell_to_latlng(h3_cell),
                        'boundary': h3.cell_to_boundary(h3_cell),
                        'covering_polygons': [],
                        'properties': {}
                    }
                
                # Add polygon properties
                polygon_data = {
                    'polygon_id': idx,
                    'coverage_ratio': self._calculate_coverage_ratio(polygon, h3_cell)
                }
                
                # Add all non-geometry columns as properties
                for col in polygons_gdf.columns:
                    if col != 'geometry':
                        polygon_data[col] = row[col]
                
                h3_cells[h3_cell]['covering_polygons'].append(polygon_data)
        
        # Aggregate polygon properties
        for cell_data in h3_cells.values():
            cell_data['properties'] = self._aggregate_polygon_properties(
                cell_data['covering_polygons']
            )
            cell_data['polygon_count'] = len(cell_data['covering_polygons'])
        
        return {
            'dataset_type': 'polygon',
            'resolution': resolution,
            'total_polygons': len(polygons_gdf),
            'total_cells': len(h3_cells),
            'cells': list(h3_cells.values())
        }
    
    def _get_covering_h3_cells(self, 
                              polygon: Polygon, 
                              resolution: int,
                              coverage_threshold: float) -> List[str]:
        """Get H3 cells that cover a polygon"""
        
        # Get bounding box
        minx, miny, maxx, maxy = polygon.bounds
        
        # Create grid of test points
        test_points = []
        step = 0.001  # Adjust based on resolution
        
        x = minx
        while x <= maxx:
            y = miny
            while y <= maxy:
                point = Point(x, y)
                if polygon.contains(point) or polygon.intersects(point):
                    test_points.append((y, x))  # lat, lng
                y += step
            x += step
        
        # Convert points to H3 cells
        h3_cells = set()
        for lat, lng in test_points:
            h3_cell = h3.latlng_to_cell(lat, lng, resolution)
            h3_cells.add(h3_cell)
        
        return list(h3_cells)
    
    def _calculate_coverage_ratio(self, polygon: Polygon, h3_cell: str) -> float:
        """Calculate how much of the H3 cell is covered by the polygon"""
        
        # Get H3 cell boundary as polygon
        cell_boundary = h3.cell_to_boundary(h3_cell)
        cell_polygon = Polygon([(lng, lat) for lat, lng in cell_boundary])
        
        # Calculate intersection
        try:
            intersection = polygon.intersection(cell_polygon)
            coverage_ratio = intersection.area / cell_polygon.area
            return min(coverage_ratio, 1.0)
        except:
            return 0.0
    
    def _aggregate_polygon_properties(self, polygons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate polygon properties for H3 cell"""
        
        if not polygons:
            return {}
        
        aggregated = {}
        
        # Weight by coverage ratio
        total_coverage = sum(p['coverage_ratio'] for p in polygons)
        
        # Get all property keys (excluding special keys)
        property_keys = set()
        for polygon in polygons:
            property_keys.update(k for k in polygon.keys() 
                               if k not in ['polygon_id', 'coverage_ratio'])
        
        for key in property_keys:
            values = []
            weights = []
            
            for polygon in polygons:
                if key in polygon and polygon[key] is not None:
                    values.append(polygon[key])
                    weights.append(polygon['coverage_ratio'])
            
            if not values:
                continue
            
            if isinstance(values[0], (int, float)):
                # Weighted average for numeric values
                weighted_sum = sum(v * w for v, w in zip(values, weights))
                weight_sum = sum(weights)
                aggregated[f'{key}_weighted_avg'] = weighted_sum / weight_sum if weight_sum > 0 else 0
                aggregated[f'{key}_sum'] = sum(values)
            else:
                # Most common value for categorical data
                aggregated[f'{key}_mode'] = max(set(values), key=values.count)
        
        aggregated['total_coverage'] = total_coverage
        
        return aggregated

# Example usage
async def integrate_administrative_boundaries():
    """Example: Integrate administrative boundary data"""
    
    # Load administrative boundaries (example with mock data)
    admin_data = gpd.GeoDataFrame({
        'admin_id': ['ADMIN001', 'ADMIN002'],
        'name': ['District A', 'District B'],
        'population': [50000, 75000],
        'area_km2': [25.5, 32.1],
        'geometry': [
            Polygon([(-74.1, 40.7), (-74.0, 40.7), (-74.0, 40.8), (-74.1, 40.8)]),
            Polygon([(-73.9, 40.6), (-73.8, 40.6), (-73.8, 40.7), (-73.9, 40.7)])
        ]
    })
    
    integrator = PolygonDatasetH3Integrator(default_resolution=8)
    
    result = await integrator.integrate_polygon_dataset(
        polygons_gdf=admin_data,
        coverage_threshold=0.3
    )
    
    print(f"Integrated {result['total_polygons']} administrative areas into {result['total_cells']} H3 cells")
    return result
```

### 3. Raster Datasets

#### Raster Data Integration
```python
import rasterio
import numpy as np
from rasterio.features import rasterize
from rasterio.transform import from_bounds

class RasterDatasetH3Integrator:
    """Integrate raster datasets with H3 system"""
    
    def __init__(self, default_resolution: int = 8):
        self.default_resolution = default_resolution
    
    async def integrate_raster_dataset(self,
                                     raster_path: str,
                                     resolution: int = None,
                                     sampling_method: str = 'bilinear',
                                     nodata_threshold: float = 0.8) -> Dict[str, Any]:
        """Integrate raster dataset into H3 grid system"""
        
        resolution = resolution or self.default_resolution
        
        with rasterio.open(raster_path) as src:
            # Get raster bounds
            bounds = src.bounds
            
            # Generate H3 cells covering the raster
            covering_cells = self._get_covering_cells_for_bounds(bounds, resolution)
            
            h3_cells = {}
            
            for h3_cell in covering_cells:
                # Get cell center and boundary
                center_lat, center_lng = h3.cell_to_latlng(h3_cell)
                cell_boundary = h3.cell_to_boundary(h3_cell)
                
                # Sample raster values within the cell
                cell_values = self._sample_raster_for_cell(
                    src, cell_boundary, sampling_method
                )
                
                # Filter out cells with too much nodata
                valid_ratio = np.sum(~np.isnan(cell_values)) / len(cell_values)
                if valid_ratio < nodata_threshold:
                    continue
                
                # Calculate statistics
                cell_stats = self._calculate_raster_statistics(cell_values)
                
                h3_cells[h3_cell] = {
                    'h3_cell': h3_cell,
                    'resolution': resolution,
                    'center': (center_lat, center_lng),
                    'boundary': cell_boundary,
                    'raster_statistics': cell_stats,
                    'valid_pixel_ratio': valid_ratio,
                    'sample_count': len(cell_values)
                }
        
        return {
            'dataset_type': 'raster',
            'source_file': raster_path,
            'resolution': resolution,
            'total_cells': len(h3_cells),
            'cells': list(h3_cells.values())
        }
    
    def _get_covering_cells_for_bounds(self, bounds, resolution: int) -> List[str]:
        """Get H3 cells that cover the raster bounds"""
        
        minx, miny, maxx, maxy = bounds
        
        # Create a grid of sample points
        step = 0.01  # Adjust based on resolution
        cells = set()
        
        x = minx
        while x <= maxx:
            y = miny
            while y <= maxy:
                h3_cell = h3.latlng_to_cell(y, x, resolution)
                cells.add(h3_cell)
                y += step
            x += step
        
        return list(cells)
    
    def _sample_raster_for_cell(self, 
                               src: rasterio.DatasetReader,
                               cell_boundary: List[tuple],
                               sampling_method: str) -> np.ndarray:
        """Sample raster values within an H3 cell"""
        
        # Create sampling points within the cell
        sample_points = self._generate_sample_points(cell_boundary)
        
        # Sample raster at these points
        values = []
        for lat, lng in sample_points:
            try:
                # Convert to raster coordinates
                row, col = src.index(lng, lat)
                if 0 <= row < src.height and 0 <= col < src.width:
                    value = src.read(1)[row, col]
                    values.append(value)
                else:
                    values.append(np.nan)
            except:
                values.append(np.nan)
        
        return np.array(values)
    
    def _generate_sample_points(self, cell_boundary: List[tuple]) -> List[tuple]:
        """Generate sample points within an H3 cell"""
        
        # Simple grid sampling within cell boundary
        lats = [lat for lat, lng in cell_boundary]
        lngs = [lng for lat, lng in cell_boundary]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        
        # Create a grid of points
        sample_points = []
        for lat in np.linspace(min_lat, max_lat, 10):
            for lng in np.linspace(min_lng, max_lng, 10):
                sample_points.append((lat, lng))
        
        return sample_points
    
    def _calculate_raster_statistics(self, values: np.ndarray) -> Dict[str, float]:
        """Calculate statistics for raster values in a cell"""
        
        valid_values = values[~np.isnan(values)]
        
        if len(valid_values) == 0:
            return {
                'mean': np.nan,
                'median': np.nan,
                'std': np.nan,
                'min': np.nan,
                'max': np.nan,
                'count': 0
            }
        
        return {
            'mean': float(np.mean(valid_values)),
            'median': float(np.median(valid_values)),
            'std': float(np.std(valid_values)),
            'min': float(np.min(valid_values)),
            'max': float(np.max(valid_values)),
            'count': int(len(valid_values))
        }

# Example usage
async def integrate_elevation_data():
    """Example: Integrate elevation raster data"""
    
    integrator = RasterDatasetH3Integrator(default_resolution=9)
    
    result = await integrator.integrate_raster_dataset(
        raster_path='path/to/elevation_dem.tif',
        sampling_method='bilinear',
        nodata_threshold=0.7
    )
    
    print(f"Integrated elevation data into {result['total_cells']} H3 cells")
    return result
```

### 4. Time Series Datasets

#### Temporal Data Integration
```python
from datetime import datetime, timedelta
import pandas as pd

class TimeSeriesH3Integrator:
    """Integrate time series datasets with H3 system"""
    
    def __init__(self, default_resolution: int = 8):
        self.default_resolution = default_resolution
    
    async def integrate_timeseries_dataset(self,
                                         timeseries_df: pd.DataFrame,
                                         lat_col: str = 'latitude',
                                         lng_col: str = 'longitude',
                                         time_col: str = 'timestamp',
                                         value_cols: List[str] = None,
                                         resolution: int = None,
                                         temporal_aggregation: str = 'daily') -> Dict[str, Any]:
        """Integrate time series dataset into H3 grid system"""
        
        resolution = resolution or self.default_resolution
        value_cols = value_cols or []
        
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(timeseries_df[time_col]):
            timeseries_df[time_col] = pd.to_datetime(timeseries_df[time_col])
        
        # Group by H3 cell and time period
        timeseries_df['h3_cell'] = timeseries_df.apply(
            lambda row: h3.latlng_to_cell(row[lat_col], row[lng_col], resolution),
            axis=1
        )
        
        # Create temporal grouping
        if temporal_aggregation == 'daily':
            timeseries_df['time_group'] = timeseries_df[time_col].dt.date
        elif temporal_aggregation == 'hourly':
            timeseries_df['time_group'] = timeseries_df[time_col].dt.floor('H')
        elif temporal_aggregation == 'weekly':
            timeseries_df['time_group'] = timeseries_df[time_col].dt.to_period('W')
        else:
            timeseries_df['time_group'] = timeseries_df[time_col]
        
        # Group and aggregate
        h3_timeseries = {}
        
        grouped = timeseries_df.groupby(['h3_cell', 'time_group'])
        
        for (h3_cell, time_group), group in grouped:
            if h3_cell not in h3_timeseries:
                h3_timeseries[h3_cell] = {
                    'h3_cell': h3_cell,
                    'resolution': resolution,
                    'center': h3.cell_to_latlng(h3_cell),
                    'boundary': h3.cell_to_boundary(h3_cell),
                    'time_series': {},
                    'summary_statistics': {}
                }
            
            # Aggregate values for this time period
            time_stats = {}
            for col in value_cols:
                if col in group.columns:
                    values = group[col].dropna()
                    if len(values) > 0:
                        time_stats[col] = {
                            'mean': float(values.mean()),
                            'sum': float(values.sum()),
                            'count': int(len(values)),
                            'min': float(values.min()),
                            'max': float(values.max()),
                            'std': float(values.std()) if len(values) > 1 else 0.0
                        }
            
            h3_timeseries[h3_cell]['time_series'][str(time_group)] = time_stats
        
        # Calculate overall summary statistics
        for cell_data in h3_timeseries.values():
            cell_data['summary_statistics'] = self._calculate_temporal_summary(
                cell_data['time_series'], value_cols
            )
        
        return {
            'dataset_type': 'timeseries',
            'resolution': resolution,
            'temporal_aggregation': temporal_aggregation,
            'total_records': len(timeseries_df),
            'total_cells': len(h3_timeseries),
            'time_range': {
                'start': str(timeseries_df[time_col].min()),
                'end': str(timeseries_df[time_col].max())
            },
            'cells': list(h3_timeseries.values())
        }
    
    def _calculate_temporal_summary(self, 
                                   time_series: Dict[str, Dict[str, Any]], 
                                   value_cols: List[str]) -> Dict[str, Any]:
        """Calculate summary statistics across time series"""
        
        summary = {}
        
        for col in value_cols:
            col_values = []
            for time_point in time_series.values():
                if col in time_point and 'mean' in time_point[col]:
                    col_values.append(time_point[col]['mean'])
            
            if col_values:
                summary[col] = {
                    'temporal_mean': float(np.mean(col_values)),
                    'temporal_std': float(np.std(col_values)),
                    'temporal_min': float(np.min(col_values)),
                    'temporal_max': float(np.max(col_values)),
                    'temporal_trend': self._calculate_trend(col_values),
                    'time_points': len(col_values)
                }
        
        return summary
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        return float(coefficients[0])  # Slope

# Example usage
async def integrate_sensor_timeseries():
    """Example: Integrate sensor time series data"""
    
    # Create sample time series data
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    sensor_data = []
    
    for i, date in enumerate(dates):
        sensor_data.append({
            'timestamp': date,
            'latitude': 40.7128 + np.random.normal(0, 0.01),
            'longitude': -74.0060 + np.random.normal(0, 0.01),
            'temperature': 20 + 5 * np.sin(i / 24 * 2 * np.pi) + np.random.normal(0, 2),
            'humidity': 60 + 10 * np.cos(i / 24 * 2 * np.pi) + np.random.normal(0, 5)
        })
    
    sensor_df = pd.DataFrame(sensor_data)
    
    integrator = TimeSeriesH3Integrator(default_resolution=10)
    
    result = await integrator.integrate_timeseries_dataset(
        timeseries_df=sensor_df,
        value_cols=['temperature', 'humidity'],
        temporal_aggregation='daily'
    )
    
    print(f"Integrated {result['total_records']} sensor readings into {result['total_cells']} H3 cells")
    return result
```

## 🔄 Multi-Resolution Integration

### Hierarchical Data Integration
```python
class MultiResolutionH3Integrator:
    """Integrate datasets across multiple H3 resolutions"""
    
    def __init__(self, resolutions: List[int] = [6, 7, 8, 9, 10]):
        self.resolutions = sorted(resolutions)
    
    async def integrate_multi_resolution(self,
                                       dataset: Dict[str, Any],
                                       base_resolution: int) -> Dict[str, Any]:
        """Integrate dataset across multiple resolutions with aggregation"""
        
        if base_resolution not in self.resolutions:
            raise ValueError(f"Base resolution {base_resolution} not in supported resolutions")
        
        # Start with base resolution data
        multi_res_data = {base_resolution: dataset['cells']}
        
        # Aggregate to coarser resolutions
        for target_res in self.resolutions:
            if target_res < base_resolution:
                multi_res_data[target_res] = await self._aggregate_to_resolution(
                    multi_res_data[base_resolution], target_res
                )
        
        # Disaggregate to finer resolutions (if needed)
        for target_res in self.resolutions:
            if target_res > base_resolution:
                multi_res_data[target_res] = await self._disaggregate_to_resolution(
                    multi_res_data[base_resolution], target_res
                )
        
        return {
            'dataset_type': f"multi_resolution_{dataset['dataset_type']}",
            'base_resolution': base_resolution,
            'resolutions': list(multi_res_data.keys()),
            'resolution_data': multi_res_data
        }
    
    async def _aggregate_to_resolution(self, 
                                     cells: List[Dict[str, Any]], 
                                     target_resolution: int) -> List[Dict[str, Any]]:
        """Aggregate cells to a coarser resolution"""
        
        aggregated_cells = {}
        
        for cell in cells:
            # Get parent cell at target resolution
            parent_cell = h3.cell_to_parent(cell['h3_cell'], target_resolution)
            
            if parent_cell not in aggregated_cells:
                aggregated_cells[parent_cell] = {
                    'h3_cell': parent_cell,
                    'resolution': target_resolution,
                    'center': h3.cell_to_latlng(parent_cell),
                    'boundary': h3.cell_to_boundary(parent_cell),
                    'child_cells': [],
                    'aggregated_properties': {}
                }
            
            aggregated_cells[parent_cell]['child_cells'].append(cell)
        
        # Aggregate properties
        for agg_cell in aggregated_cells.values():
            agg_cell['aggregated_properties'] = self._aggregate_cell_properties(
                agg_cell['child_cells']
            )
            agg_cell['child_count'] = len(agg_cell['child_cells'])
            del agg_cell['child_cells']  # Remove to save space
        
        return list(aggregated_cells.values())
    
    async def _disaggregate_to_resolution(self, 
                                        cells: List[Dict[str, Any]], 
                                        target_resolution: int) -> List[Dict[str, Any]]:
        """Disaggregate cells to a finer resolution"""
        
        disaggregated_cells = []
        
        for cell in cells:
            # Get child cells at target resolution
            child_cells = h3.cell_to_children(cell['h3_cell'], target_resolution)
            
            for child_cell in child_cells:
                disaggregated_cells.append({
                    'h3_cell': child_cell,
                    'resolution': target_resolution,
                    'center': h3.cell_to_latlng(child_cell),
                    'boundary': h3.cell_to_boundary(child_cell),
                    'parent_cell': cell['h3_cell'],
                    'inherited_properties': cell.get('properties', {}),
                    'properties': self._interpolate_properties(
                        cell.get('properties', {}), child_cell
                    )
                })
        
        return disaggregated_cells
    
    def _aggregate_cell_properties(self, child_cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate properties from child cells"""
        
        if not child_cells:
            return {}
        
        aggregated = {}
        
        # Get all property keys
        all_keys = set()
        for cell in child_cells:
            if 'properties' in cell:
                all_keys.update(cell['properties'].keys())
        
        for key in all_keys:
            values = []
            for cell in child_cells:
                if 'properties' in cell and key in cell['properties']:
                    val = cell['properties'][key]
                    if isinstance(val, (int, float)) and not np.isnan(val):
                        values.append(val)
            
            if values:
                aggregated[f'{key}_mean'] = float(np.mean(values))
                aggregated[f'{key}_sum'] = float(np.sum(values))
                aggregated[f'{key}_min'] = float(np.min(values))
                aggregated[f'{key}_max'] = float(np.max(values))
                aggregated[f'{key}_count'] = len(values)
        
        return aggregated
    
    def _interpolate_properties(self, 
                              parent_properties: Dict[str, Any], 
                              child_cell: str) -> Dict[str, Any]:
        """Interpolate properties for disaggregated cells"""
        
        # Simple inheritance - more sophisticated interpolation could be implemented
        interpolated = {}
        
        for key, value in parent_properties.items():
            if isinstance(value, (int, float)):
                # Add some spatial variation based on cell position
                cell_lat, cell_lng = h3.cell_to_latlng(child_cell)
                variation = 0.95 + 0.1 * (hash(child_cell) % 100) / 100
                interpolated[key] = value * variation
            else:
                interpolated[key] = value
        
        return interpolated
```

## 📋 Best Practices for Dataset Integration

### 1. Data Quality and Validation
```python
class DataQualityValidator:
    """Validate data quality for H3 integration"""
    
    @staticmethod
    def validate_coordinates(lat: float, lng: float) -> bool:
        """Validate coordinate values"""
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    @staticmethod
    def validate_h3_cell(h3_cell: str) -> bool:
        """Validate H3 cell identifier"""
        try:
            h3.cell_to_latlng(h3_cell)
            return True
        except:
            return False
    
    @staticmethod
    def check_data_completeness(df: pd.DataFrame, required_cols: List[str]) -> Dict[str, float]:
        """Check data completeness"""
        completeness = {}
        for col in required_cols:
            if col in df.columns:
                completeness[col] = df[col].notna().sum() / len(df)
            else:
                completeness[col] = 0.0
        return completeness
```

### 2. Performance Optimization
```python
class H3IntegrationOptimizer:
    """Optimize H3 integration performance"""
    
    @staticmethod
    def batch_h3_conversion(coords: List[Tuple[float, float]], 
                           resolution: int,
                           batch_size: int = 10000) -> List[str]:
        """Convert coordinates to H3 cells in batches"""
        
        h3_cells = []
        for i in range(0, len(coords), batch_size):
            batch = coords[i:i + batch_size]
            batch_cells = [h3.latlng_to_cell(lat, lng, resolution) 
                          for lat, lng in batch]
            h3_cells.extend(batch_cells)
        
        return h3_cells
    
    @staticmethod
    def spatial_index_optimization(cells: List[str]) -> Dict[str, List[str]]:
        """Create spatial index for efficient querying"""
        
        # Group cells by parent at coarser resolution
        spatial_index = {}
        coarse_resolution = max(0, min(h3.cell_to_res(cell) for cell in cells) - 2)
        
        for cell in cells:
            parent = h3.cell_to_parent(cell, coarse_resolution)
            if parent not in spatial_index:
                spatial_index[parent] = []
            spatial_index[parent].append(cell)
        
        return spatial_index
```

## 📊 Integration Examples by Domain

### Agriculture: Field Monitoring
```python
async def integrate_agricultural_fields():
    """Integrate agricultural field monitoring data"""
    
    # Field boundary polygons with crop data
    field_data = gpd.GeoDataFrame({
        'field_id': ['F001', 'F002', 'F003'],
        'crop_type': ['wheat', 'corn', 'soybeans'],
        'planting_date': ['2024-04-15', '2024-05-01', '2024-04-20'],
        'expected_yield': [4.5, 6.2, 3.8],  # tons per hectare
        'geometry': [...]  # Polygon geometries
    })
    
    # Sensor time series data
    sensor_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-06-01', periods=90, freq='D'),
        'field_id': ['F001'] * 90,
        'soil_moisture': np.random.normal(0.3, 0.05, 90),
        'temperature': 25 + 5 * np.sin(np.arange(90) / 15) + np.random.normal(0, 2, 90)
    })
    
    # Integrate field boundaries
    polygon_integrator = PolygonDatasetH3Integrator(default_resolution=10)
    field_h3 = await polygon_integrator.integrate_polygon_dataset(field_data)
    
    # Integrate sensor data
    ts_integrator = TimeSeriesH3Integrator(default_resolution=10)
    sensor_h3 = await ts_integrator.integrate_timeseries_dataset(
        sensor_data, 
        lat_col='latitude', 
        lng_col='longitude',
        value_cols=['soil_moisture', 'temperature']
    )
    
    return {'fields': field_h3, 'sensors': sensor_h3}
```

### Urban Planning: City Analytics
```python
async def integrate_urban_data():
    """Integrate urban planning and analytics data"""
    
    # Building footprints
    buildings = gpd.read_file('city_buildings.geojson')
    
    # Traffic sensors
    traffic_data = pd.read_csv('traffic_sensors.csv')
    
    # Population census data
    census_data = gpd.read_file('census_blocks.geojson')
    
    # Integrate all datasets at different resolutions
    multi_integrator = MultiResolutionH3Integrator([7, 8, 9, 10])
    
    # Buildings at high resolution
    polygon_integrator = PolygonDatasetH3Integrator(default_resolution=10)
    building_h3 = await polygon_integrator.integrate_polygon_dataset(buildings)
    
    # Traffic at medium resolution
    point_integrator = PointDatasetH3Integrator(default_resolution=8)
    traffic_h3 = await point_integrator.integrate_point_dataset(
        traffic_data, 
        properties_cols=['avg_speed', 'vehicle_count']
    )
    
    # Census at low resolution
    census_h3 = await polygon_integrator.integrate_polygon_dataset(
        census_data, resolution=7
    )
    
    return {
        'buildings': building_h3,
        'traffic': traffic_h3,
        'census': census_h3
    }
```

---

This comprehensive guide provides practical patterns for integrating any type of geospatial dataset with H3 systems, enabling efficient spatial analysis and visualization across the entire GEO-INFER ecosystem.