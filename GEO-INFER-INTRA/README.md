---
title: "GEO-INFER-INTRA: Internal Documentation and Repository Management"
description: "Internal documentation, repository assessment, and project management utilities for the GEO-INFER framework"
purpose: "Provide centralized documentation, configuration management, and repository health assessment tools"
module_type: "Infrastructure"
status: "Beta"
last_updated: "2026-02-25"
dependencies: []
compatibility: ["All GEO-INFER modules"]
tags: ["documentation", "repository-management", "configuration", "testing", "internal"]
difficulty: "Intermediate"
estimated_time: "30"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-INTRA: Internal Documentation and Repository Management

## Overview

**GEO-INFER-INTRA** is the internal documentation and repository management module for the GEO-INFER framework. It provides tools for:

- **Repository Assessment**: Automated health checks and code quality analysis
- **Configuration Management**: Centralized configuration for all modules
- **Documentation Generation**: Auto-generated documentation from code
- **Testing Infrastructure**: Shared test utilities and fixtures
- **Template Management**: Project and module templates

## Framework Stats (v0.2.0 — 2026-02-25)

| Metric | Count |
|--------|-------|
| Modules | 44 |
| Source Files | 858 |
| Source Lines | 295,696 |
| Test Files | 416 |
| Tests | 3,000+ |

## Features

### Repository Assessment

```python
from geo_infer_intra import RepositoryAssessor

# Assess repository health
assessor = RepositoryAssessor(root_path="./")
report = assessor.assess()

print(f"Code Quality: {report.code_quality_score}")
print(f"Documentation Coverage: {report.doc_coverage}%")
print(f"Test Coverage: {report.test_coverage}%")
```

### Configuration Management

```python
from geo_infer_intra.config import Config, load_config

# Load configuration
config = load_config("config/settings.yaml")

# Access configuration values
log_level = config.get("logging.level", default="INFO")
db_url = config.get("database.url")
```

### Testing Utilities

```python
from geo_infer_intra.testing import GeospatialTestCase

class TestMyModule(GeospatialTestCase):
    def test_spatial_operation(self):
        point = self.create_test_point(lat=37.7749, lon=-122.4194)
        polygon = self.create_test_polygon(bounds=[...])
        self.assertPointInPolygon(point, polygon)
```

## Directory Structure

```
GEO-INFER-INTRA/
├── assess_repository.py    # Repository assessment script
├── assessment_results/     # Generated assessment reports
├── config/                 # Configuration files
│   ├── settings.yaml      # Main settings
│   └── logging.yaml       # Logging configuration
├── docs/                   # Documentation
├── examples/               # Usage examples
├── scripts/                # Utility scripts
├── src/                    # Source code
│   └── geo_infer_intra/
│       ├── utils/config.py # Configuration utilities
│       ├── testing/       # Testing utilities
│       └── utils/         # General utilities
├── templates/              # Project templates
└── tests/                  # Test suite
    └── unit/
        ├── test_config.py
        ├── test_geospatial_utils.py
        ├── test_module_utils.py
        └── test_time_series_utils.py
```

## Installation

```bash
# Install with development dependencies
uv pip install -e "./GEO-INFER-INTRA[dev]"
```

## Utility Classes

### TestGeospatialUtils

Provides geospatial testing utilities:

- `create_point()`: Create test point geometries
- `create_polygon()`: Create test polygon geometries
- `create_feature()`: Create GeoJSON features
- `create_feature_collection()`: Create feature collections
- `haversine_distance()`: Calculate distances between points

### TestTimeSeriesUtils

Provides temporal testing utilities:

- `create_iso8601_timestamp()`: Generate ISO 8601 timestamps
- `create_timestamp_range()`: Create time ranges
- `create_daily_timestamps()`: Generate daily time series
- `create_hourly_timestamps()`: Generate hourly time series
- `create_time_series_data()`: Create test time series data

### Config

Configuration management class:

- `load_yaml_config()`: Load YAML configuration files
- `validate_config()`: Validate configuration against schema
- `get_config_value()`: Get values with dot notation
- `merge_configs()`: Merge multiple configurations

## Integration with Other Modules

GEO-INFER-INTRA provides shared infrastructure for all GEO-INFER modules:

| Module | Integration |
|--------|-------------|
| All modules | Shared configuration management |
| GEO-INFER-TEST | Testing utilities and fixtures |
| GEO-INFER-OPS | Deployment and monitoring configs |
| GEO-INFER-GIT | Repository assessment integration |

## Related Documentation

- [GEO-INFER-TEST](../GEO-INFER-TEST/README.md): Testing framework
- [GEO-INFER-OPS](../GEO-INFER-OPS/README.md): Operations and deployment
- [GEO-INFER-GIT](../GEO-INFER-GIT/README.md): Version control

## Development Methodology

GEO-INFER-INTRA integrates with the PAI Algorithm development methodology. See [PAI.md](../PAI.md) for the active inference-guided development workflow used across all modules.

---

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
