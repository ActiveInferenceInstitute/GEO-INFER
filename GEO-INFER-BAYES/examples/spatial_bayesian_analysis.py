#!/usr/bin/env python3
"""GEO-INFER-BAYES example: spatial Bayesian analysis end to end.

Walks the full workflow against the implemented public API:

1. Simulate data from a known Gaussian process, so the posterior can be
   checked against ground truth.
2. Sample the GP hyperparameter posterior with the Metropolis MCMC backend.
3. Summarize the posterior and check convergence with R-hat and ESS.
4. Predict at held-out locations with calibrated uncertainty.
5. Compare a correctly specified model against a misspecified one by LOO.

Every draw comes from an explicit ``numpy.random.Generator``, so the run is
reproducible from ``SEED`` alone and never touches the process-wide
``numpy.random`` stream.
"""

from __future__ import annotations

import numpy as np

from geo_infer_bayes import BayesianInference, SpatialGP
from geo_infer_bayes.core.model_comparison import ModelComparison
from geo_infer_bayes.utils.diagnostics import mcmc_diagnostics

SEED = 42
N_TRAIN = 60
N_TEST = 40
TRUE_LENGTHSCALE = 2.0
TRUE_VARIANCE = 1.5
TRUE_NOISE = 0.1


def simulate_gp_field(
    n_points: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Draw a realization of a known RBF Gaussian process with noise.

    Args:
        n_points: Number of locations to draw.
        rng: Generator supplying every draw.

    Returns:
        Tuple of ``(X, y)`` with ``X`` of shape ``(n_points, 2)`` and ``y`` of
        shape ``(n_points,)``.
    """
    X = rng.uniform(0, 10, size=(n_points, 2))
    sq_dist = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=-1)
    cov = TRUE_VARIANCE * np.exp(-0.5 * sq_dist / TRUE_LENGTHSCALE**2)
    # Jitter keeps the covariance positive definite for the Cholesky factor.
    cov += np.eye(n_points) * 1e-8
    y = rng.multivariate_normal(np.zeros(n_points), cov)
    return X, y + rng.normal(0, TRUE_NOISE, size=n_points)


def log_likelihood_matrix(
    model: SpatialGP, samples: dict, X: np.ndarray, y: np.ndarray, n_draws: int = 100
) -> np.ndarray:
    """Build the pointwise log-likelihood matrix that LOO and WAIC require.

    Args:
        model: Model whose pointwise log-likelihood is evaluated.
        samples: Posterior draws keyed by parameter name.
        X: Observation locations.
        y: Observed values.
        n_draws: Number of posterior draws to evaluate.

    Returns:
        Array of shape ``(n_draws, len(y))``.
    """
    names = ["lengthscale", "variance", "noise"]
    available = min(len(samples[name]) for name in names)
    # Spread the draws across the chain rather than taking its front.
    indices = np.linspace(0, available - 1, num=min(n_draws, available), dtype=int)
    return np.asarray(
        [
            model.pointwise_log_likelihood(
                {name: float(samples[name][i]) for name in names}, {"X": X, "y": y}
            )
            for i in indices
        ]
    )


def main() -> None:
    """Run the spatial Bayesian analysis walkthrough."""
    rng = np.random.default_rng(SEED)

    print("=" * 60)
    print("GEO-INFER-BAYES: Spatial Bayesian Analysis")
    print("=" * 60)

    print("\n1. Simulating a spatial field from a known GP")
    X, y = simulate_gp_field(N_TRAIN + N_TEST, rng)
    X_train, y_train = X[:N_TRAIN], y[:N_TRAIN]
    X_test, y_test = X[N_TRAIN:], y[N_TRAIN:]
    print(f"   train / test locations : {N_TRAIN} / {N_TEST}")
    print(f"   response mean, sd      : {y_train.mean():.2f}, {y_train.std():.2f}")
    print(
        f"   truth                  : lengthscale={TRUE_LENGTHSCALE}, "
        f"variance={TRUE_VARIANCE}, noise={TRUE_NOISE}"
    )

    print("\n2. Sampling the hyperparameter posterior with MCMC")
    model = SpatialGP(kernel="rbf", lengthscale=1.0, variance=1.0, noise=0.5)
    inference = BayesianInference(
        model=model,
        method="mcmc",
        sampler_config={"n_chains": 4, "random_seed": SEED},
    )
    posterior = inference.run(
        data={"X": X_train, "y": y_train},
        n_samples=2000,
        n_warmup=1000,
        progress_bar=False,
    )

    print("\n3. Posterior summary")
    print(posterior.summary()[["mean", "sd", "hdi_3%", "hdi_97%"]].to_string())

    # R-hat is a between-chain statistic, so it needs the draws split back out
    # per chain rather than the pooled array used for prediction.
    diagnostics = mcmc_diagnostics(posterior.chain_samples())
    print("\n4. Convergence diagnostics")
    worst_r_hat = 0.0
    for name in ("lengthscale", "variance", "noise"):
        stats = diagnostics[name]
        worst_r_hat = max(worst_r_hat, stats["r_hat"])
        print(f"   {name:<12} r_hat={stats['r_hat']:.3f}  ess={stats['ess']:.0f}")
    if worst_r_hat < 1.01:
        print(f"   converged: worst r_hat {worst_r_hat:.3f} < 1.01")
    else:
        print(
            f"   NOT converged: worst r_hat {worst_r_hat:.3f} >= 1.01; "
            "lengthen the chains before trusting these estimates"
        )

    print("\n5. Predicting at held-out locations")
    mean, std = model.predict(X_test, posterior=posterior, samples=200, return_std=True)
    residual = y_test - mean
    rmse = float(np.sqrt(np.mean(residual**2)))
    # std is latent-function uncertainty; an observation also carries noise, so
    # the interval that should cover y_test widens by the posterior noise sd.
    noise_sd = float(np.sqrt(np.mean(posterior.samples["noise"])))
    total_sd = np.sqrt(std**2 + noise_sd**2)
    covered = float(np.mean(np.abs(residual) <= 1.96 * total_sd))
    print(f"   RMSE                     : {rmse:.3f}")
    print(f"   sd of the held-out field : {y_test.std():.3f}")
    print(f"   mean predictive sd       : {total_sd.mean():.3f}")
    print(f"   95% interval coverage    : {covered:.0%} (nominal 95%)")

    print("\n6. Comparing against a misspecified model by LOO")
    # An exponential kernel is far rougher than the RBF field that generated the
    # data. A correct comparison must prefer the RBF model. Each model gets its
    # own pointwise log-likelihood matrix -- passing one model's matrix for both
    # would make the comparison vacuous.
    wrong = SpatialGP(kernel="exponential", lengthscale=1.0, variance=1.0, noise=0.5)
    wrong.fit(X_train, y_train)
    model.name, wrong.name = "gp_rbf", "gp_exponential"

    for candidate in (model, wrong):
        comparison = ModelComparison([candidate])
        result = comparison.compare_models(
            {
                "log_likelihood_matrix": log_likelihood_matrix(
                    candidate, posterior.samples, X_train, y_train
                )
            },
            method="loo",
            random_seed=SEED,
        )[candidate.name]
        print(
            f"   {candidate.name:<16} elpd_loo={result['elpd_loo']:>9.2f}  "
            f"p_loo={result['p_loo']:>6.2f}"
        )

    print("\n" + "=" * 60)
    print("Analysis complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
