---
name: geo-infer-app
description: Application framework for geospatial dashboards and web interfaces. Use when building spatial dashboards, map-based UIs, agent control widgets, interactive geospatial web applications, or configuring agent parameters through forms.
prerequisites:
  required:
    - geo-infer-api
  recommended:
    - geo-infer-data
    - geo-infer-space
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-APP

## Instructions

### Core Capabilities

- **Dashboards**: Map-based spatial analysis dashboards with real-time updates
- **Agent widgets**: Agent configuration forms with lat/lng inputs and JSON parameter editors
- **Map components**: Interactive map layers, choropleth, heatmaps, tile overlays
- **Data panels**: Tabular and chart-based data exploration
- **Agent configuration**: Forms for setting agent spatial bounds and behaviors

### Key Imports

```python
from geo_infer_app.core.dashboard import DashboardBuilder
from geo_infer_app.components.agent_widget import AgentWidget
from geo_infer_app.components.map_view import MapView
from geo_infer_app.components.agent.agent_config_form import AgentConfigForm
```

## Examples

```python
from geo_infer_app.core.dashboard import DashboardBuilder

dashboard = DashboardBuilder(title="Spatial Analysis")
dashboard.add_map_layer("h3_cells", h3_data)
dashboard.add_chart("time_series", temporal_data)
dashboard.serve(port=8050)
```

## Guidelines

- HTML form inputs use standard `placeholder` attributes (legitimate usage)

### Integrations

- Integrates with AGENT for real-time agent control
- Integrates with SPACE for H3 visualization layers
- Test: `uv run python -m pytest GEO-INFER-APP/tests/ -v`
