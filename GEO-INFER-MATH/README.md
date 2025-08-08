# GEO-INFER-MATH

**Foundational Mathematical Library for Geospatial Analysis and Inference**

## Overview

GEO-INFER-MATH serves as the **core mathematical and statistical engine** for the entire GEO-INFER framework. It provides a comprehensive suite of specialized mathematical tools, algorithms, statistical methods, and geometric operations specifically designed and optimized for processing, analyzing, and making inferences from geospatial data. This module underpins the quantitative capabilities of all other GEO-INFER modules, ensuring rigorous, accurate, and efficient computation for a wide range of spatial and spatio-temporal applications. Its scope ranges from fundamental geometric calculations and coordinate transformations to advanced spatial statistics, machine learning model components, and numerical methods.

### Documentation
- Module page: ../GEO-INFER-INTRA/docs/modules/geo-infer-math.md
- Modules index: ../GEO-INFER-INTRA/docs/modules/index.md

## Core Objectives

-   **Provide Robust Mathematical Foundations:** Offer a reliable and extensively tested set of mathematical and statistical functions tailored for geospatial data.
-   **Enable Advanced Geospatial Analysis:** Equip other GEO-INFER modules with the necessary tools for sophisticated spatial pattern analysis, modeling, and inference.
-   **Ensure Computational Efficiency:** Implement algorithms and operations optimized for performance with potentially large and complex geospatial datasets.
-   **Promote Standardization:** Offer a consistent mathematical API and common utility functions to be used across the GEO-INFER framework, reducing redundancy and improving interoperability.
-   **Facilitate Quantitative Modeling:** Supply the building blocks for constructing and evaluating complex geospatial models, including statistical, physics-based, and machine learning models.
-   **Support Diverse Data Types:** Handle various forms of geospatial data representations, including vector, raster, point clouds, and networks, from a mathematical perspective.

## Key Features

### 1. Advanced Spatial Statistics
-   **Description:** A comprehensive toolkit for analyzing spatial patterns, distributions, autocorrelation, and relationships within geospatial datasets.
-   **Techniques/Examples:**
    -   Spatial autocorrelation: Moran's I, Geary's C, Getis-Ord Gi*.
    -   Point pattern analysis: Ripley's K-function, L-function, nearest neighbor analysis.
    -   Geostatistics: Variography, kriging (Ordinary, Universal, Co-kriging), conditional simulation.
    -   Spatial regression models: SAR, CAR, GWR components.
-   **Benefits:** Quantify spatial dependencies, identify clusters and outliers, interpolate values in unsampled locations, and model relationships that vary over space.

### 2. Comprehensive Geometric Operations
-   **Description:** A wide array of functions for performing calculations and manipulations related to geometric shapes and spatial relationships in 2D and 3D.
-   **Techniques/Examples:**
    -   Distance and area calculations (Euclidean, Haversine, on various projections).
    -   Topological operations: intersections, unions, differences, buffering, convex hulls.
    -   Geometric predicates: contains, within, touches, overlaps.
    -   Shape analysis: centroid, orientation, compact_cellsness, fractal dimension.
-   **Benefits:** Enables precise measurement, spatial querying, feature manipulation, and characterization of geographic entities.

### 3. Robust Coordinate Systems & Transformations
-   **Description:** Tools for defining, interpreting, and converting coordinates between various geographic and projected coordinate reference systems (CRS).
-   **Techniques/Examples:**
    -   Support for EPSG codes and PROJ string definitions.
    -   Forward and inverse projection logic for common map projections (e.g., UTM, Mercator, Albers Equal Area).
    -   Datum transformations.
    -   Integration with `pyproj` or similar underlying libraries.
-   **Benefits:** Ensures geospatial data from different sources can be accurately aligned and analyzed in a common spatial framework.

### 4. Numerical Methods & Optimization
-   **Description:** Specialized numerical algorithms for solving mathematical problems arising in geospatial contexts, including optimization, interpolation, and solving differential equations.
-   **Techniques/Examples:**
    -   Spatial interpolation: Inverse Distance Weighting (IDW), spline interpolation, Natural Neighbor.
    -   Optimization algorithms for routing, facility location, or parameter estimation in spatial models.
    -   Solvers for PDEs describing flow, diffusion, or wave propagation in spatial domains.
    -   Numerical integration and differentiation for spatial fields.
