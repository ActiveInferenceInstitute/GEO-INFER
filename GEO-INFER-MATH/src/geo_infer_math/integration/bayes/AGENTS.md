# Agent
: bayes ## Scope
 This directory contains bayes components for the module. It provides 5 classes and 0 functions. ## Classes
 and Functions ### BayesianOptimizatio
n
 Bayesian optimization tools. **Methods**: - `optimize(objective, prior, **kwargs)`: ### MCMCHelper
s
 MCMC algorithm helpers. **Methods**: - `mcmc_sample(log_posterior, initial_state, **kwargs)`: ### ModelSelectio
n
 Bayesian model selection. **Methods**: - `select_model(models, data, **kwargs)`: ### PosteriorHelper
s
 Posterior distribution helpers. **Methods**: - `calculate_posterior(prior, likelihood, data, **kwargs)`: ### PriorBuilder
s
 Prior distribution construction tools. **Methods**: - `build_prior(distribution_type, **kwargs)`: ## Capabilities
 - **5 classes** for core functionality ## Integration
 - **Location**: `src/geo_infer_math/integration/bayes` - **Type**: Directory Node 