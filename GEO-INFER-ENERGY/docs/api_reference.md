# GEO-INFER-ENERGY API Reference

Complete API reference for the `geo_infer_energy` package. All classes are importable from the top-level package or from their respective core modules.

## SolarAnalyzer

**Module**: `geo_infer_energy.core.solar_analysis`

Physics-based solar irradiance modeling with panel orientation optimization.

### Constructor

```python
SolarAnalyzer(config: Optional[Dict] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `Optional[Dict]` | `None` | Configuration dictionary (reserved for future use) |

**Attributes**:
- `solar_constant` (`float`): Solar constant, 1361 W/m2.

### Methods

#### `solar_declination(day_of_year: int) -> float`

Calculate solar declination angle using Spencer (1971): `delta = 23.45 * sin(360/365 * (284 + n))`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `day_of_year` | `int` | Day of year (1-365) |

**Returns**: Solar declination in degrees.

#### `hour_angle(solar_time_hours: float) -> float`

Calculate hour angle from solar time. Returns negative before noon, positive after.

| Parameter | Type | Description |
|-----------|------|-------------|
| `solar_time_hours` | `float` | Solar time in hours (12.0 = solar noon) |

**Returns**: Hour angle in degrees.

#### `solar_elevation(latitude_deg: float, day_of_year: int, solar_time_hours: float) -> float`

Calculate solar elevation angle above the horizon.

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude_deg` | `float` | Latitude in degrees |
| `day_of_year` | `int` | Day of year |
| `solar_time_hours` | `float` | Solar time in hours |

**Returns**: Solar elevation in degrees.

#### `extraterrestrial_irradiance(day_of_year: int) -> float`

Calculate extraterrestrial irradiance accounting for Earth-Sun distance variation.

**Returns**: Irradiance in W/m2.

#### `clear_sky_ghi(latitude_deg: float, day_of_year: int, solar_time_hours: float, altitude_m: float = 0.0) -> float`

Estimate clear-sky Global Horizontal Irradiance using the Hottel (1976) model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latitude_deg` | `float` | -- | Latitude in degrees |
| `day_of_year` | `int` | -- | Day of year |
| `solar_time_hours` | `float` | -- | Solar time in hours |
| `altitude_m` | `float` | `0.0` | Altitude above sea level in meters |

**Returns**: Clear-sky GHI in W/m2. Returns 0 if sun is below horizon.

#### `daily_insolation(latitude_deg: float, day_of_year: int, altitude_m: float = 0.0) -> float`

Integrate hourly GHI over 24 hours at quarter-hour resolution.

**Returns**: Daily insolation in kWh/m2/day.

#### `optimal_tilt_angle(latitude_deg: float) -> float`

Calculate optimal fixed panel tilt using the Jacobson-Jadhav (2018) approximation: `tilt = |latitude| * 0.76 + 3.1`.

**Returns**: Optimal tilt in degrees from horizontal.

#### `tilted_irradiance_factor(tilt_deg: float, azimuth_deg: float, solar_elevation_deg: float, solar_azimuth_deg: float) -> float`

Calculate irradiance ratio on a tilted surface relative to horizontal.

**Returns**: Factor clamped to [0, 3].

#### `estimate_pv_output(ghi_kwh_m2_day: float, panel_area_m2: float, efficiency: float = 0.20, performance_ratio: float = 0.80) -> Dict[str, float]`

Estimate PV system energy output.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ghi_kwh_m2_day` | `float` | -- | Daily GHI in kWh/m2/day |
| `panel_area_m2` | `float` | -- | Total panel area in m2 |
| `efficiency` | `float` | `0.20` | Panel efficiency (modern silicon) |
| `performance_ratio` | `float` | `0.80` | System performance ratio |

**Returns**: Dictionary with keys `daily_kwh`, `annual_kwh`, `annual_mwh`, `peak_capacity_kw`, `capacity_factor`, `panel_area_m2`, `efficiency`.

---

## RenewableResourceAssessor

**Module**: `geo_infer_energy.core.renewable_resources`

Multi-resource renewable energy assessment including siting, capacity factors, LCOE, and storage analysis.

### Constructor

```python
RenewableResourceAssessor(config: Optional[Dict] = None)
```

