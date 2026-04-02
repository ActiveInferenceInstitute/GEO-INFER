---
name: geo-infer-intra
description: "Central documentation hub and cross-module integration layer for GEO-INFER. Use when onboarding new developers to the framework, wiring together multi-module pipelines (e.g. DATA to SPACE to BAYES), resolving import paths across the 44-module monorepo, looking up API signatures for any module, or debugging cross-module data flow issues."
prerequisites:
  required: []
  recommended: []
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-INTRA

## Instructions

### When to Use This Skill

Use `geo-infer-intra` when you need to:

- Onboard to GEO-INFER and understand the module landscape
- Wire data between two or more modules (e.g. DATA -> SPACE -> BAYES)
- Find the correct import path or API signature for any of the 44 modules
- Debug data format mismatches at module boundaries
- Locate tutorials, architecture diagrams, or integration guides

### Step-by-Step Workflow

1. **Identify the modules involved**: Determine which GEO-INFER modules your task spans. Check `docs/architecture/` for the module dependency graph.
2. **Check integration guides**: Look in `docs/integration/` for an existing pattern matching your module combination. Many common pipelines (SPACE->MATH->BAYES, DATA->AI->AGENT) are already documented.
3. **Verify data contracts**: Each module expects specific input formats. Cross-reference the API docs in `docs/api/` to confirm the output of module A matches the input of module B.
4. **Build the pipeline**: Import from each module's canonical path (`geo_infer_<module>.core.*` for algorithms, `geo_infer_<module>.api.*` for endpoints).
5. **Test the integration**: Run `uv run python -m pytest GEO-INFER-INTRA/tests/ -v` to validate cross-module flows.

### Key Directories

```text
GEO-INFER-INTRA/
├── docs/
│   ├── guides/          # How-to guides for common workflows
│   ├── tutorials/       # Step-by-step multi-module tutorials
│   ├── integration/     # Cross-module integration patterns
│   ├── architecture/    # System design and data flow diagrams
│   └── api/             # Consolidated API reference
├── src/geo_infer_intra/
│   ├── core/            # Integration logic and orchestration
│   ├── api/             # Internal API interfaces
│   ├── models/          # Shared data models
│   └── utils/           # Cross-module helpers
└── tests/               # Integration tests
```

## Examples

### Example 1: Multi-Module Geospatial Pipeline

```python
# DATA → SPACE → MATH → BAYES: load, index, analyze, model
from geo_infer_data.formats.geojson import GeoJSONLoader
from geo_infer_space.backends.h3 import H3Backend
from geo_infer_math.core.spatial_statistics import MoranI
from geo_infer_bayes.core.bayesian_inference import BayesianModel

features = GeoJSONLoader().load("observations.geojson")
cells = H3Backend().tessellate(features.bounds, resolution=7)
autocorrelation = MoranI(values, weights).compute()
posterior = BayesianModel().fit(data)
```

### Example 2: Module Discovery and Health Check

```python
# Verify which modules are installed and importable
import importlib

MODULE_NAMES = ["math", "space", "bayes", "act", "risk", "data", "ai"]
available, missing = [], []

for name in MODULE_NAMES:
    try:
        mod = importlib.import_module(f"geo_infer_{name}")
        available.append(name)
    except ImportError:
        missing.append(name)

print(f"Available: {available}")
if missing:
    print(f"Missing (install with uv): {missing}")
```

### Example 3: Cross-Module Error Handling at Boundaries

```python
# Safely chain SPACE → MATH with boundary validation
from geo_infer_space.backends.h3 import H3Backend
from geo_infer_math.core.spatial_statistics import MoranI

cells = H3Backend().tessellate(region, resolution=7)

if not cells or len(cells) == 0:
    raise ValueError("Tessellation produced no cells — check region bounds and resolution")

values = extract_values(cells)  # your extraction logic
weights = compute_spatial_weights(cells)

if values.shape[0] != weights.shape[0]:
    raise ValueError(
        f"Shape mismatch: {values.shape[0]} values vs {weights.shape[0]} weights. "
        "Ensure spatial weights match the cell count from tessellation."
    )

result = MoranI(values, weights).compute()
```

## Guidelines

### Getting Started

- Start here when onboarding to GEO-INFER; this module is the entry point for understanding the framework
- Each module's `SKILL.md` gives a quick-reference; `AGENTS.md` and `README.md` provide deeper module-level detail
- Use the data flow overview: `Data Sources → DATA → SPACE/TIME → MATH/BAYES/ACT → AI/AGENT → Domain Modules → API/APP`

### Common Pitfalls

- **Import path casing**: Most modules use lowercase (`geo_infer_math`), but environmental modules currently use mixed-case dirs (`geo_infer_FOREST`, `geo_infer_MARINE`). Check the actual package directory before importing.
- **H3 version**: SPACE and PLACE modules require `h3>=4.0.0`. Use `latlng_to_cell` / `cell_to_latlng`, not the legacy v3 API.
- **Data format mismatches**: When chaining modules, verify that the output format of one module matches the expected input of the next. GeoJSON features, H3 cell arrays, and numpy arrays are the most common interchange formats.
- **Optional dependencies**: Modules use `try/except` imports for optional deps. If a feature silently returns `None`, check whether the underlying package (e.g. `torch`, `geopandas`) is installed.

### Testing

```bash
# Run INTRA integration tests
uv run python -m pytest GEO-INFER-INTRA/tests/ -v

# Run full cross-module test suite
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
```

### Integrations

- **EXAMPLES** → Working code examples referenced from docs (`../GEO-INFER-EXAMPLES/examples/`)
- **All 44 modules** → Central hub linking documentation, API references, and integration patterns
- **TEST** → Documentation-driven testing patterns and the unified test runner
