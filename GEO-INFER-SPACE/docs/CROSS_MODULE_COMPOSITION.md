# Cross-Module H3 & Domain Composition Architecture

## 🌐 Overview

`GEO-INFER-SPACE` serves as the foundation for discrete global grid indexing (H3 v4.5+) and hierarchical spatial analytics across the entire GEO-INFER monorepo. This architecture document specifies how H3 spatial structures compose cleanly with:
- **`GEO-INFER-TIME`**: Spatiotemporal stream processing, anomaly detection, and time-series aggregation.
- **`GEO-INFER-BAYES`**: Spatial Gaussian Processes (SpatialGP), hierarchical MCMC/HMC, and Bayesian uncertainty quantification.
- **`GEO-INFER-RISK`**: Catastrophe modeling, exposure indexing, hazard mapping, and empirical Exceedance Probability (EP) curves.
- **`GEO-INFER-ACT`**: Active Inference generative models, spatial perception-action loops, and hierarchical belief diffusion.

---

## 🏗️ Architecture & Composition Data Flow

```
                     ┌───────────────────────────────┐
                     │       GEO-INFER-SPACE         │
                     │  (H3 v4.5 Spatial Indexing,   │
                     │   Nested Grids & Hierarchy)   │
                     └───────────────┬───────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │ (H3 Cell Indexing)      │ (Centroids & Neighbors) │ (H3 Discretization)
           ▼                         ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│    GEO-INFER-TIME    │  │   GEO-INFER-BAYES    │  │    GEO-INFER-RISK    │
│  - StreamProcessor   │  │  - SpatialGP (RBF)   │  │  - ExposureModel     │
│  - TimeSeries Model  │  │  - PosteriorAnalysis │  │  - Hazard Intensity  │
│  - EventDetector     │  │  - MCMC / Variational│  │  - EP & AAL Curves   │
└──────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘
           │                         │                         │
           │ (Telemetry Series)      │ (Predicted Field)       │ (Loss Probabilities)
           └─────────────────────────┼─────────────────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │        GEO-INFER-ACT          │
                     │  - ActiveInferenceModel       │
                     │  - GenerativeModel            │
                     │  - Belief Propagation & Policy│
                     └───────────────────────────────┘
```

---

## 🧩 Module Composition Patterns

### 1. SPACE + TIME Composition
- **Mechanism**: Real-time sensor observations and timestamped events are mapped to H3 indices via `SpatialIndexingInterface.latlng_to_cell(lat, lng, res)`.
- **Stream Processing**: Multi-cell buffer windows are managed using `geo_infer_time.core.stream_processing.StreamProcessor`, tracking window statistics per spatial cell.
- **Data Structure**: Standardized `TimeSeries` objects carry `spatial_location={"cell": h3_index}` metadata.

### 2. SPACE + BAYES Composition
- **Mechanism**: Cell centroids from `h3.cell_to_latlng(cell)` serve as coordinates $X \in \mathbb{R}^{N \times 2}$ for `SpatialGP` and Gaussian Process priors.
- **Spatial Kriging & Prediction**: Predictions on unobserved H3 neighborhood rings (`h3.grid_ring(center, k)`) yield mean and posterior standard deviation fields.
- **RNG Determinism**: Bayesian inference uses isolated `np.random.Generator` streams initialized via `geo_infer_bayes.utils.rng.resolve_rng`.

### 3. SPACE + RISK Composition
- **Mechanism**: Portfolios of physical assets are indexed by their containing H3 cells in `EnhancedExposureModel`.
- **Loss Modeling**: Hazard intensities sampled over the H3 grid interact with vulnerability curves to compute per-cell event losses.
- **EP Metrics**: Empirical Exceedance Probability curves are calculated using `calculate_ep_curve` with Weibull plotting positions and Poisson frequency scaling.

### 4. SPACE + ACT Composition
- **Mechanism**: Discrete state spaces in `GenerativeModel` correspond to H3 spatial grid partitions.
- **Adapter Layer**: `geo_infer_act.utils.h3_adapter.get_h3_adapter()` bridges H3 indexing seamlessly into active inference belief propagation matrices ($A, B, C, D$).
- **Multi-Scale Active Inference**: Nested H3 grids (`NestedH3Grid`) aggregate environmental free energy across parent-child resolution layers.

---

## 🧪 Integration Test Suite

The unified integration suite in `GEO-INFER-TEST/tests/integration/test_h3_space_time_bayes_risk_act_composition.py` enforces full end-to-end execution of this complete cross-module composition without mock leakage.
