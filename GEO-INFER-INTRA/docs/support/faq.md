# Frequently Asked Questions (FAQ)

This FAQ addresses common questions about GEO-INFER. If you don't find your
answer here, check the [troubleshooting guides](index.md) or open an issue in
the [GEO-INFER repository](https://github.com/ActiveInferenceInstitute/GEO-INFER/issues).

## Getting Started

### Q: What is GEO-INFER?

**A:** GEO-INFER is a 44-module geospatial inference monorepo combining spatial
analysis (H3 v4 indexing), probabilistic inference, and Active Inference for
domain modeling, agent workflows, and repository validation. See the
[repository overview](../overview.md) and the [module catalog](../modules/index.md).

### Q: What are the system requirements?

**A:**

- **Python**: 3.11+ (see `.python-version` and the root `pyproject.toml`).
- **Package manager**: `uv` (the repository is a uv workspace).
- **Supported OS**: Linux, macOS, Windows (CI runs on CPU runners; some
  native-only extras are omitted there — see `.github/workflows/ci.yml`).

### Q: How do I install GEO-INFER?

**A:** Clone the repository and sync the workspace:

```bash
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER
uv sync --all-packages --all-extras
```

For a single module, sync just that package:

```bash
uv sync --package geo-infer-act
```

See the [Installation Guide](../getting_started/installation_guide.md) for
details, including the CI extras exception list.

### Q: Can I use GEO-INFER with my existing data?

**A:** Yes. The framework supports many common formats through its I/O and
H3 backends:

- **Vector**: GeoJSON, Shapefile, GeoPackage, TopoJSON
- **Raster**: GeoTIFF, Cloud Optimized GeoTIFF, NetCDF
- **Tabular**: CSV, Parquet, Excel with spatial columns
- **Time series**: CSV with timestamps, NetCDF with time dimension

## Technical Questions

### Q: Why is my spatial analysis running slowly?

**A:** Common causes and solutions:

1. **Large datasets**: use H3 indexing and chunked processing.
2. **Missing indexes**: index cells with `latlng_to_cell` / `polygon_to_cells`
   from `geo_infer_space` before repeated lookups.
3. **Memory pressure**: reduce chunk size or stream input data.
4. **Complex geometries**: simplify geometries or use approximate methods.

### Q: How do I handle missing data in my analysis?

**A:** Use the data handling tools in `geo_infer_data` and the underlying
libraries (pandas, numpy). Drop or interpolate missing values before fitting:

```python
import pandas as pd

df = pd.read_csv("observations.csv")
clean = df.dropna()
```

### Q: My active inference model isn't converging. What should I do?

**A:** Try these debugging steps:

1. **Check data quality**: ensure no NaN values or extreme outliers.
2. **Adjust precision**: lower precision for more exploration, higher for
   exploitation.
3. **Normalize features**: scale inputs to similar ranges.
4. **Increase iterations**: allow more time for convergence.
5. **Check model specification**: ensure state and observation spaces match the
   data. See the [Active Inference guide](../active_inference_guide.md) and
   the [research-grade inference contracts](../research_grade_inference_contracts.md).

### Q: How do I handle coordinate system issues?

**A:** Standardize on one coordinate reference system (CRS) per analysis. The
SPACE module documents coordinate handling in
[Coordinate Systems](../geospatial/concepts/coordinate_systems.md) and
[Spatial Reference Systems](../geospatial/concepts/spatial_reference_systems.md);
the underlying projection libraries (pyproj) are used for transforms.

### Q: Can I use GPU acceleration?

**A:** GPU execution is not part of the supported release contract. Optional
integrations (for example PyMC backends) must be reported separately with
their prerequisites; see `AGENTS.md` and the TODO release-gate notes.

## Data Analysis

### Q: How do I perform spatial analysis?

**A:** Use the SPACE module's public interfaces:

```python
from geo_infer_space import SpatialIndexingInterface, SpatialAnalyticsInterface

indexer = SpatialIndexingInterface()
latlng_to_cell(37.7749, -122.4194, 9)  # returns an H3 cell id
```

See the [H3 guide](../geospatial/data_formats/h3/index.md) for the current
v4 API and the [SPACE module page](../modules/geo-infer-space.md).

### Q: How do I analyze temporal patterns?

**A:** Use the TIME module:

```python
from geo_infer_time import TemporalAnalyzer

analyzer = TemporalAnalyzer()
```

See the [Temporal analysis guide](../temporal_analysis_guide.md) and the
[TIME module page](../modules/geo-infer-time.md).

### Q: How do I create interactive maps?

**A:** Visualization guidance lives in the
[geospatial visualization section](../geospatial/visualization/index.md) and
the module examples under `GEO-INFER-*/examples/`. Map rendering uses standard
Python plotting libraries; see the
[examples gallery](../examples_gallery.md).

### Q: How do I handle datasets that don't fit in memory?

**A:** Use chunked processing and stream inputs where the underlying I/O layer
supports it (`geo_infer_data`), or process by H3 region. See the
[Data Management](../knowledge_base/best_practices/index.md) best practices.

## Active Inference

### Q: What is active inference?

**A:** Active inference is a framework that models perception, learning, and
decision-making as processes of minimizing free energy — the difference between
an agent's model of the world and its sensory experience. In GEO-INFER this
enables adaptive geospatial analysis. See the
[Active Inference basics](../getting_started/active_inference_basics.md) and
the [Active Inference guide](../active_inference_guide.md).

### Q: How do I build an active inference model?

**A:** Start with a simple categorical model from the ACT module:

```python
from geo_infer_act import ActiveInferenceModel

model = ActiveInferenceModel(
    state_space=['temperature', 'humidity'],
    observation_space=['sensor_reading'],
    precision=1.0,
)
model.update_beliefs({'sensor_reading': 25.5})
```

Run `GEO-INFER-ACT/examples` for end-to-end scripts.

### Q: How do I tune active inference parameters?

**A:** Key parameters to adjust:

- **Precision**: controls exploration vs exploitation.
- **Learning rate**: how quickly beliefs update.
- **Planning horizon**: how far ahead to plan.

### Q: How do I quantify uncertainty in predictions?

**A:** Uncertainty quantification is a release contract of the ACT, BAYES, and
RISK modules. See
[Research-grade inference contracts](../research_grade_inference_contracts.md)
for executable behavior and verification commands.

## Integration and API

### Q: How do I integrate GEO-INFER with my existing workflow?

**A:** Several integration options exist:

1. **Python API**: direct import and use in Python scripts.
2. **REST API**: HTTP endpoints from the API module (`geo_infer_api`).
3. **Docker containers**: containerized deployment.
4. **Jupyter notebooks**: interactive analysis environment.

See the [Integration guide](../integration/index.md).

### Q: Can I use GEO-INFER with other geospatial libraries?

**A:** Yes. The framework integrates with GeoPandas, Rasterio, Shapely,
matplotlib, and related libraries through the SPACE backends; H3 v4 is the
native hierarchical grid (see the [H3 guide](../geospatial/data_formats/h3/index.md)).

### Q: How do I deploy GEO-INFER in production?

**A:** See the [Deployment Guide](../deployment/index.md) and the
[Production Architecture](../advanced/production_architecture.md) page.

## Troubleshooting

### Q: I get "ImportError: No module named 'geo_infer_space'" — what's wrong?

**A:** This usually means:

1. **Installation incomplete**: run `uv sync --all-packages --all-extras` from
   the repository root.
2. **Wrong Python environment**: activate the uv virtual environment.
3. **Version mismatch**: pull the latest `main` and re-sync.

### Q: How do I report a bug?

**A:** Report bugs through the
[GitHub Issues](https://github.com/ActiveInferenceInstitute/GEO-INFER/issues)
tracker. Include the module, the exact command, and the error output.

## Still Need Help?

If you didn't find your answer here:

1. Search the [main documentation](../index.md).
2. Check the [troubleshooting guides](index.md).
3. Open an [issue](https://github.com/ActiveInferenceInstitute/GEO-INFER/issues).

Pro tip: many questions are answered in the [examples gallery](../examples_gallery.md)
and the [support index](index.md). Check those first.
