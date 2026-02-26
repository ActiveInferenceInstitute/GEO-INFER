---
name: geo-infer-git
description: Git-based versioning and collaboration for geospatial datasets. Use when versioning spatial data, managing geospatial dataset lineage, tracking spatial data changes, resolving merge conflicts in geospatial formats, or building reproducible analysis pipelines.
prerequisites:
  required: []
  recommended: []
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-GIT

## Instructions

### Core Capabilities

- **Spatial data versioning**: Track changes to GeoJSON, Shapefile, GeoParquet
- **Lineage tracking**: Dataset provenance, transformation history, audit trail
- **Collaboration**: Merge strategies for spatial data conflicts (geometry-aware diff)
- **Reproducibility**: Version-controlled analysis pipelines with spatial checksums
- **Branch strategies**: Feature-branch workflows for spatial analyses

### Key Imports

```python
from geo_infer_git.core.versioning import SpatialVersionControl
from geo_infer_git.core.lineage import DataLineageTracker
from geo_infer_git.core.collaboration import SpatialMergeEngine
from geo_infer_git.core.checksum import SpatialChecksumCalculator
```

## Examples

```python
from geo_infer_git.core.versioning import SpatialVersionControl

vcs = SpatialVersionControl(repo_path="./spatial_data")
vcs.track("boundaries.geojson")
vcs.commit("Updated county boundaries from 2026 census")
diff = vcs.diff("HEAD~1", "HEAD", file="boundaries.geojson")
print(f"Changed features: {diff.added + diff.modified + diff.deleted}")
```

## Guidelines


### Integrations

- Integrates with DATA for format-aware versioning
- Test: `uv run python -m pytest GEO-INFER-GIT/tests/ -v`
