# Bioregional Economics Guide

## Introduction

Bioregional economics focuses on economic analysis that respects ecological boundaries and promotes sustainable regional development.

## Key Concepts

### Bioregions

A bioregion is an area defined by natural boundaries (watersheds, ecosystems) rather than political ones.

```python
from geo_infer_econ import BioregionalAnalyzer

# Define bioregion
bioregion = BioregionalAnalyzer(
    boundary=watershed_boundary,
    include=["agriculture", "forestry", "fisheries"]
)
```

### Local Multipliers

Economic activity within a bioregion has multiplier effects:

```python
# Calculate local multiplier effect
multiplier = bioregion.calculate_multiplier(
    sector="local_food",
    method="input_output"
)

print(f"Local food dollar circulates {multiplier}x in region")
```

## Analysis Types

### Resource Flow Analysis

```python
# Track resource flows
flows = bioregion.analyze_flows(
    resources=["water", "energy", "materials"],
    direction="both"  # imports and exports
)
```

### Carrying Capacity

```python
# Assess ecological carrying capacity
capacity = bioregion.carrying_capacity(
    population=current_pop,
    consumption=consumption_patterns
)
```

## Use Cases

| Use Case | Application |
|----------|-------------|
| Food Systems | Local food economy |
| Energy | Regional renewable potential |
| Water | Watershed-based planning |
| Tourism | Eco-tourism development |

---

**Last Updated**: 2026-01-26
