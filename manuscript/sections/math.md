## GEO-INFER-MATH — Mathematical and Statistical Engine

GEO-INFER-MATH is the core mathematical and statistical engine of GEO-INFER, providing geometric operations, spatial statistics, and numerical methods for the rest of the monorepo (per its `README.md`). Its package `geo_infer_math` organizes `api/`, `core/`, `integration/`, `models/`, and `utils/`, and at roughly 21,973 lines of Python it is one of the largest module sources in the repository.

The public interface, verified from `__init__.py`, spans four clusters. Spatial statistics: `SpatialDescriptiveStats`, `MoranI`, `GearysC`, `GetisOrd`/`getis_ord_g`, `ripley_k`, `semivariogram`, `spatial_entropy`, and `local_indicators_spatial_association`. Interpolation: `SpatialInterpolator` with `IDWInterpolator`, `KrigingInterpolator`, `RBFInterpolator`, `LinearInterpolator`, and `CubicInterpolator` behind an `InterpolationManager` factory. Optimization: `Optimizer` with gradient-descent, genetic-algorithm, SciPy, and multi-objective variants coordinated by `OptimizationManager` and helpers such as `compare_optimization_methods`. Geometry: `Point`, `LineString`, `Polygon`, `haversine_distance`, `vincenty_distance`, `bearing`, and `point_in_polygon`.

The test census counts 21 test files with 97 test classes and 318 test functions — the deepest statistical test coverage in the monorepo — exercising estimators, interpolators, and geometric primitives against reference values.

Under the root README's Module Themes, MATH belongs to Bayesian & Active Inference together with BAYES, SIM, and SPM. This placement is structural: SPM's general linear models, BAYES' generative models, and SIM's dynamics all call into MATH's estimators, making it the numerical substrate of the framework's inferential claims.
