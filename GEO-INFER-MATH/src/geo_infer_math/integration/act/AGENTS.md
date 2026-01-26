# Agent
: act ## Scope
 This directory contains act components for the module. It provides 5 classes and 0 functions. ## Classes
 and Functions ### BeliefUpdatin
g
 Belief updating for Active Inference. **Methods**: - `update(current_beliefs, new_observations, **kwargs)`: ### FreeEnergyCalculato
r
 Free energy calculations for Active Inference. **Methods**: - `calculate(observations, beliefs, **kwargs)`: ### GenerativeModel
s
 Generative model construction tools. **Methods**: - `create_generative_model(model_type, parameters, **kwargs)`: ### PolicyOptimizatio
n
 Policy optimization for Active Inference. **Methods**: - `optimize_policy(policy_function, initial_policy, **kwargs)`: ### VariationalInferenceHelper
s
 Variational inference helpers. **Methods**: - `perform_vi(observations, prior, **kwargs)`: ## Capabilities
 - **5 classes** for core functionality ## Integration
 - **Location**: `src/geo_infer_math/integration/act` - **Type**: Directory Node 