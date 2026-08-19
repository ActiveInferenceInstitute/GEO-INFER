# H3 Dataset Integration Guide

## 🎯 Overview

This guide provides practical patterns and examples for integrating various types of datasets with H3 hexagonal spatial indexing systems within `GEO-INFER-SPACE`. It covers point datasets, polygon features, raster representations, time series, and multi-resolution compositions across the GEO-INFER ecosystem.

## 📊 Dataset Types and Integration Patterns

### 1. Point Datasets

Points (such as sensor positions, GPS traces, or station networks) are indexed into H3 cells using `latlng_to_cell`.

```python
import h3
import pandas as pd
from typing import List, Dict, Any

class PointDatasetH3Integrator:
    """Integrate point datasets with H3 spatial indexing."""

    def __init__(self, default_resolution: int = 8):
        self.default_resolution = default_resolution

    def integrate_point_dataset(
        self,
        points_df: pd.DataFrame,
        lat_col: str = "latitude",
        lng_col: str = "longitude",
        properties_cols: List[str] | None = None,
        resolution: int | None = None,
    ) -> Dict[str, Any]:
        """Index points into H3 cells and aggregate properties."""
        res = resolution if resolution is not None else self.default_resolution
        props = properties_cols or []

        h3_cells: Dict[str, Dict[str, Any]] = {}
        for _, row in points_df.iterrows():
            lat, lng = float(row[lat_col]), float(row[lng_col])
            cell = h3.latlng_to_cell(lat, lng, res)
            if cell not in h3_cells:
                h3_cells[cell] = {
                    "h3_cell": cell,
                    "resolution": res,
                    "center": h3.cell_to_latlng(cell),
                    "boundary": h3.cell_to_boundary(cell),
                    "points": [],
                    "properties": {},
                }
            point_entry = {"lat": lat, "lng": lng}
            for col in props:
                point_entry[col] = row[col]
            h3_cells[cell]["points"].append(point_entry)

        for cell_data in h3_cells.values():
            cell_data["properties"] = self._aggregate_properties(cell_data["points"], props)
            cell_data["point_count"] = len(cell_data["points"])

        return {
            "dataset_type": "point",
            "resolution": res,
            "total_points": len(points_df),
            "total_cells": len(h3_cells),
            "cells": list(h3_cells.values()),
        }

    def _aggregate_properties(self, points: List[Dict[str, Any]], props: List[str]) -> Dict[str, Any]:
        if not points or not props:
            return {}
        aggregated: Dict[str, Any] = {}
        for col in props:
            vals = [p[col] for p in points if col in p and p[col] is not None]
            if not vals:
                continue
            if isinstance(vals[0], (int, float)):
                aggregated[f"{col}_mean"] = sum(vals) / len(vals)
                aggregated[f"{col}_min"] = min(vals)
                aggregated[f"{col}_max"] = max(vals)
                aggregated[f"{col}_sum"] = sum(vals)
            else:
                aggregated[f"{col}_unique_count"] = len(set(vals))
        return aggregated
```

### 2. Polygon & Boundary Datasets

Geographic polygons (administrative boundaries, catchment areas, risk zones) are converted to H3 cells using `geo_to_cells` or `polygon_to_cells` with closed GeoJSON coordinate rings:

```python
import h3
from typing import Dict, Any, List

def polygon_to_h3_coverage(geojson_geometry: Dict[str, Any], resolution: int = 8) -> List[str]:
    """Cover GeoJSON polygon geometry with H3 cells using native H3 v4 API."""
    return sorted(h3.geo_to_cells(geojson_geometry, resolution))
```

### 3. Spatiotemporal Time Series Datasets

Integrating time-series sensor observations (from `GEO-INFER-TIME`) with spatial cells (from `GEO-INFER-SPACE`):

```python
import h3
import pandas as pd
from typing import Dict, Any, List

def spatio_temporal_h3_aggregation(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    time_col: str,
    value_col: str,
    resolution: int = 8,
) -> Dict[str, Dict[str, float]]:
    """Aggregate time-series metric across H3 spatial cells."""
    df_indexed = df.copy()
    df_indexed["h3_cell"] = df_indexed.apply(
        lambda r: h3.latlng_to_cell(r[lat_col], r[lon_col], resolution), axis=1
    )
    result: Dict[str, Dict[str, float]] = {}
    for cell, group in df_indexed.groupby("h3_cell"):
        result[cell] = {
            "mean": float(group[value_col].mean()),
            "std": float(group[value_col].std()) if len(group) > 1 else 0.0,
            "count": int(len(group)),
            "min": float(group[value_col].min()),
            "max": float(group[value_col].max()),
        }
    return result
```

### 4. Multi-Resolution Hierarchical Composition

H3 allows hierarchical aggregation from finer resolution cells to coarser parents and disaggregation to children:

```python
import h3
from typing import List, Set

def aggregate_cells_to_parent(cells: List[str], parent_resolution: int) -> Set[str]:
    """Aggregate a set of H3 cells to their parent resolution."""
    return {h3.cell_to_parent(c, parent_resolution) for c in cells}

def disaggregate_cell_to_children(cell: str, child_resolution: int) -> List[str]:
    """Disaggregate a parent H3 cell to its children cells."""
    return sorted(h3.cell_to_children(cell, child_resolution))
```

## 📋 Best Practices

1. **Explicit Coordinate Order**: In pure H3 function calls (`latlng_to_cell`, `cell_to_latlng`), pass `(lat, lng)`. For GeoJSON representations, standard coordinates are `[lng, lat]`.
2. **Deterministic Outputs**: Ensure cell collections and neighbor lists are consistently ordered (`sorted()`) across runs.
3. **Budget Guards**: Validate input bounds and set maximum cell budget checks before expanding large bounding boxes to avoid memory pressure at fine resolutions ($r \ge 10$).
