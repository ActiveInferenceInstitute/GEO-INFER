# Integration Guide for GEO-INFER-MATH

## Integrating with Other GEO-INFER Modules

### Active Inference (GEO-INFER-ACT)

```
python from geo_infer_math import ActiveInferenceConvenience from geo_infer_math.integration.act import FreeEnergyCalculator # Calculate free energy fe_calc = FreeEnergyCalculator() free_energy = fe_calc.calculate(observations, beliefs) # Use convenience API act_conv = ActiveInferenceConvenience() posterior, metadata = act_conv.variational_inference(observations, prior)
```
 ### Bayesian Inference (GEO-INFER-BAYES)
```
python from geo_infer_math import BayesianConvenience from geo_infer_math.integration.bayes import PosteriorHelpers, MCMCHelpers # Calculate posterior bayes_conv = BayesianConvenience() posterior = bayes_conv.calculate_posterior(prior, likelihood, data) # MCMC sampling mcmc = MCMCHelpers() samples, metadata = mcmc.mcmc_sample(log_posterior, initial_state)
```
 ### AI/ML (GEO-INFER-AI)
```python
 from geo_infer_math import AIConvenience from geo_infer_math.integration.ai import AIGradientHelpers, SpatialLossFunctions # Compute gradients ai_conv = AIConvenience() gradient = ai_conv.compute_gradient(objective_function, parameters) # Calculate spatial loss loss_func = SpatialLossFunctions() loss = loss_func.calculate_loss(predictions, targets, coordinates)
```
 ### Information Theory Integration
```
python from geo_infer_math import InformationTheoryConvenience from geo_infer_math.core.information_theory import spatial_entropy # Calculate information measures info_conv = InformationTheoryConvenience() entropy = info_conv.calculate_entropy(data, method='shannon') mi = info_conv.calculate_mutual_information(prob_xy, prob_x, prob_y)
```
 ## Best Practices 1. **Use Convenience APIs** for common operations 2. **Use Integration Layers** for deep module integration 3. **Enable Caching** for repeated computations 4. **Configure Settings** for optimal performance 5. **Validate Inputs** before processing ## Performance Optimization 1. Enable caching for expensive operations 2. Use parallel processing for batch operations 3. Configure appropriate numerical precision 4. Use theorem proving caching for repeated proofs 5. Optimize information theory calculations with appropriate bin sizes