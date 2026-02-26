---
title: "GEO-INFER-MARINE: Marine and Coastal Analysis"
description: "Ocean monitoring, coastal analysis, and marine resource management"
purpose: "Provide marine spatial analysis, oceanographic modeling, and coastal zone management"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "TIME", "DATA", "CLIMATE"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-DATA", "GEO-INFER-CLIMATE"]
tags: ["marine", "ocean", "coastal", "fisheries", "maritime"]
difficulty: "Intermediate"
estimated_time: "55"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-MARINE: Marine and Coastal Analysis

## Overview

**GEO-INFER-MARINE** provides comprehensive capabilities for marine and coastal spatial analysis. The module enables:

- **Ocean Monitoring**: Sea surface temperature, chlorophyll, currents
- **Coastal Analysis**: Erosion, inundation, habitat mapping
- **Marine Spatial Planning**: Zoning, use conflicts, conservation
- **Fisheries Management**: Stock assessment, habitat modeling
- **Maritime Operations**: Shipping routes, port analysis

## Features

### Ocean Monitoring

```python
from geo_infer_marine import OceanMonitor

# Monitor ocean conditions
monitor = OceanMonitor()

conditions = monitor.get_conditions(
    area=study_area,
    parameters=["sst", "chlorophyll", "salinity", "currents"],
    date="2026-02-25"
)

print(f"Sea Surface Temperature: {conditions.sst}°C")
print(f"Chlorophyll-a: {conditions.chlorophyll} mg/m³")
print(f"Current speed: {conditions.current_speed} m/s")
```

### Coastal Analysis

```python
from geo_infer_marine import CoastalAnalyzer

# Analyze coastal dynamics
coastal = CoastalAnalyzer()

analysis = coastal.analyze(
    shoreline=coastline,
    dem=coastal_dem,
    wave_data=wave_hindcast,
    period=("2000", "2025")
)

print(f"Erosion rate: {analysis.erosion_rate} m/year")
print(f"High erosion areas: {analysis.hotspots}")
print(f"Sea level rise impact: {analysis.slr_impact}")
```

### Marine Spatial Planning

```python
from geo_infer_marine import MarinePlanner

# Create marine spatial plan
planner = MarinePlanner()

plan = planner.create_plan(
    planning_area=eez_boundary,
    uses=["fishing", "shipping", "renewable_energy", "conservation"],
    constraints={
        "protected_areas": mpas,
        "shipping_lanes": major_routes
    }
)

print(f"Zone allocations: {plan.zones}")
print(f"Conflicts resolved: {plan.conflicts_addressed}")
```

### Fisheries Analysis

```python
from geo_infer_marine import FisheriesAnalyzer

# Analyze fisheries
fisheries = FisheriesAnalyzer()

assessment = fisheries.assess(
    species="atlantic_cod",
    area=fishing_grounds,
    data={
        "catch": catch_data,
        "effort": effort_data,
        "survey": trawl_survey
    }
)

print(f"Stock status: {assessment.stock_status}")
print(f"Spawning biomass: {assessment.spawning_biomass}")
print(f"Sustainable yield: {assessment.msy}")
```

## Analysis Capabilities

| Analysis Type | Description |
|---------------|-------------|
| **Bathymetry** | Seafloor mapping, depth analysis |
| **Habitat Mapping** | Benthic classification, coral reefs |
| **Water Quality** | Turbidity, nutrients, pollution |
| **Coastal Hazards** | Storm surge, tsunami, flooding |
| **Vessel Tracking** | AIS analysis, traffic patterns |

## Data Sources

| Data Type | Sources |
|-----------|---------|
| **Satellite** | MODIS, Sentinel-3, Landsat |
| **Buoys** | NDBC, Argo floats |
| **Models** | HYCOM, ROMS, WaveWatch III |
| **AIS** | Vessel tracking data |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-CLIMATE** | Ocean-climate interactions |
| **GEO-INFER-BIO** | Marine biodiversity |
| **GEO-INFER-RISK** | Coastal hazard assessment |
| **GEO-INFER-LOG** | Maritime logistics |

## Installation

```bash
# Install marine module
uv pip install -e "./GEO-INFER-MARINE"

# With oceanographic tools
uv pip install -e "./GEO-INFER-MARINE[ocean]"
```

## Use Cases

### Blue Economy Planning

```python
from geo_infer_marine import BlueEconomyPlanner

planner = BlueEconomyPlanner(region="pacific_islands")

# Analyze blue economy potential
potential = planner.assess_potential(
    sectors=["aquaculture", "tourism", "offshore_wind"],
    sustainability_constraints=True
)

print(f"Economic potential: ${potential.value_billions}B")
print(f"Sustainable zones: {potential.suitable_areas}")
```

## Related Documentation

- [GEO-INFER-WATER](../GEO-INFER-WATER/README.md): Water resources
- [GEO-INFER-CLIMATE](../GEO-INFER-CLIMATE/README.md): Climate
- [AGENTS.md](./AGENTS.md): Marine agent capabilities

---

**Status**: Alpha - Core functionality implemented

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
