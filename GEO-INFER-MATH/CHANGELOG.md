# Changelog

All notable changes to GEO-INFER-MATH are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.1.1] — 2026-02-09

### Fixed

- **Critical**: Fixed `SyntaxError` on lines 134/140 of `__init__.py`
  (`from geo_infer_math import models.regression` → `from geo_infer_math.models import regression`)
- **Critical**: Fixed `IndentationError` in `information_geometry.py` line 97
  (body of `information_metric()` was double-indented)
- **Critical**: Removed 14 stdlib modules from `requirements.txt` (e.g. `math`, `hashlib`, `threading`)
- Fixed name collision in `tensor_operations.py` (class `TensorOperations` → `SpatialTensorOperations`)
- Wrapped 4 missing API module imports in `api/__init__.py` with `try/except`

### Changed

- **Integration stubs expanded**: All 14 integration files (~10 lines each) rewritten
  with full mathematical implementations, logging, and validation:
  - `act/`: free energy, belief updating, variational inference, generative models, policy optimisation
  - `ai/`: spatial loss functions, optimisation bridges, spatial attention, spatial tensor operations
  - `bayes/`: conjugate posteriors, prior builders, MCMC, Bayesian optimisation, model selection
- Synced `setup.py` with `pyproject.toml` (added `install_requires` and optional deps)
- Updated `IMPROVEMENTS.md` from single line to structured documentation
- Updated `AGENTS.md` API examples

### Added

- `SpatialTensorOperations` class with distance tensor, adjacency tensor, and convolution kernels
- `FreeEnergyCalculator` with variational, expected, and Bethe free energy
- `BeliefUpdating` with precision-weighted prediction errors
- `VariationalInferenceHelpers` with CAVI and ELBO tracking
- `GenerativeModels` with POMDP A/B/C/D matrix construction
- `PolicyOptimization` with expected free energy minimisation
- `SpatialLossFunctions` with spatial MSE, geo-weighted loss, distance penalty
- `OptimizationBridges` with LR scheduling and gradient clipping
- `SpatialAttention` with multi-head and distance-weighted attention
- `PosteriorHelpers` with Normal-Normal, Beta-Binomial, Gamma-Poisson
- `PriorBuilders` with 6 distribution types
- `MCMCHelpers` with Metropolis-Hastings and ESS diagnostics
- `BayesianOptimization` with GP surrogate and Expected Improvement
- `ModelSelection` with BIC, AIC, AICc, WAIC, and Bayes factors

---

## [0.1.0] — 2026-01-26

### Added

- Initial release of GEO-INFER-MATH module
- Core modules: `spatial_statistics`, `computational_geometry`, `numerical_methods`,
  `linalg_tensor`, `transforms`, `theorem_prover`, `symbolic_math`, `information_theory`
- Model modules: `regression`, `clustering`
- API layer: `spatial_analysis`, `convenience`
- Integration sub-packages: `act`, `ai`, `bayes`
- Utility modules: caching, config, validation, exceptions, logging
- 8 unit test files, example scripts, documentation