-   **Benefits:** Provides the computational backbone for complex modeling tasks, parameter estimation, and finding optimal solutions to spatial problems.

### 5. Multi-dimensional Data Analysis (Tensor Operations)
-   **Description:** Functions and structures for handling and analyzing multi-dimensional geospatial data, such as spatio-temporal raster stacks or multi-spectral imagery.
-   **Techniques/Examples:**
    -   Tensor algebra ( leveraging libraries like NumPy, Xarray, PyTorch/TensorFlow where appropriate).
    -   Dimensionality reduction techniques for spatio-temporal data (e.g., EOF, PCA adapted for spatial data).
    -   Convolution and filtering operations on spatial grids.
-   **Benefits:** Enables analysis of complex, multi-faceted geospatial datasets, including time series of maps or hyperspectral data.

### 6. Mathematical Building Blocks for Machine Learning
-   **Description:** Provides foundational mathematical components utilized in the development and implementation of machine learning models for geospatial data within GEO-INFER-AI or other modules.
-   **Techniques/Examples:**
    -   Distance metrics for spatial feature spaces.
    -   Kernel functions adapted for spatial data.
    -   Components for spatial cross-validation.
    -   Mathematical formalisms for graph neural networks on spatial networks.
-   **Benefits:** Supports the development of specialized AI/ML solutions tailored to the unique characteristics of geospatial information.

## Module Architecture & Interdependencies

As a foundational library, GEO-INFER-MATH is primarily structured into sub-modules based on mathematical domains. Its "architecture" is less about a processing pipeline and more about a well-organized toolbox.

```mermaid
graph TD
    subgraph Core_Mathematical_Domains as "GEO-INFER-MATH Core Domains"
        GEOM[geometry.py - Geometric Operations & Primitives]
        SPAT_STATS[spatial_statistics.py - Descriptive & Inferential Stats]
        CRS_TRANS[transforms.py - Coordinate Systems & Projections]
        NUM_METH[numerical_methods.py - Interpolation, Optimization, Solvers]
        LINALG_TENSOR[linalg_tensor.py - Linear Algebra, Tensor Ops for Spatial Data]
        GRAPH_THEORY[graph_theory.py - Mathematical Graph Ops for Networks]
    end

    subgraph Utility_Layer as "Utilities & Common Functions"
        MATH_UTILS[utils.py - Common Math Helpers, Constants]
        VALIDATORS[validators.py - Input Data Validation for Math Ops]
    end

    subgraph Interfaces as "API & Integration Points"
        API_MATH[api/ - Simplified Facades for Common Workflows]
    end

    %% Domain Interdependencies (Conceptual)
    GEOM --> SPAT_STATS %% Stats often need geometric properties
    CRS_TRANS --> GEOM %% Geometry is CRS-dependent
    LINALG_TENSOR --> SPAT_STATS %% Many stats methods use linear algebra
    LINALG_TENSOR --> NUM_METH %% Numerical methods often use matrix ops
    GRAPH_THEORY --> SPAT_STATS %% Network-based spatial stats

    %% Utilities supporting domains
    MATH_UTILS --> GEOM; MATH_UTILS --> SPAT_STATS; MATH_UTILS --> NUM_METH
    VALIDATORS --> GEOM; VALIDATORS --> SPAT_STATS; VALIDATORS --> NUM_METH

    %% API layer uses core domains
    API_MATH --> GEOM; API_MATH --> SPAT_STATS; API_MATH --> CRS_TRANS

    classDef mathdomain fill:#e3f2fd,stroke:#1e88e5,stroke-width:2px;
    class Core_Mathematical_Domains mathdomain;
```

