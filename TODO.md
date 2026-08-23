# GEO-INFER Open Task & Backlog Ledger

> Last reviewed: 2026-08-20
> Scope: Multi-package repository (`GEO-INFER`) across workspace packages and 44 domain modules.
> Centralization Rule: All planned, open, or deferred engineering work across all modules is tracked exclusively in this ledger. Module source code and tests must never carry local task markers (`TODO`, `FIXME`, `XXX`, `HACK`).

---

## 🎯 Top-Level & Package-Level Backlog

### Major Scope

| ID | Module / Package | Scope | Description & Acceptance Criteria |
|---|---|---|---|
| ~~**ARCH-01**~~ | `GEO-INFER-CORE` / Monorepo | Platform Wheel Distribution & Packaging | **Completed**: Unified multi-package wheel release pipeline in GitHub Actions (`.github/workflows/release.yml`) with strict PyPI `geo-infer-*` namespace validation (`GEO-INFER-TEST/validate_packaging.py`), a wheel-build driver (`build_package_wheels.py`) that builds/validates every module wheel and optionally smoke-installs into isolated venvs, and per-module `[tool.setuptools.package-data]` so YAML/JSON config ships with wheels. Out-of-package `__file__` traversal is reported as diagnostics for installed-wheel-safe migration. CI runs `validate_packaging.py --strict`. |

### Medium Scope

| ID | Module / Package | Scope | Description & Acceptance Criteria |
|---|---|---|---|
| **SPACE-01** | `GEO-INFER-SPACE` | SRAI & GPU Spatial Kernel Bindings | Add optional CUDA/JAX GPU-accelerated spatial joins and H3 distance kernels while preserving zero-dependency CPU fallback semantics. |
| **TIME-01** | `GEO-INFER-TIME` | Online Spatiotemporal Streaming Pipelines | Add native WebSocket/Kafka stream ingest adapters to `StreamProcessor` with bounded watermarking, session windowing, and automated sliding-window anomaly alerts. |

### Minor Scope

| ID | Module / Package | Scope | Description & Acceptance Criteria |
|---|---|---|---|
| **DOCS-01** | `GEO-INFER-INTRA` | Interactive Spatial Widget Previews | Add pre-rendered Leaflet/Folium visual snapshots into MkDocs module documentation for all 44 domain modules. |
| **PLACE-01** | `GEO-INFER-PLACE` | Cascadia High-Resolution Hydrography | Ingest full NHDPlus HR vector flowlines for high-order Pacific Northwest tributaries into Cascadia place-based model. |

---

## ✅ Completed & Verified Work (Audit Log)

1. **REPRO-01 (Completed)**: Explicit seeds use isolated `np.random.Generator` instances across `GEO-INFER-RISK` (`rng.py`), `GEO-INFER-BAYES` (`rng.py`), `GEO-INFER-MATH` (`rng.py`), and `GEO-INFER-SPM` (`rng.py`); unseeded SPM helpers retain their documented behavior, including the legacy global stream where promised.
2. **PLACE-V14 (Completed)**: Authoritative GeoJSON layers sourced, structured, and verified for Cascadia volcanoes (12 Cascade Arc stratovolcanoes), Cascadia Subduction Zone (megathrust boundary), major watersheds (Columbia, Fraser, Puget Sound, Oregon Coast), and bioregion boundary. Full pipeline verified (18/18 tests pass).
3. **SUPPLY-01 (Completed)**: Cleaned all installation references to point to verified editable installs (`uv pip install -e ./GEO-INFER-<MODULE>`).
4. **H3 v4.5 Composition (Completed)**: Implemented end-to-end multi-module composition suite (`test_h3_space_time_bayes_risk_act_composition.py`) connecting H3 spatial grids to `TIME`, `BAYES`, `RISK`, and `ACT`.
5. **BAYES-01 (Completed)**: Added batched inducing-point `SparseSpatialGP` regression with collapsed variational ELBO optimization, finite posterior uncertainty, and a 10,001-observation no-dense-covariance regression test.
6. **RISK-01 (Completed)**: Added directed multi-hazard interaction matrices and engine-level compound exceedance calculation for ordered hazard chains including earthquake to fire-following to flood.
7. **SPM-01 (Completed)**: Added full Gaussian Euler-characteristic inference across all boundary resel dimensions, peak FWE thresholds, topological cluster-extent FWE p-values, closed-form unit contracts, and fixed-seed known-null Monte Carlo calibration for both peak and cluster inference.
8. **SEC-01 (Completed)**: Added authenticated GISP1 HMAC-SHA256 serialization envelopes across `DATA` (`utils/secure_serialization.py`, `caching`, `storage`), `GIT` (`utils/secure_serialization.py`, `advanced_cache`), and `OPS` (`core/secure_serialization.py`, `cache`), with SEC integration coverage (`tests/integration/test_serialization_security.py`); unsigned, truncated, cross-context, and tampered payloads never reach a deserializer.
9. **ACT-01 (Completed)**: Added continuous POMDP Active Inference via a Laplace/Kalman-Bucy filter (`models/continuous_pomdp.py`) bridging discrete categorical and continuous-state Gaussian-filter inference, with free-energy-scored action selection and a focused unit test.
10. **MATH-01 (Completed)**: Added vectorized SIMD ray-casting point-in-polygon (`geometry.points_in_polygon_vectorized`) replacing iterative loops in spatial clustering.
11. **DATA-01 (Completed)**: Added cloud-connector byte-range reading (`connectors/cloud.py` `read_byte_range`) for chunked remote GeoParquet / Cloud-Optimized GeoTIFF access.
12. **TEST-01 (Completed)**: Added the parametric load benchmark harness (`tests/unit/test_parametric_load_benchmarks.py`) to the unified test runner's performance surface.
