# Documentation Standards

## Docstring Format (Google-style)

```python
def compute_risk(
    region: dict[str, Any],
    hazard_type: str,
    return_period: int = 100,
) -> dict[str, float]:
    """Compute risk metrics for a geographic region.

    Calculates expected annual loss (EAL), probable maximum loss (PML),
    and tail value at risk (TVaR) using the region's exposure and
    vulnerability data.

    Args:
        region: GeoJSON-like dict with 'features' containing exposure data.
        hazard_type: One of 'earthquake', 'flood', 'hurricane', 'wildfire'.
        return_period: Return period in years for PML calculation.

    Returns:
        Dictionary with keys 'eal', 'pml', 'tvar'.

    Raises:
        ValueError: If hazard_type is not recognised.
        DataValidationError: If region features are malformed.

    Example:
        >>> result = compute_risk(region_data, 'earthquake', 250)
        >>> result['eal']
        1250000.0
    """
```

Every public function/method must include: `Args`, `Returns`, `Raises`, and `Example`.

## YAML Front Matter

All module READMEs must start with:

```yaml
---
title: GEO-INFER-MODULE
description: One-line module description
purpose: What this module does and why
module_type: core | domain | application | operations
status: alpha | beta | stable
version: 0.2.0
last_updated: 2026-02-25
dependencies:
  - GEO-INFER-MATH
  - GEO-INFER-SPACE
tags:
  - geospatial
  - active-inference
---
```

## README Sections (required)

1. **Overview** — module purpose and scope
2. **Core Features** — capabilities list (not "Key Features")
3. **API Reference** — core classes with signatures
4. **Integration** — how it connects to other modules
5. **Getting Started** — installation and basic usage
6. **Examples** — working code that actually runs
7. **Troubleshooting** — common issues and solutions

## AGENTS.md

Every module must have an `AGENTS.md` file that helps AI agents navigate:

```markdown
# GEO-INFER-MODULE Agent Guide

## Key Files
- `src/geo_infer_module/core/engine.py` — Main engine class
- `src/geo_infer_module/api/rest_api.py` — API endpoints

## Common Tasks
- Adding a new analysis type: extend `Engine.run_analysis()`
- Adding an API endpoint: add route in `rest_api.py`

## Gotchas
- Always validate input data before processing
- Use H3 v4 API methods (not v3)
```

## CHANGELOG.md

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [0.2.0] - 2026-02-25
### Added
- Spatial statistics (Moran's I, Geary C)
### Fixed
- Placeholder implementations replaced with real logic
### Changed
- Updated H3 API to v4
```

## Cross-Reference Standards

- Link to related modules: `See [GEO-INFER-SPACE](../GEO-INFER-SPACE/README.md)`
- Link to specific files: `See [risk_engine.py](../GEO-INFER-RISK/src/geo_infer_risk/core/risk_engine.py)`
- Reference other cursorrules: `See principles.md for logging standards`

## Language Guidelines

- Use precise, technical language over marketing terms
- Prefer "provides" over "provides comprehensive and sophisticated"
- Choose "implements" over "implements advanced and cutting-edge"
- Eliminate redundant adjectives that don't add technical value
- Focus on capabilities and functionality rather than superlatives

## API Documentation

For modules with REST APIs, maintain OpenAPI specs:

```yaml
# docs/api_schema.yaml
openapi: 3.0.0
info:
  title: GEO-INFER-MODULE API
  version: 0.2.0
paths:
  /api/v1/analyse:
    post:
      summary: Run analysis
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AnalysisRequest'
```

## Documentation Resources

- **Standards**: `GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md`
- **Templates**: `GEO-INFER-INTRA/docs/templates/`
- **Module Index**: `GEO-INFER-INTRA/docs/modules/index.md`
