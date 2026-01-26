# core
 ## Overview
 This directory contains core components. It includes 6 Python modules. ## Components
 ### bayesia
n
.py Bayesian extensions for Statistical Parametric Mapping **Classes**: `BayesianSPM` **Functions**: `negative_log_posterior` ### contrast
s
.py Contrast analysis for Statistical Parametric Mapping **Classes**: `Contrast` **Functions**: `contrast`, `_compute_t_contrast`, `_compute_f_contrast`, `generate_common_contrasts` ### gl
m
.py General Linear Model implementation for Statistical Parametric Mapping **Classes**: `GeneralLinearModel` **Functions**: `fit_glm` ### rf
t
.py Random Field Theory implementation for Statistical Parametric Mapping **Classes**: `RandomFieldTheory` **Functions**: `compute_spm`, `expected_clusters_func` ### spatial_analysi
s
.py Spatial analysis tools for Statistical Parametric Mapping **Classes**: `SpatialAnalyzer` **Functions**: `spherical_model`, `exponential_model`, `gaussian_model`, `objective` ### temporal_analysi
s
.py Temporal analysis tools for Statistical Parametric Mapping **Classes**: `TemporalAnalyzer` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 