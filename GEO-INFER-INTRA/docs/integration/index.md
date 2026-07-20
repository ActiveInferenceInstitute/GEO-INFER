# Integration Guide

GEO-INFER integrations are explicit Python imports, validated data/artifact
handoffs, and optional service adapters owned by modules. There is no implicit
framework-wide event bus or hosted INTRA service in this repository.

## Integration workflow

1. Identify the owning module for the input and output.
2. Use public package exports or a documented adapter.
3. Declare the dependency in the consuming module's metadata.
4. Define coordinate system, units, missing-value policy, random seed, and output
   schema at the boundary.
5. Add an integration test and run both module gates.

## Common patterns

### Data to inference

`text
DATA ingestion/validation
  -> SPACE indexing and CRS-aware geometry
  -> TIME alignment when timestamps exist
  -> ACT/BAYES/SPM inference
  -> domain result and validated artifact
`

### Agent and optimization

`text
observations -> AGENT/ANT policy or optimization -> SIM/domain state -> observations
`

Use ACT as the canonical Active Inference contract. ANT accepts explicit
objective functions and bounds; it does not silently fabricate an environment.

### API and application

GEO-INFER-API owns its FastAPI/GeoJSON boundary. GEO-INFER-APP consumes
application-facing interfaces. Keep authentication, serialization, and route
contracts in those modules rather than duplicating them in INTRA docs.

## Example: spatial data handoff

`python
import numpy as np
from geo_infer_space import latlng_to_cell
from geo_infer_act import FreeEnergyCalculator

cell = latlng_to_cell(37.7749, -122.4194, resolution=9)
free_energy = FreeEnergyCalculator().compute_categorical_free_energy(
    beliefs=np.array([0.7, 0.2, 0.1]),
    observations=np.array([0.8, 0.15, 0.05]),
)
print(cell, free_energy)
`

## Further reading

- [Architecture](../architecture/index.md)
- [Module catalog](../modules/index.md)
- [Module integration guide](../guides/MODULE_INTEGRATION_GUIDE.md)
- [External systems guidance](external_systems.md)
- [Testing guide](../developer_guide/testing_guide.md)
