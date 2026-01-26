# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 3 classes and 24 functions. ## Classes
 and Functions ### ConfigurationLoade
r
 Configuration loader with validation and caching. **Methods**: - `load_config(config_path: Union[str, Path, Dict[str, Any]], validate: bool, strict: bool, use_cache: bool) -> Dict[str, Any]`: Load configuration from file or dictionary. - `load_config_with_defaults(config_path: Optional[Union[str, Path, Dict[str, Any]]], **overrides) -> Dict[str, Any]`: Load configuration with default values and optional overrides. - `get_default_config() -> Dict[str, Any]`: Get default configuration. - `save_config(config: Dict[str, Any], output_path: Union[str, Path], format: str) -> str`: Save configuration to file. - `create_example_config(output_path: Union[str, Path], hazard_types: Optional[list], include_comments: bool) -> str`: Create an example configuration file. - `clear_cache() -> None`: Clear configuration and validation caches. ### ValidationResul
t
 Result of validation operation. ### ConfigurationValidato
r
 configuration validator for GEO-INFER-RISK. **Methods**: - `validate_config(config: Dict[str, Any], strict: bool) -> ValidationResult`: Validate configuration against schema and custom rules. ### load_confi
g
 `load_config(config_path: Union[str, Path, Dict[str, Any]], validate: bool, strict: bool) -> Dict[str, Any]` Load configuration from file or dictionary. ### load_config_with_default
s
 `load_config_with_defaults(config_path: Optional[Union[str, Path, Dict[str, Any]]], **overrides) -> Dict[str, Any]` Load configuration with default values and optional overrides. ### create_example_confi
g
 `create_example_config(output_path: Union[str, Path], hazard_types: Optional[list]) -> str` Create an example configuration file. ### get_default_confi
g
 `get_default_config() -> Dict[str, Any]` Get default configuration. ### save_confi
g
 `save_config(config: Dict[str, Any], output_path: Union[str, Path], format: str) -> str` Save configuration to file. ### calculate_aa
l
 `calculate_aal(event_loss_table: pd.DataFrame) -> Dict[str, Any]` Calculate the Average Annual Loss (AAL) from an event loss table. ### calculate_ep_curv
e
 `calculate_ep_curve(event_loss_table: pd.DataFrame, exceedance_probs: Optional[List[float]]) -> Dict[str, Any]` Calculate the Exceedance Probability (EP) curve from an event loss table. ### calculate_pm
l
 `calculate_pml(event_loss_table: pd.DataFrame, return_period: float) -> float` Calculate the Probable Maximum Loss (PML) for a given return period. ### calculate_loss_by_return_perio
d
 `calculate_loss_by_return_period(event_loss_table: pd.DataFrame, return_periods: List[float]) -> Dict[str, float]` Calculate losses for multiple return periods. ### calculate_tail_value_at_ris
k
 `calculate_tail_value_at_risk(event_loss_table: pd.DataFrame, confidence_level: float) -> float` Calculate the Tail Value at Risk (TVaR) at a specified confidence level. ### calculate_annual_occurrence_exceedance_probabilit
y
 `calculate_annual_occurrence_exceedance_probability(event_loss_table: pd.DataFrame, threshold: float) -> float` Calculate the Annual Occurrence Exceedance Probability (OEP) for a loss threshold. ### calculate_annual_aggregate_exceedance_probabilit
y
 `calculate_annual_aggregate_exceedance_probability(event_loss_table: pd.DataFrame, threshold: float, num_years: int) -> float` Calculate the Annual Aggregate Exceedance Probability (AEP) for a loss threshold. ### calculate_loss_frequency_curv
e
 `calculate_loss_frequency_curve(event_loss_table: pd.DataFrame, num_bins: int) -> Dict[str, List[float]]` Calculate a loss frequency curve (histogram of losses). ### calculate_correlation_matri
x
 `calculate_correlation_matrix(event_loss_table: pd.DataFrame) -> Dict[str, Any]` Calculate the correlation matrix between losses for different hazard types. ### validate_confi
g
 `validate_config(config: Dict[str, Any], schema_path: Optional[str], strict: bool) -> ValidationResult` Validate configuration against schema and custom rules. ### validate_data_fil
e
 `validate_data_file(file_path: str, data_type: str) -> ValidationResult` Validate data file format and content. ### validate_csv_fil
e
 `validate_csv_file(file_path: str) -> ValidationResult` Validate CSV file format and content. ### validate_json_fil
e
 `validate_json_file(file_path: str) -> ValidationResult` Validate JSON file format and content. ### validate_shapefil
e
 `validate_shapefile(file_path: str) -> ValidationResult` Validate shapefile format and content. ### validate_model_parameter
s
 `validate_model_parameters(model_type: str, parameters: Dict[str, Any]) -> ValidationResult` Validate model parameters for specific model types. ### validate_hazard_parameter
s
 `validate_hazard_parameters(parameters: Dict[str, Any]) -> ValidationResult` Validate hazard model parameters. ### validate_vulnerability_parameter
s
 `validate_vulnerability_parameters(parameters: Dict[str, Any]) -> ValidationResult` Validate vulnerability model parameters. ### validate_exposure_parameter
s
 `validate_exposure_parameters(parameters: Dict[str, Any]) -> ValidationResult` Validate exposure model parameters. ### validate_insurance_parameter
s
 `validate_insurance_parameters(parameters: Dict[str, Any]) -> ValidationResult` Validate insurance model parameters. ## Capabilities
 - **3 classes** for core functionality - **24 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-RISK/src/geo_infer_risk/utils` - **Type**: Directory Node 