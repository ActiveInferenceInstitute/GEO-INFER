# utils
 ## Overview
 This directory contains utils components. It includes 4 Python modules. ## Components
 ### data_i
o
.py Data input/output utilities for GEO-INFER-SPM **Functions**: `load_data`, `load_geotiff`, `load_netcdf`, `load_geojson`, `load_geopackage`, `load_csv_with_coords`, `load_hdf5`, `load_json_data`, `save_spm`, `_save_spm_json`, `_save_spm_hdf5`, `_save_spm_csv` ### helper
s
.py Helper functions for GEO-INFER-SPM **Functions**: `create_design_matrix`, `_parse_formula`, `_create_dummy_variables`, `generate_coordinates`, `generate_synthetic_data`, `create_spatial_basis_functions`, `compute_power_analysis` ### preprocessin
g
.py Data preprocessing utilities for GEO-INFER-SPM **Functions**: `preprocess_data`, `handle_missing_data`, `_spatial_interpolate_missing`, `normalize_data`, `remove_outliers`, `_detect_outliers_1d`, `spatial_filter`, `temporal_filter`, `_moving_average_filter`, `_exponential_filter` ### validatio
n
.py Data validation utilities for GEO-INFER-SPM **Functions**: `validate_spm_data`, `validate_design_matrix`, `_validate_factors`, `validate_contrast`, `validate_spatial_autocorrelation`, `_compute_morans_i`, `_compute_gearys_c`, `_compute_variogram`, `_assess_spatial_dependence` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 