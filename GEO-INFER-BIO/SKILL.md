---
name: geo-infer-bio
description: Biodiversity analysis and ecological modeling. Use when analyzing species distributions, habitat connectivity, biodiversity indices, ecological networks, conservation planning, or ecosystem health assessment.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-bayes
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-BIO

## Instructions

### Core Capabilities

- **Species distribution**: Habitat suitability modeling, range mapping
- **Biodiversity indices**: Shannon, Simpson, species richness, evenness
- **Habitat connectivity**: Corridor analysis, fragmentation metrics
- **Ecological networks**: Food webs, mutualistic networks, trophic cascades
- **Conservation planning**: Priority area identification, gap analysis

### Key Imports

```python
from geo_infer_bio.core.biodiversity import BiodiversityAnalyzer
from geo_infer_bio.core.habitat import HabitatModel
from geo_infer_bio.core.connectivity import ConnectivityAnalyzer
from geo_infer_bio.core.ecosystem import EcosystemHealthAssessor
```

## Examples

```python
from geo_infer_bio.core.biodiversity import BiodiversityAnalyzer

analyzer = BiodiversityAnalyzer()
indices = analyzer.compute_indices(species_data)
print(f"Shannon: {indices.shannon}, Simpson: {indices.simpson}")

# Hotspot detection
hotspots = analyzer.detect_hotspots(species_grid, threshold=0.95)
```

## Guidelines


### Integrations

- Integrates with SPACE for H3-based habitat tessellation
- Integrates with CLIMATE for climate-driven species range shifts
- Integrates with FOREST for canopy-biodiversity correlations
- Test: `uv run python -m pytest GEO-INFER-BIO/tests/ -v`
