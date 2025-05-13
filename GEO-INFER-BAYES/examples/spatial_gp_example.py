"""
Example: Spatial Gaussian Process modeling with GEO-INFER-BAYES.

This example demonstrates how to use the Gaussian Process model
for spatial interpolation and uncertainty quantification.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
import geopandas as gpd
from shapely.geometry import Point

from geo_infer_bayes.models import SpatialGP
from geo_infer_bayes.core import BayesianInference


def generate_synthetic_data(n_points=50, seed=42):
    """Generate synthetic spatial data."""
    np.random.seed(seed)
    
    # Generate random points in 2D space
    X = np.random.uniform(0, 10, size=(n_points, 2))
    
    # True lengthscale and variance
    true_lengthscale = 2.0
    true_variance = 1.5
    
    # Compute distances
    dist = np.zeros((n_points, n_points))
    for i in range(n_points):
        for j in range(n_points):
            dist[i, j] = np.sqrt(np.sum((X[i] - X[j])**2))
    
    # Compute covariance matrix (RBF kernel)
    cov = true_variance * np.exp(-0.5 * (dist / true_lengthscale)**2)
    
    # Generate random function values
    y = np.random.multivariate_normal(np.zeros(n_points), cov)
    
    # Add noise
    noise_std = 0.1
    y += np.random.normal(0, noise_std, size=n_points)
    
    return X, y, true_lengthscale, true_variance


def plot_spatial_data(X, y, title="Spatial Data"):
    """Plot spatial data with values as colors."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create colormap
    norm = Normalize(vmin=np.min(y), vmax=np.max(y))
    cmap = cm.viridis
    
    # Plot points
    scatter = ax.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap, norm=norm, s=60)
    
    # Add colorbar
    plt.colorbar(scatter, ax=ax, label="Value")
    
    ax.set_title(title)
    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    
    return fig, ax


def main():
    """Run the spatial GP example."""
    print("Generating synthetic spatial data...")
    X, y, true_lengthscale, true_variance = generate_synthetic_data(n_points=50)
    
    print(f"True lengthscale: {true_lengthscale}")
    print(f"True variance: {true_variance}")
    
    # Plot the data
    fig, ax = plot_spatial_data(X, y, title="Synthetic Spatial Data")
    plt.savefig("spatial_data.png")
    
    # Create and fit a Gaussian Process model
    print("\nFitting Gaussian Process model...")
    model = SpatialGP(
        kernel="rbf", 
        lengthscale=1.0,  # Initial guess
        variance=1.0,     # Initial guess
        noise=0.1
    )
    
    # Perform Bayesian inference
    inference = BayesianInference(model=model, method="mcmc")
    
    # Prepare data in the format expected by the model
    data = {"X": X, "y": y}
    
    # Run MCMC
    print("\nRunning MCMC sampling...")
    posterior = inference.run(
        data=data,
        n_samples=1000,
        n_warmup=500,
        thin=1
    )
    
    # Print summary statistics
    print("\nPosterior summary:")
    summary = posterior.summary()
    print(summary)
    
    # Plot traces and posterior distributions
    print("\nPlotting traces and posteriors...")
    posterior.plot_trace()
    plt.savefig("mcmc_traces.png")
    
    posterior.plot_posterior()
    plt.savefig("posterior_distributions.png")
    
    # Make predictions on a grid
    print("\nMaking spatial predictions...")
    grid_size = 30
    x_range = np.linspace(0, 10, grid_size)
    y_range = np.linspace(0, 10, grid_size)
    xx, yy = np.meshgrid(x_range, y_range)
    grid_points = np.column_stack((xx.flatten(), yy.flatten()))
    
    # Predict with uncertainty
    mean, std = posterior.predict(grid_points, return_std=True)
    
    # Reshape for plotting
    mean_grid = mean.reshape(grid_size, grid_size)
    std_grid = std.reshape(grid_size, grid_size)
    
    # Plot mean prediction
    fig, ax = plt.subplots(figsize=(10, 8))
    contour = ax.contourf(xx, yy, mean_grid, cmap="viridis", levels=20)
    plt.colorbar(contour, ax=ax, label="Predicted value")
    ax.scatter(X[:, 0], X[:, 1], c='white', edgecolor='black', s=40, label="Data points")
    ax.set_title("Mean Prediction")
    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    plt.savefig("mean_prediction.png")
    
    # Plot standard deviation (uncertainty)
    fig, ax = plt.subplots(figsize=(10, 8))
    contour = ax.contourf(xx, yy, std_grid, cmap="plasma", levels=20)
    plt.colorbar(contour, ax=ax, label="Standard deviation")
    ax.scatter(X[:, 0], X[:, 1], c='white', edgecolor='black', s=40, label="Data points")
    ax.set_title("Prediction Uncertainty")
    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    plt.savefig("uncertainty.png")
    
    print("\nExample completed. Results saved as PNG files.")


if __name__ == "__main__":
    main() 