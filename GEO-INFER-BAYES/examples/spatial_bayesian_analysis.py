#!/usr/bin/env python3
"""
GEO-INFER-BAYES Example: Spatial Bayesian Analysis

This example demonstrates Bayesian analysis for geospatial data
including spatial regression, hierarchical models, and uncertainty quantification.
"""

import numpy as np

from geo_infer_bayes import (
    BayesianInference,
    SpatialModel,
    PosteriorAnalysis,
    ModelComparison
)


def main():
    print("=" * 60)
    print("GEO-INFER-BAYES: Spatial Bayesian Analysis")
    print("=" * 60)
    
    # 1. Generate Synthetic Spatial Data
    print("\n1. Generating Synthetic Spatial Data...")
    np.random.seed(42)
    
    n_locations = 100
    locations = {
        'x': np.random.uniform(0, 100, n_locations),
        'y': np.random.uniform(0, 100, n_locations),
    }
    
    # True parameters
    true_intercept = 5.0
    true_slope = 2.5
    true_spatial_range = 20.0
    true_noise = 1.0
    
    # Generate spatially correlated data
    covariate = np.random.uniform(0, 10, n_locations)
    spatial_effect = np.random.normal(0, 2, n_locations)
    noise = np.random.normal(0, true_noise, n_locations)
    
    y = true_intercept + true_slope * covariate + spatial_effect + noise
    
    data = {
        'locations': locations,
        'covariate': covariate,
        'response': y
    }
    
    print(f"   Locations: {n_locations}")
    print(f"   Response mean: {np.mean(y):.2f}, std: {np.std(y):.2f}")
    
    # 2. Define Bayesian Spatial Model
    print("\n2. Defining Bayesian Spatial Model...")
    model = SpatialModel(
        model_type='spatial_regression',
        spatial_effect='gp',  # Gaussian Process
        correlation_function='matern'
    )
    
    model.set_priors(
        intercept={'type': 'normal', 'mean': 0, 'std': 10},
        slope={'type': 'normal', 'mean': 0, 'std': 5},
        spatial_range={'type': 'gamma', 'shape': 2, 'rate': 0.1},
        spatial_variance={'type': 'halfnormal', 'std': 5},
        noise_variance={'type': 'halfnormal', 'std': 2}
    )
    
    print(f"   Model type: {model.model_type}")
    print(f"   Spatial effect: {model.spatial_effect}")
    print(f"   Priors configured: 5 parameters")
    
    # 3. Run MCMC Inference
    print("\n3. Running MCMC Inference...")
    inference = BayesianInference(
        model=model,
        method='hmc',
        sampler_config={
            'num_samples': 2000,
            'num_warmup': 1000,
            'num_chains': 2
        }
    )
    
    posterior = inference.run(
        data=data,
        progress_bar=True
    )
    
    print(f"   Samples collected: {posterior.num_samples}")
    print(f"   Chains: {posterior.num_chains}")
    print(f"   Effective sample size: {posterior.ess_min:.0f}")
    
    # 4. Posterior Analysis
    print("\n4. Analyzing Posterior Distribution...")
    summary = posterior.summary()
    
    print("\n   Parameter Estimates:")
    print(f"   {'Parameter':<20} {'Mean':>10} {'Std':>10} {'95% CI':>20}")
    print(f"   {'-'*60}")
    
    for param, stats in summary.items():
        mean = stats.get('mean', 0)
        std = stats.get('std', 0)
        ci_low = stats.get('hdi_3%', mean - 2*std)
        ci_high = stats.get('hdi_97%', mean + 2*std)
        print(f"   {param:<20} {mean:>10.3f} {std:>10.3f} [{ci_low:>7.3f}, {ci_high:>7.3f}]")
    
    # 5. Model Diagnostics
    print("\n5. Running Diagnostics...")
    diagnostics = posterior.diagnostics()
    
    print(f"   R-hat (max): {diagnostics.get('rhat_max', 0):.4f}")
    print(f"   ESS (min): {diagnostics.get('ess_min', 0):.0f}")
    print(f"   Divergences: {diagnostics.get('divergences', 0)}")
    print(f"   Convergence: {'✓ Good' if diagnostics.get('converged', False) else '✗ Warning'}")
    
    # 6. Posterior Predictive Check
    print("\n6. Posterior Predictive Check...")
    ppc = posterior.predictive_check(data['response'])
    
    print(f"   p-value: {ppc.get('p_value', 0):.3f}")
    print(f"   Mean residual: {ppc.get('mean_residual', 0):.3f}")
    print(f"   RMSE: {ppc.get('rmse', 0):.3f}")
    
    # 7. Spatial Prediction
    print("\n7. Making Spatial Predictions...")
    
    # New prediction locations
    pred_locations = {
        'x': np.linspace(0, 100, 20),
        'y': np.linspace(0, 100, 20)
    }
    pred_covariate = np.random.uniform(0, 10, 20)
    
    predictions = posterior.predict(
        new_locations=pred_locations,
        new_covariates={'covariate': pred_covariate},
        return_uncertainty=True
    )
    
    print(f"   Prediction locations: {len(pred_locations['x'])}")
    print(f"   Mean prediction: {np.mean(predictions['mean']):.2f}")
    print(f"   Mean uncertainty (std): {np.mean(predictions['std']):.2f}")
    
    # 8. Model Comparison
    print("\n8. Comparing Alternative Models...")
    
    # Define alternative model (no spatial effect)
    model_nospatial = SpatialModel(
        model_type='linear_regression',
        spatial_effect=None
    )
    
    model_nospatial.set_priors(
        intercept={'type': 'normal', 'mean': 0, 'std': 10},
        slope={'type': 'normal', 'mean': 0, 'std': 5},
        noise_variance={'type': 'halfnormal', 'std': 2}
    )
    
    inference_nospatial = BayesianInference(
        model=model_nospatial,
        method='hmc'
    )
    
    posterior_nospatial = inference_nospatial.run(data=data)
    
    # Compare models
    comparison = ModelComparison(
        models=[model, model_nospatial],
        posteriors=[posterior, posterior_nospatial],
        method='waic'
    )
    
    results = comparison.compare()
    
    print("\n   Model Comparison (WAIC):")
    print(f"   {'Model':<25} {'WAIC':>10} {'dWAIC':>10} {'Weight':>10}")
    print(f"   {'-'*55}")
    for model_name, stats in results.items():
        print(f"   {model_name:<25} {stats['waic']:>10.1f} {stats['dwaic']:>10.1f} {stats['weight']:>10.3f}")
    
    print("\n" + "=" * 60)
    print("Bayesian Analysis Complete!")
    print("=" * 60)
    
    # Summary
    print("\nKey Results:")
    print(f"  - Intercept estimate: {summary.get('intercept', {}).get('mean', 0):.3f} (true: {true_intercept})")
    print(f"  - Slope estimate: {summary.get('slope', {}).get('mean', 0):.3f} (true: {true_slope})")
    print(f"  - Spatial model preferred: {'Yes' if results.get('spatial_regression', {}).get('weight', 0) > 0.5 else 'No'}")


if __name__ == "__main__":
    main()