-   **Core Mathematical Domains:** These sub-modules (`geometry`, `spatial_statistics`, etc.) contain the primary implementations of algorithms and functions. They may have some interdependencies (e.g., spatial statistics might rely on geometric calculations).
-   **Utility Layer:** Provides common helper functions, mathematical constants, and input validation routines used across the different mathematical domains.
-   **API & Integration Points:** While much of GEO-INFER-MATH will be used directly by other modules importing its functions, a thin `api/` layer might provide simplified facades or convenience functions for common multi-step mathematical workflows.

## Integration with other GEO-INFER Modules

GEO-INFER-MATH is a fundamental dependency for nearly all other modules that perform quantitative analysis:

-   **GEO-INFER-SPACE:** Heavily relies on `geometry` for spatial object representation and operations, `transforms` for CRS handling, and `numerical_methods` for things like spatial indexing algorithms or raster operations.
-   **GEO-INFER-TIME:** Uses `numerical_methods` for temporal interpolation, and `linalg_tensor` for analyzing time-series of spatial data. Statistical functions from `spatial_statistics` might be adapted for temporal autocorrelation.
-   **GEO-INFER-AI:** Leverages `linalg_tensor` for data representation, `spatial_statistics` for feature engineering (e.g., spatial lags), and various mathematical components (distance metrics, kernels) as building blocks for ML algorithms.
-   **GEO-INFER-ACT & GEO-INFER-AGENT:** Mathematical models of agent behavior or environmental dynamics will use functions from `numerical_methods` (e.g., ODE solvers), `linalg_tensor`, and potentially `spatial_statistics`.
-   **GEO-INFER-SIM:** Simulation engines require geometric calculations, random number generation routines (often part of `spatial_statistics` or `utils`), and numerical methods for updating states.
-   **GEO-INFER-BAYES & GEO-INFER-SPM:** These statistical modules directly use or extend concepts from `spatial_statistics`, `linalg_tensor` (for model matrices), and `numerical_methods` (for MCMC or optimization in Bayesian inference).
-   **GEO-INFER-DATA:** While primarily about data management, it may use basic geometric functions or transformation utilities from MATH for validating or preparing data.
-   **GEO-INFER-APP & GEO-INFER-ART:** May use transformation functions for display purposes or basic geometric calculations for interactive tools.
-   **Domain-Specific Modules (AG, ECON, HEALTH, etc.):** All will utilize relevant parts of MATH for their specific calculations, be it statistical analysis, geometric processing, or model implementation.

## Getting Started

### Prerequisites
-   Python 3.9+
-   NumPy (core dependency, often installed with Python for scientific computing)
-   SciPy (for more advanced numerical methods and statistics)
-   Optionally, libraries like `pyproj` for transformations if not vendored or wrapped.

### Installation
```bash
pip install -e ./GEO-INFER-MATH
```

### Configuration
GEO-INFER-MATH itself usually requires minimal configuration. However, it might:
-   Define default numerical precision.
-   Specify paths to geodetic grid shift files if performing very high-accuracy datum transformations (though this is often handled by underlying libraries like PROJ).

### Quick Start Examples

**1. Geometric Calculation: Haversine Distance**
```python
import numpy as np
from geo_infer_math.core.geometry import haversine_distance

# Calculate distance between two points on Earth
dist_ny_la = haversine_distance(
    lat1=40.7128, lon1=-74.0060,  # New York
    lat2=34.0522, lon2=-118.2437  # Los Angeles
)
print(f"Distance (NY to LA): {dist_ny_la:.2f} km")
```

**2. Spatial Statistics: Moran's I for Spatial Autocorrelation**
```python
from geo_infer_math.core.spatial_statistics import MoranI
# Assuming 'points_data' is a GeoDataFrame with a 'value' column and geometry
# values = points_data['value'].values
# coordinates = np.array([(p.x, p.y) for p in points_data.geometry])

# Example data:
values = np.array([1, 2, 3, 8, 7, 6])
coordinates = np.array([[0,0], [1,1], [0,1], [10,10], [11,11], [10,11]])
weight_matrix_type = 'knn' # or 'distance_band'
k_neighbors = 3 # for knn

# moran_calculator = MoranI(connectivity=weight_matrix_type, k=k_neighbors)
# moran_result = moran_calculator.compute(values, coordinates)
# print(f"Moran's I: {moran_result.I:.4f}, p-value: {moran_result.p_sim:.4f}")
# Note: Actual MoranI class and compute signature might differ. This is illustrative.
# The previous example from the original README is also a good illustration.
```

