# Agent
: macroeconomics

## Scope
 This directory contains macroeconomics components for the module. It provides 6 classes and 4 functions.

## Classes
 and Functions

### RegionProfile
 Profile of a region for macroeconomic analysis

### SolowGrowthModel
 Implementation of the Solow growth model with spatial extensions

**Methods**:
- `production_function(K: float, L: float, A: float) -> float`: Cobb-Douglas production function: Y = A * K^α * L^(1-α)
- `capital_dynamics(K: float, L: float, A: float) -> float`: Capital accumulation equation: dK/dt = s*Y - (n + δ + g)*K
- `steady_state_values() -> Dict[str, float]`: Calculate steady-state values
- `convergence_analysis(initial_capital_ratio: float) -> Dict[str, Any]`: Analyze convergence to steady state
- `simulate_growth_path(initial_conditions: Dict[str, float], time_horizon: int) -> pd.DataFrame`: Simulate growth path over time

### SpatialGrowthModels
 Spatial extensions of growth models incorporating geographic factors

**Methods**:
- `calculate_spatial_weights(decay_parameter: float) -> np.ndarray`: Calculate spatial weight matrix based on distances
- `spatial_solow_model(spillover_strength: float) -> Dict[str, Any]`: Multi-region Solow model with technology spillovers

### EndogenousGrowthModels
 Implementation of endogenous growth models with algorithms

**Methods**:
- `ak_model(A: float, s: float, delta: float) -> Dict[str, float]`: AK model: Y = AK, where A is constant returns to capital
- `romer_model(parameters: Dict[str, float]) -> Dict[str, Any]`: Romer (1990) R&D-based growth model with implementation
- `schumpeterian_model(parameters: Dict[str, float]) -> Dict[str, Any]`: Schumpeterian creative destruction model

### RegionalConvergenceAnalysis
 Analysis of regional economic convergence patterns

**Methods**:
- `beta_convergence_analysis(initial_year: int, final_year: int) -> Dict[str, Any]`: Analyze beta convergence (catch-up effect)
- `sigma_convergence_analysis() -> Dict[str, Any]`: Analyze sigma convergence (reduction in dispersion)
- `spatial_convergence_analysis(spatial_weights: np.ndarray) -> Dict[str, Any]`: Analyze spatial convergence patterns

### TechnologyDiffusionModels
 Models of technology diffusion across space

**Methods**:
- `bass_diffusion_spatial(regions: List[RegionProfile], innovation_params: Dict[str, float], spatial_weights: np.ndarray) -> Dict[str, Any]`: Spatial Bass diffusion model for technology adoption
- `knowledge_spillover_model(regions: List[RegionProfile], rd_data: pd.DataFrame) -> Dict[str, Any]`: Model knowledge spillovers and productivity growth

### example_growth_analysis
 `example_growth_analysis()` Example usage of growth models

### system_dynamics
 `system_dynamics(t, y)`

### spatial_dynamics
 `spatial_dynamics(t, y)`

### spatial_bass_dynamics
 `spatial_bass_dynamics(t, y)` Spatial Bass diffusion dynamics

## Capabilities

- **6 classes** for core functionality
- **4 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-ECON/src/geo_infer_econ/macroeconomics`
- **Type**: Directory Node
