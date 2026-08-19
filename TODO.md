# GEO-INFER Open Task & Backlog Ledger

> Last reviewed: 2026-08-19
> Scope: Multi-package repository (`GEO-INFER`) across workspace packages and 44 domain modules.
> Centralization Rule: All planned, open, or deferred engineering work across all modules is tracked exclusively in this ledger. Module source code and tests must never carry local task markers (`TODO`, `FIXME`, `XXX`, `HACK`).

---

## 🎯 Top-Level & Package-Level Backlog

### Major Scope

| ID | Module / Package | Scope | Description & Acceptance Criteria |
|---|---|---|---|
| **ARCH-01** | `GEO-INFER-CORE` / Monorepo | Platform Wheel Distribution & Packaging | Implement unified multi-package wheel release pipeline in GitHub Actions with PyPI namespace validation. Verify package configuration discovery across isolated virtual environments without reliance on `__file__` traversal. |
| **SEC-01** | `GEO-INFER-SEC` / `DATA` / `GIT` | Cryptographic Provenance & Serialization Hardening | Define explicit HMAC/signature verification on serialized state caches and model checkpoints (AG, AI, DATA, GIT, OPS) to enforce hardened trusted-data boundaries before deserialization. |

### Medium Scope

| ID | Module / Package | Scope | Description & Acceptance Criteria |
|---|---|---|---|
| **SPACE-01** | `GEO-INFER-SPACE` | SRAI & GPU Spatial Kernel Bindings | Add optional CUDA/JAX GPU-accelerated spatial joins and H3 distance kernels while preserving zero-dependency CPU fallback semantics. |
| **TIME-01** | `GEO-INFER-TIME` | Online Spatiotemporal Streaming Pipelines | Add native WebSocket/Kafka stream ingest adapters to `StreamProcessor` with bounded watermarking, session windowing, and automated sliding-window anomaly alerts. |
| **ACT-01** | `GEO-INFER-ACT` | Continuous POMDP Active Inference | Bridge discrete categorical active inference models to continuous-time Gaussian filter Active Inference for high-frequency robotic and sensor tracking. |

### Minor Scope

| ID | Module / Package | Scope | Description & Acceptance Criteria |
|---|---|---|---|
| **MATH-01** | `GEO-INFER-MATH` | Vectorized Geometry Operations | Replace iterative point-in-polygon loops in spatial clustering with SIMD-vectorized NumPy/SciPy ray casting routines. |
| **DOCS-01** | `GEO-INFER-INTRA` | Interactive Spatial Widget Previews | Add pre-rendered Leaflet/Folium visual snapshots into MkDocs module documentation for all 44 domain modules. |
| **DATA-01** | `GEO-INFER-DATA` | Cloud-Native GeoParquet Streaming | Add chunked HTTP range-request reading for remote GeoParquet / Cloud-Optimized GeoTIFF (COG) datasets. |
| **PLACE-01** | `GEO-INFER-PLACE` | Cascadia High-Resolution Hydrography | Ingest full NHDPlus HR vector flowlines for high-order Pacific Northwest tributaries into Cascadia place-based model. |
| **TEST-01** | `GEO-INFER-TEST` | Parametric Load Testing Harness | Expand Locust / performance benchmarks to stress-test 100,000 concurrent H3 coordinate lookups across the API surface. |

---

## ✅ Completed & Verified Work (Audit Log)

1. **REPRO-01 (Completed)**: Explicit seeds use isolated `np.random.Generator` instances across `GEO-INFER-RISK` (`rng.py`), `GEO-INFER-BAYES` (`rng.py`), `GEO-INFER-MATH` (`rng.py`), and `GEO-INFER-SPM` (`rng.py`); unseeded SPM helpers retain their documented behavior, including the legacy global stream where promised.
2. **PLACE-V14 (Completed)**: Authoritative GeoJSON layers sourced, structured, and verified for Cascadia volcanoes (12 Cascade Arc stratovolcanoes), Cascadia Subduction Zone (megathrust boundary), major watersheds (Columbia, Fraser, Puget Sound, Oregon Coast), and bioregion boundary. Full pipeline verified (18/18 tests pass).
3. **SUPPLY-01 (Completed)**: Cleaned all installation references to point to verified editable installs (`uv pip install -e ./GEO-INFER-<MODULE>`).
4. **H3 v4.5 Composition (Completed)**: Implemented end-to-end multi-module composition suite (`test_h3_space_time_bayes_risk_act_composition.py`) connecting H3 spatial grids to `TIME`, `BAYES`, `RISK`, and `ACT`.
5. **BAYES-01 (Completed)**: Added batched inducing-point `SparseSpatialGP` regression with collapsed variational ELBO optimization, finite posterior uncertainty, and a 10,001-observation no-dense-covariance regression test.
6. **RISK-01 (Completed)**: Added directed multi-hazard interaction matrices and engine-level compound exceedance calculation for ordered hazard chains including earthquake to fire-following to flood.
7. **SPM-01 (Completed)**: Added full Gaussian Euler-characteristic inference across all boundary resel dimensions, peak FWE thresholds, topological cluster-extent FWE p-values, closed-form unit contracts, and fixed-seed known-null Monte Carlo calibration for both peak and cluster inference.