**Attributes**:
- `efficiency` (`Dict[RenewableType, float]`): Default efficiency per resource type.
- `capital_costs` (`Dict[RenewableType, float]`): Default capital costs in USD/kW.
- `site_registry` (`Dict[str, RenewableSite]`): Registry of evaluated sites.

### Methods

#### `assess_solar_potential(solar_irradiance: xr.DataArray, slope: Optional[xr.DataArray] = None, aspect: Optional[xr.DataArray] = None) -> xr.Dataset`

Assess solar energy potential. Adjusts for terrain slope (optimal ~30 degrees) and aspect (south-facing preferred in northern hemisphere).

**Returns**: Dataset with `solar_potential` and `annual_energy` variables.

#### `assess_wind_potential(wind_speed: xr.DataArray, elevation: Optional[xr.DataArray] = None) -> xr.Dataset`

Assess wind energy potential. Power scales with cube of wind speed.

**Returns**: Dataset with `wind_power` and `energy_potential` variables.

#### `assess_hydro_potential(flow_rate: xr.DataArray, head: xr.DataArray) -> xr.Dataset`

Assess hydroelectric potential using `P = rho * g * Q * h * eta`.

**Returns**: Dataset with `hydro_power` (MW) and `energy_potential` (MWh/year).

#### `assess_site_suitability(location: Tuple[float, float], resource_type: RenewableType, resource_value: float, constraints: Optional[Dict[str, bool]] = None) -> Dict[str, Any]`

Evaluate a candidate site. Applies resource thresholds and constraint penalties.

| Parameter | Type | Description |
|-----------|------|-------------|
| `location` | `Tuple[float, float]` | (lon, lat) |
| `resource_type` | `RenewableType` | Renewable type enum value |
| `resource_value` | `float` | Resource metric (irradiance, wind speed, etc.) |
| `constraints` | `Optional[Dict[str, bool]]` | Flags: `protected_area`, `steep_slope`, `poor_access`, `grid_distance_km` |

**Returns**: Dictionary with `suitability_class`, `resource_score`, `constraint_score`, `final_score`, `development_recommended`, and more.

#### `calculate_capacity_factor(resource_type: RenewableType, resource_data: xr.DataArray, rated_capacity_mw: float = 1.0) -> Dict[str, Any]`

Calculate capacity factor from resource time series. Solar uses 1000 W/m2 as full power. Wind uses cut-in (3 m/s), rated (12 m/s), cut-out (25 m/s) thresholds.

**Returns**: Dictionary with `capacity_factor`, `annual_generation_mwh`, `hours_zero_output`, `hours_full_output`.

#### `calculate_lcoe(resource_type: RenewableType, capacity_mw: float, capacity_factor: float, capital_cost_usd_kw: Optional[float] = None, discount_rate: float = 0.07, lifetime_years: int = 25, opex_usd_kw_year: Optional[float] = None) -> Dict[str, Any]`

Calculate Levelized Cost of Energy using NPV discounting.

**Returns**: Dictionary with `lcoe_usd_kwh`, `lcoe_usd_mwh`, `competitiveness`, `lifetime_generation_gwh`.

#### `analyze_storage_requirements(generation_profile: xr.DataArray, demand_profile: xr.DataArray, renewable_penetration: float = 0.5) -> Dict[str, Any]`

Size energy storage for renewable integration. Default: 4-hour duration at peak deficit power.

**Returns**: Dictionary with `recommended_storage` (power_capacity_mw, energy_capacity_mwh, duration_hours), `curtailment_rate_pct`.

#### `register_site(site: RenewableSite) -> str`

Register a site in the portfolio. Returns site ID.

#### `get_portfolio_summary() -> Dict[str, Any]`

Aggregate statistics across registered sites: total capacity, generation, weighted capacity factor, breakdown by resource type.

---

## EnergyGridOptimizer

**Module**: `geo_infer_energy.core.energy_grid`

Grid network optimization and reliability assessment.

### Methods

#### `optimize_grid_network(demand: xr.DataArray, supply: xr.DataArray, transmission_capacity: Optional[xr.DataArray] = None) -> xr.Dataset`

Calculate supply-demand balance, identify deficits and surpluses, compute reliability ratio.

