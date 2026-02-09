# GEO-INFER-DATA: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-DATA** module provides data management capabilities for agents, enabling data ingestion, transformation, storage, and retrieval of geospatial datasets.

## Agent Capabilities

### 1. Data Ingestion

```python
from geo_infer_data import DataIngester

# Ingest geospatial data
ingester = DataIngester()

dataset = ingester.ingest(
    source="s3://bucket/parcels.parquet",
    format="geoparquet",
    validation=True)

print(f"Records: {dataset.count}")
print(f"CRS: {dataset.crs}")```

### 2. Data Transformation

```python
from geo_infer_data import DataTransformer

# Transform spatial data
transformer = DataTransformer()

transformed = transformer.transform(
    data=input_data,
    operations=["reproject", "simplify", "buffer"],
    target_crs="EPSG:4326")

print(f"Output features: {transformed.count}")```

### 3. Data Catalog

```python
from geo_infer_data import DataCatalog

# Access data catalog
catalog = DataCatalog()

# Search for datasets
datasets = catalog.search(
    keywords=["parcels", "zoning"],
    bbox=city_boundary,
    temporal="2025")

print(f"Found: {len(datasets)} datasets")```

### 4. Data Quality

```python
from geo_infer_data import DataQualityChecker

# Check data quality
checker = DataQualityChecker()

report = checker.check(
    data=spatial_dataset,
    rules=["valid_geometry", "no_gaps", "topology"])

print(f"Quality score: {report.score}%")
print(f"Issues: {report.issues}")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **Ingestion** | ✅ Ready | Multi-format import |
| **Transform** | ✅ Ready | ETL operations |
| **Catalog** | ✅ Ready | Metadata management |
| **Quality** | ✅ Ready | Validation |

### Aspirational Features

- 🔮 **DataCuratorAgent**: Autonomous data management
- 🔮 **DataDiscoveryAgent**: Intelligent search

---

**Last Updated**: 2026-01-26