**3. Coordinate Transformation (Conceptual)**
```python
from geo_infer_math.core.transforms import Transformer # Conceptual
# transformer_wgs84_to_utm = Transformer(from_crs="EPSG:4326", to_crs="EPSG:32632") # UTM Zone 32N
# point_wgs84 = (10.0, 50.0) # Longitude, Latitude
# point_utm = transformer_wgs84_to_utm.transform_point(point_wgs84)
# print(f"WGS84 {point_wgs84} -> UTM {point_utm}")
```

## Mathematical Concepts

This module implements and relies on a wide range of mathematical concepts including:
-   **Euclidean and Non-Euclidean Geometry:** For measurements on flat and curved surfaces (like Earth).
-   **Linear Algebra:** For transformations, solving systems of equations (e.g., in regression), and representing data.
-   **Calculus (Differential and Integral):** For analyzing rates of change, areas, volumes, and in optimization.
-   **Probability Theory and Statistics:** For descriptive statistics, hypothesis testing, regression, and stochastic modeling.
-   **Numerical Analysis:** For approximation techniques, interpolation, integration, and solving equations that lack analytical solutions.
-   **Graph Theory:** For network analysis, connectivity, and flow modeling.
-   **Topology:** For understanding spatial relationships like adjacency, containment, and connectivity in a formal way.

## Directory Structure

A typical structure for GEO-INFER-MATH would be:
```
GEO-INFER-MATH/
├── config/                     # Minimal config, e.g., numerical precision defaults
├── docs/                       # Detailed documentation, mathematical derivations
│   └── tutorials/              # Tutorials for specific mathematical areas
├── examples/                   # Example scripts and notebooks
│   └── spatial_statistics_example.py
├── src/
│   └── geo_infer_math/
│       ├── __init__.py
│       ├── api/                # High-level API (optional, if complex workflows are wrapped)
│       │   └── __init__.py
│       │   └── spatial_analysis.py
│       ├── core/               # Core mathematical implementations
│       │   ├── __init__.py
│       │   ├── geometry.py
│       │   ├── linalg_tensor.py
│       │   ├── numerical_methods.py
│       │   ├── spatial_statistics.py
│       │   ├── transforms.py
│       │   └── graph_theory.py
│       ├── models/             # Components for statistical/ML models (can be lean if full models elsewhere)
│       │   ├── __init__.py
│       │   └── regression_components.py
│       └── utils/              # Common math utilities, constants, validators
│           ├── __init__.py
│           └── validators.py
├── tests/                      # Unit tests for all mathematical functions
│   └── test_spatial_statistics.py
└── pyproject.toml              # Or setup.py for package definition
```

## Future Development

-   Expansion of GPU-accelerated geometric and algebraic operations.
-   Integration of symbolic mathematics capabilities (e.g., via SymPy) for model derivation or analysis.
-   More comprehensive support for 3D geospatial mathematics (volumetric analysis, 3D topology).
-   Advanced algorithms for topological data analysis (TDA) in geospatial contexts.
-   Further optimization of core algorithms for very large datasets.
-   Enhanced support for distributed mathematical computations if required by other modules.

## Contributing

Contributions are vital for a foundational library like GEO-INFER-MATH. This can include:
-   Implementing new mathematical algorithms relevant to geospatial analysis.
-   Optimizing existing functions for performance or numerical stability.
-   Adding more robust unit tests and improving test coverage.
-   Writing clear documentation and examples for mathematical functions.
-   Identifying and integrating well-vetted external mathematical libraries where appropriate.

Please refer to the main `CONTRIBUTING.md` in the GEO-INFER root directory and any specific guidelines in `GEO-INFER-MATH/docs/CONTRIBUTING_MATH.md` (to be created).

## License

This module, as part of the GEO-INFER framework, is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 