**Returns**: Dataset with `balance`, `deficit`, `surplus`, `reliability`.

#### `assess_grid_reliability(generation_capacity: xr.DataArray, peak_demand: xr.DataArray, reserve_margin: float = 0.15) -> xr.Dataset`

Assess whether generation meets demand plus reserve margin.

**Returns**: Dataset with `required_capacity`, `adequacy`, `reliability_index`, `capacity_deficit`.

---

## EnergyDemandForecaster

**Module**: `geo_infer_energy.core.energy_demand`

Demand forecasting with temperature and population adjustments.

### Methods

#### `forecast_demand(historical_demand: xr.DataArray, temperature: Optional[xr.DataArray] = None, population: Optional[xr.DataArray] = None, forecast_years: int = 10) -> xr.Dataset`

Forecast future demand using linear trend extrapolation with optional temperature and population factors.

**Returns**: Dataset with `demand_forecast` variable.

#### `identify_peak_demand(demand_time_series: xr.DataArray) -> xr.Dataset`

Identify peak demand periods from a time series.

**Returns**: Dataset with `peak_demand`, `peak_time`, `average_demand`, `peak_factor`.

---

## CarbonFootprintAnalyzer

**Module**: `geo_infer_energy.core.carbon_footprint`

Carbon emissions tracking and intensity mapping for energy systems.

### Constructor

```python
CarbonFootprintAnalyzer(config: Optional[Dict] = None)
```

### Methods

#### `calculate_emissions(energy_generation: xr.DataArray, fuel_type: str = 'natural_gas') -> xr.DataArray`

CO2 emissions (kg) from generation (MWh) using per-fuel emission factors; unknown fuels default to 350 kg CO2/MWh.

#### `calculate_carbon_intensity(total_emissions: xr.DataArray, total_energy: xr.DataArray) -> xr.DataArray`

Carbon intensity (kg CO2/MWh) = emissions / energy.

#### `assess_renewable_impact(renewable_energy: xr.DataArray, total_energy: xr.DataArray, baseline_emissions: xr.DataArray) -> xr.Dataset`

Keys: `renewable_fraction`, `emissions_avoided`, `remaining_emissions`, `emission_reduction_pct`.

---

## EnergyInfrastructurePlanner

**Module**: `geo_infer_energy.core.energy_infrastructure`

Transmission and generation infrastructure expansion planning.

### Constructor

```python
EnergyInfrastructurePlanner(config: Optional[Dict] = None)
```

### Methods

#### `optimize_facility_siting(resource_potential: xr.DataArray, demand_centers: xr.DataArray, constraints: Optional[xr.DataArray] = None, max_distance: float = 50.0) -> xr.Dataset`

Weighted suitability (60% resource, 40% demand density); `demand_centers` is normalized by its own maximum into `demand_density` (a demand-density proximity proxy, not a geographic distance). Keys: `suitability`, `optimal_sites` (top 10% by quantile), `resource_suitability`, `demand_density`.

#### `assess_infrastructure_capacity(current_capacity: xr.DataArray, projected_demand: xr.DataArray, years: int = 10) -> xr.Dataset`

Keys: `current_capacity`, `required_capacity`, `capacity_gap`, `annual_growth_needed`.


## Enums and Data Classes

### RenewableType

```python
class RenewableType(Enum):
    SOLAR_PV = "solar_pv"
    SOLAR_THERMAL = "solar_thermal"
    ONSHORE_WIND = "onshore_wind"
    OFFSHORE_WIND = "offshore_wind"
    HYDROPOWER = "hydropower"
    GEOTHERMAL = "geothermal"
    BIOMASS = "biomass"
    WAVE = "wave"
    TIDAL = "tidal"
```

### SuitabilityClass

```python
class SuitabilityClass(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    MARGINAL = "marginal"
    UNSUITABLE = "unsuitable"
```

### RenewableSite

```python
@dataclass
class RenewableSite:
    site_id: str
    name: str
    location: Tuple[float, float]
    resource_type: RenewableType
    capacity_mw: float
    capacity_factor: float
    annual_generation_gwh: Optional[float] = None
    lcoe_usd_mwh: Optional[float] = None
    land_area_km2: Optional[float] = None
```
