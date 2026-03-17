# Area Study Template

A multi-disciplinary template for doing place-based analysis that combines technical infrastructure, social systems, and environmental factors into a unified workflow.

## Prerequisites

- **Python**: 3.11+
- **uv**: recommended (`uv pip`, `uv run`)

## Modules used

### Primary (required)

- `GEO-INFER-SPACE`: spatial analysis + H3 v4 indexing
- `GEO-INFER-DATA`: ingestion + validation + data access
- `GEO-INFER-PLACE`: place-based context + local boundaries
- `GEO-INFER-PEP`: people/community analytics
- `GEO-INFER-IOT`: sensor ingestion + streaming
- `GEO-INFER-BIO`: biodiversity/ecosystem indicators
- `GEO-INFER-HEALTH`: spatial health indicators

### Supporting (optional)

- `GEO-INFER-TIME`: time series + forecasting
- `GEO-INFER-AG`: land use / agriculture overlays
- `GEO-INFER-ECON`: economic indicators
- `GEO-INFER-RISK`: hazard/vulnerability overlays
- `GEO-INFER-API`: integration endpoints
- `GEO-INFER-APP`: dashboards / UI
- `GEO-INFER-NORMS`: governance + consent constraints

## Architecture overview

```mermaid
graph TB
  TECH[Technical Infrastructure]
  SOCIAL[Social Systems]
  ENV[Environmental Factors]

  DATA[GEO-INFER-DATA]
  SPACE[GEO-INFER-SPACE]
  PLACE[GEO-INFER-PLACE]
  PEP[GEO-INFER-PEP]

  IOT[GEO-INFER-IOT]
  HEALTH[GEO-INFER-HEALTH]
  BIO[GEO-INFER-BIO]
  ECON[GEO-INFER-ECON]
  API[GEO-INFER-API]
  APP[GEO-INFER-APP]
  NORMS[GEO-INFER-NORMS]

  TECH --> DATA
  SOCIAL --> DATA
  ENV --> DATA

  DATA --> SPACE
  DATA --> PLACE
  DATA --> PEP

  SPACE --> IOT
  PLACE --> HEALTH
  PLACE --> BIO
  PEP --> ECON

  IOT --> API
  HEALTH --> API
  BIO --> API
  ECON --> API
  NORMS -.-> API
  API --> APP
```

## Quick start

```bash
uv pip install -e ./GEO-INFER-SPACE -e ./GEO-INFER-DATA -e ./GEO-INFER-PLACE -e ./GEO-INFER-PEP
uv pip install -e ./GEO-INFER-IOT -e ./GEO-INFER-BIO -e ./GEO-INFER-HEALTH
```

## Suggested workflow

- **Define study boundary**: administrative boundary, custom polygon, or H3 cells.
- **Configure sources**: census/demographics, IoT streams, environmental layers, health indicators.
- **Run integration**: align all sources to a shared spatial index (H3) + consistent CRS.
- **Validate outputs**: data quality checks + completeness checks + range checks.
- **Review + iterate**: add community feedback loops via `GEO-INFER-PEP` and governance constraints via `GEO-INFER-NORMS`.

