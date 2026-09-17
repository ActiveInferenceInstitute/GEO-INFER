## GEO-INFER-BAYES — Bayesian Inference and Uncertainty Quantification

**Purpose.** GEO-INFER-BAYES is the framework's probabilistic core: a comprehensive Bayesian inference framework with probabilistic modeling, uncertainty quantification, and computational methods for geospatial data. Its README frames the module as the source of principled uncertainty estimates for downstream geospatial decisions, and the module root carries rendered diagnostic figures (`mcmc_traces.png`, `posterior_distributions.png`, `uncertainty.png`, `spatial_data.png`, `mean_prediction.png`) evidencing its sampling and posterior workflows.

**Public API.** The `geo_infer_bayes` package exports Gaussian-process machinery (`GaussianProcess`, `SpatialCovariance`, and the spatial variants `SpatialGP`/`SparseSpatialGP`), inference engines (`BayesianInference`, `VariationalInference`, and `MCMC` re-exported as `MCMCSampler`), and posterior tooling via `PosteriorAnalysis`. The civic-intelligence integration exports `HazardCategoricalPrior`, `build_hazard_categorical_prior`, `build_hazard_prior_table`, and `load_crescent_city_intel`, converting structured hazard observations into categorical priors.

**Verification status.** The `tests/` directory is present with 28 test files — second only to ACT in the A–D band — covering the GP, MCMC, variational, and prior-construction layers.

**Theme role.** Inference and learning: BAYES is the uncertainty engine of the stack, feeding posterior beliefs and priors to the active inference core (ACT) and the domain sciences.
