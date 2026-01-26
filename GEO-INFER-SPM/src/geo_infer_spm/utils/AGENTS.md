# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 0 classes and 38 functions. ## Classes
 and Functions ### load_dat
a
 `load_data(file_path: str, **kwargs) -> SPMData` Load geospatial data from file with automatic format detection. ### load_geotif
f
 `load_geotiff(file_path: str, band: Optional[int], nodata_value: Optional[float]) -> SPMData` Load GeoTIFF raster data. ### load_netcd
f
 `load_netcdf(file_path: str, variable: Optional[str], time_dim: Optional[str], lat_dim: str, lon_dim: str) -> SPMData` Load NetCDF data. ### load_geojso
n
 `load_geojson(file_path: str, value_column: Optional[str]) -> SPMData` Load GeoJSON vector data. ### load_geopackag
e
 `load_geopackage(file_path: str, layer: Optional[str], value_column: Optional[str]) -> SPMData` Load GeoPackage vector data. ### load_csv_with_coord
s
 `load_csv_with_coords(file_path: str, x_column: str, y_column: str, value_column: Optional[str], **kwargs) -> SPMData` Load CSV data with coordinate columns. ### load_hdf
5
 `load_hdf5(file_path: str, dataset_path: str, coordinate_datasets: Optional[Dict[str, str]]) -> SPMData` Load HDF5 data. ### load_json_dat
a
 `load_json_data(file_path: str, data_key: str, coords_key: str) -> SPMData` Load JSON data with custom structure. ### save_sp
m
 `save_spm(spm_result: SPMResult, file_path: str, format: str, **kwargs) -> None` Save SPM results to file. ### create_design_matri
x
 `create_design_matrix(data: SPMData, formula: Optional[str], factors: Optional[Dict[str, List[str]]], covariates: Optional[List[str]], intercept: bool) -> DesignMatrix` Create design matrix from SPMData and specification. ### generate_coordinate
s
 `generate_coordinates(grid_type: str, n_points: int, bounds: Optional[Tuple[float, float, float, float]], **kwargs) -> np.ndarray` Generate synthetic coordinate arrays for testing and examples. ### generate_synthetic_dat
a
 `generate_synthetic_data(coordinates: np.ndarray, effects: Optional[Dict[str, Any]], noise_level: float, temporal: bool, n_timepoints: int) -> SPMData` Generate synthetic SPM data for testing and examples. ### create_spatial_basis_function
s
 `create_spatial_basis_functions(coordinates: np.ndarray, n_basis: int, method: str) -> np.ndarray` Create spatial basis functions for modeling spatial variation. ### compute_power_analysi
s
 `compute_power_analysis(effect_size: float, n_points: int, alpha: float, n_simulations: int) -> Dict[str, Any]` Perform power analysis for SPM statistical tests. ### preprocess_dat
a
 `preprocess_data(data: SPMData, steps: Optional[List[str]], **kwargs) -> SPMData` Apply preprocessing pipeline to SPM data. ### handle_missing_dat
a
 `handle_missing_data(data: SPMData, method: str, max_missing_fraction: float) -> SPMData` Handle missing data in SPM dataset. ### normalize_dat
a
 `normalize_data(data: SPMData, method: str, axis: Optional[int]) -> SPMData` Normalize data values for SPM analysis. ### remove_outlier
s
 `remove_outliers(data: SPMData, method: str, threshold: float) -> SPMData` Remove outlier data points. ### spatial_filte
r
 `spatial_filter(data: SPMData, method: str, sigma: float) -> SPMData` Apply spatial filtering to smooth data. ### temporal_filte
r
 `temporal_filter(data: SPMData, method: str, window_size: int) -> SPMData` Apply temporal filtering to time series data. ### validate_spm_dat
a
 `validate_spm_data(data: SPMData) -> SPMData` Validate SPMData object for consistency and data quality. ### validate_design_matri
x
 `validate_design_matrix(design_matrix: DesignMatrix, n_points: Optional[int]) -> DesignMatrix` Validate design matrix for GLM analysis. ### validate_contras
t
 `validate_contrast(contrast_vector: np.ndarray, n_regressors: int, contrast_type: str) -> np.ndarray` Validate contrast vector for statistical testing. ### validate_spatial_autocorrelatio
n
 `validate_spatial_autocorrelation(data: SPMData, max_lag: int, alpha: float) -> Dict[str, Any]` Validate and assess spatial autocorrelation in data. ## Capabilities
 - **38 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SPM/src/geo_infer_spm/utils` - **Type**: Directory Node 